"""
Escenario B etapa 1. Exporta resultados de emisiones a tabla común.
"""
import numpy as np
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
from acv_resumen_emisiones_csv import exportar_fila
from acv_parametros_etapa import obtener_parametros_etapa
from acv_masa_seca import convertir_vs_base_humeda, obtener_fraccion_masa_seca_etapa
from acv_factores_manejo_estiercol import obtener_factores_manejo_ipcc

PARAMS_ETAPA = obtener_parametros_etapa("B", 1)
FACTORES_MMS = obtener_factores_manejo_ipcc("B", 1)

# ============================================================
# DEFINICIÓN DE VARIABLES – LISTO PARA JUPYTER NOTEBOOK
# (Variables unificadas, desglosadas por ecuación IPCC)
# ============================================================

# ------------------------------------------------------------
# ECUACIÓN (1) – Factor de emisión de CH4 por gestión de estiércol
# Función: ef_ch4
# ------------------------------------------------------------
FRACCION_MASA_SECA = obtener_fraccion_masa_seca_etapa("B", 1)
VS_T = convertir_vs_base_humeda(PARAMS_ETAPA["vs_t_pct"], FRACCION_MASA_SECA)
B0_T = 0.24        # m3 CH4 kg-1 SV
MCF = FACTORES_MMS["MCF"]  # %
AWMS = 1.0        # adimensional


# ------------------------------------------------------------
# ECUACIÓN (2) – Emisiones directas de N2O de la gestión del estiércol
# Función: n2o_direct_mm
# ------------------------------------------------------------
N = 1          # número de cabezas
Nex = PARAMS_ETAPA["n_ex_pct"]  # % N total (tabla central)
AWMS = 1        # adimensional
N_cdg = 0.0       # kg N año-1
EF3 = FACTORES_MMS["EF3"]  # kg N2O-N kg-1 N


# ------------------------------------------------------------
# ECUACIÓN (3) – N volatilizado desde la gestión del estiércol
# Función: n_volatilization_mms
# ------------------------------------------------------------
N = 1              # número de cabezas
Nex = PARAMS_ETAPA["n_ex_pct"]  # % N total (tabla central)
AWMS = 1            # adimensional
N_cdg = 0.0           # kg N año-1
frac_gas_ms = FACTORES_MMS["frac_gas_ms"]


# ------------------------------------------------------------
# ECUACIÓN (4) – N lixiviado desde la gestión del estiércol
# Función: n_lixiviado_mms
# ------------------------------------------------------------

N = 1              # número de cabezas
Nex = PARAMS_ETAPA["n_ex_pct"]  # % N total (tabla central)
AWMS = 1            # adimensional
N_cdg = 0.0           # kg N año-1
frac_leach_ms = FACTORES_MMS["frac_leach_ms"]

# ------------------------------------------------------------
# ECUACIÓN (5) – Emisiones indirectas de N2O por volatilización
# Función: n2o_indirect_volatilization. Usa N_volatilization_MMS (ec. 3)
# ------------------------------------------------------------
N_volatilization_mms = 0.0  # kg N año-1
EF4 = 0.014                 # kg N2O-N (kg NH3-N + NOx-N)-1


# ------------------------------------------------------------
# ECUACIÓN (6) – Emisiones indirectas de N2O por lixiviación
# Función: n2o_indirect_leaching. Usa n_lixiviado_mms (ec. 4)
# ------------------------------------------------------------
N_leaching_mms = 0.0  # kg N año-1
EF5 = 0.011            # kg N2O-N kg-1 N lixiviado

# ------------------------------------------------------------
# ECUACIÓN (7) – N indirecto por volatilización (N_G mm)
# Función: n_indirect_volatilization. Usa N_volatilization_MMS (ec. 3) y EF4
# ------------------------------------------------------------

# ------------------------------------------------------------
# ECUACIÓN (8) – N indirecto por lixiviación (N_L mm)
# Función: n_indirect_leaching. Usa N_leaching_MMS (ec. 4) y EF5
# ------------------------------------------------------------

# ------------------------------------------------------------
# ECUACIÓN (12) – NH3 directo desde gestión estiércol
# Función: nh3_direct_mm. Usa resultados de ec. (7) y (8)
# ------------------------------------------------------------

# ------------------------------------------------------------
# ECUACIÓN (13) – NO3 directo desde gestión estiércol
# Función: no3_direct_mm. Usa resultados de ec. (7) y (8)
# ------------------------------------------------------------


# ============================================================
# LLAMADAS A TODAS LAS FUNCIONES
# (asumiendo que las variables ya están definidas)
# ============================================================

# Ecuación (1)
EF_T = ef_ch4(
    VS_T=VS_T,
    B0_T=B0_T,
    MCF=MCF,
    AWMS=AWMS
)


# Ecuación (2)
N2O_D_mm = n2o_direct_mm(
    N=N,
    Nex=Nex,
    AWMS=AWMS,
    N_cdg=N_cdg,
    EF3=EF3
)

# Ecuación (3)
N_volatilization_MMS = n_volatilization_mms(
    N=N,
    Nex=Nex,
    AWMS=AWMS,
    N_cdg=N_cdg,
    frac_gas_ms=frac_gas_ms
)

# Ecuación (4)
N_leaching_MMS = n_lixiviado_mms(
    N=N,
    N_ex=Nex,
    AWMS=AWMS,
    N_cdg=N_cdg,
    frac_leach_ms=frac_leach_ms
)

# Ecuación (5)
N2O_G_mm = n2o_indirect_volatilization(
    N_volatilization_mms=N_volatilization_MMS,
    EF4=EF4
)

# Ecuación (6)
N2O_L_mm = n2o_indirect_leaching(
    N_leaching_mms=N_leaching_MMS,
    EF5=EF5
)

# Ecuación (7)
N_G_mm = n_indirect_volatilization(N_volatilization_MMS, EF4)

# Ecuación (8)
N_L_mm = n_indirect_leaching(N_leaching_MMS, EF5)

# Ecuación (12)
NH3_direct_mm = nh3_direct_mm(n_indirect_volatilization=N_G_mm, n_indirect_leaching=N_L_mm)

# Ecuación (13)
NO3_direct_mm = no3_direct_mm(n_indirect_volatilization=N_G_mm, n_indirect_leaching=N_L_mm)

# Exportar a tabla común
fila = {
    "Escenario": "B",
    "Etapa": 1,
    "CH4_ec1": EF_T,
    "N2O_ec2": N2O_D_mm,
    "N2O_ec5": N2O_G_mm,
    "N2O_ec6": N2O_L_mm,
    "NH3_ec12": NH3_direct_mm,
    "NH3_ec20": np.nan,
    "NO3_ec13": NO3_direct_mm,
    "NO3_ec21": np.nan,
}
exportar_fila("B", 1, fila)
