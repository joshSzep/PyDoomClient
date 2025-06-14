# PyDoomClient justfile
# Use with https://github.com/casey/just

# List available commands
default:
    @just --list

# Setup development environment
setup:
    @echo "Setting up development environment..."
    uv venv
    uv pip install -e ".[dev]"
    @echo "Development environment setup complete!"

# Run the game
run *args:
    uv run python -m pydoomclient {{args}}

# Download WAD files for testing
download-wad:
    uv run python scripts/download_wad.py

# Run tests
test:
    pytest

# Run type checking
typecheck:
    mypy pydoomclient

# Format code
format:
    ruff format pydoomclient tests

# Lint code
lint:
    ruff check pydoomclient tests
    mypy pydoomclient

# Clean build artifacts
clean:
    rm -rf build/
    rm -rf dist/
    rm -rf *.egg-info/
    find . -type d -name __pycache__ -exec rm -rf {} +
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete
    find . -type f -name "*.pyd" -delete
    find . -type f -name ".coverage" -delete
    find . -type d -name "*.egg-info" -exec rm -rf {} +
    find . -type d -name "*.egg" -exec rm -rf {} +
