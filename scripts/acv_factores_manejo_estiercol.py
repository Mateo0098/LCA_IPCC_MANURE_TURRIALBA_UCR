"""Carga factores IPCC de manejo de estiercol por sistema y etapa."""

from __future__ import annotations

import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
TABLA_FACTORES = BASE_DIR / "processed" / "ipcc_sistemas_manejo_estiercol_factores.csv"
TABLA_SELECCION = BASE_DIR / "processed" / "ipcc_sistema_manejo_por_etapa.csv"

_CACHE_FACTORES: dict[str, dict[str, float]] | None = None
_CACHE_SELECCION: dict[tuple[str, int], str] | None = None


def _parse_float(raw: object, campo: str, ruta: Path) -> float:
    if raw is None:
        raise ValueError(f"Campo '{campo}' vacio en {ruta}")
    txt = str(raw).strip()
    if txt == "":
        raise ValueError(f"Campo '{campo}' vacio en {ruta}")
    return float(txt)


def _cargar_factores() -> dict[str, dict[str, float]]:
    if not TABLA_FACTORES.exists():
        raise FileNotFoundError(f"No existe tabla de factores: {TABLA_FACTORES}")

    out: dict[str, dict[str, float]] = {}
    with TABLA_FACTORES.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            sistema = str(row.get("sistema_manejo", "")).strip().lower()
            if not sistema:
                continue
            if sistema in out:
                raise ValueError(f"Sistema duplicado '{sistema}' en {TABLA_FACTORES}")
            out[sistema] = {
                "MCF": _parse_float(row.get("mcf_pct"), "mcf_pct", TABLA_FACTORES),
                "EF3": _parse_float(row.get("ef3"), "ef3", TABLA_FACTORES),
                "frac_gas_ms": _parse_float(
                    row.get("frac_gas_ms"), "frac_gas_ms", TABLA_FACTORES
                ),
                "frac_leach_ms": _parse_float(
                    row.get("frac_leach_ms"), "frac_leach_ms", TABLA_FACTORES
                ),
            }
    if not out:
        raise ValueError(f"Tabla de factores sin datos: {TABLA_FACTORES}")
    return out


def _cargar_seleccion() -> dict[tuple[str, int], str]:
    if not TABLA_SELECCION.exists():
        raise FileNotFoundError(f"No existe tabla de seleccion: {TABLA_SELECCION}")

    out: dict[tuple[str, int], str] = {}
    with TABLA_SELECCION.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            escenario = str(row.get("escenario", "")).strip().upper()
            etapa_raw = row.get("etapa")
            sistema = str(row.get("sistema_manejo", "")).strip().lower()
            if not escenario or etapa_raw in (None, "") or not sistema:
                continue
            etapa = int(str(etapa_raw).strip())
            key = (escenario, etapa)
            if key in out:
                raise ValueError(
                    f"Seleccion duplicada para escenario={escenario}, etapa={etapa} en {TABLA_SELECCION}"
                )
            out[key] = sistema
    if not out:
        raise ValueError(f"Tabla de seleccion sin datos: {TABLA_SELECCION}")
    return out


def obtener_factores_manejo_ipcc(escenario: str, etapa: int) -> dict[str, float | str]:
    """Retorna factores (MCF, EF3, frac_gas_ms, frac_leach_ms) por etapa IPCC."""
    global _CACHE_FACTORES, _CACHE_SELECCION
    if _CACHE_FACTORES is None:
        _CACHE_FACTORES = _cargar_factores()
    if _CACHE_SELECCION is None:
        _CACHE_SELECCION = _cargar_seleccion()

    key = (str(escenario).strip().upper(), int(etapa))
    sistema = _CACHE_SELECCION.get(key)
    if sistema is None:
        raise KeyError(
            f"No existe sistema_manejo para escenario={key[0]}, etapa={key[1]} en {TABLA_SELECCION}"
        )

    factores = _CACHE_FACTORES.get(sistema)
    if factores is None:
        raise KeyError(
            f"No existe sistema_manejo='{sistema}' en {TABLA_FACTORES} "
            f"(referenciado por escenario={key[0]}, etapa={key[1]})."
        )

    return {
        "sistema_manejo": sistema,
        "MCF": float(factores["MCF"]),
        "EF3": float(factores["EF3"]),
        "frac_gas_ms": float(factores["frac_gas_ms"]),
        "frac_leach_ms": float(factores["frac_leach_ms"]),
    }


def main() -> None:
    etapas_objetivo = [("A", 1), ("A", 2), ("A", 3), ("B", 1)]
    for escenario, etapa in etapas_objetivo:
        factores = obtener_factores_manejo_ipcc(escenario, etapa)
        sistema = str(factores["sistema_manejo"])
        print(f"{escenario}{etapa}: {sistema}")


if __name__ == "__main__":
    main()
