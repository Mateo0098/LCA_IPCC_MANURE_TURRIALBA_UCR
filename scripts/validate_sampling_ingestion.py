#!/usr/bin/env python3
"""Validación estructural y metodológica de la ingestión M1/M2."""

from __future__ import annotations

import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

from sampling_ingestion_config import PROJECT_ROOT, configured_sources


OBSERVATIONS = PROJECT_ROOT / "processed" / "muestreos_observaciones_normalizadas.csv"
SUMMARY = PROJECT_ROOT / "processed" / "muestreos_resumen_intrajornada.csv"


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []
    with OBSERVATIONS.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    with SUMMARY.open(encoding="utf-8", newline="") as handle:
        summaries = list(csv.DictReader(handle))

    required = {
        "jornada_muestreo", "tipo_material", "identificador_muestra",
        "identificador_muestra_origen", "repeticion_muestra", "replica_analitica", "nivel_observacion",
        "variable", "valor", "unidad", "base_medicion", "laboratorio",
        "metodo_analitico", "archivo_origen", "hoja_origen", "uso_modelo",
        "motivo_uso_modelo", "bandera_calidad",
    }
    missing_columns = required - set(rows[0] if rows else {})
    if missing_columns:
        fail(errors, f"Columnas obligatorias ausentes: {sorted(missing_columns)}")

    duplicate_key = lambda row: (
        row["jornada_muestreo"], row["tipo_material"], row["identificador_muestra"],
        row["replica_analitica"], row["variable"], row["archivo_origen"],
    )
    counts = Counter(duplicate_key(row) for row in rows)
    duplicates = [key for key, count in counts.items() if count > 1]
    if duplicates:
        fail(errors, f"Claves de observación duplicadas: {duplicates[:5]}")

    for row in rows:
        for field in required - {"bandera_calidad"}:
            if field not in {"replica_analitica"} and not str(row.get(field, "")).strip():
                fail(errors, f"Valor obligatorio vacío: {field} en {duplicate_key(row)}")
        try:
            float(row["valor"])
        except ValueError:
            fail(errors, f"Valor no numérico o fórmula consumida: {row['valor']!r} en {duplicate_key(row)}")
        if str(row["valor"]).lstrip().startswith("="):
            fail(errors, f"Se consumió una fórmula de Excel: {duplicate_key(row)}")
        if not str(row["identificador_muestra"]).startswith(f'{row["jornada_muestreo"]}-'):
            fail(errors, f"Posible mezcla de jornadas: {duplicate_key(row)}")

    rows_by_file = defaultdict(list)
    for row in rows:
        rows_by_file[row["archivo_origen"]].append(row)
    for source in configured_sources():
        source_rows = rows_by_file[str(source["path"]).replace("\\", "/")]
        if not source_rows:
            fail(errors, f"Fuente sin observaciones: {source['path']}")
            continue
        samples = {row["identificador_muestra"] for row in source_rows}
        expected_samples = int(source.get("expected_samples", source.get("expected_samples_by_material", 0)))
        if source["kind"] == "gravimetric_xlsx":
            for material in {"estiércol fresco", "estiércol precompostado"}:
                material_rows = [row for row in source_rows if row["tipo_material"] == material]
                material_samples = {row["identificador_muestra"] for row in material_rows}
                if len(material_samples) != expected_samples:
                    fail(errors, f"{source['jornada']} {material}: {len(material_samples)} muestras; esperadas {expected_samples}")
                for sample in material_samples:
                    for variable in {"humedad", "materia seca", "cenizas", "sólidos volátiles"}:
                        reps = {row["replica_analitica"] for row in material_rows if row["identificador_muestra"] == sample and row["variable"] == variable}
                        if reps != {"1", "2", "3"}:
                            fail(errors, f"Réplicas gravimétricas incorrectas: {source['jornada']} {sample} {variable}: {sorted(reps)}")
        else:
            if len(samples) != expected_samples:
                fail(errors, f"{source['path']}: {len(samples)} muestras; esperadas {expected_samples}")
            if source["kind"] == "lasa_pdf":
                for sample in samples:
                    reps = {row["replica_analitica"] for row in source_rows if row["identificador_muestra"] == sample}
                    if reps != {"1", "2", "3"}:
                        fail(errors, f"Réplicas LASA incorrectas: {source['jornada']} {sample}: {sorted(reps)}")

    for material in ("aguas verdes", "purines"):
        m1_n = [row for row in rows if row["jornada_muestreo"] == "M1" and row["tipo_material"] == material and row["variable"].startswith("N ")]
        m2_n = [row for row in rows if row["jornada_muestreo"] == "M2" and row["tipo_material"] == material and row["variable"] == "N total"]
        if not m1_n or any(row["uso_modelo"] != "solo_trazabilidad" or row["metodo_analitico"] != "especiación" for row in m1_n):
            fail(errors, f"Decisión metodológica incorrecta para N M1 de {material}")
        if not m2_n or any(row["uso_modelo"] != "elegible" or row["metodo_analitico"] != "Kjeldahl" for row in m2_n):
            fail(errors, f"Decisión metodológica incorrecta para N M2 de {material}")
        if any(row["variable"] == "N total" for row in m1_n):
            fail(errors, f"Se generó artificialmente N total M1 para {material}")

    precomp_nc = [
        row for row in rows
        if row["tipo_material"] == "estiércol precompostado"
        and row["variable"] in {"N total", "carbono"}
    ]
    if not precomp_nc or any(row["metodo_analitico"] != "Dumas (combustión seca)" for row in precomp_nc):
        fail(errors, "N/C de precompostado M1/M2 no quedó documentado mediante Dumas")
    if any(row["base_medicion"] != "no especificada en el reporte" for row in precomp_nc):
        fail(errors, "N/C de precompostado afirma una base de medición no respaldada")
    precomp_n = [row for row in precomp_nc if row["variable"] == "N total"]
    if any(row["uso_modelo"] != "elegible" for row in precomp_n):
        fail(errors, "El N de precompostado dejó de estar marcado como elegible")
    characterization = [
        row for row in rows if row["variable"] in {"densidad", "carbono", "relación C/N"}
    ]
    if any(row["uso_modelo"] != "solo_caracterizacion" for row in characterization):
        fail(errors, "Densidad, carbono o relación C/N heredó elegibilidad de la fuente")

    unit_groups = defaultdict(set)
    for row in rows:
        unit_groups[(row["jornada_muestreo"], row["tipo_material"], row["variable"], row["metodo_analitico"])].add(row["unidad"])
    incompatible = {key: units for key, units in unit_groups.items() if len(units) > 1}
    if incompatible:
        fail(errors, f"Unidades incompatibles dentro de un grupo: {incompatible}")

    summary_keys = [(r["jornada"], r["material"], r["variable"], r["metodo"]) for r in summaries]
    if len(summary_keys) != len(set(summary_keys)):
        fail(errors, "Hay claves duplicadas en el resumen intrajornada")

    if errors:
        print("VALIDACIÓN FALLIDA")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"VALIDACIÓN CORRECTA: {len(rows)} observaciones y {len(summaries)} resúmenes intrajornada")
    print("M1: 2 muestras compuestas por material; M2: 3 muestras compuestas por material")
    print("Sólidos y LASA: 3 réplicas analíticas por muestra")
    print("Líquidos M1: especiación/solo_trazabilidad; líquidos M2: Kjeldahl/elegible")
    print("Precompostado M1/M2: N/C por Dumas; base del porcentaje no especificada en el reporte")
    print("Densidad, carbono y relación C/N: solo_caracterizacion")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
