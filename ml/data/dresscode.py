"""Reader and PyTorch Dataset for the DressCode paired-image layout.

The loader reads pair-list files and resolves images from the extracted dataset;
it does not download, modify, or redistribute dataset assets.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

from PIL import Image
from torch.utils.data import Dataset


_CATEGORY_ALIASES = {
    "upper_body": ("upper_body", "upper-body", "upperbody"),
    "lower_body": ("lower_body", "lower-body", "lowerbody"),
    "dresses": ("dresses", "dress"),
}
_IMAGE_DIRS = ("image", "images")
_CLOTH_DIRS = ("cloth", "clothes", "garment", "garments")
_AGNOSTIC_DIRS = ("agnostic-v3.2", "agnostic-v3", "agnostic")
_DENSEPOSE_DIRS = ("image-densepose", "densepose", "dense_pose")
_EXTENSIONS = ("", ".jpg", ".jpeg", ".png", ".webp")


@dataclass(frozen=True)
class DressCodePair:
    person_name: str
    garment_name: str


def _category_dir(root: Path, category: str) -> Path:
    aliases = _CATEGORY_ALIASES.get(category, (category,))
    for alias in aliases:
        candidate = root / alias
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError(
        f"Could not find category {category!r} under {root}. "
        f"Expected one of: {', '.join(aliases)}"
    )


def _pair_file(root: Path, category_dir: Path, split: str) -> Path:
    candidates = (
        category_dir / f"{split}_pairs.txt",
        root / f"{split}_pairs.txt",
        category_dir / f"{split}.txt",
        root / f"{split}.txt",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    tried = ", ".join(str(path) for path in candidates)
    raise FileNotFoundError(f"No pair list found; checked: {tried}")


def read_pairs(pair_file: str | Path) -> list[DressCodePair]:
    """Read whitespace-delimited person/garment names, ignoring blank/comment lines."""
    path = Path(pair_file)
    pairs: list[DressCodePair] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            columns = line.split()
            if len(columns) < 2:
                raise ValueError(f"{path}:{line_number}: expected person and garment filenames")
            pairs.append(DressCodePair(columns[0], columns[1]))
    return pairs


def _resolve_image(directory: Path, name: str) -> Optional[Path]:
    """Resolve a filename, accepting a missing extension and common image formats."""
    name_path = Path(name)
    names = (name,) if name_path.suffix else tuple(name + ext for ext in _EXTENSIONS[1:])
    for candidate_name in names:
        candidate = directory / candidate_name
        if candidate.is_file():
            return candidate
    return None


class DressCodeDataset(Dataset):
    """Paired DressCode samples yielding PIL images and their source paths.

    `target` is the paired person image. `agnostic` and `densepose` are `None`
    when the corresponding optional directory or file is absent. A transform, if
    supplied, is independently applied to each present image.
    """

    def __init__(
        self,
        root: str | Path,
        category: str = "upper_body",
        split: str = "train",
        transform: Optional[Callable] = None,
    ) -> None:
        self.root = Path(root).expanduser().resolve()
        if split not in {"train", "test"}:
            raise ValueError("split must be 'train' or 'test'")
        self.category = category
        self.split = split
        self.transform = transform
        self.category_dir = _category_dir(self.root, category)
        self.pair_file = _pair_file(self.root, self.category_dir, split)
        self.pairs = read_pairs(self.pair_file)
        self.image_dir = self._find_dir(_IMAGE_DIRS, required=True)
        self.cloth_dir = self._find_dir(_CLOTH_DIRS, required=True)
        self.agnostic_dir = self._find_dir(_AGNOSTIC_DIRS)
        self.densepose_dir = self._find_dir(_DENSEPOSE_DIRS)

    def _find_dir(self, aliases: tuple[str, ...], required: bool = False) -> Optional[Path]:
        for name in aliases:
            candidate = self.category_dir / name
            if candidate.is_dir():
                return candidate
        if required:
            raise FileNotFoundError(
                f"Required image directory not found under {self.category_dir}; "
                f"expected one of: {', '.join(aliases)}"
            )
        return None

    def __len__(self) -> int:
        return len(self.pairs)

    def _path(self, directory: Optional[Path], name: str, kind: str) -> Optional[Path]:
        if directory is None:
            return None
        path = _resolve_image(directory, name)
        if path is None and kind in {"person", "garment"}:
            raise FileNotFoundError(f"{kind} image {name!r} not found in {directory}")
        return path

    def _open(self, path: Optional[Path], mode: str = "RGB") -> Optional[Image.Image]:
        if path is None:
            return None
        with Image.open(path) as image:
            result = image.convert(mode)
        return self.transform(result) if self.transform else result

    def __getitem__(self, index: int) -> dict:
        pair = self.pairs[index]
        person_path = self._path(self.image_dir, pair.person_name, "person")
        garment_path = self._path(self.cloth_dir, pair.garment_name, "garment")
        agnostic_path = self._path(self.agnostic_dir, pair.person_name, "agnostic")
        densepose_path = self._path(self.densepose_dir, pair.person_name, "densepose")
        return {
            "person": self._open(person_path),
            "garment": self._open(garment_path),
            "target": self._open(person_path),
            "agnostic": self._open(agnostic_path),
            "densepose": self._open(densepose_path),
            "person_name": pair.person_name,
            "garment_name": pair.garment_name,
            "category": self.category,
            "split": self.split,
        }
