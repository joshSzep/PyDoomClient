"""
3D Geometry module for PyDoomClient.

This module handles the conversion of 2D map data from WAD files into 3D geometry
that can be rendered by the 3D renderer.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple

from pydoomclient.camera3d import Vector3
from pydoomclient.renderer import LineDefinition, Sector
from pydoomclient.wad import WADReader


@dataclass
class Triangle:
    """A 3D triangle."""

    v1: Vector3
    v2: Vector3
    v3: Vector3
    color: Tuple[int, int, int] = (128, 128, 128)  # Default gray color
    texture_name: Optional[str] = None
    uv1: Optional[Tuple[float, float]] = None
    uv2: Optional[Tuple[float, float]] = None
    uv3: Optional[Tuple[float, float]] = None

    def normal(self) -> Vector3:
        """Calculate the normal vector of this triangle."""
        edge1 = self.v2 - self.v1
        edge2 = self.v3 - self.v1
        return edge1.cross(edge2).normalize()


@dataclass
class Wall:
    """A 3D wall segment."""

    # Bottom-left, bottom-right, top-right, top-left vertices
    vertices: List[Vector3]
    color: Tuple[int, int, int] = (128, 128, 128)
    texture_name: Optional[str] = None

    def to_triangles(self) -> List[Triangle]:
        """Convert the wall to two triangles."""
        return [
            # First triangle (bottom-left, bottom-right, top-right)
            Triangle(
                self.vertices[0],
                self.vertices[1],
                self.vertices[2],
                self.color,
                self.texture_name,
                (0, 1),
                (1, 1),
                (1, 0),  # UV coordinates
            ),
            # Second triangle (bottom-left, top-right, top-left)
            Triangle(
                self.vertices[0],
                self.vertices[2],
                self.vertices[3],
                self.color,
                self.texture_name,
                (0, 1),
                (1, 0),
                (0, 0),  # UV coordinates
            ),
        ]


class GeometryBuilder:
    """Builds 3D geometry from 2D map data."""

    def __init__(self, wad_reader: WADReader, map_name: str):
        """Initialize the geometry builder.

        Args:
            wad_reader: WAD reader to get map data from
            map_name: Name of the map to build geometry for
        """
        self.wad_reader = wad_reader
        self.map_name = map_name
        self.map_data = None
        self.walls: List[Wall] = []
        self.floor_triangles: List[Triangle] = []
        self.ceiling_triangles: List[Triangle] = []

        # Load map data
        self._load_map_data()

    def _load_map_data(self):
        """Load map data from the WAD file."""
        from pydoomclient.renderer import MapData

        self.map_data = MapData(self.wad_reader, self.map_name)

    def build_geometry(self):
        """Build 3D geometry from the map data."""
        if not self.map_data:
            return

        # Clear existing geometry
        self.walls = []
        self.floor_triangles = []
        self.ceiling_triangles = []

        # Process each linedef to create walls
        for linedef in self.map_data.linedefs:
            self._process_linedef(linedef)

        # Process sectors to create floors and ceilings
        for i, sector in enumerate(self.map_data.sectors):
            self._process_sector(i, sector)

    def _process_linedef(self, linedef: LineDefinition):
        """Process a linedef to create a wall."""
        # Get vertices
        v1 = self.map_data.vertices[linedef.start_vertex]
        v2 = self.map_data.vertices[linedef.end_vertex]

        # Get sidedefs
        if linedef.front_sidedef >= 0 and linedef.front_sidedef < len(
            self.map_data.sidedefs
        ):
            front_sidedef = self.map_data.sidedefs[linedef.front_sidedef]
            front_sector = None
            if front_sidedef.sector >= 0 and front_sidedef.sector < len(
                self.map_data.sectors
            ):
                front_sector = self.map_data.sectors[front_sidedef.sector]
        else:
            front_sidedef = None
            front_sector = None

        if (
            linedef.back_sidedef is not None
            and linedef.back_sidedef >= 0
            and linedef.back_sidedef < len(self.map_data.sidedefs)
        ):
            back_sidedef = self.map_data.sidedefs[linedef.back_sidedef]
            back_sector = None
            if back_sidedef.sector >= 0 and back_sidedef.sector < len(
                self.map_data.sectors
            ):
                back_sector = self.map_data.sectors[back_sidedef.sector]
        else:
            back_sidedef = None
            back_sector = None

        # One-sided wall
        if front_sector and not back_sector:
            # Create a wall from floor to ceiling
            floor_height = front_sector.floor_height
            ceiling_height = front_sector.ceiling_height

            # Create 3D vertices for the wall
            # Bottom-left, bottom-right, top-right, top-left
            vertices = [
                Vector3(v1.x, v1.y, floor_height),
                Vector3(v2.x, v2.y, floor_height),
                Vector3(v2.x, v2.y, ceiling_height),
                Vector3(v1.x, v1.y, ceiling_height),
            ]

            # Get texture name
            texture_name = front_sidedef.middle_texture if front_sidedef else None

            # Create wall
            wall = Wall(vertices, (128, 128, 128), texture_name)
            self.walls.append(wall)

        # Two-sided wall (portal between sectors)
        elif front_sector and back_sector:
            # Handle upper wall if needed
            if front_sector.ceiling_height > back_sector.ceiling_height:
                upper_vertices = [
                    Vector3(v1.x, v1.y, back_sector.ceiling_height),
                    Vector3(v2.x, v2.y, back_sector.ceiling_height),
                    Vector3(v2.x, v2.y, front_sector.ceiling_height),
                    Vector3(v1.x, v1.y, front_sector.ceiling_height),
                ]
                texture_name = front_sidedef.upper_texture if front_sidedef else None
                upper_wall = Wall(upper_vertices, (100, 100, 100), texture_name)
                self.walls.append(upper_wall)

            # Handle lower wall if needed
            if front_sector.floor_height < back_sector.floor_height:
                lower_vertices = [
                    Vector3(v1.x, v1.y, front_sector.floor_height),
                    Vector3(v2.x, v2.y, front_sector.floor_height),
                    Vector3(v2.x, v2.y, back_sector.floor_height),
                    Vector3(v1.x, v1.y, back_sector.floor_height),
                ]
                texture_name = front_sidedef.lower_texture if front_sidedef else None
                lower_wall = Wall(lower_vertices, (100, 100, 100), texture_name)
                self.walls.append(lower_wall)

    def _process_sector(self, sector_index: int, sector: Sector):
        """Process a sector to create floor and ceiling triangles."""
        # This is a simplified approach - in a real Doom engine, sectors would be
        # properly triangulated using algorithms like ear clipping
        # For now, we'll just create a simple triangulation based on the sector's
        # linedefs

        # TODO: Implement proper sector triangulation
        # For now, we'll skip this as it requires more complex algorithms
        pass
