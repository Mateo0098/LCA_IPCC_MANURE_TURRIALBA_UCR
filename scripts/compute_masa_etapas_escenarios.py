from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass(frozen=True)
class ParametrosOperativos:
    peso_vivo_promedio: float
    poblacion_media: float
    permanencia_sala: float
    estiercol_recolectado_animal: float
    estiercol_recolectado_anual: float
    agua_lavado_diaria: float
    fraccion_generacion_diaria: float
    horas_dia: float
    dias_ano: float


@dataclass(frozen=True)
class BalanceEstiercol:
    generacion_diaria_teorica_animal: float
    estiercol_teorico_sala_animal: float
    fraccion_recolectada: float
    fraccion_remanente: float
    estiercol_total_depositado_anual: float
    estiercol_remanente_anual: float
    agua_lavado_anual: float


def load_operational_parameters(csv_path: Path) -> ParametrosOperativos:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        values: Dict[str, float] = {}
        for row in reader:
            parameter = str(row.get("parametro", "")).strip()
            raw_value = row.get("valor")
            if parameter and raw_value not in (None, ""):
                values[parameter] = float(raw_value)
    required = set(ParametrosOperativos.__dataclass_fields__)
    faltantes = required - set(values)
    if faltantes:
        raise ValueError(f"Faltan parámetros operativos: {sorted(faltantes)} en {csv_path}")
    return ParametrosOperativos(**{name: values[name] for name in required})


def compute_manure_balance(params: ParametrosOperativos) -> BalanceEstiercol:
    if params.peso_vivo_promedio <= 0 or params.estiercol_recolectado_anual <= 0:
        raise ValueError("El peso vivo y el estiércol anual recolectado deben ser positivos.")
    if not 0 < params.fraccion_generacion_diaria <= 1:
        raise ValueError("La fracción de generación diaria debe estar en (0, 1].")
    if not 0 < params.permanencia_sala <= params.horas_dia:
        raise ValueError("La permanencia en sala debe estar entre 0 y las horas del día.")

    generacion_diaria = params.peso_vivo_promedio * params.fraccion_generacion_diaria
    teorico_sala = generacion_diaria * (params.permanencia_sala / params.horas_dia)
    if params.estiercol_recolectado_animal >= teorico_sala:
        raise ValueError(
            "El estiércol recolectado por animal debe ser menor que el depósito teórico en sala."
        )
    fraccion_recolectada = params.estiercol_recolectado_animal / teorico_sala
    fraccion_remanente = 1.0 - fraccion_recolectada
    total_depositado = params.estiercol_recolectado_anual / fraccion_recolectada
    remanente = total_depositado - params.estiercol_recolectado_anual
    agua_anual = params.agua_lavado_diaria * params.dias_ano

    if abs(total_depositado - params.estiercol_recolectado_anual - remanente) > 1e-9:
        raise AssertionError("No se conserva el balance de estiércol en sala.")
    if abs(fraccion_recolectada + fraccion_remanente - 1.0) > 1e-12:
        raise AssertionError("Las fracciones recolectada y remanente no suman uno.")

    return BalanceEstiercol(
        generacion_diaria_teorica_animal=generacion_diaria,
        estiercol_teorico_sala_animal=teorico_sala,
        fraccion_recolectada=fraccion_recolectada,
        fraccion_remanente=fraccion_remanente,
        estiercol_total_depositado_anual=total_depositado,
        estiercol_remanente_anual=remanente,
        agua_lavado_anual=agua_anual,
    )


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


def build_rows(
    params: ParametrosOperativos, balance: BalanceEstiercol, factor_a2: float
) -> List[Dict[str, object]]:
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

    # El estiércol remanente es parte del depósito teórico total y no una generación adicional.
    # Solo A3/A4 usan el remanente para representar la formación de aguas verdes.
    # B recibe el 100 % del depósito teórico, sin separación por paleado.
    stage_definitions = [
        ("A", 1, params.estiercol_recolectado_anual, "estiércol fresco recolectado"),
        (
            "A",
            2,
            params.estiercol_recolectado_anual * factor_a2,
            "estiércol recolectado con conversión fresca a precompostada",
        ),
        ("A", 3, balance.estiercol_remanente_anual, "estiércol remanente arrastrable"),
        ("A", 4, balance.estiercol_remanente_anual, "estiércol remanente más agua de lavado"),
        (
            "B",
            1,
            balance.estiercol_total_depositado_anual,
            "estiércol total teóricamente depositado",
        ),
        (
            "B",
            2,
            balance.estiercol_total_depositado_anual,
            "estiércol total teóricamente depositado más agua de lavado",
        ),
    ]
    for escenario, etapa, boniga_base, formula in stage_definitions:
        agua_base = balance.agua_lavado_anual
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


def validate_scenario_balances(
    rows: List[Dict[str, object]],
    params: ParametrosOperativos,
    balance: BalanceEstiercol,
    tolerance: float = 1e-6,
) -> None:
    by_stage = {
        (str(row["escenario"]), int(row["etapa"])): row
        for row in rows
    }
    required = {("A", 1), ("A", 3), ("A", 4), ("B", 1), ("B", 2)}
    missing = required - set(by_stage)
    if missing:
        raise AssertionError(f"Faltan etapas para validar balances: {sorted(missing)}")

    a1 = float(by_stage[("A", 1)]["boniga_kg"])
    a3 = float(by_stage[("A", 3)]["boniga_kg"])
    a4 = float(by_stage[("A", 4)]["masa_total_kg_eq"])
    b1 = float(by_stage[("B", 1)]["boniga_kg"])
    b2 = float(by_stage[("B", 2)]["masa_total_kg_eq"])
    reference_a = a1 + a3
    reference_b = b1

    checks = {
        "balance A": (reference_a, balance.estiercol_total_depositado_anual),
        "balance B": (reference_b, balance.estiercol_total_depositado_anual),
        "aplicación A4": (a4, balance.agua_lavado_anual + balance.estiercol_remanente_anual),
        "aplicación B2": (b2, balance.agua_lavado_anual + balance.estiercol_total_depositado_anual),
        "flujo de referencia A/B": (reference_a, reference_b),
        "A1 recolectado": (a1, params.estiercol_recolectado_anual),
    }
    for name, (actual, expected) in checks.items():
        if not abs(actual - expected) <= tolerance:
            raise AssertionError(
                f"Fallo en {name}: valor={actual:.12f}; esperado={expected:.12f}"
            )


def write_output(
    rows: List[Dict[str, object]],
    output_path: Path,
    factor_a2: float,
    params: ParametrosOperativos,
    balance: BalanceEstiercol,
) -> None:
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
        "estiercol_recolectado_anual_kg",
        "estiercol_total_depositado_anual_kg",
        "estiercol_remanente_anual_kg",
        "fraccion_recolectada",
        "fraccion_remanente",
        "flujo_referencia_anual_kg",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            out = dict(row)
            out["factor_restante_a2"] = factor_a2
            out["fuente_agua_boniga"] = "Academic_documents/references/parametros_operativos_sanchez_2026.csv"
            out["fuente_factor_a2"] = "processed/volatile_solids_mass_loss_fresh_to_precomposted.csv"
            out["fuente_factor_overrides"] = "processed/masa_total_factor_overrides.csv"
            out["estiercol_recolectado_anual_kg"] = f"{params.estiercol_recolectado_anual:.6f}"
            out["estiercol_total_depositado_anual_kg"] = (
                f"{balance.estiercol_total_depositado_anual:.6f}"
            )
            out["estiercol_remanente_anual_kg"] = f"{balance.estiercol_remanente_anual:.6f}"
            out["fraccion_recolectada"] = f"{balance.fraccion_recolectada:.12f}"
            out["fraccion_remanente"] = f"{balance.fraccion_remanente:.12f}"
            out["flujo_referencia_anual_kg"] = (
                f"{balance.estiercol_total_depositado_anual:.6f}"
            )
            for key in ("boniga_kg", "agua_l", "factor_restante_a2", "masa_total_kg_eq"):
                out[key] = f"{float(out[key]):.6f}"
            for key in ("factor_boniga_override", "factor_agua_override", "factor_masa_total_override"):
                out[key] = f"{float(out[key]):.6f}"
            writer.writerow(out)


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    processed = project_root / "processed"

    operational_parameters_path = (
        project_root / "Academic_documents" / "references" / "parametros_operativos_sanchez_2026.csv"
    )
    mass_loss_path = processed / "volatile_solids_mass_loss_fresh_to_precomposted.csv"
    factor_overrides_path = processed / "masa_total_factor_overrides.csv"
    output_path = processed / "masa_total_escenario_etapa.csv"

    params = load_operational_parameters(operational_parameters_path)
    balance = compute_manure_balance(params)
    factor_a2 = load_mass_ratio(mass_loss_path)

    rows_base = build_rows(params=params, balance=balance, factor_a2=factor_a2)
    required_keys = [
        (str(r["escenario"]).strip().upper(), int(r["etapa"]))
        for r in rows_base
    ]
    overrides = load_factor_overrides(factor_overrides_path, required_keys)
    rows = apply_factor_overrides(rows_base, overrides)
    validate_scenario_balances(rows, params, balance)
    write_output(rows, output_path, factor_a2, params, balance)

    print(f"Generated file: {output_path}")
    print(f"Rows: {len(rows)}")
    print(f"Factor overrides: {factor_overrides_path} ({len(overrides)} filas aplicadas)")
    print(f"Estiércol recolectado: {params.estiercol_recolectado_anual:.6f} kg/año")
    print(f"Estiércol total depositado: {balance.estiercol_total_depositado_anual:.6f} kg/año")
    print(f"Estiércol remanente: {balance.estiercol_remanente_anual:.6f} kg/año")
    print(f"Fracción recolectada: {balance.fraccion_recolectada:.12f}")
    print(f"Fracción remanente: {balance.fraccion_remanente:.12f}")
    print(f"Agua de lavado: {balance.agua_lavado_anual:.6f} L/año")
    print(
        "Flujo de referencia A = B: "
        f"{balance.estiercol_total_depositado_anual:.6f} kg estiércol fresco/año"
    )


if __name__ == "__main__":
    main()
