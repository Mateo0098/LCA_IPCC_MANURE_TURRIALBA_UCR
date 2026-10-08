"""Vista académica reproducible de la metodología vigente por etapa A1–B2.

El módulo organiza relaciones ya productivas; no calcula emisiones, masas ni
impactos. Las definiciones se contrastan con las fuentes estructuradas activas y
reutilizan la taxonomía de procedencia del inventario.
"""

from __future__ import annotations

import csv
from pathlib import Path

from inventory_data_provenance import ACADEMIC_PROVENANCE, build_provenance_rows


ROOT = Path(__file__).resolve().parents[1]
STAGES = {
    "A1": ("A", "A1: Precomposteo"),
    "A2": ("A", "A2: Lombricompostaje"),
    "A3": ("A", "A3: Almacenamiento de aguas verdes"),
    "A4": ("A", "A4: Aplicación de aguas verdes en campos de pastoreo"),
    "B1": ("B", "B1: Almacenamiento de purines"),
    "B2": ("B", "B2: Aplicación de purines en campo de pastoreo"),
}

SOURCES = {
    "parameters": ROOT / "processed/reactive_n_ledger_parameters.csv",
    "ledger": ROOT / "processed/reactive_n_ledger.csv",
    "masses": ROOT / "processed/masa_total_escenario_etapa.csv",
    "chemistry": ROOT / "processed/acv_parametros_escenario_etapa.csv",
    "systems": ROOT / "processed/ipcc_sistema_manejo_por_etapa.csv",
    "system_factors": ROOT / "processed/ipcc_sistemas_manejo_estiercol_factores.csv",
    "overrides": ROOT / "processed/ipcc_factores_manejo_overrides_etapa.csv",
    "operations": ROOT / "processed/acv_parametros_operativos.csv",
    "operational_inventory": ROOT / "processed/acv_inventario_recursos_operativos.csv",
    "imn": ROOT / "processed/acv_factores_imn_recursos_operativos.csv",
    "ef31": ROOT / "processed/acv_factores_equivalencia.csv",
    "mass_transformation": ROOT / "processed/muestreos_transformacion_masa_interjornada.csv",
}

CODE_SOURCES = {
    "MASS": "scripts/compute_masa_etapas_escenarios.py",
    "DRY": "scripts/acv_masa_seca.py",
    "CH4": "scripts/ecuaciones_acv.py; scripts/reactive_n_ledger.py",
    "N": "scripts/reactive_n_ledger.py",
    "OPS": "scripts/compute_operational_inventory.py",
    "IMN": "scripts/imn_operational_factors.py",
    "LCIA": "scripts/compute_acv_impact_equivalents.py",
}


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _row(
    code: str,
    phase: str,
    process: str,
    variable: str,
    equation_id: str,
    equation: str,
    activity: str,
    factor: str,
    provenance: str,
    source: str,
    output: str,
    responsible: str,
) -> dict[str, str]:
    scenario, stage = STAGES[code]
    return {
        "id_fila": f"{code}-{equation_id}",
        "escenario": scenario,
        "etapa": stage,
        "fase_metodologica": phase,
        "proceso_o_fenomeno_modelado": process,
        "variable_o_flujo_calculado": variable,
        "identificador_ecuacion": equation_id,
        "ecuacion_o_relacion_calculo": equation,
        "dato_actividad": activity,
        "parametro_o_factor": factor,
        "procedencia_dato_factor": provenance,
        "fuente_metodologica": source,
        "salida_o_uso_posterior": output,
        "fuente_responsable_interna": responsible,
    }


def build_detailed_rows() -> list[dict[str, str]]:
    """Construye la matriz detallada desde relaciones vigentes y verificables."""

    rows: list[dict[str, str]] = []
    add = rows.append
    primary_secondary = "Mixta: primaria y secundaria; tratamiento calculado o propagado"
    calculated_mixed = (
        "Mixta: primaria y secundaria; dato de actividad o reserva de N heredada de entradas primarias y secundarias, "
        "con factor metodológico secundario; tratamiento calculado"
    )

    # Datos de actividad y transformación de masa. Cada identificador representa
    # una relación distinta; las masas equivalentes de aplicación describen la
    # mezcla física y nunca inicializan ni escalan la reserva de N.
    mass_relations = {
        "A1": {
            "id": "M11", "variable": "Estiércol fresco recolectado", "equation": "m_A1 = m_recolectado",
            "activity": "Masa recolectada publicada para la misma lechería",
            "factor": "No aplica; uso directo del dato publicado",
            "provenance": "Secundaria; dato publicado del sitio",
            "source": "Sánchez-Romero y Brenes-Gamboa (2026)",
            "output": "Dato de actividad del inventario y masa de entrada a la transformación A1→A2",
        },
        "A2": {
            "id": "M12", "variable": "Masa húmeda inferida de precompostado",
            "equation": "m_A2 = m_A1 × promedio(R_j); R_j = (d_f,j × a_f,j)/(d_p,j × a_p,j)",
            "activity": "Masa A1 publicada y factor experimental integrado a partir de materia seca y cenizas de M1–M2",
            "factor": "Razón de transformación húmeda A1→A2 calculada primero por jornada y promediada con igual peso",
            "provenance": "Mixta: primaria y secundaria; factor de transformación primario y masa A1 secundaria; tratamiento calculado",
            "source": "Mediciones gravimétricas del TFG para el factor; Sánchez-Romero y Brenes-Gamboa (2026) para la masa A1",
            "output": "Masa húmeda inferida que ingresa a A2 y dato de actividad del inventario",
        },
        "A3": {
            "id": "M13", "variable": "Estiércol remanente arrastrable", "equation": "m_A3 = m_depositado − m_recolectado",
            "activity": "Masa recolectada publicada y masa depositada derivada del supuesto bibliográfico vigente",
            "factor": "Fracción recolectada derivada de datos publicados y supuesto con base bibliográfica",
            "provenance": "Secundaria; datos publicados y supuesto con base bibliográfica; tratamiento calculado",
            "source": "Sánchez-Romero y Brenes-Gamboa (2026)",
            "output": "Masa de estiércol de A3 usada para N, sólidos volátiles y CH₄; excluye agua de lavado",
        },
        "A4": {
            "id": "M14", "variable": "Masa equivalente total de aguas verdes",
            "equation": "m_eq,A4 = m_remanente + V_agua × 1 kg/L",
            "activity": "Estiércol remanente calculado y agua de lavado publicada",
            "factor": "Convención de equivalencia 1 kg/L para representar la mezcla física",
            "provenance": "Secundaria: componentes derivados de datos publicados y supuesto bibliográfico; No aplica: convención del estudio para 1 kg/L; tratamiento calculado",
            "source": "Sánchez-Romero y Brenes-Gamboa (2026); convención explícita de equivalencia de la mezcla",
            "output": "Representación de mezcla/dilución; no constituye nueva masa de N ni base de las ecuaciones de emisiones del suelo",
        },
        "B1": {
            "id": "M15", "variable": "Estiércol total teóricamente depositado", "equation": "m_B1 = m_recolectado / f_recolectada",
            "activity": "Masa recolectada publicada y fracción recolectada derivada del supuesto bibliográfico vigente",
            "factor": "Fracción recolectada derivada de datos publicados y supuesto con base bibliográfica",
            "provenance": "Secundaria; datos publicados y supuesto con base bibliográfica; tratamiento calculado",
            "source": "Sánchez-Romero y Brenes-Gamboa (2026)",
            "output": "Masa de estiércol de B1 usada para N, sólidos volátiles y CH₄; excluye agua de lavado",
        },
        "B2": {
            "id": "M16", "variable": "Masa equivalente total de purines",
            "equation": "m_eq,B2 = m_depositado + V_agua × 1 kg/L",
            "activity": "Estiércol total depositado calculado y agua de lavado publicada",
            "factor": "Convención de equivalencia 1 kg/L para representar la mezcla física",
            "provenance": "Secundaria: componentes derivados de datos publicados y supuesto bibliográfico; No aplica: convención del estudio para 1 kg/L; tratamiento calculado",
            "source": "Sánchez-Romero y Brenes-Gamboa (2026); convención explícita de equivalencia de la mezcla",
            "output": "Representación de mezcla/dilución; no constituye nueva masa de N ni base de las ecuaciones de emisiones del suelo",
        },
    }
    for code, relation in mass_relations.items():
        add(_row(code, "Construcción del dato de actividad", "Cuantificación del flujo anual de la etapa",
                 relation["variable"], relation["id"], relation["equation"], relation["activity"],
                 relation["factor"], relation["provenance"], relation["source"], relation["output"],
                 CODE_SOURCES["MASS"]))

    # Manejo: N/TAN, sólidos volátiles y emisiones.
    for code in ("A1", "A2", "A3", "B1"):
        fresh = code in {"A1", "A3", "B1"}
        add(_row(code, "Construcción del inventario", "Disponibilidad de sólidos volátiles en la masa húmeda",
                 "Fracción de sólidos volátiles en base húmeda", "M02",
                 "f_SV,húmeda = (%SV/100) × (%MS/100)", "Masa húmeda de estiércol de la etapa",
                 "Materia seca y sólidos volátiles integrados", "Primaria; mediciones experimentales M1–M2 integradas",
                 "Determinaciones gravimétricas de Bioenergía", "Entrada de la ecuación de CH₄", CODE_SOURCES["DRY"]))
        add(_row(code, "Generación del inventario", "Producción de metano durante el manejo",
                 "CH₄ biogénico", "E01", "m_CH4 = m_manejada × f_SV,húmeda × B₀ × ρ_CH4 × (MCF/100) × AWMS",
                 "Masa húmeda y fracción de sólidos volátiles de la etapa", "B₀; densidad de CH₄; MCF; AWMS",
                 primary_secondary, "IPCC 2019, volumen 4, capítulo 10", "Flujo elemental a aire para cambio climático EF 3.1",
                 CODE_SOURCES["CH4"]))
        if fresh:
            n_eq = "N_total,entrada = m_manejada × f_N,húmeda; TAN_entrada = 0,60 × N_total,entrada"
            n_activity = "Masa de estiércol fresco de la etapa y fracción másica de N integrada"
        else:
            n_eq = "N_total,entrada,A2 = N_total,salida,A1; TAN_entrada,A2 = TAN_salida,A1"
            n_activity = "N total y TAN propagados desde A1"
        n_id = "N01" if fresh else "N10"
        n_process = "Inicialización de N total y TAN frescos" if fresh else "Propagación interetapa de N total y TAN"
        add(_row(code, "Balance físico de nitrógeno", n_process,
                 "N total y TAN de entrada", n_id, n_eq, n_activity,
                 "TAN/N = 0,60 únicamente en fronteras frescas" if fresh else "Sin reinicialización con la medición intermedia",
                 primary_secondary, "EMEP/EEA 2023 y caracterización experimental activa",
                 "Base secuencial de emisiones nitrogenadas y balance de salida", CODE_SOURCES["N"]))
        if code in {"A3", "B1"}:
            add(_row(code, "Balance físico de nitrógeno", "Mineralización de N orgánico antes del almacenamiento líquido",
                     "TAN disponible", "N02", "N_mineralizado = (N_total − TAN_entrada) × f_min; TAN_disponible = TAN_entrada + N_mineralizado",
                     "N total y TAN de entrada", "f_min = 0,10", calculated_mixed, "EMEP/EEA 2023, capítulo 3.B, ecuación 32",
                     "Reserva de TAN sobre la que se estiman NH₃, NO y N₂", CODE_SOURCES["N"]))
        tan_base = "TAN disponible" if code in {"A3", "B1"} else "TAN de entrada"
        if code == "A2":
            add(_row(code, "Generación del inventario", "Volatilización de amoniaco en lombricompostaje", "NH₃ y NH₃-N", "N03K",
                     "m_NH3 = (m_A2/1000) × 12,8/1000; N_NH3 = m_NH3 × 14/17", "Masa húmeda inferida que ingresa a A2",
                     "12,8 g NH₃/Mg de residuo orgánico húmedo; cálculo independiente antes del descuento conjunto",
                     calculated_mixed, "Komakech et al. (2016)",
                     "Flujo elemental a aire; precursor explícito de N₂O indirecto; no reinicializa N/TAN", CODE_SOURCES["N"]))
        else:
            add(_row(code, "Generación del inventario", "Volatilización de amoniaco durante el manejo", "NH₃ y NH₃-N", "N03",
                     "N_NH3 = TAN_base × f_NH3; m_NH3 = N_NH3 × 17/14", tan_base,
                     ("Factor EMEP/EEA de almacenamiento sólido" if code == "A1" else "Factor EMEP/EEA de almacenamiento líquido")
                     + "; cálculo paralelo sobre la misma base de TAN antes del descuento conjunto",
                     calculated_mixed, "EMEP/EEA 2023, capítulo 3.B, tabla 3-9", "Flujo elemental a aire; precursor explícito de N₂O indirecto",
                     CODE_SOURCES["N"]))
        add(_row(code, "Generación del inventario", "Emisión de óxidos de nitrógeno durante el manejo", "NOx reportado como NO₂ y NOx-N", "N04",
                 "N_NOx = TAN_base × f_NO; m_NO2 = N_NOx × 46/14", tan_base,
                 "Factor EMEP/EEA de NO-N para almacenamiento sólido o líquido; cálculo paralelo sobre la misma base de TAN antes del descuento conjunto",
                 calculated_mixed,
                 "EMEP/EEA 2023, capítulo 3.B, tabla 3-10", "Flujo elemental a aire; precursor explícito de N₂O indirecto", CODE_SOURCES["N"]))
        add(_row(code, "Balance físico de nitrógeno", "Pérdida de nitrógeno molecular durante el manejo", "N₂-N", "N05",
                 "N_N2 = TAN_base × f_N2", tan_base,
                 "Factor EMEP/EEA de N₂-N para almacenamiento sólido o líquido; cálculo paralelo sobre la misma base de TAN antes del descuento conjunto",
                 calculated_mixed, "EMEP/EEA 2023, capítulo 3.B, tabla 3-10",
                 "Pérdida física descontada junto con NH₃-N y NO-N; sin factor de caracterización actual", CODE_SOURCES["N"]))
        add(_row(code, "Generación del inventario", "Formación directa de óxido nitroso durante el manejo", "N₂O directo", "N06",
                 "m_N2O,directo = N_total,entrada × EF3 × 44/28", "N total de entrada de la etapa",
                 "EF3 = 0 del sistema líquido vigente; produce cero en el modelo, sin afirmar imposibilidad física" if code in {"A3", "B1"} else "EF3 del sistema de manejo asignado",
                 calculated_mixed, "IPCC 2019, volumen 4, capítulo 10, tabla 10.21",
                 "N₂O directo igual a cero en el modelo vigente; no implica ausencia física universal" if code in {"A3", "B1"} else "Flujo elemental a aire para cambio climático EF 3.1",
                 CODE_SOURCES["N"]))
        add(_row(code, "Generación del inventario", "Formación indirecta de N₂O por deposición atmosférica", "N₂O indirecto por volatilización", "N07",
                 "m_N2O,ind,vol = (N_NH3 + N_NOx) × EF4 × 44/28", "NH₃-N y NOx-N explícitos de la etapa", "EF4 = 0,014",
                 calculated_mixed, "IPCC 2019, volumen 4, capítulo 11, tabla 11.3", "Flujo elemental a aire para cambio climático EF 3.1", CODE_SOURCES["N"]))

    # Ruta hídrica específica de A1.
    add(_row("A1", "Generación del inventario", "Pérdida hídrica de N estimada durante el manejo", "N perdido por la ruta hídrica modelada", "N08",
             "N_water_loss = N_total,entrada × FracLeachMS", "N total de entrada en A1", "FracLeachMS = 0,04", calculated_mixed,
             "IPCC 2019, volumen 4, capítulo 10, tabla 10.22",
             "Pérdida hídrica modelada que, por la frontera metodológica aprobada, se trata después como entrada a la ruta de suelo; no produce directamente NO₃⁻",
             CODE_SOURCES["N"]))
    add(_row("A1", "Generación del inventario", "Ruta posterior de lixiviación o escorrentía en el suelo", "N lixiviado, NO₃⁻ y N₂O indirecto", "N09",
             "N_lix = N_water_loss × FracLEACH; m_NO3 = N_lix × 62/14; m_N2O,ind,lix = N_lix × EF5 × 44/28",
             "Pérdida hídrica A1 tratada como entrada al suelo según la frontera aprobada",
             "FracLEACH = 0,24; conversión 62/14; EF5 = 0,011", calculated_mixed,
             "IPCC 2019, volumen 4, capítulo 11, tabla 11.3", "NO₃⁻ a agua dulce y N₂O a aire para caracterización EF 3.1", CODE_SOURCES["N"]))

    # Aplicación al suelo.
    for code, previous in (("A4", "A3"), ("B2", "B1")):
        add(_row(code, "Balance físico de nitrógeno", "Propagación desde el almacenamiento hacia la aplicación", "N total y TAN aplicados", "N10",
                 f"N_aplicado,{code} = N_salida,{previous}; TAN_aplicado,{code} = TAN_salida,{previous}",
                 f"Salida de N total y TAN de {previous}", "Sin reinicialización con la medición líquida", primary_secondary,
                 "Balance secuencial vigente de N total y TAN", "Base de las rutas de aplicación al suelo", CODE_SOURCES["N"]))
        add(_row(code, "Generación del inventario", "Volatilización de amoniaco durante la aplicación", "NH₃ y NH₃-N", "N11",
                 "N_NH3,aplic = TAN_aplicado × f_NH3,aplic; m_NH3 = N_NH3 × 17/14", "TAN aplicado propagado",
                 "0,55 kg NH₃-N/kg TAN", calculated_mixed, "EMEP/EEA 2023, capítulo 3.B, tabla 3-9",
                 "Flujo elemental a aire; precursor explícito de N₂O indirecto", CODE_SOURCES["N"]))
        add(_row(code, "Generación del inventario", "Emisión de óxidos de nitrógeno durante la aplicación", "NOx reportado como NO₂ y NOx-N", "N12",
                 "m_NO2 = N_aplicado × 0,04; N_NOx = m_NO2 × 14/46", "N total aplicado propagado", "0,04 kg NO₂/kg N aplicado", calculated_mixed,
                 "EMEP/EEA 2023, capítulo 3.D, tabla 3-1", "Flujo elemental a aire; precursor explícito de N₂O indirecto", CODE_SOURCES["N"]))
        add(_row(code, "Generación del inventario", "Formación directa de N₂O en suelo", "N₂O directo", "N13",
                 "m_N2O,directo = N_aplicado × EF1 × 44/28", "N total aplicado propagado", "EF1 = 0,006", calculated_mixed,
                 "IPCC 2019, volumen 4, capítulo 11, tabla 11.1", "Flujo elemental a aire para cambio climático EF 3.1", CODE_SOURCES["N"]))
        add(_row(code, "Generación del inventario", "Formación indirecta de N₂O por deposición atmosférica", "N₂O indirecto por volatilización", "N14",
                 "m_N2O,ind,vol = (N_NH3 + N_NOx) × EF4 × 44/28", "NH₃-N y NOx-N explícitos de la aplicación", "EF4 = 0,014", calculated_mixed,
                 "IPCC 2019, volumen 4, capítulo 11, tabla 11.3", "Flujo elemental a aire para cambio climático EF 3.1", CODE_SOURCES["N"]))
        add(_row(code, "Generación del inventario", "Lixiviación o escorrentía desde el suelo", "N lixiviado y NO₃⁻", "N15",
                 "N_lix = N_aplicado × FracLEACH; m_NO3 = N_lix × 62/14", "N total aplicado propagado", "FracLEACH = 0,24", calculated_mixed,
                 "IPCC 2019, volumen 4, capítulo 11, tabla 11.3", "NO₃⁻ a agua dulce para eutrofización marina EF 3.1", CODE_SOURCES["N"]))
        add(_row(code, "Generación del inventario", "Formación indirecta de N₂O por lixiviación o escorrentía", "N₂O indirecto por lixiviación", "N16",
                 "m_N2O,ind,lix = N_lix × EF5 × 44/28", "N lixiviado o escurrido", "EF5 = 0,011", calculated_mixed,
                 "IPCC 2019, volumen 4, capítulo 11, tabla 11.3", "Flujo elemental a aire para cambio climático EF 3.1", CODE_SOURCES["N"]))

    # Recursos operativos.
    for code in ("A3", "B1"):
        add(_row(code, "Inventario operativo", "Bombeo del agua pluvial de lavado", "Consumo eléctrico y contribución climática agregada", "O01",
                 "E = (P_mec/η) × (365/d_ciclo) × n_lavados × (t_lavado/60); CC_elec = E × FE_IMN",
                 "Potencia de placa y operación observada/comunicada; eficiencia supuesta; anualización",
                 "η = 0,80 como supuesto del estudio; factor agregado IMN de consumo eléctrico 2025",
                 "Primaria: placa, tiempos y frecuencias; No aplica: supuesto del estudio para η = 0,80; Secundaria: factor IMN; tratamiento calculado y anualizado",
                 "Placa y registro de campo; supuesto explícito del estudio; IMN (2026)",
                 "Contribución agregada de cambio climático; no es una emisión elemental EF 3.1", f"{CODE_SOURCES['OPS']}; {CODE_SOURCES['IMN']}"))
    for code in ("A4", "B2"):
        add(_row(code, "Inventario operativo", "Combustión de diésel en tractor y cañón", "Diésel; CO₂ fósil, CH₄ fósil y N₂O", "O02",
                 "V_diesel = (365/d_ciclo) × (t_operación/60) × q_diesel; m_i = V_diesel × FE_IMN,i",
                 "Frecuencia y duración operativa comunicadas; consumo de 3 L/h supuesto; anualización",
                 "q_diesel = 3 L/h como supuesto del estudio; factores físicos IMN para CO₂, CH₄ y N₂O",
                 "Primaria: frecuencia y duración comunicadas; No aplica: supuesto del estudio para 3 L/h; Secundaria: factores IMN; tratamiento calculado y anualizado",
                 "Registro de campo; supuesto explícito del estudio; IMN (2026)",
                 "Flujos elementales fósiles para caracterización climática EF 3.1", f"{CODE_SOURCES['OPS']}; {CODE_SOURCES['IMN']}"))

    # Caracterización separada del inventario.
    characterization = {
        "A1": {
            "equation": "I_c = Σ_i (m_i × CF_i,c), i ∈ {CH₄, N₂O, NH₃, NOx, NO₃⁻}",
            "activity": "Emisiones elementales de CH₄, N₂O, NH₃, NOx y NO₃⁻ generadas en A1",
            "factor": "Factores EF 3.1 por identidad, compartimento y categoría",
            "source": "Environmental Footprint 3.1 de la Comisión Europea y el JRC",
            "provenance": "Mixta: primaria y secundaria; inventario con procedencia heredada y factores EF 3.1 secundarios; tratamiento calculado",
            "output": "Cambio climático, eutrofización terrestre y eutrofización marina de A1",
        },
        "A2": {
            "equation": "I_c = Σ_i (m_i × CF_i,c), i ∈ {CH₄, N₂O, NH₃, NOx}",
            "activity": "Emisiones elementales de CH₄, N₂O, NH₃ y NOx generadas en A2; sin recursos operativos",
            "factor": "Factores EF 3.1 por identidad, compartimento y categoría",
            "source": "Environmental Footprint 3.1 de la Comisión Europea y el JRC",
            "provenance": "Mixta: primaria y secundaria; inventario con procedencia heredada y factores EF 3.1 secundarios; tratamiento calculado",
            "output": "Cambio climático, eutrofización terrestre y eutrofización marina de A2",
        },
        "A3": {
            "equation": "I_c = Σ_i (m_i × CF_i,c) + 1_(c=CC) × (E × FE_IMN,elec)",
            "activity": "Emisiones elementales de CH₄, N₂O, NH₃ y NOx de A3; electricidad anual como actividad separada",
            "factor": "EF 3.1 para emisiones elementales; factor eléctrico agregado IMN aplicado directamente a cambio climático",
            "source": "Environmental Footprint 3.1 de la Comisión Europea y el JRC; IMN (2026) para electricidad agregada",
            "provenance": "Mixta: primaria y secundaria; inventario con procedencia heredada y factores EF 3.1 e IMN secundarios; tratamiento calculado",
            "output": "Indicadores de A3; electricidad sumada directamente a cambio climático, fuera de Σ(m_i × CF_i,c)",
        },
        "A4": {
            "equation": "I_c = Σ_i (m_i × CF_i,c), i ∈ {N₂O, NH₃, NOx, NO₃⁻, CO₂ fósil, CH₄ fósil, N₂O de combustión}; los tres flujos fósiles se obtienen primero con IMN",
            "activity": "Emisiones elementales de suelo y emisiones físicas de CO₂ fósil, CH₄ fósil y N₂O de combustión del diésel",
            "factor": "Factores físicos IMN para obtener emisiones del diésel; factores EF 3.1 para caracterizarlas",
            "source": "IMN (2026) para emisiones físicas del diésel; Environmental Footprint 3.1 para caracterización",
            "provenance": "Mixta: primaria y secundaria; inventario con procedencia heredada, factores físicos IMN y factores EF 3.1 secundarios; tratamiento calculado",
            "output": "Indicadores de A4; ruta del diésel IMN → emisiones físicas → EF 3.1",
        },
        "B1": {
            "equation": "I_c = Σ_i (m_i × CF_i,c) + 1_(c=CC) × (E × FE_IMN,elec)",
            "activity": "Emisiones elementales de CH₄, N₂O, NH₃ y NOx de B1; electricidad anual como actividad separada",
            "factor": "EF 3.1 para emisiones elementales; factor eléctrico agregado IMN aplicado directamente a cambio climático",
            "source": "Environmental Footprint 3.1 de la Comisión Europea y el JRC; IMN (2026) para electricidad agregada",
            "provenance": "Mixta: primaria y secundaria; inventario con procedencia heredada y factores EF 3.1 e IMN secundarios; tratamiento calculado",
            "output": "Indicadores de B1; electricidad sumada directamente a cambio climático, fuera de Σ(m_i × CF_i,c)",
        },
        "B2": {
            "equation": "I_c = Σ_i (m_i × CF_i,c), i ∈ {N₂O, NH₃, NOx, NO₃⁻, CO₂ fósil, CH₄ fósil, N₂O de combustión}; los tres flujos fósiles se obtienen primero con IMN",
            "activity": "Emisiones elementales de suelo y emisiones físicas de CO₂ fósil, CH₄ fósil y N₂O de combustión del diésel",
            "factor": "Factores físicos IMN para obtener emisiones del diésel; factores EF 3.1 para caracterizarlas",
            "source": "IMN (2026) para emisiones físicas del diésel; Environmental Footprint 3.1 para caracterización",
            "provenance": "Mixta: primaria y secundaria; inventario con procedencia heredada, factores físicos IMN y factores EF 3.1 secundarios; tratamiento calculado",
            "output": "Indicadores de B2; ruta del diésel IMN → emisiones físicas → EF 3.1",
        },
    }
    for code, relation in characterization.items():
        add(_row(code, "Caracterización de impactos", "Conversión de flujos elementales en indicadores ambientales",
                 "Cambio climático, eutrofización terrestre y eutrofización marina", "C01",
                 relation["equation"], relation["activity"], relation["factor"],
                 relation["provenance"],
                 relation["source"], relation["output"], CODE_SOURCES["LCIA"]))

    validate_detailed_rows(rows)
    return rows


def build_summary_rows(detailed_rows: list[dict[str, str]] | None = None) -> list[dict[str, str]]:
    rows = detailed_rows or build_detailed_rows()
    by_stage = {code: [row for row in rows if row["etapa"].startswith(code + ":")] for code in STAGES}
    summaries = {
        "A1": (
            "Precomposteo pasivo; transformación inicial de la corriente sólida; pérdida hídrica modelada y ruta posterior de suelo",
            "Estiércol fresco recolectado; N total, TAN, materia seca y sólidos volátiles",
            "IPCC para CH₄, N₂O y pérdida hídrica; EMEP/EEA para NH₃, NO y N₂; EF 3.1 para caracterización",
            "Masa inferida hacia A2; emisiones; pérdida hídrica tratada después en suelo para NO₃⁻ y N₂O indirecto",
        ),
        "A2": (
            "Lombricompostaje del material precompostado", "Masa húmeda inferida de entrada; N total y TAN propagados desde A1; materia seca y sólidos volátiles",
            "IPCC para CH₄ y N₂O; Komakech para NH₃; EMEP/EEA para NO y N₂; EF 3.1 para caracterización",
            "Emisiones de A2 y balance final de la corriente sólida",
        ),
        "A3": (
            "Almacenamiento de aguas verdes en tanqueta; ruta de N₂O directo evaluada con EF3 vigente igual a cero",
            "Estiércol remanente; N total y TAN frescos; electricidad de bombeo",
            "IPCC y EMEP/EEA para almacenamiento; EF 3.1 para emisiones; factor agregado IMN para electricidad",
            "N total y TAN hacia A4; emisiones de manejo; N₂O directo igual a cero en el modelo y contribución eléctrica agregada",
        ),
        "A4": (
            "Aplicación de aguas verdes en campos de pastoreo",
            "N total y TAN propagados desde A3; masa equivalente solo como mezcla/dilución, no como base de N; diésel",
            "EMEP/EEA e IPCC para suelo; IMN → emisiones físicas del diésel → EF 3.1",
            "Emisiones al aire y agua; indicadores por etapa",
        ),
        "B1": (
            "Almacenamiento de purines en tanqueta; ruta de N₂O directo evaluada con EF3 vigente igual a cero",
            "Estiércol total depositado; N total y TAN frescos; electricidad de bombeo",
            "IPCC y EMEP/EEA para almacenamiento; EF 3.1 para emisiones; factor agregado IMN para electricidad",
            "N total y TAN hacia B2; emisiones de manejo; N₂O directo igual a cero en el modelo y contribución eléctrica agregada",
        ),
        "B2": (
            "Aplicación de purines en campo de pastoreo",
            "N total y TAN propagados desde B1; masa equivalente solo como mezcla/dilución, no como base de N; diésel",
            "EMEP/EEA e IPCC para suelo; IMN → emisiones físicas del diésel → EF 3.1",
            "Emisiones al aire y agua; indicadores por etapa",
        ),
    }
    result = []
    for code, (processes, activity, frameworks, outputs) in summaries.items():
        result.append({
            "escenario": STAGES[code][0],
            "etapa": STAGES[code][1],
            "procesos_principales": processes,
            "datos_actividad": activity,
            "marcos_fuentes_metodologicas": frameworks,
            "salidas_principales": outputs,
            "filas_detalladas": str(len(by_stage[code])),
        })
    assert sum(int(row["filas_detalladas"]) for row in result) == len(rows)
    summary_by_stage = {row["etapa"][:2]: row for row in result}
    assert "pérdida hídrica" in summary_by_stage["A1"]["procesos_principales"]
    assert "ruta posterior" in summary_by_stage["A1"]["procesos_principales"]
    assert "masa húmeda inferida de entrada" in summary_by_stage["A2"]["datos_actividad"].casefold()
    for code in ("A3", "B1"):
        joined = " ".join(summary_by_stage[code].values())
        assert "EF3 vigente igual a cero" in joined
        assert "factor agregado IMN" in joined
    for code in ("A4", "B2"):
        joined = " ".join(summary_by_stage[code].values())
        assert "no como base de N" in joined
        assert "IMN → emisiones físicas del diésel → EF 3.1" in joined
    return result


def validate_detailed_rows(rows: list[dict[str, str]]) -> None:
    missing = [path.relative_to(ROOT).as_posix() for path in SOURCES.values() if not path.exists()]
    assert not missing, f"Faltan fuentes canónicas: {missing}"
    assert {row["etapa"][:2] for row in rows} == set(STAGES)
    assert len({row["id_fila"] for row in rows}) == len(rows)
    required = {
        "fase_metodologica", "proceso_o_fenomeno_modelado", "variable_o_flujo_calculado",
        "ecuacion_o_relacion_calculo", "dato_actividad", "parametro_o_factor",
        "procedencia_dato_factor", "fuente_metodologica", "salida_o_uso_posterior",
    }
    assert all(all(row[column].strip() for column in required) for row in rows)
    assert all(any(row["etapa"].startswith(code + ":") for row in rows) for code in STAGES)
    assert not any("M3" in " ".join(row.values()) for row in rows)
    assert not any("EF 3.1" in row["fase_metodologica"] and row["fase_metodologica"] != "Caracterización de impactos" for row in rows)
    assert all("Environmental Footprint 3.1" in row["fuente_metodologica"] for row in rows if row["fase_metodologica"] == "Caracterización de impactos")
    assert all("IPCC" not in row["fuente_metodologica"] or "EMEP" not in row["parametro_o_factor"] for row in rows)

    by_key = {(row["etapa"][:2], row["identificador_ecuacion"]): row for row in rows}
    expected_mass_ids = {
        "A1": "M11", "A2": "M12", "A3": "M13", "A4": "M14", "B1": "M15", "B2": "M16",
    }
    assert all((code, equation_id) in by_key for code, equation_id in expected_mass_ids.items())
    assert not any(row["identificador_ecuacion"] == "M01" for row in rows)
    assert len(set(expected_mass_ids.values())) == len(expected_mass_ids)
    assert all((code, "N01") in by_key for code in ("A1", "A3", "B1"))
    assert ("A2", "N01") not in by_key and ("A2", "N10") in by_key
    assert all((code, "N10") in by_key for code in ("A2", "A4", "B2"))

    for code in ("A4", "B2"):
        mass_row = by_key[(code, expected_mass_ids[code])]
        assert "no constituye nueva masa de N" in mass_row["salida_o_uso_posterior"]
        assert "base de las ecuaciones de emisiones del suelo" in mass_row["salida_o_uso_posterior"]

    n08 = by_key[("A1", "N08")]
    n09 = by_key[("A1", "N09")]
    assert "pérdida hídrica" in " ".join(n08.values()).casefold()
    assert "frontera metodológica aprobada" in n08["salida_o_uso_posterior"].casefold()
    assert "no produce directamente no₃" in n08["salida_o_uso_posterior"].casefold()
    assert "drenaje" not in " ".join(n08.values()).casefold()
    assert all(token in n09["ecuacion_o_relacion_calculo"] for token in ("FracLEACH", "62/14", "EF5"))

    calculated_n_ids = {"N02", "N03", "N03K", "N04", "N05", "N06", "N07", "N08", "N09", "N11", "N12", "N13", "N14", "N15", "N16"}
    calculated_n_rows = [row for row in rows if row["identificador_ecuacion"] in calculated_n_ids]
    assert calculated_n_rows and all("Mixta: primaria y secundaria" in row["procedencia_dato_factor"] for row in calculated_n_rows)
    for code in ("A3", "B1"):
        n06 = by_key[(code, "N06")]
        assert "EF3 = 0" in n06["parametro_o_factor"]
        assert "sin afirmar imposibilidad física" in n06["parametro_o_factor"]

    management_parallel_ids = {"N03", "N04", "N05"}
    assert all(
        "misma base de TAN antes del descuento conjunto" in row["parametro_o_factor"]
        for row in rows if row["identificador_ecuacion"] in management_parallel_ids
    )
    assert "cálculo independiente antes del descuento conjunto" in by_key[("A2", "N03K")]["parametro_o_factor"]

    forbidden_provenance = "Mixta: primaria, supuesto del estudio y secundaria"
    assert not any(forbidden_provenance in row["procedencia_dato_factor"] for row in rows)
    for code in ("A3", "B1"):
        operational = by_key[(code, "O01")]
        assert all(token in operational["procedencia_dato_factor"] for token in ("Primaria:", "No aplica: supuesto del estudio", "Secundaria:"))
        assert "no es una emisión elemental EF 3.1" in operational["salida_o_uso_posterior"]
    for code in ("A4", "B2"):
        operational = by_key[(code, "O02")]
        assert all(token in operational["procedencia_dato_factor"] for token in ("Primaria:", "No aplica: supuesto del estudio", "Secundaria:"))
        assert "Flujos elementales fósiles" in operational["salida_o_uso_posterior"]

    for code in STAGES:
        c01 = by_key[(code, "C01")]
        assert "Mixta: primaria y secundaria" in c01["procedencia_dato_factor"]
    for code in ("A3", "B1"):
        c01 = by_key[(code, "C01")]
        assert "E × FE_IMN,elec" in c01["ecuacion_o_relacion_calculo"]
        assert "fuera de Σ(m_i × CF_i,c)" in c01["salida_o_uso_posterior"]
    for code in ("A4", "B2"):
        c01 = by_key[(code, "C01")]
        assert "flujos fósiles se obtienen primero con IMN" in c01["ecuacion_o_relacion_calculo"]
        assert "IMN → emisiones físicas → EF 3.1" in c01["salida_o_uso_posterior"]

    ledger_parameters = {row["parameter"] for row in _read(SOURCES["parameters"])}
    expected_parameters = {
        "fresh_manure_tan_fraction", "emep_solid_nh3_n_fraction_tan", "emep_solid_no_n_fraction_tan",
        "emep_solid_n2_n_fraction_tan", "emep_slurry_mineralisation_fraction", "emep_slurry_nh3_n_fraction_tan",
        "emep_slurry_no_n_fraction_tan", "emep_slurry_n2_n_fraction_tan", "emep_application_nh3_n_fraction_tan",
        "emep_soil_no2_fraction_n_applied", "ef4_ipcc", "ef5_ipcc", "soil_frac_leach", "soil_ef1",
        "komakech_nh3_factor", "dairy_b0_m3_ch4_per_kg_vs", "ch4_density_kg_per_m3", "awms_assigned_stream_fraction",
    }
    assert expected_parameters <= ledger_parameters
    assert len(_read(SOURCES["ledger"])) == 6
    assert len(_read(SOURCES["masses"])) == 6
    assert len(_read(SOURCES["systems"])) == 6
    assert all(path.exists() for path in (ROOT / value for value in CODE_SOURCES.values() for value in value.split("; ")))
    signatures = {
        "scripts/ecuaciones_acv.py": ("return VS_T * B0_T",),
        "scripts/reactive_n_ledger.py": (
            "tan_available = tan_in + mineralised_n",
            "indirect_vol_n = precursor * ef4",
            "leach_n = n_applic * p[\"soil_frac_leach\"]",
        ),
        "scripts/compute_masa_etapas_escenarios.py": (
            "params.estiercol_recolectado_anual * factor_a2",
            "masa_base = boniga_base + agua_base",
        ),
        "scripts/compute_operational_inventory.py": (
            "pump_input_kw = parameters[\"pump_mechanical_power_kw\"]",
            "diesel = tractor_hours * parameters[\"tractor_diesel_l_per_hour\"]",
        ),
        "scripts/compute_acv_impact_equivalents.py": (
            "out[\"impacto_calentamiento_global_kg_co2eq\"]",
            "out[\"impacto_eutrofizacion_marina_kg_neq\"]",
        ),
    }
    for relative, expected in signatures.items():
        source = (ROOT / relative).read_text(encoding="utf-8")
        assert all(signature in source for signature in expected), f"Cambió la fuente responsable: {relative}"

    provenance_rows = build_provenance_rows()
    labels = {row["procedencia_academica"] for row in provenance_rows}
    assert labels <= ACADEMIC_PROVENANCE


def academic_columns() -> list[str]:
    return [
        "escenario", "etapa", "fase_metodologica", "proceso_o_fenomeno_modelado",
        "variable_o_flujo_calculado", "identificador_ecuacion", "ecuacion_o_relacion_calculo",
        "dato_actividad", "parametro_o_factor", "procedencia_dato_factor",
        "fuente_metodologica", "salida_o_uso_posterior",
    ]


def main() -> None:
    detailed = build_detailed_rows()
    summary = build_summary_rows(detailed)
    counts = {
        code: sum(row["etapa"].startswith(code + ":") for row in detailed)
        for code in STAGES
    }
    print(
        "Trazabilidad metodológica PASS: "
        f"{len(summary)} etapas; {len(detailed)} relaciones; cobertura={counts}"
    )


if __name__ == "__main__":
    main()
