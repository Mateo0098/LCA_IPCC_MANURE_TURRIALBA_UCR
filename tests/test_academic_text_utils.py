from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from academic_text_utils import (  # noqa: E402
    clean_academic_label,
    clean_avoidable_anglicisms,
    clean_chemical_notation,
)


def test_area_and_volume_units_are_spaced_and_superscripted() -> None:
    source = "Superficies de 15m2, 60m2 y 81m2; volúmenes de 2m3 y 11,25 m3."
    assert clean_chemical_notation(source) == (
        "Superficies de 15 m², 60 m² y 81 m²; volúmenes de 2 m³ y 11,25 m³."
    )


def test_negative_powers_of_ten_use_unicode_superscripts() -> None:
    source = "1,18 × 10-8; 2,17 × 10−9; 4 × 10^-5"
    assert clean_chemical_notation(source) == "1,18 × 10⁻⁸; 2,17 × 10⁻⁹; 4 × 10⁻⁵"


def test_humeda_does_not_corrupt_humedad() -> None:
    assert clean_academic_label("masa humeda y contenido de humedad") == (
        "masa húmeda y contenido de humedad"
    )


def test_free_prose_is_not_rewritten_word_by_word() -> None:
    source = "el benchmark usa un proxy y el pool residual"
    assert clean_avoidable_anglicisms(source) == source


def test_nox_label_is_translated_without_changing_the_species() -> None:
    assert clean_academic_label("mol N-eq/kg NOx as NO2") == (
        "mol N-eq/kg NOx como NO₂"
    )


def test_controlled_ledger_labels_are_translated_as_complete_phrases() -> None:
    assert clean_academic_label("Factor del ledger de N total y TAN") == (
        "Factor del balance secuencial de N total y TAN"
    )
    assert clean_academic_label("Benchmark FracGasMS de A1") == (
        "Referencia de contraste FracGasMS de A1"
    )
