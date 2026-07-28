from __future__ import annotations

import re


ACADEMIC_LABELS = {
    "B2: Aplicación en campo": "B2: Aplicación de purines en campo de pastoreo",
    "uncovered anaerobic lagoon": "Laguna anaerobia descubierta",
    "dry_lot": "Sistema de manejo en corral seco",
    "dry lot": "Sistema de manejo en corral seco",
    "uncovered_anaerobic_lagoon": "Laguna anaerobia descubierta",
    "in-vessel composting": "Compostaje en sistema cerrado",
    "composting_invessel": "Compostaje en sistema cerrado",
    "solid storage": "Almacenamiento sólido",
    "solid_storage": "Almacenamiento sólido",
    "liquid slurry": "Sistema líquido tipo purín",
    "liquid_slurry": "Sistema líquido tipo purín",
    "aerobic treatment": "Tratamiento aeróbico",
    "aerobic_treatment": "Tratamiento aeróbico",
    "composting_intensive": "Compostaje intensivo",
    "composting_pasive": "Compostaje pasivo",
    "modelo_calculo": "Modelo de estimación",
    "sistema_manejo_ipcc": "Sistema de manejo asignado",
    "masa_total_kg_eq": "Masa equivalente total",
    "n_ex_pct": "N total reportado (%)",
    "n_ex_fraction": "Fracción másica de N",
    "tipo_factor": "Tipo de factor",
    "sistema_o_compuesto": "Sistema o compuesto evaluado",
    "definicion": "Definición",
    "resultado_total": "Resultado total",
    "escenario_A": "Escenario A",
    "escenario_B": "Escenario B",
    "diferencia_absoluta_B_menos_A": "Diferencia absoluta B − A",
    "diferencia_porcentual_B_vs_A": "Diferencia porcentual B respecto a A",
    "escenario_con_mayor_impacto": "Escenario con mayor impacto",
    "fuente_dato": "Fuente metodológica",
    "Factor hardcodeado auditado": "Parámetro complementario",
    "referencia_metodologica": "Referencia metodológica",
    "clasificacion_referencia": "Clasificación de la referencia",
    "estado_referencia": "Estado de la referencia",
    "impact category": "Categoría de impacto",
    "stage name": "Etapa del sistema",
    "factor type": "Tipo de factor",
    "total result": "Resultado total",
    "absolute difference": "Diferencia absoluta",
    "percentage difference": "Diferencia porcentual",
    "highest impact scenario": "Escenario con mayor impacto",
    "global warming": "Calentamiento global",
    "eutrophication": "Eutrofización",
    "fresh manure": "Estiércol fresco",
    "precomposted manure": "Estiércol precompostado",
    "green waters": "Aguas verdes",
    "green water": "Aguas verdes",
    "wash water": "Agua de lavado",
    "pasture field application": "Aplicación en campo de pastoreo",
    "field application": "Aplicación en campo",
    "slurries": "Purines",
    "slurry": "Purín",
    "dry matter": "Materia seca",
    "volatile solids": "Sólidos volátiles",
    "organic carbon": "Carbono orgánico",
    "emissions": "Emisiones estimadas",
    "emission": "Emisión estimada",
    "measured": "Factor medido",
    "calculated": "Calculado",
    "substance": "Sustancia",
    "compound": "Compuesto",
    "scenario": "Escenario",
    "category": "Categoría",
    "source": "Fuente",
    "units": "Unidades",
    "unit": "Unidad",
    "value": "Valor",
    "stage": "Etapa del sistema",
    "annual": "Anual",
    "average": "Promedio",
    "fraction": "Fracción",
    "moisture": "Humedad",
    "nitrogen": "Nitrógeno",
    "manure": "Estiércol",
    "dung": "Boñiga",
    "ash": "Cenizas",
}


def repair_mojibake(value: str) -> str:
    markers = ("\u00c3", "\u00c2", "\u00e2\u20ac", "\ufffd")
    if any(marker in value for marker in markers):
        for encoding in ("cp1252", "latin1"):
            try:
                return value.encode(encoding).decode("utf-8")
            except UnicodeError:
                continue
    return value


def clean_annual_units(value: object) -> str:
    """Corrige referencias temporales anuales sin alterar palabras mayores."""
    text = str(value)
    text = re.sub(r"/ano\b", "/año", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(por|al|cada)\s+ano\b", r"\1 año", text, flags=re.IGNORECASE)
    return text


def clean_chemical_notation(value: object) -> str:
    """Normaliza fórmulas químicas visibles sin alterar identificadores mayores."""
    text = str(value)
    replacements = (
        (r"(?<![\w₀-₉])PO4-eq(?![\w₀-₉])", "PO₄-eq"),
        (r"(?<![\w₀-₉])CO2-eq(?![\w₀-₉])", "CO₂-eq"),
        (r"(?<![\w₀-₉])PO4(?:\^?3-|³-)(?![\w₀-₉])", "PO₄³⁻"),
        (r"(?<![\w₀-₉])N2O-N(?![\w₀-₉])", "N₂O-N"),
        (r"(?<![\w₀-₉])NH3-N(?![\w₀-₉])", "NH₃-N"),
        (r"(?<![\w₀-₉])NO3-N(?![\w₀-₉])", "NO₃-N"),
        (r"(?<![\w₀-₉])CH4(?![\w₀-₉])", "CH₄"),
        (r"(?<![\w₀-₉])N2O(?![\w₀-₉])", "N₂O"),
        (r"(?<![\w₀-₉])NH3(?![\w₀-₉])", "NH₃"),
        (r"(?<![\w₀-₉])NO3-?(?![\w₀-₉])", "NO₃⁻"),
        (r"(?<![\w₀-₉])CO2(?![\w₀-₉])", "CO₂"),
        (r"(?<![\w₀-₉])PO4(?![\w₀-₉])", "PO₄³⁻"),
    )
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def clean_academic_label(value: object) -> str:
    text = clean_annual_units(repair_mojibake(str(value)))
    for internal, academic in sorted(
        ACADEMIC_LABELS.items(), key=lambda item: len(item[0]), reverse=True
    ):
        text = re.sub(
            rf"(?<![\w]){re.escape(internal)}(?![\w])",
            lambda _match, replacement=academic: replacement,
            text,
            flags=re.IGNORECASE,
        )
    if "_" in text:
        text = re.sub(r"_+", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("Sístema", "Sistema")
    text = text.replace("N total reportado (%) (%)", "N total reportado (%)")
    text = text.replace("Nitrogeno", "Nitrógeno")
    text = text.replace("Solidos", "Sólidos")
    text = text.replace("volatiles", "volátiles")
    text = text.replace("humeda", "húmeda")
    text = text.replace("Eutrofizacion", "Eutrofización")
    text = text.replace("categoria impacto", "Categoría de impacto")
    return clean_chemical_notation(text)
