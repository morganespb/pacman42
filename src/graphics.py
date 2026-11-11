"""Low-level pygame drawing helpers: neon glow,
    gaussian blur, blit utilities."""

import math
import numpy as np
import pygame


def neon(speed: float = 2.0) -> float:
    """Compute a smooth oscillating value based on elapsed time.

    Args:
        speed: Oscillation speed multiplier.

    Returns:
        A value between 0.0 and 1.0, following a sine wave over time.
    """
    time = pygame.time.get_ticks() / 1000.0
    return (math.sin(time * speed) + 1.0) / 2.0


def gaussian_kernel(radius: int) -> np.ndarray:
    """Build a 1D normalized gaussian kernel for blurring.

    Args:
        radius: Kernel radius in pixels. 0 or less returns a no-op kernel.

    Returns:
        A 1D array of kernel weights summing to 1.0.
    """
    if radius <= 0:
        return np.array([1.0], dtype=np.float32)

    blur = max(radius / 2.5, 0.8)
    x = np.arange(-radius, radius + 1, dtype=np.float32)

    kernel = np.exp(-(x * x) / (2.0 * blur * blur))
    kernel /= kernel.sum()

    return kernel


def blur_axis(array: np.ndarray, kernel: np.ndarray, axis: int) -> np.ndarray:
    """Convolve a 2D array with a 1D kernel along one axis.

    Args:
        array: The 2D array to blur.
        kernel: The 1D kernel to convolve with.
        axis: The axis (0 or 1) to blur along.

    Returns:
        The blurred array, same shape as the input.
    """
    radius = len(kernel) // 2

    padding = [(0, 0), (0, 0)]
    padding[axis] = (radius, radius)

    padded = np.pad(array, padding, mode="constant")

    return np.apply_along_axis(
        lambda values: np.convolve(
            values,
            kernel,
            mode="valid",
        ),
        axis,
        padded,
    )


def gaussian_blur_alpha(alpha: np.ndarray, radius: int) -> np.ndarray:
    """Blur a 2D alpha channel with a separable gaussian filter.

    Args:
        alpha: The 2D alpha array to blur.
        radius: Blur radius in pixels.

    Returns:
        The blurred alpha array as float32.
    """
    if radius <= 0:
        return alpha.astype(np.float32)

    kernel = gaussian_kernel(radius)

    blurred = alpha.astype(np.float32)
    blurred = blur_axis(blurred, kernel, axis=0)
    blurred = blur_axis(blurred, kernel, axis=1)

    return blurred


def surface_from_alpha(
        alpha: np.ndarray,
        color: tuple[int, int, int]) -> pygame.Surface:
    """Build a colored, alpha-shaped pygame Surface from a 2D alpha array.

    Args:
        alpha: 2D array of alpha values (0-255).
        color: RGB color to fill the surface with.

    Returns:
        A Surface tinted with color, shaped by the given alpha values.
    """
    width, height = alpha.shape

    surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
    surface.fill((*color, 255))

    pixels = pygame.surfarray.pixels_alpha(surface)
    pixels[:] = np.clip(alpha, 0, 255).astype(np.uint8)

    # release Surface lock created by pixels_alpha()
    del pixels

    return surface


def tint_mask(
        mask: pygame.Surface, color: tuple[int, int, int]) -> pygame.Surface:
    """Recolor a white alpha mask into a sharp, colored surface.

    Args:
        mask: A surface whose alpha channel defines the shape to tint.
        color: RGB color to apply.

    Returns:
        A new surface with the mask's shape in the given color.
    """
    alpha = pygame.surfarray.array_alpha(mask)
    return surface_from_alpha(alpha, color)


def make_bloom(
        mask: pygame.Surface,
        color: tuple[int, int, int],
        radius: int, strength: float = 1.0) -> pygame.Surface:
    """Create a blurred, colored glow surface from a shape mask.

    Args:
        mask: A surface whose alpha channel defines the glow's shape.
        color: RGB color of the glow.
        radius: Blur radius in pixels.
        strength: Multiplier applied to the blurred alpha, controlling
            glow intensity.

    Returns:
        A new surface containing the blurred, colored glow.
    """
    alpha = pygame.surfarray.array_alpha(mask)

    blurred = gaussian_blur_alpha(alpha, radius)
    blurred *= strength

    return surface_from_alpha(blurred, color)


def combine_glows(
        size: tuple[int, int], *glows: pygame.Surface) -> pygame.Surface:
    """Additively blend multiple glow surfaces into one.

    Args:
        size: Size of the resulting surface.
        *glows: Any number of glow surfaces to combine.

    Returns:
        A single surface with all glows additively blended.
    """
    result = pygame.Surface(size, pygame.SRCALPHA, 32)

    for glow in glows:
        result.blit(glow, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    return result


def interpolated_position(
        x: int, y: int, prev_x: int, prev_y: int,
        move_timer: float, move_delay: float) -> tuple[float, float]:
    """Compute the visually interpolated position between two cells.

    Args:
        x: Current column.
        y: Current row.
        prev_x: Previous column.
        prev_y: Previous row.
        move_timer: Seconds accumulated since the last move.
        move_delay: Seconds required between two moves.

    Returns:
        The interpolated (x, y) position, in cell units.
    """
    ratio = min(move_timer / move_delay, 1.0)
    visual_x = prev_x + (x - prev_x) * ratio
    visual_y = prev_y + (y - prev_y) * ratio
    return visual_x, visual_y


def distance_between(
        x1: float, y1: float, x2: float, y2: float) -> float:
    """Compute the Euclidean distance between two points.

    Args:
        x1: First point's x coordinate.
        y1: First point's y coordinate.
        x2: Second point's x coordinate.
        y2: Second point's y coordinate.

    Returns:
        The straight-line distance between the two points.
    """
    return float(((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5)
