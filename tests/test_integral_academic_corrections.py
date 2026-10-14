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


if __name__ == "__main__":
    unittest.main()
