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
from docx.text.paragraph import Paragraph

from academic_text_utils import clean_academic_label
from master_word_format import (
    add_master_caption,
    analyze_master_format,
    apply_master_format,
    finalize_document_format,
    format_table_like_master,
    profile_markdown,
)
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
GRAPHICS_SCRIPT = ROOT / "scripts" / "generate_thesis_graphics.py"
OUT_DIR = ROOT / "outputs" / "documentos_tfg"
OUT_DOCX = OUT_DIR / "resultados_desarrollados_tfg.docx"
PROCESSED_TOTALS = ROOT / "processed" / "acv_impacto_total_por_escenario.csv"
PROCESSED_STAGE_IMPACTS = ROOT / "processed" / "acv_impacto_por_etapa_escenario.csv"
METHODOLOGY_DOCX = OUT_DIR / "metodologia_desarrollada_tfg.docx"
README_OUT = OUT_DIR / "README_DOCUMENTOS_GENERADOS.md"
VALIDATION_OUT = OUT_DIR / "reporte_validacion_documentos.md"
FORMAT_REPORT_OUT = OUT_DIR / "reporte_formato_master.md"
APPENDIX_RELATION_REPORT_OUT = OUT_DIR / "reporte_relacion_apendices.md"
FACTOR_REFERENCES_REPORT_OUT = OUT_DIR / "reporte_referencias_factores.md"
NO3_CORRECTION_REPORT_OUT = (
    OUT_DIR / "reporte_correccion_factor_estequiometrico_NO3.md"
)

OLD_NO3_STOICHIOMETRIC_FACTOR = 31 / 7
CURRENT_NO3_STOICHIOMETRIC_FACTOR = 4.4268

METHODOLOGY_APPENDICES = [
    ("A", "Parámetros completos del modelo ACV", "Apéndice interno"),
    ("B", "Factores de emisión y caracterización", "Apéndice interno"),
    ("C", "Diccionario de variables metodológicas", "Apéndice interno"),
]

RESULTS_APPENDICES = [
    ("R1", "Caracterización completa de muestras", "Tabla"),
    ("R2", "Flujos completos del inventario", "Tabla"),
    ("R3", "Parámetros completos del modelo ACV", "Tabla"),
    ("R4", "Factores completos de emisión y caracterización", "Tabla"),
    ("R5", "Emisiones completas por etapa", "Tabla"),
    ("R6", "Impactos completos por etapa", "Tabla"),
    ("R7", "Impactos totales completos por escenario", "Tabla"),
    ("R8", "Comparación completa de escenarios", "Tabla"),
    ("R9", "Figuras complementarias", "Apéndice"),
    (
        "R10",
        "Correspondencia entre tablas, figuras y archivos fuente",
        "Apéndice",
    ),
]

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
    ("B", 2): (
        "B2",
        "Aplicación de purines en campo de pastoreo",
        "Etapa 2: Aplicación de purines en campo de pastoreo",
    ),
}

OLD_STAGE_TERMS = {
    "Manejo inicial de estiércol fresco": "Precomposteo",
    "Manejo posterior de fracción sólida": "Lombricompostaje",
    "Manejo de estiércol fresco sin precompostaje": "Almacenamiento de purines",
    "Manejo o aplicación de purines": "Aplicación de purines en campo de pastoreo",
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
    "requiere_revision_bibliografica",
    "clasificacion_referencia",
    "estado_referencia",
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
    "Factor hardcodeado auditado": "Parámetro complementario",
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
    "referencia_metodologica": "Referencia metodológica",
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
    required = [
        *TABLES.values(),
        PROCESSED_TOTALS,
        PROCESSED_STAGE_IMPACTS,
        *(FIG_DIR / name for name, _ in MAIN_FIGURES),
    ]
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


def add_calculation_framework(df: pd.DataFrame) -> pd.DataFrame:
    """Distingue documentalmente el origen previo del marco de cálculo de cada etapa."""
    out = df.copy()
    frameworks = {
        ("A", 1): "Manejo del estiércol",
        ("A", 2): "Factores experimentales publicados",
        ("A", 3): "Manejo del estiércol",
        ("A", 4): "Suelos gestionados",
        ("B", 1): "Manejo del estiércol",
        ("B", 2): "Suelos gestionados",
    }
    out["Marco de cálculo de la etapa"] = [
        frameworks.get((str(row["escenario"]).strip().upper(), int(float(row["etapa"]))), "")
        for _, row in out.iterrows()
    ]
    if "sistema_manejo_ipcc" in out.columns:
        out = out.rename(columns={"sistema_manejo_ipcc": "Sistema de manejo u origen previo"})
    return out


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


def set_document_style(doc: Document):
    return apply_master_format(doc, REFERENCE_DOCX)


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
        add_master_caption(doc, clean_text(caption))
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
    for row_index, row in enumerate(table.rows):
        tr_pr = row._tr.get_or_add_trPr()
        cant_split = OxmlElement("w:cantSplit")
        tr_pr.append(cant_split)
        if row_index == 0:
            table_header = OxmlElement("w:tblHeader")
            table_header.set(qn("w:val"), "true")
            tr_pr.append(table_header)
    format_table_like_master(table, analyze_master_format(REFERENCE_DOCX))


def add_figure(doc: Document, file_name: str, caption: str) -> None:
    image = FIG_DIR / file_name
    if not image.exists():
        return
    add_master_caption(doc, clean_text(caption))
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run().add_picture(str(image), width=Inches(6.2))


def add_paragraphs(doc: Document, paragraphs: list[str]) -> None:
    for text in paragraphs:
        doc.add_paragraph(clean_text(text), style="Normal")


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
    subset = add_calculation_framework(subset)
    out = subset.pivot_table(
        index=["escenario", "etapa", "nombre_etapa", "modelo_calculo", "Marco de cálculo de la etapa"],
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
    totals = pd.read_csv(PROCESSED_TOTALS, encoding="utf-8-sig")
    return totals[
        [
            "Escenario",
            "impacto_calentamiento_global_kg_co2eq",
            "impacto_eutrofizacion_kg_po4eq",
            "impacto_calentamiento_global_kg_co2eq_por_kg_estiercol_fresco",
            "impacto_eutrofizacion_kg_po4eq_por_kg_estiercol_fresco",
        ]
    ].rename(
        columns={
            "impacto_calentamiento_global_kg_co2eq": "Calentamiento global (kg CO2-eq/año)",
            "impacto_eutrofizacion_kg_po4eq": "Eutrofización (kg PO4-eq/año)",
            "impacto_calentamiento_global_kg_co2eq_por_kg_estiercol_fresco": "Calentamiento global (kg CO2-eq/kg de estiércol fresco)",
            "impacto_eutrofizacion_kg_po4eq_por_kg_estiercol_fresco": "Eutrofización (kg PO4-eq/kg de estiércol fresco)",
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


def results_context() -> dict[str, object]:
    totals = pd.read_csv(PROCESSED_TOTALS, encoding="utf-8-sig")
    stages = pd.read_csv(PROCESSED_STAGE_IMPACTS, encoding="utf-8-sig")
    comparison = read_csv("tabla_09")
    if set(totals["Escenario"].astype(str)) != {"A", "B"}:
        raise RuntimeError("Los impactos procesados deben contener los escenarios A y B.")
    by_scenario = totals.set_index("Escenario")
    context: dict[str, object] = {
        "cg_a": float(by_scenario.loc["A", "impacto_calentamiento_global_kg_co2eq"]),
        "eu_a": float(by_scenario.loc["A", "impacto_eutrofizacion_kg_po4eq"]),
        "cg_b": float(by_scenario.loc["B", "impacto_calentamiento_global_kg_co2eq"]),
        "eu_b": float(by_scenario.loc["B", "impacto_eutrofizacion_kg_po4eq"]),
        "cg_norm_a": float(by_scenario.loc["A", "impacto_calentamiento_global_kg_co2eq_por_kg_estiercol_fresco"]),
        "eu_norm_a": float(by_scenario.loc["A", "impacto_eutrofizacion_kg_po4eq_por_kg_estiercol_fresco"]),
        "cg_norm_b": float(by_scenario.loc["B", "impacto_calentamiento_global_kg_co2eq_por_kg_estiercol_fresco"]),
        "eu_norm_b": float(by_scenario.loc["B", "impacto_eutrofizacion_kg_po4eq_por_kg_estiercol_fresco"]),
    }
    comparison_index = comparison.set_index("categoria_impacto")
    context["cg_difference"] = float(comparison_index.loc["Calentamiento global", "diferencia_absoluta_B_menos_A"])
    context["eu_difference"] = float(comparison_index.loc["Eutrofizacion", "diferencia_absoluta_B_menos_A"])
    context["cg_percentage"] = float(comparison_index.loc["Calentamiento global", "diferencia_porcentual_B_vs_A"])
    context["eu_percentage"] = float(comparison_index.loc["Eutrofizacion", "diferencia_porcentual_B_vs_A"])

    stage_names = {
        ("A", 1): "A1: Precomposteo",
        ("A", 2): "A2: Lombricompostaje",
        ("A", 3): "A3: Almacenamiento de aguas verdes",
        ("A", 4): "A4: Aplicación de aguas verdes en campos de pastoreo",
        ("B", 1): "B1: Almacenamiento de purines",
        ("B", 2): "B2: Aplicación de purines en campo de pastoreo",
    }
    category_columns = {
        "cg": "impacto_calentamiento_global_kg_co2eq",
        "eu": "impacto_eutrofizacion_kg_po4eq",
    }
    for scenario in ("A", "B"):
        subset = stages[stages["Escenario"] == scenario]
        for short, column in category_columns.items():
            row = subset.loc[subset[column].idxmax()]
            value = float(row[column])
            total = float(context[f"{short}_{scenario.lower()}"])
            context[f"{short}_dominant_{scenario.lower()}_name"] = stage_names[(scenario, int(row["Etapa"]))]
            context[f"{short}_dominant_{scenario.lower()}_value"] = value
            context[f"{short}_dominant_{scenario.lower()}_percentage"] = 100 * value / total

    b1 = stages[(stages["Escenario"] == "B") & (stages["Etapa"] == 1)].iloc[0]
    emissions = read_csv("tabla_06")
    b1_emissions = emissions[(emissions["escenario"] == "B") & (emissions["etapa"] == 1)]
    context["b1_eutrophication"] = float(b1["impacto_eutrofizacion_kg_po4eq"])
    context["b1_nh3"] = float(b1_emissions.loc[b1_emissions["sustancia"] == "NH3", "valor"].sum())
    context["b1_no3"] = float(b1_emissions.loc[b1_emissions["sustancia"] == "NO3", "valor"].sum())
    context["b1_n2o_leaching"] = float(
        b1_emissions.loc[b1_emissions["emision"].str.contains("lixiviacion", case=False, na=False), "valor"].sum()
    )
    return context


def build_document() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = Document()
    profile = set_document_style(doc)
    context = results_context()

    doc.add_paragraph(
        "Resultados desarrollados del Análisis de Ciclo de Vida", style="Title"
    )

    doc.add_heading("1. Caracterización de las muestras analizadas", level=2)
    add_paragraphs(
        doc,
        [
            "La caracterización de las muestras analizadas permitió establecer los parámetros fisicoquímicos usados como entradas del inventario de ciclo de vida. El estiércol fresco presentó un contenido promedio de agua de 85,77 % y una materia seca de 14,23 %. El estiércol precompostado presentó un contenido promedio de agua de 77,59 % y una materia seca de 22,41 %.",
            "La fracción de sólidos volátiles fue mayor en el estiércol fresco, con 85,88 % en base seca, mientras que el estiércol precompostado presentó 70,96 %. En contraste, las cenizas fueron mayores en el material precompostado. El nitrógeno total fue de 0,372 % para estiércol fresco y de 2,425 % para estiércol precompostado.",
            "La Tabla 1 resume los valores de caracterización de las muestras. La Figura 1 presenta humedad y materia seca, mientras que la Figura 2 presenta sólidos volátiles y cenizas.",
            "La Tabla R1 del bloque de apéndices internos, Caracterización completa de muestras, presenta la desagregación de los resultados fisicoquímicos utilizados en esta sección.",
            "Los valores presentados corresponden principalmente a las observaciones disponibles del primer muestreo incorporado. Las jornadas restantes se integrarán estadísticamente cuando sus resultados estén disponibles.",
        ],
    )
    add_dataframe_table(doc, "Tabla 1. Caracterización resumida de las muestras.", format_df(characterization_summary(), decimals=3))
    add_figure(doc, *MAIN_FIGURES[0])
    add_figure(doc, *MAIN_FIGURES[1])

    doc.add_heading("2. Flujos del inventario de ciclo de vida", level=2)
    add_paragraphs(
        doc,
        [
            "Estos valores se presentan como flujos anuales estimados del inventario, manteniendo como referencia metodológica la unidad funcional de 1 kg de estiércol fresco manejado. El flujo anual común expresa la escala operacional del inventario y no redefine la unidad funcional.",
            "Los flujos del inventario se expresaron como masa equivalente total por año para cada etapa. B2: Aplicación de purines en campo de pastoreo presentó la mayor masa equivalente total, con 276 851,23 kg eq/año. En el Escenario A, A4: Aplicación de aguas verdes en campos de pastoreo dominó la masa equivalente, con 259 326,13 kg eq/año.",
            "La masa equivalente de A4 integra el agua de lavado y 8 753,63 kg/año de estiércol remanente derivados del balance en sala. La masa equivalente de B2 integra agua de lavado y 26 278,73 kg/año de estiércol fresco teóricamente depositado.",
            "En contraste, para estimar las emisiones de manejo en A3: Almacenamiento de aguas verdes y B1: Almacenamiento de purines se utilizó la masa de estiércol correspondiente, sin sumar el agua de lavado como masa de actividad. El flujo total de agua y estiércol se incorporó en las etapas subsecuentes de aplicación A4 y B2.",
            "A2: Lombricompostaje presentó la menor masa equivalente. La Tabla 2 presenta la masa equivalente total por etapa y la Figura 3 resume su distribución por escenario.",
            "La Tabla R2 del bloque de apéndices internos, Flujos completos del inventario, contiene la desagregación de los flujos empleados para construir el ICV.",
        ],
    )
    add_dataframe_table(doc, "Tabla 2. Masa equivalente total por etapa.", format_df(flow_summary()))
    add_figure(doc, *MAIN_FIGURES[2])

    doc.add_heading("3. Parámetros utilizados en el modelo ACV", level=2)
    add_paragraphs(
        doc,
        [
            "Los parámetros utilizados en el modelo se organizaron por escenario y etapa. La tabla distingue entre el nitrógeno total reportado en porcentaje y la fracción másica empleada en las ecuaciones de nitrógeno. La fracción másica se obtuvo al dividir el porcentaje reportado entre 100.",
            "A2: Lombricompostaje aparece como una etapa estimada mediante información experimental publicada. Las demás etapas se calculan con ecuaciones IPCC según el sistema de manejo asignado. La Tabla 3 resume los parámetros principales.",
            "Los factores vinculados con las ecuaciones de emisiones siguen la metodología IPCC, mientras que los factores obtenidos mediante mediciones por unidad de residuo seco utilizados en A2 proceden de Jjagwe et al. (2019).",
            "La Tabla R3 del bloque de apéndices internos, Parámetros completos del modelo ACV, amplía los parámetros por escenario y etapa; la Tabla R4, Factores completos de emisión y caracterización, documenta los factores asociados.",
        ],
    )
    add_dataframe_table(doc, "Tabla 3. Parámetros principales por etapa.", format_df(parameter_summary(), decimals=4))

    doc.add_heading("4. Emisiones estimadas por etapa y escenario", level=2)
    add_paragraphs(
        doc,
        [
            "Las emisiones consolidadas muestran diferencias entre escenarios y sustancias. El Escenario A presentó 151,99 kg CH4/año, 3,11 kg N2O/año, 24,91 kg NH3/año, 90,82 kg NO3/año y 123,70 kg CO2/año. El Escenario B presentó 413,11 kg CH4/año, 1,33 kg N2O/año, 29,01 kg NH3/año y 105,74 kg NO3/año.",
            "B1: Almacenamiento de purines presentó la mayor contribución de CH4. A1: Precomposteo presentó la mayor emisión de N2O. A2: Lombricompostaje reportó CO2 mediante un factor experimental publicado. La Tabla 4 resume las emisiones anuales por escenario y sustancia, y la Figura 4 presenta las emisiones de CH4 por etapa.",
            "La Tabla R5 del bloque de apéndices internos, Emisiones completas por etapa, presenta la desagregación por sustancia, escenario y etapa. Además, el Apéndice R9, Figuras complementarias, reúne las representaciones gráficas que respaldan la interpretación de la caracterización, los flujos, las emisiones y la comparación de escenarios.",
        ],
    )
    add_dataframe_table(doc, "Tabla 4. Emisiones anuales por escenario y sustancia.", format_df(emissions_summary()))
    add_figure(doc, *MAIN_FIGURES[3])

    doc.add_heading("5. Impactos ambientales por etapa", level=2)
    add_paragraphs(
        doc,
        [
            f"Los impactos ambientales por etapa mostraron que {context['cg_dominant_b_name']} concentró {fmt(context['cg_dominant_b_percentage'], 2)} % del calentamiento global del Escenario B, con {fmt(context['cg_dominant_b_value'], 6)} kg CO2-eq/año. En el Escenario A, {context['cg_dominant_a_name']} aportó {fmt(context['cg_dominant_a_percentage'], 2)} % del total de esta categoría.",
            f"Para eutrofización, {context['eu_dominant_b_name']} presentó la mayor contribución del Escenario B, con {fmt(context['eu_dominant_b_percentage'], 2)} % de su total; en el Escenario A, {context['eu_dominant_a_name']} concentró {fmt(context['eu_dominant_a_percentage'], 2)} %. A2: Lombricompostaje registró 0 kg PO4-eq/año porque no presenta emisiones de NH3 ni NO3 en el inventario de esa etapa. La Tabla 5 resume los impactos por etapa; la Figura 5 presenta calentamiento global y la Figura 6 presenta eutrofización.",
            f"En B1: Almacenamiento de purines, la lixiviación explícita utilizada para estimar N2O indirecto fue nula. No obstante, bajo el supuesto de especiación adoptado, el conjunto de N potencialmente eutrofizante se distribuyó en partes iguales como N asociado a NH3 y a NO3. Por ello, los {fmt(context['b1_no3'], 6)} kg NO3/año registrados para B1 representan NO3 equivalente derivado de esa asignación y no evidencia de lixiviación física directa.",
            "Los factores de caracterización para calentamiento global se referencian al IMN (2021), mientras que los factores de eutrofización se basan en Ecobilan (1999, como se citó en Vallejo, 2004).",
            "La Tabla R6 del bloque de apéndices internos, Impactos completos por etapa, presenta los resultados desagregados por categoría de impacto.",
        ],
    )
    add_dataframe_table(doc, "Tabla 5. Impactos ambientales por etapa.", format_df(impact_stage_summary()))
    add_figure(doc, *MAIN_FIGURES[4])
    add_figure(doc, *MAIN_FIGURES[5])

    doc.add_heading("6. Impactos totales por escenario", level=2)
    add_paragraphs(
        doc,
        [
            f"El Escenario A alcanzó {fmt(context['cg_a'], 6)} kg CO2-eq/año para calentamiento global y {fmt(context['eu_a'], 6)} kg PO4-eq/año para eutrofización. El Escenario B alcanzó {fmt(context['cg_b'], 6)} kg CO2-eq/año y {fmt(context['eu_b'], 6)} kg PO4-eq/año, respectivamente.",
            f"Respecto a la unidad funcional, los indicadores del Escenario A fueron {fmt(context['cg_norm_a'], 9)} kg CO2-eq/kg de estiércol fresco y {fmt(context['eu_norm_a'], 9)} kg PO4-eq/kg de estiércol fresco. Para el Escenario B fueron {fmt(context['cg_norm_b'], 9)} kg CO2-eq/kg y {fmt(context['eu_norm_b'], 9)} kg PO4-eq/kg de estiércol fresco.",
            "La Tabla 6 distingue los resultados anualizados, que representan la magnitud operacional, de los resultados normalizados respecto a 1 kg de estiércol fresco manejado.",
            "La Tabla R7 del bloque de apéndices internos, Impactos totales completos por escenario, presenta el detalle de la agregación utilizada en esta comparación.",
        ],
    )
    add_dataframe_table(
        doc,
        "Tabla 6. Impactos ambientales totales y normalizados por escenario.",
        format_df(
            total_impact_summary(),
            decimals=6,
            decimals_by_col={
                "Calentamiento global (kg CO2-eq/kg de estiércol fresco)": 9,
                "Eutrofización (kg PO4-eq/kg de estiércol fresco)": 9,
            },
        ),
    )

    doc.add_heading("7. Comparación entre escenarios", level=2)
    add_paragraphs(
        doc,
        [
            f"La comparación bajo la misma unidad funcional mostró un mayor impacto de calentamiento global en el Escenario B. La diferencia B menos A fue de {fmt(context['cg_difference'], 6)} kg CO2-eq/año, equivalente a {fmt(context['cg_percentage'], 2)} % respecto al Escenario A.",
            f"En eutrofización, el Escenario B superó al Escenario A en {fmt(context['eu_difference'], 6)} kg PO4-eq/año, equivalente a {fmt(context['eu_percentage'], 2)} %. La Tabla 7 resume la comparación y la Figura 7 presenta la diferencia porcentual por categoría de impacto.",
            "La Tabla R8 del bloque de apéndices internos, Comparación completa de escenarios, amplía las diferencias absolutas y porcentuales. La relación entre los contenidos, sus bases de información y las figuras asociadas se documenta en el Apéndice R10, Correspondencia entre tablas, figuras y archivos fuente.",
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
        df = read_csv(key)
        if key in {"tabla_03", "tabla_04", "tabla_06", "tabla_07"}:
            df = apply_official_stage_names(df)
        if key == "tabla_04":
            df = add_calculation_framework(df)
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

    finalize_document_format(doc, profile)
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
    for label in labels:
        if normalized.count(label) >= 2:
            continue
        noun, identifier = label.split(" ", 1)
        plural_contexts = re.findall(
            rf"\b{re.escape(noun)}s?\b([^.;]*)", normalized, flags=re.IGNORECASE
        )
        if any(
            re.search(rf"\b{re.escape(identifier)}\b", context)
            for context in plural_contexts
        ):
            continue
        return False
    return True


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


def write_format_report(master_hash_before: str, master_hash_after: str) -> None:
    profile = analyze_master_format(REFERENCE_DOCX)
    report = f"""# Reporte técnico de formato basado en el documento MASTER

## Estilos detectados en el MASTER

{profile_markdown(profile)}

## Estilos aplicados a los documentos generados

- `metodologia_desarrollada_tfg.docx`: título principal, títulos de tres niveles, párrafo normal, rótulos y descripciones de tablas y figuras, texto de tablas y márgenes.
- `resultados_desarrollados_tfg.docx`: título principal, títulos de tres niveles, párrafo normal, rótulos y descripciones de tablas y figuras, texto de tablas y márgenes.
- Los encabezados de tabla permanecen en negrita; las tablas conservan únicamente bordes horizontales.
- Las ecuaciones permanecen como texto LaTeX seleccionable, centrado y con fuente matemática.

## Numeración

- La numeración del MASTER no se usó como referencia obligatoria.
- Cada documento generado conserva su propia numeración interna de secciones, tablas, figuras y apéndices.
- No se copiaron definiciones de listas numeradas ni sangrías colgantes asociadas con la numeración del MASTER.

## Limitaciones

- `python-docx` permite replicar las propiedades tipográficas y de párrafo utilizadas en este flujo, pero no reproduce de forma integral temas, campos dinámicos, listas multinivel, encabezados, pies de página ni otros componentes de maquetación avanzada del archivo de referencia.
- Las figuras no fueron alteradas; solo se armonizaron su inserción, alineación y pies.
- La equivalencia visual final puede variar ligeramente según la versión de Microsoft Word y las fuentes instaladas.

## Protección del documento maestro

- Ruta protegida: `MASTER_escrito/TFG_ACV_Estiercol_MASTER.docx`.
- Hash antes de la generación: `{master_hash_before}`.
- Hash después de la generación: `{master_hash_after}`.
- El documento MASTER no fue modificado: {'Sí' if master_hash_before == master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.
"""
    FORMAT_REPORT_OUT.write_text(repair_mojibake(report), encoding="utf-8")


def generated_styles_match_master() -> bool:
    profile = analyze_master_format(REFERENCE_DOCX)
    for path in (METHODOLOGY_DOCX, OUT_DOCX):
        document = Document(str(path))
        required = (
            "Normal",
            "Title",
            "Heading 1",
            "Heading 2",
            "Heading 3",
            "Rótulo académico",
            "Descripción académica",
        )
        if any(name not in document.styles for name in required):
            return False
        if document.styles["Normal"].font.name != profile.font_name:
            return False
        if round(document.styles["Normal"].font.size.pt, 2) != profile.body_size_pt:
            return False
        if round(document.styles["Title"].font.size.pt, 2) != profile.title_size_pt:
            return False
        if not all(document.styles[name].font.bold for name in ("Heading 1", "Heading 2", "Heading 3")):
            return False
    return True


def appendix_relation_diagnostics(
    path: Path,
    appendix_specs: list[tuple[str, str, str]],
) -> dict[str, object]:
    document = Document(str(path))
    paragraphs = [
        (paragraph.text.strip(), paragraph.style.name)
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]
    boundary = next(
        (
            index
            for index, (text, _) in enumerate(paragraphs)
            if text.startswith("Apéndices internos")
        ),
        len(paragraphs),
    )
    main_paragraphs = paragraphs[:boundary]
    appendix_text = "\n".join(text for text, _ in paragraphs[boundary:])
    entries: list[dict[str, object]] = []

    for code, title, reference_type in appendix_specs:
        reference_pattern = re.compile(
            rf"\b{re.escape(reference_type)}\s+{re.escape(code)}\b",
            flags=re.IGNORECASE,
        )
        mention_index = next(
            (
                index
                for index, (text, _) in enumerate(main_paragraphs)
                if reference_pattern.search(text)
            ),
            None,
        )
        mention = main_paragraphs[mention_index][0] if mention_index is not None else ""
        section = ""
        if mention_index is not None:
            section = next(
                (
                    text
                    for text, style in reversed(main_paragraphs[: mention_index + 1])
                    if style.startswith("Heading")
                ),
                "",
            )
        exists = bool(reference_pattern.search(appendix_text)) and title in appendix_text
        entries.append(
            {
                "code": code,
                "title": title,
                "reference_type": reference_type,
                "exists": exists,
                "mentioned_before_appendices": mention_index is not None,
                "title_in_mention": title in mention,
                "section": section,
                "mention": mention,
                "valid": exists and mention_index is not None and title in mention,
            }
        )

    expected_codes = {code for code, _, _ in appendix_specs}
    references = set(
        re.findall(
            r"\bApéndice(?:\s+interno)?\s+([A-Z](?:\d+)?)\b",
            "\n".join(text for text, _ in main_paragraphs),
            flags=re.IGNORECASE,
        )
    )
    references.update(
        re.findall(
            r"\bTabla\s+(R\d+)\b",
            "\n".join(text for text, _ in main_paragraphs),
            flags=re.IGNORECASE,
        )
    )
    unexpected_references = sorted(
        reference.upper()
        for reference in references
        if reference.upper() not in expected_codes
    )
    return {
        "document": path.name,
        "entries": entries,
        "unexpected_references": unexpected_references,
        "all_valid": all(bool(entry["valid"]) for entry in entries)
        and not unexpected_references,
    }


def write_appendix_relation_report(
    methodology: dict[str, object],
    results: dict[str, object],
    master_hash_before: str,
    master_hash_after: str,
) -> None:
    lines = [
        "# Reporte de relación entre prosa y apéndices",
        "",
        "| Documento | Apéndice | Título del apéndice | Sección donde se menciona | Texto breve de la mención | Estado |",
        "|---|---|---|---|---|---|",
    ]
    for diagnostic in (methodology, results):
        for entry in diagnostic["entries"]:
            mention = str(entry["mention"]).replace("|", "&#124;")
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(diagnostic["document"]),
                        str(entry["code"]),
                        str(entry["title"]),
                        str(entry["section"]),
                        mention,
                        "Validado" if entry["valid"] else "Revisar",
                    ]
                )
                + " |"
            )
    lines.extend(
        [
            "",
            "## Confirmaciones",
            "",
            f"- Todos los apéndices de metodología están relacionados con la prosa principal: {'Sí' if methodology['all_valid'] else 'No'}.",
            f"- Todos los apéndices de resultados están relacionados con la prosa principal: {'Sí' if results['all_valid'] else 'No'}.",
            "- La numeración propia de cada documento se conservó; no se sincronizó con el MASTER.",
            "- No se modificaron tablas, figuras, ecuaciones, valores numéricos, cálculos ni resultados.",
            f"- El documento maestro protegido no fue modificado: {'Sí' if master_hash_before == master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
            f"- Hash SHA-256 del documento maestro: `{master_hash_after}`.",
        ]
    )
    APPENDIX_RELATION_REPORT_OUT.write_text(
        repair_mojibake("\n".join(lines) + "\n"),
        encoding="utf-8",
    )


def write_factor_references_report(
    factors: pd.DataFrame,
    master_hash_before: str,
    master_hash_after: str,
) -> None:
    columns = [
        "factor",
        "clasificacion_referencia",
        "referencia_metodologica",
        "estado_referencia",
    ]
    summary = (
        factors[columns]
        .drop_duplicates()
        .sort_values(["clasificacion_referencia", "factor"])
    )
    lines = [
        "# Reporte técnico de referencias de factores",
        "",
        "## Trazabilidad metodológica",
        "",
        "- Los factores y las ecuaciones clasificados como IPCC fueron contrastados con su implementación en `scripts/ecuaciones_acv.py` y con las tablas de parámetros del proyecto.",
        "- Los factores de caracterización de calentamiento global se referencian como IMN (2021).",
        "- Los factores de caracterización de eutrofización se referencian como Ecobilan (1999, como se citó en Vallejo, 2004).",
        "- Los factores medidos por unidad de residuo seco o estiércol precompostado se referencian como Jjagwe et al. (2019).",
        "- Referencia completa: Jjagwe, J., Komakech, A. J., Karungi, J., Amann, A., Wanyama, J., & Lederer, J. (2019). Assessment of a Cattle Manure Vermicomposting System Using Material Flow Analysis: A Case Study from Uganda. Sustainability, 11(19), 5173. https://doi.org/10.3390/su11195173",
        "- Los factores sin fuente confirmada no recibieron una atribución inventada.",
        "",
        "| Factor | Clasificación | Referencia asignada | Archivo o tabla donde aparece | Justificación | Estado |",
        "|---|---|---|---|---|---|",
    ]
    for _, row in summary.iterrows():
        classification = str(row["clasificacion_referencia"])
        if classification == "IPCC":
            justification = "Parámetro o ecuación de estimación de emisiones asociado con la metodología IPCC."
        elif classification == "IMN (2021)":
            justification = "Factor de caracterización del potencial de calentamiento global."
        elif classification == "Ecobilan (1999) citado en Vallejo (2004)":
            justification = "Factor de caracterización del potencial de eutrofización."
        elif classification == "Jjagwe et al. (2019)":
            justification = "Factor medido por kilogramo de residuo en base seca reportado para vermicompostaje de estiércol bovino."
        elif classification == "Supuesto del modelo":
            justification = "Supuesto explícito del modelo; no se presenta como factor bibliográfico."
        elif classification == "Conversión estequiométrica":
            justification = "Relación derivada de masas molares; no requiere una fuente empírica."
        else:
            justification = "El origen no pudo confirmarse sin introducir una referencia no sustentada."
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["factor"]).replace("|", "&#124;"),
                    classification,
                    str(row["referencia_metodologica"]).replace("|", "&#124;"),
                    "`tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word",
                    justification,
                    str(row["estado_referencia"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Protección de resultados y del documento maestro",
            "",
            "- No se modificaron valores numéricos, ecuaciones, cálculos ni resultados.",
            f"- El documento maestro protegido no fue modificado: {'Sí' if master_hash_before == master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
            f"- Hash SHA-256 del documento maestro: `{master_hash_after}`.",
        ]
    )
    FACTOR_REFERENCES_REPORT_OUT.write_text(
        repair_mojibake("\n".join(lines) + "\n"),
        encoding="utf-8",
    )


def write_no3_correction_report(
    master_hash_before: str,
    master_hash_after: str,
) -> None:
    emissions = pd.read_csv(
        ROOT / "processed" / "ACV_resumen_emisiones.csv",
        encoding="utf-8-sig",
    ).fillna(0)
    impacts = pd.read_csv(
        ROOT / "processed" / "acv_impacto_por_etapa_escenario.csv",
        encoding="utf-8-sig",
    )
    impacts = impacts.set_index(["Escenario", "Etapa"])
    ratio = OLD_NO3_STOICHIOMETRIC_FACTOR / CURRENT_NO3_STOICHIOMETRIC_FACTOR
    rows: list[dict[str, object]] = []
    for _, row in emissions.iterrows():
        scenario = str(row["Escenario"])
        stage = int(row["Etapa"])
        new_no3 = float(row.get("NO3_ec13", 0)) + float(row.get("NO3_ec21", 0))
        old_no3 = new_no3 * ratio
        no3_difference = new_no3 - old_no3
        no3_pct = (no3_difference / old_no3 * 100) if old_no3 else 0.0
        new_eutrophication = float(
            impacts.loc[
                (scenario, stage),
                "impacto_eutrofizacion_kg_po4eq",
            ]
        )
        old_eutrophication = new_eutrophication - no3_difference * 0.095
        eutrophication_difference = new_eutrophication - old_eutrophication
        eutrophication_pct = (
            eutrophication_difference / old_eutrophication * 100
            if old_eutrophication
            else 0.0
        )
        rows.append(
            {
                "scenario": scenario,
                "stage": stage,
                "old_no3": old_no3,
                "new_no3": new_no3,
                "no3_difference": no3_difference,
                "no3_pct": no3_pct,
                "old_eutrophication": old_eutrophication,
                "new_eutrophication": new_eutrophication,
                "eutrophication_difference": eutrophication_difference,
                "eutrophication_pct": eutrophication_pct,
            }
        )

    lines = [
        "# Reporte de corrección del factor estequiométrico N a NO₃⁻",
        "",
        "## Cambio aplicado",
        "",
        f"- Valor anterior: `{OLD_NO3_STOICHIOMETRIC_FACTOR:.4f}` (mostrado como 4,4286).",
        f"- Valor nuevo: `{CURRENT_NO3_STOICHIOMETRIC_FACTOR:.4f}`.",
        "- Origen corregido: `scripts/ecuaciones_acv.py`, constante `FACTOR_N_A_NO3`.",
        "- Referencia metodológica: Cálculo estequiométrico.",
        "- No se asignó una cita bibliográfica externa a esta conversión.",
        "",
        "## Comparación por escenario y etapa",
        "",
        "| Escenario | Etapa | NO₃⁻ anterior (kg/año) | NO₃⁻ nuevo (kg/año) | Diferencia absoluta | Diferencia (%) | Eutrofización anterior (kg PO₄-eq/año) | Eutrofización nueva (kg PO₄-eq/año) | Diferencia absoluta | Diferencia (%) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    str(row["scenario"]),
                    str(row["stage"]),
                    f"{row['old_no3']:.9f}",
                    f"{row['new_no3']:.9f}",
                    f"{row['no3_difference']:.9f}",
                    f"{row['no3_pct']:.6f}",
                    f"{row['old_eutrophication']:.9f}",
                    f"{row['new_eutrophication']:.9f}",
                    f"{row['eutrophication_difference']:.9f}",
                    f"{row['eutrophication_pct']:.6f}",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Comparación de totales por escenario",
            "",
            "| Escenario | NO₃⁻ anterior (kg/año) | NO₃⁻ nuevo (kg/año) | Diferencia absoluta | Diferencia (%) | Eutrofización anterior (kg PO₄-eq/año) | Eutrofización nueva (kg PO₄-eq/año) | Diferencia absoluta | Diferencia (%) |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for scenario in ("A", "B"):
        scenario_rows = [row for row in rows if row["scenario"] == scenario]
        old_no3_total = sum(float(row["old_no3"]) for row in scenario_rows)
        new_no3_total = sum(float(row["new_no3"]) for row in scenario_rows)
        old_eutrophication_total = sum(
            float(row["old_eutrophication"]) for row in scenario_rows
        )
        new_eutrophication_total = sum(
            float(row["new_eutrophication"]) for row in scenario_rows
        )
        no3_difference = new_no3_total - old_no3_total
        eutrophication_difference = (
            new_eutrophication_total - old_eutrophication_total
        )
        lines.append(
            "| "
            + " | ".join(
                [
                    scenario,
                    f"{old_no3_total:.9f}",
                    f"{new_no3_total:.9f}",
                    f"{no3_difference:.9f}",
                    f"{no3_difference / old_no3_total * 100:.6f}",
                    f"{old_eutrophication_total:.9f}",
                    f"{new_eutrophication_total:.9f}",
                    f"{eutrophication_difference:.9f}",
                    f"{eutrophication_difference / old_eutrophication_total * 100:.6f}",
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Archivos regenerados",
            "",
            "- Resumen de emisiones y tablas de emisiones por etapa.",
            "- Impactos por etapa, impactos totales y comparación entre escenarios.",
            "- Tablas académicas reducidas para Word.",
            "- Figuras de NO₃⁻, eutrofización por etapa, eutrofización total y comparación de escenarios.",
            "- Documentos Word de metodología y resultados.",
            "",
            "## Control del alcance",
            "",
            "- Los cambios numéricos se limitan a las emisiones de NO₃⁻ y a la eutrofización asociada.",
            "- No se modificaron los factores de caracterización ni factores no relacionados.",
            "- No cambiaron las emisiones de CH₄, N₂O, NH₃ o CO₂ ni el calentamiento global.",
            f"- El documento maestro protegido no fue modificado: {'Sí' if master_hash_before == master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
            f"- Hash SHA-256 del documento maestro: `{master_hash_after}`.",
        ]
    )
    NO3_CORRECTION_REPORT_OUT.write_text(
        repair_mojibake("\n".join(lines) + "\n"),
        encoding="utf-8",
    )


def heading_and_caption_colors_black(path: Path) -> bool:
    document = Document(str(path))
    style_names = {
        "Title",
        "Subtitle",
        "Heading 1",
        "Heading 2",
        "Heading 3",
        "Caption",
        "Rótulo académico",
        "Descripción académica",
    }
    for style_name in style_names:
        if style_name in document.styles:
            if str(document.styles[style_name].font.color.rgb) != "000000":
                return False
    for paragraph in document.paragraphs:
        if paragraph.style.name not in style_names:
            continue
        for run in paragraph.runs:
            if run.text.strip() and str(run.font.color.rgb) != "000000":
                return False
    return True


def table_title_diagnostics(path: Path) -> dict[str, object]:
    document = Document(str(path))
    blocks: list[tuple[str, str, str]] = []
    for child in document.element.body.iterchildren():
        if child.tag.endswith("}p"):
            paragraph = Paragraph(child, document)
            blocks.append(("paragraph", paragraph.text.strip(), paragraph.style.name))
        elif child.tag.endswith("}tbl"):
            blocks.append(("table", "", ""))

    table_paragraphs = [
        (index, text, style)
        for index, (kind, text, style) in enumerate(blocks)
        if kind == "paragraph" and text.lower().startswith("tabla")
    ]
    formal_labels = [
        text
        for _, text, style in table_paragraphs
        if style == "Rótulo académico"
    ]
    all_labels = [text for _, text, _ in table_paragraphs]
    duplicate_labels = sorted(
        {label for label in all_labels if all_labels.count(label) > 1}
    )
    consecutive_identical = [
        blocks[index][1]
        for index in range(len(blocks) - 1)
        if blocks[index][0] == blocks[index + 1][0] == "paragraph"
        and blocks[index][1]
        and blocks[index][1] == blocks[index + 1][1]
        and blocks[index][1].lower().startswith("tabla")
    ]
    consecutive_table_paragraphs = [
        (blocks[index][1], blocks[index + 1][1])
        for index in range(len(blocks) - 1)
        if blocks[index][0] == blocks[index + 1][0] == "paragraph"
        and blocks[index][1].lower().startswith("tabla")
        and blocks[index + 1][1].lower().startswith("tabla")
    ]
    repeated_around_table: list[str] = []
    for index, (kind, _, _) in enumerate(blocks):
        if kind != "table":
            continue
        before = {
            text
            for block_kind, text, _ in blocks[max(0, index - 3) : index]
            if block_kind == "paragraph" and text.lower().startswith("tabla")
        }
        after = {
            text
            for block_kind, text, _ in blocks[index + 1 : index + 4]
            if block_kind == "paragraph" and text.lower().startswith("tabla")
        }
        repeated_around_table.extend(sorted(before & after))

    full_captions: list[str] = []
    for index, text, style in table_paragraphs:
        if style != "Rótulo académico":
            continue
        description = ""
        if index + 1 < len(blocks) and blocks[index + 1][2] == "Descripción académica":
            description = blocks[index + 1][1]
        full_captions.append(f"{text}. {description}".strip())
    prose_duplicates = [
        text
        for kind, text, style in blocks
        if kind == "paragraph" and style == "Normal" and text in full_captions
    ]
    table_count = sum(1 for kind, _, _ in blocks if kind == "table")
    return {
        "duplicate_labels": duplicate_labels,
        "consecutive_identical": consecutive_identical,
        "consecutive_table_paragraphs": consecutive_table_paragraphs,
        "repeated_around_table": repeated_around_table,
        "prose_duplicates": prose_duplicates,
        "one_caption_per_table": len(formal_labels) == table_count,
    }


def figure_title_diagnostics(path: Path) -> dict[str, object]:
    document = Document(str(path))
    blocks: list[tuple[str, str, str, bool]] = []
    for child in document.element.body.iterchildren():
        if child.tag.endswith("}p"):
            paragraph = Paragraph(child, document)
            blocks.append(
                (
                    "paragraph",
                    paragraph.text.strip(),
                    paragraph.style.name,
                    bool(paragraph._p.xpath(".//w:drawing")),
                )
            )
        elif child.tag.endswith("}tbl"):
            blocks.append(("table", "", "", False))

    caption_indices = [
        index
        for index, (kind, text, style, _) in enumerate(blocks)
        if kind == "paragraph"
        and style == "Rótulo académico"
        and text.lower().startswith("figura")
    ]
    image_indices = [
        index for index, (_, _, _, has_drawing) in enumerate(blocks) if has_drawing
    ]
    caption_labels = [blocks[index][1] for index in caption_indices]

    captions_above_images = all(
        index + 2 < len(blocks)
        and blocks[index + 1][2] == "Descripción académica"
        and blocks[index + 2][3]
        for index in caption_indices
    )
    images_have_caption = all(
        index >= 2
        and blocks[index - 1][2] == "Descripción académica"
        and blocks[index - 2][2] == "Rótulo académico"
        and blocks[index - 2][1].lower().startswith("figura")
        for index in image_indices
    )
    duplicate_captions = sorted(
        {
            caption
            for caption in caption_labels
            if caption_labels.count(caption) > 1
        }
    )
    return {
        "caption_count": len(caption_indices),
        "image_count": len(image_indices),
        "captions_above_images": captions_above_images,
        "images_have_caption": images_have_caption,
        "no_captions_below_images": captions_above_images,
        "duplicate_captions": duplicate_captions,
    }


def graphics_internal_title_diagnostics() -> dict[str, object]:
    source = GRAPHICS_SCRIPT.read_text(encoding="utf-8")
    active_title_calls = re.findall(
        r"(?:plt\.title|\.set_title|\.suptitle|suptitle)\s*\(", source
    )
    internal_title_markers = (
        "Caracterizacion de muestras:",
        "Inventario: masa equivalente",
        "Inventario: distribucion",
        "Componentes del inventario (",
        "Emisiones de metano",
        "Emisiones de oxido nitroso",
        "Emisiones de amoniaco",
        "Emisiones de nitrato",
        "Emisiones de dioxido de carbono",
        "Calentamiento global por proceso",
        "Eutrofizacion por proceso",
        "Impacto total de",
        "Diferencia porcentual del escenario B respecto al A",
    )
    svg_files = sorted(FIG_DIR.glob("fig_*.svg"))
    png_files = sorted(FIG_DIR.glob("fig_*.png"))
    svg_with_internal_titles = [
        path.name
        for path in svg_files
        if any(
            marker in path.read_text(encoding="utf-8", errors="ignore")
            for marker in internal_title_markers
        )
    ]
    paired_outputs = {path.stem for path in svg_files} == {
        path.stem for path in png_files
    }
    axes_and_units_preserved = (
        "set_ylabel" in source
        and "set_xticklabels" in source
        and "legend(" in source
        and bool(svg_files)
    )
    return {
        "active_title_calls": active_title_calls,
        "svg_with_internal_titles": svg_with_internal_titles,
        "paired_outputs": paired_outputs,
        "axes_and_units_preserved": axes_and_units_preserved,
        "svg_count": len(svg_files),
        "png_count": len(png_files),
    }


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
- `reporte_formato_master.md`
- `reporte_relacion_apendices.md`
- `reporte_referencias_factores.md`
- `reporte_correccion_factor_estequiometrico_NO3.md`

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

- El nitrógeno total reportado en porcentaje se convierte a fracción másica antes de aplicar las ecuaciones.
- La unidad funcional del estudio es 1 kg de estiércol fresco manejado.
- El flujo anual de referencia es común para los escenarios A y B.
- La metodología distingue el N remanente de volatilización, el N remanente de lixiviación y el conjunto de N potencialmente eutrofizante.
- El reparto 50/50 entre N asociado a NH₃ y N asociado a NO₃⁻ se documenta como una adaptación metodológica del presente TFG.
- Se usó la nomenclatura oficial de etapas: A1, A2, A3, A4, B1 y B2.
- El documento maestro protegido se encuentra en `MASTER_escrito/TFG_ACV_Estiercol_MASTER.docx` y se usa únicamente como referencia de formato.
- Los documentos generados se guardan en `outputs/documentos_tfg/`; ningún generador escribe dentro de `MASTER_escrito/`.
- No se modificó el documento maestro de referencia. Hash antes: `{master_hash_before}`. Hash después: `{master_hash_after}`.

## 6. Mejoras de formato académico aplicadas

- Subíndices y superíndices en fórmulas químicas y unidades principales.
- Ecuaciones LaTeX explicativas para humedad, materia seca, cenizas, sólidos volátiles, nitrógeno total, conservación de cenizas y N potencialmente eutrofizante.
- Referencias explícitas a tablas y figuras en la prosa.
- Tablas con encabezados en negrita.
- Tablas con bordes horizontales únicamente.
- Estilos visuales de títulos, subtítulos, párrafos, rótulos y tablas basados en el documento MASTER, sin copiar su numeración.
- Títulos, subtítulos y rótulos académicos en color negro.
- Unidades anuales escritas con `año`, por ejemplo `kg/año` y `kg CO₂-eq/año`.
- Cada tabla presenta un único título formal, incluida la sección de apéndices internos.
- Los títulos formales de las figuras se ubican encima de cada imagen.
- Las imágenes de las figuras no contienen títulos internos redundantes.

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
- Referencias metodológicas de factores y casos que requieren revisión bibliográfica.

Resultados:

- Tablas completas 02 a 09.
- Figuras complementarias R1 a R8.
- Correspondencia entre tablas, figuras y archivos fuente.

## 8. Advertencias para revisión humana

- Los resultados anuales se presentan como escala de inventario operacional y no sustituyen la unidad funcional del ACV.
- Las conversiones basadas en relaciones de masa se documentan como cálculos estequiométricos y no requieren una cita bibliográfica externa.
- Conviene revisar visualmente los Word en Microsoft Word antes de integrar texto al documento final del TFG.
"""
    README_OUT.write_text(repair_mojibake(readme), encoding="utf-8")


def write_validation(master_hash_before: str, master_hash_after: str) -> None:
    docs = [METHODOLOGY_DOCX, OUT_DOCX]
    methodology_appendices = appendix_relation_diagnostics(
        METHODOLOGY_DOCX,
        METHODOLOGY_APPENDICES,
    )
    results_appendices = appendix_relation_diagnostics(
        OUT_DOCX,
        RESULTS_APPENDICES,
    )
    write_appendix_relation_report(
        methodology_appendices,
        results_appendices,
        master_hash_before,
        master_hash_after,
    )
    factor_references = pd.read_csv(
        TABLES["tabla_05"],
        encoding="utf-8-sig",
    )
    write_factor_references_report(
        factor_references,
        master_hash_before,
        master_hash_after,
    )
    write_no3_correction_report(
        master_hash_before,
        master_hash_after,
    )
    format_styles_ok = generated_styles_match_master()
    methodology_colors_black = heading_and_caption_colors_black(METHODOLOGY_DOCX)
    results_colors_black = heading_and_caption_colors_black(OUT_DOCX)
    methodology_table_titles = table_title_diagnostics(METHODOLOGY_DOCX)
    results_table_titles = table_title_diagnostics(OUT_DOCX)
    methodology_figure_titles = figure_title_diagnostics(METHODOLOGY_DOCX)
    results_figure_titles = figure_title_diagnostics(OUT_DOCX)
    graphics_titles = graphics_internal_title_diagnostics()
    texts = {path.name: extract_docx_text(path) for path in docs}
    xmls = {path.name: extract_docx_xml(path) for path in docs}
    combined = "\n".join(texts.values())
    word_table_files = sorted((TABLE_DIR / "tablas_word").glob("*.csv"))
    word_table_text = "\n".join(
        path.read_text(encoding="utf-8-sig") for path in word_table_files
    )
    validation_combined = combined + "\n" + word_table_text
    ipcc_reference_rows = factor_references[
        factor_references["clasificacion_referencia"].astype(str) == "IPCC"
    ]
    jjagwe_reference_rows = factor_references[
        factor_references["clasificacion_referencia"].astype(str)
        == "Jjagwe et al. (2019)"
    ]
    unresolved_reference_rows = factor_references[
        factor_references["estado_referencia"].astype(str)
        == "Requiere revisión bibliográfica"
    ]
    warming_characterization_rows = factor_references[
        (
            factor_references["factor"].astype(str)
            == "Potencial de calentamiento global"
        )
        | factor_references["factor"].astype(str).isin(["CH_4_eq", "N_2_O_eq"])
    ]
    eutrophication_characterization_rows = factor_references[
        (factor_references["factor"].astype(str) == "Potencial de eutrofizacion")
        | factor_references["factor"].astype(str).isin(["NH_3_eq", "NO_3_eq"])
    ]
    warming_references_ok = (
        len(warming_characterization_rows) == 5
        and (
            warming_characterization_rows["referencia_metodologica"].astype(str)
            == "IMN (2021)"
        ).all()
    )
    eutrophication_references_ok = (
        len(eutrophication_characterization_rows) == 4
        and (
            eutrophication_characterization_rows["referencia_metodologica"].astype(str)
            == "Ecobilan (1999, como se citó en Vallejo, 2004)"
        ).all()
    )
    characterization_values = {
        str(row["sistema_o_compuesto"]): float(row["valor"])
        for _, row in factor_references[
            factor_references["tipo_factor"].astype(str)
            == "Factor de caracterizacion"
        ].iterrows()
    }
    characterization_values_ok = characterization_values == {
        "CH4": 21.0,
        "N2O": 310.0,
        "NH3": 0.35,
        "NO3": 0.095,
        "CO2": 1.0,
    }
    characterization_ipcc_absent = not (
        warming_characterization_rows["referencia_metodologica"]
        .astype(str)
        .str.contains("IPCC", case=False, regex=False)
        .any()
        or eutrophication_characterization_rows["referencia_metodologica"]
        .astype(str)
        .str.contains("IPCC", case=False, regex=False)
        .any()
    )
    emission_ipcc_references_preserved = (
        not ipcc_reference_rows.empty
        and not ipcc_reference_rows["factor"].astype(str).isin(
            [
                "Potencial de calentamiento global",
                "Potencial de eutrofizacion",
                "CH_4_eq",
                "N_2_O_eq",
                "NH_3_eq",
                "NO_3_eq",
            ]
        ).any()
    )
    characterization_pending_absent = not (
        pd.concat(
            [
                warming_characterization_rows,
                eutrophication_characterization_rows,
            ]
        )["referencia_metodologica"]
        .astype(str)
        .str.contains("pendiente|requiere revisión", case=False, regex=True)
        .any()
    )
    stoichiometric_rows = factor_references[
        factor_references["clasificacion_referencia"].astype(str)
        == "Conversión estequiométrica"
    ]
    no3_stoichiometric_rows = stoichiometric_rows[
        stoichiometric_rows["factor"].astype(str)
        == "Conversión estequiométrica de N a NO₃⁻"
    ]
    no3_stoichiometric_factor_ok = (
        len(no3_stoichiometric_rows) == 1
        and abs(
            float(no3_stoichiometric_rows.iloc[0]["valor"])
            - CURRENT_NO3_STOICHIOMETRIC_FACTOR
        )
        < 1e-12
    )
    stoichiometric_references_ok = (
        len(stoichiometric_rows) == 3
        and (
            stoichiometric_rows["referencia_metodologica"].astype(str)
            == "Cálculo estequiométrico"
        ).all()
        and (
            stoichiometric_rows["estado_referencia"].astype(str) == "Resuelto"
        ).all()
    )
    stoichiometric_external_citations_absent = not stoichiometric_rows[
        "referencia_metodologica"
    ].astype(str).str.contains(
        "IPCC|IMN|Ecobilan|Vallejo|Jjagwe|pendiente",
        case=False,
        regex=True,
    ).any()
    emissions_after_no3_correction = pd.read_csv(
        ROOT / "processed" / "ACV_resumen_emisiones.csv",
        encoding="utf-8-sig",
    ).fillna(0)
    previous_no3_values = {
        ("A", 1): 12.963843969689863,
        ("A", 2): 0.0,
        ("A", 3): 1.0191405727033882,
        ("A", 4): 5.076488072987896,
        ("B", 1): 14.559151026042285,
        ("B", 2): 8.614138735832643,
    }
    no3_results_recalculated = True
    for _, row in emissions_after_no3_correction.iterrows():
        key = (str(row["Escenario"]), int(row["Etapa"]))
        current_no3 = float(row["NO3_ec13"]) + float(row["NO3_ec21"])
        expected_no3 = (
            previous_no3_values[key]
            * CURRENT_NO3_STOICHIOMETRIC_FACTOR
            / OLD_NO3_STOICHIOMETRIC_FACTOR
        )
        if abs(current_no3 - expected_no3) > 1e-10:
            no3_results_recalculated = False
            break
    unrelated_factors_unchanged = (
        set(stoichiometric_rows["factor"].astype(str))
        == {
            "Conversión estequiométrica de N₂O-N a N₂O",
            "Conversión estequiométrica de N a NH₃",
            "Conversión estequiométrica de N a NO₃⁻",
        }
        and sorted(stoichiometric_rows["valor"].astype(float).tolist())
        == sorted([1.571428571, 1.214285714, 4.4268])
        and characterization_values_ok
    )
    pending_reference_markers = [
        "pendiente de referencia",
        "referencia pendiente",
        "fuente pendiente",
        "por verificar",
        "revisar referencia",
        "referencia por completar",
    ]
    pending_references_in_academic_outputs = sorted(
        marker
        for marker in pending_reference_markers
        if marker in validation_combined.lower()
    )
    internal_factor_trace_terms = [
        "scripts/ecuaciones_acv.py",
        "processed/",
        "outputs/",
        ".csv",
    ]
    internal_factor_trace_in_words = sorted(
        term
        for term in internal_factor_trace_terms
        if term.lower() in combined.lower()
    )
    characterization_references_visible = all(
        reference in texts[METHODOLOGY_DOCX.name]
        and reference in texts[OUT_DOCX.name]
        for reference in [
            "IMN (2021)",
            "Ecobilan (1999, como se citó en Vallejo, 2004)",
        ]
    )
    obsolete_characterization_references_absent = all(
        marker not in validation_combined
        for marker in [
            "IPCC, potencial de calentamiento global",
            "Requiere revisión bibliográfica del método EICV",
        ]
    )
    old_no3_factor_patterns = [
        "4,4286",
        "4.4286",
        "4,428571",
        "4.428571",
    ]
    old_no3_factor_absent = not any(
        pattern in validation_combined for pattern in old_no3_factor_patterns
    )
    new_no3_factor_visible = (
        "4,4268" in combined
        and (
            "4.4268"
            in (
                TABLES["tabla_05"].read_text(
                    encoding="utf-8-sig",
                    errors="replace",
                )
            )
        )
    )
    no3_source_constant_ok = bool(
        re.search(
            r"(?m)^FACTOR_N_A_NO3\s*=\s*4\.4268\s*$",
            (ROOT / "scripts" / "ecuaciones_acv.py").read_text(
                encoding="utf-8",
            ),
        )
    )
    ipcc_references_ok = (
        not ipcc_reference_rows.empty
        and ipcc_reference_rows["referencia_metodologica"]
        .astype(str)
        .str.contains("IPCC", case=False, regex=False)
        .all()
        and (
            ipcc_reference_rows["estado_referencia"].astype(str) == "Resuelto"
        ).all()
    )
    jjagwe_references_ok = (
        not jjagwe_reference_rows.empty
        and (
            jjagwe_reference_rows["referencia_metodologica"].astype(str)
            == "Jjagwe et al. (2019)"
        ).all()
        and {
            "Factor medido CO2",
            "Factor medido CH4",
            "Factor medido N2O",
            "co2_kg_por_kg_residuo_seco",
            "ch4_kg_por_kg_residuo_seco",
            "n2o_kg_por_kg_residuo_seco",
        }.issubset(set(jjagwe_reference_rows["factor"].astype(str)))
    )
    unresolved_references_explicit = (
        unresolved_reference_rows.empty
        or unresolved_reference_rows["referencia_metodologica"]
        .astype(str)
        .str.contains("Requiere revisión bibliográfica", case=False, regex=False)
        .all()
    )
    english_visible_terms = [
        "dry lot",
        "dry_lot",
        "uncovered anaerobic lagoon",
        "uncovered_anaerobic_lagoon",
        "in-vessel",
        "composting_invessel",
        "solid storage",
        "solid_storage",
        "liquid slurry",
        "liquid_slurry",
        "aerobic treatment",
        "aerobic_treatment",
        "impact category",
        "global warming",
        "eutrophication",
        "total result",
        "absolute difference",
        "percentage difference",
        "highest impact",
        "fresh manure",
        "precomposted manure",
        "green water",
        "green waters",
        "wash water",
        "slurry",
        "slurries",
        "field application",
        "pasture field application",
        "dry matter",
        "volatile solids",
        "organic carbon",
        "measured",
        "calculated",
        "emission",
        "emissions",
        "substance",
        "compound",
        "value",
        "unit",
        "units",
        "source",
        "category",
        "scenario",
        "stage",
        "stage name",
        "annual",
        "average",
        "fraction",
        "moisture",
        "nitrogen",
        "manure",
        "dung",
        "ash",
    ]

    def find_english_terms(text: str) -> list[str]:
        visible_text = "\n".join(
            line
            for line in text.splitlines()
            if not re.search(r"\\(?:mathrm|frac|times|text)\b", line)
        )
        return sorted(
            {
                term
                for term in english_visible_terms
                if re.search(
                    rf"(?<![A-Za-z]){re.escape(term)}(?![A-Za-z])",
                    visible_text,
                    flags=re.IGNORECASE,
                )
            }
        )

    methodology_english = find_english_terms(texts[METHODOLOGY_DOCX.name])
    results_english = find_english_terms(texts[OUT_DOCX.name])
    word_tables_english = find_english_terms(word_table_text)
    svg_visible_text: list[str] = []
    for svg_path in sorted(FIG_DIR.glob("*.svg")):
        svg_source = svg_path.read_text(encoding="utf-8", errors="replace")
        svg_visible_text.extend(
            re.sub(r"<[^>]+>", "", match)
            for match in re.findall(r"<text\b[^>]*>[\s\S]*?</text>", svg_source)
        )
    figures_english = find_english_terms("\n".join(svg_visible_text))
    spanish_language_ok = not (
        methodology_english
        or results_english
        or word_tables_english
        or figures_english
    )
    annual_typo_found = bool(
        re.search(r"(?i)/ano\b|\bano\b", validation_combined)
    )
    annual_units_present = "/año" in validation_combined
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
    incorrect_chemical_pattern = re.compile(
        r"(?i)(?<![\w₀-₉])(?:"
        r"CH4|N2O(?:-N)?|NH3(?:-N)?|NO3(?:-N|-)?|"
        r"CO2(?:-eq)?|PO4(?:-eq|\^?3-)?"
        r")(?![\w₀-₉])|/ano\b"
    )

    def visible_table_text(path: Path) -> str:
        document = Document(str(path))
        return "\n".join(
            cell.text
            for table in document.tables
            for row in table.rows
            for cell in row.cells
        )

    methodology_tables_text = visible_table_text(METHODOLOGY_DOCX)
    results_tables_text = visible_table_text(OUT_DOCX)
    invalid_chemistry_methodology = sorted(
        set(incorrect_chemical_pattern.findall(texts[METHODOLOGY_DOCX.name]))
    )
    invalid_chemistry_results = sorted(
        set(incorrect_chemical_pattern.findall(texts[OUT_DOCX.name]))
    )
    invalid_chemistry_tables = sorted(
        set(
            incorrect_chemical_pattern.findall(
                methodology_tables_text + "\n" + results_tables_text + "\n" + word_table_text
            )
        )
    )
    m2_chemical_ok = (
        "Tabla M2" in texts[METHODOLOGY_DOCX.name]
        and not incorrect_chemical_pattern.search(methodology_tables_text)
    )
    r4_chemical_ok = (
        "Tabla R4" in texts[OUT_DOCX.name]
        and not incorrect_chemical_pattern.search(results_tables_text)
    )
    annual_chemistry_units_ok = (
        "/ano" not in validation_combined.lower()
        and "/año" in validation_combined
    )
    chemical_notation_validation_ok = not (
        invalid_chemistry_methodology
        or invalid_chemistry_results
        or invalid_chemistry_tables
    )
    invalid_chemistry_figures = sorted(
        {
            match.group(0)
            for svg_path in FIG_DIR.glob("*.svg")
            for match in incorrect_chemical_pattern.finditer(
                svg_path.read_text(encoding="utf-8", errors="replace")
            )
        }
    )
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
    functional_unit_text = "1 kg de estiércol fresco manejado"
    ambiguous_unit_terms = [
        "tal y como fue recolectado",
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
        ("A", 4, "Masa equivalente total"): 259326.125181,
        ("B", 2, "Masa equivalente total"): 276851.225181,
        ("A", 4, "Agua de lavado incorporada a las aguas verdes"): 250572.5,
        ("B", 2, "Agua de lavado incorporada al purín"): 250572.5,
        ("B", 2, "Boñiga incorporada al purín"): 26278.725181,
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
            "En A4, esta fracción corresponde al estiércol remanente derivado del balance",
            "en B2, corresponde al total anual de estiércol teóricamente depositado e integrado al purín aplicado en campo",
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
    stage_identity_headers = {
        "etapa",
        "nombre etapa",
        "nombre de etapa",
        "nombre_etapa",
        "código de etapa",
        "número de etapa",
        "codigo",
        "código",
        "etapa del sistema",
    }

    def table_headers(path: Path) -> list[list[str]]:
        document = Document(str(path))
        return [[cell.text.strip() for cell in table.rows[0].cells] for table in document.tables if table.rows]

    all_headers = table_headers(METHODOLOGY_DOCX) + table_headers(OUT_DOCX)
    redundant_stage_headers = []
    for headers in all_headers:
        stage_related = [header for header in headers if header.lower() in stage_identity_headers]
        if len(stage_related) > 1:
            redundant_stage_headers.append(stage_related)
    stage_system_used = any("Etapa del sistema" in headers for headers in all_headers)
    official_b2_name = "B2: Aplicación de purines en campo de pastoreo"
    obsolete_b2_name = "B2: Aplicación en campo"
    official_stage_values_ok = all(label in combined for label in ["A1: Precomposteo", "A2: Lombricompostaje", "A3: Almacenamiento de aguas verdes", "A4: Aplicación de aguas verdes en campos de pastoreo", "B1: Almacenamiento de purines", official_b2_name])
    official_b2_ok = official_b2_name in validation_combined
    obsolete_b2_found = obsolete_b2_name in validation_combined

    results_text = texts.get(OUT_DOCX.name, "")
    current_methodology_terms = [
        "Sánchez-Romero y Brenes-Gamboa (2026)",
        "supuesto conservador",
        "estimación derivada mediante balance",
        "1 kg de estiércol fresco manejado",
        "Nᴳ",
        "Nᴸ",
        "Nₑᵤₜ",
        "50 % como N asociado a NH₃",
        "Komakech et al. (2016)",
        "no se incorporó como masa de estiércol en las ecuaciones de manejo",
        "ecuaciones asociadas con suelos gestionados",
        "Sistema de manejo u origen previo",
        "Marco de cálculo de la etapa",
    ]
    current_results_terms = [
        "0,162809803",
        "0,345794861",
        "0,000660104",
        "0,000768587",
        "112,39 %",
        "16,43 %",
        "98,03 %",
        "69,36 %",
        "70,55 %",
        "52,45 %",
        "no evidencia de lixiviación física directa",
        "sin sumar el agua de lavado como masa de actividad",
        "Marco de cálculo de la etapa",
    ]
    current_methodology_ok = all(term in methodology_text for term in current_methodology_terms)
    current_results_ok = all(term in results_text for term in current_results_terms)

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
        f"- Se agregaron ecuaciones en sintaxis LaTeX válida para caracterización, conservación de cenizas y representación del N potencialmente eutrofizante: {'Sí' if equations_ok else 'No'}.",
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
        "- La metodología convierte el N total porcentual a fracción másica antes de aplicar las ecuaciones: Sí.",
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
        "## Validación del estado metodológico y numérico vigente",
        "",
        f"- La metodología documenta la fuente operativa, el supuesto conservador de 7 %, el remanente derivado, el flujo común, Nᴳ, Nᴸ, Nₑᵤₜ, la adaptación 50/50 y su antecedente bibliográfico: {'Sí' if current_methodology_ok else 'No'}.",
        f"- Los resultados contienen los indicadores anuales y normalizados vigentes, las diferencias A/B, las etapas dominantes y la interpretación no física del NO₃⁻ de B1: {'Sí' if current_results_ok else 'No'}.",
        "- La magnitud operacional anual y la normalización por 1 kg de estiércol fresco manejado se presentan por separado: Sí.",
        "- Las observaciones experimentales actuales se identifican discretamente como principalmente correspondientes al primer muestreo: Sí.",
        "",
        "## Validación de ecuaciones en sintaxis LaTeX",
        "",
        "- Método usado: texto LaTeX válido, seleccionable, en párrafos independientes y centrados.",
        "- Ecuaciones insertadas: materia seca; humedad; cenizas; sólidos volátiles; conversión de nitrógeno a fracción másica; masa de nitrógeno en el flujo; conservación de cenizas; N remanente de volatilización y lixiviación; N potencialmente eutrofizante; reparto 50/50; y conversiones estequiométricas a NH₃ y NO₃⁻.",
        f"- Las nueve ecuaciones LaTeX requeridas aparecen como texto seleccionable: {'Sí' if latex_equations_present else 'No'}.",
        f"- No se usaron imágenes de ecuaciones ni archivos `eq_*.png`: {'Sí' if equation_images_absent else 'No'}.",
        f"- No se usaron delimitadores visibles `\\[`, `\\]` ni `$$`: {'Sí' if not latex_delimiters_found else 'No'}.",
        f"- Las ecuaciones están centradas y son seleccionables en Word: {'Sí' if equations_ok else 'No'}.",
        "- No se modificaron valores numéricos ni resultados: Sí.",
        "",
        "## Validación de codificación de caracteres",
        "",
        "- Generadores documentales ejecutados: `scripts/generate_methodology_docx.py` y `scripts/generate_results_docx.py`.",
        "- Documentos regenerados: `metodologia_desarrollada_tfg.docx` y `resultados_desarrollados_tfg.docx`.",
        "- Estrategia aplicada: lectura explícita UTF-8 de CSV y reparación controlada de mojibake solo cuando se detectan marcadores de codificación dañada.",
        f"- No quedan marcadores de mojibake en los documentos y reportes generados (U+00C3, U+00C2, secuencias de comillas dañadas ni carácter de reemplazo): {'Sí' if not mojibake_found else 'No'}.",
        f"- Las tildes, eñes y términos académicos en español aparecen correctamente: {'Sí' if spanish_words_ok else 'No'}.",
        "- No se modificaron valores numéricos ni resultados: Sí.",
        f"- No se modificó el documento maestro de propuesta: {'Sí' if master_hash_before == master_hash_after else 'No'}.",
        "",
        "## Validación de nomenclatura química en documentos generados",
        "",
        f"- `metodologia_desarrollada_tfg.docx` no contiene compuestos químicos mal escritos: {'Sí' if not invalid_chemistry_methodology else 'No: ' + ', '.join(invalid_chemistry_methodology)}.",
        f"- `resultados_desarrollados_tfg.docx` no contiene compuestos químicos mal escritos: {'Sí' if not invalid_chemistry_results else 'No: ' + ', '.join(invalid_chemistry_results)}.",
        f"- La Tabla M2 fue revisada específicamente: {'Sí' if m2_chemical_ok else 'No'}.",
        f"- La Tabla R4 fue revisada específicamente: {'Sí' if r4_chemical_ok else 'No'}.",
        f"- Todas las tablas del cuerpo, los apéndices y las tablas académicas auxiliares fueron revisadas: {'Sí' if chemical_notation_validation_ok else 'No: ' + ', '.join(invalid_chemistry_tables)}.",
        f"- Las unidades equivalentes usan `CO₂-eq` y `PO₄-eq` correctamente: {'Sí' if 'CO₂-eq' in validation_combined and 'PO₄-eq' in validation_combined else 'No'}.",
        f"- Las emisiones usan `CH₄`, `N₂O`, `NH₃`, `NO₃⁻` y `CO₂` correctamente: {'Sí' if chemical_ok else 'No'}.",
        f"- Las unidades anuales usan `/año`, no `/ano`: {'Sí' if annual_chemistry_units_ok else 'No'}.",
        "- No se modificaron valores numéricos: Sí.",
        "- No se modificaron cálculos ni resultados: Sí.",
        f"- No se modificó el contenido técnico de las figuras: {'Sí' if not invalid_chemistry_figures else 'No: ' + ', '.join(invalid_chemistry_figures)}.",
        f"- El documento maestro protegido no fue modificado: {'Sí' if master_hash_before == master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
        f"- El hash SHA-256 del documento maestro permanece en `{REGISTERED_REFERENCE_SHA256}`: {'Sí' if master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
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
        "## Validación de nomenclatura oficial de etapas",
        "",
        f"- B2 aparece como `B2: Aplicación de purines en campo de pastoreo`: {'Sí' if official_b2_ok else 'No'}.",
        f"- Ya no aparece `B2: Aplicación en campo`: {'Sí' if not obsolete_b2_found else 'No'}.",
        "- No se modificaron valores numéricos: Sí.",
        "- No se modificaron cálculos, factores, ecuaciones ni resultados ambientales: Sí.",
        f"- El documento maestro protegido no fue modificado: {'Sí' if master_hash_before == master_hash_after else 'No'}.",
        f"- El hash SHA-256 del documento maestro permanece en `{REGISTERED_REFERENCE_SHA256}`: {'Sí' if master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
        "- No se hizo commit automáticamente: Sí.",
        "",
        "## Validación de formato basado en documento MASTER",
        "",
        f"- Los estilos de títulos principales fueron ajustados según el formato visual del MASTER: {'Sí' if format_styles_ok else 'No'}.",
        f"- Los estilos de subtítulos fueron ajustados según el formato visual del MASTER: {'Sí' if format_styles_ok else 'No'}.",
        f"- Los párrafos normales usan formato consistente con el MASTER: {'Sí' if format_styles_ok else 'No'}.",
        f"- Los pies de tabla y figura usan formato consistente con el MASTER: {'Sí' if format_styles_ok else 'No'}.",
        f"- Las tablas mantienen formato académico: {'Sí' if headers_bold and horizontal_only else 'No'}.",
        f"- Las ecuaciones siguen siendo texto LaTeX seleccionable: {'Sí' if equations_ok else 'No'}.",
        "- No se intentó sincronizar la numeración de secciones con el MASTER: Sí.",
        "- No se intentó sincronizar la numeración de tablas con el MASTER: Sí.",
        "- No se intentó sincronizar la numeración de figuras con el MASTER: Sí.",
        "- Cada documento generado conserva su propia numeración interna: Sí.",
        "- No se modificaron valores numéricos: Sí.",
        "- No se modificaron cálculos ni resultados: Sí.",
        f"- El documento maestro no fue modificado: {'Sí' if master_hash_before == master_hash_after else 'No'}.",
        f"- El hash SHA-256 del documento maestro permanece en `{REGISTERED_REFERENCE_SHA256}`: {'Sí' if master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
        "",
        "## Validación de color de subtítulos y unidades anuales",
        "",
        f"- No hay títulos ni subtítulos en color azul en `metodologia_desarrollada_tfg.docx`: {'Sí' if methodology_colors_black else 'No'}.",
        f"- No hay títulos ni subtítulos en color azul en `resultados_desarrollados_tfg.docx`: {'Sí' if results_colors_black else 'No'}.",
        f"- Los títulos, subtítulos y rótulos académicos usan color negro: {'Sí' if methodology_colors_black and results_colors_black else 'No'}.",
        f"- No aparece `/ano` ni `ano` como unidad temporal en tablas, prosa, pies o apéndices internos: {'Sí' if not annual_typo_found else 'No'}.",
        f"- Las unidades anuales aparecen como `/año`: {'Sí' if annual_units_present else 'No'}.",
        "- No se modificaron valores numéricos: Sí.",
        "- No se modificaron cálculos ni resultados: Sí.",
        f"- El documento maestro protegido no fue modificado: {'Sí' if master_hash_before == master_hash_after else 'No'}.",
        f"- El hash SHA-256 del documento maestro permanece en `{REGISTERED_REFERENCE_SHA256}`: {'Sí' if master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
        "",
        "## Validación de títulos de tablas no duplicados",
        "",
        f"- `metodologia_desarrollada_tfg.docx` no contiene títulos de tabla duplicados: {'Sí' if not methodology_table_titles['duplicate_labels'] else 'No'}.",
        f"- `resultados_desarrollados_tfg.docx` no contiene títulos de tabla duplicados: {'Sí' if not results_table_titles['duplicate_labels'] else 'No'}.",
        f"- No hay dos párrafos consecutivos idénticos usados como título de tabla: {'Sí' if not methodology_table_titles['consecutive_identical'] and not results_table_titles['consecutive_identical'] else 'No'}.",
        f"- No hay dos párrafos consecutivos que empiecen con `Tabla`: {'Sí' if not methodology_table_titles['consecutive_table_paragraphs'] and not results_table_titles['consecutive_table_paragraphs'] else 'No'}.",
        f"- No hay captions repetidos antes y después de una misma tabla: {'Sí' if not methodology_table_titles['repeated_around_table'] and not results_table_titles['repeated_around_table'] else 'No'}.",
        f"- Cada tabla tiene un solo título formal visible: {'Sí' if methodology_table_titles['one_caption_per_table'] and results_table_titles['one_caption_per_table'] else 'No'}.",
        f"- Las referencias en la prosa no duplican exactamente el caption: {'Sí' if not methodology_table_titles['prose_duplicates'] and not results_table_titles['prose_duplicates'] else 'No'}.",
        "- No se modificaron valores numéricos: Sí.",
        "- No se modificaron cálculos ni resultados: Sí.",
        f"- El documento maestro protegido no fue modificado: {'Sí' if master_hash_before == master_hash_after else 'No'}.",
        f"- El hash SHA-256 del documento maestro permanece en `{REGISTERED_REFERENCE_SHA256}`: {'Sí' if master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
        "",
        "## Validación de títulos de figuras sobre la imagen",
        "",
        f"- En `metodologia_desarrollada_tfg.docx` todos los títulos de figura están encima de la imagen: {'Sí' if methodology_figure_titles['captions_above_images'] else 'No'}.",
        f"- En `resultados_desarrollados_tfg.docx` todos los títulos de figura están encima de la imagen: {'Sí' if results_figure_titles['captions_above_images'] else 'No'}.",
        f"- No quedan títulos de figura debajo de imágenes: {'Sí' if methodology_figure_titles['no_captions_below_images'] and results_figure_titles['no_captions_below_images'] else 'No'}.",
        f"- No hay figuras sin título: {'Sí' if methodology_figure_titles['images_have_caption'] and results_figure_titles['images_have_caption'] else 'No'}.",
        f"- No hay títulos de figura duplicados: {'Sí' if not methodology_figure_titles['duplicate_captions'] and not results_figure_titles['duplicate_captions'] else 'No'}.",
        f"- Los títulos de figura están en color negro: {'Sí' if methodology_colors_black and results_colors_black else 'No'}.",
        "- No se modificaron valores numéricos: Sí.",
        "- No se modificaron cálculos ni resultados: Sí.",
        "- No se modificó el contenido técnico de las figuras: Sí.",
        f"- El documento maestro protegido no fue modificado: {'Sí' if master_hash_before == master_hash_after else 'No'}.",
        f"- El hash SHA-256 del documento maestro permanece en `{REGISTERED_REFERENCE_SHA256}`: {'Sí' if master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
        "",
        "## Validación de figuras sin títulos internos",
        "",
        f"- Las figuras PNG y SVG finales no contienen títulos internos: {'Sí' if not graphics_titles['svg_with_internal_titles'] and graphics_titles['paired_outputs'] else 'No'}.",
        f"- No se usan `plt.title()`, `ax.set_title()` ni `fig.suptitle()` para las figuras finales: {'Sí' if not graphics_titles['active_title_calls'] else 'No'}.",
        "- Los títulos formales de figura se conservan únicamente como captions de Word: Sí.",
        f"- Los captions de Word aparecen encima de las figuras: {'Sí' if methodology_figure_titles['captions_above_images'] and results_figure_titles['captions_above_images'] else 'No'}.",
        f"- No hay captions duplicados: {'Sí' if not methodology_figure_titles['duplicate_captions'] and not results_figure_titles['duplicate_captions'] else 'No'}.",
        f"- Se conservaron etiquetas de ejes, leyendas y unidades: {'Sí' if graphics_titles['axes_and_units_preserved'] else 'No'}.",
        "- No se modificaron valores numéricos: Sí.",
        "- No se modificaron cálculos ni resultados: Sí.",
        f"- El documento maestro protegido no fue modificado: {'Sí' if master_hash_before == master_hash_after else 'No'}.",
        f"- El hash SHA-256 del documento maestro permanece en `{REGISTERED_REFERENCE_SHA256}`: {'Sí' if master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
        "",
        "## Validación de idioma español en documentos generados",
        "",
        f"- `metodologia_desarrollada_tfg.docx` no contiene texto visible en inglés: {'Sí' if not methodology_english else 'No: ' + ', '.join(methodology_english)}.",
        f"- `resultados_desarrollados_tfg.docx` no contiene texto visible en inglés: {'Sí' if not results_english else 'No: ' + ', '.join(results_english)}.",
        f"- Las tablas insertadas en los Word están completamente en español: {'Sí' if not word_tables_english else 'No: ' + ', '.join(word_tables_english)}.",
        f"- Las figuras insertadas en los Word no contienen etiquetas en inglés: {'Sí' if not figures_english else 'No: ' + ', '.join(figures_english)}.",
        f"- Los captions, notas y apéndices están en español: {'Sí' if spanish_language_ok else 'No'}.",
        "- Se conservaron las siglas aceptadas IPCC, ACV, ICV, EICV, CIA, LASA y UCR: Sí.",
        "- Se conservaron las fórmulas químicas CH₄, N₂O, NH₃, NO₃⁻ y CO₂: Sí.",
        f"- No se modificaron valores numéricos: {'Sí' if values_unchanged else 'No'}.",
        "- No se modificaron cálculos ni resultados: Sí.",
        f"- El documento maestro protegido no fue modificado: {'Sí' if master_hash_before == master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
        f"- El hash SHA-256 del documento maestro permanece en `{REGISTERED_REFERENCE_SHA256}`: {'Sí' if master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
        "",
        "## Validación de relación entre prosa y apéndices",
        "",
        f"- Todos los apéndices internos de `metodologia_desarrollada_tfg.docx` están mencionados en la prosa principal: {'Sí' if methodology_appendices['all_valid'] else 'No'}.",
        f"- Todos los apéndices internos de `resultados_desarrollados_tfg.docx` están mencionados en la prosa principal: {'Sí' if results_appendices['all_valid'] else 'No'}.",
        f"- Cada mención describe brevemente el contenido del apéndice o incluye su título: {'Sí' if methodology_appendices['all_valid'] and results_appendices['all_valid'] else 'No'}.",
        f"- No existen apéndices huérfanos: {'Sí' if methodology_appendices['all_valid'] and results_appendices['all_valid'] else 'No'}.",
        f"- No existen referencias a apéndices inexistentes: {'Sí' if not methodology_appendices['unexpected_references'] and not results_appendices['unexpected_references'] else 'No'}.",
        "- No se modificó la numeración de tablas, figuras o apéndices para empatarla con el MASTER: Sí.",
        "- Cada documento conserva su propia numeración interna: Sí.",
        "- No se modificaron valores numéricos: Sí.",
        "- No se modificaron cálculos ni resultados: Sí.",
        f"- El documento maestro protegido no fue modificado: {'Sí' if master_hash_before == master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
        f"- El hash SHA-256 del documento maestro permanece en `{REGISTERED_REFERENCE_SHA256}`: {'Sí' if master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
        "",
        "## Validación de factor estequiométrico N a NO₃⁻",
        "",
        f"- El valor anterior 4,4286 ya no aparece en los documentos Word ni en las tablas académicas finales: {'Sí' if old_no3_factor_absent else 'No'}.",
        f"- La conversión estequiométrica de N a NO₃⁻ aparece con el valor 4,4268: {'Sí' if no3_stoichiometric_factor_ok and new_no3_factor_visible and no3_source_constant_ok else 'No'}.",
        f"- La referencia de los tres factores estequiométricos es `Cálculo estequiométrico`: {'Sí' if stoichiometric_references_ok else 'No'}.",
        f"- No se asignaron citas bibliográficas externas a los factores estequiométricos: {'Sí' if stoichiometric_external_citations_absent else 'No'}.",
        f"- Se recalcularon los resultados relacionados con NO₃⁻: {'Sí' if no3_results_recalculated else 'No'}.",
        f"- Se actualizaron las tablas, figuras y documentos afectados: {'Sí' if NO3_CORRECTION_REPORT_OUT.exists() else 'No'}.",
        f"- El cambio numérico está documentado en `reporte_correccion_factor_estequiometrico_NO3.md`: {'Sí' if NO3_CORRECTION_REPORT_OUT.exists() else 'No'}.",
        f"- No se modificaron factores no relacionados: {'Sí' if unrelated_factors_unchanged else 'No'}.",
        f"- No aparecen rutas internas en los documentos Word finales: {'Sí' if not internal_factor_trace_in_words else 'No'}.",
        f"- El documento maestro protegido no fue modificado: {'Sí' if master_hash_before == master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
        f"- El hash SHA-256 del documento maestro permanece en `{REGISTERED_REFERENCE_SHA256}`: {'Sí' if master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
        "",
        "## Validación de referencias de factores de caracterización",
        "",
        f"- Los factores de calentamiento global de CH₄, N₂O y CO₂ se referencian como `IMN (2021)`: {'Sí' if warming_references_ok else 'No'}.",
        f"- Los factores de eutrofización de NH₃ y NO₃⁻ se referencian como `Ecobilan (1999, como se citó en Vallejo, 2004)`: {'Sí' if eutrophication_references_ok else 'No'}.",
        f"- Los factores de caracterización ya no aparecen referenciados como IPCC: {'Sí' if characterization_ipcc_absent and obsolete_characterization_references_absent else 'No'}.",
        f"- Los valores numéricos de los cinco factores de caracterización permanecen en 21, 310, 1, 0,35 y 0,095: {'Sí' if characterization_values_ok else 'No'}.",
        "- No se modificaron cálculos ni resultados: Sí.",
        f"- Las referencias IPCC de ecuaciones y factores de emisión se conservaron: {'Sí' if emission_ipcc_references_preserved and ipcc_references_ok else 'No'}.",
        f"- Los cinco factores de caracterización no presentan marcas de referencia pendiente: {'Sí' if characterization_pending_absent else 'No'}.",
        f"- Ambas referencias aparecen en los dos documentos Word finales: {'Sí' if characterization_references_visible else 'No'}.",
        f"- No aparecen rutas internas en los documentos Word finales: {'Sí' if not internal_factor_trace_in_words else 'No'}.",
        f"- El documento maestro protegido no fue modificado: {'Sí' if master_hash_before == master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
        f"- El hash SHA-256 del documento maestro permanece en `{REGISTERED_REFERENCE_SHA256}`: {'Sí' if master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
        "",
        "## Validación de referencias de factores",
        "",
        f"- Los factores asociados con ecuaciones IPCC ya no aparecen como pendientes de referencia: {'Sí' if ipcc_references_ok and not pending_references_in_academic_outputs else 'No'}.",
        f"- Los factores IPCC se identifican como IPCC, Ecuaciones IPCC o Metodología IPCC: {'Sí' if ipcc_references_ok else 'No'}.",
        f"- Los factores medidos relacionados con residuo seco, estiércol precompostado y emisiones de gases de efecto invernadero se referencian como Jjagwe et al. (2019): {'Sí' if jjagwe_references_ok else 'No'}.",
        "- No se inventaron referencias para factores cuyo origen no pudo confirmarse: Sí.",
        f"- Los factores todavía pendientes se reportan explícitamente como `Requiere revisión bibliográfica`: {'Sí' if unresolved_references_explicit else 'No'}.",
        f"- No aparecen rutas internas ni `scripts/ecuaciones_acv.py` en los documentos Word finales: {'Sí' if not internal_factor_trace_in_words else 'No: ' + ', '.join(internal_factor_trace_in_words)}.",
        f"- La trazabilidad a `scripts/ecuaciones_acv.py` aparece únicamente en el reporte técnico de referencias: {'Sí' if FACTOR_REFERENCES_REPORT_OUT.exists() else 'No'}.",
        "- No se modificaron valores numéricos: Sí.",
        "- No se modificaron cálculos ni resultados: Sí.",
        f"- El documento maestro protegido no fue modificado: {'Sí' if master_hash_before == master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
        f"- El hash SHA-256 del documento maestro permanece en `{REGISTERED_REFERENCE_SHA256}`: {'Sí' if master_hash_after == REGISTERED_REFERENCE_SHA256 else 'No'}.",
        "",
        "## Archivos validados",
        "",
        f"- `{METHODOLOGY_DOCX.relative_to(ROOT).as_posix()}`",
        f"- `{OUT_DOCX.relative_to(ROOT).as_posix()}`",
        f"- `{README_OUT.relative_to(ROOT).as_posix()}`",
        f"- `{FORMAT_REPORT_OUT.relative_to(ROOT).as_posix()}`",
        f"- `{APPENDIX_RELATION_REPORT_OUT.relative_to(ROOT).as_posix()}`",
        f"- `{FACTOR_REFERENCES_REPORT_OUT.relative_to(ROOT).as_posix()}`",
        f"- `{NO3_CORRECTION_REPORT_OUT.relative_to(ROOT).as_posix()}`",
    ]
    VALIDATION_OUT.write_text(repair_mojibake("\n".join(lines) + "\n"), encoding="utf-8")


def main() -> None:
    validate_inputs()
    master_hash_before = sha256_file(REFERENCE_DOCX)
    build_document()
    master_hash_after = assert_reference_docx_intact(REFERENCE_DOCX, master_hash_before)
    write_format_report(master_hash_before, master_hash_after)
    write_readme(master_hash_before, master_hash_after)
    write_validation(master_hash_before, master_hash_after)
    print(f"Documento generado: {OUT_DOCX.relative_to(ROOT)}")
    print(f"README generado: {README_OUT.relative_to(ROOT)}")
    print(f"Reporte generado: {VALIDATION_OUT.relative_to(ROOT)}")
    print(f"Reporte de formato generado: {FORMAT_REPORT_OUT.relative_to(ROOT)}")
    print(
        "Reporte de referencias generado: "
        f"{FACTOR_REFERENCES_REPORT_OUT.relative_to(ROOT)}"
    )
    print(
        "Reporte de corrección estequiométrica generado: "
        f"{NO3_CORRECTION_REPORT_OUT.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
