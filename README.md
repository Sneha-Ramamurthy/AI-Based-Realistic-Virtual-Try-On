# AI-Based Realistic Virtual Try-On

A lightweight full-stack starter for an AI-powered virtual try-on application. The project includes:

- a FastAPI backend that accepts a user photo and garment image and returns a simulated try-on preview
- a browser UI for uploading images and previewing the result
- a MLOps/ML structure so the project can evolve into a more advanced computer-vision pipeline
- Docker support for local development

## Project structure

```text
apps/
  web/                    browser client for try-on demos
infra/
  docker/                 Docker Compose setup
ml/
  configs/                model and training config placeholders
  README.md               ML pipeline overview
services/
  api/                    FastAPI application and API routes
```

## What this MVP does

This version implements a practical, working starter that demonstrates the core UX:

1. The user uploads a person image and a garment image.
2. The backend estimates a torso region and overlays the garment using image processing.
3. The result is returned as a base64-encoded preview image that the browser can display.

This is intentionally lightweight and deterministic so it works without model weights or GPU infrastructure.

## Quick start

### 1) Create a virtual environment

```bash
cd /path/to/AI-Based-Realistic-Virtual-Try-On
python -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r services/api/requirements.txt
```

### 3) Start the API

```bash
cd services/api
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4) Open the demo UI

Open:

```text
http://localhost:8000/docs
```

Or serve the frontend directly:

```bash
cd apps/web
python -m http.server 8080
```

Then open `http://localhost:8080`.

## API

### Health check

```bash
curl http://localhost:8000/health
```

### Try-on preview

```bash
curl -X POST "http://localhost:8000/api/v1/tryon" \
  -F "user_image=@path/to/person.png" \
  -F "garment_image=@path/to/garment.png"
```

The response includes a base64 preview image.

## Production roadmap

This MVP is intentionally modular so you can evolve it to real AI/ML:

- integrate a pose-estimation model (OpenPose, MediaPipe, or HRNet)
- add garment segmentation and dense correspondence
- replace heuristic overlay with diffusion or GAN-based generation
- add async job queue with Celery and Redis
- move the app to a real deployment stack with Postgres and cloud storage

## Notes

The repository was mostly scaffolded, so the key missing part was a working end-to-end starting point. This version provides that baseline and a clear path to the more advanced pipeline described in the project goal.
