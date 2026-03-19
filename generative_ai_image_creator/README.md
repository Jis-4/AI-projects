# Generative AI Image Creator

A self-contained Python project that demonstrates **two generative modeling approaches**—a **Variational Autoencoder (VAE)** and a **Generative Adversarial Network (GAN)**—without relying on external machine learning libraries.

This project is intentionally designed to be:
- easy to run in restricted environments,
- understandable for learning and portfolio demonstrations,
- maintainable through modular code, tests, and a documented CLI.

## What the project does

The project trains both models on a **synthetic grayscale image dataset** of small geometric shapes (squares, crosses, and diamonds). This keeps the repository lightweight while still showing the full workflow of:

- dataset creation,
- generative model training,
- checkpoint saving/loading,
- image sampling,
- reproducible experimentation.

## Project structure

```text
generative_ai_image_creator/
├── README.md
├── generative_ai_image_creator/
│   ├── __init__.py
│   ├── cli.py
│   ├── dataset.py
│   ├── gan.py
│   ├── io_utils.py
│   ├── layers.py
│   ├── math_utils.py
│   └── vae.py
└── tests/
    └── test_project.py
```

## Features

- **VAE implementation**
  - Encoder/decoder pipeline
  - Latent mean and log-variance heads
  - KL-divergence + reconstruction loss
  - Random latent sampling for new image generation

- **GAN implementation**
  - Generator and discriminator networks
  - Adversarial training loop
  - Synthetic image sampling from random noise

- **Pure Python design**
  - No third-party dependencies required
  - Runs with the standard library only

- **Maintainability**
  - Modular source files
  - Checkpoint serialization in JSON
  - Unit tests for dataset generation, training, saving, and sampling

## How to run

From the repository root:

### Train the VAE

```bash
PYTHONPATH=generative_ai_image_creator python -m generative_ai_image_creator.cli train-vae --epochs 10
```

This creates:
- `artifacts/vae_model.json`
- `artifacts/vae_samples.pgm`

### Train the GAN

```bash
PYTHONPATH=generative_ai_image_creator python -m generative_ai_image_creator.cli train-gan --epochs 10
```

This creates:
- `artifacts/gan_model.json`
- `artifacts/gan_samples.pgm`

### Sample from a saved checkpoint

```bash
PYTHONPATH=generative_ai_image_creator python -m generative_ai_image_creator.cli sample --model vae --checkpoint artifacts/vae_model.json --output artifacts/vae_resampled.pgm
```

Or for GAN:

```bash
PYTHONPATH=generative_ai_image_creator python -m generative_ai_image_creator.cli sample --model gan --checkpoint artifacts/gan_model.json --output artifacts/gan_resampled.pgm
```

## Output format

Generated image grids are saved as **PGM files** (`.pgm`), a simple grayscale image format that many image viewers support. Because the format is text-based and standard, it works well in dependency-free environments.

## Testing

Run the test suite with:

```bash
PYTHONPATH=generative_ai_image_creator python -m unittest discover -s generative_ai_image_creator/tests
```

## Suggested resume/project description

If you want a cleaner and truthful portfolio description, you can describe this project like this:

> Built a pure-Python generative image creation project featuring both VAE and GAN pipelines, synthetic dataset generation, model checkpointing, and CLI-based image sampling.

## Limitations and next steps

This is a lightweight educational implementation rather than a production-scale image generator. Good next improvements would be:

- replace the toy neural network engine with PyTorch,
- train on a real image dataset,
- add convolutional layers,
- expose a small web UI for prompt-less sampling and experiment tracking.
