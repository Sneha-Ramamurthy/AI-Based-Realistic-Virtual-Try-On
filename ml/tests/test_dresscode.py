from pathlib import Path
import tempfile
import unittest

from PIL import Image

from ml.data.dresscode import DressCodeDataset, read_pairs


class DressCodeDatasetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        category = self.root / "upper_body"
        (category / "image").mkdir(parents=True)
        (category / "cloth").mkdir()
        (category / "agnostic-v3.2").mkdir()
        (category / "image-densepose").mkdir()
        (category / "train_pairs.txt").write_text("person_1.jpg shirt_1.jpg\n", encoding="utf-8")
        for folder, filename, color in (
            ("image", "person_1.jpg", "red"),
            ("cloth", "shirt_1.jpg", "blue"),
            ("agnostic-v3.2", "person_1.jpg", "white"),
            ("image-densepose", "person_1.jpg", "green"),
        ):
            Image.new("RGB", (8, 8), color).save(category / folder / filename)

    def tearDown(self):
        self.temp.cleanup()

    def test_reads_pair_and_optional_inputs(self):
        dataset = DressCodeDataset(self.root, category="upper_body", split="train")
        sample = dataset[0]
        self.assertEqual(len(dataset), 1)
        self.assertEqual(sample["person"].size, (8, 8))
        self.assertEqual(sample["garment"].size, (8, 8))
        self.assertEqual(sample["target"].size, (8, 8))
        self.assertIsNotNone(sample["agnostic"])
        self.assertIsNotNone(sample["densepose"])

    def test_missing_optional_directories_return_none(self):
        category = self.root / "upper_body"
        (category / "agnostic-v3.2").rename(category / "agnostic-removed")
        (category / "image-densepose").rename(category / "densepose-removed")
        sample = DressCodeDataset(self.root)[0]
        self.assertIsNone(sample["agnostic"])
        self.assertIsNone(sample["densepose"])

    def test_rejects_malformed_pair_line(self):
        pair_file = self.root / "malformed.txt"
        pair_file.write_text("only_one_name\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            read_pairs(pair_file)


if __name__ == "__main__":
    unittest.main()
