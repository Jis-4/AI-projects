"""Pure-Python toy variational autoencoder trainer."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import List

from .dataset import SyntheticShapesDataset
from .io_utils import load_json, save_json
from .layers import DenseLayer
from .math_utils import Vector, clamp, mean, zeros


@dataclass
class VAETrainer:
    input_dim: int = 64
    hidden_dim: int = 32
    latent_dim: int = 8
    learning_rate: float = 0.02
    seed: int = 7
    encoder: DenseLayer = field(init=False)
    mu_layer: DenseLayer = field(init=False)
    logvar_layer: DenseLayer = field(init=False)
    decoder_hidden: DenseLayer = field(init=False)
    decoder_output: DenseLayer = field(init=False)
    rng: random.Random = field(init=False)

    def __post_init__(self) -> None:
        self.rng = random.Random(self.seed)
        self.encoder = DenseLayer(self.input_dim, self.hidden_dim, self.learning_rate, "tanh", self.rng)
        self.mu_layer = DenseLayer(self.hidden_dim, self.latent_dim, self.learning_rate, "linear", self.rng)
        self.logvar_layer = DenseLayer(self.hidden_dim, self.latent_dim, self.learning_rate, "linear", self.rng)
        self.decoder_hidden = DenseLayer(self.latent_dim, self.hidden_dim, self.learning_rate, "tanh", self.rng)
        self.decoder_output = DenseLayer(self.hidden_dim, self.input_dim, self.learning_rate, "sigmoid", self.rng)

    def encode(self, vector: Vector) -> tuple[Vector, Vector, Vector]:
        hidden = self.encoder.forward(vector)
        mu = self.mu_layer.forward(hidden)
        logvar = [clamp(value, -4.0, 4.0) for value in self.logvar_layer.forward(hidden)]
        latent = []
        for mu_value, logvar_value in zip(mu, logvar):
            std = math.exp(0.5 * logvar_value)
            eps = self.rng.gauss(0.0, 1.0)
            latent.append(mu_value + eps * std)
        return mu, logvar, latent

    def decode(self, latent: Vector) -> Vector:
        hidden = self.decoder_hidden.forward(latent)
        return self.decoder_output.forward(hidden)

    def reconstruct(self, vector: Vector) -> Vector:
        mu, _logvar, _latent = self.encode(vector)
        return self.decode(mu)

    def train_epoch(self, dataset: List[Vector]) -> dict:
        losses = []
        reconstruction_losses = []
        kl_losses = []
        for sample in dataset:
            mu, logvar, latent = self.encode(sample)
            reconstruction = self.decode(latent)

            grad_recon = []
            reconstruction_loss = 0.0
            for predicted, target in zip(reconstruction, sample):
                predicted = clamp(predicted, 1e-5, 1.0 - 1e-5)
                reconstruction_loss += -(target * math.log(predicted) + (1.0 - target) * math.log(1.0 - predicted))
                grad_recon.append(predicted - target)

            grad_decoder_hidden = self.decoder_output.backward(grad_recon)
            grad_latent = self.decoder_hidden.backward(grad_decoder_hidden)

            kl_loss = 0.0
            grad_mu = zeros(self.latent_dim)
            grad_logvar = zeros(self.latent_dim)
            for index, (mu_value, logvar_value, latent_grad, latent_value) in enumerate(
                zip(mu, logvar, grad_latent, latent)
            ):
                std = math.exp(0.5 * logvar_value)
                eps = 0.0 if std == 0.0 else (latent_value - mu_value) / std
                kl_loss += -0.5 * (1.0 + logvar_value - mu_value * mu_value - math.exp(logvar_value))
                grad_mu[index] = latent_grad + mu_value
                grad_logvar[index] = latent_grad * (0.5 * eps * std) + 0.5 * (math.exp(logvar_value) - 1.0)

            grad_hidden_from_mu = self.mu_layer.backward(grad_mu)
            grad_hidden_from_logvar = self.logvar_layer.backward(grad_logvar)
            grad_encoder_hidden = [a + b for a, b in zip(grad_hidden_from_mu, grad_hidden_from_logvar)]
            self.encoder.backward(grad_encoder_hidden)

            total_loss = reconstruction_loss + kl_loss
            losses.append(total_loss)
            reconstruction_losses.append(reconstruction_loss)
            kl_losses.append(kl_loss)

        return {
            "loss": mean(losses),
            "reconstruction_loss": mean(reconstruction_losses),
            "kl_loss": mean(kl_losses),
        }

    def sample(self, num_images: int) -> List[Vector]:
        images = []
        for _ in range(num_images):
            latent = [self.rng.gauss(0.0, 1.0) for _ in range(self.latent_dim)]
            images.append(self.decode(latent))
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
            "input_dim": self.input_dim,
            "hidden_dim": self.hidden_dim,
            "latent_dim": self.latent_dim,
            "learning_rate": self.learning_rate,
            "seed": self.seed,
            "encoder": self.encoder.to_dict(),
            "mu_layer": self.mu_layer.to_dict(),
            "logvar_layer": self.logvar_layer.to_dict(),
            "decoder_hidden": self.decoder_hidden.to_dict(),
            "decoder_output": self.decoder_output.to_dict(),
        }

    def save(self, path: str) -> None:
        save_json(path, self.to_dict())

    @classmethod
    def load(cls, path: str) -> "VAETrainer":
        payload = load_json(path)
        model = cls(
            input_dim=payload["input_dim"],
            hidden_dim=payload["hidden_dim"],
            latent_dim=payload["latent_dim"],
            learning_rate=payload["learning_rate"],
            seed=payload["seed"],
        )
        model.encoder = DenseLayer.from_dict(payload["encoder"])
        model.mu_layer = DenseLayer.from_dict(payload["mu_layer"])
        model.logvar_layer = DenseLayer.from_dict(payload["logvar_layer"])
        model.decoder_hidden = DenseLayer.from_dict(payload["decoder_hidden"])
        model.decoder_output = DenseLayer.from_dict(payload["decoder_output"])
        return model
