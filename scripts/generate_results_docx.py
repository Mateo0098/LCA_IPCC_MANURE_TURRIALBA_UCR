from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
TABLE_DIR = ROOT / "outputs" / "tablas_tesis"
FIG_DIR = ROOT / "outputs" / "graficos_tesis"
WORD_TABLE_DIR = TABLE_DIR / "tablas_word"
OUT_DOCX = ROOT / "outputs" / "resultados_tfg.docx"

REQUIRED_TABLES = {
    "tabla_02": TABLE_DIR / "tabla_02_caracterizacion_muestras.csv",
    "tabla_03": TABLE_DIR / "tabla_03_flujos_icv.csv",
    "tabla_04": TABLE_DIR / "tabla_04_parametros_modelo_acv.csv",
    "tabla_05": TABLE_DIR / "tabla_05_factores_emision_y_caracterizacion.csv",
    "tabla_06": TABLE_DIR / "tabla_06_emisiones_por_etapa.csv",
    "tabla_07": TABLE_DIR / "tabla_07_impactos_por_etapa.csv",
    "tabla_08": TABLE_DIR / "tabla_08_impactos_totales_por_escenario.csv",
    "tabla_09": TABLE_DIR / "tabla_09_comparacion_escenarios.csv",
    "resumen": TABLE_DIR / "resumen_resultados_para_redaccion.md",
}

REQUIRED_FIGURES = {
    1: FIG_DIR / "fig_01_caracterizacion_humedad_materia_seca.png",
    2: FIG_DIR / "fig_02_caracterizacion_solidos_volatiles_cenizas.png",
    3: FIG_DIR / "fig_04_flujos_masa_equivalente_total.png",
    4: FIG_DIR / "fig_06_emisiones_ch4.png",
    5: FIG_DIR / "fig_11_impactos_calentamiento_global_etapa.png",
    6: FIG_DIR / "fig_12_impactos_eutrofizacion_etapa.png",
    7: FIG_DIR / "fig_15_comparacion_diferencia_porcentual.png",
}

FIGURE_CAPTIONS = {
    1: "Figura 1. Humedad y materia seca promedio por tipo de muestra.",
    2: "Figura 2. Sólidos volátiles y cenizas por tipo de muestra.",
    3: "Figura 3. Masa equivalente total por etapa y escenario.",
    4: "Figura 4. Emisiones anuales de CH4 por etapa y escenario.",
    5: "Figura 5. Potencial de calentamiento global por etapa y escenario.",
    6: "Figura 6. Potencial de eutrofización por etapa y escenario.",
    7: "Figura 7. Diferencia porcentual del escenario B respecto al escenario A por categoría de impacto.",
}

OFFICIAL_STAGE_NAMES = {
    ("A", 1): "Etapa 1: Precomposteo",
    ("A", 2): "Etapa 2: Lombricompostaje",
    ("A", 3): "Etapa 3: Almacenamiento de aguas verdes",
    ("A", 4): "Etapa 4: Aplicación de aguas verdes en campos de pastoreo",
    ("B", 1): "Etapa 1: Almacenamiento de purines",
    ("B", 2): "Etapa 2: Aplicación en campo",
}


def validate_inputs() -> None:
    missing = [str(path.relative_to(ROOT)) for path in [*REQUIRED_TABLES.values(), *REQUIRED_FIGURES.values()] if not path.exists()]
    if missing:
        raise FileNotFoundError("Faltan archivos requeridos:\n" + "\n".join(f"- {item}" for item in missing))

    forbidden = [
        path
        for path in [*REQUIRED_TABLES.values(), *REQUIRED_FIGURES.values()]
        if "antes_correccion_nitrogeno" in path.name
    ]
    if forbidden:
        names = "\n".join(f"- {path.relative_to(ROOT)}" for path in forbidden)
        raise ValueError("La lista de insumos contiene archivos no permitidos:\n" + names)


def clean_text(value):
    if pd.isna(value):
        return ""
    return str(value)


def official_stage_name(escenario, etapa) -> str:
    try:
        key = (str(escenario).strip().upper(), int(etapa))
    except (TypeError, ValueError):
        return ""
    return OFFICIAL_STAGE_NAMES.get(key, "")


def apply_official_stage_names(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if {"escenario", "etapa", "nombre_etapa"}.issubset(out.columns):
        out["nombre_etapa"] = out.apply(lambda row: official_stage_name(row["escenario"], row["etapa"]), axis=1)
    return out


def round_number(value, decimals=2):
    if pd.isna(value):
        return ""
    return round(float(value), decimals)


def fmt(value, decimals=2):
    if value == "" or pd.isna(value):
        return ""
    text = f"{float(value):,.{decimals}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", " ")


def add_table_borders(table) -> None:
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = OxmlElement(f"w:{edge}")
        tag.set(qn("w:val"), "single")
        tag.set(qn("w:sz"), "4")
        tag.set(qn("w:space"), "0")
        tag.set(qn("w:color"), "808080")
        borders.append(tag)
    tbl_pr.append(borders)


def add_caption(doc: Document, text: str) -> None:
    paragraph = doc.add_paragraph()
    run = paragraph.add_run(text)
    run.italic = True
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER


def add_dataframe_table(doc: Document, title: str, df: pd.DataFrame) -> None:
    paragraph = doc.add_paragraph()
    run = paragraph.add_run(title)
    run.bold = True

    table = doc.add_table(rows=1, cols=len(df.columns))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    add_table_borders(table)

    header_cells = table.rows[0].cells
    for idx, column in enumerate(df.columns):
        header_cells[idx].text = str(column)
        for run in header_cells[idx].paragraphs[0].runs:
            run.bold = True
        header_cells[idx].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

    for _, row in df.iterrows():
        cells = table.add_row().cells
        for idx, value in enumerate(row):
            cells[idx].text = clean_text(value)
            cells[idx].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def add_figure(doc: Document, number: int) -> None:
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    run.add_picture(str(REQUIRED_FIGURES[number]), width=Inches(6.2))
    add_caption(doc, FIGURE_CAPTIONS[number])


def set_document_style(doc: Document) -> None:
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    styles = doc.styles
    styles["Normal"].font.name = "Times New Roman"
    styles["Normal"].font.size = Pt(12)
    styles["Normal"]._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")

    for style_name in ("Heading 1", "Heading 2", "Heading 3"):
        style = styles[style_name]
        style.font.name = "Times New Roman"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")

    for paragraph in doc.paragraphs:
        paragraph.paragraph_format.line_spacing = 1.5


def format_table_for_word(df: pd.DataFrame, decimals_by_column=None) -> pd.DataFrame:
    decimals_by_column = decimals_by_column or {}
    out = df.copy()
    for column in out.columns:
        if pd.api.types.is_numeric_dtype(out[column]):
            decimals = decimals_by_column.get(column, 2)
            out[column] = out[column].map(lambda x: fmt(x, decimals))
        else:
            out[column] = out[column].map(clean_text)
    return out


def create_reduced_tables() -> dict[str, pd.DataFrame]:
    WORD_TABLE_DIR.mkdir(parents=True, exist_ok=True)

    t02 = pd.read_csv(REQUIRED_TABLES["tabla_02"])
    t03 = pd.read_csv(REQUIRED_TABLES["tabla_03"])
    t03 = apply_official_stage_names(t03)
    t04 = apply_official_stage_names(pd.read_csv(REQUIRED_TABLES["tabla_04"]))
    t05 = pd.read_csv(REQUIRED_TABLES["tabla_05"])
    t06 = apply_official_stage_names(pd.read_csv(REQUIRED_TABLES["tabla_06"]))
    t07 = apply_official_stage_names(pd.read_csv(REQUIRED_TABLES["tabla_07"]))
    t08 = pd.read_csv(REQUIRED_TABLES["tabla_08"])
    t09 = pd.read_csv(REQUIRED_TABLES["tabla_09"])

    sample_map = {"Fresh manure": "Estiércol fresco", "Precomposted manure": "Estiércol precompostado"}
    d_rows = []
    for sample, group in t02.groupby("tipo_muestra", sort=False):
        row = {"Tipo de muestra": sample_map.get(sample, sample)}
        for _, record in group.iterrows():
            variable = record["variable"]
            unit = record["unidad"]
            value = record["valor"]
            if variable == "Humedad":
                row["Humedad (% masa húmeda)"] = round_number(value, 2)
            elif variable == "Materia seca":
                row["Materia seca (% masa húmeda)"] = round_number(value, 2)
            elif variable == "Cenizas":
                row["Cenizas (% base seca)"] = round_number(value, 2)
            elif variable == "Solidos volatiles":
                row["Sólidos volátiles (% base seca)"] = round_number(value, 2)
            elif variable == "Nitrogeno total" and unit == "% N total":
                row["N total (%)"] = round_number(value, 3)
            elif variable == "Nitrogeno total" and unit == "mg N/kg muestra":
                row["N total (mg N/kg)"] = round_number(value, 2)
        d_rows.append(row)
    ap_d = pd.DataFrame(d_rows)

    ap_e = t03[t03["flujo"] == "Masa equivalente total"][
        ["escenario", "etapa", "nombre_etapa", "valor"]
    ].rename(
        columns={
            "escenario": "Escenario",
            "etapa": "Etapa",
            "nombre_etapa": "Nombre de etapa",
            "valor": "Masa equivalente total (kg eq/año)",
        }
    )
    ap_e["Masa equivalente total (kg eq/año)"] = ap_e["Masa equivalente total (kg eq/año)"].map(lambda x: round_number(x, 2))

    param_pivot = (
        t04[t04["parametro"].isin(["Nitrogeno total reportado", "Nitrogeno total como fraccion masica", "MCF", "EF3"])]
        .pivot_table(
            index=["escenario", "etapa", "nombre_etapa", "modelo_calculo", "sistema_manejo_ipcc"],
            columns="parametro",
            values="valor",
            aggfunc="first",
        )
        .reset_index()
    )
    ap_f = param_pivot.rename(
        columns={
            "escenario": "Escenario",
            "etapa": "Etapa",
            "nombre_etapa": "Nombre de etapa",
            "modelo_calculo": "Modelo de cálculo",
            "sistema_manejo_ipcc": "Sistema de manejo asignado",
            "Nitrogeno total reportado": "n_ex_pct (%)",
            "Nitrogeno total como fraccion masica": "n_ex_fraction (kg N/kg muestra)",
            "MCF": "MCF (%)",
            "EF3": "EF3",
        }
    )
    ap_f = ap_f[
        [
            "Escenario",
            "Etapa",
            "Nombre de etapa",
            "Modelo de cálculo",
            "Sistema de manejo asignado",
            "n_ex_pct (%)",
            "n_ex_fraction (kg N/kg muestra)",
            "MCF (%)",
            "EF3",
        ]
    ]
    for column in ["n_ex_pct (%)", "n_ex_fraction (kg N/kg muestra)", "MCF (%)", "EF3"]:
        if column in ap_f:
            ap_f[column] = ap_f[column].map(lambda x: round_number(x, 4))

    ap_g_source = t05[
        (t05["tipo_factor"] == "Factor de caracterizacion")
        | (t05["sistema_o_compuesto"].isin(["CH4", "N2O", "CO2", "NH3", "NO3"]))
    ].copy()
    ap_g_source = ap_g_source[ap_g_source["factor"].str.contains("Calentamiento global|Eutrofizacion|Factor", na=False) | ap_g_source["sistema_o_compuesto"].isin(["CH4", "N2O", "CO2", "NH3", "NO3"])]
    if ap_g_source.empty:
        ap_g_source = t05[t05["sistema_o_compuesto"].isin(["CH4", "N2O", "CO2", "NH3", "NO3"])].copy()
    ap_g = ap_g_source[["sistema_o_compuesto", "factor", "valor", "unidad"]].rename(
        columns={
            "sistema_o_compuesto": "Sustancia",
            "factor": "Categoría de impacto",
            "valor": "Factor de caracterización",
            "unidad": "Unidad",
        }
    )
    ap_g = ap_g[ap_g["Sustancia"].isin(["CH4", "N2O", "CO2", "NH3", "NO3"])].drop_duplicates()
    category_map = {
        "GWP100": "Calentamiento global",
        "EP": "Eutrofización",
        "Calentamiento global": "Calentamiento global",
        "Eutrofizacion": "Eutrofización",
        "Potencial de calentamiento global": "Calentamiento global",
        "Potencial de eutrofizacion": "Eutrofización",
    }
    ap_g["Categoría de impacto"] = ap_g["Categoría de impacto"].map(lambda x: category_map.get(x, x))
    ap_g["Factor de caracterización"] = ap_g["Factor de caracterización"].map(lambda x: round_number(x, 4))

    ap_h = (
        t06.groupby(["escenario", "sustancia"], as_index=False)["valor"].sum()
        .pivot(index="escenario", columns="sustancia", values="valor")
        .reset_index()
        .rename_axis(None, axis=1)
    )
    for substance in ["CH4", "N2O", "NH3", "NO3", "CO2"]:
        if substance not in ap_h:
            ap_h[substance] = 0.0
    ap_h = ap_h.fillna(0.0)
    ap_h = ap_h[["escenario", "CH4", "N2O", "NH3", "NO3", "CO2"]].rename(
        columns={
            "escenario": "Escenario",
            "CH4": "CH4 (kg/año)",
            "N2O": "N2O (kg/año)",
            "NH3": "NH3 (kg/año)",
            "NO3": "NO3 (kg/año)",
            "CO2": "CO2 (kg/año)",
        }
    )
    for column in ap_h.columns[1:]:
        ap_h[column] = ap_h[column].map(lambda x: round_number(x, 2))

    impact_stage = (
        t07.groupby(["escenario", "etapa", "nombre_etapa", "categoria_impacto"], as_index=False)["resultado_equivalente"].sum()
        .pivot(index=["escenario", "etapa", "nombre_etapa"], columns="categoria_impacto", values="resultado_equivalente")
        .reset_index()
        .rename_axis(None, axis=1)
    )
    ap_i = impact_stage.rename(
        columns={
            "escenario": "Escenario",
            "etapa": "Etapa",
            "nombre_etapa": "Nombre de etapa",
            "Calentamiento global": "Calentamiento global (kg CO2-eq/año)",
            "Eutrofizacion": "Eutrofización (kg PO4-eq/año)",
        }
    )
    for column in ["Calentamiento global (kg CO2-eq/año)", "Eutrofización (kg PO4-eq/año)"]:
        ap_i[column] = ap_i[column].map(lambda x: round_number(x, 2))

    ap_j = (
        t08.pivot(index="escenario", columns="categoria_impacto", values="resultado_total")
        .reset_index()
        .rename_axis(None, axis=1)
        .rename(
            columns={
                "escenario": "Escenario",
                "Calentamiento global": "Calentamiento global (kg CO2-eq/año)",
                "Eutrofizacion": "Eutrofización (kg PO4-eq/año)",
            }
        )
    )
    for column in ["Calentamiento global (kg CO2-eq/año)", "Eutrofización (kg PO4-eq/año)"]:
        ap_j[column] = ap_j[column].map(lambda x: round_number(x, 2))

    ap_k = t09[
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
    ap_k["Categoría de impacto"] = ap_k["Categoría de impacto"].replace({"Eutrofizacion": "Eutrofización"})
    for column in ["Escenario A", "Escenario B", "Diferencia absoluta", "Diferencia porcentual B respecto a A"]:
        ap_k[column] = ap_k[column].map(lambda x: round_number(x, 3 if column == "Diferencia absoluta" else 2))

    outputs = {
        "D": ap_d,
        "E": ap_e,
        "F": ap_f,
        "G": ap_g,
        "H": ap_h,
        "I": ap_i,
        "J": ap_j,
        "K": ap_k,
    }
    csv_names = {
        "D": "apendice_D_caracterizacion_muestras_word.csv",
        "E": "apendice_E_flujos_icv_word.csv",
        "F": "apendice_F_parametros_modelo_word.csv",
        "G": "apendice_G_factores_caracterizacion_word.csv",
        "H": "apendice_H_emisiones_word.csv",
        "I": "apendice_I_impactos_por_etapa_word.csv",
        "J": "apendice_J_impactos_totales_word.csv",
        "K": "apendice_K_comparacion_escenarios_word.csv",
    }
    for key, df in outputs.items():
        df.to_csv(WORD_TABLE_DIR / csv_names[key], index=False, encoding="utf-8-sig")
    return outputs


def add_correspondence_table(doc: Document) -> None:
    doc.add_heading("Correspondencia entre apéndices y archivos fuente", level=2)
    data = pd.DataFrame(
        [
            ["Apéndice D", "Caracterización fisicoquímica de las muestras.", "Sección 6.1."],
            ["Apéndice E", "Flujos del inventario de ciclo de vida.", "Sección 6.2."],
            ["Apéndice F", "Parámetros utilizados en el modelo ACV.", "Sección 6.3."],
            ["Apéndice G", "Factores de emisión y caracterización.", "Sección 6.3."],
            ["Apéndice H", "Emisiones estimadas por etapa y escenario.", "Sección 6.4."],
            ["Apéndice I", "Impactos ambientales por etapa.", "Sección 6.5."],
            ["Apéndice J", "Impactos ambientales totales por escenario.", "Sección 6.6."],
            ["Apéndice K", "Comparación de impactos ambientales entre escenarios.", "Sección 6.7."],
        ],
        columns=["Apéndice", "Contenido", "Sección de resultados relacionada"],
    )
    add_dataframe_table(doc, "", data)


def build_document(tables: dict[str, pd.DataFrame]) -> None:
    doc = Document()
    set_document_style(doc)

    doc.add_heading("6. Resultados", level=1)

    doc.add_heading("6.1 Caracterización de las muestras analizadas", level=2)
    doc.add_paragraph(
        "La caracterización de las muestras analizadas permitió obtener los parámetros fisicoquímicos empleados como datos de entrada para el inventario de ciclo de vida. "
        "En el estiércol fresco se registró una humedad promedio de 85,77 % y una materia seca de 14,23 %, mientras que en el estiércol precompostado la humedad fue de 77,59 % y la materia seca de 22,41 %. "
        "Como se muestra en la Figura 1, el material precompostado presentó una menor proporción de humedad y una mayor fracción de materia seca respecto al estiércol fresco."
    )
    add_figure(doc, 1)
    doc.add_paragraph(
        "En relación con la composición de la materia seca, el estiércol fresco presentó 85,88 % de sólidos volátiles y 14,12 % de cenizas. "
        "El estiércol precompostado presentó 70,96 % de sólidos volátiles y 29,04 % de cenizas, lo que indica una mayor proporción mineral en el material precompostado. "
        "El nitrógeno total fue de 2,425 % en el precompostado, equivalente a 24 250 mg N/kg, y de 0,372 % en el estiércol fresco, equivalente a 3716,67 mg N/kg. "
        "Estos resultados se resumen en el Apéndice D, y los patrones de sólidos volátiles y cenizas se presentan en la Figura 2."
    )
    add_figure(doc, 2)
    add_dataframe_table(doc, "Apéndice D. Resumen de caracterización fisicoquímica de las muestras.", format_table_for_word(tables["D"], {"N total (%)": 3}))

    doc.add_heading("6.2 Flujos del inventario de ciclo de vida", level=2)
    doc.add_paragraph(
        "Los flujos del inventario de ciclo de vida permitieron cuantificar la masa equivalente anual asociada con cada etapa y escenario. "
        "La mayor contribución individual correspondió a B2, correspondiente a la Etapa 2: Aplicación en campo, con 76 557,27 kg eq/año, seguida de A4, correspondiente a la Etapa 4: Aplicación de aguas verdes en campos de pastoreo, con 71 789,81 kg eq/año. "
        "En contraste, A3, correspondiente a la Etapa 3: Almacenamiento de aguas verdes, presentó 358,84 kg eq/año. El total del escenario A fue de 78 388,50 kg eq/año y el del escenario B fue de 81 683,56 kg eq/año. "
        "La diferencia B - A fue de 3295,06 kg eq/año, equivalente aproximadamente a 4,2 %. Como se muestra en la Figura 3, la distribución de masa estuvo dominada por las etapas líquidas o de aplicación. "
        "Los valores completos se presentan en el Apéndice E."
    )
    add_figure(doc, 3)
    add_dataframe_table(doc, "Apéndice E. Resumen de flujos de masa equivalente total.", format_table_for_word(tables["E"]))

    doc.add_heading("6.3 Parámetros utilizados en el modelo ACV", level=2)
    doc.add_paragraph(
        "Los parámetros utilizados en el modelo ACV se organizaron por escenario y etapa. "
        "El parámetro n_ex_pct corresponde al nitrógeno total reportado en porcentaje, mientras que n_ex_fraction corresponde a la fracción másica usada en las ecuaciones de nitrógeno. "
        "A1, correspondiente a la Etapa 1: Precomposteo, empleó el sistema dry_lot con modelo IPCC, y A2, correspondiente a la Etapa 2: Lombricompostaje, utilizó un modelo medido. "
        "De acuerdo con la tabla actual de parámetros, A3, correspondiente a la Etapa 3: Almacenamiento de aguas verdes; A4, correspondiente a la Etapa 4: Aplicación de aguas verdes en campos de pastoreo; B1, correspondiente a la Etapa 1: Almacenamiento de purines; y B2, correspondiente a la Etapa 2: Aplicación en campo, utilizaron el sistema uncovered_anaerobic_lagoon. "
        "La información detallada se presenta en el Apéndice F."
    )
    add_dataframe_table(doc, "Apéndice F. Resumen de parámetros por escenario y etapa.", format_table_for_word(tables["F"], {"n_ex_pct (%)": 4, "n_ex_fraction (kg N/kg muestra)": 4, "EF3": 4}))
    doc.add_paragraph(
        "Los factores de caracterización aplicados fueron: CH4 = 21 kg CO2-eq/kg, N2O = 310 kg CO2-eq/kg, CO2 = 1 kg CO2-eq/kg, NH3 = 0,35 kg PO4-eq/kg y NO3 = 0,095 kg PO4-eq/kg. "
        "Estos factores se sintetizan en el Apéndice G."
    )
    add_dataframe_table(doc, "Apéndice G. Factores de caracterización utilizados.", format_table_for_word(tables["G"], {"Factor de caracterización": 4}))

    doc.add_heading("6.4 Emisiones estimadas por etapa y escenario", level=2)
    doc.add_paragraph(
        "Las emisiones estimadas por escenario mostraron diferencias claras entre alternativas de manejo. "
        "El escenario A presentó 9,55 kg CH4/año, 0,79 kg N2O/año, 5,23 kg NH3/año, 19,06 kg NO3/año y 33,65 kg CO2/año. "
        "El escenario B presentó 80,59 kg CH4/año, 0,31 kg N2O/año, 6,35 kg NH3/año, 23,17 kg NO3/año y 0 kg CO2/año. "
        "Como se muestra en la Figura 4, B1, correspondiente a la Etapa 1: Almacenamiento de purines, fue la mayor fuente de CH4. Además, B1 concentró las mayores emisiones de NH3 y NO3, mientras que A1, correspondiente a la Etapa 1: Precomposteo, fue la mayor fuente de N2O. "
        "A2, correspondiente a la Etapa 2: Lombricompostaje, reportó CO2 por el uso de un factor medido. La información detallada por etapa se presenta en el Apéndice H."
    )
    add_figure(doc, 4)
    add_dataframe_table(doc, "Apéndice H. Resumen de emisiones anuales por escenario y sustancia.", format_table_for_word(tables["H"]))

    doc.add_heading("6.5 Impactos ambientales por etapa", level=2)
    doc.add_paragraph(
        "Los impactos ambientales por etapa evidenciaron una concentración del potencial de calentamiento global en el escenario B. "
        "B1, correspondiente a la Etapa 1: Almacenamiento de purines, alcanzó 1737,81 kg CO2-eq/año, mientras que en el escenario A los valores fueron 241,72 kg CO2-eq/año en A1 (Etapa 1: Precomposteo), 86,31 kg CO2-eq/año en A2 (Etapa 2: Lombricompostaje), 121,65 kg CO2-eq/año en A3 (Etapa 3: Almacenamiento de aguas verdes) y 29,10 kg CO2-eq/año en A4 (Etapa 4: Aplicación de aguas verdes en campos de pastoreo). "
        "Estos resultados se presentan gráficamente en la Figura 5 y de forma detallada en el Apéndice I."
    )
    add_figure(doc, 5)
    doc.add_paragraph(
        "Para la eutrofización, B1 (Etapa 1: Almacenamiento de purines) presentó 2,78 kg PO4-eq/año y A1 (Etapa 1: Precomposteo) presentó 2,48 kg PO4-eq/año. "
        "A2 (Etapa 2: Lombricompostaje) registró 0 kg PO4-eq/año en la tabla final, debido a que dicha tabla no reporta emisiones de NH3 ni NO3 para esa etapa. "
        "Como se muestra en la Figura 6, las contribuciones de eutrofización se asociaron con las etapas que reportaron emisiones nitrogenadas relevantes."
    )
    add_figure(doc, 6)
    add_dataframe_table(doc, "Apéndice I. Resumen de impactos ambientales por etapa.", format_table_for_word(tables["I"]))

    doc.add_heading("6.6 Impactos totales por escenario", level=2)
    doc.add_paragraph(
        "Los impactos totales por escenario muestran que el escenario A alcanzó 478,78 kg CO2-eq/año, mientras que el escenario B alcanzó 1787,19 kg CO2-eq/año. "
        "Para eutrofización, el escenario A presentó 3,64 kg PO4-eq/año y el escenario B presentó 4,43 kg PO4-eq/año. "
        "Los valores completos se presentan en el Apéndice J."
    )
    add_dataframe_table(doc, "Apéndice J. Impactos ambientales totales por escenario.", format_table_for_word(tables["J"]))

    doc.add_heading("6.7 Comparación entre escenarios", level=2)
    doc.add_paragraph(
        "La comparación entre escenarios indicó que el calentamiento global fue mayor en el escenario B. "
        "El escenario A presentó 478,78 kg CO2-eq/año y el escenario B presentó 1787,19 kg CO2-eq/año, con una diferencia absoluta de 1308,41 kg CO2-eq/año y una diferencia porcentual de 273,28 %. "
        "En eutrofización, el escenario A registró 3,64 kg PO4-eq/año y el escenario B 4,43 kg PO4-eq/año, con una diferencia absoluta de 0,786 kg PO4-eq/año y una diferencia porcentual de 21,58 %. "
        "Como se muestra en la Figura 7, el incremento relativo fue más marcado en calentamiento global. La comparación completa se presenta en el Apéndice K."
    )
    add_figure(doc, 7)
    add_dataframe_table(doc, "Apéndice K. Comparación de impactos ambientales entre escenarios.", format_table_for_word(tables["K"], {"Diferencia absoluta": 3}))

    add_correspondence_table(doc)

    for paragraph in doc.paragraphs:
        paragraph.paragraph_format.line_spacing = 1.5
        for run in paragraph.runs:
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)

    doc.save(OUT_DOCX)


def main() -> None:
    validate_inputs()
    tables = create_reduced_tables()
    build_document(tables)
    print(f"Documento generado: {OUT_DOCX.relative_to(ROOT)}")
    print(f"Tablas reducidas generadas en: {WORD_TABLE_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
