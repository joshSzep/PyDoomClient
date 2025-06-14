# PyDoomClient

An experimental Python Doom client that reads and interprets classic Doom WAD files, rendering a playable first-person view using Pygame.

## Features

- WAD file parsing and interpretation
- Raycasting-based first-person rendering
- WASD movement and arrow key rotation
- Debug mode with 2D map view (toggle with TAB)
- Support for Freedoom and other compatible WAD files

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

### Controls

- `W` - Move forward
- `S` - Move backward
- `A` - Strafe left
- `D` - Strafe right
- `←` - Turn left
- `→` - Turn right
- `TAB` - Toggle debug mode (shows 2D map)
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
│   ├── game.py            # Game loop and input handling
│   ├── renderer.py        # Rendering engine
│   └── wad.py             # WAD file parsing
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

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgements

- [Doom](https://github.com/id-Software/DOOM) - The original game by id Software
- [Freedoom](https://freedoom.github.io/) - Free content game based on the Doom engine
- [Pygame](https://www.pygame.org/) - SDL wrapper for Python used for rendering
