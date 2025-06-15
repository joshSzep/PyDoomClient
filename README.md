# PyDoomClient

An experimental Python Doom client that reads and interprets classic Doom WAD files, rendering a fully 3D first-person view using Pygame.

## Features

- Full 3D rendering with perspective projection
- WAD file parsing and interpretation
- Mouse look with WASD movement controls
- Texture mapping system for walls
- Debug mode with 2D map overlay (toggle with TAB)
- Support for Freedoom and other compatible WAD files
- Wall rendering with backface culling
- Player position based on map data

## Requirements

- Python 3.12+
- `uv` package manager
- `just` command runner

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/PyDoomClient.git
cd PyDoomClient
```

### 2. Set up the development environment

The project uses `uv` for dependency management and `just` for task automation.

```bash
# Install uv if you don't have it already
curl -sSf https://raw.githubusercontent.com/astral-sh/uv/main/install.sh | sh

# Install just if you don't have it already
brew install just  # On macOS with Homebrew
# OR
cargo install just  # If you have Rust installed

# Set up the development environment
just setup
```

### 3. Download a WAD file

The project includes a script to download Freedoom WAD files for testing:

```bash
just download-wad
```

This will download and extract Freedoom WAD files to the `wads` directory.

## Usage

### Running the game

```bash
just run [wad_path]
```

If no WAD path is provided, the game will look for WAD files in the `wads` directory and use the first one found.

You can also run the test script specifically for the 3D renderer:

```bash
python test_3d_renderer.py [wad_path]
```

### Controls

- **Mouse** - Look/rotate camera
- `W` - Move forward
- `S` - Move backward
- `A` - Strafe left
- `D` - Strafe right
- `Q` - Move up (for debugging)
- `E` - Move down (for debugging)
- `←` - Turn left (alternative to mouse)
- `→` - Turn right (alternative to mouse)
- `M` - Toggle mouse look on/off
- `R` - Reset camera position
- `TAB` - Toggle debug mode (shows 2D map overlay)
- `ESC` - Exit game

## Development

### Project Structure

```
PyDoomClient/
├── justfile                # Task automation
├── pyproject.toml         # Project metadata and tool configs
├── README.md              # This file
├── scripts/               # Development and utility scripts
│   ├── download_wad.py    # Script to download WAD files
│   └── setup_dev.py       # Development environment setup
├── pydoomclient/          # Main package
│   ├── __init__.py        # Package initialization
│   ├── __main__.py        # Entry point
│   ├── camera3d.py        # 3D camera and vector math
│   ├── game3d.py          # 3D game loop and input handling
│   ├── geometry3d.py      # 3D geometry conversion from 2D map data
│   ├── renderer3d.py      # 3D rendering engine
│   ├── renderer_bridge.py # Bridge between 2D and 3D renderers
│   ├── texture3d.py       # Texture management for 3D renderer
│   ├── renderer.py        # Legacy 2D rendering engine
│   └── wad.py             # WAD file parsing
├── test_3d_renderer.py    # Test script for 3D renderer
└── wads/                  # Directory for WAD files
```

### Development Commands

```bash
just setup      # Set up development environment
just run        # Run the game
just test       # Run tests
just typecheck  # Run type checking
just format     # Format code with ruff
just lint       # Lint code with ruff
just clean      # Clean build artifacts
```

### Code Style

The project uses:
- Type hints with `mypy` for type checking
- `ruff` for formatting and linting with an 88 character line limit

## Future Improvements

- Proper sector triangulation for floors and ceilings
- Advanced lighting effects
- Sprite rendering for enemies and items
- Collision detection with walls
- Weapon rendering and shooting mechanics
- Sound effects and music playback

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgements

- [Doom](https://github.com/id-Software/DOOM) - The original game by id Software
- [Freedoom](https://freedoom.github.io/) - Free content game based on the Doom engine
- [Pygame](https://www.pygame.org/) - SDL wrapper for Python used for rendering
