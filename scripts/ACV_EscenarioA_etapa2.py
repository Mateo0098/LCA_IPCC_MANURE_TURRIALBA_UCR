"""
Escenario A etapa 2. Exporta resultados de emisiones a tabla común.

Soporta dos modelos:
- ipcc (default)
- medido (factores medidos sobre residuo en base seca)
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from acv_modelo_etapa import obtener_modelo_etapa
from acv_parametros_etapa import obtener_parametros_etapa
from acv_resumen_emisiones_csv import exportar_fila
from ecuaciones_acv import (
    ef_ch4,
    n2o_direct_mm,
    n_volatilization_mms,
    n_lixiviado_mms,
    n2o_indirect_volatilization,
    n2o_indirect_leaching,
    n_indirect_volatilization,
    n_indirect_leaching,
    nh3_direct_mm,
    no3_direct_mm,
)
from acv_masa_seca import convertir_vs_base_humeda
from acv_factores_manejo_estiercol import obtener_factores_manejo_ipcc


def _load_precomposted_dry_matter_fraction(base: Path) -> float:
    """
    Carga fracción de materia seca del estiércol precompostado desde:
    processed/volatile_solids_treatment_table.csv
    Referencia de usuario: columna H, fila 3.
    """
    path = base / "processed" / "volatile_solids_treatment_table.csv"
    df = pd.read_csv(path)

    col_dm = "dry_matter_treatment_mean_pct"
    if col_dm not in df.columns:
        raise ValueError(f"No existe columna '{col_dm}' en {path}")

    row = None
    if "sample_type" in df.columns:
        mask = df["sample_type"].astype(str).str.lower().str.contains("precompost")
        if mask.any():
            row = df.loc[mask].iloc[0]
    if row is None and "treatment" in df.columns:
        mask = df["treatment"].astype(str).str.strip().str.upper() == "B"
        if mask.any():
            row = df.loc[mask].iloc[0]
    if row is None:
        if df.shape[0] < 2:
            raise ValueError(f"No hay suficientes filas en {path} para tomar fila 3/segundo tratamiento.")
        row = df.iloc[1]

    dm_pct = float(row[col_dm])
    if dm_pct <= 0:
        raise ValueError(f"dry_matter_treatment_mean_pct invalido: {dm_pct} en {path}")
    return dm_pct / 100.0


def _load_medido_factors(base: Path) -> tuple[float, float, float]:
    path = base / "processed" / "factores_emision_medidos.csv"
    df = pd.read_csv(path)
    if "modelo" not in df.columns:
        raise ValueError(f"No existe columna 'modelo' en {path}")

    row_df = df[df["modelo"].astype(str).str.strip().str.lower() == "medido"]
    if row_df.empty:
        raise ValueError(f"No existe fila con modelo='medido' en {path}")
    row = row_df.iloc[0]

    required = [
        "co2_kg_por_kg_residuo_seco",
        "ch4_kg_por_kg_residuo_seco",
        "n2o_kg_por_kg_residuo_seco",
    ]
    for col in required:
        if col not in row.index:
            raise ValueError(f"No existe columna '{col}' en {path}")

    ef_co2_dry = float(row["co2_kg_por_kg_residuo_seco"])
    ef_ch4_dry = float(row["ch4_kg_por_kg_residuo_seco"])
    ef_n2o_dry = float(row["n2o_kg_por_kg_residuo_seco"])
    if ef_co2_dry < 0 or ef_ch4_dry < 0 or ef_n2o_dry < 0:
        raise ValueError(f"Factores medidos no pueden ser negativos en {path}")
    return ef_co2_dry, ef_ch4_dry, ef_n2o_dry


def _build_ipcc_row() -> dict[str, float | int]:
    params = obtener_parametros_etapa("A", 2)
    factores_mms = obtener_factores_manejo_ipcc("A", 2)

    dry_fraction = _load_precomposted_dry_matter_fraction(Path(__file__).resolve().parent.parent)
    vs_t = convertir_vs_base_humeda(params["vs_t_pct"], dry_fraction)
    b0_t = 0.24
    mcf = float(factores_mms["MCF"])
    awms = 1.0

    n = 1
    n_ex_pct = params["n_ex_pct"]  # % N total reportado en laboratorio
    n_ex_fraction = n_ex_pct / 100.0  # fraccion masica kg N / kg muestra
    nex = n_ex_fraction
    n_cdg = 0.0
    ef3 = float(factores_mms["EF3"])
    frac_gas_ms = float(factores_mms["frac_gas_ms"])
    frac_leach_ms = float(factores_mms["frac_leach_ms"])
    ef4 = 0.014
    ef5 = 0.011

    ch4_ec1 = ef_ch4(VS_T=vs_t, B0_T=b0_t, MCF=mcf, AWMS=awms)
    n2o_ec2 = n2o_direct_mm(N=n, Nex=nex, AWMS=awms, N_cdg=n_cdg, EF3=ef3)
    n_vol = n_volatilization_mms(N=n, Nex=nex, AWMS=awms, N_cdg=n_cdg, frac_gas_ms=frac_gas_ms)
    n_leach = n_lixiviado_mms(N=n, N_ex=nex, AWMS=awms, N_cdg=n_cdg, frac_leach_ms=frac_leach_ms)
    n2o_ec5 = n2o_indirect_volatilization(N_volatilization_mms=n_vol, EF4=ef4)
    n2o_ec6 = n2o_indirect_leaching(N_leaching_mms=n_leach, EF5=ef5)
    n_g = n_indirect_volatilization(n_vol, ef4)
    n_l = n_indirect_leaching(n_leach, ef5)
    nh3_ec12 = nh3_direct_mm(n_indirect_volatilization=n_g, n_indirect_leaching=n_l)
    no3_ec13 = no3_direct_mm(n_indirect_volatilization=n_g, n_indirect_leaching=n_l)

    return {
        "Escenario": "A",
        "Etapa": 2,
        "CO2_medido": np.nan,
        "CH4_ec1": ch4_ec1,
        "N2O_ec2": n2o_ec2,
        "N2O_ec5": n2o_ec5,
        "N2O_ec6": n2o_ec6,
        "NH3_ec12": nh3_ec12,
        "NH3_ec20": np.nan,
        "NO3_ec13": no3_ec13,
        "NO3_ec21": np.nan,
    }


def _build_medido_row(base: Path) -> dict[str, float | int]:
    # Factores medidos (por kg residuo seco) desde tabla editable.
    ef_co2_dry, ef_ch4_dry, ef_n2o_dry = _load_medido_factors(base)

    dry_fraction = _load_precomposted_dry_matter_fraction(base)

    # Se exportan factores por kg masa húmeda y luego exportar_fila escala por masa_total_kg_eq.
    co2_per_kg_wet = ef_co2_dry * dry_fraction
    ch4_per_kg_wet = ef_ch4_dry * dry_fraction
    n2o_per_kg_wet = ef_n2o_dry * dry_fraction

    return {
        "Escenario": "A",
        "Etapa": 2,
        "CO2_medido": co2_per_kg_wet,
        "CH4_ec1": ch4_per_kg_wet,
        "N2O_ec2": n2o_per_kg_wet,
        "N2O_ec5": 0.0,
        "N2O_ec6": 0.0,
        "NH3_ec12": 0.0,
        "NH3_ec20": np.nan,
        "NO3_ec13": 0.0,
        "NO3_ec21": np.nan,
    }


def main() -> None:
    base = Path(__file__).resolve().parent.parent
    modelo = obtener_modelo_etapa("A", 2, default="ipcc")

    if modelo == "ipcc":
        fila = _build_ipcc_row()
    elif modelo == "medido":
        fila = _build_medido_row(base)
    else:
        raise ValueError(f"Modelo no soportado para A2: {modelo}")

    exportar_fila("A", 2, fila)
    print(f"A2 modelo usado: {modelo}")


if __name__ == "__main__":
    main()
