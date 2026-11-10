# AI-Based Realistic Virtual Try-On

A development scaffold for a virtual try-on product with a future browser extension and standalone storefront. The first implementation milestone is a reliable DressCode data pipeline and a demo API; the current image compositor is a placeholder, not a trained virtual try-on model.

## Repository layout

```text
apps/
  web/                         standalone browser demo
  extension/                   browser-extension scaffold (planned)
services/api/                  FastAPI upload and preview API
ml/data/                       DressCode pair-list reader and PyTorch dataset
ml/scripts/                    dataset inspection and manifest utilities
ml/configs/                    experiment configuration
train.jsonl                    tracked LFS pointer; not assumed to be DressCode format
```

## DressCode dataset setup

Use a locally downloaded copy of DressCode for which you have the appropriate access rights. Do not commit the dataset or redistribute it from this repository. The large `DressCode-MR.tar.gz.part_*` and JSONL entries tracked here are Git LFS pointers; clone/pull with Git LFS if you specifically need those files. For the pipeline below, point `--dataset-root` to the extracted dataset directory.

The loader expects the official per-category structure and pair files, for example:

```text
<DRESSCODE_ROOT>/
  upper_body/                 # or lower_body/ or dresses/
    train_pairs.txt
    test_pairs.txt
    image/                    # person images
    cloth/                    # garment images
    agnostic-v3.2/            # optional person-agnostic inputs
    image-densepose/           # optional pose inputs
```

Directory aliases and image extensions are checked by the loader. Pair-list lines should contain a person filename followed by a garment filename. The pair file may be at the dataset root or category directory. Keep the original dataset layout intact where possible.

### Validate a split and export a manifest

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r services/api/requirements.txt
python -m ml.scripts.prepare_dresscode \
  --dataset-root /path/to/DressCode \
  --category upper_body \
  --split train \
  --output ml/artifacts/dresscode-upper-body-train.jsonl
```

Use `--split test` or categories `lower_body` / `dresses` as needed. The command reports missing pair images and exits non-zero if any are missing. Generated manifests and downloaded data belong outside version control (`ml/artifacts/` and dataset paths are ignored).

### Use the dataset from Python

```python
from ml.data.dresscode import DressCodeDataset

dataset = DressCodeDataset("/path/to/DressCode", category="upper_body", split="train")
sample = dataset[0]
# sample: person, garment, target (paired person), optional agnostic/densepose, metadata
```

The data loader intentionally does not claim to train a production-quality synthesis model. Training, evaluation, and inference need a selected try-on architecture/checkpoint and should be implemented as a separate milestone. The current service returns a simple overlay preview for API/UI integration testing only.

## Run the demo API

```bash
pip install -r services/api/requirements.txt
cd services/api
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs: <http://127.0.0.1:8000/docs>. Health check: `GET /health`. The preview endpoint is `POST /api/v1/tryon` with multipart fields `user_image` and `garment_image`.

To serve the web demo in a second terminal:

```bash
cd apps/web
python -m http.server 8080
```

Open <http://127.0.0.1:8080>. The current UI calls the API at `http://localhost:8000`.

## Product direction

The API is intended to become the shared backend for a standalone shop and an opt-in browser extension. Keep retailer integrations user-initiated and site-specific; do not rely on scraping retailer pages as the product catalog. Before launch, add authentication, PostgreSQL-backed product/job records, object storage with retention controls, and a real trained try-on model. Do not store sensitive user photos longer than needed; provide clear consent and deletion behavior.
