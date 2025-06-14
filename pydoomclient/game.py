"""
Game module for PyDoomClient.

This module contains the main Game class that ties together the WAD parsing,
rendering, and input handling.
"""
import math
import sys
import time
from pathlib import Path
from typing import Optional

import pygame
import structlog

from pydoomclient.renderer import Renderer
from pydoomclient.wad import WADReader


class Game:
    """Main game class for PyDoomClient."""

    def __init__(self, wad_path: Path) -> None:
        """Initialize the game with a WAD file."""
        self.logger = structlog.get_logger()
        self.wad_path = wad_path
        self.running = False
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.move_speed = 5.0
        self.rotation_speed = 0.05  # radians per frame
        
        # Initialize pygame
        pygame.init()
        
        # Load WAD file
        self.logger.info("Loading WAD file", wad_path=str(wad_path))
        try:
            self.wad_reader = WADReader(wad_path)
            if not self.wad_reader.maps:
                self.logger.error("No maps found in WAD file")
                raise ValueError("No maps found in WAD file")
            
            self.current_map = self.wad_reader.maps[0]
            self.logger.info(
                "WAD file loaded",
                maps=self.wad_reader.maps,
                current_map=self.current_map
            )
        except Exception as e:
            self.logger.error("Failed to load WAD file", error=str(e))
            raise
        
        # Initialize renderer
        self.renderer = Renderer()
        self.renderer.load_map(self.wad_reader, self.current_map)
        
        # Debug mode
        self.debug = False
        self.debug_map_surface: Optional[pygame.Surface] = None

    def handle_input(self) -> None:
        """Handle user input."""
        keys = pygame.key.get_pressed()
        
        # Movement
        move_x = 0
        move_y = 0
        
        if keys[pygame.K_w]:  # Forward
            move_x += self.move_speed * pygame.math.Vector2.normalize(
                pygame.math.Vector2(
                    math.cos(self.renderer.player_angle),
                    math.sin(self.renderer.player_angle)
                )
            ).x
            move_y += self.move_speed * pygame.math.Vector2.normalize(
                pygame.math.Vector2(
                    math.cos(self.renderer.player_angle),
                    math.sin(self.renderer.player_angle)
                )
            ).y
        
        if keys[pygame.K_s]:  # Backward
            move_x -= self.move_speed * pygame.math.Vector2.normalize(
                pygame.math.Vector2(
                    math.cos(self.renderer.player_angle),
                    math.sin(self.renderer.player_angle)
                )
            ).x
            move_y -= self.move_speed * pygame.math.Vector2.normalize(
                pygame.math.Vector2(
                    math.cos(self.renderer.player_angle),
                    math.sin(self.renderer.player_angle)
                )
            ).y
        
        if keys[pygame.K_a]:  # Strafe left
            move_x += self.move_speed * pygame.math.Vector2.normalize(
                pygame.math.Vector2(
                    math.cos(self.renderer.player_angle - math.pi / 2),
                    math.sin(self.renderer.player_angle - math.pi / 2)
                )
            ).x
            move_y += self.move_speed * pygame.math.Vector2.normalize(
                pygame.math.Vector2(
                    math.cos(self.renderer.player_angle - math.pi / 2),
                    math.sin(self.renderer.player_angle - math.pi / 2)
                )
            ).y
        
        if keys[pygame.K_d]:  # Strafe right
            move_x += self.move_speed * pygame.math.Vector2.normalize(
                pygame.math.Vector2(
                    math.cos(self.renderer.player_angle + math.pi / 2),
                    math.sin(self.renderer.player_angle + math.pi / 2)
                )
            ).x
            move_y += self.move_speed * pygame.math.Vector2.normalize(
                pygame.math.Vector2(
                    math.cos(self.renderer.player_angle + math.pi / 2),
                    math.sin(self.renderer.player_angle + math.pi / 2)
                )
            ).y
        
        # Apply movement
        if move_x != 0 or move_y != 0:
            self.renderer.move_player(move_x, move_y)
        
        # Rotation
        if keys[pygame.K_LEFT]:  # Turn left
            self.renderer.rotate_player(-self.rotation_speed)
        
        if keys[pygame.K_RIGHT]:  # Turn right
            self.renderer.rotate_player(self.rotation_speed)
        
        # Debug mode toggle
        if keys[pygame.K_TAB]:
            self.debug = not self.debug
            time.sleep(0.2)  # Simple debounce

    def run(self) -> None:
        """Run the game loop."""
        self.running = True
        self.logger.info("Starting game loop")
        
        try:
            while self.running:
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                
                # Handle input
                self.handle_input()
                
                # Render
                self.renderer.render()
                
                # Debug rendering
                if self.debug:
                    self.debug_map_surface = self.renderer.render_2d_map()
                    if self.debug_map_surface:
                        self.renderer.screen.blit(
                            self.debug_map_surface,
                            (10, 10)
                        )
                        pygame.display.flip()
                
                # Cap the frame rate
                self.clock.tick(self.fps)
        
        except Exception as e:
            self.logger.error("Error in game loop", error=str(e))
            raise
        
        finally:
            self.logger.info("Shutting down")
            pygame.quit()

    def change_map(self, map_name: str) -> None:
        """Change to a different map in the WAD."""
        if map_name not in self.wad_reader.maps:
            self.logger.error("Map not found", map_name=map_name)
            return
        
        self.current_map = map_name
        self.logger.info("Changing map", map_name=map_name)
        self.renderer.load_map(self.wad_reader, map_name)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m pydoomclient.game <wad_file>")
        sys.exit(1)
    
    wad_path = Path(sys.argv[1])
    game = Game(wad_path)
    game.run()
