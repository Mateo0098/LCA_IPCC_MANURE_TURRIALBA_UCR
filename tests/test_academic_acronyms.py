from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from academic_acronyms import (  # noqa: E402
    ACRONYMS,
    acronym_by_code,
    unregistered_acronym_candidates,
)


def test_registry_distinguishes_english_and_conventional_forms() -> None:
    assert acronym_by_code("EEA").requires_english_notice
    assert acronym_by_code("TAN").requires_english_notice
    assert not acronym_by_code("ISO").requires_english_notice
    assert acronym_by_code("ISO").kind == "abreviatura_institucional"
    assert "forma abreviada universal" in acronym_by_code("ISO").list_definition
    assert not acronym_by_code("EMEP").requires_english_notice
    assert acronym_by_code("EMEP").kind == "denominacion_convencional"
    assert "denominación abreviada establecida" in acronym_by_code("EMEP").list_definition


def test_registry_has_unique_codes_and_correct_cia() -> None:
    codes = [entry.code for entry in ACRONYMS]
    assert len(codes) == len(set(codes))
    assert acronym_by_code("CIA").spanish_name == "Centro de Investigaciones Agronómicas"
    assert acronym_by_code("DA").first_mention == "digestión anaeróbica (DA)"


def test_candidate_audit_is_conservative_but_reports_unknowns() -> None:
    texts = [
        "La digestión anaeróbica (DA) se comparó con A1 y M2.",
        "Se aplicaron EMEP/EEA, NO-N, EF4 e ISO/TC 207.",
        "La organización ficticia XYZ requiere clasificación.",
    ]
    assert unregistered_acronym_candidates(texts) == {
        "XYZ": "La organización ficticia XYZ requiere clasificación."
    }
