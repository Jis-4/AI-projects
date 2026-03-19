"""Synthetic dataset for quick image generation experiments."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List

from .math_utils import Vector, clamp


@dataclass
class SyntheticShapesDataset:
    image_size: int = 8
    samples_per_class: int = 60
    noise_level: float = 0.08
    seed: int = 42

    def generate(self) -> List[Vector]:
        rng = random.Random(self.seed)
        dataset: List[Vector] = []
        for _ in range(self.samples_per_class):
            dataset.append(self._make_square(rng))
            dataset.append(self._make_cross(rng))
            dataset.append(self._make_diamond(rng))
        rng.shuffle(dataset)
        return dataset

    def _blank(self) -> List[List[float]]:
        return [[0.0 for _ in range(self.image_size)] for _ in range(self.image_size)]

    def _jitter(self, value: int, rng: random.Random, limit: int = 1) -> int:
        return max(1, min(self.image_size - 2, value + rng.randint(-limit, limit)))

    def _finalize(self, image: List[List[float]], rng: random.Random) -> Vector:
        flattened: Vector = []
        for row in image:
            for value in row:
                noisy = value + rng.uniform(-self.noise_level, self.noise_level)
                flattened.append(clamp(noisy, 0.0, 1.0))
        return flattened

    def _make_square(self, rng: random.Random) -> Vector:
        image = self._blank()
        top = self._jitter(1, rng)
        left = self._jitter(1, rng)
        size = rng.randint(3, 4)
        for row in range(top, min(self.image_size - 1, top + size)):
            for col in range(left, min(self.image_size - 1, left + size)):
                image[row][col] = 1.0
        return self._finalize(image, rng)

    def _make_cross(self, rng: random.Random) -> Vector:
        image = self._blank()
        center = self._jitter(self.image_size // 2, rng)
        for index in range(1, self.image_size - 1):
            image[index][center] = 1.0
            image[center][index] = 1.0
        return self._finalize(image, rng)

    def _make_diamond(self, rng: random.Random) -> Vector:
        image = self._blank()
        center = self._jitter(self.image_size // 2, rng)
        radius = rng.randint(2, 3)
        for row in range(self.image_size):
            for col in range(self.image_size):
                if abs(row - center) + abs(col - center) <= radius:
                    image[row][col] = 1.0
        return self._finalize(image, rng)
