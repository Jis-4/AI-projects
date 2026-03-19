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

### Marketing Creative Studio
A realistic generative-creative product prototype focused on marketing use cases, with prompt optimization, ranked asset storage, targeted edit controls, and a real web frontend.

- Project folder: `generative_ai_image_creator/`
- Project README: `generative_ai_image_creator/README.md`

Run:

```bash
PYTHONPATH=generative_ai_image_creator python -m generative_ai_image_creator.server --host 127.0.0.1 --port 8000
```

## Testing

```bash
python -m unittest test_textparaphraser.py
PYTHONPATH=generative_ai_image_creator python -m unittest discover -s generative_ai_image_creator/tests
```
