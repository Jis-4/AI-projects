# AI Projects

This repository contains small, self-contained AI and ML portfolio projects.

## Projects

### Text Paraphraser
A Python script that paraphrases input text by replacing words with synonyms using NLTK.

- File: `textparaphraser.py`
- Tests: `test_textparaphraser.py`

Run:

```bash
python textparaphraser.py "This is the sentence I want to paraphrase."
```

### Generative AI Image Creator
A dependency-light image generation project that implements both a **VAE** and a **GAN** in pure Python, trains on synthetic geometric images, saves checkpoints, and exports generated image grids.

- Project folder: `generative_ai_image_creator/`
- Project README: `generative_ai_image_creator/README.md`

Run:

```bash
PYTHONPATH=generative_ai_image_creator python -m generative_ai_image_creator.cli train-vae --epochs 10
PYTHONPATH=generative_ai_image_creator python -m generative_ai_image_creator.cli train-gan --epochs 10
```

## Testing

```bash
python -m unittest test_textparaphraser.py
PYTHONPATH=generative_ai_image_creator python -m unittest discover -s generative_ai_image_creator/tests
```
