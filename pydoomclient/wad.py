"""
WAD file parsing module.

This module provides functionality to read and parse Doom WAD files.
WAD (Where's All the Data) is the file format used by Doom to store game data.
"""

import struct
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import BinaryIO, Dict, List, Optional, Union


class WADType(Enum):
    """WAD file types."""

    IWAD = auto()  # Internal WAD (main game data)
    PWAD = auto()  # Patch WAD (modifications)


@dataclass
class WADHeader:
    """WAD file header structure."""

    wad_type: WADType
    num_lumps: int
    directory_offset: int


@dataclass
class Lump:
    """WAD lump entry."""

    offset: int
    size: int
    name: str
    data: Optional[bytes] = None


class WADReader:
    """Class for reading and parsing WAD files."""

    def __init__(self, wad_path: Union[str, Path]) -> None:
        """Initialize WAD reader with path to WAD file."""
        self.wad_path = Path(wad_path)
        self.header: Optional[WADHeader] = None
        self.directory: Dict[str, Lump] = {}
        self.lumps: List[Lump] = []
        self.maps: List[str] = []

        if not self.wad_path.exists():
            raise FileNotFoundError(f"WAD file not found: {self.wad_path}")

        self._read_wad()

    def _read_wad(self) -> None:
        """Read and parse the WAD file."""
        with open(self.wad_path, "rb") as f:
            self._read_header(f)
            self._read_directory(f)
            self._identify_maps()

    def _read_header(self, f: BinaryIO) -> None:
        """Read the WAD header."""
        wad_type_str = f.read(4).decode("ascii")
        if wad_type_str == "IWAD":
            wad_type = WADType.IWAD
        elif wad_type_str == "PWAD":
            wad_type = WADType.PWAD
        else:
            raise ValueError(f"Invalid WAD type: {wad_type_str}")

        num_lumps = struct.unpack("<I", f.read(4))[0]
        directory_offset = struct.unpack("<I", f.read(4))[0]

        self.header = WADHeader(wad_type, num_lumps, directory_offset)

    def _read_directory(self, f: BinaryIO) -> None:
        """Read the WAD directory."""
        f.seek(self.header.directory_offset)

        for _ in range(self.header.num_lumps):
            offset = struct.unpack("<I", f.read(4))[0]
            size = struct.unpack("<I", f.read(4))[0]
            name = f.read(8).split(b"\0", 1)[0].decode("ascii")

            lump = Lump(offset, size, name)
            self.lumps.append(lump)
            self.directory[name] = lump

    def _identify_maps(self) -> None:
        """Identify maps in the WAD file."""
        # In Doom, maps start with E#M# (Episode # Map #) or MAP## format
        for i, lump in enumerate(self.lumps):
            if (lump.name.startswith("E") and "M" in lump.name) or lump.name.startswith(
                "MAP"
            ):
                if i + 10 < len(
                    self.lumps
                ):  # Check if we have enough lumps for a complete map
                    # A map should have THINGS, LINEDEFS, SIDEDEFS, VERTEXES, etc.
                    if self.lumps[i + 1].name == "THINGS":
                        self.maps.append(lump.name)

    def get_lump_data(self, name: str) -> Optional[bytes]:
        """Get data for a specific lump by name."""
        if name not in self.directory:
            return None

        lump = self.directory[name]
        if lump.data is None:
            with open(self.wad_path, "rb") as f:
                f.seek(lump.offset)
                lump.data = f.read(lump.size)

        return lump.data

    def get_map_data(self, map_name: str) -> Dict[str, bytes]:
        """Get all data for a specific map."""
        if map_name not in self.maps:
            raise ValueError(f"Map not found: {map_name}")

        map_data = {}
        map_lump_index = self.lumps.index(self.directory[map_name])

        # Map lumps follow a specific order
        map_components = [
            "THINGS",
            "LINEDEFS",
            "SIDEDEFS",
            "VERTEXES",
            "SEGS",
            "SSECTORS",
            "NODES",
            "SECTORS",
            "REJECT",
            "BLOCKMAP",
        ]

        for i, component in enumerate(map_components):
            lump_index = map_lump_index + i + 1
            if (
                lump_index < len(self.lumps)
                and self.lumps[lump_index].name == component
            ):
                map_data[component] = self.get_lump_data(component)

        return map_data


def list_available_wads() -> None:
    """List available WAD files in the default directory."""
    wad_dir = Path.home() / ".pydoomclient" / "wads"
    if not wad_dir.exists():
        print("No WAD files found. Use scripts/download_wad.py to download some.")
        return

    wad_files = list(wad_dir.glob("*.wad"))
    if not wad_files:
        print("No WAD files found. Use scripts/download_wad.py to download some.")
        return

    print("Available WAD files:")
    for wad_file in wad_files:
        print(f"  {wad_file}")


if __name__ == "__main__":
    # Simple test code
    import sys

    if len(sys.argv) < 2:
        print("Usage: python -m pydoomclient.wad <wad_file>")
        sys.exit(1)

    wad_path = sys.argv[1]
    try:
        wad = WADReader(wad_path)
        print(f"WAD Type: {wad.header.wad_type.name}")
        print(f"Number of lumps: {wad.header.num_lumps}")
        print(f"Maps found: {', '.join(wad.maps)}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
