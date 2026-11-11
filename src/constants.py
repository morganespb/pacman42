import pygame

CELL_SIZE = 35
MARGIN = 20
HUD_HEIGHT = 50
HUD_COLOR = (180, 250, 255)
FONT = "assets/fonts/Michroma.ttf"

# Game parameters
BACKGROUND = (0, 0, 4)
TEXT_COLOR = (240, 240, 255)
PACGUM_COLOR = (255, 225, 190)
LIFE_SIZE = 20
COUNTDOWN_TIMER = 3.0

# Normal maze
WALL_COLOR = (85, 170, 255)
WALL_GLOW_COLOR = (20, 100, 255)
WALL_WIDTH = 2

# Pac-Man
PACMAN_COLOR = (255, 230, 40)
PACMAN_GLOW_COLOR = (255, 170, 0)
PACMAN_DEFAULT_MOVE_DELAY = 0.2
PACMAN_CHEAT_MODE_MOVE_DELAY = 0.1

# GHOST
GHOST_MOVE_DELAY = 0.4
GHOST_RESPAWN_TIMER = 6.0
GHOST_SIZE = 36
EDIBLE_DURATION = 8.0
# 42
FORTY_TWO_COLOR = (210, 255, 255)
FORTY_TWO_GLOW = (20, 220, 255)
FORTY_TWO_WIDTH = 3

# Pacgums Radiuses
PACGUM_RADIUS = 5
SUPER_PACGUM_OUTER_RADIUS = 15
SUPER_PACGUM_INNER_RADIUS = 10
SUPER_PACGUM_CORE_RADIUS = 8

GHOSTS_IT_IMAGES = [
    pygame.transform.smoothscale(
        pygame.image.load("assets/ghosts/staff1.png"),
        (GHOST_SIZE, GHOST_SIZE),
    ),
    pygame.transform.smoothscale(
        pygame.image.load("assets/ghosts/staff2.png"),
        (GHOST_SIZE, GHOST_SIZE),
    ),
    pygame.transform.smoothscale(
        pygame.image.load("assets/ghosts/staff3.png"),
        (GHOST_SIZE, GHOST_SIZE),
    ),
    pygame.transform.smoothscale(
        pygame.image.load("assets/ghosts/staff4.png"),
        (GHOST_SIZE, GHOST_SIZE),
    ),
]

GHOSTS_PC_IMAGES = [
    pygame.transform.smoothscale(
        pygame.image.load("assets/ghosts/pirate.png"),
        (GHOST_SIZE, GHOST_SIZE),
    ),
    pygame.transform.smoothscale(
        pygame.image.load("assets/ghosts/punk.png"),
        (GHOST_SIZE, GHOST_SIZE),
    ),
    pygame.transform.smoothscale(
        pygame.image.load("assets/ghosts/geisha.png"),
        (GHOST_SIZE, GHOST_SIZE),
    ),
    pygame.transform.smoothscale(
        pygame.image.load("assets/ghosts/square.png"),
        (GHOST_SIZE, GHOST_SIZE),
    ),
]

SCARED_GHOST_IMAGE = pygame.transform.smoothscale(
    pygame.image.load("assets/ghosts/scared_ghost.png"),
    (GHOST_SIZE, GHOST_SIZE),
)

LIFE_IMAGE = pygame.transform.scale(
    pygame.image.load("assets/heart.png"), (LIFE_SIZE, LIFE_SIZE))

LOGO = "assets/logo.png"
