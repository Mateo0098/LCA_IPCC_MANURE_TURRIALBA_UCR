"""
Módulo de ecuaciones ACV (Análisis de Ciclo de Vida) para emisiones de ganadería.
Variables globales y funciones correspondientes a las ecuaciones IPCC documentadas
en el notebook ACV_ecuaciones_referencia.ipynb.
"""

# Factores de equivalencia (conversiones 9, 10, 11 en documento)
CH_4_eq = 21
N_2_O_eq = 310
NH_3_eq = 0.35
NO_3_eq = 0.095

# Factores de conversion de kg N a kg de compuesto emitido
FACTOR_N_A_N2O = 44 / 28
FACTOR_N_A_NH3 = 17 / 14
# Conversión estequiométrica de N a NO₃⁻.
FACTOR_N_A_NO3 = 4.4268


# Ecuación (1)
def ef_ch4(VS_T, B0_T, MCF, AWMS):
    """
    Calcula el factor de emisión anual de CH4 para una única categoría T,
    un sistema S y una región climática k.

    Parámetros
    ----------
    VS_T : float
        Sólidos volátiles diarios excretados (kg MS animal-1 día-1)
    B0_T : float
        Capacidad máxima de producción de metano (m3 CH4 kg-1 SV)
    MCF : float
        Factor de conversión de metano (%)
    AWMS : float
        Fracción de estiércol manejado por el sistema AWMS (adimensional)

    Retorna
    -------
    float
        EF_T : kg CH4 animal-1 año-1
    """
    return (VS_T ) * (B0_T * 0.67 * (MCF / 100) * AWMS) # se quito (VS_T *365 )


# Ecuación (2)
def n2o_direct_mm(N, Nex, AWMS, N_cdg, EF3):
    """
    Calcula las emisiones directas de N2O provenientes de la gestión del estiércol
    para un único T, S y P.

    Parámetros
    ----------
    N : float
        Número de cabezas de ganado
    Nex : float
        Excreción media anual de N por cabeza (kg N animal-1 año-1)
    AWMS : float
        Fracción de la excreción total anual de N manejada en el sistema AWMS
    N_cdg : float
        Aporte anual de nitrógeno vía codigestación (kg N año-1)
    EF3 : float
        Factor de emisión de N2O-N del sistema de gestión de estiércol (kg N2O-N / kg N)

    Retorna
    -------
    float
        N2O_D(mm) : kg N2O año-1
    """
    return ((N * Nex) * AWMS + N_cdg) * EF3 * FACTOR_N_A_N2O


# Ecuación (3)
def n_volatilization_mms(N, Nex, AWMS, N_cdg, frac_gas_ms):
    """
    Calcula el nitrógeno volatilizado desde la gestión del estiércol (MMS)
    para un único T, S y P.

    Parámetros
    ----------
    N : float
        Número de cabezas de ganado
    Nex : float
        Excreción media anual de N por cabeza (kg N animal-1 año-1)
    AWMS : float
        Fracción de la excreción total anual de N manejada en el sistema AWMS
    N_cdg : float
        Aporte anual de nitrógeno vía codigestación (kg N año-1)
    frac_gas_ms : float
        Fracción del N que se volatiliza en el sistema de gestión de estiércol

    Retorna
    -------
    float
        N_volatilization_MMS : kg N año-1
    """
    return ((N * Nex) * AWMS + N_cdg) * frac_gas_ms


# Ecuación (4)
def n_lixiviado_mms(N, N_ex, AWMS, N_cdg, frac_leach_ms):
    """
    Calcula la lixiviación asociada a MMS para un único S, T y P.

    Parámetros
    ----------
    N : float
        Número de unidades (antes N_(T,P))
    N_ex : float
        Excreción/emisión de N por unidad
    AWMS : float
        Fracción del sistema de manejo de residuos
    N_cdg : float
        Aporte adicional de N dependiente del escenario
    frac_leach_ms : float
        Fracción de lixiviación del MMS

    Retorna
    -------
    float
        L_leaching_MMS
    """
    return (N * N_ex * AWMS + N_cdg) * frac_leach_ms


# Ecuación (5)
def n2o_indirect_volatilization(N_volatilization_mms, EF4):
    """
    Calcula las emisiones indirectas de N2O debidas a la volatilización
    de N proveniente de la gestión del estiércol.

    Parámetros
    ----------
    N_volatilization_mms : float
        Nitrógeno volatilizado desde la gestión del estiércol (kg N año-1)
    EF4 : float
        Factor de emisión de N2O-N por deposición atmosférica
        (kg N2O-N / (kg NH3-N + NOx-N volatilizado))

    Retorna
    -------
    float
        N2O_G(mm) : kg N2O año-1
    """
    return N_volatilization_mms * EF4 * FACTOR_N_A_N2O


# Ecuación (6)
def n2o_indirect_leaching(N_leaching_mms, EF5):
    """
    Calcula las emisiones indirectas de N2O debidas a la lixiviación
    proveniente de la gestión del estiércol.

    Parámetros
    ----------
    N_leaching_mms : float
        Nitrógeno lixiviado desde la gestión del estiércol (kg N año-1)
    EF5 : float
        Factor de emisión de N2O-N por lixiviación
        (kg N2O-N / kg N lixiviado)

    Retorna
    -------
    float
        N2O_L(mm) : kg N2O año-1
    """
    return N_leaching_mms * EF5 * FACTOR_N_A_N2O


# Ecuación (7)
def n_indirect_volatilization(N_volatilization_mms, EF4):
    """
    Calcula las emisiones indirectas de N2O debidas a la volatilización
    de N proveniente de la gestión del estiércol.

    Parámetros
    ----------
    N_volatilization_mms : float
        Nitrógeno volatilizado desde la gestión del estiércol (kg N año-1)
    EF4 : float
        Factor de emisión de N2O-N por deposición atmosférica
        (kg N2O-N / (kg NH3-N + NOx-N volatilizado))

    Retorna
    -------
    float
        N_G(mm) : kg N año-1
    """
    return N_volatilization_mms * (1 - EF4)


# Ecuación (8)
def n_indirect_leaching(N_leaching_mms, EF5):
    """
    Calcula las emisiones indirectas de N2O debidas a la lixiviación
    proveniente de la gestión del estiércol.

    Parámetros
    ----------
    N_leaching_mms : float
        Nitrógeno lixiviado desde la gestión del estiércol (kg N año-1)
    EF5 : float
        Factor de emisión de N2O-N por lixiviación
        (kg N2O-N / kg N lixiviado)

    Retorna
    -------
    float
        N_L(mm) : kg N año-1
    """
    return N_leaching_mms * (1 - EF5)


# Ecuación (12)
def nh3_direct_mm(n_indirect_volatilization, n_indirect_leaching):
    """
    Calcula las emisiones irectas de NH3 debidas a la lixiviación y volatilizacion
    proveniente de la gestión del estiércol.

    Parámetros
    ----------
    N_G(mm) : kg N año-1
        Nitrógeno volatilizado desde la gestión del estiércol (kg N año-1) float
    N_L(mm) : kg N año-1
        Nitrógeno lixiviado desde la gestión del estiércol (kg N año-1) float
    Retorna
    -------
    float
        nh3_direct_mm : kg NH3 año-1
    """
    return ((n_indirect_volatilization + n_indirect_leaching) / 2) * FACTOR_N_A_NH3


# Ecuación (13)
def no3_direct_mm(n_indirect_volatilization, n_indirect_leaching):
    """
    Calcula las emisiones directas de NO3 debidas a la lixiviación y volatilizacion
    proveniente de la gestión del estiércol.

    Parámetros
    ----------
     N_G(mm) : kg N año-1
        Nitrógeno volatilizado desde la gestión del estiércol (kg N año-1) float
     N_L(mm) : kg N año-1
        Nitrógeno lixiviado desde la gestión del estiércol (kg N año-1) float

    Retorna
    -------
    float
        no3_direct_mm : kg NO3 año-1
    """
    return ((n_indirect_volatilization + n_indirect_leaching) / 2) * FACTOR_N_A_NO3


# Ecuación (14)
def n2o_n_inputs(F_ON, EF1):
    """
    Calcula las emisiones directas anuales de N2O–N producidas por suelos gestionados
    a partir de entradas de fertilizante orgánico.

    Parámetros
    ----------
    F_ON : float
        Cantidad anual total de fertilizante orgánico nitrogenado aplicado
        (kg N año-1)
    EF1 : float
        Factor de emisión de N2O–N por entradas de N
        (kg N2O–N / kg N de entrada)

    Retorna
    -------
    float
        N2O-N_inputs : kg N2O–N año-1
    """
    return F_ON * EF1 * FACTOR_N_A_N2O


# Ecuación (15)
def f_on(F_AM, F_SEW, F_COMP, F_OOA):
    """
    Calcula la cantidad anual total de fertilizante orgánico nitrogenado
    aplicado a los suelos.

    Parámetros
    ----------
    F_AM : float
        Cantidad anual de N de estiércol animal aplicado al suelo (kg N año-1)
    F_SEW : float
        Cantidad anual de N total de aguas residuales aplicada a los suelos (kg N año-1)
    F_COMP : float
        Cantidad anual de N total de compost aplicado a los suelos (kg N año-1)
    F_OOA : float
        Cantidad anual de otras enmiendas orgánicas aplicadas como fertilizantes (kg N año-1)

    Retorna
    -------
    float
        F_ON : kg N año-1
    """
    return F_AM + F_SEW + F_COMP + F_OOA


# Ecuación (16)
def n2o_atd_n(F_ON, F_PRP, frac_gasm, EF4):
    """
    Calcula la cantidad anual de N2O–N producida a partir de la deposición
    atmosférica de N volatilizado de suelos gestionados.

    Parámetros
    ----------
    F_ON : float
        Cantidad anual total de fertilizante orgánico nitrogenado aplicado a suelos (kg N año-1)
    F_PRP : float
        Cantidad anual de N en orina y estiércol depositado por animales de pastoreo (kg N año-1)
    frac_gasm : float
        Fracción del N aplicado o depositado que se volatiliza como NH3 y NOx
    EF4 : float
        Factor de emisión de N2O–N por deposición atmosférica
        (kg N2O–N / (kg NH3–N + NOx–N volatilizado))

    Retorna
    -------
    float
        N2O_(ATD)-N : kg N2O–N año-1
    """
    return (F_ON + F_PRP) * frac_gasm * EF4 * FACTOR_N_A_N2O


# Ecuación (17)
def n_atd_sm(F_ON, F_PRP, frac_gasm, EF4):
    """
    Calcula la cantidad anual de N producida a partir de la deposición
    atmosférica de N volatilizado de suelos gestionados.

    Parámetros
    ----------
    F_ON : float
        Cantidad anual total de fertilizante orgánico nitrogenado aplicado a suelos (kg N año-1)
    F_PRP : float
        Cantidad anual de N en orina y estiércol depositado por animales de pastoreo (kg N año-1)
    frac_gasm : float
        Fracción del N aplicado o depositado que se volatiliza como NH3 y NOx
    EF4 : float
        Factor de emisión de N2O–N por deposición atmosférica
        (kg N2O–N / (kg NH3–N + NOx–N volatilizado))

    Retorna
    -------
    float
        n_atd_sm : kg N2 año-1
    """
    return (F_ON + F_PRP) * frac_gasm * (1 - EF4)


# Ecuación (18)
def n2o_l_n(F_ON, F_PRP, frac_leach_h, EF5):
    """
    Calcula la cantidad anual de N2O–N producida por lixiviación y escorrentía
    de N desde suelos gestionados.

    Parámetros
    ----------
    F_ON : float
        Cantidad anual de estiércol animal N aplicada a los suelos (kg N año-1)
    F_PRP : float
        Cantidad anual de N en orina y estiércol depositado por animales de pastoreo (kg N año-1)
    frac_leach_h : float
        Fracción del N añadido/mineralizado que se pierde por lixiviación y escorrentía
    EF5 : float
        Factor de emisión de N2O–N por lixiviación y escorrentía
        (kg N2O–N / kg N lixiviado/escurrido)

    Retorna
    -------
    float
        N2O_(L)-N : kg N2O–N año-1
    """
    return (F_ON + F_PRP) * frac_leach_h * EF5 * FACTOR_N_A_N2O


# Ecuación (19)
def n_l_sm(F_ON, F_PRP, frac_leach_h, EF5):
    """
    Calcula la cantidad anual de N producida por lixiviación y escorrentía
    de N desde suelos gestionados.

    Parámetros
    ----------
    F_ON : float
        Cantidad anual de estiércol animal N aplicada a los suelos (kg N año-1)
    F_PRP : float
        Cantidad anual de N en orina y estiércol depositado por animales de pastoreo (kg N año-1)
    frac_leach_h : float
        Fracción del N añadido/mineralizado que se pierde por lixiviación y escorrentía
    EF5 : float
        Factor de emisión de N2O–N por lixiviación y escorrentía
        (kg N2O–N / kg N lixiviado/escurrido)

    Retorna
    -------
    float
        n_l_sm : kg N año-1
    """
    return (F_ON + F_PRP) * frac_leach_h * (1 - EF5)


# Ecuación (20)
def nh3_direct_sm(n_atd_sm, n_l_sm):
    """
    Calcula las emisiones irectas de N3 debidas a la lixiviación y ATD
    proveniente desde suelos gestionado.

    Parámetros
    ----------
    n_atd_sm : kg N año-1
        Nitrógeno depositado en atmosfera desde la gestión de suelo (kg N año-1) float
    n_l_sm : kg N año-1
        Nitrógeno lixiviado desde la gestión de suelo (kg N año-1) float
    Retorna
    -------
    float
        nh3_direct_sm : kg NH3 año-1
    """
    return ((n_atd_sm + n_l_sm) / 2) * FACTOR_N_A_NH3


# Ecuación (21)
def no3_direct_sm(n_atd_sm, n_l_sm):
    """
    Calcula las emisiones irectas de N3 debidas a la lixiviación y ATD
    proveniente desde suelos gestionado.

    Parámetros
    ----------
    n_atd_sm : kg N año-1
        Nitrógeno depositado en atmosfera desde la gestión de suelo (kg N año-1) float
    n_l_sm : kg N año-1
        Nitrógeno lixiviado desde la gestión de suelo (kg N año-1) float
    Retorna
    -------
    float
        no3_direct_sm : kg NO3 año-1
    """
    return ((n_atd_sm + n_l_sm) / 2) * FACTOR_N_A_NO3


# Ecuación (22)
def n_mms_available(N, Nex, AWMS, N_cdg, frac_loss_m):
    """
    Calcula la cantidad de N disponible para la aplicación en suelos
    proveniente de la gestión del estiércol.

    Parámetros
    ----------
    N : float
        Número de cabezas de ganado
    Nex : float
        Excreción media anual de N por cabeza (kg N animal-1 año-1)
    AWMS : float
        Fracción del N excretado manejado en el sistema de gestión de estiércol
    N_cdg : float
        Aporte anual de nitrógeno vía codigestación (kg N año-1)
    frac_loss_m : float
        Fracción de pérdidas de N en el sistema de gestión de estiércol

    Retorna
    -------
    float
        N_MMS_Avb : kg N año-1
    """
    return (N * Nex * AWMS + N_cdg) * (1 - frac_loss_m)


# Ecuación (23)
def frac_loss_ms(frac_gas_ms, frac_leach_ms, frac_n2_ms, EF3):
    """
    Calcula la fracción total de nitrógeno perdido en el sistema
    de gestión de estiércol (MMS) para una categoría de ganado (T)
    y sistema de gestión (S).

    Parámetros
    ----------
    frac_gas_ms : float
        Fracción de N perdido como NH3 y NOx en el sistema MMS (adimensional)
    frac_leach_ms : float
        Fracción de N perdido por lixiviación en el sistema MMS (adimensional)
    frac_n2_ms : float
        Fracción de N perdido como N2 en el sistema MMS (adimensional)
    EF3 : float
        Factor de emisión de N2O-N del sistema MMS,
        kg N2O-N (kg N)-1 (adimensional en términos fraccionales)

    Retorna
    -------
    float
        FRAC_LOSS_MS : fracción total de N perdido en el sistema MMS (adimensional)
    """
    return frac_gas_ms + frac_leach_ms + frac_n2_ms + EF3


# Ecuación (24)
def frac_n2_ms(R_N2_N2O, EF3):
    """
    Calcula la fracción de nitrógeno del estiércol gestionado que se pierde como N2
    en el sistema de gestión del estiércol.

    Parámetros
    ----------
    R_N2_N2O : float
        Relación de emisiones N2 : N2O (kg N2-N / kg N2O-N)
    EF3 : float
        Factor de emisión de N2O-N del sistema de gestión de estiércol
        (kg N2O-N / kg N)

    Retorna
    -------
    float
        Frac_N2MS : fracción adimensional
    """
    return R_N2_N2O * EF3
