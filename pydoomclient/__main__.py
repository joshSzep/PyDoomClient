"""
Main entry point for PyDoomClient.
"""

import argparse
import logging
import sys
from pathlib import Path

import structlog

from pydoomclient.game import Game


def setup_logging() -> None:
    """Configure structured logging."""
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="PyDoomClient - A Python-based Doom client"
    )
    parser.add_argument(
        "wad_file",
        type=Path,
        nargs="?",
        help="Path to WAD file to load",
    )
    parser.add_argument(
        "--list-wads",
        action="store_true",
        help="List available WAD files",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()
    setup_logging()

    logger = structlog.get_logger()

    if args.debug:
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG)
        )
        logger.debug("Debug logging enabled")

    if args.list_wads:
        from pydoomclient.wad import list_available_wads

        list_available_wads()
        return 0

    # Check for WAD file
    wad_path = args.wad_file
    if not wad_path:
        # Try to find a default WAD
        default_wad_dir = Path.home() / ".pydoomclient" / "wads"
        if default_wad_dir.exists():
            wad_files = list(default_wad_dir.glob("*.wad"))
            if wad_files:
                wad_path = wad_files[0]
                logger.info(f"Using default WAD file: {wad_path}")

    if not wad_path or not wad_path.exists():
        logger.error("No WAD file specified or found")
        print("Error: No WAD file specified or found.")
        print("Run with --list-wads to see available WAD files or specify a path.")
        print("You can download WADs using the scripts/download_wad.py script.")
        return 1

    try:
        game = Game(wad_path)
        game.run()
        return 0
    except Exception as e:
        logger.exception("Error running game", error=str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
