from __future__ import annotations

import sys
import unittest
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_integral_tfg_docx as integral  # noqa: E402


class IntegralSimaProAcademicTests(unittest.TestCase):
    def test_aggregate_registry_matches_python_summary(self) -> None:
        comparison = integral.simapro_aggregate_comparison()
        self.assertEqual(len(comparison), 6)
        self.assertEqual(set(comparison["escenario"]), {"A", "B"})
        self.assertTrue(comparison["clasificacion_A_H"].eq("A").all())
        self.assertTrue(
            comparison["alcance"].str.contains(
                "electricidad IMN excluida", regex=False
            ).all()
        )

    def test_aggregate_differences_are_simapro_minus_python(self) -> None:
        comparison = integral.simapro_aggregate_comparison()
        for row in comparison.itertuples():
            expected = Decimal(row.resultado_simapro_observado) - Decimal(
                row.resultado_python_esperado
            )
            self.assertEqual(row.diferencia_calculada, expected)

    def test_unit_registry_preserves_nine_factors_and_seven_results(self) -> None:
        table = integral.simapro_unit_academic_table()
        self.assertEqual(len(table), 9)
        self.assertEqual((table["Clasificación"] == "B").sum(), 1)
        self.assertEqual(
            table["Observación en SimaPro"].str.contains(
                "sin resultado unitario independiente", regex=False
            ).sum(),
            2,
        )

    def test_appendix_f_is_part_of_the_integral_structure(self) -> None:
        self.assertIn(
            "Apéndice F. Trazabilidad de la verificación independiente Python–SimaPro",
            integral.EXPECTED_HEADINGS,
        )


if __name__ == "__main__":
    unittest.main()
