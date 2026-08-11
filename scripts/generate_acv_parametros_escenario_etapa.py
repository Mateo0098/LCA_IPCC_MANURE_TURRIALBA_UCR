"""Genera los parámetros experimentales activos del ACV desde la integración vigente."""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Dict, List

from sampling_integration_rules import FUTURE_JOURNEY, RULES_BY_KEY


STAGE_MATERIALS = [
    ("A", 1, "ESTIERCOL FRESCO", "estiércol fresco"),
    ("A", 2, "SOL: PRECOMPOSTADO", "estiércol precompostado"),
    ("A", 3, "ESTIERCOL FRESCO", "estiércol fresco"),
    ("A", 4, "LIQ: AGUA VERDE", "aguas verdes"),
    ("B", 1, "ESTIERCOL FRESCO", "estiércol fresco"),
    ("B", 2, "LIQ: PURINES", "purines"),
]

REQUIRED_VARIABLES = {
    "estiércol fresco": ("N total", "sólidos volátiles", "materia seca"),
    "estiércol precompostado": ("N total", "sólidos volátiles", "materia seca"),
    "aguas verdes": ("N total",),
    "purines": ("N total",),
}

def load_integration(path: Path) -> Dict[tuple[str, str], Dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"No existe la integración experimental vigente: {path}")
    indexed: Dict[tuple[str, str], Dict[str, str]] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            key = (str(row.get("material", "")).strip(), str(row.get("variable", "")).strip())
            if not all(key):
                continue
            if key in indexed:
                raise ValueError(f"Parámetro integrado duplicado: {key}")
            indexed[key] = row
    return indexed


def validate_integration_metadata(row: Dict[str, str], material: str, variable: str) -> None:
    """Valida una integración provisional o final contra la regla metodológica."""
    key = (material, variable)
    rule = RULES_BY_KEY.get(key)
    if rule is None:
        raise KeyError(f"No existe regla metodológica para {key}")

    configured = [
        journey["jornada"]
        for journey in rule["jornadas"]
        if journey["elegibilidad_temporal"]
    ]
    provisional = [journey for journey in configured if journey != FUTURE_JOURNEY]
    observed = [item for item in str(row.get("jornadas_elegibles", "")).split(";") if item]
    if observed not in (provisional, configured):
        raise ValueError(
            f"Jornadas elegibles incoherentes para {key}: {observed}; "
            f"se esperaba {provisional} (provisional) o {configured} (final)"
        )
    if len(observed) != int(str(row.get("numero_jornadas_elegibles", "")).strip()):
        raise ValueError(f"Número de jornadas incoherente para {key}: {observed}")

    state = str(row.get("estado_integracion", "")).strip()
    if observed == configured:
        if state != "final":
            raise ValueError(f"La integración completa de {key} debe tener estado final, no {state}")
    elif not state.startswith("provisional_"):
        raise ValueError(f"La integración incompleta válida de {key} debe ser provisional, no {state}")


def require_value(indexed: Dict[tuple[str, str], Dict[str, str]], material: str, variable: str) -> Dict[str, str]:
    key = (material, variable)
    if key not in indexed:
        raise KeyError(f"Falta el parámetro integrado obligatorio: material={material}, variable={variable}")
    row = indexed[key]
    validate_integration_metadata(row, material, variable)
    raw = str(row.get("valor_integrado_provisional", "")).strip()
    if raw == "":
        raise ValueError(f"Valor integrado vacío para {key}")
    value = float(raw)
    if not math.isfinite(value):
        raise ValueError(f"Valor integrado no finito para {key}: {raw}")
    return row


def build_rows(indexed: Dict[tuple[str, str], Dict[str, str]], source_name: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for escenario, etapa, tratamiento, material in STAGE_MATERIALS:
        selected = {
            variable: require_value(indexed, material, variable)
            for variable in REQUIRED_VARIABLES[material]
        }
        n_row = selected["N total"]
        vs_row = selected.get("sólidos volátiles")
        dm_row = selected.get("materia seca")
        rows.append({
            "escenario": escenario,
            "etapa": str(etapa),
            "tratamiento": tratamiento,
            "material_integrado": material,
            "n_ex_pct": n_row["valor_integrado_provisional"],
            "vs_t_pct": "" if vs_row is None else vs_row["valor_integrado_provisional"],
            "materia_seca_pct": "" if dm_row is None else dm_row["valor_integrado_provisional"],
            "unidad_n_ex": "% N total",
            "unidad_vs_t": "" if vs_row is None else "% Sólidos volátiles",
            "unidad_materia_seca": "" if dm_row is None else "% Materia seca",
            "jornadas_n_ex": n_row["jornadas_elegibles"],
            "jornadas_vs_t": "" if vs_row is None else vs_row["jornadas_elegibles"],
            "jornadas_materia_seca": "" if dm_row is None else dm_row["jornadas_elegibles"],
            "estado_integracion_n_ex": n_row["estado_integracion"],
            "estado_integracion_vs_t": "" if vs_row is None else vs_row["estado_integracion"],
            "estado_integracion_materia_seca": "" if dm_row is None else dm_row["estado_integracion"],
            "fuente_integracion": source_name,
        })
    return rows


def write_rows(rows: List[Dict[str, str]], output_path: Path) -> None:
    if not rows:
        raise ValueError("No se generaron parámetros activos del ACV")
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    source = root / "processed" / "muestreos_integracion_interjornada_provisional.csv"
    output = root / "processed" / "acv_parametros_escenario_etapa.csv"
    rows = build_rows(load_integration(source), source.name)
    write_rows(rows, output)
    print(f"Tabla generada: {output}")
    print(f"Filas exportadas: {len(rows)}")
    print(f"Fuente experimental única: {source}")


if __name__ == "__main__":
    main()
