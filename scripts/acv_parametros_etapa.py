"""
Carga parametros representativos (N_ex y VS_T) por escenario/etapa.
"""
from __future__ import annotations

import csv
from pathlib import Path


TABLA_PARAMETROS = (
    Path(__file__).resolve().parent.parent
    / "processed"
    / "acv_parametros_escenario_etapa.csv"
)

_CACHE = None


def _to_float(value: str):
    if value is None:
        return None
    raw = str(value).strip()
    if raw == "":
        return None
    return float(raw)


def _cargar_tabla():
    tabla = {}
    with TABLA_PARAMETROS.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            escenario = str(row["escenario"]).strip().upper()
            etapa = int(row["etapa"])
            tabla[(escenario, etapa)] = {
                "escenario": escenario,
                "etapa": etapa,
                "tratamiento": str(row["tratamiento"]).strip(),
                "n_ex_pct": _to_float(row.get("n_ex_pct")),
                "vs_t_pct": _to_float(row.get("vs_t_pct")),
                "fecha_n_ex": str(row.get("fecha_n_ex", "")).strip(),
                "fecha_vs_t": str(row.get("fecha_vs_t", "")).strip(),
                "unidad_n_ex": str(row.get("unidad_n_ex", "")).strip(),
                "unidad_vs_t": str(row.get("unidad_vs_t", "")).strip(),
            }
    return tabla


def obtener_parametros_etapa(escenario: str, etapa: int):
    global _CACHE
    if _CACHE is None:
        _CACHE = _cargar_tabla()

    key = (str(escenario).strip().upper(), int(etapa))
    if key not in _CACHE:
        raise KeyError(
            f"No existe configuracion para escenario={key[0]} etapa={key[1]} en {TABLA_PARAMETROS}"
        )

    return _CACHE[key]
