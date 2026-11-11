"""Persistent highscore storage as a JSON file."""

import json
from pathlib import Path
from typing import cast


def load_high_scores(filename: str) -> list[dict[str, object]]:
    """Load saved highscores from a JSON file.

    Args:
        filename: Path to the highscores JSON file.

    Returns:
        A list of {"name": str, "score": int} entries, or an empty list
        if the file does not exist.
    """
    path = Path(filename)

    if not path.exists():
        return []

    with path.open("r") as file:
        data: list[dict[str, object]] = json.load(file)
        return data


def save_high_scores(filename: str, name: str, score: int) -> None:
    """Add a new score and persist the top 10 highscores.

    Args:
        filename: Path to the highscores JSON file.
        name: Player name to record.
        score: Score achieved by the player.
    """
    scores = load_high_scores(filename)

    scores.append({"name": name, "score": score})
    scores.sort(key=lambda entry: cast(int, entry["score"]), reverse=True)
    scores = scores[:10]

    with Path(filename).open("w") as file:
        json.dump(scores, file, indent=4)
