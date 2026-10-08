from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from methodological_traceability import (  # noqa: E402
    STAGES,
    build_detailed_rows,
    build_summary_rows,
)


def rows_by_key() -> dict[tuple[str, str], dict[str, str]]:
    return {(row["etapa"][:2], row["identificador_ecuacion"]): row for row in build_detailed_rows()}


def test_six_stages_and_66_relations_remain_covered() -> None:
    rows = build_detailed_rows()
    assert len(rows) == 66
    assert {row["etapa"][:2] for row in rows} == set(STAGES)
    assert len({(row["etapa"][:2], row["identificador_ecuacion"]) for row in rows}) == 66


def test_mass_relations_have_distinct_semantic_identifiers() -> None:
    rows = rows_by_key()
    expected = {"A1": "M11", "A2": "M12", "A3": "M13", "A4": "M14", "B1": "M15", "B2": "M16"}
    assert all((stage, equation_id) in rows for stage, equation_id in expected.items())
    assert len(set(expected.values())) == 6
    assert not any(equation_id == "M01" for _, equation_id in rows)
    assert rows[("A1", "M11")]["procedencia_dato_factor"].startswith("Secundaria")
    assert rows[("A2", "M12")]["procedencia_dato_factor"].startswith("Mixta: primaria y secundaria")
    for stage in ("A3", "A4", "B1", "B2"):
        assert rows[(stage, expected[stage])]["procedencia_dato_factor"].startswith("Secundaria")


def test_equivalent_mass_is_never_presented_as_nitrogen_basis() -> None:
    rows = rows_by_key()
    for key in (("A4", "M14"), ("B2", "M16")):
        output = rows[key]["salida_o_uso_posterior"]
        assert "no constituye nueva masa de N" in output
        assert "base de las ecuaciones de emisiones del suelo" in output


def test_fresh_initialization_and_interstage_propagation_are_distinct() -> None:
    rows = rows_by_key()
    assert all((stage, "N01") in rows for stage in ("A1", "A3", "B1"))
    assert ("A2", "N01") not in rows
    assert all((stage, "N10") in rows for stage in ("A2", "A4", "B2"))
    assert "Sin reinicialización" in rows[("A2", "N10")]["parametro_o_factor"]


def test_calculated_n_relations_keep_inherited_provenance() -> None:
    calculated_ids = {"N02", "N03", "N03K", "N04", "N05", "N06", "N07", "N08", "N09", "N11", "N12", "N13", "N14", "N15", "N16"}
    selected = [row for row in build_detailed_rows() if row["identificador_ecuacion"] in calculated_ids]
    assert selected
    assert all("Mixta: primaria y secundaria" in row["procedencia_dato_factor"] for row in selected)


def test_a1_water_loss_and_later_soil_route_are_separate() -> None:
    rows = rows_by_key()
    n08 = rows[("A1", "N08")]
    n09 = rows[("A1", "N09")]
    assert "N_water_loss" in n08["ecuacion_o_relacion_calculo"]
    assert "no produce directamente NO₃⁻" in n08["salida_o_uso_posterior"]
    assert "drenaje" not in " ".join(n08.values()).casefold()
    assert all(token in n09["ecuacion_o_relacion_calculo"] for token in ("FracLEACH", "62/14", "EF5"))


def test_operational_routes_preserve_component_provenance_and_characterization() -> None:
    rows = rows_by_key()
    for stage in ("A3", "B1"):
        operational = rows[(stage, "O01")]
        c01 = rows[(stage, "C01")]
        assert all(token in operational["procedencia_dato_factor"] for token in ("Primaria:", "No aplica: supuesto del estudio", "Secundaria:"))
        assert "no es una emisión elemental EF 3.1" in operational["salida_o_uso_posterior"]
        assert "E × FE_IMN,elec" in c01["ecuacion_o_relacion_calculo"]
        assert "fuera de Σ(m_i × CF_i,c)" in c01["salida_o_uso_posterior"]
    for stage in ("A4", "B2"):
        operational = rows[(stage, "O02")]
        c01 = rows[(stage, "C01")]
        assert all(token in operational["procedencia_dato_factor"] for token in ("Primaria:", "No aplica: supuesto del estudio", "Secundaria:"))
        assert "flujos fósiles se obtienen primero con IMN" in c01["ecuacion_o_relacion_calculo"]
        assert "IMN → emisiones físicas → EF 3.1" in c01["salida_o_uso_posterior"]


def test_ef3_zero_and_parallel_tan_losses_are_described_as_model_behaviour() -> None:
    rows = rows_by_key()
    for stage in ("A3", "B1"):
        n06 = rows[(stage, "N06")]
        assert "EF3 = 0" in n06["parametro_o_factor"]
        assert "sin afirmar imposibilidad física" in n06["parametro_o_factor"]
    for row in build_detailed_rows():
        if row["identificador_ecuacion"] in {"N03", "N04", "N05"}:
            assert "misma base de TAN antes del descuento conjunto" in row["parametro_o_factor"]


def test_summary_is_derived_and_preserves_semantic_caveats() -> None:
    summary = {row["etapa"][:2]: row for row in build_summary_rows()}
    assert len(summary) == 6
    assert "ruta posterior" in summary["A1"]["procesos_principales"]
    assert "masa húmeda inferida de entrada" in summary["A2"]["datos_actividad"].casefold()
    for stage in ("A3", "B1"):
        text = " ".join(summary[stage].values())
        assert "EF3 vigente igual a cero" in text
        assert "factor agregado IMN" in text
    for stage in ("A4", "B2"):
        text = " ".join(summary[stage].values())
        assert "no como base de N" in text
        assert "IMN → emisiones físicas del diésel → EF 3.1" in text


def test_incomplete_m3_is_absent_from_methodological_view() -> None:
    text = "\n".join(" | ".join(row.values()) for row in build_detailed_rows())
    assert "M3" not in text
    assert "resultados CIA y LASA muestreo 3" not in text
