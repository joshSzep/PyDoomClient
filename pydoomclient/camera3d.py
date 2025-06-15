"""
3D Camera module for PyDoomClient.

This module provides 3D camera functionality and perspective projection
for the 3D renderer.
"""

import math
from dataclasses import dataclass
from typing import Tuple


@dataclass
class Vector3:
    """A 3D vector."""

    x: float
    y: float
    z: float

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normalize(self):
        length = self.length()
        if length > 0:
            return Vector3(self.x / length, self.y / length, self.z / length)
        return Vector3(0, 0, 0)


class Camera3D:
    """3D Camera for the renderer."""

    def __init__(
        self,
        position: Vector3,
        direction: Vector3,
        up: Vector3,
        fov: float = 60.0,
        aspect_ratio: float = 4 / 3,
        near: float = 0.1,
        far: float = 1000.0,
    ):
        """Initialize the camera.

        Args:
            position: Camera position in 3D space
            direction: Direction the camera is facing
            up: Up vector for the camera
            fov: Field of view in degrees
            aspect_ratio: Screen aspect ratio (width/height)
            near: Near clipping plane distance
            far: Far clipping plane distance
        """
        self.position = position
        self.direction = direction.normalize()
        self.up = up.normalize()
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        self.near = near
        self.far = far

        # Calculate right vector
        self.right = self.direction.cross(self.up).normalize()
        # Recalculate up vector to ensure orthogonality
        self.up = self.right.cross(self.direction).normalize()

        # Calculate projection matrix values
        self.fov_rad = math.radians(fov)
        self.tan_half_fov = math.tan(self.fov_rad / 2)

    def move(self, delta_x: float, delta_y: float, delta_z: float):
        """Move the camera by the given deltas."""
        self.position.x += delta_x
        self.position.y += delta_y
        self.position.z += delta_z

    def move_forward(self, distance: float):
        """Move the camera forward by the given distance."""
        self.position = self.position + self.direction * distance

    def move_right(self, distance: float):
        """Move the camera right by the given distance."""
        self.position = self.position + self.right * distance

    def move_up(self, distance: float):
        """Move the camera up by the given distance."""
        self.position = self.position + self.up * distance

    def rotate_yaw(self, angle: float):
        """Rotate the camera around the up vector (yaw)."""
        # Create rotation matrix around up axis
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)

        # Rotate direction vector around the up axis (Z axis in our case)
        # Reversed sin_angle to change rotation direction
        new_direction_x = self.direction.x * cos_angle + self.direction.y * sin_angle
        new_direction_y = -self.direction.x * sin_angle + self.direction.y * cos_angle
        self.direction.x = new_direction_x
        self.direction.y = new_direction_y
        self.direction = self.direction.normalize()

        # Recalculate right and up vectors
        self.right = self.direction.cross(self.up).normalize()
        self.up = self.right.cross(self.direction).normalize()

    def rotate_pitch(self, angle: float):
        """Rotate the camera around the right vector (pitch)."""
        # Create rotation matrix around right axis
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)

        # Rotate direction vector
        new_direction_y = self.direction.y * cos_angle - self.direction.z * sin_angle
        new_direction_z = self.direction.y * sin_angle + self.direction.z * cos_angle
        self.direction.y = new_direction_y
        self.direction.z = new_direction_z
        self.direction = self.direction.normalize()

        # Recalculate up vector
        self.up = self.right.cross(self.direction).normalize()
        
    def rotate(self, angle: float):
        """Rotate the camera around the up vector (convenience method)."""
        self.rotate_yaw(angle)
        
    def reset_position(self):
        """Reset the camera to a default position and orientation."""
        # Set default position (can be adjusted as needed)
        self.position = Vector3(0, 0, 0)
        
        # Set default orientation
        self.direction = Vector3(1, 0, 0).normalize()
        self.up = Vector3(0, 0, 1).normalize()
        
        # Recalculate right vector
        self.right = self.direction.cross(self.up).normalize()

    def project_point(self, point: Vector3) -> Tuple[float, float, float]:
        """Project a 3D point onto the 2D screen.

        Returns:
            Tuple of (screen_x, screen_y, depth) where screen_x and screen_y are in
            [-1, 1] range and depth is the distance from the camera.
        """
        # Vector from camera to point
        to_point = point - self.position

        # Calculate dot products for projection
        z = to_point.dot(self.direction)

        # Point is behind the camera
        if z < self.near:
            return None

        # Calculate screen coordinates
        x = to_point.dot(self.right)
        y = to_point.dot(self.up)

        # Apply perspective division
        screen_x = x / (z * self.tan_half_fov)
        screen_y = y / (z * self.tan_half_fov / self.aspect_ratio)

        return (screen_x, screen_y, z)

    def world_to_screen(
        self, point: Vector3, screen_width: int, screen_height: int
    ) -> Tuple[int, int, float]:
        """Convert a 3D world point to 2D screen coordinates.

        Args:
            point: 3D point in world space
            screen_width: Width of the screen in pixels
            screen_height: Height of the screen in pixels

        Returns:
            Tuple of (screen_x, screen_y, depth) in pixel coordinates, or None if point
            is behind camera
        """
        projected = self.project_point(point)
        if projected is None:
            return None

        screen_x, screen_y, depth = projected

        # Convert from [-1, 1] to screen coordinates
        pixel_x = int((screen_x + 1) * 0.5 * screen_width)
        pixel_y = int(
            (1 - screen_y) * 0.5 * screen_height
        )  # Y is flipped in screen space

        return (pixel_x, pixel_y, depth)
