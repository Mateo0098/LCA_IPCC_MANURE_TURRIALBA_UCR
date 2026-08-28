"""Calcula consumos operativos foreground desde parámetros canónicos."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = ROOT / "processed" / "acv_parametros_operativos.csv"
MASSES = ROOT / "processed" / "masa_total_escenario_etapa.csv"
OUTPUT = ROOT / "processed" / "acv_inventario_recursos_operativos.csv"


def load_parameters() -> dict[str, float]:
    table = pd.read_csv(PARAMETERS)
    if table["parametro"].duplicated().any():
        raise ValueError("Hay parámetros operativos duplicados.")
    values = dict(zip(table["parametro"], pd.to_numeric(table["valor"], errors="raise")))
    required = {
        "model_year_days", "pump_mechanical_power_kw", "pump_motor_efficiency",
        "pump_wash_minutes", "pump_washes_per_cycle", "pump_cycle_days",
        "tractor_diesel_l_per_hour", "tractor_operation_minutes", "tractor_cycle_days",
    }
    missing = required - values.keys()
    if missing:
        raise ValueError(f"Faltan parámetros operativos: {sorted(missing)}")
    if any(values[name] <= 0 for name in required):
        raise ValueError("Todos los parámetros operativos deben ser positivos.")
    return values


def functional_reference() -> float:
    mass = pd.read_csv(MASSES)
    refs = pd.to_numeric(mass["flujo_referencia_anual_kg"], errors="raise").unique()
    if len(refs) != 1 or refs[0] <= 0:
        raise ValueError("La referencia funcional anual debe ser única y positiva.")
    return float(refs[0])


def build_inventory(parameters: dict[str, float], reference_kg: float) -> pd.DataFrame:
    days = parameters["model_year_days"]
    pump_input_kw = parameters["pump_mechanical_power_kw"] / parameters["pump_motor_efficiency"]
    washes_per_year = days / parameters["pump_cycle_days"] * parameters["pump_washes_per_cycle"]
    pump_hours = washes_per_year * parameters["pump_wash_minutes"] / 60.0
    electricity = pump_input_kw * pump_hours

    operations_per_year = days / parameters["tractor_cycle_days"]
    tractor_hours = operations_per_year * parameters["tractor_operation_minutes"] / 60.0
    diesel = tractor_hours * parameters["tractor_diesel_l_per_hour"]

    common = {
        "referencia_funcional_estiercol_fresco_kg": reference_kg,
        "estado_lcia_actual": "Inventariado; proceso de fondo pendiente",
        "dataset_background_pendiente": "Sí",
    }
    rows = [
        {"escenario": "A", "etapa": 3, "flujo": "Electricidad", "cantidad_anual": electricity,
         "unidad": "kWh/año", "procedencia": "Bombeo de agua pluvial para lavado", **common},
        {"escenario": "A", "etapa": 4, "flujo": "Diésel", "cantidad_anual": diesel,
         "unidad": "L/año", "procedencia": "Tractor y cañón durante la aplicación", **common},
        {"escenario": "B", "etapa": 1, "flujo": "Electricidad", "cantidad_anual": electricity,
         "unidad": "kWh/año", "procedencia": "Bombeo de agua pluvial para lavado", **common},
        {"escenario": "B", "etapa": 2, "flujo": "Diésel", "cantidad_anual": diesel,
         "unidad": "L/año", "procedencia": "Tractor y cañón durante la aplicación", **common},
    ]
    out = pd.DataFrame(rows)
    out["cantidad_por_unidad_funcional"] = out["cantidad_anual"] / reference_kg
    out["unidad_por_unidad_funcional"] = out["unidad"].str.replace("/año", "/kg de estiércol fresco", regex=False)
    return out


def validate(df: pd.DataFrame) -> None:
    by_stage = {(row.escenario, int(row.etapa), row.flujo): float(row.cantidad_anual)
                for row in df.itertuples()}
    assert abs(by_stage[("A", 3, "Electricidad")] - 53.229166666666664) < 1e-10
    assert by_stage[("A", 3, "Electricidad")] == by_stage[("B", 1, "Electricidad")]
    assert abs(by_stage[("A", 4, "Diésel")] - 182.5) < 1e-10
    assert by_stage[("A", 4, "Diésel")] == by_stage[("B", 2, "Diésel")]
    assert not df["flujo"].str.contains("cañón", case=False, regex=False).any()


def main() -> None:
    inventory = build_inventory(load_parameters(), functional_reference())
    validate(inventory)
    inventory.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    print(f"Inventario operativo: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

