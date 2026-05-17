"""
Escenario A etapa 4. Exporta resultados de emisiones (suelos gestionados) a tabla común.
"""
import numpy as np
from ecuaciones_acv import (
    n2o_n_inputs,
    f_on,
    n2o_atd_n,
    n_atd_sm,
    n2o_l_n,
    n_l_sm,
    nh3_direct_sm,
    no3_direct_sm,
    n_mms_available,
    frac_n2_ms,
)
from acv_resumen_emisiones_csv import exportar_fila
from acv_parametros_etapa import obtener_parametros_etapa
from acv_factores_manejo_estiercol import obtener_factores_manejo_ipcc

PARAMS_ETAPA = obtener_parametros_etapa("A", 4)
FACTORES_MMS = obtener_factores_manejo_ipcc("A", 4)
n_ex_pct = PARAMS_ETAPA["n_ex_pct"]  # % N total reportado en laboratorio
n_ex_fraction = n_ex_pct / 100.0     # fraccion masica kg N / kg muestra

# ============================================================
# DEFINICIÓN DE VARIABLES – LISTO PARA JUPYTER NOTEBOOK
# (Variables unificadas, desglosadas por ecuación IPCC)
# ============================================================

# Variables comunes (para ec. 14, 16, 18, 22, 24)
N = 1          # número de cabezas
Nex = n_ex_fraction  # fraccion masica de N (kg N / kg muestra)
AWMS = 1       # adimensional
N_cdg = 0.0    # kg N año-1
EF3 = FACTORES_MMS["EF3"]  # kg N2O-N kg-1 N
frac_gas_ms = FACTORES_MMS["frac_gas_ms"]
frac_leach_ms = FACTORES_MMS["frac_leach_ms"]
EF4 = 0.014    # kg N2O-N (kg NH3-N + NOx-N)-1
EF5 = 0.011    # kg N2O-N kg-1 N lixiviado

# ------------------------------------------------------------
# ECUACIÓN (14) – Emisiones directas de N2O-N por entradas de N
# Función: n2o_n_inputs
# ------------------------------------------------------------
F_ON = n_ex_fraction   # fraccion masica de N (kg N / kg muestra)
EF1 = 0.006    # kg N2O-N kg-1 N


# ------------------------------------------------------------
# ECUACIÓN (15) – Fertilizante orgánico nitrogenado total
# Función: f_on
# ------------------------------------------------------------
F_AM = 0.0    # kg N año-1
F_SEW = 0.0   # kg N año-1
F_COMP = n_ex_fraction  # fraccion masica de N (kg N / kg muestra)
F_OOA = 0.0   # kg N año-1


# ------------------------------------------------------------
# ECUACIÓN (16) – N2O-N por deposición atmosférica
# Función: n2o_atd_n
# ------------------------------------------------------------
F_ON = n_ex_fraction        # fraccion masica de N (kg N / kg muestra)
F_PRP = 0.0       # kg N año-1
frac_gasm = 0.21   # adimensional
EF4 = 0.014        # kg N2O-N (kg NH3-N + NOx-N)-1

# ------------------------------------------------------------
# ECUACIÓN (17) – N por deposición atmosférica desde suelos gestionados
# Función: n_atd_sm. Usa F_ON, F_PRP, frac_gasm, EF4 (mismos que ec. 16)
# ------------------------------------------------------------


# ------------------------------------------------------------
# ECUACIÓN (18) – N2O-N por lixiviación y escorrentía
# Función: n2o_l_n
# ------------------------------------------------------------
F_ON = n_ex_fraction            # fraccion masica de N (kg N / kg muestra)
F_PRP = 0.0           # kg N año-1
frac_leach_h = 0.24   # adimensional
EF5 = 0.011            # kg N2O-N kg-1 N lixiviado

# ------------------------------------------------------------
# ECUACIÓN (19) – N por lixiviación desde suelos gestionados
# Función: n_l_sm. Usa F_ON, F_PRP, frac_leach_h, EF5 (mismos que ec. 18)
# ------------------------------------------------------------

# ------------------------------------------------------------
# ECUACIÓN (20) – NH3 directo desde suelos gestionados
# Función: nh3_direct_sm. Usa resultados de ec. (17) y (19)
# ------------------------------------------------------------

# ------------------------------------------------------------
# ECUACIÓN (21) – NO3 directo desde suelos gestionados
# Función: no3_direct_sm. Usa resultados de ec. (17) y (19)
# ------------------------------------------------------------


# ------------------------------------------------------------
# ECUACIÓN (22) – N disponible desde la gestión del estiércol
# Función: n_mms_available
# ------------------------------------------------------------
N = 1          # número de cabezas
Nex = n_ex_fraction     # fraccion masica de N (kg N / kg muestra)
AWMS = 1        # adimensional
N_cdg = 0.0     # kg N año-1
frac_loss_m = EF3+frac_leach_ms+ frac_gas_ms +3*EF3 # adimensional    ##############################################################################################


# ------------------------------------------------------------
# ECUACIÓN (24) – Fracción de N perdido como N2 en MMS
# Función: frac_n2_ms
# ------------------------------------------------------------
R_N2_N2O = 3   # kg N2-N (kg N2O-N)-1
EF3 = EF3       # kg N2O-N kg-1 N


# ============================================================
# LLAMADAS A TODAS LAS FUNCIONES
# (asumiendo que las variables ya están definidas)
# ============================================================

# Ecuación (14)
N2O_N_inputs = n2o_n_inputs(
    F_ON=F_ON,
    EF1=EF1
)

# Ecuación (15)
F_ON_total = f_on(
    F_AM=F_AM,
    F_SEW=F_SEW,
    F_COMP=F_COMP,
    F_OOA=F_OOA
)

# Ecuación (16)
N2O_ATD_N = n2o_atd_n(
    F_ON=F_ON,
    F_PRP=F_PRP,
    frac_gasm=frac_gasm,
    EF4=EF4
)

# Ecuación (17)
N_ATD_sm = n_atd_sm(F_ON=F_ON, F_PRP=F_PRP, frac_gasm=frac_gasm, EF4=EF4)

# Ecuación (18)
N2O_L_N = n2o_l_n(
    F_ON=F_ON,
    F_PRP=F_PRP,
    frac_leach_h=frac_leach_h,
    EF5=EF5
)

# Ecuación (19)
N_L_sm = n_l_sm(F_ON=F_ON, F_PRP=F_PRP, frac_leach_h=frac_leach_h, EF5=EF5)

# Ecuación (20)
NH3_direct_sm = nh3_direct_sm(n_atd_sm=N_ATD_sm, n_l_sm=N_L_sm)

# Ecuación (21)
NO3_direct_sm = no3_direct_sm(n_atd_sm=N_ATD_sm, n_l_sm=N_L_sm)

# Ecuación (22)
N_MMS_Avb = n_mms_available(
    N=N,
    Nex=Nex,
    AWMS=AWMS,
    N_cdg=N_cdg,
    frac_loss_m=frac_loss_m
)

# Ecuación (24)
Frac_N2MS = frac_n2_ms(
    R_N2_N2O=R_N2_N2O,
    EF3=EF3
)

# Exportar a tabla común (SM: columnas MM en NaN; ec20/ec21 = NH3/NO3 direct sm)
fila = {
    "Escenario": "A",
    "Etapa": 4,
    "CH4_ec1": np.nan,
    "N2O_ec14": N2O_N_inputs,
    "N2O_ec2": np.nan,
    "N2O_ec5": np.nan,
    "N2O_ec6": np.nan,
    "N2O_ec16": N2O_ATD_N,
    "N2O_ec18": N2O_L_N,
    "NH3_ec12": np.nan,
    "NH3_ec20": NH3_direct_sm,
    "NO3_ec13": np.nan,
    "NO3_ec21": NO3_direct_sm,
}
exportar_fila("A", 4, fila)
