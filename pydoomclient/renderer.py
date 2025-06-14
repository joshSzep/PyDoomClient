"""
Renderer module for PyDoomClient.

This module handles the rendering of the game world using Pygame.
"""

import math
from dataclasses import dataclass
from typing import Optional

import pygame

from pydoomclient.wad import WADReader


@dataclass
class Vertex:
    """Vertex in 2D space."""

    x: float
    y: float


@dataclass
class LineDefinition:
    """Line definition from the WAD file."""
    start_vertex: int
    end_vertex: int
    flags: int
    special_type: int
    sector_tag: int
    front_sidedef: int
    back_sidedef: int | None = None  # -1 means no back side (one-sided)


@dataclass
class SideDef:
    """Side definition from the WAD file."""

    x_offset: int
    y_offset: int
    upper_texture: str
    lower_texture: str
    middle_texture: str
    sector: int
    flags: int


@dataclass
class Sector:
    """Sector from the WAD file."""

    floor_height: int
    ceiling_height: int
    floor_texture: str
    ceiling_texture: str
    light_level: int
    special_type: int
    tag: int


@dataclass
class Thing:
    """Thing (entity) from the WAD file."""

    x: int
    y: int
    angle: int
    type: int
    flags: int


class MapData:
    """Class to hold and process map data."""

    def __init__(self, wad_reader: WADReader, map_name: str) -> None:
        """Initialize map data from WAD reader."""
        self.wad_reader = wad_reader
        self.map_name = map_name
        self.vertices: list[Vertex] = []
        self.linedefs: list[LineDefinition] = []
        self.sidedefs: list[SideDef] = []
        self.sectors: list[Sector] = []
        self.things: list[Thing] = []

        self._load_map_data()

    def _load_map_data(self) -> None:
        """Load map data from WAD."""
        map_data = self.wad_reader.get_map_data(self.map_name)

        # Parse VERTEXES
        if "VERTEXES" in map_data:
            vertices_data = map_data["VERTEXES"]
            for i in range(0, len(vertices_data), 4):
                x = int.from_bytes(
                    vertices_data[i : i + 2], byteorder="little", signed=True
                )
                y = int.from_bytes(
                    vertices_data[i + 2 : i + 4], byteorder="little", signed=True
                )
                self.vertices.append(Vertex(x, y))

        # Parse LINEDEFS
        if "LINEDEFS" in map_data:
            linedefs_data = map_data["LINEDEFS"]
            for i in range(0, len(linedefs_data), 14):
                start_vertex = int.from_bytes(
                    linedefs_data[i : i + 2], byteorder="little"
                )
                end_vertex = int.from_bytes(
                    linedefs_data[i + 2 : i + 4], byteorder="little"
                )
                flags = int.from_bytes(linedefs_data[i + 4 : i + 6], byteorder="little")
                special_type = int.from_bytes(
                    linedefs_data[i + 6 : i + 8], byteorder="little"
                )
                sector_tag = int.from_bytes(
                    linedefs_data[i + 8 : i + 10], byteorder="little"
                )
                front_sidedef = int.from_bytes(
                    linedefs_data[i + 10 : i + 12], byteorder="little"
                )
                back_sidedef = int.from_bytes(
                    linedefs_data[i + 12 : i + 14], byteorder="little", signed=True
                )

                if back_sidedef == -1:
                    back_sidedef = None

                self.linedefs.append(
                    LineDefinition(
                        start_vertex,
                        end_vertex,
                        flags,
                        special_type,
                        sector_tag,
                        front_sidedef,
                        back_sidedef,
                    )
                )

        # Parse SIDEDEFS
        if "SIDEDEFS" in map_data:
            sidedefs_data = map_data["SIDEDEFS"]
            for i in range(0, len(sidedefs_data), 30):
                x_offset = int.from_bytes(
                    sidedefs_data[i : i + 2], byteorder="little", signed=True
                )
                y_offset = int.from_bytes(
                    sidedefs_data[i + 2 : i + 4], byteorder="little", signed=True
                )

                # Extract texture names (8 bytes each)
                upper_texture = (
                    sidedefs_data[i + 4 : i + 12].split(b"\0", 1)[0].decode("ascii")
                )
                lower_texture = (
                    sidedefs_data[i + 12 : i + 20].split(b"\0", 1)[0].decode("ascii")
                )
                middle_texture = (
                    sidedefs_data[i + 20 : i + 28].split(b"\0", 1)[0].decode("ascii")
                )

                sector = int.from_bytes(
                    sidedefs_data[i + 28 : i + 30], byteorder="little"
                )

                self.sidedefs.append(
                    SideDef(
                        x_offset,
                        y_offset,
                        upper_texture,
                        lower_texture,
                        middle_texture,
                        sector,
                        0,
                    )
                )

        # Parse SECTORS
        if "SECTORS" in map_data:
            sectors_data = map_data["SECTORS"]
            for i in range(0, len(sectors_data), 26):
                floor_height = int.from_bytes(
                    sectors_data[i : i + 2], byteorder="little", signed=True
                )
                ceiling_height = int.from_bytes(
                    sectors_data[i + 2 : i + 4], byteorder="little", signed=True
                )

                # Extract texture names (8 bytes each)
                floor_texture = (
                    sectors_data[i + 4 : i + 12].split(b"\0", 1)[0].decode("ascii")
                )
                ceiling_texture = (
                    sectors_data[i + 12 : i + 20].split(b"\0", 1)[0].decode("ascii")
                )

                light_level = int.from_bytes(
                    sectors_data[i + 20 : i + 22], byteorder="little"
                )
                special_type = int.from_bytes(
                    sectors_data[i + 22 : i + 24], byteorder="little"
                )
                tag = int.from_bytes(sectors_data[i + 24 : i + 26], byteorder="little")

                self.sectors.append(
                    Sector(
                        floor_height,
                        ceiling_height,
                        floor_texture,
                        ceiling_texture,
                        light_level,
                        special_type,
                        tag,
                    )
                )

        # Parse THINGS
        if "THINGS" in map_data:
            things_data = map_data["THINGS"]
            for i in range(0, len(things_data), 10):
                x = int.from_bytes(
                    things_data[i : i + 2], byteorder="little", signed=True
                )
                y = int.from_bytes(
                    things_data[i + 2 : i + 4], byteorder="little", signed=True
                )
                angle = int.from_bytes(things_data[i + 4 : i + 6], byteorder="little")
                thing_type = int.from_bytes(
                    things_data[i + 6 : i + 8], byteorder="little"
                )
                flags = int.from_bytes(things_data[i + 8 : i + 10], byteorder="little")

                self.things.append(Thing(x, y, angle, thing_type, flags))


class Renderer:
    """Renderer class for PyDoomClient."""

    def __init__(self, screen_width: int = 800, screen_height: int = 600) -> None:
        """Initialize the renderer."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("PyDoomClient")

        self.map_data: Optional[MapData] = None
        self.player_x = 0
        self.player_y = 0
        self.player_angle = 0
        self.fov = 60  # Field of view in degrees

        # Colors
        self.sky_color = (0, 0, 128)  # Dark blue
        self.wall_color = (128, 128, 128)  # Gray
        self.floor_color = (64, 64, 64)  # Dark gray
        self.ceiling_color = (96, 96, 96)  # Medium gray

    def load_map(self, wad_reader: WADReader, map_name: str) -> None:
        """Load map data for rendering."""
        self.map_data = MapData(wad_reader, map_name)

        # Find player start position (thing type 1)
        for thing in self.map_data.things:
            if thing.type == 1:  # Player 1 start
                self.player_x = thing.x
                self.player_y = thing.y
                # Convert to radians
                self.player_angle = thing.angle * math.pi / 180
                break

    def move_player(self, dx: float, dy: float) -> None:
        """Move the player by the given delta."""
        # Simple collision detection could be added here
        self.player_x += dx
        self.player_y += dy

    def rotate_player(self, angle_delta: float) -> None:
        """Rotate the player by the given angle delta in radians."""
        self.player_angle += angle_delta
        # Keep angle in [0, 2π)
        self.player_angle %= 2 * math.pi

    def render(self) -> None:
        """Render the current view."""
        if not self.map_data:
            # No map loaded, render a black screen
            self.screen.fill((0, 0, 0))
            return

        # Clear the screen
        self.screen.fill((0, 0, 0))

        # Draw sky, ceiling, and floor
        self._draw_background()

        # Draw walls
        self._draw_walls()

        # Update the display
        pygame.display.flip()

    def _draw_background(self) -> None:
        """Draw the sky, ceiling, and floor."""
        # Sky (top third)
        pygame.draw.rect(
            self.screen,
            self.sky_color,
            (0, 0, self.screen_width, self.screen_height // 3),
        )

        # Ceiling (middle third)
        pygame.draw.rect(
            self.screen,
            self.ceiling_color,
            (0, self.screen_height // 3, self.screen_width, self.screen_height // 3),
        )

        # Floor (bottom third)
        pygame.draw.rect(
            self.screen,
            self.floor_color,
            (
                0,
                2 * self.screen_height // 3,
                self.screen_width,
                self.screen_height // 3,
            ),
        )

    def _draw_walls(self) -> None:
        """Draw walls using raycasting."""
        if not self.map_data:
            return

        # For each vertical column on the screen
        for x in range(self.screen_width):
            # Calculate ray angle
            ray_angle = (
                self.player_angle
                - (self.fov / 2 * math.pi / 180)
                + (x / self.screen_width) * (self.fov * math.pi / 180)
            )

            # Ray direction
            ray_dir_x = math.cos(ray_angle)
            ray_dir_y = math.sin(ray_angle)

            # Find closest wall intersection
            min_dist = float("inf")
            wall_height = 0

            for linedef in self.map_data.linedefs:
                # Get vertices
                v1 = self.map_data.vertices[linedef.start_vertex]
                v2 = self.map_data.vertices[linedef.end_vertex]

                # Line segment from v1 to v2
                edge_x = v2.x - v1.x
                edge_y = v2.y - v1.y

                # Ray from player to line
                ray_to_start_x = v1.x - self.player_x
                ray_to_start_y = v1.y - self.player_y

                # Calculate determinant for intersection
                det = edge_x * (-ray_dir_y) - edge_y * (-ray_dir_x)
                
                # Define a small value for floating point comparison
                epsilon = 1e-6
                if abs(det) < epsilon:  # Ray is parallel to line
                    continue

                # Calculate intersection parameters
                t1 = (
                    ray_to_start_x * (-ray_dir_y) - ray_to_start_y * (-ray_dir_x)
                ) / det
                t2 = (ray_to_start_x * edge_y - ray_to_start_y * edge_x) / det

                # Check if intersection is valid
                if 0 <= t1 <= 1 and t2 >= 0:
                    # Calculate distance to intersection
                    dist = t2

                    # If this is the closest wall so far
                    if dist < min_dist:
                        min_dist = dist

                        # Calculate wall height based on distance
                        # Use perpendicular distance to avoid fisheye effect
                        perp_dist = dist * math.cos(ray_angle - self.player_angle)
                        wall_height = min(
                            self.screen_height, int(self.screen_height / perp_dist * 32)
                        )

            # Draw wall column
            if wall_height > 0:
                # Calculate wall top and bottom
                wall_top = max(0, (self.screen_height - wall_height) // 2)
                wall_bottom = min(
                    self.screen_height, (self.screen_height + wall_height) // 2
                )

                # Draw wall column
                pygame.draw.line(
                    self.screen, self.wall_color, (x, wall_top), (x, wall_bottom), 1
                )

    def render_2d_map(self, scale: float = 0.1) -> pygame.Surface:
        """Render a 2D top-down view of the map for debugging."""
        if not self.map_data:
            return pygame.Surface((100, 100))

        # Find map bounds
        min_x = min(v.x for v in self.map_data.vertices)
        max_x = max(v.x for v in self.map_data.vertices)
        min_y = min(v.y for v in self.map_data.vertices)
        max_y = max(v.y for v in self.map_data.vertices)

        # Calculate map dimensions
        map_width = int((max_x - min_x) * scale) + 20
        map_height = int((max_y - min_y) * scale) + 20

        # Create surface for map
        map_surface = pygame.Surface((map_width, map_height))
        map_surface.fill((0, 0, 0))

        # Draw lines
        for linedef in self.map_data.linedefs:
            v1 = self.map_data.vertices[linedef.start_vertex]
            v2 = self.map_data.vertices[linedef.end_vertex]

            # Transform to surface coordinates
            x1 = int((v1.x - min_x) * scale) + 10
            y1 = int((v1.y - min_y) * scale) + 10
            x2 = int((v2.x - min_x) * scale) + 10
            y2 = int((v2.y - min_y) * scale) + 10

            # Draw line
            pygame.draw.line(map_surface, (255, 255, 255), (x1, y1), (x2, y2), 1)

        # Draw player
        player_x = int((self.player_x - min_x) * scale) + 10
        player_y = int((self.player_y - min_y) * scale) + 10
        pygame.draw.circle(map_surface, (255, 0, 0), (player_x, player_y), 3)

        # Draw player direction
        dir_x = player_x + int(math.cos(self.player_angle) * 10)
        dir_y = player_y + int(math.sin(self.player_angle) * 10)
        pygame.draw.line(
            map_surface, (255, 0, 0), (player_x, player_y), (dir_x, dir_y), 1
        )

        return map_surface
