from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List


def load_agua_boniga_flujo_anual(csv_path: Path) -> Dict[str, float]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        values: Dict[str, float] = {}
        for row in reader:
            variable = str(row.get("variable", "")).strip().lower()
            flujo_anual = row.get("flujo_por_ano")
            if variable and flujo_anual not in (None, ""):
                values[variable] = float(flujo_anual)
    faltantes = {"agua", "boniga"} - set(values.keys())
    if faltantes:
        raise ValueError(
            f"Faltan valores de flujo_por_ano para: {sorted(faltantes)} en {csv_path}"
        )
    return values


def load_mass_ratio(csv_path: Path) -> float:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
    if not rows:
        raise ValueError(f"Sin filas en {csv_path}")
    raw = rows[0].get("mass_ratio_to_over_from")
    if raw in (None, ""):
        raise ValueError(f"Columna mass_ratio_to_over_from vacia en {csv_path}")
    return float(raw)


def _parse_optional_float(raw: object) -> float | None:
    if raw is None:
        return None
    text = str(raw).strip()
    if text == "":
        return None
    return float(text)


def load_factor_overrides(
    csv_path: Path, required_keys: List[tuple[str, int]]
) -> Dict[tuple[str, int], Dict[str, float]]:
    if not csv_path.exists():
        raise FileNotFoundError(f"No existe archivo de overrides requerido: {csv_path}")

    overrides: Dict[tuple[str, int], Dict[str, float]] = {}
    with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            escenario = str(row.get("escenario", "")).strip().upper()
            etapa_raw = row.get("etapa")
            if not escenario or etapa_raw in (None, ""):
                continue
            etapa = int(str(etapa_raw).strip())
            key = (escenario, etapa)
            if key in overrides:
                raise ValueError(f"Override duplicado para escenario={escenario}, etapa={etapa}")

            factor_boniga = _parse_optional_float(row.get("factor_boniga"))
            factor_agua = _parse_optional_float(row.get("factor_agua"))
            factor_masa_total = _parse_optional_float(row.get("factor_masa_total"))

            out = {
                "factor_boniga": 1.0 if factor_boniga is None else float(factor_boniga),
                "factor_agua": 1.0 if factor_agua is None else float(factor_agua),
                "factor_masa_total": 1.0 if factor_masa_total is None else float(factor_masa_total),
            }
            for name, val in out.items():
                if val < 0:
                    raise ValueError(
                        f"{name} debe ser >= 0 para escenario={escenario}, etapa={etapa}. Valor: {val}"
                    )
            overrides[key] = out
    missing = [k for k in required_keys if k not in overrides]
    if missing:
        missing_txt = ", ".join([f"{esc}-{et}" for esc, et in missing])
        raise ValueError(
            f"Faltan filas en overrides para etapas/escenarios requeridos: {missing_txt}"
        )
    return overrides


def apply_factor_overrides(
    rows: List[Dict[str, object]], overrides: Dict[tuple[str, int], Dict[str, float]]
) -> List[Dict[str, object]]:
    updated_rows: List[Dict[str, object]] = []
    for row in rows:
        out = dict(row)
        key = (str(out["escenario"]).strip().upper(), int(out["etapa"]))
        factors = overrides.get(key)
        if factors is None:
            raise ValueError(
                f"No existe override para escenario={key[0]}, etapa={key[1]}. "
                "Todas las etapas deben depender del CSV de overrides."
            )
        boniga = float(out["boniga_kg"]) * factors["factor_boniga"]
        agua = float(out["agua_l"]) * factors["factor_agua"]
        masa = (boniga + agua) * factors["factor_masa_total"]
        out["boniga_kg"] = boniga
        out["agua_l"] = agua
        out["masa_total_kg_eq"] = masa
        out["factor_boniga_override"] = factors["factor_boniga"]
        out["factor_agua_override"] = factors["factor_agua"]
        out["factor_masa_total_override"] = factors["factor_masa_total"]
        out["origen_masa_total"] = "override_factor"
        updated_rows.append(out)
    return updated_rows


def build_rows(agua_anual_l: float, boniga_anual_kg: float, factor_a2: float) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []

    def add_row(
        escenario: str,
        etapa: int,
        formula: str,
        boniga_kg: float,
        agua_l: float,
        masa_total_kg_eq: float,
    ) -> None:
        rows.append(
            {
                "escenario": escenario,
                "etapa": etapa,
                "formula": formula,
                "boniga_kg": boniga_kg,
                "agua_l": agua_l,
                "masa_total_kg_eq": masa_total_kg_eq,
                "unidad_masa_total": "kg_eq (1 L agua = 1 kg)",
            }
        )

    # Base neutral para todas las etapas/escenarios:
    # - agua base: flujo anual de agua
    # - boniga base: flujo anual de boniga fresca
    # Excepcion permitida fuera de override: A2 convierte fresca->precompostada con factor_a2.
    stage_definitions = [
        ("A", 1, 1.0, "base_anual (override controla inclusion de agua/boniga)"),
        ("A", 2, factor_a2, "base_anual con conversion fresca->precompostada (factor_a2)"),
        ("A", 3, 1.0, "base_anual (override controla inclusion de agua/boniga)"),
        ("A", 4, 1.0, "base_anual (override controla inclusion de agua/boniga)"),
        ("B", 1, 1.0, "base_anual (override controla inclusion de agua/boniga)"),
        ("B", 2, 1.0, "base_anual (override controla inclusion de agua/boniga)"),
    ]
    for escenario, etapa, factor_boniga_base, formula in stage_definitions:
        boniga_base = boniga_anual_kg * factor_boniga_base
        agua_base = agua_anual_l
        masa_base = boniga_base + agua_base
        add_row(
            escenario,
            etapa,
            formula,
            boniga_kg=boniga_base,
            agua_l=agua_base,
            masa_total_kg_eq=masa_base,
        )

    return rows


def write_output(rows: List[Dict[str, object]], output_path: Path, factor_a2: float) -> None:
    columns = [
        "escenario",
        "etapa",
        "formula",
        "boniga_kg",
        "agua_l",
        "factor_restante_a2",
        "masa_total_kg_eq",
        "unidad_masa_total",
        "factor_boniga_override",
        "factor_agua_override",
        "factor_masa_total_override",
        "origen_masa_total",
        "fuente_agua_boniga",
        "fuente_factor_a2",
        "fuente_factor_overrides",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            out = dict(row)
            out["factor_restante_a2"] = factor_a2
            out["fuente_agua_boniga"] = "processed/agua_boniga_estadistica_descriptiva.csv"
            out["fuente_factor_a2"] = "processed/volatile_solids_mass_loss_fresh_to_precomposted.csv"
            out["fuente_factor_overrides"] = "processed/masa_total_factor_overrides.csv"
            for key in ("boniga_kg", "agua_l", "factor_restante_a2", "masa_total_kg_eq"):
                out[key] = f"{float(out[key]):.6f}"
            for key in ("factor_boniga_override", "factor_agua_override", "factor_masa_total_override"):
                out[key] = f"{float(out[key]):.6f}"
            writer.writerow(out)


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    processed = project_root / "processed"

    agua_boniga_path = processed / "agua_boniga_estadistica_descriptiva.csv"
    mass_loss_path = processed / "volatile_solids_mass_loss_fresh_to_precomposted.csv"
    factor_overrides_path = processed / "masa_total_factor_overrides.csv"
    output_path = processed / "masa_total_escenario_etapa.csv"

    flujo_anual = load_agua_boniga_flujo_anual(agua_boniga_path)
    agua_anual_l = flujo_anual["agua"]
    boniga_anual_kg = flujo_anual["boniga"]
    factor_a2 = load_mass_ratio(mass_loss_path)

    rows_base = build_rows(agua_anual_l=agua_anual_l, boniga_anual_kg=boniga_anual_kg, factor_a2=factor_a2)
    required_keys = [
        (str(r["escenario"]).strip().upper(), int(r["etapa"]))
        for r in rows_base
    ]
    overrides = load_factor_overrides(factor_overrides_path, required_keys)
    rows = apply_factor_overrides(rows_base, overrides)
    write_output(rows, output_path, factor_a2)

    print(f"Generated file: {output_path}")
    print(f"Rows: {len(rows)}")
    print(f"Factor overrides: {factor_overrides_path} ({len(overrides)} filas aplicadas)")


if __name__ == "__main__":
    main()
