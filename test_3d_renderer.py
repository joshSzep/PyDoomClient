#!/usr/bin/env python3
"""
Test script for the 3D renderer.

This script runs the 3D renderer in isolation to test its functionality.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the pydoomclient package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydoomclient.game3d import Game3D
from pydoomclient.wad import list_available_wads


def main():
    """Run the test script."""
    # Check if a WAD file was specified
    if len(sys.argv) < 2:
        print("No WAD file specified.")
        print("Usage: python test_3d_renderer.py <wad_file>")
        print("\nAvailable WAD files:")
        list_available_wads()
        return

    # Get the WAD file path
    wad_path = Path(sys.argv[1])
    if not wad_path.exists():
        print(f"WAD file not found: {wad_path}")
        return

    print(f"Testing 3D renderer with WAD file: {wad_path}")
    print("Controls:")
    print("  Mouse: Look/rotate camera")
    print("  W/S: Move forward/backward")
    print("  A/D: Strafe left/right")
    print("  Q/E: Move up/down (for debugging)")
    print("  Left/Right arrows: Alternative camera rotation")
    print("  M: Toggle mouse look on/off")
    print("  R: Reset camera position")
    print("  Tab: Toggle debug map view")
    print("  Esc: Quit")

    # Create and run the game
    game = Game3D(wad_path)
    game.run()


if __name__ == "__main__":
    main()
