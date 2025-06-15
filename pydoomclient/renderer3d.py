"""
3D Renderer module for PyDoomClient.

This module handles the 3D rendering of the game world using Pygame.
"""

import math
from typing import List

import numpy as np
import pygame

from pydoomclient.camera3d import Camera3D, Vector3
from pydoomclient.geometry3d import GeometryBuilder, Triangle, Wall
from pydoomclient.wad import WADReader


class Renderer3D:
    """3D Renderer class for PyDoomClient."""

    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        """Initialize the renderer.

        Args:
            screen_width: Width of the screen in pixels
            screen_height: Height of the screen in pixels
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("PyDoomClient 3D")

        # Create camera
        self.camera = Camera3D(
            position=Vector3(0, 0, 40),  # Start slightly above ground
            direction=Vector3(1, 0, 0),  # Looking along X axis
            up=Vector3(0, 0, 1),  # Z is up
            fov=60.0,
            aspect_ratio=screen_width / screen_height,
        )

        # Geometry
        self.geometry_builder = None
        self.walls: List[Wall] = []
        self.floor_triangles: List[Triangle] = []
        self.ceiling_triangles: List[Triangle] = []

        # Z-buffer for depth testing
        self.z_buffer = np.full((screen_width, screen_height), float("inf"))

        # Colors
        self.sky_color = (0, 0, 128)  # Dark blue
        self.floor_color = (64, 64, 64)  # Dark gray
        self.ceiling_color = (96, 96, 96)  # Medium gray

        # Textures
        self.textures = {}

    def load_map(self, wad_reader: WADReader, map_name: str):
        """Load map data for rendering.

        Args:
            wad_reader: WAD reader to get map data from
            map_name: Name of the map to load
        """
        # Create geometry builder
        self.geometry_builder = GeometryBuilder(wad_reader, map_name)

        # Build geometry
        self.geometry_builder.build_geometry()

        # Get geometry from builder
        self.walls = self.geometry_builder.walls
        self.floor_triangles = self.geometry_builder.floor_triangles
        self.ceiling_triangles = self.geometry_builder.ceiling_triangles

        # Set initial player position based on map data
        if self.geometry_builder.map_data and self.geometry_builder.map_data.things:
            # Find player start (thing type 1)
            for thing in self.geometry_builder.map_data.things:
                if thing.type == 1:  # Player 1 start
                    self.camera.position = Vector3(
                        thing.x, thing.y, 40
                    )  # Z is slightly above ground
                    # Convert angle from Doom format (0-359, 0 = east) to radians
                    angle_rad = math.radians(thing.angle)
                    self.camera.direction = Vector3(
                        math.cos(angle_rad), math.sin(angle_rad), 0
                    ).normalize()
                    # Recalculate camera vectors
                    self.camera.right = self.camera.direction.cross(
                        Vector3(0, 0, 1)
                    ).normalize()
                    self.camera.up = self.camera.right.cross(
                        self.camera.direction
                    ).normalize()
                    break

    def move_player(self, dx: float, dy: float, dz: float = 0):
        """Move the player by the given deltas."""
        self.camera.move(dx, dy, dz)

    def rotate_player(self, angle_delta: float):
        """Rotate the player by the given angle delta in radians."""
        self.camera.rotate(angle_delta)

    def render(self):
        """Render the current view."""
        if not self.geometry_builder:
            # No map loaded, render a black screen
            self.screen.fill((0, 0, 0))
            return

        # Clear the screen and z-buffer
        self.screen.fill(self.sky_color)
        self.z_buffer.fill(float("inf"))

        # Draw walls
        self._draw_walls()

        # Update the display
        pygame.display.flip()

    def _draw_walls(self):
        """Draw walls using 3D projection."""
        if not self.walls:
            return

        # Draw each wall
        for wall in self.walls:
            self._draw_wall(wall)

    def _draw_wall(self, wall: Wall):
        """Draw a single wall."""
        # Project wall vertices to screen space
        screen_vertices = []
        for vertex in wall.vertices:
            screen_coords = self.camera.world_to_screen(
                vertex, self.screen_width, self.screen_height
            )
            if screen_coords:
                screen_vertices.append(screen_coords)

        # If we don't have enough vertices, skip this wall
        if len(screen_vertices) < 3:
            return

        # Draw the wall as a polygon
        points = [(x, y) for x, y, _ in screen_vertices]

        # Simple backface culling
        # Calculate if this wall is facing the camera
        if len(points) >= 3:
            # Calculate 2D normal of the polygon
            x1, y1 = points[0]
            x2, y2 = points[1]
            x3, y3 = points[2]

            # Cross product in 2D to determine winding
            cross_product = (x2 - x1) * (y3 - y2) - (y2 - y1) * (x3 - x2)

            # If cross product is positive, the polygon is facing away from the camera
            if cross_product > 0:
                return

        # Draw the wall
        pygame.draw.polygon(self.screen, wall.color, points)

        # Draw outline for clarity
        pygame.draw.polygon(self.screen, (0, 0, 0), points, 1)

    def render_2d_map(self, scale: float = 0.1) -> pygame.Surface:
        """Render a 2D top-down view of the map for debugging."""
        if not self.geometry_builder or not self.geometry_builder.map_data:
            return pygame.Surface((100, 100))

        # Get the original map data
        map_data = self.geometry_builder.map_data

        # Find map bounds
        min_x = min(v.x for v in map_data.vertices)
        max_x = max(v.x for v in map_data.vertices)
        min_y = min(v.y for v in map_data.vertices)
        max_y = max(v.y for v in map_data.vertices)

        # Calculate map dimensions
        map_width = int((max_x - min_x) * scale) + 20
        map_height = int((max_y - min_y) * scale) + 20

        # Create surface for map
        map_surface = pygame.Surface((map_width, map_height))
        map_surface.fill((0, 0, 0))

        # Draw lines
        for linedef in map_data.linedefs:
            v1 = map_data.vertices[linedef.start_vertex]
            v2 = map_data.vertices[linedef.end_vertex]

            # Transform to surface coordinates
            x1 = int((v1.x - min_x) * scale) + 10
            y1 = int((v1.y - min_y) * scale) + 10
            x2 = int((v2.x - min_x) * scale) + 10
            y2 = int((v2.y - min_y) * scale) + 10

            # Draw line
            pygame.draw.line(map_surface, (255, 255, 255), (x1, y1), (x2, y2), 1)

        # Draw player
        player_x = int((self.camera.position.x - min_x) * scale) + 10
        player_y = int((self.camera.position.y - min_y) * scale) + 10
        pygame.draw.circle(map_surface, (255, 0, 0), (player_x, player_y), 3)

        # Draw player direction
        dir_x = player_x + int(self.camera.direction.x * 10)
        dir_y = player_y + int(self.camera.direction.y * 10)
        pygame.draw.line(
            map_surface, (255, 0, 0), (player_x, player_y), (dir_x, dir_y), 1
        )

        return map_surface
