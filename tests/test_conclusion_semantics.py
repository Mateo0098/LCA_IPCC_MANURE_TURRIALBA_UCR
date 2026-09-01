from __future__ import annotations

import sys
import unittest
from pathlib import Path

from docx import Document


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_provisional_m1_m2_outputs import (  # noqa: E402
    TABLES,
    canonical_stage_dominants,
    validate_c2_semantics,
)


class ConclusionSemanticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        document = Document(ROOT / "outputs" / "documentos_tfg" / "conclusiones_desarrolladas_tfg.docx")
        candidates = [
            paragraph.text for paragraph in document.paragraphs
            if paragraph.text.startswith("Las cargas ambientales se concentraron")
        ]
        if len(candidates) != 1:
            raise AssertionError("No se encontró una única conclusión C2.")
        cls.c2 = candidates[0]
        cls.dominants = canonical_stage_dominants(TABLES / "tabla_07_impactos_por_etapa.csv")

    def test_current_c2_is_semantically_valid(self) -> None:
        validate_c2_semantics(self.c2)

    def test_omission_of_terrestrial_eutrophication_fails(self) -> None:
        altered = self.c2.replace("En eutrofización terrestre,", "En eutrofización,")
        with self.assertRaises(AssertionError):
            validate_c2_semantics(altered)

    def test_swapping_terrestrial_and_marine_dominant_stage_fails(self) -> None:
        terrestrial_stage = self.dominants[("A", "Eutrofización terrestre")][0]
        marine_stage = self.dominants[("A", "Eutrofización marina")][0]
        altered = self.c2.replace(terrestrial_stage, marine_stage, 1)
        with self.assertRaises(AssertionError):
            validate_c2_semantics(altered)

    def test_historical_phrase_fails(self) -> None:
        altered = self.c2 + " Se consideró nitrógeno potencialmente eutrofizante."
        with self.assertRaises(AssertionError):
            validate_c2_semantics(altered)


if __name__ == "__main__":
    unittest.main()
