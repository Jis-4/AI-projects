"""CLI entrypoint for the Generative AI Image Creator project."""

from __future__ import annotations

import argparse
from pathlib import Path

from .dataset import SyntheticShapesDataset
from .gan import GANTrainer
from .io_utils import save_pgm_grid
from .vae import VAETrainer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train and sample from toy GAN and VAE image generators.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    train_vae = subparsers.add_parser("train-vae", help="Train the VAE model.")
    train_vae.add_argument("--epochs", type=int, default=15)
    train_vae.add_argument("--checkpoint", default="artifacts/vae_model.json")
    train_vae.add_argument("--samples", type=int, default=8)
    train_vae.add_argument("--output", default="artifacts/vae_samples.pgm")

    train_gan = subparsers.add_parser("train-gan", help="Train the GAN model.")
    train_gan.add_argument("--epochs", type=int, default=20)
    train_gan.add_argument("--checkpoint", default="artifacts/gan_model.json")
    train_gan.add_argument("--samples", type=int, default=8)
    train_gan.add_argument("--output", default="artifacts/gan_samples.pgm")

    sample = subparsers.add_parser("sample", help="Sample from a saved model.")
    sample.add_argument("--model", choices=["vae", "gan"], required=True)
    sample.add_argument("--checkpoint", required=True)
    sample.add_argument("--samples", type=int, default=8)
    sample.add_argument("--output", required=True)

    return parser


def train_vae(args: argparse.Namespace) -> None:
    dataset = SyntheticShapesDataset().generate()
    trainer = VAETrainer()
    history = trainer.train(args.epochs, dataset)
    trainer.save(args.checkpoint)
    save_pgm_grid(trainer.sample(args.samples), args.output, image_size=8)
    print(f"Saved VAE checkpoint to {args.checkpoint}")
    print(f"Saved VAE samples to {args.output}")
    print(f"Final epoch metrics: {history[-1]}")


def train_gan(args: argparse.Namespace) -> None:
    dataset = SyntheticShapesDataset().generate()
    trainer = GANTrainer()
    history = trainer.train(args.epochs, dataset)
    trainer.save(args.checkpoint)
    save_pgm_grid(trainer.sample(args.samples), args.output, image_size=8)
    print(f"Saved GAN checkpoint to {args.checkpoint}")
    print(f"Saved GAN samples to {args.output}")
    print(f"Final epoch metrics: {history[-1]}")


def sample_from_checkpoint(args: argparse.Namespace) -> None:
    output_path = Path(args.output)
    if args.model == "vae":
        trainer = VAETrainer.load(args.checkpoint)
    else:
        trainer = GANTrainer.load(args.checkpoint)
    save_pgm_grid(trainer.sample(args.samples), output_path, image_size=8)
    print(f"Saved samples to {output_path}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "train-vae":
        train_vae(args)
    elif args.command == "train-gan":
        train_gan(args)
    else:
        sample_from_checkpoint(args)


if __name__ == "__main__":
    main()
