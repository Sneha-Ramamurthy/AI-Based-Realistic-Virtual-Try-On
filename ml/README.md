# DressCode data pipeline

`ml/data/dresscode.py` provides a PyTorch `Dataset` for paired DressCode samples. It reads whitespace-separated person/garment filename pairs and resolves them against category image folders. The dataset returns the paired person image as the reconstruction target plus optional agnostic and DensePose inputs when those folders exist.

`ml/scripts/prepare_dresscode.py` validates a split and writes an absolute-path JSONL manifest. Run it from the repository root:

```bash
python -m ml.scripts.prepare_dresscode \
  --dataset-root /path/to/DressCode \
  --category upper_body \
  --split train \
  --output ml/artifacts/upper_body-train.jsonl
```

Dataset variants may name folders differently. The loader handles common aliases; if your copy differs, adapt `_IMAGE_DIRS`, `_CLOTH_DIRS`, or the optional directory aliases to the actual extracted layout. This code only prepares and reads data; it does not train a virtual try-on model. Do not commit dataset assets, generated manifests, or trained checkpoints.

Run the small unit tests with:

```bash
python -m unittest ml.tests.test_dresscode
```
