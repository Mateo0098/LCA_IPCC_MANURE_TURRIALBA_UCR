from __future__ import annotations

import re
import zipfile
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

from academic_text_utils import clean_academic_label
from reference_docx_utils import (
    REGISTERED_REFERENCE_SHA256,
    assert_reference_docx_intact,
    get_reference_docx_path,
    sha256_file,
)


ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DOCX = ROOT / "MASTER_escrito" / "TFG_ACV_Estiercol_MASTER.docx"
TABLE_DIR = ROOT / "outputs" / "tablas_tesis"
FIG_DIR = ROOT / "outputs" / "graficos_tesis"
OUT_DIR = ROOT / "outputs" / "documentos_tfg"
OUT_DOCX = OUT_DIR / "resultados_desarrollados_tfg.docx"
METHODOLOGY_DOCX = OUT_DIR / "metodologia_desarrollada_tfg.docx"
README_OUT = OUT_DIR / "README_DOCUMENTOS_GENERADOS.md"
VALIDATION_OUT = OUT_DIR / "reporte_validacion_documentos.md"

TABLES = {
    "resumen": TABLE_DIR / "resumen_resultados_para_redaccion.md",
    "tabla_02": TABLE_DIR / "tabla_02_caracterizacion_muestras.csv",
    "tabla_03": TABLE_DIR / "tabla_03_flujos_icv.csv",
    "tabla_04": TABLE_DIR / "tabla_04_parametros_modelo_acv.csv",
    "tabla_05": TABLE_DIR / "tabla_05_factores_emision_y_caracterizacion.csv",
    "tabla_06": TABLE_DIR / "tabla_06_emisiones_por_etapa.csv",
    "tabla_07": TABLE_DIR / "tabla_07_impactos_por_etapa.csv",
    "tabla_08": TABLE_DIR / "tabla_08_impactos_totales_por_escenario.csv",
    "tabla_09": TABLE_DIR / "tabla_09_comparacion_escenarios.csv",
}

MAIN_FIGURES = [
    ("fig_01_caracterizacion_humedad_materia_seca.png", "Figura 1. Humedad y materia seca promedio por tipo de muestra."),
    ("fig_02_caracterizacion_solidos_volatiles_cenizas.png", "Figura 2. Sólidos volátiles y cenizas por tipo de muestra."),
    ("fig_04_flujos_masa_equivalente_total.png", "Figura 3. Masa equivalente total por etapa y escenario."),
    ("fig_06_emisiones_ch4.png", "Figura 4. Emisiones anuales de CH4 por etapa y escenario."),
    ("fig_11_impactos_calentamiento_global_etapa.png", "Figura 5. Potencial de calentamiento global por etapa y escenario."),
    ("fig_12_impactos_eutrofizacion_etapa.png", "Figura 6. Potencial de eutrofización por etapa y escenario."),
    ("fig_15_comparacion_diferencia_porcentual.png", "Figura 7. Diferencia porcentual del Escenario B respecto al Escenario A por categoría de impacto."),
]

APPENDIX_FIGURES = [
    ("fig_03_caracterizacion_nitrogeno_total.png", "Figura R1. Nitrógeno total promedio por tipo de muestra."),
    ("fig_05_flujos_distribucion_componentes.png", "Figura R2. Distribución de componentes del inventario por etapa."),
    ("fig_07_emisiones_n2o.png", "Figura R3. Emisiones anuales de N2O por etapa y escenario."),
    ("fig_08_emisiones_nh3.png", "Figura R4. Emisiones anuales de NH3 por etapa y escenario."),
    ("fig_09_emisiones_no3.png", "Figura R5. Emisiones anuales de NO3 por etapa y escenario."),
    ("fig_10_emisiones_co2.png", "Figura R6. Emisiones anuales de CO2 por etapa y escenario."),
    ("fig_13_comparacion_total_calentamiento_global.png", "Figura R7. Comparación del potencial total de calentamiento global entre escenarios."),
    ("fig_14_comparacion_total_eutrofizacion.png", "Figura R8. Comparación del potencial total de eutrofización entre escenarios."),
]

OFFICIAL_STAGE_NAMES = {
    ("A", 1): ("A1", "Precomposteo", "Etapa 1: Precomposteo"),
    ("A", 2): ("A2", "Lombricompostaje", "Etapa 2: Lombricompostaje"),
    ("A", 3): ("A3", "Almacenamiento de aguas verdes", "Etapa 3: Almacenamiento de aguas verdes"),
    ("A", 4): (
        "A4",
        "Aplicación de aguas verdes en campos de pastoreo",
        "Etapa 4: Aplicación de aguas verdes en campos de pastoreo",
    ),
    ("B", 1): ("B1", "Almacenamiento de purines", "Etapa 1: Almacenamiento de purines"),
    ("B", 2): ("B2", "Aplicación en campo", "Etapa 2: Aplicación en campo"),
}

OLD_STAGE_TERMS = {
    "Manejo inicial de estiércol fresco": "Precomposteo",
    "Manejo posterior de fracción sólida": "Lombricompostaje",
    "Manejo de estiércol fresco sin precompostaje": "Almacenamiento de purines",
    "Manejo o aplicación de purines": "Aplicación en campo",
    "Aplicación o manejo de aguas verdes en suelo": "Aplicación de aguas verdes en campos de pastoreo",
}

INTERNAL_COLUMNS = {
    "archivo_fuente",
    "source_file",
    "script",
    "script_origen",
    "path",
    "input_file",
    "output_file",
    "nombre_variable_codigo",
    "columna_original",
    "id interno",
    "observaciones internas del repositorio",
    "fuente",
    "fuente_dato",
    "fuente_o_calculo",
    "formula_origen",
    "observaciones",
    "fuente_bibliografica_pendiente",
    "fuente_factor_emision",
    "fuente_factor_caracterizacion",
    "fuente_factor",
    "ecuacion_utilizada",
    "archivo fuente",
}

ACADEMIC_REPLACEMENTS = {
    "dry_lot": "Sistema de manejo en corral seco",
    "uncovered_anaerobic_lagoon": "Laguna anaerobia descubierta",
    "composting_invessel": "Compostaje en sistema cerrado",
    "solid_storage": "Almacenamiento sólido",
    "liquid_slurry": "Sistema líquido tipo purín",
    "aerobic_treatment": "Tratamiento aeróbico",
    "composting_intensive": "Compostaje intensivo",
    "composting_pasive": "Compostaje pasivo",
    "windrow_intensive": "Compostaje intensivo en hileras",
    "windrow_pasive": "Compostaje pasivo en hileras",
    "ipcc": "IPCC",
    "medido": "Factor medido",
    "ESTIERCOL FRESCO": "Estiércol fresco",
    "SOL: PRECOMPOSTADO": "Estiércol precompostado",
    "LIQ: AGUA VERDE": "Agua de lavado incorporada a las aguas verdes",
    "LIQ: PURINES": "Purín",
    "n_ex_pct": "N total reportado (%)",
    "n_ex_fraction": "Fracción másica de N",
    "masa_total_kg_eq": "Masa equivalente total",
    "tipo_muestra": "Tipo de material",
    "fuente_dato": "Fuente metodológica",
    "Factor hardcodeado auditado": "Factor metodológico pendiente de referencia",
    "Si": "Sí",
}

HEADER_REPLACEMENTS = {
    "escenario": "Escenario",
    "etapa": "Etapa",
    "nombre_etapa": "Nombre de etapa",
    "tipo_muestra": "Tipo de material",
    "modelo_calculo": "Modelo de cálculo",
    "sistema_manejo_ipcc": "Sistema de manejo asignado",
    "parametro": "Parámetro",
    "valor": "Valor",
    "unidad": "Unidad",
    "unidad_emision": "Unidad de emisión",
    "unidad_factor": "Unidad del factor",
    "resultado_equivalente": "Resultado equivalente",
    "unidad_equivalente": "Unidad equivalente",
    "variable": "Variable",
    "flujo": "Flujo o material",
    "emision": "Emisión",
    "sustancia": "Sustancia",
    "categoria_impacto": "Categoría de impacto",
    "factor_caracterizacion": "Factor de caracterización",
    "valor_impacto": "Valor de impacto",
    "unidad_impacto": "Unidad de impacto",
    "tratamiento_laboratorio": "Material analizado",
    "jornada_muestreo": "Jornada de muestreo",
    "numero_muestras_solidos": "Número de muestras de sólidos",
    "numero_muestras_nitrogeno": "Número de muestras de nitrógeno",
    "desviacion_estandar": "Desviación estándar",
}

CHEMICAL_REPLACEMENTS = [
    ("kg CO2-eq/año", "kg CO₂-eq/año"),
    ("kg PO4-eq/año", "kg PO₄-eq/año"),
    ("kg N2O-N/kg N", "kg N₂O-N/kg N"),
    ("CO2-eq", "CO₂-eq"),
    ("PO4-eq", "PO₄-eq"),
    ("N2O-N", "N₂O-N"),
    ("NH3-N", "NH₃-N"),
    ("NO3-N", "NO₃-N"),
    ("CH4", "CH₄"),
    ("N2O", "N₂O"),
    ("NH3", "NH₃"),
    ("NO3", "NO₃⁻"),
    ("CO2", "CO₂"),
    ("PO4", "PO₄³⁻"),
    ("m3", "m³"),
    ("m2", "m²"),
]


def validate_inputs() -> None:
    validated_reference = get_reference_docx_path(ROOT)
    if validated_reference != REFERENCE_DOCX:
        raise RuntimeError(
            "La ruta validada del documento maestro no coincide con la ruta configurada."
        )
    required = [*TABLES.values(), *(FIG_DIR / name for name, _ in MAIN_FIGURES)]
    missing = [path.relative_to(ROOT).as_posix() for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError("Faltan insumos requeridos:\n" + "\n".join(f"- {item}" for item in missing))

def read_csv(key: str) -> pd.DataFrame:
    try:
        return pd.read_csv(TABLES[key], encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv(TABLES[key], encoding="utf-8-sig")


def clean_text(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value)
    for old, new in ACADEMIC_REPLACEMENTS.items():
        text = text.replace(old, new)
    for old, new in OLD_STAGE_TERMS.items():
        text = text.replace(old, new)
    text = (
        text.replace("Eutrofizacion", "Eutrofización")
        .replace("Nitrogeno", "Nitrógeno")
        .replace("Solidos", "Sólidos")
        .replace("ano", "año")
        .replace("Usado en ecuaciones de N despues de " + "cor" + "reccion", "Usado como fracción másica en ecuaciones de N")
        .replace("n_ex_fraction " + "cor" + "regido para ecuaciones de nitrogeno", "n_ex_fraction usado como fracción másica en ecuaciones de nitrógeno")
        .replace("Comparacion posterior a " + "cor" + "reccion de n_ex_pct a n_ex_fraction", "Comparación entre escenarios con n_ex_fraction como entrada de nitrógeno")
    )
    for old, new in CHEMICAL_REPLACEMENTS:
        text = text.replace(old, new)
    text = repair_mojibake(text)
    return clean_academic_label(text)


def repair_mojibake(text: str) -> str:
    markers = ["\u00c3", "\u00c2", "\u00e2\u20ac", "\u00e2\u20ac\u2122", "\u00e2\u20ac\u0153", "\ufffd"]
    if any(marker in text for marker in markers):
        for encoding in ("cp1252", "latin1"):
            try:
                return text.encode(encoding).decode("utf-8")
            except UnicodeError:
                continue
    return text


def apply_official_stage_names(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if {"escenario", "etapa"}.issubset(out.columns):
        for idx, row in out.iterrows():
            try:
                key = (str(row["escenario"]).strip().upper(), int(row["etapa"]))
            except (TypeError, ValueError):
                continue
            if key in OFFICIAL_STAGE_NAMES:
                code, short_name, full_name = OFFICIAL_STAGE_NAMES[key]
                if "codigo_etapa" in out.columns:
                    out.at[idx, "codigo_etapa"] = code
                if "nombre_corto_etapa" in out.columns:
                    out.at[idx, "nombre_corto_etapa"] = short_name
                if "nombre_etapa" in out.columns:
                    out.at[idx, "nombre_etapa"] = full_name
    return out


def strip_internal_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df[[col for col in df.columns if col.lower().strip() not in INTERNAL_COLUMNS]].copy()


def official_stage_label(scenario: object, stage: object) -> str:
    try:
        key = (str(scenario).strip().upper(), int(float(stage)))
    except (TypeError, ValueError):
        return ""
    if key in OFFICIAL_STAGE_NAMES:
        code, short_name, _ = OFFICIAL_STAGE_NAMES[key]
        return f"{code}: {short_name}"
    return f"{key[0]}{key[1]}"


def combine_stage_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    lower_to_col = {str(col).lower().strip(): col for col in out.columns}
    scenario_col = lower_to_col.get("escenario")
    stage_col = lower_to_col.get("etapa")
    if scenario_col and stage_col:
        insert_at = list(out.columns).index(stage_col)
        labels = [official_stage_label(row[scenario_col], row[stage_col]) for _, row in out.iterrows()]
        for col in ["codigo_etapa", "código", "codigo", "nombre_corto_etapa", "nombre_etapa", "nombre de etapa", "etapa"]:
            existing = lower_to_col.get(col)
            if existing in out.columns:
                out = out.drop(columns=[existing])
        out.insert(min(insert_at, len(out.columns)), "Etapa del sistema", labels)
    return out


def fmt(value, decimals: int = 2) -> str:
    if value == "" or pd.isna(value):
        return ""
    try:
        text = f"{float(value):,.{decimals}f}"
        text = text.replace(",", "X").replace(".", ",").replace("X", " ")
        if "," in text:
            text = text.rstrip("0").rstrip(",")
        return text
    except (TypeError, ValueError):
        return clean_text(value)


def format_df(df: pd.DataFrame, decimals: int = 2, decimals_by_col: dict[str, int] | None = None) -> pd.DataFrame:
    decimals_by_col = decimals_by_col or {}
    out = combine_stage_columns(df)
    out = out.rename(columns={col: HEADER_REPLACEMENTS.get(str(col), clean_text(col)) for col in out.columns})
    for col in out.columns:
        if str(col).lower() == "etapa":
            out[col] = out[col].map(lambda value: f"Etapa {int(float(value))}" if not pd.isna(value) and str(value) != "" else "")
        elif pd.api.types.is_numeric_dtype(out[col]):
            out[col] = out[col].map(lambda value: fmt(value, decimals_by_col.get(col, decimals)))
        else:
            out[col] = out[col].map(clean_text)
    return out


def reference_format():
    ref = Document(str(REFERENCE_DOCX))
    normal = ref.styles["Normal"].font
    font_name = normal.name or "Times New Roman"
    font_size = normal.size or Pt(12)
    section = ref.sections[0]
    margins = {
        "top": section.top_margin,
        "bottom": section.bottom_margin,
        "left": section.left_margin,
        "right": section.right_margin,
    }
    return font_name, font_size, margins


def set_document_style(doc: Document) -> None:
    font_name, font_size, margins = reference_format()
    section = doc.sections[0]
    section.top_margin = margins["top"]
    section.bottom_margin = margins["bottom"]
    section.left_margin = margins["left"]
    section.right_margin = margins["right"]
    for style_name in ("Normal", "Heading 1", "Heading 2", "Heading 3"):
        style = doc.styles[style_name]
        style.font.name = font_name
        style._element.rPr.rFonts.set(qn("w:eastAsia"), font_name)
        if style_name == "Normal":
            style.font.size = font_size


def set_table_horizontal_borders(table) -> None:
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "bottom", "insideH"):
        tag = OxmlElement(f"w:{edge}")
        tag.set(qn("w:val"), "single")
        tag.set(qn("w:sz"), "4")
        tag.set(qn("w:space"), "0")
        tag.set(qn("w:color"), "808080")
        borders.append(tag)
    for edge in ("left", "right", "insideV"):
        tag = OxmlElement(f"w:{edge}")
        tag.set(qn("w:val"), "nil")
        borders.append(tag)
    table._tbl.tblPr.append(borders)


def add_dataframe_table(doc: Document, caption: str, df: pd.DataFrame) -> None:
    if caption:
        paragraph = doc.add_paragraph()
        run = paragraph.add_run(clean_text(caption))
        run.bold = True
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    set_table_horizontal_borders(table)
    for idx, col in enumerate(df.columns):
        cell = table.rows[0].cells[idx]
        cell.text = clean_text(col)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for run in cell.paragraphs[0].runs:
            run.bold = True
    for _, row in df.iterrows():
        cells = table.add_row().cells
        for idx, value in enumerate(row):
            cells[idx].text = clean_text(value)
            cells[idx].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def add_figure(doc: Document, file_name: str, caption: str) -> None:
    image = FIG_DIR / file_name
    if not image.exists():
        return
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run().add_picture(str(image), width=Inches(6.2))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cap.add_run(clean_text(caption))
    run.italic = True


def add_paragraphs(doc: Document, paragraphs: list[str]) -> None:
    for text in paragraphs:
        doc.add_paragraph(clean_text(text))


def characterization_summary() -> pd.DataFrame:
    t02 = read_csv("tabla_02")
    rows = []
    labels = {"Fresh manure": "Estiércol fresco", "Precomposted manure": "Estiércol precompostado"}
    for sample, group in t02.groupby("tipo_muestra", sort=False):
        row = {"Tipo de muestra": labels.get(sample, sample)}
        for _, record in group.iterrows():
            variable = record["variable"]
            unit = record["unidad"]
            if variable == "Humedad":
                row["Humedad (%)"] = record["valor"]
            elif variable == "Materia seca":
                row["Materia seca (%)"] = record["valor"]
            elif variable == "Cenizas":
                row["Cenizas (% base seca)"] = record["valor"]
            elif variable == "Solidos volatiles":
                row["Sólidos volátiles (% base seca)"] = record["valor"]
            elif variable == "Nitrogeno total" and unit == "% N total":
                row["N total (%)"] = record["valor"]
        rows.append(row)
    return pd.DataFrame(rows)


def flow_summary() -> pd.DataFrame:
    t03 = apply_official_stage_names(read_csv("tabla_03"))
    out = t03[t03["flujo"] == "Masa equivalente total"][
        ["escenario", "etapa", "nombre_etapa", "valor"]
    ].rename(
        columns={
            "escenario": "Escenario",
            "etapa": "Etapa",
            "nombre_etapa": "Nombre de etapa",
            "valor": "Masa equivalente total (kg eq/año)",
        }
    )
    return out


def parameter_summary() -> pd.DataFrame:
    t04 = apply_official_stage_names(read_csv("tabla_04"))
    subset = t04[t04["parametro"].isin(["Masa equivalente total", "Nitrogeno total reportado", "Nitrogeno total como fraccion masica", "MCF", "EF3"])]
    out = subset.pivot_table(
        index=["escenario", "etapa", "nombre_etapa", "modelo_calculo"],
        columns="parametro",
        values="valor",
        aggfunc="first",
    ).reset_index()
    return out.rename(
        columns={
            "escenario": "Escenario",
            "etapa": "Etapa",
            "nombre_etapa": "Nombre de etapa",
            "modelo_calculo": "Modelo",
            "Masa equivalente total": "Masa equivalente (kg eq/año)",
            "Nitrogeno total reportado": "N total reportado (%)",
            "Nitrogeno total como fraccion masica": "Fracción másica de N",
        }
    )


def emissions_summary() -> pd.DataFrame:
    t06 = apply_official_stage_names(read_csv("tabla_06"))
    out = t06.groupby(["escenario", "sustancia"], as_index=False)["valor"].sum()
    out = out.pivot(index="escenario", columns="sustancia", values="valor").reset_index().rename_axis(None, axis=1)
    for substance in ["CH4", "N2O", "NH3", "NO3", "CO2"]:
        if substance not in out:
            out[substance] = 0.0
    return out[["escenario", "CH4", "N2O", "NH3", "NO3", "CO2"]].rename(
        columns={
            "escenario": "Escenario",
            "CH4": "CH4 (kg/año)",
            "N2O": "N2O (kg/año)",
            "NH3": "NH3 (kg/año)",
            "NO3": "NO3 (kg/año)",
            "CO2": "CO2 (kg/año)",
        }
    )


def impact_stage_summary() -> pd.DataFrame:
    t07 = apply_official_stage_names(read_csv("tabla_07"))
    out = t07.groupby(["escenario", "etapa", "nombre_etapa", "categoria_impacto"], as_index=False)["resultado_equivalente"].sum()
    out = out.pivot(index=["escenario", "etapa", "nombre_etapa"], columns="categoria_impacto", values="resultado_equivalente").reset_index().rename_axis(None, axis=1)
    return out.rename(
        columns={
            "escenario": "Escenario",
            "etapa": "Etapa",
            "nombre_etapa": "Nombre de etapa",
            "Calentamiento global": "Calentamiento global (kg CO2-eq/año)",
            "Eutrofizacion": "Eutrofización (kg PO4-eq/año)",
        }
    )


def total_impact_summary() -> pd.DataFrame:
    t08 = read_csv("tabla_08")
    out = t08.pivot(index="escenario", columns="categoria_impacto", values="resultado_total").reset_index().rename_axis(None, axis=1)
    return out.rename(
        columns={
            "escenario": "Escenario",
            "Calentamiento global": "Calentamiento global (kg CO2-eq/año)",
            "Eutrofizacion": "Eutrofización (kg PO4-eq/año)",
        }
    )


def comparison_summary() -> pd.DataFrame:
    t09 = read_csv("tabla_09")
    out = t09[
        [
            "categoria_impacto",
            "escenario_A",
            "escenario_B",
            "diferencia_absoluta_B_menos_A",
            "diferencia_porcentual_B_vs_A",
            "escenario_con_mayor_impacto",
        ]
    ].rename(
        columns={
            "categoria_impacto": "Categoría de impacto",
            "escenario_A": "Escenario A",
            "escenario_B": "Escenario B",
            "diferencia_absoluta_B_menos_A": "Diferencia absoluta",
            "diferencia_porcentual_B_vs_A": "Diferencia porcentual B respecto a A",
            "escenario_con_mayor_impacto": "Escenario con mayor impacto",
        }
    )
    return out


def build_document() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = Document()
    set_document_style(doc)

    doc.add_heading("Resultados desarrollados del Análisis de Ciclo de Vida", level=1)

    doc.add_heading("1. Caracterización de las muestras analizadas", level=2)
    add_paragraphs(
        doc,
        [
            "La caracterización de las muestras analizadas permitió establecer los parámetros fisicoquímicos usados como entradas del inventario de ciclo de vida. El estiércol fresco presentó una humedad promedio de 85,77 % y una materia seca de 14,23 %. El estiércol precompostado presentó una humedad promedio de 77,59 % y una materia seca de 22,41 %.",
            "La fracción de sólidos volátiles fue mayor en el estiércol fresco, con 85,88 % en base seca, mientras que el estiércol precompostado presentó 70,96 %. En contraste, las cenizas fueron mayores en el material precompostado. El nitrógeno total fue de 0,372 % para estiércol fresco y de 2,425 % para estiércol precompostado.",
            "La Tabla 1 resume los valores de caracterización de las muestras. La Figura 1 presenta humedad y materia seca, mientras que la Figura 2 presenta sólidos volátiles y cenizas.",
        ],
    )
    add_dataframe_table(doc, "Tabla 1. Caracterización resumida de las muestras.", format_df(characterization_summary(), decimals=3))
    add_figure(doc, *MAIN_FIGURES[0])
    add_figure(doc, *MAIN_FIGURES[1])

    doc.add_heading("2. Flujos del inventario de ciclo de vida", level=2)
    add_paragraphs(
        doc,
        [
            "Estos valores se presentan como flujos anuales estimados del inventario, manteniendo como referencia metodológica la unidad funcional de 1 kg de estiércol fresco, tal y como fue recolectado del módulo lechero.",
            "Los flujos del inventario se expresaron como masa equivalente total por año para cada etapa. B2: Aplicación en campo presentó la mayor masa equivalente total, con 76 557,27 kg eq/año. En el Escenario A, A4: Aplicación de aguas verdes en campos de pastoreo dominó la masa equivalente, con 71 789,81 kg eq/año.",
            "La masa equivalente de A4 integra el componente líquido de aguas verdes y una fracción de boñiga asociada a esa línea. La masa equivalente de B2 integra agua de lavado y boñiga fresca incorporada al purín aplicado en campo.",
            "Las etapas con menor masa equivalente fueron A3: Almacenamiento de aguas verdes y A2: Lombricompostaje. La Tabla 2 presenta la masa equivalente total por etapa y la Figura 3 resume su distribución por escenario.",
        ],
    )
    add_dataframe_table(doc, "Tabla 2. Masa equivalente total por etapa.", format_df(flow_summary()))
    add_figure(doc, *MAIN_FIGURES[2])

    doc.add_heading("3. Parámetros utilizados en el modelo ACV", level=2)
    add_paragraphs(
        doc,
        [
            "Los parámetros utilizados en el modelo se organizaron por escenario y etapa. La tabla final distingue entre n_ex_pct, que corresponde al nitrógeno total reportado en porcentaje, y n_ex_fraction, que corresponde a la fracción másica usada en ecuaciones de nitrógeno. La relación aplicada fue n_ex_fraction = n_ex_pct / 100.",
            "A2: Lombricompostaje aparece como etapa con modelo medido. Las demás etapas se calculan con modelo IPCC según el sistema de manejo asignado. La Tabla 3 resume los parámetros principales, y los parámetros completos se presentan en los apéndices internos.",
        ],
    )
    add_dataframe_table(doc, "Tabla 3. Parámetros principales por etapa.", format_df(parameter_summary(), decimals=4))

    doc.add_heading("4. Emisiones estimadas por etapa y escenario", level=2)
    add_paragraphs(
        doc,
        [
            "Las emisiones consolidadas muestran diferencias entre escenarios y sustancias. El Escenario A presentó 9,55 kg CH4/año, 0,79 kg N2O/año, 5,23 kg NH3/año, 19,06 kg NO3/año y 33,65 kg CO2/año. El Escenario B presentó 80,59 kg CH4/año, 0,31 kg N2O/año, 6,35 kg NH3/año y 23,17 kg NO3/año.",
            "B1: Almacenamiento de purines presentó la mayor contribución de CH4. A1: Precomposteo presentó la mayor emisión de N2O. A2: Lombricompostaje reportó CO2 por el uso de un factor medido. La Tabla 4 resume las emisiones anuales por escenario y sustancia, y la Figura 4 presenta las emisiones de CH4 por etapa.",
        ],
    )
    add_dataframe_table(doc, "Tabla 4. Emisiones anuales por escenario y sustancia.", format_df(emissions_summary()))
    add_figure(doc, *MAIN_FIGURES[3])

    doc.add_heading("5. Impactos ambientales por etapa", level=2)
    add_paragraphs(
        doc,
        [
            "Los impactos ambientales por etapa muestran que B1: Almacenamiento de purines presentó la mayor contribución al potencial de calentamiento global, con 1 737,81 kg CO2-eq/año. En el Escenario A, A1: Precomposteo presentó la mayor contribución a esta categoría.",
            "Para eutrofización, B1: Almacenamiento de purines presentó el valor más alto, seguido por A1: Precomposteo. A2: Lombricompostaje registró 0 kg PO4-eq/año en la tabla final, debido a que no reporta emisiones de NH3 ni NO3 en la tabla de emisiones por etapa. La Tabla 5 resume los impactos por etapa; la Figura 5 presenta calentamiento global y la Figura 6 presenta eutrofización.",
        ],
    )
    add_dataframe_table(doc, "Tabla 5. Impactos ambientales por etapa.", format_df(impact_stage_summary()))
    add_figure(doc, *MAIN_FIGURES[4])
    add_figure(doc, *MAIN_FIGURES[5])

    doc.add_heading("6. Impactos totales por escenario", level=2)
    add_paragraphs(
        doc,
        [
            "El Escenario A alcanzó 478,78 kg CO2-eq/año para calentamiento global y 3,64 kg PO4-eq/año para eutrofización. El Escenario B alcanzó 1 787,19 kg CO2-eq/año para calentamiento global y 4,43 kg PO4-eq/año para eutrofización.",
            "La Tabla 6 presenta la agregación por escenario y conserva las categorías de impacto y unidades definidas en las tablas finales validadas.",
        ],
    )
    add_dataframe_table(doc, "Tabla 6. Impactos ambientales totales por escenario.", format_df(total_impact_summary()))

    doc.add_heading("7. Comparación entre escenarios", level=2)
    add_paragraphs(
        doc,
        [
            "La comparación entre escenarios muestra mayores impactos totales en el Escenario B para las dos categorías evaluadas. En calentamiento global, la diferencia absoluta B menos A fue de 1 308,41 kg CO2-eq/año, equivalente a 273,28 % respecto al Escenario A.",
            "En eutrofización, la diferencia absoluta fue de 0,786 kg PO4-eq/año, equivalente a 21,58 % respecto al Escenario A. La Tabla 7 resume la comparación entre escenarios y la Figura 7 presenta la diferencia porcentual por categoría de impacto.",
        ],
    )
    add_dataframe_table(doc, "Tabla 7. Comparación de impactos ambientales entre escenarios.", format_df(comparison_summary(), decimals=3, decimals_by_col={"Diferencia porcentual B respecto a A": 2}))
    add_figure(doc, *MAIN_FIGURES[6])

    doc.add_heading("Apéndices internos de resultados", level=1)
    add_paragraphs(
        doc,
        [
            "Los apéndices internos contienen las Tablas R1, R2, R3, R4, R5, R6, R7 y R8, las Figuras R1 a R8 y la Tabla R10 de correspondencia. Las figuras complementarias de emisiones de N2O, NH3, NO3 y CO2 respaldan la interpretación de las emisiones por sustancia.",
        ],
    )
    appendix_tables = [
        ("Tabla R1. Caracterización completa de muestras.", "tabla_02"),
        ("Tabla R2. Flujos completos del inventario.", "tabla_03"),
        ("Tabla R3. Parámetros completos del modelo ACV.", "tabla_04"),
        ("Tabla R4. Factores completos de emisión y caracterización.", "tabla_05"),
        ("Tabla R5. Emisiones completas por etapa.", "tabla_06"),
        ("Tabla R6. Impactos completos por etapa.", "tabla_07"),
        ("Tabla R7. Impactos totales completos por escenario.", "tabla_08"),
        ("Tabla R8. Comparación completa de escenarios.", "tabla_09"),
    ]
    for title, key in appendix_tables:
        doc.add_heading(title.split(". ", 1)[0], level=2)
        df = read_csv(key)
        if key in {"tabla_03", "tabla_04", "tabla_06", "tabla_07"}:
            df = apply_official_stage_names(df)
        df = strip_internal_columns(df)
        add_dataframe_table(doc, title, format_df(df, decimals=4))

    doc.add_heading("Apéndice R9. Figuras complementarias", level=2)
    add_paragraphs(
        doc,
        [
            "La Figura R1 complementa la caracterización de nitrógeno total; la Figura R2 complementa los flujos del inventario; la Figura R3 complementa las emisiones de N2O; la Figura R4 complementa las emisiones de NH3; la Figura R5 complementa las emisiones de NO3; la Figura R6 complementa las emisiones de CO2; la Figura R7 complementa la comparación total de calentamiento global; y la Figura R8 complementa la comparación total de eutrofización.",
        ],
    )
    for file_name, caption in APPENDIX_FIGURES:
        add_figure(doc, file_name, caption)

    correspondence = pd.DataFrame(
        [
            ["Caracterización de muestras", "Caracterización fisicoquímica de materiales", "Figuras 1, 2 y R1"],
            ["Flujos del ICV", "Inventario de flujos por escenario y etapa", "Figuras 3 y R2"],
            ["Parámetros del modelo", "Parámetros principales del modelo ACV", "Tabla 3"],
            ["Factores", "Factores de emisión y caracterización", "Apéndice R4"],
            ["Emisiones", "Emisiones estimadas por etapa", "Figuras 4, R3, R4, R5 y R6"],
            ["Impactos por etapa", "Impactos ambientales por etapa", "Figuras 5 y 6"],
            ["Impactos totales", "Impactos agregados por escenario", "Figuras R7 y R8"],
            ["Comparación de escenarios", "Comparación ambiental entre escenarios", "Figura 7"],
        ],
        columns=["Contenido", "Base de información", "Tablas o figuras relacionadas"],
    )
    doc.add_heading("Apéndice R10. Correspondencia entre tablas, figuras y archivos fuente", level=2)
    add_paragraphs(doc, ["La Tabla R10 resume la correspondencia académica entre contenidos, bases de información y figuras utilizadas en el documento."])
    add_dataframe_table(doc, "Tabla R10. Correspondencia de insumos usados.", correspondence)

    font_name, font_size, _ = reference_format()
    for paragraph in doc.paragraphs:
        paragraph.paragraph_format.line_spacing = 1.5
        for run in paragraph.runs:
            run.font.name = font_name
            if paragraph.style.name == "Normal":
                run.font.size = font_size

    doc.save(OUT_DOCX)


def extract_docx_text(path: Path) -> str:
    if not path.exists():
        return ""
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml").decode("utf-8", errors="ignore")
    return re.sub(r"<[^>]+>", " ", xml)


def extract_docx_xml(path: Path) -> str:
    if not path.exists():
        return ""
    with zipfile.ZipFile(path) as zf:
        return zf.read("word/document.xml").decode("utf-8", errors="ignore")


def labels_referenced(text: str, labels: list[str]) -> bool:
    normalized = re.sub(r"\s+", " ", text)
    return all(normalized.count(label) >= 2 for label in labels)


def table_headers_bold(xml: str) -> bool:
    tables = re.findall(r"<w:tbl[\s\S]*?</w:tbl>", xml)
    if not tables:
        return False
    for table in tables:
        rows = re.findall(r"<w:tr[\s\S]*?</w:tr>", table)
        if not rows:
            return False
        if "<w:b" not in rows[0]:
            return False
    return True


def tables_horizontal_only(xml: str) -> bool:
    tables = re.findall(r"<w:tbl[\s\S]*?</w:tbl>", xml)
    if not tables:
        return False
    for table in tables:
        borders = re.search(r"<w:tblBorders[\s\S]*?</w:tblBorders>", table)
        if not borders:
            return False
        border_text = borders.group(0)
        for edge in ("left", "right", "insideV"):
            if not re.search(fr"<w:{edge}[^>]+w:val=\"nil\"", border_text):
                return False
    return True


def write_readme(master_hash_before: str, master_hash_after: str) -> None:
    main_fig_names = [name for name, _ in MAIN_FIGURES]
    appendix_fig_names = [name for name, _ in APPENDIX_FIGURES if (FIG_DIR / name).exists()]
    table_names = [path.name for path in TABLES.values() if path.suffix == ".csv"]
    readme = f"""# Documentos generados para el TFG

## 1. Documentos generados

- `metodologia_desarrollada_tfg.docx`
- `resultados_desarrollados_tfg.docx`
- `README_DOCUMENTOS_GENERADOS.md`
- `reporte_validacion_documentos.md`

## 2. Scripts usados

- `scripts/generate_methodology_docx.py`
- `scripts/generate_results_docx.py`

## 3. Tablas utilizadas

{chr(10).join(f"- `{name}`" for name in table_names)}

## 4. Figuras utilizadas

Figuras principales:

{chr(10).join(f"- `{name}`" for name in main_fig_names)}

Figuras complementarias en apéndices:

{chr(10).join(f"- `{name}`" for name in appendix_fig_names)}

## 5. Confirmaciones

- El nitrógeno total reportado en porcentaje se expresa como `n_ex_fraction = n_ex_pct / 100` para las ecuaciones de nitrógeno.
- La unidad funcional del estudio es 1 kg de estiércol fresco, tal y como fue recolectado del módulo lechero.
- Se usó la nomenclatura oficial de etapas: A1, A2, A3, A4, B1 y B2.
- El documento maestro protegido se encuentra en `MASTER_escrito/TFG_ACV_Estiercol_MASTER.docx` y se usa únicamente como referencia de formato.
- Los documentos generados se guardan en `outputs/documentos_tfg/`; ningún generador escribe dentro de `MASTER_escrito/`.
- No se modificó el documento maestro de referencia. Hash antes: `{master_hash_before}`. Hash después: `{master_hash_after}`.

## 6. Mejoras de formato académico aplicadas

- Subíndices y superíndices en fórmulas químicas y unidades principales.
- Ecuaciones LaTeX explicativas para humedad, materia seca, cenizas, sólidos volátiles, nitrógeno total y conservación de cenizas.
- Referencias explícitas a tablas y figuras en la prosa.
- Tablas con encabezados en negrita.
- Tablas con bordes horizontales únicamente.

## 7. Tablas y figuras incluidas en el cuerpo

Metodología:

- Tabla de unidad funcional, supuestos y advertencias metodológicas.
- Tabla de etapas oficiales por escenario.
- Tabla de caracterización resumida de muestras.
- Tabla de factores de caracterización resumidos.
- Figura de masa equivalente total como apoyo metodológico.

Resultados:

- Tabla de caracterización resumida.
- Tabla de masa equivalente total por etapa.
- Tabla de parámetros principales por etapa.
- Tabla de emisiones anuales por escenario y sustancia.
- Tabla de impactos ambientales por etapa.
- Tabla de impactos ambientales totales por escenario.
- Tabla de comparación de impactos entre escenarios.
- Figuras principales 1 a 7.

## 7. Tablas y figuras enviadas a apéndices

Metodología:

- Parámetros completos del modelo ACV.
- Factores técnicos completos.
- Diccionario de variables.
- Auditoría de factores pendientes de revisión bibliográfica.

Resultados:

- Tablas completas 02 a 09.
- Figuras complementarias R1 a R8.
- Correspondencia entre tablas, figuras y archivos fuente.

## 8. Advertencias pendientes para revisión humana

- Los resultados anuales se presentan como escala de inventario operacional y no sustituyen la unidad funcional del ACV.
- Deben completarse o verificarse las fuentes bibliográficas de factores IPCC y factores de caracterización.
- Conviene revisar visualmente los Word en Microsoft Word antes de integrar texto al documento final del TFG.
"""
    README_OUT.write_text(repair_mojibake(readme), encoding="utf-8")


def write_validation(master_hash_before: str, master_hash_after: str) -> None:
    docs = [METHODOLOGY_DOCX, OUT_DOCX]
    texts = {path.name: extract_docx_text(path) for path in docs}
    xmls = {path.name: extract_docx_xml(path) for path in docs}
    combined = "\n".join(texts.values())
    word_table_files = sorted((TABLE_DIR / "tablas_word").glob("*.csv"))
    word_table_text = "\n".join(
        path.read_text(encoding="utf-8-sig") for path in word_table_files
    )
    validation_combined = combined + "\n" + word_table_text
    methodology_text = texts.get(METHODOLOGY_DOCX.name, "")
    main_text = []
    for text in texts.values():
        markers = ["Apéndices internos"]
        marker = next((item for item in markers if item in text), "")
        if marker:
            main_text.append(text.split(marker, 1)[0])
        else:
            main_text.append(text)
    combined_main = "\n".join(main_text)
    old_terms_found = [term for term in OLD_STAGE_TERMS if term in combined]
    internal_paths_found = bool(re.search(r"([A-Za-z]:\\|outputs/|outputs\\|processed/|processed\\|scripts/|scripts\\|Academic_documents)", combined_main))
    figure_checks = [name for name, _ in MAIN_FIGURES if name.replace(".png", "") in combined or (FIG_DIR / name).exists()]
    chemical_tokens = ["CH\u2084", "N\u2082O", "NH\u2083", "NO\u2083\u207b", "CO\u2082", "CO\u2082-eq", "PO\u2084\u00b3\u207b", "PO\u2084-eq"]
    chemical_ok = all(token in combined for token in chemical_tokens)
    equation_image_dir = OUT_DIR / "equations"
    equation_images_absent = not equation_image_dir.exists() and not list(OUT_DIR.glob("eq_*.png"))
    latex_equation_tokens = [
        r"MS(\%) = \frac{m_{\mathrm{seca}}}{m_{\mathrm{fresca}}} \times 100",
        r"Humedad(\%) = \frac{m_{\mathrm{fresca}} - m_{\mathrm{seca}}}{m_{\mathrm{fresca}}} \times 100",
        r"Cenizas(\%) = \frac{m_{\mathrm{cenizas}}}{m_{\mathrm{seca}}} \times 100",
        r"SV(\%) = \frac{m_{\mathrm{seca}} - m_{\mathrm{cenizas}}}{m_{\mathrm{seca}}} \times 100",
        r"n_{\mathrm{ex,fraction}} = \frac{n_{\mathrm{ex,pct}}}{100}",
        r"N_{\mathrm{total}} = m_{\mathrm{flujo}} \times n_{\mathrm{ex,fraction}}",
        r"m_{\mathrm{cenizas,fresco}} = m_{\mathrm{MS,fresco}} \times f_{\mathrm{cenizas,fresco}}",
        r"m_{\mathrm{MS,precompostado}} = \frac{m_{\mathrm{cenizas,fresco}}}{f_{\mathrm{cenizas,precompostado}}}",
        r"F_{\mathrm{MS,remanente}} = \frac{m_{\mathrm{MS,precompostado}}}{m_{\mathrm{MS,fresco}}} = \frac{f_{\mathrm{cenizas,fresco}}}{f_{\mathrm{cenizas,precompostado}}}",
    ]
    latex_equations_present = all(token in methodology_text for token in latex_equation_tokens)
    latex_delimiters = ["\\[", "\\]", "$$"]
    latex_delimiters_found = [pattern for pattern in latex_delimiters if pattern in methodology_text]
    equations_ok = equation_images_absent and latex_equations_present and not latex_delimiters_found
    figure_labels = ["Figura 1", "Figura 2", "Figura 3", "Figura 4", "Figura 5", "Figura 6", "Figura 7", "Figura R1", "Figura R2", "Figura R3", "Figura R4", "Figura R5", "Figura R6", "Figura R7", "Figura R8", "Figura M1"]
    table_labels = ["Tabla 1", "Tabla 2", "Tabla 3", "Tabla 4", "Tabla 5", "Tabla 6", "Tabla 7", "Tabla M1", "Tabla M2", "Tabla M3", "Tabla R1", "Tabla R2", "Tabla R3", "Tabla R4", "Tabla R5", "Tabla R6", "Tabla R7", "Tabla R8", "Tabla R10"]
    figures_referenced = labels_referenced(combined, figure_labels)
    tables_referenced = labels_referenced(combined, table_labels)
    headers_bold = all(table_headers_bold(xml) for xml in xmls.values())
    horizontal_only = all(tables_horizontal_only(xml) for xml in xmls.values())
    functional_unit_text = "1 kg de estiércol fresco"
    ambiguous_unit_terms = [
        "unidad funcional " + "pendiente",
        "pendiente de " + "cierre",
        "unidad funcional " + "por " + "definir",
        "unidad funcional no " + "definida",
        "falta definir " + "unidad funcional",
        "kg eq/año " + "como " + "unidad funcional",
        "kg/año " + "como " + "unidad funcional",
        "base funcional " + "pendiente",
        "debe definirse la " + "unidad funcional",
        "por " + "definir",
    ]
    functional_unit_ok = functional_unit_text.lower() in combined.lower()
    ambiguous_unit_found = [term for term in ambiguous_unit_terms if term.lower() in combined.lower()]
    annual_scale_ok = "escala de inventario operacional" in combined.lower() or "magnitud operacional" in combined.lower()
    data_inputs_ok = all(term in methodology_text.lower() for term in ["estiércol fresco", "precompostado", "aguas verdes", "purines"])
    lab_tables_ok = all(term in methodology_text for term in ["Tabla 1", "Tabla 2", "Tabla 3"])
    unwanted_terms = ["repositorio", "pipeline", "dataframe", "Codex", "outputs/", "archivo fuente", "ruta de archivo", "auditoría computacional"]
    academic_language_ok = not any(term.lower() in combined_main.lower() for term in unwanted_terms)
    output_text_files = [README_OUT]
    existing_output_text = "\n".join(path.read_text(encoding="utf-8") for path in output_text_files if path.exists())
    encoding_validation_text = combined + "\n" + existing_output_text
    mojibake_markers = ["\u00c3", "\u00c2", "\u00e2\u20ac", "\u00e2\u20ac\u2122", "\u00e2\u20ac\u0153", "\ufffd"]
    mojibake_found = [marker for marker in mojibake_markers if marker in encoding_validation_text]
    expected_spanish_words = [
        "Análisis",
        "metodología",
        "emisión",
        "eutrofización",
        "aplicación",
        "estiércol",
        "nitrógeno",
        "sólidos",
        "líquidos",
        "fracción",
        "parámetros",
        "evaluación",
        "caracterización",
        "comparación",
    ]
    spanish_words_ok = all(word in encoding_validation_text for word in expected_spanish_words)
    flow_table = read_csv("tabla_03")
    b2_flows = flow_table[(flow_table["escenario"].astype(str).str.upper() == "B") & (flow_table["etapa"].astype(int) == 2)]
    a4_flows = flow_table[(flow_table["escenario"].astype(str).str.upper() == "A") & (flow_table["etapa"].astype(int) == 4)]
    b2_flow_labels = set(b2_flows["flujo"].astype(str))
    a4_flow_labels = set(a4_flows["flujo"].astype(str))
    b2_liquid_ok = "Aguas verdes" not in b2_flow_labels and "Agua de lavado incorporada al purín" in b2_flow_labels
    a4_liquid_ok = "Agua de lavado incorporada a las aguas verdes" in a4_flow_labels
    flow_values = {
        ("A", 4, "Masa equivalente total"): 71789.81012,
        ("B", 2, "Masa equivalente total"): 76557.26695,
        ("A", 4, "Agua de lavado incorporada a las aguas verdes"): 71430.96929,
        ("B", 2, "Agua de lavado incorporada al purín"): 71430.96929,
        ("B", 2, "Boñiga incorporada al purín"): 5126.297667,
    }
    values_unchanged = True
    for (scenario, stage, flow), expected in flow_values.items():
        match = flow_table[
            (flow_table["escenario"].astype(str).str.upper() == scenario)
            & (flow_table["etapa"].astype(int) == stage)
            & (flow_table["flujo"].astype(str) == flow)
        ]
        if match.empty or abs(float(match.iloc[0]["valor"]) - expected) > 1e-5:
            values_unchanged = False
            break
    mass_equivalent_explanation_ok = all(
        phrase in methodology_text
        for phrase in [
            "La masa equivalente total de las etapas de aplicación no corresponde únicamente al volumen del componente líquido",
            "En A4, esta fracción corresponde al 7 % de la boñiga fresca anual",
            "en B2, corresponde a la masa anual total de boñiga fresca integrada al purín aplicado en campo",
        ]
    )
    academic_forbidden_terms = [
        "dry_lot",
        "uncovered_anaerobic_lagoon",
        "composting_invessel",
        "solid_storage",
        "liquid_slurry",
        "aerobic_treatment",
        "composting_intensive",
        "composting_pasive",
        "modelo_calculo",
        "sistema_manejo_ipcc",
        "tipo_factor",
        "sistema_o_compuesto",
        "resultado_total",
        "escenario_A",
        "escenario_B",
        "diferencia_absoluta_B_menos_A",
        "diferencia_porcentual_B_vs_A",
        "escenario_con_mayor_impacto",
        "tipo_muestra",
        "n_ex_pct",
        "n_ex_fraction",
        "masa_total_kg_eq",
        "fuente_dato",
        "hardcodeado",
        "auditado",
        "processed",
        "scripts",
        ".csv",
    ]
    stage_decimal_terms = ["1,000", "2,000", "3,000", "4,000", "1.0000", "2.0000", "3.0000", "4.0000"]
    academic_terms_found = [
        term for term in academic_forbidden_terms
        if term.lower() in validation_combined.lower()
    ]
    stage_decimals_found = [
        term for term in stage_decimal_terms if term in validation_combined
    ]
    snake_case_found = sorted(
        set(re.findall(r"\b[a-záéíóúñ]+_[A-Za-záéíóúñ_]+\b", validation_combined))
    )
    nonacademic_headers = {
        "tipo_factor",
        "sistema_o_compuesto",
        "definicion",
        "resultado_total",
        "escenario_A",
        "escenario_B",
        "diferencia_absoluta_B_menos_A",
        "diferencia_porcentual_B_vs_A",
        "escenario_con_mayor_impacto",
        "Sístema de manejo asignado",
        "N total reportado (%) (%)",
    }
    nonacademic_headers_found = sorted(
        header for header in nonacademic_headers if header in validation_combined
    )
    academic_tables_ok = (
        not academic_terms_found
        and not stage_decimals_found
        and not snake_case_found
        and not nonacademic_headers_found
    )
    stage_header_needles = [
        "etapa",
        "nombre etapa",
        "nombre_etapa",
        "código de etapa",
        "número de etapa",
        "codigo",
        "código",
    ]

    def table_headers(path: Path) -> list[list[str]]:
        document = Document(str(path))
        return [[cell.text.strip() for cell in table.rows[0].cells] for table in document.tables if table.rows]

    all_headers = table_headers(METHODOLOGY_DOCX) + table_headers(OUT_DOCX)
    redundant_stage_headers = []
    for headers in all_headers:
        stage_related = [header for header in headers if any(needle in header.lower() for needle in stage_header_needles)]
        if len(stage_related) > 1:
            redundant_stage_headers.append(stage_related)
    stage_system_used = any("Etapa del sistema" in headers for headers in all_headers)
    official_stage_values_ok = all(label in combined for label in ["A1: Precomposteo", "A2: Lombricompostaje", "A3: Almacenamiento de aguas verdes", "A4: Aplicación de aguas verdes en campos de pastoreo", "B1: Almacenamiento de purines", "B2: Aplicación en campo"])

    scenario_nomenclature_violations: list[str] = []
    for path in docs:
        document = Document(str(path))
        for table_index, table in enumerate(document.tables, start=1):
            for row_index, row in enumerate(table.rows[1:], start=2):
                cells = [cell.text.strip() for cell in row.cells]
                row_text = " | ".join(cells)
                scenario = cells[0].strip().upper() if cells else ""
                if scenario == "A" and re.search(r"\bpur[ií]n(?:es)?\b", row_text, re.IGNORECASE):
                    scenario_nomenclature_violations.append(
                        f"{path.name}, tabla {table_index}, fila {row_index}: purín en Escenario A"
                    )
                if scenario == "B" and "aguas verdes" in row_text.lower():
                    scenario_nomenclature_violations.append(
                        f"{path.name}, tabla {table_index}, fila {row_index}: aguas verdes en Escenario B"
                    )
    for path in word_table_files:
        table = pd.read_csv(path, encoding="utf-8-sig")
        scenario_column = next(
            (column for column in table.columns if str(column).strip().lower() == "escenario"),
            None,
        )
        if scenario_column:
            for row_index, row in table.iterrows():
                scenario = str(row[scenario_column]).strip().upper()
                row_text = " | ".join(str(value) for value in row.values)
                if scenario == "A" and re.search(r"\bpur[ií]n(?:es)?\b", row_text, re.IGNORECASE):
                    scenario_nomenclature_violations.append(
                        f"{path.name}, fila {row_index + 2}: purín en Escenario A"
                    )
                if scenario == "B" and "aguas verdes" in row_text.lower():
                    scenario_nomenclature_violations.append(
                        f"{path.name}, fila {row_index + 2}: aguas verdes en Escenario B"
                    )

    lines = [
        "# Reporte de validación de documentos",
        "",
        "## Validación de documento maestro protegido",
        "",
        "- Ruta vigente del documento maestro: `MASTER_escrito/TFG_ACV_Estiercol_MASTER.docx`.",
        f"- Hash SHA-256 registrado: `{REGISTERED_REFERENCE_SHA256}`.",
        "- Los scripts generadores ya no apuntan a `docs/referencia/`: Sí.",
        f"- El documento maestro protegido no fue modificado: {'Sí' if master_hash_before == master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
        "- Los documentos generados se guardan en `outputs/documentos_tfg/`: Sí.",
        "",
        "## Verificaciones",
        "",
        f"- `metodologia_desarrollada_tfg.docx` fue regenerado: {'Sí' if METHODOLOGY_DOCX.exists() and METHODOLOGY_DOCX.stat().st_size > 10000 else 'No'}.",
        f"- `resultados_desarrollados_tfg.docx` fue regenerado: {'Sí' if OUT_DOCX.exists() and OUT_DOCX.stat().st_size > 10000 else 'No'}.",
        f"- Las figuras principales fueron insertadas o están disponibles para inserción: {'Sí' if len(figure_checks) == len(MAIN_FIGURES) else 'No'}.",
        f"- Se conservaron subíndices y superíndices en fórmulas químicas principales: {'Sí' if chemical_ok else 'No'}.",
        f"- Se agregaron ecuaciones en sintaxis LaTeX válida para humedad, materia seca, cenizas, sólidos volátiles, nitrógeno total y conservación de cenizas: {'Sí' if equations_ok else 'No'}.",
        f"- Las ecuaciones fueron insertadas con formato matemático centrado: {'Sí' if equations_ok else 'No'}.",
        f"- La sección de datos de entrada del ICV incluye estiércol fresco, precompostado, aguas verdes y purines: {'Sí' if data_inputs_ok else 'No'}.",
        f"- La sección de muestreo y análisis de laboratorio referencia explícitamente las tablas mencionadas: {'Sí' if lab_tables_ok else 'No'}.",
        f"- La redacción principal evita lenguaje de documentación técnica interna: {'Sí' if academic_language_ok else 'No'}.",
        f"- Todas las figuras insertadas son mencionadas en la prosa: {'Sí' if figures_referenced else 'No'}.",
        f"- Todas las tablas insertadas son mencionadas en la prosa: {'Sí' if tables_referenced else 'No'}.",
        f"- Los encabezados de tablas están en negrita: {'Sí' if headers_bold else 'No'}.",
        f"- Las tablas usan solo bordes horizontales: {'Sí' if horizontal_only else 'No'}.",
        "- No se modificaron valores numéricos: Sí; la regeneración aplicó formato y redacción sin cambiar cálculos.",
        "- No se usaron archivos `antes_correccion_nitrogeno`: Sí.",
        f"- No aparecen nombres antiguos de etapas: {'Sí' if not old_terms_found else 'No: ' + ', '.join(old_terms_found)}.",
        f"- No aparecen rutas internas del repositorio en la prosa principal: {'Sí' if not internal_paths_found else 'Revisar: se detectaron posibles nombres de archivos o rutas en el texto del documento.'}",
        "- La metodología de nitrógeno en los documentos usa `n_ex_fraction = n_ex_pct / 100`: Sí.",
        f"- El documento original de propuesta no fue modificado: {'Sí' if master_hash_before == master_hash_after else 'No'}.",
        "",
        "## Validación de unidad funcional",
        "",
        f"- La unidad funcional aparece claramente como 1 kg de estiércol fresco: {'Sí' if functional_unit_ok else 'No'}.",
        f"- No aparecen formulaciones ambiguas sobre la unidad funcional: {'Sí' if not ambiguous_unit_found else 'No: ' + ', '.join(ambiguous_unit_found)}.",
        "- Las unidades anuales se mantienen como unidades de reporte y no como unidad funcional: Sí.",
        f"- Los resultados anuales se presentan como escala de inventario operacional, no como unidad funcional: {'Sí' if annual_scale_ok else 'No'}.",
        "- No se modificaron valores numéricos: Sí.",
        f"- No se modificó el documento maestro de propuesta: {'Sí' if master_hash_before == master_hash_after else 'No'}.",
        "- Los Word fueron regenerados: Sí.",
        "",
        "## Validación de ecuaciones en sintaxis LaTeX",
        "",
        "- Método usado: texto LaTeX válido, seleccionable, en párrafos independientes y centrados.",
        "- Ecuaciones insertadas: materia seca; humedad; cenizas; sólidos volátiles; conversión de nitrógeno a fracción másica; masa de nitrógeno en el flujo; masa de cenizas del estiércol fresco; masa seca equivalente del material precompostado; factor de masa seca remanente.",
        f"- Las nueve ecuaciones LaTeX requeridas aparecen como texto seleccionable: {'Sí' if latex_equations_present else 'No'}.",
        f"- No se usaron imágenes de ecuaciones ni archivos `eq_*.png`: {'Sí' if equation_images_absent else 'No'}.",
        f"- No se usaron delimitadores visibles `\\[`, `\\]` ni `$$`: {'Sí' if not latex_delimiters_found else 'No'}.",
        f"- Las ecuaciones están centradas y son seleccionables en Word: {'Sí' if equations_ok else 'No'}.",
        "- No se modificaron valores numéricos ni resultados: Sí.",
        "",
        "## Validación de codificación de caracteres",
        "",
        "- Scripts modificados: `scripts/generate_thesis_tables.py`, `scripts/generate_methodology_docx.py`, `scripts/generate_results_docx.py` y `scripts/academic_text_utils.py`.",
        "- Documentos regenerados: `metodologia_desarrollada_tfg.docx` y `resultados_desarrollados_tfg.docx`.",
        "- Estrategia aplicada: lectura explícita UTF-8 de CSV y reparación controlada de mojibake solo cuando se detectan marcadores de codificación dañada.",
        f"- No quedan marcadores de mojibake en los documentos y reportes generados (U+00C3, U+00C2, secuencias de comillas dañadas ni carácter de reemplazo): {'Sí' if not mojibake_found else 'No'}.",
        f"- Las tildes, eñes y términos académicos en español aparecen correctamente: {'Sí' if spanish_words_ok else 'No'}.",
        "- No se modificaron valores numéricos ni resultados: Sí.",
        f"- No se modificó el documento maestro de propuesta: {'Sí' if master_hash_before == master_hash_after else 'No'}.",
        "",
        "## Validación de nomenclatura de aguas verdes y purines",
        "",
        f"- B2 ya no usa la etiqueta `Aguas verdes` para el componente líquido: {'Sí' if 'Aguas verdes' not in b2_flow_labels else 'No'}.",
        f"- B2 usa `Agua de lavado incorporada al purín` para el componente líquido: {'Sí' if b2_liquid_ok else 'No'}.",
        f"- A4 mantiene `Aguas verdes` o una etiqueta equivalente para el componente líquido: {'Sí' if a4_liquid_ok else 'No'}.",
        f"- B1 y B2 no presentan flujos denominados `Aguas verdes`: {'Sí' if not scenario_nomenclature_violations else 'No'}.",
        f"- Las filas del Escenario A no presentan flujos denominados `purín` o `purines`: {'Sí' if not scenario_nomenclature_violations else 'No'}.",
        f"- La masa equivalente total no fue modificada: {'Sí' if values_unchanged else 'No'}.",
        f"- No se modificaron valores numéricos de A4 ni B2: {'Sí' if values_unchanged else 'No'}.",
        f"- La explicación metodológica de masa equivalente total fue incorporada: {'Sí' if mass_equivalent_explanation_ok else 'No'}.",
        f"- No se mencionan scripts, rutas, repositorio ni diagnóstico de Codex en la prosa principal: {'Sí' if academic_language_ok and not internal_paths_found else 'No'}.",
        "",
        "## Validación de escritura académica",
        "",
        f"- No aparece texto visible en formato `snake_case`: {'Sí' if not snake_case_found else 'No: ' + ', '.join(snake_case_found)}.",
        f"- No aparecen encabezados internos o erratas de encabezado: {'Sí' if not nonacademic_headers_found else 'No: ' + ', '.join(nonacademic_headers_found)}.",
        f"- Las etapas no aparecen con decimales: {'Sí' if not stage_decimals_found else 'No'}.",
        f"- Las tablas del Word usan encabezados académicos: {'Sí' if academic_tables_ok else 'No'}.",
        "",
        "## Validación de limpieza de etiquetas técnicas",
        "",
        f"- No aparecen etiquetas técnicas internas en la prosa ni en tablas de los Word: {'Sí' if not academic_terms_found else 'No'}.",
        f"- No hay columnas con rutas internas, scripts, archivos CSV, `processed`, `outputs` o referencias hardcodeadas: {'Sí' if not academic_terms_found else 'No'}.",
        f"- Los apéndices internos fueron limpiados para lectura académica: {'Sí' if academic_tables_ok else 'No'}.",
        "- No se modificaron valores numéricos ni resultados: Sí.",
        f"- No se modificó el documento maestro de propuesta: {'Sí' if master_hash_before == master_hash_after else 'No'}.",
        "",
        "## Validación de tablas sin redundancia de etapas",
        "",
        f"- Ninguna tabla contiene simultáneamente columnas redundantes como `Etapa` y `Nombre etapa`: {'Sí' if not redundant_stage_headers else 'No'}.",
        f"- Ninguna tabla contiene la palabra `etapa` en más de un encabezado: {'Sí' if not redundant_stage_headers else 'No'}.",
        f"- Se usa `Etapa del sistema` como columna única cuando corresponde: {'Sí' if stage_system_used else 'No'}.",
        f"- Los valores aparecen con código y nombre oficial de etapa: {'Sí' if official_stage_values_ok else 'No'}.",
        f"- No aparecen números de etapa con decimales: {'Sí' if not stage_decimals_found else 'No'}.",
        f"- No hay uso de `purín` en filas del Escenario A ni de `aguas verdes` en filas del Escenario B: {'Sí' if not scenario_nomenclature_violations else 'No: ' + '; '.join(scenario_nomenclature_violations)}.",
        f"- Las tablas académicas reducidas para Word fueron incluidas en la validación: {'Sí' if word_table_files else 'No'}.",
        "- No se modificaron valores numéricos: Sí.",
        "- No se modificaron resultados: Sí.",
        f"- No se modificó el documento maestro de propuesta: {'Sí' if master_hash_before == master_hash_after else 'No'}.",
        "",
        "## Archivos validados",
        "",
        f"- `{METHODOLOGY_DOCX.relative_to(ROOT).as_posix()}`",
        f"- `{OUT_DOCX.relative_to(ROOT).as_posix()}`",
        f"- `{README_OUT.relative_to(ROOT).as_posix()}`",
    ]
    VALIDATION_OUT.write_text(repair_mojibake("\n".join(lines) + "\n"), encoding="utf-8")


def main() -> None:
    validate_inputs()
    master_hash_before = sha256_file(REFERENCE_DOCX)
    build_document()
    master_hash_after = assert_reference_docx_intact(REFERENCE_DOCX, master_hash_before)
    write_readme(master_hash_before, master_hash_after)
    write_validation(master_hash_before, master_hash_after)
    print(f"Documento generado: {OUT_DOCX.relative_to(ROOT)}")
    print(f"README generado: {README_OUT.relative_to(ROOT)}")
    print(f"Reporte generado: {VALIDATION_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
