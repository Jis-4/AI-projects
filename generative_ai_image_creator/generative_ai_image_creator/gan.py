"""Pure-Python toy GAN trainer."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List

from .dataset import SyntheticShapesDataset
from .io_utils import load_json, save_json
from .layers import DenseLayer
from .math_utils import Vector, clamp, mean


@dataclass
class GANTrainer:
    data_dim: int = 64
    hidden_dim: int = 32
    noise_dim: int = 8
    generator_lr: float = 0.015
    discriminator_lr: float = 0.01
    seed: int = 11
    generator_hidden: DenseLayer = field(init=False)
    generator_output: DenseLayer = field(init=False)
    discriminator_hidden: DenseLayer = field(init=False)
    discriminator_output: DenseLayer = field(init=False)
    rng: random.Random = field(init=False)

    def __post_init__(self) -> None:
        self.rng = random.Random(self.seed)
        self.generator_hidden = DenseLayer(self.noise_dim, self.hidden_dim, self.generator_lr, "tanh", self.rng)
        self.generator_output = DenseLayer(self.hidden_dim, self.data_dim, self.generator_lr, "sigmoid", self.rng)
        self.discriminator_hidden = DenseLayer(self.data_dim, self.hidden_dim, self.discriminator_lr, "tanh", self.rng)
        self.discriminator_output = DenseLayer(self.hidden_dim, 1, self.discriminator_lr, "sigmoid", self.rng)

    def generator_forward(self, noise: Vector) -> Vector:
        hidden = self.generator_hidden.forward(noise)
        return self.generator_output.forward(hidden)

    def discriminator_forward(self, image: Vector) -> float:
        hidden = self.discriminator_hidden.forward(image)
        return self.discriminator_output.forward(hidden)[0]

    def _bce_grad(self, prediction: float, target: float) -> float:
        prediction = clamp(prediction, 1e-5, 1.0 - 1e-5)
        return prediction - target

    def train_epoch(self, dataset: List[Vector]) -> dict:
        d_losses = []
        g_losses = []
        for real_image in dataset:
            noise = [self.rng.uniform(-1.0, 1.0) for _ in range(self.noise_dim)]
            fake_image = self.generator_forward(noise)

            real_pred = self.discriminator_forward(real_image)
            real_loss = -math_log(real_pred)
            grad_real = [self._bce_grad(real_pred, 1.0)]
            grad_real_hidden = self.discriminator_output.backward(grad_real)
            self.discriminator_hidden.backward(grad_real_hidden)

            fake_pred = self.discriminator_forward(fake_image)
            fake_loss = -math_log(1.0 - fake_pred)
            grad_fake = [self._bce_grad(fake_pred, 0.0)]
            grad_fake_hidden = self.discriminator_output.backward(grad_fake)
            grad_fake_image = self.discriminator_hidden.backward(grad_fake_hidden)

            noise_for_generator = [self.rng.uniform(-1.0, 1.0) for _ in range(self.noise_dim)]
            generated_for_update = self.generator_forward(noise_for_generator)
            pred_for_generator = self.discriminator_forward(generated_for_update)
            generator_loss = -math_log(pred_for_generator)
            grad_pred_for_generator = [self._bce_grad(pred_for_generator, 1.0)]
            grad_gen_disc_hidden = self.discriminator_output.backward(grad_pred_for_generator)
            grad_generated_image = self.discriminator_hidden.backward(grad_gen_disc_hidden)
            grad_generator_hidden = self.generator_output.backward(grad_generated_image)
            self.generator_hidden.backward(grad_generator_hidden)

            d_losses.append((real_loss + fake_loss) / 2.0)
            g_losses.append(generator_loss)
        return {"discriminator_loss": mean(d_losses), "generator_loss": mean(g_losses)}

    def sample(self, num_images: int) -> List[Vector]:
        images = []
        for _ in range(num_images):
            noise = [self.rng.uniform(-1.0, 1.0) for _ in range(self.noise_dim)]
            images.append(self.generator_forward(noise))
        return images

    def train(self, epochs: int, dataset: List[Vector] | None = None) -> List[dict]:
        if dataset is None:
            dataset = SyntheticShapesDataset().generate()
        history = []
        for _ in range(epochs):
            self.rng.shuffle(dataset)
            history.append(self.train_epoch(dataset))
        return history

    def to_dict(self) -> dict:
        return {
            "data_dim": self.data_dim,
            "hidden_dim": self.hidden_dim,
            "noise_dim": self.noise_dim,
            "generator_lr": self.generator_lr,
            "discriminator_lr": self.discriminator_lr,
            "seed": self.seed,
            "generator_hidden": self.generator_hidden.to_dict(),
            "generator_output": self.generator_output.to_dict(),
            "discriminator_hidden": self.discriminator_hidden.to_dict(),
            "discriminator_output": self.discriminator_output.to_dict(),
        }

    def save(self, path: str) -> None:
        save_json(path, self.to_dict())

    @classmethod
    def load(cls, path: str) -> "GANTrainer":
        payload = load_json(path)
        model = cls(
            data_dim=payload["data_dim"],
            hidden_dim=payload["hidden_dim"],
            noise_dim=payload["noise_dim"],
            generator_lr=payload["generator_lr"],
            discriminator_lr=payload["discriminator_lr"],
            seed=payload["seed"],
        )
        model.generator_hidden = DenseLayer.from_dict(payload["generator_hidden"])
        model.generator_output = DenseLayer.from_dict(payload["generator_output"])
        model.discriminator_hidden = DenseLayer.from_dict(payload["discriminator_hidden"])
        model.discriminator_output = DenseLayer.from_dict(payload["discriminator_output"])
        return model


def math_log(value: float) -> float:
    import math

    return math.log(clamp(value, 1e-5, 1.0 - 1e-5))
