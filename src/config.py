"""Configuration dataclasses and default values."""

from dataclasses import dataclass

DFT_LIVES = 3
DFT_PACGUM = 42
DFT_POINTS_PER_PACGUM = 10
DFT_POINTS_PER_SUPERPACGUM = 50
DFT_POINTS_PER_GHOSTS = 200
DFT_SEED = 42
DFT_LEVEL_MAX_TIME = 90
DFT_HS_FILENAME = "highscores.json"


@dataclass
class LevelConfig:
    """Size of a single level.

    Attributes:
        width: Level width in cells.
        height: Level height in cells.
    """
    width: int
    height: int

    @classmethod
    def from_dict(cls, data: dict[str, int]) -> "LevelConfig":
        """Build a LevelConfig from a raw {"width", "height"} dict.

        Args:
            data: A dict with "width" and "height" keys.

        Returns:
            The corresponding LevelConfig.
        """
        return cls(width=data["width"], height=data["height"])


@dataclass
class Config:
    """Fully validated game configuration.

    Attributes:
        highscore_filename: Path to the highscores JSON file.
        lives: Starting number of lives.
        pacgum: Number of pacgums to place per level.
        points_per_pacgum: Points awarded per pacgum eaten.
        points_per_super_pacgum: Points awarded per super pacgum eaten.
        points_per_ghost: Points awarded per ghost eaten.
        seed: Random seed for the first level's maze.
        level_max_time: Time limit per level, in seconds.
        levels: Size configuration for each level.
    """
    highscore_filename: str
    lives: int
    pacgum: int
    points_per_pacgum: int
    points_per_super_pacgum: int
    points_per_ghost: int
    seed: int
    level_max_time: int
    levels: list[LevelConfig]
