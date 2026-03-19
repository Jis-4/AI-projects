"""Basic trainable layers implemented in pure Python."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List

from .math_utils import Matrix, Vector, apply, random_matrix, random_vector, relu, sigmoid, tanh, zeros


@dataclass
class DenseLayer:
    in_features: int
    out_features: int
    learning_rate: float
    activation: str = "linear"
    rng: random.Random = field(default_factory=random.Random)
    weights: Matrix = field(init=False)
    bias: Vector = field(init=False)
    last_input: Vector | None = field(default=None, init=False)
    last_linear: Vector | None = field(default=None, init=False)
    last_output: Vector | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        scale = (2.0 / max(1, self.in_features)) ** 0.5
        self.weights = random_matrix(self.out_features, self.in_features, scale=scale, rng=self.rng)
        self.bias = random_vector(self.out_features, scale=0.01, rng=self.rng)

    def _activate(self, values: Vector) -> Vector:
        if self.activation == "sigmoid":
            return apply(values, sigmoid)
        if self.activation == "tanh":
            return apply(values, tanh)
        if self.activation == "relu":
            return apply(values, relu)
        return values[:]

    def _activation_grad(self, linear: Vector, output: Vector) -> Vector:
        if self.activation == "sigmoid":
            return [value * (1.0 - value) for value in output]
        if self.activation == "tanh":
            return [1.0 - value * value for value in output]
        if self.activation == "relu":
            return [1.0 if value > 0.0 else 0.0 for value in linear]
        return [1.0 for _ in linear]

    def forward(self, inputs: Vector) -> Vector:
        self.last_input = inputs[:]
        linear = []
        for row, bias in zip(self.weights, self.bias):
            linear.append(sum(weight * value for weight, value in zip(row, inputs)) + bias)
        self.last_linear = linear
        self.last_output = self._activate(linear)
        return self.last_output[:]

    def backward(self, grad_output: Vector) -> Vector:
        if self.last_input is None or self.last_linear is None or self.last_output is None:
            raise RuntimeError("forward must run before backward")

        activation_grad = self._activation_grad(self.last_linear, self.last_output)
        grad_linear = [go * ga for go, ga in zip(grad_output, activation_grad)]
        grad_input = zeros(self.in_features)

        for output_index in range(self.out_features):
            for input_index in range(self.in_features):
                grad_input[input_index] += self.weights[output_index][input_index] * grad_linear[output_index]
                self.weights[output_index][input_index] -= (
                    self.learning_rate * grad_linear[output_index] * self.last_input[input_index]
                )
            self.bias[output_index] -= self.learning_rate * grad_linear[output_index]

        return grad_input

    def to_dict(self) -> dict:
        return {
            "in_features": self.in_features,
            "out_features": self.out_features,
            "learning_rate": self.learning_rate,
            "activation": self.activation,
            "weights": self.weights,
            "bias": self.bias,
        }

    @classmethod
    def from_dict(cls, payload: dict) -> "DenseLayer":
        layer = cls(
            in_features=payload["in_features"],
            out_features=payload["out_features"],
            learning_rate=payload["learning_rate"],
            activation=payload["activation"],
        )
        layer.weights = payload["weights"]
        layer.bias = payload["bias"]
        return layer
