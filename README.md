# AI-Based-Realistic-Virtual-Try-On
An AI-powered virtual try-on system that realistically visualizes garments on users using AI/ML techniques, computer vision, and image synthesis techniques.
Realistic, explainable virtual try-on with an LLM stylist layer, shipped two ways:

- **App** — standalone web app with its own catalog, chat stylist, and checkout
- **Extension** — Chrome/Edge extension that overlays try-on onto existing e-commerce sites (Amazon fashion first)

Both share one backend: pose/parsing → warping → diffusion generation → LLM reasoning → recommendations.

## Status

`Draft / proposed project` — see [`docs/PROPOSAL.docx`](docs/StyleSync_AI_VTON_Proposal.docx) for the full write-up (architecture, timeline, evaluation plan, risk register).

## Repo Structure

```
.
├── apps/
│   ├── web/                 # Next.js standalone app (Version A)
│   └── extension/           # Manifest V3 browser extension (Version B)
├── services/
│   ├── api/                 # FastAPI orchestration layer
│   ├── vision/               # pose estimation, parsing, segmentation, garment extraction
│   ├── generation/           # warping + try-on generation (fast tier / quality tier)
│   ├── reasoning/            # LLM fit/style/chat layer
│   └── recommendation/       # CLIP embeddings + vector DB + hybrid filtering
├── ml/
│   ├── notebooks/            # experiments, eval notebooks
│   ├── checkpoints/          # (gitignored) model weights
│   └── configs/              # training configs
├── infra/
│   ├── docker/                # Dockerfiles per service
│   ├── docker-compose.yml     # local dev: api + redis + postgres + worker
│   └── k8s/                   # (optional) manifests for scale
├── docs/
│   ├── StyleSync_AI_VTON_Proposal.docx
│   └── evaluation/            # FID/LPIPS/fairness reports
├── .github/workflows/         # CI: lint, test, build
├── .env.example
├── .gitignore
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.11+, Node 20+, Docker + Docker Compose
- GPU (16–24GB) for local generation, or a Replicate/Modal/RunPod API key for hosted inference
- PostgreSQL 15+, Redis 7+ (or use `docker-compose up`)

### 1. Clone & configure

```bash
git clone https://github.com/<you>/stylesync-ai.git
cd stylesync-ai
cp .env.example .env   # fill in API keys — never commit .env
```

### 2. Backend (Python)

```bash
cd services/api
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 3. Full stack via Docker Compose

```bash
docker compose -f infra/docker-compose.yml up --build
```

Spins up: FastAPI backend, Redis, PostgreSQL, Celery worker.

### 4. Web app (Version A)

```bash
cd apps/web
npm install
npm run dev
```

### 5. Browser extension (Version B)

```bash
cd apps/extension
npm install
npm run build
# then: chrome://extensions → Developer mode → Load unpacked → apps/extension/dist
```

## Environment Variables

See `.env.example`. Never hardcode keys or commit `.env` — it's gitignored by default.

| Variable | Purpose |
|---|---|
| `GPU_INFERENCE_API_KEY` | Replicate / Modal / RunPod key for hosted generation |
| `LLM_API_KEY` | GPT / Gemini / Llama endpoint key |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `STORAGE_BUCKET` | Object storage for uploaded/generated images |

## Development Phases

| Phase | Weeks | Goal |
|---|---|---|
| A1 | 1–2 | Working pipeline, no training — pretrained pose/parsing + TPS warp |
| A2 | 3–5 | Train UNet + PatchGAN generator, 256px |
| B | 6–13 | Fidelity upgrade, LLM reasoning, Version A app |
| C | 14–18 | Browser extension, recommendations, fairness audit |
| D | 19–20 | Hardening, docs, demo |

Full breakdown in the proposal doc.

## Evaluation

- **Image quality:** SSIM, FID, LPIPS on VITON-HD / DressCode subsets, benchmarked against published baselines
- **Alignment:** Mask IoU (target > 0.6)
- **Human preference:** A/B study vs. naive baseline (target > 70%)
- **Fairness:** results across ≥5 body types and 6 skin-tone classes, failure cases documented honestly

## Security & Privacy

- Uploaded photos processed and discarded by default — not persisted unless the user opts in
- No photos in logs, error traces, or git history
- Rate-limited inference endpoint; input validation on all uploads (signature check + size/resolution caps)
- Secrets in `.env` only, `.gitignore`'d from commit one
- Extension requests minimal permissions (`activeTab`, `storage`), read-only DOM access, no purchase automation
- Generated outputs watermarked/tagged as AI-generated

## Datasets

VITON-HD, DressCode, DeepFashion2, FashionIQ, MPV. See `docs/StyleSync_AI_VTON_Proposal.docx` §13 for details and licensing notes.

## Contributing

This is a solo/team capstone project. Branch naming: `feature/<short-name>`, `fix/<short-name>`. All PRs require the CI workflow (lint + test + build) to pass.

## License

TBD — add a LICENSE file before making the repo public if you plan to use third-party model weights with non-permissive licenses (check IDM-VTON / OOTDiffusion / SCHP license terms individually).
