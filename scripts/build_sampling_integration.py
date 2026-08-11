"""Construye la integración interjornada provisional M1–M2."""

from __future__ import annotations

import csv
import statistics
from pathlib import Path

from sampling_integration_rules import INTEGRATION_RULES, MASS_TRANSFORMATION_RULE


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "processed" / "muestreos_resumen_intrajornada.csv"
OUTPUT = ROOT / "processed" / "muestreos_integracion_interjornada_provisional.csv"
REPORT = ROOT / "auditoria_integracion_estadistica_m1_m2.md"
MASS_TRANSFORMATION_OUTPUT = ROOT / "processed" / "muestreos_transformacion_masa_interjornada.csv"

FIELDNAMES = [
    "material", "variable", "unidad", "metodo_o_compatibilidad", "jornadas_disponibles",
    "jornadas_elegibles", "numero_jornadas_elegibles", "promedios_jornada",
    "valor_integrado_provisional", "desviacion_estandar_entre_jornadas",
    "minimo_entre_jornadas", "maximo_entre_jornadas", "diferencia_M2_M1",
    "diferencia_pct_M2_vs_M1", "estado_integracion", "uso_previsto",
    "regla_integracion", "observacion_metodologica",
]

MASS_TRANSFORMATION_FIELDS = [
    "tipo_fila", "jornada", "materia_seca_fresco", "materia_seca_precompostado",
    "cenizas_fresco", "cenizas_precompostado", "dry_matter_retention_ratio",
    "mass_ratio_precomp_over_fresh", "mass_loss_pct", "estado",
    "jornadas_elegibles", "numero_jornadas", "mass_ratio_integrado",
    "mass_loss_pct_integrado", "estado_integracion",
]


def _fmt(value: float | None) -> str:
    return "" if value is None else str(value)


def _read_source() -> list[dict]:
    with SOURCE.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    seen: set[tuple[str, str, str]] = set()
    for row in rows:
        key = (row["jornada"], row["material"], row["variable"])
        if key in seen:
            raise ValueError(f"Jornada duplicada para {key}")
        seen.add(key)
    return rows


def _build_row(rule: dict, source_rows: list[dict]) -> dict:
    matching = [r for r in source_rows if (r["material"], r["variable"]) == (rule["material"], rule["variable"])]
    available = {r["jornada"]: r for r in matching}
    journey_rules = {r["jornada"]: r for r in rule["jornadas"]}
    eligible = {
        jornada: row for jornada, row in available.items()
        if jornada in journey_rules
        and journey_rules[jornada]["elegibilidad_temporal"]
        and row["metodo"] == journey_rules[jornada]["metodo_requerido"]
    }
    ordered_available = sorted(available)
    ordered_eligible = sorted(eligible)
    values = {j: float(eligible[j]["promedio_jornada"]) for j in ordered_eligible}
    numeric = list(values.values())
    m1 = values.get("M1")
    m2 = values.get("M2")
    difference = m2 - m1 if m1 is not None and m2 is not None else None
    difference_pct = difference / m1 * 100 if difference is not None and m1 != 0 else None
    enough = len(values) >= rule["minimo_jornadas_necesarias"]
    eligible_journeys = set(values)
    if rule["tipo_regla"] == "solido_integrable" and enough:
        expected_final = {
            journey["jornada"] for journey in rule["jornadas"]
            if journey["elegibilidad_temporal"]
        }
        final_complete = (
            len(eligible_journeys) == rule["numero_jornadas_final_esperado"]
            and eligible_journeys == expected_final
        )
        if final_complete:
            state = "final"
        elif eligible_journeys == {"M1", "M2"}:
            state = "provisional_M1_M2"
        else:
            state = "provisional_incompleto"
        integrated = statistics.fmean(numeric)
    elif rule["tipo_regla"] == "liquido_n_provisional":
        expected_final = {
            journey["jornada"] for journey in rule["jornadas"]
            if journey["elegibilidad_temporal"]
        }
        final_complete = (
            len(eligible_journeys) == rule["numero_jornadas_final_esperado"]
            and eligible_journeys == expected_final
        )
        if final_complete:
            state, integrated = "final", statistics.fmean(numeric)
        elif eligible_journeys == {"M2"}:
            state, integrated = "provisional_M2_pendiente_M3", values["M2"]
        else:
            state, integrated = "provisional_incompleto", None
    elif rule["tipo_regla"] == "solo_caracterizacion":
        state, integrated = "solo_caracterizacion", statistics.fmean(numeric) if numeric else None
    else:
        state, integrated = "no_integrable", None
    methods = sorted({r["metodo"] for r in matching})
    notes = [rule["observacion_metodologica"]]
    excluded = [j for j in ordered_available if j in journey_rules and not journey_rules[j]["elegibilidad_temporal"]]
    if excluded:
        notes.append("Jornadas excluidas: " + ", ".join(f"{j} ({journey_rules[j]['motivo']})" for j in excluded))
    incompatible = [
        j for j in ordered_available
        if journey_rules[j]["elegibilidad_temporal"]
        and available[j]["metodo"] != journey_rules[j]["metodo_requerido"]
    ]
    if incompatible:
        notes.append(
            "Jornadas metodológicamente incompatibles: "
            + ", ".join(
                f"{j} (observado: {available[j]['metodo']}; requerido: {journey_rules[j]['metodo_requerido']})"
                for j in incompatible
            )
        )
    return {
        "material": rule["material"], "variable": rule["variable"],
        "unidad": next((r["unidad"] for r in matching), ""),
        "metodo_o_compatibilidad": "; ".join(methods),
        "jornadas_disponibles": ";".join(ordered_available),
        "jornadas_elegibles": ";".join(ordered_eligible),
        "numero_jornadas_elegibles": str(len(values)),
        "promedios_jornada": ";".join(f"{j}={_fmt(values[j])}" for j in ordered_eligible),
        "valor_integrado_provisional": _fmt(integrated),
        "desviacion_estandar_entre_jornadas": _fmt(statistics.stdev(numeric) if len(numeric) >= 2 else None),
        "minimo_entre_jornadas": _fmt(min(numeric) if numeric else None),
        "maximo_entre_jornadas": _fmt(max(numeric) if numeric else None),
        "diferencia_M2_M1": _fmt(difference),
        "diferencia_pct_M2_vs_M1": _fmt(difference_pct),
        "estado_integracion": state, "uso_previsto": rule["uso_previsto"],
        "regla_integracion": rule["politica_integracion"],
        "observacion_metodologica": " ".join(note for note in notes if note),
    }


def build_mass_transformation_rows(source_rows: list[dict]) -> list[dict]:
    """Calcula primero el factor de cada jornada y luego integra esos factores."""
    indexed = {
        (row["jornada"], row["material"], row["variable"]): row
        for row in source_rows
    }
    journey_rows: list[dict] = []
    for jornada in MASS_TRANSFORMATION_RULE["jornadas_esperadas"]:
        required = [
            indexed.get((jornada, material, variable))
            for material, variable in MASS_TRANSFORMATION_RULE["variables_requeridas"]
        ]
        if any(row is None for row in required):
            continue
        if any(row["metodo"] != MASS_TRANSFORMATION_RULE["metodo_requerido"] for row in required):
            continue
        values = {
            (row["material"], row["variable"]): float(row["promedio_jornada"])
            for row in required
        }
        dm_fresh = values[("estiércol fresco", "materia seca")]
        dm_precomp = values[("estiércol precompostado", "materia seca")]
        ash_fresh = values[("estiércol fresco", "cenizas")]
        ash_precomp = values[("estiércol precompostado", "cenizas")]
        if dm_precomp == 0 or ash_precomp == 0:
            raise ValueError(f"Denominador cero en la transformación de masa de {jornada}")
        retention = ash_fresh / ash_precomp
        mass_ratio = retention * (dm_fresh / dm_precomp)
        journey_rows.append({
            "tipo_fila": "jornada", "jornada": jornada,
            "materia_seca_fresco": _fmt(dm_fresh),
            "materia_seca_precompostado": _fmt(dm_precomp),
            "cenizas_fresco": _fmt(ash_fresh),
            "cenizas_precompostado": _fmt(ash_precomp),
            "dry_matter_retention_ratio": _fmt(retention),
            "mass_ratio_precomp_over_fresh": _fmt(mass_ratio),
            "mass_loss_pct": _fmt((1.0 - mass_ratio) * 100.0),
            "estado": "elegible", "jornadas_elegibles": "", "numero_jornadas": "",
            "mass_ratio_integrado": "", "mass_loss_pct_integrado": "",
            "estado_integracion": "",
        })
    eligible = {row["jornada"] for row in journey_rows}
    expected = set(MASS_TRANSFORMATION_RULE["jornadas_esperadas"])
    factors = [float(row["mass_ratio_precomp_over_fresh"]) for row in journey_rows]
    integrated = statistics.fmean(factors) if factors else None
    if eligible == expected and len(eligible) == MASS_TRANSFORMATION_RULE["numero_jornadas_final_esperado"]:
        state = "final"
    elif eligible == {"M1", "M2"}:
        state = "provisional_M1_M2"
    elif eligible:
        state = "provisional_incompleto"
    else:
        state = "no_integrable"
    summary = {
        "tipo_fila": "integracion", "jornada": "", "materia_seca_fresco": "",
        "materia_seca_precompostado": "", "cenizas_fresco": "",
        "cenizas_precompostado": "", "dry_matter_retention_ratio": "",
        "mass_ratio_precomp_over_fresh": "", "mass_loss_pct": "", "estado": "",
        "jornadas_elegibles": ";".join(sorted(eligible)),
        "numero_jornadas": str(len(eligible)), "mass_ratio_integrado": _fmt(integrated),
        "mass_loss_pct_integrado": _fmt((1.0 - integrated) * 100.0 if integrated is not None else None),
        "estado_integracion": state,
    }
    return journey_rows + [summary]


def _report(rows: list[dict]) -> str:
    provisional = [r for r in rows if r["estado_integracion"] == "provisional_M1_M2"]
    pending = [r for r in rows if r["estado_integracion"] == "provisional_M2_pendiente_M3"]
    characterization = [r for r in rows if r["estado_integracion"] == "solo_caracterizacion"]
    lines = [
        "# Auditoría de integración estadística provisional M1–M2", "",
        "## Alcance y reglas aplicadas", "",
        "La integración se construyó exclusivamente desde los promedios de jornada de `processed/muestreos_resumen_intrajornada.csv`. M1 y M2 reciben igual peso temporal; el número de muestras compuestas y de réplicas analíticas no modifica ese peso. La desviación estándar presentada es la desviación entre promedios de jornada y permanece separada de la variabilidad intrajornada.", "",
        "No se aplicaron pruebas inferenciales ni se conectaron los resultados al modelo ACV. Toda integración M1–M2 es provisional.", "",
        "## Variables comparables e integración provisional", "",
        "| Material | Variable | Unidad | M1 | M2 | Promedio provisional | DE entre jornadas | M2 − M1 | Diferencia M2 vs M1 (%) |", "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in provisional:
        values = dict(item.split("=", 1) for item in row["promedios_jornada"].split(";") if item)
        lines.append("| {material} | {variable} | {unidad} | {m1} | {m2} | {avg} | {sd} | {diff} | {pct} |".format(
            **row, m1=values.get("M1", "—"), m2=values.get("M2", "—"), avg=row["valor_integrado_provisional"],
            sd=row["desviacion_estandar_entre_jornadas"], diff=row["diferencia_M2_M1"], pct=row["diferencia_pct_M2_vs_M1"]))
    lines += ["", "La diferencia porcentual es descriptiva y no constituye evidencia de diferencia estadísticamente significativa.", "", "## Variables no comparables y pendientes de M3", ""]
    for row in pending:
        lines.append(f"- **{row['material']} — N total:** M1 corresponde a especiación y se excluye; M2 ({row['promedios_jornada']}) es el único estimador Kjeldahl elegible. Estado: `pendiente_M3`.")
    lines += ["", "Las fracciones de N amoniacal, nítrico y ureico de M1 permanecen en la fuente intrajornada únicamente como trazabilidad; no se suman ni se comparan con N total Kjeldahl.", "", "## Variables de solo caracterización", ""]
    for row in characterization:
        lines.append(f"- **{row['material']} — {row['variable']}:** {row['promedios_jornada'] or 'sin estimador elegible disponible'}; no es un parámetro actual del modelo ACV.")
    lines += ["", "## Observaciones metodológicas y anomalías", "",
        "- El N total precompostado se conserva exactamente en la base reportada por el CIA. No se convirtió con la materia seca gravimétrica del TFG.",
        "- Carbono y relación C/N precompostados se mantienen como caracterización descriptiva.",
        "- La relación C/N precompostada no está disponible como fila independiente en M1; por ello su resumen descriptivo actual contiene únicamente M2.",
        "- No se detectaron duplicados de jornada por material y variable en la fuente.",
        "- Con M3, las reglas incorporarán automáticamente M1+M2+M3 para sólidos y M2+M3 para N de líquidos, sujeto a compatibilidad metodológica.", ""]
    return "\n".join(lines)


def main() -> None:
    source_rows = _read_source()
    rows = [_build_row(rule, source_rows) for rule in INTEGRATION_RULES]
    source_has_m3 = any(row["jornada"] == "M3" for row in source_rows)
    if not source_has_m3 and any(row["estado_integracion"] == "final" for row in rows):
        raise ValueError("No se permite estado final mientras M3 no esté disponible")
    with OUTPUT.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    mass_rows = build_mass_transformation_rows(source_rows)
    with MASS_TRANSFORMATION_OUTPUT.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=MASS_TRANSFORMATION_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(mass_rows)
    REPORT.write_text(_report(rows), encoding="utf-8")
    print(f"Generadas {len(rows)} filas en {OUTPUT.relative_to(ROOT)}")
    print(f"Generadas {len(mass_rows)} filas en {MASS_TRANSFORMATION_OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
