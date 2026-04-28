"""Utilidades para exportar resultados ACV a una tabla CSV comun."""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any

COLUMNAS = [
    "Escenario",
    "Etapa",
    "masa_total_kg_eq",
    "CO2_medido",
    "CH4_ec1",
    "N2O_ec14",
    "N2O_ec2",
    "N2O_ec5",
    "N2O_ec6",
    "N2O_ec16",
    "N2O_ec18",
    "NH3_ec12",
    "NH3_ec20",
    "NO3_ec13",
    "NO3_ec21",
]


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    raw = str(value).strip()
    if raw == "":
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _cargar_masas_por_etapa(base: Path) -> dict[tuple[str, int], float]:
    ruta = base / "processed" / "masa_total_escenario_etapa.csv"
    if not ruta.exists():
        return {}

    masas: dict[tuple[str, int], float] = {}
    with ruta.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            escenario = str(row.get("escenario", "")).strip().upper()
            etapa_raw = row.get("etapa")
            masa_raw = row.get("masa_total_kg_eq")
            if not escenario or etapa_raw in (None, "") or masa_raw in (None, ""):
                continue
            try:
                etapa = int(str(etapa_raw).strip())
                masa = float(str(masa_raw).strip())
            except ValueError:
                continue
            masas[(escenario, etapa)] = masa
    return masas


def _escalar_fila_por_masa(
    fila: dict[str, Any], escenario: str, etapa: int, masas: dict[tuple[str, int], float]
) -> dict[str, Any]:
    key = (str(escenario).strip().upper(), int(etapa))
    masa = masas.get(key)
    fila_escalada = dict(fila)
    fila_escalada["masa_total_kg_eq"] = masa if masa is not None else ""
    if masa is None:
        return fila_escalada

    for col in COLUMNAS:
        if col in ("Escenario", "Etapa", "masa_total_kg_eq"):
            continue
        value = _to_float(fila_escalada.get(col))
        if value is None:
            continue
        if math.isnan(value):
            continue
        fila_escalada[col] = value * masa
    return fila_escalada


def _normalizar_fila(fila: dict[str, Any], escenario: str, etapa: int) -> dict[str, Any]:
    fila_out = {col: fila.get(col, "") for col in COLUMNAS}
    fila_out["Escenario"] = str(escenario)
    fila_out["Etapa"] = int(etapa)
    return fila_out


def _clave_orden(fila: dict[str, Any]) -> tuple[int, int]:
    escenario = str(fila.get("Escenario", ""))
    etapa = int(fila.get("Etapa", 0))
    if escenario == "A":
        i = 0
    elif escenario == "B":
        i = 1
    else:
        i = 99
    return i, etapa


def exportar_fila(escenario: str, etapa: int, fila: dict[str, Any]) -> None:
    """
    Inserta o actualiza una fila por (Escenario, Etapa) en la tabla resumen.
    """
    base = Path(__file__).resolve().parent.parent
    ruta_csv = base / "processed" / "ACV_resumen_emisiones.csv"
    ruta_csv.parent.mkdir(parents=True, exist_ok=True)
    masas_por_etapa = _cargar_masas_por_etapa(base)

    fila_escalada = _escalar_fila_por_masa(fila, escenario, etapa, masas_por_etapa)
    nueva_fila = _normalizar_fila(fila_escalada, escenario, etapa)
    filas: list[dict[str, Any]] = []

    if ruta_csv.exists():
        with ruta_csv.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if not row:
                    continue
                filas.append(_normalizar_fila(row, row.get("Escenario", ""), int(row.get("Etapa", 0))))

    reemplazada = False
    for i, row in enumerate(filas):
        if str(row["Escenario"]) == str(escenario) and int(row["Etapa"]) == int(etapa):
            filas[i] = nueva_fila
            reemplazada = True
            break

    if not reemplazada:
        filas.append(nueva_fila)

    filas.sort(key=_clave_orden)

    try:
        with ruta_csv.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNAS)
            writer.writeheader()
            writer.writerows(filas)
    except PermissionError:
        ruta_fallback = ruta_csv.with_name(f"{ruta_csv.stem}_updated{ruta_csv.suffix}")
        with ruta_fallback.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNAS)
            writer.writeheader()
            writer.writerows(filas)

