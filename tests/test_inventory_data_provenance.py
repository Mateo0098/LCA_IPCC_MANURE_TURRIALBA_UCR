from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from inventory_data_provenance import (  # noqa: E402
    ACADEMIC_PROVENANCE,
    EXPECTED_FAMILY_IDS,
    MACROFAMILY_DEFINITIONS,
    build_provenance_rows,
    build_provenance_summary_rows,
)


def rows_by_id() -> dict[str, dict[str, str]]:
    return {row["id_familia"]: row for row in build_provenance_rows()}


def test_all_active_inventory_families_have_provenance_and_source() -> None:
    rows = rows_by_id()
    assert set(rows) == EXPECTED_FAMILY_IDS
    assert all(row["procedencia_academica"] in ACADEMIC_PROVENANCE for row in rows.values())
    assert all(row["fuente_concreta"].strip() for row in rows.values())
    assert all(row["uso_metodologico"].strip() for row in rows.values())


def test_experimental_services_remain_primary_evidence() -> None:
    row = rows_by_id()["experimental_characterization"]
    assert row["procedencia_academica"] == "Primaria"
    assert "CIA/LASA" in row["fuente_concreta"]
    assert "servicio analítico externo" in row["subtipo_procedencia"]


def test_published_and_official_factors_remain_secondary() -> None:
    rows = rows_by_id()
    for family in (
        "published_farm_operations",
        "ipcc_factors",
        "emep_factors",
        "literature_factor",
        "imn_factors",
        "ef31_factors",
    ):
        assert rows[family]["procedencia_academica"] == "Secundaria"
        assert rows[family]["fuente_concreta"].strip()


def test_transformations_do_not_become_tertiary_sources() -> None:
    rows = rows_by_id()
    for family in ("mass_transformation", "calculated_inventory_flows", "propagated_nitrogen"):
        assert "Terciaria" not in rows[family]["procedencia_academica"]
        assert any(
            term in rows[family]["tratamiento_tfg"]
            for term in ("Calculado", "Derivado", "integrado", "propagado")
        )


def test_incomplete_m3_is_absent_from_active_provenance_matrix() -> None:
    text = "\n".join(" | ".join(row.values()) for row in build_provenance_rows())
    assert "M3" not in text
    assert "resultados CIA y LASA muestreo 3" not in text


def test_no_quantitative_active_family_is_forced_into_tertiary_category() -> None:
    assert not any(
        row["procedencia_academica"] == "Terciaria"
        for row in build_provenance_rows()
    )


def test_unreferenced_operational_assumptions_are_not_primary_sources() -> None:
    row = rows_by_id()["field_based_assumptions"]
    assert row["procedencia_academica"] == "No aplica: supuesto del estudio"
    assert row["subtipo_procedencia"] == "Supuesto numérico definido para el modelo"
    assert row["tratamiento_tfg"] == "Supuesto del estudio"
    assert "contexto operativo" in row["fuente_concreta"]


def test_mixed_families_keep_inherited_and_separable_provenance() -> None:
    rows = rows_by_id()
    for family in ("calculated_inventory_flows", "propagated_nitrogen"):
        row = rows[family]
        assert row["procedencia_academica"] == "Mixta: primaria y secundaria"
        assert "heredada y separable" in row["subtipo_procedencia"]
        assert "no constituye una tercera clase" in row["subtipo_procedencia"]
        assert "matriz metodológica A1–B2" in row["uso_metodologico"]


def test_body_macrofamilies_cover_each_detailed_family_exactly_once() -> None:
    summary = build_provenance_summary_rows()
    grouped_ids = [
        family_id
        for definition in MACROFAMILY_DEFINITIONS
        for family_id in definition["family_ids"]
    ]
    assert len(summary) == 6
    assert len(grouped_ids) == 15
    assert len(grouped_ids) == len(set(grouped_ids))
    assert set(grouped_ids) == EXPECTED_FAMILY_IDS
    assert all(set(row) == {
        "macrofamilia",
        "procedencia_general",
        "tratamiento_general",
        "funcion_icv",
    } for row in summary)
