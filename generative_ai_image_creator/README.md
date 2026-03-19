# Marketing Creative Studio

A realistic replacement for the earlier toy GAN/VAE demo: this project is now a **use-case-focused generative creative application** built around a **marketing content workflow**.

Instead of pretending to be a production text-to-image model, it demonstrates the parts that make a portfolio project actually impressive:

- **prompt optimization** for better generation requests,
- **multi-variant creative generation**,
- **storage and ranking** of outputs,
- **editing controls** for targeted revisions,
- a **real frontend** with gallery, ranking, and edit flows,
- a clean backend architecture that can later be connected to a real image model provider.

## Product focus

This version is positioned as a **marketing creative generator**.

A marketer or founder can:
1. enter brand, product, audience, campaign goal, and style cues,
2. get an optimized prompt and multiple creative directions,
3. favorite/rate the best outputs,
4. edit specific regions like the headline, CTA, hero visual, or background,
5. reuse the top-ranked concepts in a campaign workflow.

## What is realistic about it

This project behaves like a real product, not just a model script:

- **Frontend UI** with use-case switching, generation form, optimized prompt panel, ranking board, and gallery.
- **Backend API** with generation, listing, rating, and edit endpoints.
- **SQLite persistence** so generated outputs and rankings are stored.
- **Versioned edits** where a modified creative is stored as a new child asset.
- **Provider-ready architecture** so the local renderer can later be swapped for OpenAI, Replicate, Stability, or another image backend.

## Current implementation model

Because this environment has no external API credentials and no installable ML stack, the project uses a **local SVG creative renderer** to simulate polished marketing outputs while preserving the product workflow.

That means:
- the **application architecture is realistic**,
- the **UX is realistic**,
- the **storage/ranking/editing workflow is realistic**,
- but the local generation engine is still a demo renderer rather than a real diffusion model.

## Architecture

```text
generative_ai_image_creator/
├── README.md
├── data/
│   └── generated/                  # saved SVG outputs
├── generative_ai_image_creator/
│   ├── __init__.py
│   ├── config.py                   # paths and runtime config
│   ├── creative_engine.py          # local polished SVG creative renderer
│   ├── models.py                   # record model
│   ├── prompt_optimizer.py         # transforms rough prompts into structured prompts
│   ├── repository.py               # SQLite storage and ranking
│   ├── server.py                   # HTTP API + static frontend server
│   ├── service.py                  # orchestration layer
│   └── static/
│       ├── app.js                  # frontend logic
│       ├── index.html              # UI
│       └── styles.css              # styling
└── tests/
    └── test_project.py
```

## Features

### 1. Prompt optimization
The app turns a rough prompt into a structured, use-case-aware creative brief.

### 2. Ranked image storage
Each generated output is stored in SQLite with:
- prompt metadata,
- style preset,
- palette,
- layout,
- score,
- favorite/rating state,
- parent-child linkage for edited versions.

### 3. Output editing
The UI allows targeted edits with controls for:
- mask region,
- replacement text,
- edit instruction,
- layout,
- palette,
- style strength.

### 4. Real frontend
The interface includes:
- use-case selectors,
- generation form,
- optimized prompt review,
- ranked outputs,
- image gallery,
- per-image rating and edit controls.

## API endpoints

- `GET /api/health`
- `GET /api/images?use_case=marketing`
- `POST /api/generate`
- `POST /api/images/<id>/rate`
- `POST /api/images/<id>/edit`
- `GET /generated/<filename>.svg`

## How to run

From the repository root:

```bash
PYTHONPATH=generative_ai_image_creator python -m generative_ai_image_creator.server --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000
```

## Testing

```bash
PYTHONPATH=generative_ai_image_creator python -m unittest discover -s generative_ai_image_creator/tests -v
```

## How to make this even more impressive later

To turn this into a truly standout project, next upgrades should be:

- connect the generation layer to a real model API,
- add asset collections/projects and user auth,
- implement batch prompt testing and A/B comparison,
- support reference-image upload for better edit control,
- add export presets for Meta, LinkedIn, and landing-page hero banners.

## Honest resume framing

A truthful resume description would be:

> Built a marketing-focused generative creative studio with prompt optimization, ranked asset storage, edit/version workflows, a real frontend, and a provider-ready backend architecture for future model integration.
