from __future__ import annotations

import sys
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_simapro_ef31_qa as qa  # noqa: E402
from generate_simapro_ef31_qa import (  # noqa: E402
    build_observation_template,
    build_provisional_inventory,
    build_summary,
    build_unit_cases,
    validate_against_canonical_impacts,
)


class SimaProEF31QATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.unit_cases = build_unit_cases()
        cls.inventory = build_provisional_inventory()

    def test_all_active_factor_combinations_have_unit_case(self) -> None:
        factors = pd.read_csv(ROOT / "processed" / "acv_factores_equivalencia.csv")
        self.assertEqual(len(self.unit_cases), len(factors))
        self.assertEqual(len(self.unit_cases), 9)
        keys = ["flujo_python", "compartimento_python", "categoria_ef31"]
        self.assertFalse(self.unit_cases.duplicated(keys).any())
        self.assertTrue((self.unit_cases["cantidad_entrada"] == 1.0).all())
        self.assertTrue(
            (self.unit_cases["factor_python"] == self.unit_cases["resultado_python_esperado"]).all()
        )

    def test_provisional_inventory_reproduces_active_ef_subtotals(self) -> None:
        validate_against_canonical_impacts(self.inventory)
        self.assertTrue(self.inventory["corrida_python"].eq("PROVISIONAL M1–M2").all())
        self.assertFalse(self.inventory["flujo_python"].str.contains("Electricidad", case=False).any())
        self.assertFalse(self.inventory["unidad"].str.contains("kWh", case=False).any())
        self.assertEqual(
            set(self.inventory["origen_emision"]),
            {"manejo del estiércol", "combustión operacional de diésel"},
        )

    def test_summary_has_only_verifiable_ef_categories(self) -> None:
        summary = build_summary(self.inventory)
        self.assertEqual(len(summary), 6)
        self.assertEqual(set(summary["escenario"]), {"A", "B"})
        self.assertEqual(
            set(summary["categoria_ef31"]),
            {"Cambio climático", "Eutrofización terrestre", "Eutrofización marina"},
        )
        self.assertTrue(summary["resultado_simapro_observado"].eq("").all())

    def test_observation_template_is_blank_for_simapro_fields(self) -> None:
        template = build_observation_template(self.unit_cases)
        for column in [
            "version_simapro",
            "nombre_metodo_simapro",
            "factor_simapro_observado",
            "resultado_simapro_observado",
            "clasificacion_A_H",
            "evidencia_conservada",
        ]:
            self.assertTrue(template[column].eq("").all(), column)

    def test_generator_does_not_depend_on_session_evidence(self) -> None:
        with TemporaryDirectory(dir=ROOT) as temporary:
            output_dir = Path(temporary) / "qa_output_without_session_evidence"
            with patch.object(qa, "OUTPUT_DIR", output_dir), redirect_stdout(StringIO()):
                qa.main()

            expected = {
                "casos_unitarios_python_ef31.csv",
                "inventario_provisional_m1_m2_para_simapro.csv",
                "resumen_python_provisional_m1_m2_ef31.csv",
                "plantilla_registro_presencial_simapro.csv",
                "MANIFIESTO_QA_QC.md",
            }
            self.assertEqual({path.name for path in output_dir.iterdir()}, expected)
            manifest = (output_dir / "MANIFIESTO_QA_QC.md").read_text(encoding="utf-8")
            self.assertIn("manifiesto de insumos", manifest)
            self.assertNotIn("2026-10-07", manifest)


if __name__ == "__main__":
    unittest.main()
