"""Validate a DressCode split and export resolved paths as JSON Lines."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from ml.data.dresscode import DressCodeDataset, _resolve_image


def build_manifest(root: Path, category: str, split: str, output: Path) -> int:
    dataset = DressCodeDataset(root, category=category, split=split)
    records = []
    missing = []
    for pair in dataset.pairs:
        person = _resolve_image(dataset.image_dir, pair.person_name)
        garment = _resolve_image(dataset.cloth_dir, pair.garment_name)
        if person is None:
            missing.append(f"person: {pair.person_name}")
        if garment is None:
            missing.append(f"garment: {pair.garment_name}")
        if person is not None and garment is not None:
            records.append({
                "category": category,
                "split": split,
                "person": str(person),
                "garment": str(garment),
                "target": str(person),
                "person_name": pair.person_name,
                "garment_name": pair.garment_name,
            })

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"Pair list: {dataset.pair_file}")
    print(f"Valid pairs: {len(records)} / {len(dataset)}")
    print(f"Manifest: {output}")
    if missing:
        preview = "\n".join(f"  - {item}" for item in missing[:20])
        print(f"Missing files ({len(missing)}):\n{preview}", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", required=True, type=Path, help="Root of extracted DressCode dataset")
    parser.add_argument("--category", choices=("upper_body", "lower_body", "dresses"), default="upper_body")
    parser.add_argument("--split", choices=("train", "test"), default="train")
    parser.add_argument("--output", required=True, type=Path, help="Output JSONL path")
    args = parser.parse_args()
    try:
        return build_manifest(args.dataset_root, args.category, args.split, args.output)
    except (FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
