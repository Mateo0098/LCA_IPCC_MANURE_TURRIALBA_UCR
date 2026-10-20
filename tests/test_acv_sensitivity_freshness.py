from __future__ import annotations

import hashlib
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_acv_sensitivity as sensitivity  # noqa: E402
import generate_integral_tfg_docx as integral  # noqa: E402


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AcvSensitivityFreshnessTests(unittest.TestCase):
    def _fixture(self, directory: Path) -> dict[str, Path]:
        sources = {
            "canonical_stage_path": sensitivity.CANONICAL_STAGE_IMPACTS,
            "canonical_scenario_path": sensitivity.CANONICAL_SCENARIO_IMPACTS,
            "sensitivity_stage_path": sensitivity.SENSITIVITY_STAGE_IMPACTS,
            "sensitivity_scenario_path": sensitivity.SENSITIVITY_SCENARIO_IMPACTS,
            "comparison_path": sensitivity.SENSITIVITY_COMPARISON,
            "threshold_path": sensitivity.SENSITIVITY_THRESHOLD,
            "figure_path": sensitivity.SENSITIVITY_FIGURE,
        }
        paths: dict[str, Path] = {}
        for key, source in sources.items():
            destination = directory / source.name
            shutil.copy2(source, destination)
            paths[key] = destination
        paths["provenance_path"] = directory / sensitivity.SENSITIVITY_PROVENANCE.name
        sensitivity.write_sensitivity_provenance(**paths)
        return paths

    def test_current_outputs_are_fresh_for_all_categories_and_stages(self) -> None:
        result = sensitivity.validate_sensitivity_freshness()
        self.assertLessEqual(result["maximum_stage_error"], 1e-11)
        self.assertLessEqual(result["maximum_scenario_error"], 1e-11)
        self.assertLessEqual(result["maximum_comparison_error"], 1e-11)

    def test_incompatible_reference_case_is_rejected_with_regeneration_command(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = self._fixture(Path(temporary))
            comparison = pd.read_csv(paths["comparison_path"], encoding="utf-8-sig")
            selector = comparison["Caso"].eq("MCF_38") & comparison[
                "Categoría de impacto"
            ].eq("Eutrofización terrestre")
            comparison.loc[selector, "Impacto escenario A"] += 1.0
            comparison.to_csv(paths["comparison_path"], index=False, encoding="utf-8-sig")
            sensitivity.write_sensitivity_provenance(**paths)

            with self.assertRaisesRegex(
                RuntimeError,
                r"difiere del valor canónico.*python scripts/generate_acv_sensitivity.py",
            ):
                sensitivity.validate_sensitivity_freshness(**paths)

    def test_missing_category_or_stage_is_rejected(self) -> None:
        cases = (
            ("Categoría de impacto", "Eutrofización marina"),
            ("Etapa", "A3"),
        )
        for column, value in cases:
            with self.subTest(column=column, value=value), tempfile.TemporaryDirectory() as temporary:
                paths = self._fixture(Path(temporary))
                stage = pd.read_csv(paths["sensitivity_stage_path"], encoding="utf-8-sig")
                stage = stage[~stage[column].eq(value)]
                stage.to_csv(
                    paths["sensitivity_stage_path"], index=False, encoding="utf-8-sig"
                )
                sensitivity.write_sensitivity_provenance(**paths)

                with self.assertRaisesRegex(RuntimeError, r"categoría, etapa"):
                    sensitivity.validate_sensitivity_freshness(**paths)

    def test_stale_figure_is_rejected_by_run_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            paths = self._fixture(Path(temporary))
            paths["figure_path"].write_bytes(paths["figure_path"].read_bytes() + b"stale")
            with self.assertRaisesRegex(RuntimeError, r"huellas.*no coinciden"):
                sensitivity.validate_sensitivity_freshness(**paths)

    def test_validation_does_not_modify_canonical_files(self) -> None:
        canonical = sensitivity.CANONICAL_GUARDS
        before = {path: _sha256(path) for path in canonical}
        sensitivity.validate_sensitivity_freshness()
        after = {path: _sha256(path) for path in canonical}
        self.assertEqual(before, after)

    def test_integral_input_validation_invokes_freshness_guard(self) -> None:
        message = "freshness guard invoked"
        with patch.object(
            integral.acv_sensitivity_source,
            "validate_sensitivity_freshness",
            side_effect=RuntimeError(message),
        ):
            with self.assertRaisesRegex(RuntimeError, message):
                integral.validate_inputs()


if __name__ == "__main__":
    unittest.main()
