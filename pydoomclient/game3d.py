"""
Game3D module for PyDoomClient.

This module contains a 3D-enabled Game class that uses the new 3D renderer.
"""

import sys
import time
from pathlib import Path

import pygame
import structlog

from pydoomclient.renderer3d import Renderer3D
from pydoomclient.wad import WADReader


class Game3D:
    """3D-enabled game class for PyDoomClient."""

    def __init__(self, wad_path: Path) -> None:
        """Initialize the game with a WAD file."""
        self.logger = structlog.get_logger()
        self.wad_path = wad_path
        self.running = False
        self.clock = pygame.time.Clock()
        self.fps = 60

        # Movement and rotation speeds
        self.move_speed = 5.0
        self.rotation_speed = 0.05  # radians per frame
        self.mouse_sensitivity = 0.002  # mouse sensitivity factor

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
                current_map=self.current_map,
            )
        except Exception as e:
            self.logger.error("Failed to load WAD file", error=str(e))
            raise

        # Initialize 3D renderer
        self.renderer = Renderer3D()
        self.renderer.load_map(self.wad_reader, self.current_map)

        # Debug mode
        self.debug = False

        # Key repeat delay and interval
        pygame.key.set_repeat(200, 50)  # 200ms delay, 50ms interval
        
        # Mouse settings
        pygame.mouse.set_visible(False)  # Hide the mouse cursor
        pygame.event.set_grab(True)  # Capture the mouse
        self.mouse_look_enabled = True
        self.last_mouse_pos = pygame.mouse.get_pos()

    def handle_input(self) -> None:
        """Handle user input."""
        keys = pygame.key.get_pressed()

        # Handle mouse movement for camera rotation if enabled
        if self.mouse_look_enabled:
            current_mouse_pos = pygame.mouse.get_pos()
            mouse_dx = current_mouse_pos[0] - self.last_mouse_pos[0]
            
            # Apply mouse movement to camera rotation
            if mouse_dx != 0:
                self.renderer.camera.rotate(mouse_dx * self.mouse_sensitivity)
            
            # Reset mouse position to center of screen to allow continuous rotation
            center_x = pygame.display.get_surface().get_width() // 2
            center_y = pygame.display.get_surface().get_height() // 2
            pygame.mouse.set_pos(center_x, center_y)
            self.last_mouse_pos = (center_x, center_y)

        # Movement
        move_x = 0
        move_y = 0
        move_z = 0

        # Forward/backward movement
        if keys[pygame.K_w]:  # Forward
            move_x += self.move_speed * self.renderer.camera.direction.x
            move_y += self.move_speed * self.renderer.camera.direction.y

        if keys[pygame.K_s]:  # Backward
            move_x -= self.move_speed * self.renderer.camera.direction.x
            move_y -= self.move_speed * self.renderer.camera.direction.y

        # Strafe left/right
        if keys[pygame.K_a]:  # Strafe left
            move_x += self.move_speed * self.renderer.camera.right.x
            move_y += self.move_speed * self.renderer.camera.right.y

        if keys[pygame.K_d]:  # Strafe right
            move_x -= self.move_speed * self.renderer.camera.right.x
            move_y -= self.move_speed * self.renderer.camera.right.y

        # Vertical movement (for debugging/testing)
        if keys[pygame.K_q]:  # Move up
            move_z += self.move_speed

        if keys[pygame.K_e]:  # Move down
            move_z -= self.move_speed

        # Apply movement
        if move_x != 0 or move_y != 0 or move_z != 0:
            self.renderer.camera.move(move_x, move_y, move_z)

        # Keyboard rotation (as backup or alternative to mouse)
        if keys[pygame.K_LEFT]:  # Turn left
            self.renderer.camera.rotate(-self.rotation_speed)

        if keys[pygame.K_RIGHT]:  # Turn right
            self.renderer.camera.rotate(self.rotation_speed)

        # Reset camera position (replacing the toggle renderer functionality)
        if keys[pygame.K_r]:
            self.renderer.camera.reset_position()
            time.sleep(0.2)  # Simple debounce

        # Debug mode toggle
        if keys[pygame.K_TAB]:
            self.debug = not self.debug
            self.renderer.debug = self.debug
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
                        elif event.key == pygame.K_m:  # Toggle mouse look
                            self.mouse_look_enabled = not self.mouse_look_enabled
                            pygame.mouse.set_visible(not self.mouse_look_enabled)
                            pygame.event.set_grab(self.mouse_look_enabled)

                # Handle input
                self.handle_input()

                # Render
                self.renderer.render()

                # Cap the frame rate
                self.clock.tick(self.fps)

                # Display FPS in window title
                pygame.display.set_caption(
                    f"PyDoomClient 3D - FPS: {int(self.clock.get_fps())}"
                )

        except Exception as e:
            self.logger.error("Error in game loop", error=str(e))
            raise

        finally:
            # Release mouse before quitting
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(False)
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
        print("Usage: python -m pydoomclient.game3d <wad_file>")
        sys.exit(1)

    wad_path = Path(sys.argv[1])
    game = Game3D(wad_path)
    game.run()
