from __future__ import annotations

import re


ACADEMIC_LABELS = {
    "B2: Aplicación en campo": "B2: Aplicación de purines en campo de pastoreo",
    "dry_lot": "Sistema de manejo en corral seco",
    "uncovered_anaerobic_lagoon": "Laguna anaerobia descubierta",
    "composting_invessel": "Compostaje en sistema cerrado",
    "solid_storage": "Almacenamiento sólido",
    "liquid_slurry": "Sistema líquido tipo purín",
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
    "Factor hardcodeado auditado": "Factor metodológico pendiente de referencia",
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


def clean_academic_label(value: object) -> str:
    text = clean_annual_units(repair_mojibake(str(value)))
    for internal, academic in sorted(
        ACADEMIC_LABELS.items(), key=lambda item: len(item[0]), reverse=True
    ):
        text = text.replace(internal, academic)
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
    for plain, scientific in (
        ("CH4", "CH₄"),
        ("N2O", "N₂O"),
        ("NH3", "NH₃"),
        ("NO3", "NO₃⁻"),
        ("CO2", "CO₂"),
        ("PO4", "PO₄"),
    ):
        text = text.replace(plain, scientific)
    return text
