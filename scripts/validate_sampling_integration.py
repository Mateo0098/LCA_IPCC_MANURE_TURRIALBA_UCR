"""Valida la integración estadística provisional sin ejecutar ni alterar el ACV."""

from __future__ import annotations

import ast
import csv
import hashlib
import math
import statistics
from pathlib import Path

from build_sampling_integration import _build_row, _fmt, build_mass_transformation_rows
from sampling_integration_rules import RULES_BY_KEY


ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "scripts" / "build_sampling_integration.py"
SOURCE = ROOT / "processed" / "muestreos_resumen_intrajornada.csv"
OUTPUT = ROOT / "processed" / "muestreos_integracion_interjornada_provisional.csv"
MASS_OUTPUT = ROOT / "processed" / "muestreos_transformacion_masa_interjornada.csv"
HISTORICAL_M1 = ROOT / "processed" / "volatile_solids_mass_loss_fresh_to_precomposted.csv"
PROTECTED = [
    "processed/ACV_resumen_emisiones.csv", "processed/acv_impacto_por_etapa_escenario.csv",
    "processed/acv_impacto_total_por_escenario.csv", "processed/masa_total_escenario_etapa.csv",
    "processed/acv_parametros_escenario_etapa.csv",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    before = {name: sha256(ROOT / name) for name in PROTECTED}
    source = _rows(SOURCE)
    result = _rows(OUTPUT)
    mass_result = _rows(MASS_OUTPUT)
    build_text = BUILD.read_text(encoding="utf-8")
    tree = ast.parse(build_text)
    literals = {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)}
    assert "muestreos_resumen_intrajornada.csv" in literals
    assert "muestreos_observaciones_normalizadas.csv" not in build_text
    keys = [(r["jornada"], r["material"], r["variable"]) for r in source]
    assert len(keys) == len(set(keys)), "Hay jornadas duplicadas en la fuente"
    source_has_m3 = any(row["jornada"] == "M3" for row in source)
    if not source_has_m3:
        assert all(r["estado_integracion"] != "final" for r in result)
    indexed = {(r["material"], r["variable"]): r for r in result}
    assert len(result) == 16
    assert sum(r["estado_integracion"] == "provisional_M1_M2" for r in result) == 10
    assert sum(r["estado_integracion"] == "provisional_M2_pendiente_M3" for r in result) == 2
    assert sum(r["estado_integracion"] == "solo_caracterizacion" for r in result) == 4
    assert _fmt(1.2345678901234567) == str(1.2345678901234567)
    for material in ("estiércol fresco", "estiércol precompostado"):
        for variable in ("N total", "humedad", "materia seca", "cenizas", "sólidos volátiles"):
            row = indexed[(material, variable)]
            values = dict(item.split("=", 1) for item in row["promedios_jornada"].split(";"))
            expected = (float(values["M1"]) + float(values["M2"])) / 2
            assert math.isclose(float(row["valor_integrado_provisional"]), expected, rel_tol=1e-12)
            assert row["numero_jornadas_elegibles"] == "2"
            assert row["estado_integracion"] == "provisional_M1_M2"
            rule = RULES_BY_KEY[(material, variable)]
            source_pair = [
                item for item in source
                if (item["material"], item["variable"]) == (material, variable)
            ]
            m1 = next(item for item in source_pair if item["jornada"] == "M1")
            m2 = next(item for item in source_pair if item["jornada"] == "M2")
            m3 = {**m2, "jornada": "M3"}
            assert _build_row(rule, [m1, m2])["estado_integracion"] == "provisional_M1_M2"
            assert _build_row(rule, [m1, m2, m3])["estado_integracion"] == "final"
            assert _build_row(rule, [m1, m3])["estado_integracion"] == "provisional_incompleto"
            assert _build_row(rule, [m2, m3])["estado_integracion"] == "provisional_incompleto"
            incompatible_m3 = {**m3, "metodo": "método incompatible"}
            assert _build_row(rule, [m1, m2, incompatible_m3])["estado_integracion"] != "final"
    for material in ("aguas verdes", "purines"):
        row = indexed[(material, "N total")]
        assert row["jornadas_elegibles"] == "M2" and "M1=" not in row["promedios_jornada"]
        assert row["estado_integracion"] == "provisional_M2_pendiente_M3"
        assert row["valor_integrado_provisional"] != ""
        values = dict(item.split("=", 1) for item in row["promedios_jornada"].split(";") if item)
        assert set(values) == {"M2"}
        assert math.isclose(float(row["valor_integrado_provisional"]), float(values["M2"]), rel_tol=1e-12)
        rule = RULES_BY_KEY[(material, "N total")]
        m2 = next(
            item for item in source
            if (item["jornada"], item["material"], item["variable"]) == ("M2", material, "N total")
        )
        m3 = {**m2, "jornada": "M3"}
        provisional = _build_row(rule, [m2])
        assert provisional["estado_integracion"] == "provisional_M2_pendiente_M3"
        assert math.isclose(float(provisional["valor_integrado_provisional"]), float(m2["promedio_jornada"]), rel_tol=1e-12)
        assert _build_row(rule, [m2, m3])["estado_integracion"] == "final"
        incompatible_m3 = {**m3, "metodo": "método incompatible"}
        assert _build_row(rule, [m2, incompatible_m3])["estado_integracion"] == "provisional_M2_pendiente_M3"
    pre_n = indexed[("estiércol precompostado", "N total")]
    assert "No se aplica conversión" in pre_n["observacion_metodologica"]
    for row in result:
        if row["estado_integracion"] == "solo_caracterizacion":
            assert "no es parámetro" in row["uso_previsto"]
    assert "numero_muestras_compuestas" not in build_text and "numero_replicas_analiticas" not in build_text
    mass_journeys = {row["jornada"]: row for row in mass_result if row["tipo_fila"] == "jornada"}
    mass_summary = next(row for row in mass_result if row["tipo_fila"] == "integracion")
    assert set(mass_journeys) == {"M1", "M2"}
    assert mass_summary["jornadas_elegibles"] == "M1;M2"
    assert mass_summary["numero_jornadas"] == "2"
    assert mass_summary["estado_integracion"] == "provisional_M1_M2"
    expected_integrated = statistics.fmean(
        float(mass_journeys[j]["mass_ratio_precomp_over_fresh"]) for j in ("M1", "M2")
    )
    assert math.isclose(float(mass_summary["mass_ratio_integrado"]), expected_integrated, rel_tol=1e-15)
    assert math.isclose(
        float(mass_summary["mass_loss_pct_integrado"]),
        (1.0 - float(mass_summary["mass_ratio_integrado"])) * 100.0,
        rel_tol=1e-15,
    )
    historical = _rows(HISTORICAL_M1)[0]
    assert math.isclose(
        float(mass_journeys["M1"]["mass_ratio_precomp_over_fresh"]),
        float(historical["mass_ratio_to_over_from"]),
        abs_tol=5e-7,
    ), "M1 no reproduce el factor histórico dentro de la precisión persistida"
    gravimetric = [
        row for row in source
        if row["material"] in {"estiércol fresco", "estiércol precompostado"}
        and row["variable"] in {"materia seca", "cenizas"}
    ]
    m1 = [row for row in gravimetric if row["jornada"] == "M1"]
    m2 = [row for row in gravimetric if row["jornada"] == "M2"]
    m3 = [{**row, "jornada": "M3"} for row in m2]
    assert build_mass_transformation_rows(m1 + m2)[-1]["estado_integracion"] == "provisional_M1_M2"
    assert build_mass_transformation_rows(m1 + m2 + m3)[-1]["estado_integracion"] == "final"
    assert build_mass_transformation_rows(m1 + m3)[-1]["estado_integracion"] == "provisional_incompleto"
    assert build_mass_transformation_rows(m2 + m3)[-1]["estado_integracion"] == "provisional_incompleto"
    assert build_mass_transformation_rows(m1 + m2 + m3[:-1])[-1]["estado_integracion"] != "final"
    after = {name: sha256(ROOT / name) for name in PROTECTED}
    assert before == after, "La validación modificó archivos protegidos del ACV"
    print(
        f"VALIDACIÓN CORRECTA: {len(result)} reglas; integración válida; "
        "archivos protegidos del ACV sin cambios durante la validación."
    )
    for name in PROTECTED:
        print(f"{after[name]}  {name}")


if __name__ == "__main__":
    main()
