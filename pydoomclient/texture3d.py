"""
Texture handling module for PyDoomClient 3D renderer.

This module handles loading, processing, and applying textures from WAD files
for the 3D renderer.
"""

from typing import Dict, Optional, Tuple

import pygame

from pydoomclient.wad import WADReader


class TextureManager:
    """Manages textures for the 3D renderer."""

    def __init__(self, wad_reader: Optional[WADReader] = None):
        """Initialize the texture manager.

        Args:
            wad_reader: WAD reader to load textures from
        """
        self.wad_reader = wad_reader
        self.textures: Dict[str, pygame.Surface] = {}
        self.default_texture = self._create_default_texture()

        # If a WAD reader is provided, preload some common textures
        if wad_reader:
            self.preload_common_textures()

    def _create_default_texture(self) -> pygame.Surface:
        """Create a default checkerboard texture."""
        size = 64
        texture = pygame.Surface((size, size))

        # Create a checkerboard pattern
        square_size = size // 8
        for y in range(0, size, square_size):
            for x in range(0, size, square_size):
                color = (
                    (128, 128, 128)
                    if (x // square_size + y // square_size) % 2 == 0
                    else (64, 64, 64)
                )
                pygame.draw.rect(texture, color, (x, y, square_size, square_size))

        return texture

    def preload_common_textures(self):
        """Preload common textures from the WAD file."""
        if not self.wad_reader:
            return

        # Common Doom texture names
        common_textures = [
            "STARTAN",
            "STARG1",
            "STARG2",
            "STARG3",  # Star textures
            "BROWN1",
            "BROWN96",
            "BROWNGRN",  # Brown textures
            "COMP",
            "COMPBLUE",
            "COMPSPAN",  # Computer textures
            "DOOR1",
            "DOOR3",
            "DOORBLU",
            "DOORRED",  # Door textures
            "FLAT1",
            "FLAT5",
            "FLAT14",  # Flat textures
            "FLOOR0_1",
            "FLOOR0_3",
            "FLOOR4_8",  # Floor textures
            "CEIL1_1",
            "CEIL3_1",
            "CEIL3_2",  # Ceiling textures
        ]

        # Try to load each texture
        for name in common_textures:
            self.load_texture(name)

    def load_texture(self, name: str) -> bool:
        """Load a texture from the WAD file.

        Args:
            name: Name of the texture to load

        Returns:
            True if the texture was loaded successfully, False otherwise
        """
        if not self.wad_reader:
            return False

        if name in self.textures:
            return True

        # Try to load the texture from the WAD
        texture_data = self.wad_reader.get_lump_data(name)
        if not texture_data:
            return False

        # For now, we'll create a simple colored texture based on the name
        # In a real implementation, we would parse the actual texture data
        # from the WAD file, which is quite complex

        # Create a simple colored texture
        color = self._hash_string_to_color(name)
        texture = pygame.Surface((64, 64))
        texture.fill(color)

        # Add some visual interest with clamped color values
        darker = (max(0, min(255, color[0] - 20)), 
                 max(0, min(255, color[1] - 20)), 
                 max(0, min(255, color[2] - 20)))
        lighter = (max(0, min(255, color[0] + 20)), 
                  max(0, min(255, color[1] + 20)), 
                  max(0, min(255, color[2] + 20)))
        
        pygame.draw.rect(texture, darker, (0, 0, 64, 64), 2)
        pygame.draw.rect(texture, lighter, (4, 4, 56, 56), 1)

        self.textures[name] = texture
        return True

    def _hash_string_to_color(self, s: str) -> Tuple[int, int, int]:
        """Convert a string to a color using a simple hash function."""
        hash_val = 0
        for c in s:
            hash_val = (hash_val * 31 + ord(c)) & 0xFFFFFF

        r = (hash_val & 0xFF0000) >> 16
        g = (hash_val & 0x00FF00) >> 8
        b = hash_val & 0x0000FF

        # Ensure minimum brightness
        r = max(64, r)
        g = max(64, g)
        b = max(64, b)

        return (r, g, b)

    def get_texture(self, name: str) -> pygame.Surface:
        """Get a texture by name.

        Args:
            name: Name of the texture to get

        Returns:
            The requested texture, or the default texture if not found
        """
        if not name or name == "-" or name not in self.textures:
            # Try to load the texture
            if name and name != "-" and self.load_texture(name):
                return self.textures[name]
            return self.default_texture

        return self.textures[name]

    def apply_texture_to_wall(
        self,
        surface: pygame.Surface,
        wall_rect: pygame.Rect,
        texture_name: str,
        u_offset: float = 0,
        v_offset: float = 0,
    ):
        """Apply a texture to a wall rectangle on the given surface.

        Args:
            surface: Surface to draw on
            wall_rect: Rectangle defining the wall area
            texture_name: Name of the texture to apply
            u_offset: Horizontal texture offset (0-1)
            v_offset: Vertical texture offset (0-1)
        """
        texture = self.get_texture(texture_name)

        # Scale texture to fit wall
        scaled_texture = pygame.transform.scale(
            texture, (wall_rect.width, wall_rect.height)
        )

        # Apply offsets (simple implementation)
        u_pixels = int(u_offset * texture.get_width()) % texture.get_width()
        v_pixels = int(v_offset * texture.get_height()) % texture.get_height()

        if u_pixels > 0 or v_pixels > 0:
            # Create a subsurface with the offset
            temp = pygame.Surface(
                (scaled_texture.get_width(), scaled_texture.get_height())
            )
            temp.blit(scaled_texture, (-u_pixels, -v_pixels))
            temp.blit(
                scaled_texture, (scaled_texture.get_width() - u_pixels, -v_pixels)
            )
            temp.blit(
                scaled_texture, (-u_pixels, scaled_texture.get_height() - v_pixels)
            )
            temp.blit(
                scaled_texture,
                (
                    scaled_texture.get_width() - u_pixels,
                    scaled_texture.get_height() - v_pixels,
                ),
            )
            scaled_texture = temp

        # Blit the texture onto the surface
        surface.blit(scaled_texture, wall_rect)
