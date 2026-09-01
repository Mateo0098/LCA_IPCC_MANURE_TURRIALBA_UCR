from __future__ import annotations

import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_thesis_graphics as graphics_generator  # noqa: E402
from validate_provisional_m1_m2_outputs import (  # noqa: E402
    GRAPHICS,
    HISTORICAL_GRAPH_STEMS,
    TABLES,
    compare_graphics_snapshot,
    validate_graph_sources_and_freshness,
)


class DeterministicGraphValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.expected_context = tempfile.TemporaryDirectory(prefix="expected_graphics_")
        cls.expected = Path(cls.expected_context.name)
        graphics_generator.main(output_dir=cls.expected, table_dir=TABLES)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.expected_context.cleanup()

    def copy_canonical_graphics(self, destination: Path) -> Path:
        copied = destination / "graphics"
        shutil.copytree(GRAPHICS, copied)
        return copied

    def test_canonical_graphics_pass_full_validation(self) -> None:
        validate_graph_sources_and_freshness(GRAPHICS)

    def test_mtime_changes_do_not_fail(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mtime_graphics_") as folder:
            copied = self.copy_canonical_graphics(Path(folder))
            original_mtimes = {path.name: path.stat().st_mtime_ns for path in copied.iterdir()}
            for index, path in enumerate(sorted(copied.iterdir())):
                timestamp = 946684800 + index
                os.utime(path, (timestamp, timestamp))
            self.assertTrue(any(path.stat().st_mtime_ns != original_mtimes[path.name] for path in copied.iterdir()))
            compare_graphics_snapshot(copied, self.expected)

    def test_pixel_change_fails(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pixel_graphics_") as folder:
            copied = self.copy_canonical_graphics(Path(folder))
            target = copied / "fig_11_impactos_cambio_climatico_etapa.png"
            with Image.open(target) as image:
                changed = image.copy()
            pixel = changed.getpixel((0, 0))
            if isinstance(pixel, tuple):
                replacement = ((pixel[0] + 1) % 256, *pixel[1:])
            else:
                replacement = (int(pixel) + 1) % 256
            changed.putpixel((0, 0), replacement)
            changed.save(target)
            with self.assertRaises(AssertionError):
                compare_graphics_snapshot(copied, self.expected)

    def test_missing_expected_graph_fails(self) -> None:
        with tempfile.TemporaryDirectory(prefix="missing_graphics_") as folder:
            copied = self.copy_canonical_graphics(Path(folder))
            (copied / "fig_12_impactos_eutrofizacion_terrestre_etapa.svg").unlink()
            with self.assertRaises(AssertionError):
                compare_graphics_snapshot(copied, self.expected)

    def test_historical_graph_fails(self) -> None:
        with tempfile.TemporaryDirectory(prefix="historical_graphics_") as folder:
            copied = self.copy_canonical_graphics(Path(folder))
            historical = sorted(HISTORICAL_GRAPH_STEMS)[0] + ".png"
            shutil.copy2(copied / "fig_11_impactos_cambio_climatico_etapa.png", copied / historical)
            with self.assertRaises(AssertionError):
                compare_graphics_snapshot(copied, self.expected)


if __name__ == "__main__":
    unittest.main()
