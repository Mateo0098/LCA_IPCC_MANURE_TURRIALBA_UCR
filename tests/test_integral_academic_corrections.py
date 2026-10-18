from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_integral_tfg_docx as integral  # noqa: E402


class IntegralAcademicCorrectionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corrected_text = "\n".join(integral.MASTER_PARAGRAPH_OVERRIDES.values())

    def test_reported_regressions_are_absent_from_overrides(self) -> None:
        folded = self.corrected_text.casefold()
        for phrase in integral.ACADEMIC_REGRESSION_PHRASES:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase.casefold(), folded)

    def test_corrected_narrative_citations_are_present(self) -> None:
        for citation in (
            "Vargas Sarmiento (2023)",
            "Rojas y Elizondo (2020)",
            "Komakech et al. (2015)",
            "International Organization for Standardization, 2006",
        ):
            with self.subTest(citation=citation):
                self.assertIn(citation, self.corrected_text)

    def test_climate_values_are_preserved_with_defined_meaning(self) -> None:
        paragraph = integral.MASTER_PARAGRAPH_OVERRIDES[100]
        self.assertIn("precipitación total anual promedio de 2.375,6 mm", paragraph)
        self.assertIn("promedios mensuales de temperatura máxima entre 28,2 °C y 28,5 °C", paragraph)

    def test_jjagwe_warning_preserves_approved_benchmark(self) -> None:
        paragraph = integral.MASTER_PARAGRAPH_OVERRIDES[86]
        self.assertIn("3,943 × 10⁻⁵ g N₂O/kg", paragraph)
        self.assertIn("39,43 mg N₂O/kg", paragraph)
        self.assertIn("sin tratarla como una validación del modelo", paragraph)

    def test_svg_hash_salt_is_stable(self) -> None:
        self.assertEqual(
            integral.SVG_HASHSALT,
            "lca-ipcc-manure-turrialba-ucr",
        )

    def test_nitrogen_contrast_table_supports_positive_negative_and_zero(self) -> None:
        context = {
            "A1": {"reference": 8.0, "model": 10.0, "difference": 2.0, "relative": 25.0},
            "A3": {"reference": 0.012, "model": 0.010, "difference": -0.002, "relative": -16.666},
            "B1": {"reference": 0.02, "model": 0.02, "difference": 0.0, "relative": 0.0},
        }
        table = integral.nitrogen_contrast_table(context)

        self.assertEqual(table.iloc[0]["Diferencia absoluta (modelo − referencia)"], "+2,0 kg N/año")
        self.assertEqual(table.iloc[1]["Diferencia absoluta (modelo − referencia)"], "−0,0020 puntos porcentuales")
        self.assertEqual(table.iloc[2]["Diferencia absoluta (modelo − referencia)"], "0,0000 puntos porcentuales")
        self.assertEqual(table.iloc[0]["Diferencia relativa"], "+25,0 %")
        self.assertEqual(table.iloc[1]["Diferencia relativa"], "−16,7 %")
        self.assertEqual(table.iloc[2]["Diferencia relativa"], "0,0 %")

    def test_nitrogen_narrative_tracks_positive_negative_and_zero(self) -> None:
        context = {
            "A1": {"reference": 8.0, "model": 10.0, "difference": 2.0, "relative": 25.0},
            "A3": {"reference": 0.012, "model": 0.010, "difference": -0.002, "relative": -16.666},
            "B1": {"reference": 0.02, "model": 0.02, "difference": 0.0, "relative": 0.0},
        }
        results = "\n".join(integral.nitrogen_results_paragraphs(context))
        discussion = "\n".join(integral.nitrogen_discussion_paragraphs(context))
        conclusion = integral.nitrogen_conclusion_text(context)

        self.assertIn("conservó más N residual", results)
        self.assertIn("concentración modelada fue menor", results)
        self.assertIn("no se distinguió de la medición M2", results)
        self.assertIn("superó a la referencia derivada", discussion)
        self.assertIn("16,7 % menor", discussion)
        self.assertIn("no mostró una diferencia visible", discussion)
        self.assertIn(
            "superó la referencia en A1, fue inferior a la referencia en aguas verdes y no mostró diferencia visible respecto de la referencia en purines",
            conclusion,
        )

    def test_rounded_zero_has_no_false_positive_or_negative_sign(self) -> None:
        self.assertEqual(
            integral.nitrogen_direction_wording(
                0.004,
                2,
                positive="positivo",
                negative="negativo",
                zero="cero",
            ),
            "cero",
        )
        self.assertEqual(
            integral.format_spanish_number(-0.004, 2, explicit_sign=True),
            "0,00",
        )


if __name__ == "__main__":
    unittest.main()
