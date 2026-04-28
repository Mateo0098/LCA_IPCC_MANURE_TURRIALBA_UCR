"""Utilidades para convertir parametros en base seca a base humeda por etapa."""

from __future__ import annotations

import csv
from pathlib import Path

from acv_parametros_etapa import obtener_parametros_etapa


def _ruta_tabla_tratamientos() -> Path:
    return Path(__file__).resolve().parent.parent / "processed" / "volatile_solids_treatment_table.csv"


def _inferir_tratamiento_desde_texto(texto: str) -> str | None:
    norm = str(texto).strip().lower()
    if "precompost" in norm:
        return "B"
    if "fresco" in norm:
        return "A"
    return None


def obtener_fraccion_masa_seca_etapa(escenario: str, etapa: int) -> float:
    """Devuelve fraccion de masa seca (0-1) para la etapa, usando tabla de tratamientos."""
    params = obtener_parametros_etapa(escenario, etapa)
    tratamiento = _inferir_tratamiento_desde_texto(params.get("tratamiento", ""))

    ruta = _ruta_tabla_tratamientos()
    with ruta.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        filas = list(reader)

    if not filas:
        raise ValueError(f"Sin filas en {ruta}")

    fila_obj = None
    if tratamiento is not None:
        for fila in filas:
            val = str(fila.get("treatment", "")).strip().upper()
            if val == tratamiento:
                fila_obj = fila
                break

    if fila_obj is None:
        raise ValueError(
            f"No se pudo mapear tratamiento para escenario={escenario}, etapa={etapa} en {ruta}"
        )

    raw = fila_obj.get("dry_matter_treatment_mean_pct")
    if raw in (None, ""):
        raise ValueError(f"dry_matter_treatment_mean_pct vacio para tratamiento={tratamiento} en {ruta}")
    dry_matter_pct = float(str(raw).strip())
    if dry_matter_pct <= 0:
        raise ValueError(
            f"dry_matter_treatment_mean_pct debe ser > 0 para tratamiento={tratamiento} en {ruta}"
        )
    return dry_matter_pct / 100.0


def convertir_vs_base_humeda(vs_pct_base_seca: float, fraccion_masa_seca: float) -> float:
    """Convierte %SV en base seca a fraccion SV en base humeda."""
    return (float(vs_pct_base_seca) / 100.0) * float(fraccion_masa_seca)
