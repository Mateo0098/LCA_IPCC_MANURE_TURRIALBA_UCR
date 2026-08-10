#!/usr/bin/env python3
"""Construye las capas de observaciones y resúmenes M1/M2 sin tocar el ACV."""

from __future__ import annotations

import csv
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from compute_sample_parameters import extract_gravimetric_normalized
from extract_analysis_results import (
    NORMALIZED_COMMON_FIELDS,
    extract_cia_normalized,
    extract_lasa_normalized,
)
from sampling_ingestion_config import PROJECT_ROOT, configured_sources


OBSERVATIONS_PATH = PROJECT_ROOT / "processed" / "muestreos_observaciones_normalizadas.csv"
SUMMARY_PATH = PROJECT_ROOT / "processed" / "muestreos_resumen_intrajornada.csv"

SUMMARY_FIELDS = [
    "jornada", "material", "variable", "numero_muestras_compuestas",
    "numero_replicas_analiticas", "numero_datos_validos", "promedio_jornada",
    "desviacion_estandar_entre_muestras", "desviacion_analitica_intramuestra_media",
    "minimo_entre_muestras", "maximo_entre_muestras", "unidad", "metodo",
    "uso_modelo", "bandera_calidad",
]


def ingest_all() -> List[Dict[str, object]]:
    observations: List[Dict[str, object]] = []
    extractors = {
        "cia_xlsx": extract_cia_normalized,
        "lasa_pdf": extract_lasa_normalized,
        "gravimetric_xlsx": extract_gravimetric_normalized,
    }
    for source in configured_sources():
        path = Path(source["absolute_path"])
        if not path.exists():
            raise FileNotFoundError(path)
        observations.extend(extractors[str(source["kind"])](source, PROJECT_ROOT))
    return observations


def _float(value: object) -> float:
    return float(str(value).replace(",", "."))


def summarize_intrajornada(observations: Iterable[Dict[str, object]]) -> List[Dict[str, object]]:
    groups: Dict[Tuple[str, ...], List[Dict[str, object]]] = defaultdict(list)
    for row in observations:
        key = (
            str(row["jornada_muestreo"]), str(row["tipo_material"]), str(row["variable"]),
            str(row["unidad"]), str(row["metodo_analitico"]), str(row["uso_modelo"]),
        )
        groups[key].append(row)

    summaries: List[Dict[str, object]] = []
    for key, rows in sorted(groups.items()):
        jornada, material, variable, unidad, metodo, uso = key
        by_sample: Dict[str, List[float]] = defaultdict(list)
        analytical_count = 0
        for row in rows:
            by_sample[str(row["identificador_muestra"])].append(_float(row["valor"]))
            if str(row.get("replica_analitica", "")).strip():
                analytical_count += 1

        sample_means = [statistics.mean(values) for values in by_sample.values()]
        within_sds = [statistics.stdev(values) for values in by_sample.values() if len(values) > 1]
        summaries.append({
            "jornada": jornada,
            "material": material,
            "variable": variable,
            "numero_muestras_compuestas": len(by_sample),
            "numero_replicas_analiticas": analytical_count,
            "numero_datos_validos": len(rows),
            "promedio_jornada": statistics.mean(sample_means),
            "desviacion_estandar_entre_muestras": statistics.stdev(sample_means) if len(sample_means) > 1 else 0.0,
            "desviacion_analitica_intramuestra_media": statistics.mean(within_sds) if within_sds else "",
            "minimo_entre_muestras": min(sample_means),
            "maximo_entre_muestras": max(sample_means),
            "unidad": unidad,
            "metodo": metodo,
            "uso_modelo": uso,
            "bandera_calidad": "",
        })
    return summaries


def _write_csv(path: Path, fields: List[str], rows: Iterable[Dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            formatted = {
                key: f"{value:.10g}" if isinstance(value, float) else value
                for key, value in row.items()
            }
            writer.writerow(formatted)


def main() -> int:
    observations = ingest_all()
    summaries = summarize_intrajornada(observations)
    _write_csv(OBSERVATIONS_PATH, NORMALIZED_COMMON_FIELDS, observations)
    _write_csv(SUMMARY_PATH, SUMMARY_FIELDS, summaries)
    print(f"Observaciones: {len(observations)}")
    print(f"Resúmenes intrajornada: {len(summaries)}")
    print(OBSERVATIONS_PATH)
    print(SUMMARY_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
