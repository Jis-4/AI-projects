"""Serialization and image export helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from .math_utils import clamp


def save_json(path: str | Path, payload: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save_pgm_grid(
    images: Iterable[List[float]],
    path: str | Path,
    image_size: int,
    columns: int = 4,
    padding: int = 1,
) -> None:
    images = list(images)
    if not images:
        raise ValueError("At least one image is required")

    rows = (len(images) + columns - 1) // columns
    width = columns * image_size + (columns - 1) * padding
    height = rows * image_size + (rows - 1) * padding
    canvas = [[0 for _ in range(width)] for _ in range(height)]

    for index, image in enumerate(images):
        row_offset = (index // columns) * (image_size + padding)
        col_offset = (index % columns) * (image_size + padding)
        for row in range(image_size):
            for col in range(image_size):
                pixel = int(clamp(image[row * image_size + col], 0.0, 1.0) * 255)
                canvas[row_offset + row][col_offset + col] = pixel

    lines = ["P2", f"{width} {height}", "255"]
    for row in canvas:
        lines.append(" ".join(str(pixel) for pixel in row))

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
