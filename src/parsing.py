"""Load and validate the JSON game configuration file."""

import json
from .config import (DFT_LIVES, DFT_POINTS_PER_PACGUM,
                     DFT_POINTS_PER_SUPERPACGUM, DFT_LEVEL_MAX_TIME,
                     DFT_PACGUM, DFT_POINTS_PER_GHOSTS, DFT_SEED,
                     DFT_HS_FILENAME, Config, LevelConfig)


def strip_comments(path: str) -> str:
    """Read a JSON file, stripping lines that start with '#'.

    Args:
        path: Path to the file to read.

    Returns:
        The file's content with comment lines removed.
    """
    lines = []
    with open(path, "r") as file:
        for line in file:
            if line.strip().startswith("#"):
                continue
            lines.append(line)
    return "".join(lines)


def parsing(path: str) -> dict[str, object]:
    """Parse a config file into a raw dict, tolerating '#' comments.

    Args:
        path: Path to the JSON config file.

    Returns:
        The parsed configuration as a dict.

    Raises:
        ValueError: If the file's content is not valid JSON.
    """
    cleaned = strip_comments(path)
    try:
        data: dict[str, object] = json.loads(cleaned)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in config file: {error}")
    return data


def validate_positive_int(value: object, default: int, name: str) -> int:
    """Validate that a value is a positive int, else fall back to a default.

    Args:
        value: The raw value to validate.
        default: The value to use if validation fails.
        name: Field name, used in the warning message.

    Returns:
        value if it is a valid positive int, else default.
    """
    if not isinstance(value, int) or value <= 0:
        print(f"Warning: invalid '{name}' value ({value}), "
              f"using default {default}")
        return default
    return value


def validate_str(value: object, default: str, name: str) -> str:
    """Validate that a value is a non-empty string, else use a default.

    Args:
        value: The raw value to validate.
        default: The value to use if validation fails.
        name: Field name, used in the warning message.

    Returns:
        value if it is a valid non-empty string, else default.
    """
    if not isinstance(value, str) or not value:
        print(f"Warning: invalid '{name}' value ({value}), "
              f"using default {default}")
        return default
    return value


def validate_levels(value: object, default: list[dict[str, int]],
                    name: str) -> list[dict[str, int]]:
    """Validate a list of level dicts, clamping invalid entries.

    Each entry is expected to be a dict with 'width' and 'height' keys;
    both are validated individually. Non-dict entries are skipped. If no
    entry is valid, falls back to default.

    Args:
        value: The raw levels value to validate.
        default: The value to use if validation fails entirely.
        name: Field name, used in the warning message.

    Returns:
        A list of {"width": int, "height": int} dicts.
    """
    if not isinstance(value, list):
        print(f"Warning: invalid '{name}' value ({value}), "
              f"using default {default}")
        return default

    validated = []
    for level in value:
        if isinstance(level, dict):
            width = validate_positive_int(
                level.get("width", 21), 21, "width")
            height = validate_positive_int(
                level.get("height", 21), 21, "height")
            validated.append({"width": width, "height": height})
        else:
            print(f"Warning: invalid level entry ({level}), skipping")
    if not validated:
        print(f"Warning: no valid levels found, using default {default}")
        return default
    return validated


def from_dict(data: dict[str, object]) -> "Config":
    """Build a validated Config from a raw parsed dict.

    Args:
        data: The raw dict returned by parsing().

    Returns:
        A Config with every field validated or clamped to a safe default.
    """
    default_levels = [{"width": 21, "height": 21}]
    validated_levels = validate_levels(
        data.get("levels"), default_levels, "levels")

    return Config(
        lives=validate_positive_int(data.get("lives"), DFT_LIVES, "lives"),
        highscore_filename=validate_str(
            data.get("highscore_filename"), DFT_HS_FILENAME,
            "highscore_filename"
        ),
        pacgum=validate_positive_int(data.get("pacgum"), DFT_PACGUM, "pacgum"),
        points_per_pacgum=validate_positive_int(
            data.get("points_per_pacgum"), DFT_POINTS_PER_PACGUM,
            "points_per_pacgum"
        ),
        points_per_super_pacgum=validate_positive_int(
            data.get("points_per_super_pacgum"), DFT_POINTS_PER_SUPERPACGUM,
            "points_per_super_pacgum"
        ),
        points_per_ghost=validate_positive_int(
            data.get("points_per_ghost"), DFT_POINTS_PER_GHOSTS,
            "points_per_ghost"
        ),
        seed=validate_positive_int(data.get("seed"), DFT_SEED, "seed"),
        level_max_time=validate_positive_int(
            data.get("level_max_time"), DFT_LEVEL_MAX_TIME, "level_max_time"),
        levels=[LevelConfig.from_dict(level) for level in validated_levels]
    )
