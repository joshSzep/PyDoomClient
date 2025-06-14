#!/usr/bin/env python3
"""
Development environment setup script for PyDoomClient.
This script helps set up the development environment and checks for required dependencies.
"""

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.absolute()


def check_python_version() -> bool:
    """Check if Python version meets requirements."""
    required_version = (3, 12)
    current_version = sys.version_info[:2]

    if current_version < required_version:
        print(
            f"Error: Python {required_version[0]}.{required_version[1]}+ is required."
        )
        print(f"Current version: {current_version[0]}.{current_version[1]}")
        return False

    print(
        f"✓ Python version {current_version[0]}.{current_version[1]} meets requirements."
    )
    return True


def check_uv_installed() -> bool:
    """Check if uv is installed."""
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        print("✓ uv is installed.")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: uv is not installed or not in PATH.")
        print("Please install uv: https://github.com/astral-sh/uv")
        return False


def setup_environment() -> None:
    """Set up the development environment."""
    if not (check_python_version() and check_uv_installed()):
        sys.exit(1)

    print("\nSetting up development environment...")

    # Create virtual environment and install dependencies
    os.chdir(PROJECT_ROOT)
    subprocess.run(["uv", "venv"], check=True)
    subprocess.run(["uv", "pip", "install", "-e", ".[dev]"], check=True)

    print("\n✓ Development environment setup complete!")
    print("\nYou can now use 'just' commands to manage the project:")
    print("  just run    - Run the game")
    print("  just test   - Run tests")
    print("  just format - Format code")
    print("  just lint   - Lint code")


if __name__ == "__main__":
    setup_environment()
