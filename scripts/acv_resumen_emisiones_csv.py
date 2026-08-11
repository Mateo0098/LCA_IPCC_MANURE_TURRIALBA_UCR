"""Utilidades para exportar resultados ACV a una tabla CSV comun."""

from __future__ import annotations

import argparse
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

ETAPAS_ESPERADAS = {("A", 1), ("A", 2), ("A", 3), ("A", 4), ("B", 1), ("B", 2)}


def _ruta_resumen() -> Path:
    return Path(__file__).resolve().parent.parent / "processed" / "ACV_resumen_emisiones.csv"


def inicializar_resumen() -> Path:
    """Inicia la salida canónica vacía para impedir mezclas entre corridas."""
    ruta = _ruta_resumen()
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNAS)
        writer.writeheader()
    return ruta


def validar_resumen_completo() -> Path:
    """Exige exactamente una fila por cada una de las seis etapas del ACV."""
    ruta = _ruta_resumen()
    if not ruta.exists():
        raise FileNotFoundError(f"No existe el resumen canónico de emisiones: {ruta}")
    with ruta.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    keys = [(str(row.get("Escenario", "")).strip().upper(), int(row["Etapa"])) for row in rows]
    if len(keys) != len(set(keys)):
        raise ValueError(f"Hay etapas duplicadas en {ruta}: {keys}")
    if len(keys) != len(ETAPAS_ESPERADAS) or set(keys) != ETAPAS_ESPERADAS:
        missing = sorted(ETAPAS_ESPERADAS - set(keys))
        unexpected = sorted(set(keys) - ETAPAS_ESPERADAS)
        raise ValueError(
            f"Resumen de emisiones incompleto: filas={len(keys)}, faltantes={missing}, "
            f"inesperadas={unexpected}"
        )
    return ruta


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
        raise FileNotFoundError(f"No existe la tabla canónica de masas por etapa: {ruta}")

    masas: dict[tuple[str, int], float] = {}
    with ruta.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            escenario = str(row.get("escenario", "")).strip().upper()
            etapa_raw = row.get("etapa")
            masa_raw = row.get("masa_total_kg_eq")
            if not escenario or etapa_raw in (None, "") or masa_raw in (None, ""):
                raise ValueError(f"Fila de masa incompleta en {ruta}: {row}")
            try:
                etapa = int(str(etapa_raw).strip())
                masa = float(str(masa_raw).strip())
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Masa o etapa no numérica en {ruta}: {row}") from exc
            if not math.isfinite(masa) or masa <= 0:
                raise ValueError(
                    f"La masa debe ser finita y positiva para escenario={escenario}, etapa={etapa}: {masa}"
                )
            key = (escenario, etapa)
            if key in masas:
                raise ValueError(f"Masa duplicada para escenario={escenario}, etapa={etapa} en {ruta}")
            masas[key] = masa
    if not masas:
        raise ValueError(f"La tabla canónica de masas no contiene filas: {ruta}")
    return masas


def _escalar_fila_por_masa(
    fila: dict[str, Any], escenario: str, etapa: int, masas: dict[tuple[str, int], float]
) -> dict[str, Any]:
    key = (str(escenario).strip().upper(), int(etapa))
    if key not in masas:
        raise KeyError(f"Falta masa válida para escenario={key[0]}, etapa={key[1]}")
    masa = float(masas[key])
    if not math.isfinite(masa) or masa <= 0:
        raise ValueError(
            f"La masa debe ser finita y positiva para escenario={key[0]}, etapa={key[1]}: {masa}"
        )
    fila_escalada = dict(fila)
    fila_escalada["masa_total_kg_eq"] = masa

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
    ruta_csv = _ruta_resumen()
    if not ruta_csv.exists():
        raise RuntimeError(
            "El resumen de emisiones no fue inicializado para la corrida vigente. "
            "Ejecute acv_resumen_emisiones_csv.py --initialize antes de las etapas."
        )
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

    with ruta_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNAS)
        writer.writeheader()
        writer.writerows(filas)


def main() -> None:
    parser = argparse.ArgumentParser(description="Inicializa o valida el resumen canónico de emisiones.")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--initialize", action="store_true")
    action.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if args.initialize:
        path = inicializar_resumen()
        print(f"Resumen inicializado: {path}")
    else:
        path = validar_resumen_completo()
        print(f"Resumen validado: seis etapas completas en {path}")


if __name__ == "__main__":
    main()

