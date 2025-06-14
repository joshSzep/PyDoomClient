#!/usr/bin/env python3
"""
Script to download freely available WAD files for testing the PyDoomClient.
This script downloads the Freedoom WAD files which are open-source alternatives to
Doom WADs.
"""

import hashlib
import shutil
import tempfile
import urllib.request
from pathlib import Path
from typing import Dict, Optional

# Freedoom WADs with their URLs and SHA256 checksums
WADS = {
    "freedoom1.wad": {
        "url": "https://github.com/freedoom/freedoom/releases/download/v0.12.1/freedoom-0.12.1.zip",
        "sha256": "f42c6810fc89b0282de1466c2c9c7c9818031a8d556256a6db1b69f6a77b5806",
        "extract_path": "freedoom-0.12.1/freedoom1.wad",
    },
    "freedoom2.wad": {
        "url": "https://github.com/freedoom/freedoom/releases/download/v0.12.1/freedoom-0.12.1.zip",
        "sha256": "f42c6810fc89b0282de1466c2c9c7c9818031a8d556256a6db1b69f6a77b5806",
        "extract_path": "freedoom-0.12.1/freedoom2.wad",
    },
}

DATA_DIR = Path.home() / ".pydoomclient" / "wads"


def download_file(url: str, target_path: Path) -> bool:
    """Download a file from a URL to a target path."""
    print(f"Downloading {url}...")
    try:
        with urllib.request.urlopen(url) as response:
            with open(target_path, "wb") as out_file:
                shutil.copyfileobj(response, out_file)
        return True
    except Exception as e:
        print(f"Error downloading file: {e}")
        return False


def verify_checksum(file_path: Path, expected_sha256: str) -> bool:
    """Verify the SHA256 checksum of a file."""
    print(f"Verifying checksum for {file_path.name}...")
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    actual_sha256 = sha256_hash.hexdigest()
    if actual_sha256 != expected_sha256:
        print("Checksum verification failed!")
        print(f"Expected: {expected_sha256}")
        print(f"Actual: {actual_sha256}")
        return False

    print("Checksum verified successfully.")
    return True


def extract_wad(zip_path: Path, wad_name: str, extract_path: str) -> Optional[Path]:
    """Extract a WAD file from a ZIP archive."""
    import zipfile

    print(f"Extracting {wad_name}...")
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            # Create a temporary directory for extraction
            with tempfile.TemporaryDirectory() as tmpdirname:
                zip_ref.extractall(tmpdirname)
                source_path = Path(tmpdirname) / extract_path
                if not source_path.exists():
                    print(f"Error: {extract_path} not found in ZIP archive")
                    return None

                # Create target directory if it doesn't exist
                target_path = DATA_DIR / wad_name
                DATA_DIR.mkdir(parents=True, exist_ok=True)

                # Copy the WAD file to the target location
                shutil.copy2(source_path, target_path)
                print(f"Extracted {wad_name} to {target_path}")
                return target_path
    except Exception as e:
        print(f"Error extracting WAD: {e}")
        return None


def download_wads() -> None:
    """Download and extract all WAD files."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Track which WADs we've already downloaded to avoid redundant downloads
    downloaded_archives: Dict[str, Path] = {}

    for wad_name, info in WADS.items():
        target_path = DATA_DIR / wad_name

        # Check if WAD already exists
        if target_path.exists():
            print(f"{wad_name} already exists at {target_path}")
            continue

        # Check if we've already downloaded this archive
        url = info["url"]
        if url in downloaded_archives and downloaded_archives[url].exists():
            zip_path = downloaded_archives[url]
        else:
            # Download the archive
            zip_filename = url.split("/")[-1]
            zip_path = DATA_DIR / zip_filename
            if not download_file(url, zip_path):
                continue

            # Verify checksum
            if not verify_checksum(zip_path, info["sha256"]):
                continue

            downloaded_archives[url] = zip_path

        # Extract the WAD
        extract_wad(zip_path, wad_name, info["extract_path"])

    # Clean up downloaded archives
    for zip_path in downloaded_archives.values():
        if zip_path.exists():
            zip_path.unlink()
            print(f"Removed temporary file {zip_path}")

    print("\nWAD files are available at:")
    for wad_path in DATA_DIR.glob("*.wad"):
        print(f"  {wad_path}")


if __name__ == "__main__":
    download_wads()
