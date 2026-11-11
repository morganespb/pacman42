"""Neon-styled rendering of the maze, player, ghosts, pacgums, and HUD."""

import pygame
from .graphics import (
    combine_glows, make_bloom, tint_mask, neon, interpolated_position)
from .maze.maze import Cell, Direction, Maze
from .player import Player
from .ghost import Ghost
from .game import GhostMode
from .constants import (CELL_SIZE, MARGIN, HUD_HEIGHT, HUD_COLOR, FONT,
                        FORTY_TWO_COLOR, FORTY_TWO_GLOW, FORTY_TWO_WIDTH,
                        PACMAN_COLOR, PACMAN_GLOW_COLOR, WALL_COLOR,
                        WALL_GLOW_COLOR, WALL_WIDTH,
                        GHOSTS_IT_IMAGES, GHOSTS_PC_IMAGES, LIFE_SIZE,
                        LIFE_IMAGE, PACGUM_COLOR, PACGUM_RADIUS,
                        SUPER_PACGUM_INNER_RADIUS, SUPER_PACGUM_OUTER_RADIUS,
                        SUPER_PACGUM_CORE_RADIUS, SCARED_GHOST_IMAGE
                        )

__all__ = [
    "CELL_SIZE", "MARGIN", "HUD_HEIGHT",
    "draw_maze", "draw_player", "draw_hud", "draw_pacgums",
    "draw_super_pacgums", "draw_ghosts",
]

# Cache of built maze surfaces, keyed by (maze id, screen size), since
# the maze's static graphics don't change frame to frame.
maze_cache: dict[tuple[int, tuple[int, int]], tuple[
        pygame.Surface,
        pygame.Surface,
        pygame.Surface,
        pygame.Surface,
    ],
] = {}


def draw_outer_frame(surface: pygame.Surface, maze: Maze) -> None:
    """Draw the maze's outer border rectangle into a mask surface.

    Args:
        surface: Mask surface to draw onto.
        maze: The maze being framed.
    """
    width = maze.width * CELL_SIZE
    height = maze.height * CELL_SIZE

    rect = pygame.Rect(MARGIN, HUD_HEIGHT + MARGIN, width, height)
    pygame.draw.rect(surface, (255, 255, 255, 255), rect, WALL_WIDTH, 12)


def draw_mask_line(
        surface: pygame.Surface,
        start: tuple[int, int], end: tuple[int, int], width: int) -> None:
    """Draw a single opaque white line into a mask surface.

    Args:
        surface: Mask surface to draw onto.
        start: Line start point.
        end: Line end point.
        width: Line thickness in pixels.
    """
    pygame.draw.line(surface, (255, 255, 255, 255), start, end, width)


def draw_normal_cell(
        mask: pygame.Surface, maze: Maze,
        cell: Cell, x: int, y: int, px: int, py: int) -> None:
    """Draw a regular cell's walls into the maze mask.

    Skips walls that border a '42' cell, since those are drawn separately
    by draw_42_contour.

    Args:
        mask: Mask surface to draw onto.
        maze: The maze being drawn.
        cell: The cell being drawn.
        x: Cell column index.
        y: Cell row index.
        px: Cell's pixel x position.
        py: Cell's pixel y position.
    """
    # NORTH
    if (y > 0 and cell.walls[Direction.NORTH]
            and not maze.get_cell(x, y - 1).is_42):
        draw_mask_line(mask, (px, py), (px + CELL_SIZE, py), WALL_WIDTH)

    # SOUTH
    if (y < maze.height - 1 and cell.walls[Direction.SOUTH]
            and not maze.get_cell(x, y + 1).is_42):
        draw_mask_line(mask, (px, py + CELL_SIZE),
                       (px + CELL_SIZE, py + CELL_SIZE), WALL_WIDTH)

    # WEST
    if (x > 0 and cell.walls[Direction.WEST]
            and not maze.get_cell(x - 1, y).is_42):
        draw_mask_line(mask, (px, py), (px, py + CELL_SIZE), WALL_WIDTH)

    # EAST
    if (x < maze.width - 1 and cell.walls[Direction.EAST]
            and not maze.get_cell(x + 1, y).is_42):
        draw_mask_line(mask, (px + CELL_SIZE, py),
                       (px + CELL_SIZE, py + CELL_SIZE), WALL_WIDTH)


def draw_42_contour(
        mask: pygame.Surface, maze: Maze,
        x: int, y: int, px: int, py: int) -> None:
    """Draw only the outer contour of a '42' cell into the '42' mask.

    Internal borders between two adjacent '42' cells are skipped, so the
    shape reads as one solid outline rather than a grid.

    Args:
        mask: Mask surface to draw onto.
        maze: The maze being drawn.
        x: Cell column index.
        y: Cell row index.
        px: Cell's pixel x position.
        py: Cell's pixel y position.
    """
    # NORTH
    if (y == 0 or not maze.get_cell(x, y - 1).is_42):
        draw_mask_line(mask, (px, py), (px + CELL_SIZE, py), FORTY_TWO_WIDTH)

    # SOUTH
    if (y == maze.height - 1 or not maze.get_cell(x, y + 1,).is_42):
        draw_mask_line(mask, (px, py + CELL_SIZE),
                       (px + CELL_SIZE, py + CELL_SIZE), FORTY_TWO_WIDTH)

    # WEST
    if (x == 0 or not maze.get_cell(x - 1, y).is_42):
        draw_mask_line(mask, (px, py), (px, py + CELL_SIZE), FORTY_TWO_WIDTH,)

    # EAST
    if (x == maze.width - 1 or not maze.get_cell(x + 1, y).is_42):
        draw_mask_line(mask, (px + CELL_SIZE, py),
                       (px + CELL_SIZE, py + CELL_SIZE), FORTY_TWO_WIDTH)


def build_maze_surfaces(screen: pygame.Surface, maze: Maze) -> tuple[
        pygame.Surface,
        pygame.Surface,
        pygame.Surface,
        pygame.Surface,
]:
    """Build the four neon layers (normal/42 x glow/core) for a maze.

    Args:
        screen: The game's display surface (used for sizing).
        maze: The maze to render.

    Returns:
        A tuple of (normal_glow, normal_core, forty_two_glow,
        forty_two_core) surfaces.
    """
    size = screen.get_size()

    normal_mask = pygame.Surface(size, pygame.SRCALPHA, 32)
    forty_two_mask = pygame.Surface(size, pygame.SRCALPHA, 32)
    draw_outer_frame(normal_mask, maze)

    for y in range(maze.height):
        for x in range(maze.width):
            cell = maze.get_cell(x, y)

            px = (MARGIN + x * CELL_SIZE)
            py = (HUD_HEIGHT + MARGIN + y * CELL_SIZE)

            if cell.is_42:
                draw_42_contour(forty_two_mask, maze, x, y, px, py)
            else:
                draw_normal_cell(normal_mask, maze, cell, x, y, px, py)

    # Sharp wall surfaces
    normal_core = tint_mask(normal_mask, WALL_COLOR,)
    forty_two_core = tint_mask(forty_two_mask, FORTY_TWO_COLOR)

    # REAL blurred bloom
    normal_outer = make_bloom(normal_mask, WALL_GLOW_COLOR, 8, 0.45)
    normal_inner = make_bloom(normal_mask, WALL_GLOW_COLOR, 3, 0.90)
    normal_glow = combine_glows(size, normal_outer, normal_inner)

    # 42 is brighter and spreads farther
    forty_two_outer = make_bloom(forty_two_mask, FORTY_TWO_GLOW, 11, 0.75)
    forty_two_middle = make_bloom(forty_two_mask, FORTY_TWO_GLOW, 6, 0.90)
    forty_two_inner = make_bloom(forty_two_mask, FORTY_TWO_GLOW, 2, 1.15)
    forty_two_glow = combine_glows(
            size, forty_two_outer, forty_two_middle, forty_two_inner)

    return (normal_glow, normal_core, forty_two_glow, forty_two_core)


def get_maze_surfaces(screen: pygame.Surface, maze: Maze) -> tuple[
        pygame.Surface,
        pygame.Surface,
        pygame.Surface,
        pygame.Surface,
]:
    """Get cached maze surfaces, building them once per (maze, size).

    Args:
        screen: The game's display surface.
        maze: The maze to render.

    Returns:
        The cached (or newly built) tuple of maze surfaces.
    """
    key = (id(maze), screen.get_size())

    if key not in maze_cache:
        maze_cache[key] = (build_maze_surfaces(screen, maze))

    return maze_cache[key]


def draw_maze(screen: pygame.Surface, maze: Maze) -> None:
    """Draw the full neon maze, with a pulsing glow on the '42' shape.

    Args:
        screen: Surface to draw onto.
        maze: The maze to render.
    """
    (normal_glow, normal_core, forty_two_glow, forty_two_core) = (
            get_maze_surfaces(screen, maze)
        )

    # normal maze: stable glow
    screen.blit(normal_glow, (0, 0))
    screen.blit(normal_core, (0, 0))

    # 42: pulsing glow
    pulse = (0.65 + neon(1.8) * 0.35)
    pulsing_glow = (forty_two_glow.copy())
    pulsing_glow.set_alpha(int(255 * pulse))

    screen.blit(pulsing_glow, (0, 0))

    # keep neon tube sharp
    screen.blit(forty_two_core, (0, 0))


def player_mouth(
        direction: Direction,
        center: int, radius: int) -> list[tuple[int, int]]:
    """Compute the triangle points for Pac-Man's open mouth.

    Args:
        direction: Direction the mouth should face.
        center: Center coordinate (same for x and y) of the player sprite.
        radius: Radius of the player sprite.

    Returns:
        Three (x, y) points forming the mouth triangle.
    """
    if direction == Direction.EAST:
        return [
            (center, center),
            (center + radius, center - radius // 2),
            (center + radius, center + radius // 2)
        ]

    if direction == Direction.WEST:
        return [
            (center, center),
            (center - radius, center - radius // 2),
            (center - radius, center + radius // 2)
        ]

    if direction == Direction.NORTH:
        return [
            (center, center),
            (center - radius // 2, center - radius),
            (center + radius // 2, center - radius)
        ]

    return [
        (center, center),
        (center - radius // 2, center + radius),
        (center + radius // 2, center + radius),
    ]


def draw_player(screen: pygame.Surface, player: Player) -> None:
    """Draw the player as a glowing Pac-Man with an animated mouth.

    Position is visually interpolated between the player's previous
    and current cell, for smooth movement between moves.

    Args:
        screen: Surface to draw onto.
        player: The player to render.
    """
    radius = CELL_SIZE // 3
    padding = 14
    local_size = (radius * 2 + padding * 2 + 1)
    center = (local_size // 2)

    mask = pygame.Surface((local_size, local_size), pygame.SRCALPHA, 32)

    pygame.draw.circle(mask, (255, 255, 255, 255), (center, center), radius)

    mouth_open = (pygame.time.get_ticks() // 150) % 2 == 0

    if mouth_open:
        pygame.draw.polygon(mask, (0, 0, 0, 0), player_mouth(
                player.direction,
                center,
                radius,
            ),
        )

    core = tint_mask(mask, PACMAN_COLOR)

    outer_glow = make_bloom(mask, PACMAN_GLOW_COLOR, radius=7, strength=0.75)
    inner_glow = make_bloom(mask, PACMAN_GLOW_COLOR, radius=3, strength=1.10)

    player_glow = combine_glows(
            (local_size, local_size), outer_glow, inner_glow)

    visual_x, visual_y = interpolated_position(
        player.x, player.y, player.prev_x, player.prev_y,
        player.move_timer, player.move_delay)

    center_x = (MARGIN + visual_x * CELL_SIZE + CELL_SIZE // 2)
    center_y = (HUD_HEIGHT + MARGIN + visual_y * CELL_SIZE + CELL_SIZE // 2)

    position = (center_x - center, center_y - center)

    screen.blit(player_glow, position)
    screen.blit(core, position)


def draw_hud(
        screen: pygame.Surface, score: int, lives: int, level: int,
        time_left: int, cheat_mode: bool) -> None:
    """Draw the top HUD bar: score, level, time left, and lives.

    Args:
        screen: Surface to draw onto.
        score: Current score.
        lives: Remaining lives.
        level: Current level number (1-indexed for display).
        time_left: Seconds remaining for the current level.
        cheat_mode: If True, shows a stylized "infinite lives" indicator
            instead of individual life icons.
    """
    width = screen.get_width()
    y = HUD_HEIGHT // 2
    font = pygame.font.Font(FONT, 18)

    # Divide the HUD into four equal areas
    score_x = width // 8
    level_x = width * 3 // 8
    time_x = width * 5 // 8
    lives_x = width * 7 // 8

    score_text = font.render(f"SCORE {score}", True, HUD_COLOR)
    level_text = font.render(f"LEVEL {level}", True, HUD_COLOR)
    time_text = font.render(f"TIME {time_left}", True, HUD_COLOR)
    screen.blit(score_text, score_text.get_rect(center=(score_x, y)))
    screen.blit(level_text, level_text.get_rect(center=(level_x, y)))
    screen.blit(time_text, time_text.get_rect(center=(time_x, y)))

    # draw lives
    if cheat_mode:
        icon_rect = LIFE_IMAGE.get_rect(center=(lives_x - 20, y))
        screen.blit(LIFE_IMAGE, icon_rect)
        lives_left = lives + 10
        lives_text = font.render(f"x {lives_left}", True, HUD_COLOR)

        text_rect = lives_text.get_rect(midleft=(lives_x + 5, y))
        screen.blit(lives_text, text_rect)

    else:
        gap = 5
        total_width = lives * LIFE_SIZE + max(0, lives - 1) * gap
        start_x = lives_x - total_width // 2

        for i in range(lives):
            x = start_x + i * (LIFE_SIZE + gap)
            rect = LIFE_IMAGE.get_rect(center=(x + LIFE_SIZE // 2, y))

            screen.blit(LIFE_IMAGE, rect)


def draw_pacgums(
        screen: pygame.Surface, pacgums: set[tuple[int, int]]) -> None:
    """Draw every remaining pacgum as a small dot.

    Args:
        screen: Surface to draw onto.
        pacgums: Coordinates of remaining pacgums.
    """
    for x, y in pacgums:
        center_x = MARGIN + x * CELL_SIZE + CELL_SIZE // 2
        center_y = HUD_HEIGHT + MARGIN + y * CELL_SIZE + CELL_SIZE // 2

        pygame.draw.circle(screen,
                           PACGUM_COLOR,
                           (center_x, center_y),
                           PACGUM_RADIUS)


def draw_super_pacgums(
        screen: pygame.Surface, super_pacgums: set[tuple[int, int]]) -> None:
    """Draw every remaining super pacgum with a pulsing glow.

    Args:
        screen: Surface to draw onto.
        super_pacgums: Coordinates of remaining super pacgums.
    """
    pulse = 0.7 + neon(3.0) * 0.3

    for x, y in super_pacgums:
        center_x = MARGIN + x * CELL_SIZE + CELL_SIZE // 2
        center_y = HUD_HEIGHT + MARGIN + y * CELL_SIZE + CELL_SIZE // 2

        glow = pygame.Surface(screen.get_size(), pygame.SRCALPHA)

        pygame.draw.circle(
                glow, (*PACGUM_COLOR, int(40 * pulse)),
                (center_x, center_y), SUPER_PACGUM_OUTER_RADIUS)
        pygame.draw.circle(
                glow, (*PACGUM_COLOR, int(90 * pulse)),
                (center_x, center_y), SUPER_PACGUM_INNER_RADIUS)

        screen.blit(glow, (0, 0))

        pygame.draw.circle(screen, PACGUM_COLOR, (center_x, center_y),
                           SUPER_PACGUM_CORE_RADIUS)


def draw_ghosts(
        screen: pygame.Surface, ghosts: list[Ghost], mode: GhostMode) -> None:
    """Draw every ghost using its sprite for the current ghost mode.

    Edible ghosts use the shared "scared" sprite regardless of mode.
    Ghosts respawning after being eaten flicker (alternating alpha)
    to show their temporary immunity. Position is visually
    interpolated for smooth movement.

    Args:
        screen: Surface to draw onto.
        ghosts: Ghosts to render.
        mode: Which cosmetic skin set to use (CLASSIC or STAFF).
    """
    images = GHOSTS_PC_IMAGES

    if mode == GhostMode.STAFF:
        images = GHOSTS_IT_IMAGES

    for ghost, image in zip(ghosts, images):
        if ghost.edible:
            image = SCARED_GHOST_IMAGE

        if ghost.respawn_timer > 0:
            alpha = int(128 + 127 * neon(6.0))
            image = image.copy()
            image.set_alpha(alpha)

        visual_x, visual_y = interpolated_position(
            ghost.x, ghost.y, ghost.prev_x, ghost.prev_y,
            ghost.move_timer, ghost.move_delay)

        center_x = MARGIN + visual_x * CELL_SIZE + CELL_SIZE // 2
        center_y = HUD_HEIGHT + MARGIN + visual_y * CELL_SIZE
        center_y += CELL_SIZE // 2

        rect = image.get_rect(center=(center_x, center_y))
        screen.blit(image, rect)
