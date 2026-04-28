from __future__ import annotations

import csv
from pathlib import Path


def obtener_modelo_etapa(escenario: str, etapa: int, default: str = "ipcc") -> str:
    base = Path(__file__).resolve().parent.parent
    ruta = base / "processed" / "modelo_etapa_overrides.csv"
    if not ruta.exists():
        return default

    objetivo_escenario = str(escenario).strip().upper()
    objetivo_etapa = int(etapa)
    with ruta.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            esc = str(row.get("escenario", "")).strip().upper()
            etapa_raw = row.get("etapa")
            modelo = str(row.get("modelo", "")).strip().lower()
            if not esc or etapa_raw in (None, ""):
                continue
            try:
                et = int(str(etapa_raw).strip())
            except ValueError:
                continue
            if esc == objetivo_escenario and et == objetivo_etapa:
                if modelo in {"ipcc", "medido"}:
                    return modelo
                raise ValueError(
                    f"Modelo invalido '{modelo}' para escenario={esc}, etapa={et}. "
                    "Modelos permitidos: ipcc, medido."
                )

    return default
