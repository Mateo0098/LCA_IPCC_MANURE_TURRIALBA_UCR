"""
Escenario A etapa 2. Exporta resultados de emisiones a tabla común.

Utiliza las ecuaciones IPCC compartidas y los factores efectivos configurados
para la etapa.
"""

from __future__ import annotations

import numpy as np

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
from acv_masa_seca import (
    convertir_n_material_preparado_a_base_humeda,
    convertir_vs_base_humeda,
    obtener_fraccion_masa_seca_etapa,
)
from acv_factores_manejo_estiercol import obtener_factores_manejo_ipcc


def _build_ipcc_row() -> dict[str, float | int]:
    params = obtener_parametros_etapa("A", 2)
    factores_mms = obtener_factores_manejo_ipcc("A", 2)

    dry_fraction = obtener_fraccion_masa_seca_etapa("A", 2)
    vs_t = convertir_vs_base_humeda(params["vs_t_pct"], dry_fraction)
    b0_t = 0.24
    mcf = float(factores_mms["MCF"])
    awms = 1.0

    n = 1
    n_ex_pct = params["n_ex_pct"]  # % N del material preparado/seco; se conserva sin alterar
    expected_transformation = "multiplicar_por_fraccion_materia_seca_gravimetrica_TFG_105C"
    if params["transformacion_n_acv"] != expected_transformation:
        raise ValueError(
            "La base analítica de N de A2 no declara la transformación aprobada "
            "a masa húmeda"
        )
    n_ex_fraction = convertir_n_material_preparado_a_base_humeda(
        n_ex_pct,
        dry_fraction,
    )  # kg N / kg de precompostado húmedo
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


def main() -> None:
    modelo = obtener_modelo_etapa("A", 2, default="ipcc")
    if modelo != "ipcc":
        raise ValueError(f"Modelo no soportado para A2: {modelo}")
    fila = _build_ipcc_row()
    exportar_fila("A", 2, fila)
    print(f"A2 modelo usado: {modelo}")


if __name__ == "__main__":
    main()
