"""Factores IMN por actividad: electricidad agregada y masas de combustión.

No caracteriza el diésel: esa responsabilidad corresponde al módulo LCIA EF.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FACTOR_PATH = ROOT / "processed/acv_factores_imn_recursos_operativos.csv"
EXPECTED = {
    "imn_electricidad_consumo_2025": ("Electricidad", "consumo agregado", "CO2-eq", "kg CO2-eq/kWh", "Consumo de electricidad", "2025"),
    "imn_diesel_co2": ("Diésel", "emisión física", "CO2", "kg CO2/L", "Diésel: general por combustible", "ND"),
    "imn_diesel_ch4_agricola": ("Diésel", "emisión física", "CH4", "g CH4/L", "Residencial y agrícola/Diésel", "ND"),
    "imn_diesel_n2o_agricola": ("Diésel", "emisión física", "N2O", "g N2O/L", "Residencial y agrícola/Diésel", "ND"),
}
DERIVED_COLUMNS = ["co2_fosil_diesel_kg", "ch4_fosil_diesel_kg", "n2o_combustion_diesel_kg", "clima_electricidad_imn_kg_co2eq"]


def load_imn_factors(path: Path = FACTOR_PATH) -> pd.DataFrame:
    table = pd.read_csv(path, keep_default_na=False, dtype=str)
    if table["id_factor"].duplicated().any() or set(table["id_factor"]) != set(EXPECTED):
        raise ValueError("Selección IMN incompleta o duplicada.")
    table = table.set_index("id_factor")
    columns = ["recurso", "tipo_factor", "especie_indicador", "unidad_original", "categoria_imn", "ano_representado"]
    for ident, expected in EXPECTED.items():
        row = table.loc[ident]
        if tuple(row[c] for c in columns) != expected or row["estado_seleccion"] != "Aprobado":
            raise ValueError(f"Factor IMN incompatible con la decisión aprobada: {ident}")
        source = ROOT / row["ruta_fuente"]
        if hashlib.sha256(source.read_bytes()).hexdigest() != row["sha256_fuente"]:
            raise ValueError(f"La fuente IMN cambió: {source}")
    table["valor"] = pd.to_numeric(table["valor"], errors="raise")
    if not np.isfinite(table["valor"]).all() or (table["valor"] <= 0).any():
        raise ValueError("Los factores IMN deben ser positivos y finitos.")
    return table


def add_operational_emissions(inventory: pd.DataFrame, factors: pd.DataFrame) -> pd.DataFrame:
    out = inventory.copy()
    for column in DERIVED_COLUMNS:
        out[column] = 0.0
    for index, row in out.iterrows():
        quantity = float(row["cantidad_anual"])
        if not np.isfinite(quantity) or quantity < 0:
            raise ValueError("Cantidad operativa inválida.")
        if row["flujo"] == "Electricidad" and row["unidad"] == "kWh/año":
            ident = "imn_electricidad_consumo_2025"
            out.loc[index, DERIVED_COLUMNS[3]] = quantity * float(factors.loc[ident, "valor"])
            out.loc[index, "factores_imn"] = ident
            out.loc[index, "estado_lcia_actual"] = "Contribución climática agregada IMN de consumo 2025"
        elif row["flujo"] == "Diésel" and row["unidad"] == "L/año":
            identities = ["imn_diesel_co2", "imn_diesel_ch4_agricola", "imn_diesel_n2o_agricola"]
            # CO2 se publica en kg/L; CH4 y N2O en g/L: conversión explícita a kg.
            for column, ident, grams_per_kg in zip(DERIVED_COLUMNS[:3], identities, (1.0, 1000.0, 1000.0)):
                out.loc[index, column] = quantity * float(factors.loc[ident, "valor"]) / grams_per_kg
            out.loc[index, "factores_imn"] = ";".join(identities)
            out.loc[index, "estado_lcia_actual"] = "Emisiones físicas IMN para caracterización EF 3.1"
        else:
            raise ValueError(f"Recurso o unidad operativa no admitida: {row['flujo']}, {row['unidad']}")
    for column in DERIVED_COLUMNS:
        out[column + "_por_kg_estiercol_fresco"] = out[column] / out["referencia_funcional_estiercol_fresco_kg"]
    return out
