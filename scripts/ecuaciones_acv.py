"""Ecuaciones generales del ACV que permanecen fuera del ledger de N/TAN.

Las ecuaciones de nitrógeno reactivo residen exclusivamente en
``reactive_n_ledger.py``. Se retiraron de este módulo las funciones históricas
de reparto 50/50 y los precursores basados en FracGas para evitar dos rutas
productivas incompatibles.
"""

CH_4_eq = 21
N_2_O_eq = 310
NH_3_eq = 0.35
NO_3_eq = 0.095

FACTOR_N_A_N2O = 44 / 28
FACTOR_N_A_NH3 = 17 / 14
FACTOR_N_A_NO3 = 62 / 14


def ef_ch4(VS_T: float, B0_T: float, MCF: float, AWMS: float) -> float:
    """Calcula CH4 por kg de material manejado con el modelo IPCC vigente."""
    return VS_T * B0_T * 0.67 * (MCF / 100.0) * AWMS
