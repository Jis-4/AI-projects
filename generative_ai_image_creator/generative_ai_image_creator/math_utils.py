"""Small pure-Python math helpers for toy neural networks."""

from __future__ import annotations

import math
import random
from typing import Iterable, List

Vector = List[float]
Matrix = List[List[float]]


def random_vector(size: int, scale: float = 0.1, rng: random.Random | None = None) -> Vector:
    rng = rng or random
    return [rng.uniform(-scale, scale) for _ in range(size)]


def random_matrix(rows: int, cols: int, scale: float = 0.1, rng: random.Random | None = None) -> Matrix:
    rng = rng or random
    return [random_vector(cols, scale=scale, rng=rng) for _ in range(rows)]


def dot(a: Vector, b: Vector) -> float:
    return sum(x * y for x, y in zip(a, b))


def matvec(matrix: Matrix, vector: Vector) -> Vector:
    return [dot(row, vector) for row in matrix]


def add_vectors(a: Vector, b: Vector) -> Vector:
    return [x + y for x, y in zip(a, b)]


def sub_vectors(a: Vector, b: Vector) -> Vector:
    return [x - y for x, y in zip(a, b)]


def mul_scalar(vector: Vector, scalar: float) -> Vector:
    return [scalar * value for value in vector]


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def tanh(x: float) -> float:
    return math.tanh(x)


def relu(x: float) -> float:
    return x if x > 0.0 else 0.0


def apply(vector: Vector, fn) -> Vector:
    return [fn(value) for value in vector]


def zeros(size: int) -> Vector:
    return [0.0 for _ in range(size)]


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / max(1, len(values))
