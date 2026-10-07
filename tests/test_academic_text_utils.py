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
    find_campaign_unit_corruptions,
)
from generate_methodology_docx import clean_text as clean_methodology_text  # noqa: E402


def test_area_and_volume_units_are_spaced_and_superscripted() -> None:
    source = "Superficies de 15m2, 60m2 y 81m2; volúmenes de 2m3 y 11,25 m3."
    assert clean_chemical_notation(source) == (
        "Superficies de 15 m², 60 m² y 81 m²; volúmenes de 2 m³ y 11,25 m³."
    )


def test_bare_lowercase_area_and_volume_units_are_superscripted() -> None:
    assert clean_chemical_notation("Unidades: m2 y m3") == "Unidades: m² y m³"


def test_sampling_campaign_identifiers_are_preserved() -> None:
    samples = (
        "M1",
        "M2",
        "M3",
        "M1–M2",
        "PROVISIONAL M1–M2",
        "jornada M2",
        "campaña M3",
        "En M2",
        "M3 permanece pendiente",
    )
    for source in samples:
        assert clean_chemical_notation(source) == source
        assert clean_academic_label(source) == source


def test_campaign_corruption_detector_is_context_specific() -> None:
    corruptions = (
        "PROVISIONAL M1–m²",
        "M1;m²",
        "provisional M1 m²",
        "provisional m² pendiente m³",
        "La jornada m³ permanece pendiente",
        "En M1 hubo dos muestras. En m² se obtuvieron tres muestras.",
        "El N procedió de m² mediante Kjeldahl.",
        "La fase pre-m³ no es definitiva.",
        "Después de m³ se actualizará el análisis.",
    )
    for source in corruptions:
        assert find_campaign_unit_corruptions(source)

    legitimate_units = (
        "La superficie fue de 60 m².",
        "El volumen fue de 11,25 m³.",
        "El factor se expresó en m³ CH₄/kg SV.",
    )
    for source in legitimate_units:
        assert not find_campaign_unit_corruptions(source)


def test_negative_powers_of_ten_use_unicode_superscripts() -> None:
    source = "1,18 × 10-8; 2,17 × 10−9; 4 × 10^-5"
    assert clean_chemical_notation(source) == "1,18 × 10⁻⁸; 2,17 × 10⁻⁹; 4 × 10⁻⁵"


def test_existing_chemical_subscripts_and_superscripts_are_preserved() -> None:
    source = "CH4, N2O, NH3, NO3-, CO2 y PO4^3-; ya: CH₄, N₂O, m² y m³."
    assert clean_chemical_notation(source) == (
        "CH₄, N₂O, NH₃, NO₃⁻, CO₂ y PO₄³⁻; ya: CH₄, N₂O, m² y m³."
    )


def test_humeda_does_not_corrupt_humedad() -> None:
    assert clean_academic_label("masa humeda y contenido de humedad") == (
        "masa húmeda y contenido de humedad"
    )


def test_free_prose_is_not_rewritten_word_by_word() -> None:
    source = "el benchmark usa un proxy y el pool residual"
    assert clean_avoidable_anglicisms(source) == source


def test_measured_treatment_in_prose_is_not_promoted_to_factor_label() -> None:
    source = "medido, observado, publicado, supuesto, calculado, integrado y propagado"
    assert clean_methodology_text(source) == source
    assert clean_methodology_text("medido") == "Factor medido"
    assert clean_methodology_text("Factor medido") == "Factor medido"


def test_official_emep_eea_title_is_preserved_verbatim() -> None:
    title = "EMEP/EEA Air Pollutant Emission Inventory Guidebook 2023"
    assert clean_academic_label(title) == title


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
