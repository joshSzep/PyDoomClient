"""
Renderer Bridge module for PyDoomClient.

This module provides a bridge between the old 2D renderer and the new 3D renderer,
allowing for a smooth transition between the two rendering systems.
"""

import pygame

from pydoomclient.renderer import Renderer
from pydoomclient.renderer3d import Renderer3D
from pydoomclient.texture3d import TextureManager
from pydoomclient.wad import WADReader


class RendererBridge:
    """Bridge between the old 2D renderer and the new 3D renderer."""

    def __init__(
        self, screen_width: int = 800, screen_height: int = 600, use_3d: bool = True
    ):
        """Initialize the renderer bridge.

        Args:
            screen_width: Width of the screen in pixels
            screen_height: Height of the screen in pixels
            use_3d: Whether to use the 3D renderer (True) or 2D renderer (False)
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.use_3d = use_3d

        # Create both renderers
        self.renderer_2d = Renderer(screen_width, screen_height)
        self.renderer_3d = Renderer3D(screen_width, screen_height)

        # Texture manager for 3D renderer
        self.texture_manager = None

        # Current active renderer
        self.active_renderer = self.renderer_3d if use_3d else self.renderer_2d

        # Debug mode
        self.debug = False
        self.debug_map_surface = None

    def toggle_renderer(self):
        """Toggle between 2D and 3D renderers."""
        self.use_3d = not self.use_3d
        self.active_renderer = self.renderer_3d if self.use_3d else self.renderer_2d

    def load_map(self, wad_reader: WADReader, map_name: str):
        """Load map data for rendering.

        Args:
            wad_reader: WAD reader to get map data from
            map_name: Name of the map to load
        """
        # Initialize texture manager if needed
        if self.texture_manager is None:
            self.texture_manager = TextureManager(wad_reader)

        # Load map in both renderers
        self.renderer_2d.load_map(wad_reader, map_name)
        self.renderer_3d.load_map(wad_reader, map_name)

    def move_player(self, dx: float, dy: float, dz: float = 0):
        """Move the player by the given deltas."""
        # Move player in both renderers
        self.renderer_2d.move_player(dx, dy)
        self.renderer_3d.move_player(dx, dy, dz)

    def rotate_player(self, angle_delta: float):
        """Rotate the player by the given angle delta in radians."""
        # Rotate player in both renderers
        self.renderer_2d.rotate_player(angle_delta)
        self.renderer_3d.rotate_player(angle_delta)

    def render(self):
        """Render the current view."""
        # Render using the active renderer
        self.active_renderer.render()

        # Render debug map if enabled
        if self.debug:
            self.debug_map_surface = self.active_renderer.render_2d_map()
            if self.debug_map_surface:
                self.active_renderer.screen.blit(self.debug_map_surface, (10, 10))
                pygame.display.flip()

    def set_debug(self, debug: bool):
        """Set debug mode."""
        self.debug = debug
