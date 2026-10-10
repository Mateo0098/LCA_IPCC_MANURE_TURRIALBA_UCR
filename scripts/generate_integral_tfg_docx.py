from __future__ import annotations

import re
import sys
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle
from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import generate_conclusions_docx as conclusions_source  # noqa: E402
import generate_methodology_docx as methodology_source  # noqa: E402
import generate_results_docx as results_source  # noqa: E402
from academic_text_utils import (  # noqa: E402
    clean_academic_label,
    find_campaign_unit_corruptions,
)
from academic_acronyms import (  # noqa: E402
    ACRONYMS,
    IGNORED_ACRONYM_CANDIDATES,
    acronym_by_code,
    acronym_is_used,
    unregistered_acronym_candidates,
    used_acronyms,
)
from academic_word_math import add_word_equation  # noqa: E402
from master_word_format import (  # noqa: E402
    add_master_caption,
    apply_master_format,
    finalize_document_format,
    format_table_like_master,
)
from reference_docx_utils import (  # noqa: E402
    REGISTERED_REFERENCE_SHA256,
    assert_reference_docx_intact,
    get_reference_docx_path,
    sha256_file,
)


PROVISIONAL_LABEL = "PROVISIONAL M1–M2"
MASTER = ROOT / "MASTER_escrito" / "TFG_ACV_Estiercol_MASTER.docx"
REFERENCES = ROOT / "docs" / "REFERENCIAS_TFG.md"
SENSITIVITY = ROOT / "outputs" / "auditoria_n_reactivo" / "sensibilidad_n2_a2.csv"
OUT_DIR = ROOT / "outputs" / "documentos_tfg"
OUT_DOCX = OUT_DIR / "TFG_ACV_Estiercol_INTEGRAL_PROVISIONAL_M1_M2.docx"
OUT_VALIDATION = OUT_DIR / "reporte_validacion_documento_integral.md"
FIG_DIR = ROOT / "outputs" / "graficos_tesis"
INTEGRAL_FIG_DIR = OUT_DIR / "recursos_integral"
SYSTEM_BOUNDARY_PNG = INTEGRAL_FIG_DIR / "fronteras_sistema_integral.png"
SYSTEM_BOUNDARY_SVG = INTEGRAL_FIG_DIR / "fronteras_sistema_integral.svg"

OBJECTIVE_GENERAL = (
    "Desarrollar un Análisis de Ciclo de Vida del manejo del estiércol del ganado "
    "de una lechería especializada, para estimación del impacto ambiental."
)
OBJECTIVE_SPECIFIC_1 = (
    "Realizar el inventario para el Análisis de Ciclo de Vida del estiércol bovino "
    "manejado mediante lombricompostaje y el aplicado como purines directamente en "
    "los campos de pastoreo."
)
OBJECTIVE_SPECIFIC_2 = (
    "Evaluar el impacto ambiental del estiércol bovino manejado mediante "
    "lombricompostaje y el aplicado como purines directamente en los campos de pastoreo."
)

EXPECTED_HEADINGS = [
    "1. Introducción",
    "2. Marco teórico y antecedentes",
    "3. Objetivos",
    "4. Metodología",
    "5. Resultados provisionales M1–M2",
    "6. Discusión provisional",
    "7. Conclusiones provisionales",
    "8. Recomendaciones",
    "9. Referencias",
    "Apéndice A. Trazabilidad entre objetivos y evidencia provisional",
    "Apéndice B. Matriz detallada de procedencia de los datos del inventario",
    "Apéndice C. Matriz detallada de trazabilidad metodológica por etapa A1–B2",
    "Apéndice D. Trazabilidad experimental de las campañas M1–M2",
    "Apéndice E. Balances intermedios y emisiones desagregadas",
]

REQUIRED_REFERENCE_KEYS = {
    "Arfelli2023",
    "Asman1998",
    "Baek2020",
    "Barrantes2019",
    "CalderonChaves2020",
    "Callejo2020",
    "ConejoMoralesWingChing2020",
    "Curran2006",
    "Curran2013",
    "EMEPEEA2023",
    "AndreasiBassi2023",
    "Fernandez2014",
    "Garro2016",
    "Garza2021",
    "Hou2015",
    "IMN2021",
    "IMN2026",
    "INEC2023",
    "IPCC2019",
    "ISO140402006",
    "Jjagwe2019",
    "Komakech2014",
    "Komakech2015",
    "Komakech2016",
    "Kupper2020",
    "Leitner2020",
    "Lim2016",
    "Macktoobian2024",
    "MAG2018",
    "MARM2010",
    "Moller2004",
    "Monteny1998",
    "NRCS2009",
    "RojasElizondo2020",
    "Salazar2012",
    "SanchezBrenes2026",
    "VargasSarmiento2023",
    "VanderZaag2013",
    "VanderZaag2018",
    "Zhou2017",
}

INTERNAL_CANDIDATE_REFERENCE_KEYS = {
    "Anton2004",
    "Cordero2013",
    "Ecobilan1999",
}


@dataclass
class EditorialCounters:
    table: int = 0
    figure: int = 0
    equation: int = 0


def validate_inputs() -> Path:
    reference = get_reference_docx_path(ROOT)
    if reference != MASTER:
        raise RuntimeError("La ruta validada del MASTER no coincide con la esperada.")
    required = [REFERENCES, SENSITIVITY]
    missing = [path.relative_to(ROOT) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Faltan entradas para el documento integral: {missing}")
    methodology_source.validate_inputs()
    results_source.validate_inputs()
    return reference


def master_text(document: Document, index: int) -> str:
    value = document.paragraphs[index].text.strip()
    if not value:
        raise RuntimeError(f"El párrafo {index} esperado del MASTER está vacío.")
    return value


def add_text(document: Document, paragraphs: list[str]) -> None:
    for value in paragraphs:
        document.add_paragraph(clean_academic_label(value), style="Normal")


def add_master_paragraphs(document: Document, master: Document, indexes: range | list[int]) -> None:
    values = []
    for index in indexes:
        value = master.paragraphs[index].text.strip()
        if index == 28:
            value = value.replace(
                "Instituto Nacional de Estadística y Censo [INEC]",
                "Instituto Nacional de Estadística y Censos (INEC)",
                1,
            )
        elif index == 29:
            value = value.replace(
                "Ministerio de Agricultura y Ganadería [MAG]",
                "Ministerio de Agricultura y Ganadería (MAG)",
                1,
            )
        elif index == 31:
            value = value.replace("IMN, 2021", "Instituto Meteorológico Nacional (IMN), 2021", 1)
        elif index == 52:
            value = value.replace("(NRCS, 2009)", "(NRCS, por sus siglas en inglés; 2009)")
            value = value.replace("(USDA)", "(USDA, por sus siglas en inglés)")
        elif index == 74:
            value = value.replace(
                "Directrices del IPCC",
                "Directrices del Grupo Intergubernamental de Expertos sobre el Cambio Climático "
                "(IPCC, por sus siglas en inglés)",
                1,
            )
        values.append(value)
    add_text(document, [value for value in values if value])


def add_chapter(document: Document, title: str, *, first: bool = False) -> None:
    if not first:
        document.add_page_break()
    document.add_heading(title, level=1)


def display_value(value: object, decimals: int = 4) -> str:
    if pd.isna(value):
        return "—"
    if isinstance(value, bool):
        return "Sí" if value else "No"
    if isinstance(value, (int, float)):
        return results_source.fmt(value, decimals)
    text = clean_academic_label(value)
    replacements = {
        "ESTIERCOL FRESCO": "Estiércol fresco",
        "SOL: PRECOMPOSTADO": "Estiércol precompostado",
        "LIQ: AGUA VERDE": "Aguas verdes",
        "LIQ: PURINES": "Purines",
        "ipcc": "IPCC",
        "Amoniaco": "Amoníaco",
        "NOx as NO₂": "NOx como NO₂",
        "15a edición": "15.ª edición",
    }
    for source, target in replacements.items():
        text = text.replace(source, target)
    return text


def experimental_body_table() -> pd.DataFrame:
    """Vista compacta de la procedencia experimental y su función en el ACV."""

    return pd.DataFrame(
        [
            {
                "Material": "Estiércol fresco",
                "Procedencia física": "Sala de espera; cinco submuestras de puntos aleatorios por muestra compuesta",
                "Determinaciones": "Humedad, materia seca, cenizas, sólidos volátiles y N total",
                "Laboratorio": "Bioenergía y LASA",
                "Relación con el sistema": "A1: Precomposteo; A3: Almacenamiento de aguas verdes; B1: Almacenamiento de purines",
                "Función metodológica": "Materia seca y sólidos volátiles para CH₄; N total para inicializar N y TAN en las fronteras frescas; cenizas para la transformación A1→A2",
            },
            {
                "Material": "Estiércol precompostado",
                "Procedencia física": "Pila con mayor permanencia, lista para alimentar las lombrices; no corresponde a lombricompost terminado",
                "Determinaciones": "Humedad, materia seca, cenizas, sólidos volátiles, N total, C y relación C/N",
                "Laboratorio": "Bioenergía y CIA",
                "Relación con el sistema": "Salida de A1 y material de entrada a A2: Lombricompostaje",
                "Función metodológica": "Materia seca y cenizas para la transformación A1→A2; materia seca y sólidos volátiles para CH₄; N como referencia de contraste sin reinicializar A2; C y C/N como caracterización descriptiva",
            },
            {
                "Material": "Aguas verdes",
                "Procedencia física": "Tanqueta del Escenario A, después de remoción manual; cinco alícuotas consecutivas desde una abertura",
                "Determinaciones": "M1: N–NH₄, N–NO₃ y N ureico; M2: N total",
                "Laboratorio": "CIA",
                "Relación con el sistema": "A3: Almacenamiento de aguas verdes y A4: Aplicación de aguas verdes en campos de pastoreo",
                "Función metodológica": "M1 se conserva como especiación de trazabilidad; M2 aporta la referencia provisional de contraste y no reinicializa el N ni el TAN propagados",
            },
            {
                "Material": "Purines",
                "Procedencia física": "Tanqueta durante la operación temporal del Escenario B, después de remoción manual; cinco alícuotas consecutivas desde una abertura",
                "Determinaciones": "M1: N–NH₄, N–NO₃ y N ureico; M2: N total",
                "Laboratorio": "CIA",
                "Relación con el sistema": "B1: Almacenamiento de purines y B2: Aplicación de purines en campo de pastoreo",
                "Función metodológica": "M1 se conserva como especiación de trazabilidad; M2 aporta la referencia provisional de contraste y no reinicializa el N ni el TAN propagados",
            },
        ]
    )


def experimental_campaign_table() -> pd.DataFrame:
    """Diseño físico ejecutado, sin reproducir observaciones ni réplicas crudas."""

    rows = [
        ("M1", "Muestreo: 10 de noviembre de 2025; recepción LASA: 11 de noviembre", "Estiércol fresco", "4: dos para Bioenergía y dos independientes para LASA", "Bioenergía: gravimetría; LASA: N total por Kjeldahl", "Conjuntos físicos disjuntos entre laboratorios"),
        ("M1", "Recepción CIA: 10 de noviembre de 2025", "Estiércol precompostado", "4: dos para Bioenergía y dos independientes para CIA", "Bioenergía: gravimetría; CIA: N y C por Dumas", "Conjuntos físicos disjuntos entre laboratorios"),
        ("M1", "Recepción CIA: 10 de noviembre de 2025", "Aguas verdes", "2", "CIA: N–NH₄, N–NO₃ y N ureico", "Especiación conservada únicamente para trazabilidad"),
        ("M1", "Recepción CIA: 17 de noviembre de 2025", "Purines", "2", "CIA: N–NH₄, N–NO₃ y N ureico", "Especiación conservada únicamente para trazabilidad"),
        ("M2", "Recepción LASA: 23 de julio de 2026", "Estiércol fresco", "3", "Bioenergía: gravimetría; LASA: N total por Kjeldahl", "Tres réplicas gravimétricas por muestra; el remanente de las mismas muestras se remitió a LASA"),
        ("M2", "Recepción CIA: 23 de julio de 2026", "Estiércol precompostado", "3", "Bioenergía: gravimetría; CIA: N y C por Dumas", "Tres réplicas gravimétricas por muestra; el remanente de las mismas muestras se remitió a CIA"),
        ("M2", "Recepción CIA: 23 de julio de 2026", "Aguas verdes", "3", "CIA: N total por Kjeldahl y colorimetría por análisis de inyección en flujo", "Estimador provisional líquido; uso de contraste"),
        ("M2", "Recepción CIA: 27 de julio de 2026", "Purines", "3", "CIA: N total por Kjeldahl y colorimetría por análisis de inyección en flujo", "Estimador provisional líquido; uso de contraste"),
    ]
    return pd.DataFrame(
        rows,
        columns=[
            "Campaña",
            "Identificación temporal",
            "Material",
            "Muestras compuestas",
            "Determinación y laboratorio",
            "Relación física y condición de uso",
        ],
    )


def experimental_parameter_table() -> pd.DataFrame:
    """Resultados intermedios esenciales recuperados de la integración vigente."""

    integration = pd.read_csv(
        ROOT / "processed" / "muestreos_integracion_interjornada_provisional.csv",
        encoding="utf-8-sig",
    )
    selected = {
        ("estiércol fresco", "N total"): "Inicialización productiva de N total y TAN en A1, A3 y B1",
        ("estiércol fresco", "materia seca"): "Conversión de sólidos volátiles a base húmeda y transformación A1→A2",
        ("estiércol fresco", "cenizas"): "Transformación de masa A1→A2",
        ("estiércol fresco", "sólidos volátiles"): "Estimación de CH₄ en A1, A3 y B1",
        ("estiércol precompostado", "N total"): "Referencia experimental de A2; no reinicializa N total ni TAN",
        ("estiércol precompostado", "materia seca"): "Conversión de sólidos volátiles a base húmeda, transformación A1→A2 y conversión autorizada de la referencia de N",
        ("estiércol precompostado", "cenizas"): "Transformación de masa A1→A2",
        ("estiércol precompostado", "sólidos volátiles"): "Estimación de CH₄ en A2",
        ("aguas verdes", "N total"): "Referencia provisional de contraste; no reinicializa A3 ni A4",
        ("purines", "N total"): "Referencia provisional de contraste; no reinicializa B1 ni B2",
        ("estiércol precompostado", "carbono"): "Caracterización descriptiva; no se consume en el ACV",
        ("estiércol precompostado", "relación C/N"): "Caracterización descriptiva; no se consume en el ACV",
    }
    rows: list[dict[str, str]] = []
    for _, source in integration.iterrows():
        key = (str(source["material"]), str(source["variable"]))
        if key not in selected:
            continue
        base = str(source["unidad"])
        if key == ("estiércol precompostado", "N total"):
            base = "% en material acondicionado a 80 °C durante 48 h"
        rows.append(
            {
                "Material o derivación": source["material"].capitalize(),
                "Variable": "Relación C/N" if source["variable"] == "relación C/N" else source["variable"].capitalize(),
                "Campañas elegibles": str(source["jornadas_elegibles"]).replace(";", "–"),
                "Resultado provisional": results_source.fmt(float(source["valor_integrado_provisional"]), 4),
                "Base o unidad": base,
                "Función en el modelo": selected[key],
            }
        )
    transformation = pd.read_csv(
        ROOT / "processed" / "muestreos_transformacion_masa_interjornada.csv",
        encoding="utf-8-sig",
    )
    integrated = transformation.loc[transformation["tipo_fila"] == "integracion"].iloc[0]
    rows.append(
        {
            "Material o derivación": "Transformación de estiércol fresco a precompostado",
            "Variable": "Razón de masa húmeda remanente",
            "Campañas elegibles": str(integrated["jornadas_elegibles"]).replace(";", "–"),
            "Resultado provisional": results_source.fmt(float(integrated["mass_ratio_integrado"]), 6),
            "Base o unidad": "kg/kg",
            "Función en el modelo": "Masa húmeda inferida que ingresa a A2; calculada primero por campaña y luego integrada con igual peso temporal",
        }
    )
    return pd.DataFrame(rows)


def nitrogen_propagation_table() -> pd.DataFrame:
    """Vista académica del balance canónico, sin recalcular sus magnitudes."""

    ledger = pd.read_csv(
        ROOT / "processed" / "reactive_n_ledger.csv",
        encoding="utf-8-sig",
    )
    propagated = ledger["n_total_out_kg"].where(
        ledger["n_total_out_kg"].notna(), ledger["n_returned_emep_kg"]
    )
    return pd.DataFrame(
        {
            "Etapa del sistema": ledger["stage"],
            "N total de entrada (kg N/año)": ledger["n_total_in_kg"],
            "TAN de entrada (kg N/año)": ledger["tan_in_kg"],
            "N transferido o retornado según EMEP (kg N/año)": propagated,
            "N residual del suelo después de pérdidas directas (kg N/año)": ledger[
                "soil_n_remaining_after_direct_losses_kg"
            ],
            "TAN de salida (kg N/año)": ledger["tan_out_kg"],
        }
    )


def nitrogen_direct_loss_table() -> pd.DataFrame:
    """Pérdidas físicas del balance expresadas sobre una base común de N."""

    ledger = pd.read_csv(
        ROOT / "processed" / "reactive_n_ledger.csv",
        encoding="utf-8-sig",
    )
    tan_basis = ledger["stage"].map(
        {
            "A1: Precomposteo": "TAN de entrada",
            "A2: Lombricompostaje": "TAN de entrada",
            "A3: Almacenamiento de aguas verdes": "TAN disponible después de mineralización",
            "A4: Aplicación de aguas verdes en campos de pastoreo": "TAN de entrada a la aplicación",
            "B1: Almacenamiento de purines": "TAN disponible después de mineralización",
            "B2: Aplicación de purines en campo de pastoreo": "TAN de entrada a la aplicación",
        }
    )
    return pd.DataFrame(
        {
            "Etapa del sistema": ledger["stage"],
            "Base de TAN para las pérdidas": tan_basis,
            "NH₃-N (kg N/año)": ledger["nh3_n_kg"],
            "NOx-N (kg N/año)": ledger["nox_n_kg"],
            "N₂-N (kg N/año)": ledger["n2_n_kg"],
            "N₂O-N directo (kg N/año)": ledger["n2o_n_direct_kg"],
            "N perdido en agua durante el manejo (kg N/año)": ledger["n_water_loss_kg"],
            "N por lixiviación o escorrentía (kg N/año)": ledger["n_leach_runoff_kg"],
        }
    )


def detailed_emission_table() -> pd.DataFrame:
    """Desagrega rutas ya calculadas en la tabla canónica de emisiones."""

    emissions = pd.read_csv(
        ROOT / "outputs" / "tablas_tesis" / "tabla_06_emisiones_por_etapa.csv",
        encoding="utf-8-sig",
    )
    emissions = emissions.loc[
        ~emissions["sustancia"].astype(str).str.contains("diésel", case=False, na=False)
    ].copy()
    stages = (
        emissions[["escenario", "etapa", "nombre_etapa"]]
        .drop_duplicates()
        .sort_values(["escenario", "etapa"])
    )
    rows: list[dict[str, str | float]] = []
    for _, stage in stages.iterrows():
        selected = emissions.loc[
            (emissions["escenario"] == stage["escenario"])
            & (emissions["etapa"] == stage["etapa"])
        ]
        values = {
            "CH₄ (kg/año)": 0.0,
            "N₂O directo (kg/año)": 0.0,
            "N₂O indirecto por volatilización (kg/año)": 0.0,
            "N₂O indirecto por lixiviación (kg/año)": 0.0,
            "NH₃ (kg/año)": 0.0,
            "NOx como NO₂ (kg/año)": 0.0,
            "NO₃⁻ (kg/año)": 0.0,
        }
        for _, emission in selected.iterrows():
            substance = str(emission["sustancia"])
            description = str(emission["emision"]).casefold()
            value = float(emission["valor"])
            if substance == "CH4":
                values["CH₄ (kg/año)"] = value
            elif substance == "N2O" and (
                "indirecto por volatilizacion" in description
                or "indirecto por deposicion atmosferica" in description
            ):
                values["N₂O indirecto por volatilización (kg/año)"] = value
            elif substance == "N2O" and "indirecto" in description and "lixiviacion" in description:
                values["N₂O indirecto por lixiviación (kg/año)"] = value
            elif substance == "N2O" and description.startswith("n2o directo"):
                values["N₂O directo (kg/año)"] = value
            elif substance == "NH3":
                values["NH₃ (kg/año)"] = value
            elif substance == "NOx":
                values["NOx como NO₂ (kg/año)"] = value
            elif substance == "NO3":
                values["NO₃⁻ (kg/año)"] = value
        rows.append(
            {
                "Etapa del sistema": f"{stage['escenario']}{int(stage['etapa'])}: "
                + re.sub(r"^Etapa\s+\d+:\s*", "", str(stage["nombre_etapa"])),
                **values,
            }
        )
    return pd.DataFrame(rows)


def climate_contribution_table() -> pd.DataFrame:
    """Recupera la desagregación climática ya calculada por el pipeline."""

    totals = pd.read_csv(
        ROOT / "processed" / "acv_impacto_total_por_escenario.csv",
        encoding="utf-8-sig",
    )
    return totals[
        [
            "Escenario",
            "clima_manejo_ef31_kg_co2eq",
            "clima_electricidad_imn_kg_co2eq",
            "clima_diesel_ef31_kg_co2eq",
            "impacto_calentamiento_global_kg_co2eq",
        ]
    ].rename(
        columns={
            "clima_manejo_ef31_kg_co2eq": "Manejo del estiércol (kg CO₂-eq/año)",
            "clima_electricidad_imn_kg_co2eq": "Electricidad (kg CO₂-eq/año)",
            "clima_diesel_ef31_kg_co2eq": "Diésel (kg CO₂-eq/año)",
            "impacto_calentamiento_global_kg_co2eq": "Cambio climático total (kg CO₂-eq/año)",
        }
    )


def operational_resource_context() -> dict[str, float]:
    """Magnitudes operativas únicas recuperadas de las salidas responsables."""

    inventory = pd.read_csv(
        ROOT / "processed" / "acv_inventario_recursos_operativos.csv",
        encoding="utf-8-sig",
    )
    totals = pd.read_csv(
        ROOT / "processed" / "acv_impacto_total_por_escenario.csv",
        encoding="utf-8-sig",
    )
    electricity = inventory.loc[inventory["flujo"] == "Electricidad"].iloc[0]
    diesel = inventory.loc[inventory["flujo"] == "Diésel"].iloc[0]
    climate = totals.loc[totals["Escenario"] == "A"].iloc[0]
    return {
        "electricity_kwh": float(electricity["cantidad_anual"]),
        "diesel_l": float(diesel["cantidad_anual"]),
        "electricity_climate": float(climate["clima_electricidad_imn_kg_co2eq"]),
        "diesel_climate": float(climate["clima_diesel_ef31_kg_co2eq"]),
        "diesel_co2": float(diesel["co2_fosil_diesel_kg"]),
        "diesel_ch4": float(diesel["ch4_fosil_diesel_kg"]),
        "diesel_n2o": float(diesel["n2o_combustion_diesel_kg"]),
    }


def inventory_mass_table() -> pd.DataFrame:
    """Masas activas por etapa recuperadas de la vista académica vigente."""

    flows = results_source.flow_summary()
    stage_codes = flows["Escenario"].astype(str) + flows["Etapa"].astype(int).astype(str)
    stage_names = flows["Nombre de etapa"].astype(str).str.replace(
        r"^Etapa\s+\d+:\s*", "", regex=True
    )
    meanings = {
        "A1": "Estiércol fresco recolectado; masa húmeda anual",
        "A2": "Precompostado de entrada; masa húmeda inferida mediante la transformación A1→A2",
        "A3": "Fracción de boñiga incorporada a las aguas verdes; el agua se excluye de esta masa de actividad",
        "A4": "Masa equivalente: agua de lavado + fracción de boñiga; no es masa de estiércol medida ni base de N",
        "B1": "Estiércol fresco teóricamente depositado; el agua se excluye de esta masa de actividad",
        "B2": "Masa equivalente: agua de lavado + boñiga; no es masa de estiércol medida ni base de N",
    }
    return pd.DataFrame(
        {
            "Etapa del sistema": stage_codes + ": " + stage_names,
            "Masa gestionada (kg eq/año)": flows[
                "Masa equivalente total (kg eq/año)"
            ],
            "Significado físico": stage_codes.map(meanings),
        }
    )


def add_dataframe(
    document: Document,
    profile,
    counters: EditorialCounters,
    description: str,
    dataframe: pd.DataFrame,
    *,
    decimals: int = 4,
) -> int:
    counters.table += 1
    caption_start = len(document.paragraphs)
    add_master_caption(document, f"Tabla {counters.table}. {description}")
    for paragraph in document.paragraphs[caption_start:]:
        paragraph.paragraph_format.keep_with_next = True
    table = document.add_table(rows=1, cols=len(dataframe.columns))
    for column_index, column in enumerate(dataframe.columns):
        table.rows[0].cells[column_index].text = clean_academic_label(column)
    for _, row in dataframe.iterrows():
        cells = table.add_row().cells
        for column_index, value in enumerate(row):
            cells[column_index].text = display_value(value, decimals)
    for row_index, row in enumerate(table.rows):
        tr_properties = row._tr.get_or_add_trPr()
        cant_split = OxmlElement("w:cantSplit")
        tr_properties.append(cant_split)
        if row_index == 0:
            table_header = OxmlElement("w:tblHeader")
            table_header.set(qn("w:val"), "true")
            tr_properties.append(table_header)
    format_table_like_master(table, profile)
    return counters.table


def add_figure(
    document: Document,
    counters: EditorialCounters,
    file_name: str | Path,
    description: str,
) -> int:
    image = Path(file_name)
    if not image.is_absolute():
        image = FIG_DIR / image
    if not image.exists():
        raise FileNotFoundError(f"No existe la figura requerida: {image.relative_to(ROOT)}")
    counters.figure += 1
    caption_start = len(document.paragraphs)
    add_master_caption(document, f"Figura {counters.figure}. {description}")
    for caption_paragraph in document.paragraphs[caption_start:]:
        caption_paragraph.paragraph_format.keep_with_next = True
    paragraph = document.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run().add_picture(str(image), width=Inches(6.0))
    return counters.figure


def add_equation(
    document: Document,
    counters: EditorialCounters,
    equation_latex: str,
    definition: str | None = None,
) -> int:
    counters.equation += 1
    if definition:
        document.add_paragraph(clean_academic_label(definition), style="Normal")
    add_word_equation(document, equation_latex, number=counters.equation)
    return counters.equation


def generate_system_boundary_figure() -> None:
    """Reconstruye las fronteras vigentes de ambos escenarios desde código."""

    def box(axis, x, y, width, height, text, *, facecolor="#EAF2F8", fontsize=8.5):
        patch = FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle="round,pad=0.015,rounding_size=0.012",
            linewidth=1.0,
            edgecolor="#1F3A4D",
            facecolor=facecolor,
        )
        axis.add_patch(patch)
        axis.text(x + width / 2, y + height / 2, text, ha="center", va="center", fontsize=fontsize)
        return patch

    def arrow(axis, start, end, *, text=None, text_offset=(0.0, 0.0), style="-"):
        axis.add_patch(
            FancyArrowPatch(
                start,
                end,
                arrowstyle="-|>",
                mutation_scale=12,
                linewidth=1.2,
                linestyle=style,
                color="#263238",
                shrinkA=2,
                shrinkB=2,
            )
        )
        if text:
            axis.text(
                (start[0] + end[0]) / 2 + text_offset[0],
                (start[1] + end[1]) / 2 + text_offset[1],
                text,
                ha="center",
                va="center",
                fontsize=7.5,
                color="#263238",
            )

    def prepare_axis(axis, title):
        axis.set_xlim(0, 1)
        axis.set_ylim(0, 1)
        axis.axis("off")
        axis.add_patch(Rectangle((0.025, 0.07), 0.95, 0.84, fill=False, linewidth=1.4, edgecolor="#2E75B6"))
        axis.text(0.5, 0.955, title, ha="center", va="top", fontsize=11, fontweight="bold")
        axis.text(0.965, 0.925, "Frontera del sistema", ha="right", va="bottom", fontsize=7.5, color="#2E75B6")

    fig, axes = plt.subplots(2, 1, figsize=(10, 9.2))

    ax = axes[0]
    prepare_axis(ax, "Escenario A: ruta sólida y ruta de aguas verdes")
    box(ax, 0.36, 0.76, 0.28, 0.09, "Flujo común de estiércol fresco\n26 278,7 kg/año", facecolor="#F3F6F8")
    ax.text(0.50, 0.69, "Separación física durante la limpieza", ha="center", va="center", fontsize=7.5, fontstyle="italic")
    box(ax, 0.11, 0.49, 0.25, 0.10, "A1: Precomposteo")
    box(ax, 0.11, 0.21, 0.25, 0.10, "A2: Lombricompostaje")
    box(ax, 0.64, 0.49, 0.25, 0.10, "A3: Almacenamiento\nde aguas verdes")
    box(ax, 0.64, 0.21, 0.25, 0.10, "A4: Aplicación de aguas verdes\nen campos de pastoreo")
    arrow(ax, (0.46, 0.76), (0.235, 0.59), text="Fracción paleada\n17 525,1 kg/año", text_offset=(-0.06, 0.035))
    arrow(ax, (0.54, 0.76), (0.765, 0.59), text="Fracción remanente\n8 753,6 kg/año", text_offset=(0.06, 0.035))
    arrow(ax, (0.235, 0.49), (0.235, 0.31))
    arrow(ax, (0.765, 0.49), (0.765, 0.31))
    arrow(ax, (0.97, 0.54), (0.89, 0.54), text="Agua de lavado", text_offset=(0.0, 0.045))
    arrow(ax, (0.11, 0.525), (0.055, 0.40), text="Drenaje a suelo agrícola\no matorral", text_offset=(0.035, -0.01), style="--")
    ax.text(0.90, 0.64, "Electricidad", ha="center", va="center", fontsize=7.5)
    arrow(ax, (0.88, 0.62), (0.85, 0.59))
    ax.text(0.765, 0.14, "Diésel", ha="center", va="center", fontsize=7.5)
    arrow(ax, (0.765, 0.16), (0.765, 0.21))
    ax.text(0.235, 0.13, "Lombricompost", ha="center", va="center", fontsize=7.5)
    arrow(ax, (0.235, 0.21), (0.235, 0.16))
    arrow(ax, (0.36, 0.54), (0.45, 0.54), text="Emisiones", text_offset=(0.0, 0.035), style="--")
    arrow(ax, (0.36, 0.26), (0.45, 0.26), text="Emisiones", text_offset=(0.0, 0.035), style="--")
    arrow(ax, (0.64, 0.54), (0.55, 0.54), text="Emisiones", text_offset=(0.0, 0.035), style="--")
    arrow(ax, (0.64, 0.26), (0.55, 0.26), text="Emisiones", text_offset=(0.0, 0.035), style="--")

    ax = axes[1]
    prepare_axis(ax, "Escenario B: almacenamiento y aplicación de purines")
    box(ax, 0.08, 0.54, 0.25, 0.12, "Flujo común de estiércol fresco\n26 278,7 kg/año", facecolor="#F3F6F8")
    box(ax, 0.40, 0.54, 0.22, 0.12, "B1: Almacenamiento\nde purines")
    box(ax, 0.70, 0.54, 0.24, 0.12, "B2: Aplicación de purines\nen campo de pastoreo")
    arrow(ax, (0.33, 0.60), (0.40, 0.60))
    arrow(ax, (0.62, 0.60), (0.70, 0.60))
    arrow(ax, (0.51, 0.80), (0.51, 0.66), text="Agua de lavado", text_offset=(0.09, 0.0))
    ax.text(0.46, 0.43, "Electricidad", ha="center", va="center", fontsize=7.5)
    arrow(ax, (0.46, 0.46), (0.46, 0.54))
    ax.text(0.77, 0.43, "Diésel", ha="center", va="center", fontsize=7.5)
    arrow(ax, (0.77, 0.46), (0.77, 0.54))
    ax.text(0.50, 0.22, "Se cuantifican emisiones de manejo y consumos operativos dentro de la frontera.", ha="center", va="center", fontsize=8)
    arrow(ax, (0.57, 0.54), (0.57, 0.31), text="Emisiones", text_offset=(0.065, 0.0), style="--")
    arrow(ax, (0.88, 0.54), (0.88, 0.31), text="Emisiones", text_offset=(0.065, 0.0), style="--")

    fig.subplots_adjust(left=0.03, right=0.97, top=0.98, bottom=0.03, hspace=0.10)
    INTEGRAL_FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(SYSTEM_BOUNDARY_PNG, dpi=300, bbox_inches="tight", metadata={"Date": None})
    fig.savefig(SYSTEM_BOUNDARY_SVG, bbox_inches="tight", metadata={"Date": None})
    plt.close(fig)
    svg_lines = SYSTEM_BOUNDARY_SVG.read_text(encoding="utf-8").splitlines()
    SYSTEM_BOUNDARY_SVG.write_text(
        "\n".join(line.rstrip() for line in svg_lines) + "\n",
        encoding="utf-8",
    )


def read_reference_registry() -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    for line in REFERENCES.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 6 or cells[0] in {"Clave", "---"} or set(cells[0]) == {"-"}:
            continue
        entries.append(
            {
                "key": cells[0],
                "reference": cells[1].replace("*", "").replace("`", ""),
                "section": cells[2],
                "purpose": cells[3],
                "status": cells[4],
                "notes": cells[5],
            }
        )
    keys = [entry["key"] for entry in entries]
    duplicates = sorted(key for key, count in Counter(keys).items() if count > 1)
    if duplicates:
        raise RuntimeError(f"Hay claves bibliográficas duplicadas en el registro: {duplicates}")
    found = set(keys)
    missing = sorted(REQUIRED_REFERENCE_KEYS - found)
    if missing:
        raise RuntimeError(f"Faltan referencias requeridas en el registro: {missing}")
    missing_candidates = sorted(INTERNAL_CANDIDATE_REFERENCE_KEYS - found)
    if missing_candidates:
        raise RuntimeError(f"Faltan referencias candidatas gobernadas en el registro: {missing_candidates}")
    unclassified = sorted(found - REQUIRED_REFERENCE_KEYS - INTERNAL_CANDIDATE_REFERENCE_KEYS)
    if unclassified:
        raise RuntimeError(
            "Hay referencias sin clasificación visible/candidata en el registro: "
            f"{unclassified}"
        )
    return entries


def visible_reference_entries(entries: list[dict[str, str]]) -> list[dict[str, str]]:
    """Devuelve únicamente las referencias con una cita vigente en el integral."""

    visible = [entry for entry in entries if entry["key"] in REQUIRED_REFERENCE_KEYS]
    visible_keys = {entry["key"] for entry in visible}
    if visible_keys != REQUIRED_REFERENCE_KEYS:
        missing = sorted(REQUIRED_REFERENCE_KEYS - visible_keys)
        extra = sorted(visible_keys - REQUIRED_REFERENCE_KEYS)
        raise RuntimeError(
            f"La selección de bibliografía visible no coincide con las citas gobernadas; "
            f"faltan={missing}, sobran={extra}"
        )
    return visible


def conclusion_items() -> list[dict[str, str]]:
    totals = conclusions_source.impact_totals()
    percentages = conclusions_source.comparisons(totals)
    reference_flow, normalized = conclusions_source.processed_indicators(totals)
    collected, remainder = conclusions_source.flow_inventory(reference_flow)
    stages = conclusions_source.stage_totals()
    conclusions_source.validate_stage_sums(stages, totals)
    return conclusions_source.build_conclusions(
        totals,
        normalized,
        percentages,
        stages,
        reference_flow,
        collected,
        remainder,
    )


def sensitivity_summary() -> tuple[pd.DataFrame, float]:
    source = pd.read_csv(SENSITIVITY, encoding="utf-8-sig")
    table = pd.DataFrame(
        {
            "Factor de N₂-N respecto al TAN": source["emep_n2_factor_fraction_tan"],
            "N₂-N estimado (kg)": source["n2_n_kg"],
            "N total remanente (kg)": source["n_total_out_kg"],
            "Cambio respecto al caso central (% del N de entrada)": source[
                "change_vs_central_pct_n_total_in"
            ],
        }
    )
    maximum = float(source["change_vs_central_pct_n_total_in"].abs().max())
    return table, maximum


def committee_from_master(master: Document) -> list[tuple[str, str]]:
    director = master_text(master, 10)
    director_role = master_text(master, 11)
    members_line = master_text(master, 16)
    parts = [part.strip() for part in members_line.split("\t") if part.strip()]
    if len(parts) != 3 or "Miembro, Comité Asesor" not in members_line:
        raise RuntimeError("La estructura del comité asesor cambió en el MASTER.")
    first_member = parts[0]
    second_member = parts[1].removesuffix(" Miembro, Comité Asesor").strip()
    member_role = parts[2]
    committee = [
        (director, director_role),
        (first_member, member_role),
        (second_member, "Miembro, Comité Asesor"),
    ]
    if any(not name or "Comité Asesor" not in role for name, role in committee):
        raise RuntimeError("No fue posible extraer el comité asesor completo del MASTER.")
    return committee


def add_title_page(document: Document, profile, master: Document) -> None:
    centered = document.styles.add_style("Portada centrada", WD_STYLE_TYPE.PARAGRAPH)
    centered.base_style = document.styles["Normal"]
    centered.font.name = profile.font_name
    centered.font.size = Pt(profile.body_size_pt)
    centered.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    centered.paragraph_format.left_indent = Pt(0)
    centered.paragraph_format.first_line_indent = Pt(0)
    centered.paragraph_format.space_after = Pt(8)

    title_style = document.styles.add_style("Título integral", WD_STYLE_TYPE.PARAGRAPH)
    title_style.base_style = centered
    title_style.font.name = profile.font_name
    title_style.font.size = Pt(profile.title_size_pt)
    title_style.font.italic = True
    title_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_style.paragraph_format.space_before = Pt(24)
    title_style.paragraph_format.space_after = Pt(24)

    title_lines = [
        "Universidad de Costa Rica",
        "Escuela de Ingeniería de Biosistemas",
        "Trabajo Final de Graduación",
    ]
    title_paragraphs = []
    for line in title_lines:
        paragraph = document.add_paragraph(style="Portada centrada")
        paragraph.add_run(line).bold = True
        title_paragraphs.append(paragraph)
    title_paragraph = document.add_paragraph(
        "Análisis de ciclo de vida de los desechos bovinos, sólidos y líquidos "
        "producidos en una lechería especializada en Turrialba, Costa Rica",
        style="Título integral",
    )
    author = document.add_paragraph(style="Portada centrada")
    author.add_run("Mateo Cerdas Barboza\nCarné B71946")
    author.paragraph_format.space_after = Pt(18)
    for name, role in committee_from_master(master):
        committee_paragraph = document.add_paragraph(style="Portada centrada")
        committee_paragraph.add_run(name).bold = True
        committee_paragraph.add_run(f"\n{role}")
        committee_paragraph.paragraph_format.space_after = Pt(8)
    status = document.add_paragraph(style="Portada centrada")
    run = status.add_run(PROVISIONAL_LABEL)
    run.bold = True
    status.paragraph_format.space_before = Pt(18)
    note = document.add_paragraph(style="Portada centrada")
    note.add_run(
        "Documento integral de trabajo para revisión académica. La jornada M3 permanece pendiente."
    ).italic = True
    date = document.add_paragraph(style="Portada centrada")
    date.add_run("Turrialba, Costa Rica\nSeptiembre de 2026")

    # Espaciado estructural de los bloques de portada. La cadena keep-with-next
    # conserva el conjunto en una página sin párrafos vacíos ni saltos internos.
    for paragraph in title_paragraphs[:2]:
        paragraph.paragraph_format.space_after = Pt(4)
    title_paragraphs[-1].paragraph_format.space_after = Pt(24)
    title_paragraph.paragraph_format.space_before = Pt(20)
    title_paragraph.paragraph_format.space_after = Pt(30)
    author.paragraph_format.space_before = Pt(8)
    author.paragraph_format.space_after = Pt(24)
    for committee_paragraph in document.paragraphs[-6:-3]:
        committee_paragraph.paragraph_format.space_after = Pt(12)
    status.paragraph_format.space_before = Pt(44)
    status.paragraph_format.space_after = Pt(8)
    note.paragraph_format.space_before = Pt(8)
    note.paragraph_format.space_after = Pt(44)
    date.paragraph_format.space_before = Pt(20)
    for paragraph in document.paragraphs:
        paragraph.paragraph_format.keep_with_next = paragraph is not date


def add_preliminaries(document: Document):
    document.add_page_break()
    document.add_heading("Estado del documento", level=1)
    add_text(
        document,
        [
            "Este trabajo final de graduación (TFG) integra la propuesta académica original con la metodología ejecutada y los productos regenerables de la corrida vigente. Los resultados, la discusión y las conclusiones corresponden a la integración PROVISIONAL M1–M2. La incorporación de M3 actualizará la caracterización y puede modificar las magnitudes, comparaciones e interpretaciones presentadas.",
            "El documento maestro aprobado se conserva como fuente protegida de continuidad académica y formato. La presente versión establece una ruta editorial única hacia el TFG final sin alterar ese documento original.",
        ],
    )
    document.add_heading("Contenido", level=1)
    for heading in EXPECTED_HEADINGS:
        document.add_paragraph(heading, style="Normal")
    marker = document.add_paragraph("__LISTA_SIGLAS__")
    marker.paragraph_format.page_break_before = True
    return marker


def populate_acronym_list(document: Document, marker) -> list[str]:
    body_text = all_document_text(document).replace("__LISTA_SIGLAS__", "")
    entries = used_acronyms(body_text)
    marker.text = "Lista de siglas y abreviaturas"
    marker.style = document.styles["Heading 1"]
    anchor = marker._p
    for entry in entries:
        paragraph = document.add_paragraph(style="Normal")
        paragraph.paragraph_format.left_indent = Inches(0.35)
        paragraph.paragraph_format.first_line_indent = Inches(-0.35)
        paragraph.add_run(entry.code).bold = True
        paragraph.add_run(f" — {entry.list_definition}")
        anchor.addnext(paragraph._p)
        anchor = paragraph._p
    return [entry.code for entry in entries]


def build_document() -> tuple[int, int, int, int]:
    master = Document(str(MASTER))
    document = Document()
    profile = apply_master_format(document, MASTER)
    counters = EditorialCounters()
    methodology_context = methodology_source.methodology_context()
    result_context = results_source.results_context()
    resource_context = operational_resource_context()
    reference_registry = read_reference_registry()
    references = visible_reference_entries(reference_registry)

    for section in document.sections:
        header = section.header.paragraphs[0]
        header.text = PROVISIONAL_LABEL
        header.alignment = WD_ALIGN_PARAGRAPH.CENTER

    add_title_page(document, profile, master)
    acronym_marker = add_preliminaries(document)

    add_chapter(document, "1. Introducción")
    document.add_heading("1.1 Justificación", level=2)
    add_master_paragraphs(document, master, range(28, 37))
    add_text(
        document,
        [
            "Las cifras contextuales y referencias heredadas de la propuesta se conservan en esta versión para mantener continuidad académica; su cotejo bibliográfico final se encuentra identificado en el registro integral de referencias.",
        ],
    )
    document.add_heading("1.2 Delimitación del problema", level=2)
    add_master_paragraphs(document, master, [39, 40])
    add_text(
        document,
        [
            "El estudio aplicó el análisis de ciclo de vida (ACV) a dos alternativas del manejo de estiércol en la lechería: el Escenario A, que integra la ruta sólida de precomposteo y lombricompostaje con la ruta de aguas verdes, y el Escenario B, que representa el almacenamiento y la aplicación directa de purines. La evaluación abarcó cambio climático, eutrofización terrestre y eutrofización marina. En esta etapa documental, la evidencia disponible integra M1 y M2 y mantiene pendiente M3.",
        ],
    )

    add_chapter(document, "2. Marco teórico y antecedentes")
    inherited_theoretical_blocks = [
        ("2.1 Generación de excreta bovina", range(50, 55)),
        ("2.2 Métodos para el manejo de la excreta bovina", []),
        ("2.2.1 Lombricompostaje", [58]),
        ("2.2.2 Enmienda agrícola", [61]),
        ("2.3 Análisis de ciclo de vida e impacto ambiental", range(64, 72)),
    ]
    for title, indexes in inherited_theoretical_blocks:
        document.add_heading(title, level=2 if title.count(".") == 1 else 3)
        if indexes:
            add_master_paragraphs(document, master, indexes)

    document.add_heading("2.4 Modelado de emisiones del manejo del estiércol", level=2)
    add_text(
        document,
        [
            "En este TFG se distinguen tres niveles que no deben confundirse. El inventario reúne datos de actividad, como masas de material, contenido de sólidos volátiles, N total, nitrógeno amoniacal total, electricidad y diésel. El modelado de emisiones relaciona esos datos con factores y aproximaciones metodológicas para estimar flujos elementales hacia el aire, el agua o el suelo. La evaluación de impactos se realiza después, al caracterizar los flujos elementales obtenidos. Por tanto, un factor de emisión no es una medición directa de la finca y un factor de caracterización no genera por sí mismo una emisión.",
        ],
    )
    document.add_heading("2.4.1 Directrices para inventarios de gases de efecto invernadero", level=3)
    add_text(
        document,
        [
            "El Refinamiento de 2019 de las Directrices de 2006 del Grupo Intergubernamental de Expertos sobre el Cambio Climático (IPCC, por sus siglas en inglés) se adoptó porque actualiza el marco internacional para inventarios de gases de efecto invernadero y contiene métodos aplicables al manejo de estiércol y a las entradas orgánicas en suelos gestionados (IPCC, 2019). En las etapas de manejo A1, A2, A3 y B1, este marco permite estimar CH₄ y N₂O directo; en A4 y B2 permite representar el N₂O directo del suelo y las rutas indirectas asociadas con volatilización y con lixiviación o escorrentía. Estas estimaciones forman parte del inventario de emisiones y anteceden a la evaluación de impactos.",
            "Para CH₄, B₀ expresa la capacidad máxima de producción de metano de los sólidos volátiles; el factor de conversión de metano (MCF, por sus siglas en inglés) representa la fracción de ese potencial que se alcanza bajo el sistema de manejo y las condiciones climáticas consideradas; y la fracción asignada al sistema de manejo de desechos animales (AWMS, por sus siglas en inglés) representa la parte de la corriente ya asignada que se maneja mediante el sistema correspondiente. La masa manejada y su fracción de sólidos volátiles son datos de actividad, mientras que B₀, MCF y AWMS cumplen una función metodológica. Estos factores no constituyen mediciones directas de la lechería.",
            "Para las rutas de N, EF₃ relaciona el N que ingresa al sistema de manejo con el N₂O-N directo; EF₁ cumple la función equivalente para entradas orgánicas al suelo; EF₄ transforma en N₂O-N indirecto la deposición derivada de las pérdidas explícitas de NH₃-N y NOx-N; y EF₅ se aplica al N perdido por lixiviación o escorrentía. FracLEACH representa la fracción de N que sigue la ruta hídrica una vez que el N ha llegado al suelo. Las fracciones específicas de drenaje del manejo se mantienen separadas de esta última ruta. Así, los factores describen fenómenos y bases de actividad diferentes y se aplican únicamente en las etapas donde la ruta física está representada.",
        ],
    )
    document.add_heading("2.4.2 Emisiones de N reactivo y guía europea de inventarios atmosféricos", level=3)
    add_text(
        document,
        [
            "El marco del IPCC se complementó con la Guía de inventarios de emisiones atmosféricas 2023 del Programa cooperativo de seguimiento y evaluación del transporte a larga distancia de contaminantes atmosféricos en Europa (EMEP) y la Agencia Europea de Medio Ambiente (EEA, por sus siglas en inglés) para representar rutas de N reactivo que el modelo vigente calcula de forma explícita (European Environment Agency, 2023). Esta guía conjunta no sustituye al IPCC: aporta factores de NH₃-N, NO-N o NOx-N y N₂-N, además de la mineralización previa del N orgánico en el almacenamiento líquido, mientras el IPCC conserva las rutas de CH₄, N₂O directo e indirecto y las pérdidas hídricas que le corresponden.",
            "El nitrógeno amoniacal total constituye la base de actividad para las pérdidas atmosféricas de almacenamiento y manejo cuando así lo establece EMEP/EEA. La volatilización de NH₃ puede comenzar desde la excreción y continuar durante el almacenamiento y tratamiento del estiércol; una vez emitido, el NH₃ participa en procesos de transporte y deposición atmosférica (Asman et al., 1998; Monteny y Erisman, 1998). En A1 se utilizan relaciones para almacenamiento sólido; en A3 y B1 se representan el almacenamiento líquido y la mineralización previa; y en A4 y B2 se distinguen los factores propios de aplicación al suelo. Las masas explícitas de NH₃-N y NOx-N alimentan después la ruta indirecta de N₂O del IPCC mediante EF₄. El N₂ se conserva como pérdida física del balance de N, pero no recibe caracterización ambiental en las categorías evaluadas.",
            "A2 constituye una excepción acotada. Komakech et al. (2016) aporta la aproximación experimental adoptada para estimar NH₃ a partir de la masa húmeda de residuo que ingresa a la etapa. Esta relación no sustituye las aproximaciones EMEP/EEA utilizadas para NO y N₂, no se extiende a otras rutas o etapas y no reinicializa las reservas propagadas de N total y nitrógeno amoniacal total.",
        ],
    )
    document.add_heading("2.5 Evaluación de impactos y factores nacionales", level=2)
    document.add_heading("2.5.1 Método de Huella Ambiental 3.1", level=3)
    add_text(
        document,
        [
            "El método de Huella Ambiental 3.1 (EF 3.1, por sus siglas en inglés) pertenece a la fase de Evaluación del Impacto del Ciclo de Vida. Su función es aplicar factores de caracterización que relacionan la masa de cada flujo elemental, su compartimento ambiental y una categoría de impacto con un indicador común (Andreasi Bassi et al., 2023). En este TFG se utilizan únicamente cambio climático, eutrofización terrestre y eutrofización marina, expresadas respectivamente en kg CO₂-eq, mol N-eq y kg N-eq. El potencial de calentamiento global (PCG) mencionado en los antecedentes corresponde al indicador climático utilizado por los estudios allí resumidos.",
            "La secuencia conceptual es flujo elemental por factor de caracterización igual a contribución a la categoría de impacto. Emitir una masa de CH₄, N₂O, NH₃, NOx o NO₃⁻ pertenece al inventario modelado; convertirla en una contribución potencial a cambio climático o eutrofización pertenece a la caracterización. EF 3.1 no estima ni genera las emisiones. La implementación productiva y reproducible de esta relación se realiza en Python a partir de la identidad del flujo, el compartimento y la categoría.",
        ],
    )
    document.add_heading("2.5.2 Factores oficiales nacionales para recursos operativos", level=3)
    add_text(
        document,
        [
            "Los factores oficiales del Instituto Meteorológico Nacional permiten representar los consumos energéticos con información nacional pertinente para Costa Rica (IMN, 2026). Su función depende del recurso. Para la electricidad se utiliza un factor agregado de consumo que entrega directamente una contribución de cambio climático y no se vuelve a caracterizar con EF 3.1. Para el diésel se emplean factores físicos de combustión que convierten el volumen consumido en masas de CO₂ fósil, CH₄ fósil y N₂O; estas emisiones elementales sí se caracterizan posteriormente con EF 3.1. La separación evita recaracterizar la electricidad o mezclar factores nacionales de inventario con factores de evaluación de impacto.",
        ],
    )
    document.add_heading("2.6 Antecedentes", level=2)
    add_master_paragraphs(document, master, range(79, 88))

    add_chapter(document, "3. Objetivos")
    document.add_heading("3.1 Objetivo general", level=2)
    document.add_paragraph(master_text(master, 91), style="Normal")
    document.add_heading("3.2 Objetivos específicos", level=2)
    document.add_paragraph(master_text(master, 93), style="Normal")
    document.add_paragraph(master_text(master, 94), style="Normal")

    add_chapter(document, "4. Metodología")
    document.add_heading("4.1 Enfoque metodológico y sitio de estudio", level=2)
    add_text(
        document,
        [
            "El estudio se desarrolló como un Análisis de Ciclo de Vida aplicado al manejo del estiércol bovino en una lechería especializada de Turrialba, Costa Rica. Comprendió la definición de meta y alcance, la construcción del Inventario de Ciclo de Vida, la estimación de emisiones por etapa y la conversión de esas emisiones a indicadores de impacto ambiental.",
        ],
    )
    add_master_paragraphs(document, master, range(100, 103))
    add_text(
        document,
        [
            "La descripción del sitio y de sus operaciones conserva la formulación de la propuesta cuando continúa siendo compatible con el trabajo ejecutado. Los parámetros operativos cuantitativos se actualizaron con la evidencia de la misma lechería reportada por Sánchez-Romero y Brenes-Gamboa (2026).",
            "En la operación habitual del Escenario A, el estiércol recogido con pala se conduce a A1: Precomposteo y después a A2: Lombricompostaje. El remanente del piso se incorpora al agua de lavado y las aguas verdes llegan mediante el drenaje o canal a la tanqueta para su almacenamiento en A3. La tanqueta se vacía aproximadamente cada tres días y el tractor acciona el cañón VAIA para la aplicación en A4. La tanqueta almacena; el cañón aplica.",
        ],
    )
    document.add_heading("4.2 Meta, alcance, unidad funcional y escenarios", level=2)
    add_text(
        document,
        [
            "La meta fue comparar el desempeño ambiental de dos alternativas de manejo bajo una misma unidad funcional de 1 kg de estiércol fresco manejado. Los flujos y emisiones anuales describen la escala operacional; los indicadores por kilogramo corresponden a la normalización respecto a la unidad funcional.",
            f"El flujo anual común fue {results_source.fmt(methodology_context['flujo_referencia'], 6)} kg de estiércol fresco/año. En el Escenario A, la fracción sólida ingresó a A1: Precomposteo y continuó hacia A2: Lombricompostaje; el remanente se incorporó a A3: Almacenamiento de aguas verdes y A4: Aplicación de aguas verdes en campos de pastoreo. En el Escenario B, el flujo completo ingresó a B1: Almacenamiento de purines y continuó hacia B2: Aplicación de purines en campo de pastoreo.",
            "El Escenario B no fue la operación habitual permanente ni una alternativa puramente hipotética. Para materializarlo temporalmente se suspendió la desviación normal del sólido hacia precomposteo y lombricompostaje, el estiércol paleado se dirigió a la tanqueta y el remanente del piso se incorporó mediante lavado. Los purines resultantes fueron acumulados, observados y muestreados físicamente. Los escenarios A y B se materializaron en momentos distintos con la misma tanqueta y no implicaron la coexistencia de ambos contenidos. B1 representa el almacenamiento y B2 la aplicación con el mismo conjunto tractor–cañón utilizado para A4.",
            "A1 duró aproximadamente entre 21 días y cerca de un mes, por lo que se representa como tres a cuatro semanas sin tratar 28 días como una medición exacta. A2 comenzó después de A1, cuando el material precompostado ingresó a las camas, y su operación regular duró aproximadamente 13 semanas. Vargas Sarmiento (2023, sección 5.2.2.1, p. 14; sección 6.1.3, p. 25) documentó en el mismo lombricario 13 semanas desde la siembra de las lombrices y para procesar toda la boñiga. Estas duraciones son contextuales y no escalan factores. El presente TFG no muestreó lombricompost terminado; las muestras correspondieron a material precompostado previo a A2.",
        ],
    )
    generate_system_boundary_figure()
    boundary_figure = counters.figure + 1
    add_text(
        document,
        [
            f"La Figura {boundary_figure} reconstruye los diagramas conceptuales de la propuesta con la nomenclatura y las conexiones vigentes. En el Escenario A, la fracción paleada y la fracción remanente siguen rutas físicamente separadas; en el Escenario B, el flujo común completo continúa por almacenamiento y aplicación. Los consumos de electricidad y diésel se asignan a las etapas operativas correspondientes.",
        ],
    )
    boundary_figure = add_figure(
        document,
        counters,
        SYSTEM_BOUNDARY_PNG,
        "Fronteras y conexiones físicas de los escenarios evaluados.",
    )
    stage_table = methodology_source.stage_summary().drop(
        columns=["Modelo de estimación"], errors="ignore"
    )
    table_1 = counters.table + 1
    add_text(
        document,
        [
            f"La Tabla {table_1} presenta la jerarquía de etapas utilizada en todo el documento integral. En los gráficos por etapa se emplean las claves A1–A4 y B1–B2 definidas en esta tabla.",
        ],
    )
    table_1 = add_dataframe(
        document,
        profile,
        counters,
        "Etapas oficiales de los escenarios evaluados.",
        stage_table,
        decimals=2,
    )

    document.add_heading("4.3 Diseño experimental, muestreo y análisis de laboratorio", level=2)
    document.add_heading("4.3.1 Campañas y procedencia física de las muestras", level=3)
    add_text(
        document,
        [
            "La caracterización primaria vigente procede exclusivamente de las campañas M1 y M2. La evidencia sitúa actividades de campo de M1 el 10 de noviembre de 2025; el informe de los Laboratorios de Servicios Analíticos de la Escuela de Química (LASA) identifica esa fecha para el muestreo de estiércol fresco y el 11 de noviembre para su recepción. Los informes del laboratorio agronómico consignan fechas de recepción específicas por material, que no se interpretaron automáticamente como fechas de muestreo. Para M2, la evidencia documental sitúa la preparación de campo el 20 de julio de 2026, las actividades de Bioenergía el 21 de julio y la recepción en LASA el 23 de julio. Estas referencias identifican la cronología documental disponible y no se generalizan a todos los materiales ni se intercambian con las fechas de análisis o emisión de los informes.",
            "Se distinguieron submuestra, muestra compuesta y réplica analítica. Cada muestra compuesta sólida reunió aproximadamente 500 g a partir de cinco submuestras de cerca de 100 g. El estiércol fresco se tomó en cinco puntos aleatorios de la sala de espera donde permanecían las vacas antes del ordeño. El estiércol precompostado se tomó en cinco puntos aleatorios de la pila con mayor tiempo de permanencia, cuyo material estaba listo para alimentar las lombrices. Por tanto, esta segunda muestra representa la salida de A1 y la entrada a A2, no una muestra de lombricompost terminado.",
            "Las aguas verdes y los purines se muestrearon en campañas separadas y en condiciones operativas distintas, aunque se utilizó la misma tanqueta. Antes de la toma, el contenido se removió manualmente desde el fondo durante aproximadamente 2 min con un rastrillo. Luego se reunieron cinco alícuotas consecutivas de cerca de 100 mL, tomadas con un vaso de laboratorio desde una misma abertura, hasta obtener aproximadamente 500 mL. Las dos aberturas de la tanqueta estaban muy próximas; el procedimiento no se interpreta como un muestreo espacial de zonas distantes.",
            "Antes de cada muestreo líquido, la tanqueta se vació el jueves por la tarde y recibió entradas continuas hasta el lunes por la mañana; durante ese intervalo de acumulación previo al muestreo ocurrieron dos lavados de la sala de espera. La muestra representó una acumulación operacional dinámica y no una carga estática aislada. Esta condición específica de campaña se mantuvo separada de la frecuencia operativa anual, representada por el vaciado aproximado cada tres días.",
            "En M1 se obtuvieron, para cada sólido, dos muestras compuestas destinadas a Bioenergía y otras dos muestras compuestas físicamente independientes destinadas al laboratorio externo: LASA para estiércol fresco y el Laboratorio de Suelos y Foliares del Centro de Investigaciones Agronómicas (CIA) para precompostado. En M2 se obtuvieron tres muestras compuestas por sólido; de cada una se tomaron tres réplicas para Bioenergía y el material remanente de esas mismas muestras se remitió a LASA o CIA. En M1 se recolectaron además dos muestras compuestas de cada líquido y en M2, tres. El Apéndice D presenta el diseño ejecutado sin reproducir las observaciones ni las réplicas crudas.",
        ],
    )

    document.add_heading("4.3.2 Preparación, conservación y transporte", level=3)
    add_text(
        document,
        [
            "Las muestras se colocaron en recipientes de polipropileno para alimentos con capacidad aproximada de 750–900 mL, se etiquetaron y se transportaron desde Turrialba hasta la Universidad de Costa Rica en San Pedro dentro de una hielera con hielo. En M2, la identidad física compartida entre Bioenergía y los laboratorios externos se conservó tomando primero las porciones requeridas para la gravimetría y remitiendo después el material remanente de cada muestra compuesta.",
        ],
    )

    document.add_heading("4.3.3 Determinaciones en Bioenergía", level=3)
    add_text(
        document,
        [
            "Bioenergía determinó humedad, materia seca, cenizas y sólidos volátiles en estiércol fresco y precompostado, con tres réplicas analíticas por muestra compuesta. Para humedad y materia seca se colocaron aproximadamente 10 g de muestra fresca por réplica en recipientes previamente pesados. Se registraron las masas del recipiente vacío y con muestra mediante balanza analítica; las porciones se secaron en estufa a 105 °C durante 16 h, se enfriaron en desecador y se pesaron nuevamente. Este TFG adoptó esas condiciones experimentales, también empleadas por Jjagwe et al. (2019) para determinar sólidos totales en estiércol bovino.",
            "Para cenizas y sólidos volátiles se tomó aproximadamente 1 g de la muestra seca, se trató en mufla a 575 °C durante 4 h, se enfrió en desecador y se efectuó la pesada posterior. El TFG adoptó este procedimiento con respaldo en el protocolo de Leitner et al. (2020), sin atribuirle el carácter de norma universal. El registro operativo contemporáneo de M1 consigna además una ventana de operación de seis horas cuya composición no está desglosada. Para el tratamiento se adoptó la confirmación consolidada del ejecutor de cuatro horas a 575 °C; la ventana total se conserva como discrepancia documental y no se reinterpretó como exposición continua a la temperatura objetivo. Las cenizas correspondieron a la fracción mineral remanente y los sólidos volátiles a la fracción de la materia seca perdida durante la calcinación.",
            "El procedimiento documenta funcionalmente una estufa de secado, una mufla, balanzas, crisoles y desecadores. No se consignan fabricante, modelo, placa o número de serie porque esa identificación no está confirmada. La ausencia de esos datos instrumentales no altera los tiempos, temperaturas, masas aproximadas ni secuencia de pesada documentados.",
        ],
    )

    document.add_heading("4.3.4 Determinaciones en LASA y CIA", level=3)
    add_text(
        document,
        [
            "LASA determinó el N total del estiércol fresco mediante Kjeldahl. El procedimiento utilizó entre 0,2 g y 0,3 g de muestra homogénea por triplicado, digestión con mezcla catalítica, destilación por arrastre de vapor hacia una solución receptora y valoración con ácido sulfúrico 0,0500 mol/L. Los resultados se expresaron como porcentaje en masa del material presentado al laboratorio.",
            "En M1, el CIA determinó por separado N–NH₄, N–NO₃ y N ureico en aguas verdes y purines. Estas especies se conservaron para trazabilidad y no se sumaron para reconstruir N total. En M2, el CIA determinó N total de ambos líquidos mediante digestión húmeda de 10 g con ácido sulfúrico por Kjeldahl, aforo a 250 mL y determinación colorimétrica mediante análisis por inyección en flujo. Los decimales internos almacenados se conservaron para el cálculo, sin atribuirles una precisión analítica formal mayor que la reportada por el laboratorio.",
            "Para el precompostado, el CIA secó el material a 80 °C durante 48 h, lo molió, lo cribó a 1 mm y pesó aproximadamente 80–100 mg para determinar N y C por combustión seca de Dumas en un autoanalizador Elementar Vario Macro Cube. Este acondicionamiento no fue una determinación de humedad y no sustituyó la gravimetría independiente de Bioenergía a 105 °C durante 16 h.",
            "El porcentaje integrado de N del precompostado se conservó en la base preparada por el CIA. Únicamente para construir la referencia experimental en base húmeda de A2 se combinó con la materia seca gravimétrica de Bioenergía. Esa referencia se utilizó como contraste: A2 recibió productivamente el N total y el nitrógeno amoniacal total propagados desde A1. El carbono y la relación C/N permanecieron como caracterización descriptiva, sin conversión a base húmeda ni consumo en el ACV.",
        ],
    )

    document.add_heading("4.3.5 Integración M1–M2 y relación con el modelo", level=3)
    add_text(
        document,
        [
            "La jerarquía estadística fue réplica analítica, muestra compuesta, promedio de campaña e integración entre campañas. Primero se resumieron las réplicas dentro de cada muestra compuesta y las muestras dentro de cada campaña; después se integraron los promedios de las campañas elegibles. Las réplicas analíticas no se trataron como observaciones temporales independientes y M1 y M2 recibieron igual peso, aunque M2 contuviera más muestras y réplicas.",
            "Para los sólidos metodológicamente comparables, la integración provisional combinó M1 y M2 mediante la media de sus promedios de campaña. Cuando una variable no fue compatible, no se forzó la combinación: en líquidos, M1 correspondió a especiación y se mantuvo como trazabilidad, mientras que el N total provisional procedió solo de M2 mediante Kjeldahl. No se aplicaron pruebas inferenciales.",
            "La transformación de estiércol fresco a precompostado se calculó primero por campaña a partir de la materia seca y las cenizas de ambos materiales. Después se integraron las razones de M1 y M2 con igual peso temporal y la diferencia de masa se derivó de esa razón integrada; no se construyó a partir de un promedio global previo de las cuatro mediciones.",
            "La secuencia experimental fue muestra, determinación, resultado analítico, resumen de campaña, integración M1–M2, parámetro experimental y consumo por una etapa o ecuación. La materia seca y los sólidos volátiles del estiércol fresco alimentaron las estimaciones de CH₄ de A1, A3 y B1; las variables equivalentes del precompostado alimentaron A2. La materia seca y las cenizas de ambos sólidos construyeron la transformación A1→A2. El N del estiércol fresco inicializó el N total en A1, A3 y B1, mientras que el N del precompostado y de los líquidos se conservó como contraste sin reinicializar las cadenas propagadas.",
            "La corrida permanece identificada como PROVISIONAL M1–M2. M3 está pendiente y no interviene en los datos, parámetros, ecuaciones o resultados presentados en esta versión.",
        ],
    )
    table_2 = counters.table + 1
    add_text(
        document,
        [
            f"La Tabla {table_2} sintetiza la relación entre el punto de muestreo, las determinaciones, el laboratorio y la función metodológica, sin duplicar la matriz general por etapa ni trasladar al cuerpo las réplicas crudas.",
        ],
    )
    table_2 = add_dataframe(
        document,
        profile,
        counters,
        "Procedencia experimental, determinaciones y función metodológica de los materiales analizados.",
        experimental_body_table(),
        decimals=3,
    )

    document.add_heading("4.4 Fuentes y levantamiento del inventario", level=2)
    add_text(
        document,
        [
            "El Inventario de Ciclo de Vida se levantó mediante seis componentes complementarios: caracterización experimental; observaciones y registros operativos de la finca; datos previamente publicados cuando fueron necesarios; factores metodológicos oficiales o de literatura; supuestos explícitos; y cálculos, integraciones y transformaciones reproducibles dentro del flujo de trabajo.",
            "La procedencia y el tratamiento se registraron por separado. Según la taxonomía adoptada para este TFG, se clasificó como primaria la información obtenida específicamente mediante muestreo, medición, observación o registro directo. Los análisis de CIA y LASA conservaron esta condición cuando correspondieron a muestras del estudio, aunque se ejecutaran como servicio analítico externo. Los datos preexistentes, la literatura y los factores del IPCC, del Programa cooperativo de seguimiento y evaluación del transporte a larga distancia de contaminantes atmosféricos en Europa (EMEP) y la Agencia Europea de Medio Ambiente (EEA, por sus siglas en inglés), del IMN y de Environmental Footprint 3.1 se clasificaron como secundarios con subtipos que identifican su función.",
            "La categoría terciaria se reservó para materiales de compilación o localización y no se asignó a ninguna entrada cuantitativa activa. Medido, observado, publicado, supuesto, calculado, integrado, propagado, factor metodológico y factor de caracterización describen el tratamiento del dato; no alteran por sí mismos su procedencia.",
        ],
    )
    provenance_table = counters.table + 1
    add_text(
        document,
        [
            f"La Tabla {provenance_table} resume seis macrofamilias de datos y su uso. El Apéndice B, Matriz detallada de procedencia de los datos del inventario, conserva las 15 familias, etapas, subtipos, fuentes concretas y tratamientos necesarios para la trazabilidad fina.",
        ],
    )
    provenance_table = add_dataframe(
        document,
        profile,
        counters,
        "Procedencia y tratamiento de las familias de datos del inventario.",
        methodology_source.provenance_summary(),
        decimals=2,
    )

    methodology_trace_table = counters.table + 1
    add_text(
        document,
        [
            f"La Tabla {methodology_trace_table} sintetiza la secuencia metodológica de cada etapa A1–B2. El Apéndice C, Matriz detallada de trazabilidad metodológica por etapa A1–B2, relaciona cada fenómeno con su ecuación vigente, dato de actividad, factor, procedencia, fuente y uso posterior.",
            "Esta vista conserva separadas la generación del inventario y la caracterización de impactos: una emisión elemental o un consumo se obtiene primero y, cuando corresponde, se vincula después con el factor de Environmental Footprint 3.1. La electricidad mantiene el resultado agregado del Instituto Meteorológico Nacional y no se presenta como un flujo elemental caracterizado.",
        ],
    )
    methodology_trace_table = add_dataframe(
        document,
        profile,
        counters,
        "Síntesis de la trazabilidad metodológica por etapa A1–B2.",
        methodology_source.methodological_summary(),
        decimals=2,
    )

    document.add_heading("4.5 Construcción de masas y bases experimentales", level=2)
    add_text(
        document,
        [
            "Las masas anuales de las seis etapas se construyeron a partir del estiércol fresco recolectado, la fracción recolectada respecto del depósito teórico en la sala de ordeño, el balance de la fracción remanente y el volumen anual de agua de lavado. El primer conjunto de relaciones define las masas de estiércol que ingresan a A1, A3 y B1; todas se expresan en kg/año.",
        ],
    )
    add_equation(
        document,
        counters,
        r"m_{\mathrm{A1}}=m_{\mathrm{recolectado}};\quad m_{\mathrm{B1}}=m_{\mathrm{depositado}}=\frac{m_{\mathrm{recolectado}}}{f_{\mathrm{recolectada}}};\quad m_{\mathrm{A3}}=m_{\mathrm{depositado}}-m_{\mathrm{recolectado}}",
        "En estas relaciones, m_A1 es la masa recolectada, f_recolectada es la fracción del depósito teórico recuperada por paleado, m_B1 es la masa total teóricamente depositada y m_A3 es la masa remanente arrastrable.",
    )
    add_equation(
        document,
        counters,
        r"m_{\mathrm{eq,A4}}=m_{\mathrm{A3}}+V_{\mathrm{agua}}\left(1\ \frac{\mathrm{kg}}{\mathrm{L}}\right);\quad m_{\mathrm{eq,B2}}=m_{\mathrm{B1}}+V_{\mathrm{agua}}\left(1\ \frac{\mathrm{kg}}{\mathrm{L}}\right)",
        "Las masas equivalentes de A4 y B2 expresan la mezcla física o dilución del estiércol con el agua de lavado. No crean N, no reinicializan N total ni nitrógeno amoniacal total (TAN, por sus siglas en inglés) y no constituyen la base de las ecuaciones nitrogenadas del suelo, que reciben las reservas propagadas desde A3 y B1.",
    )
    add_equation(
        document,
        counters,
        r"R_j=\frac{f_{\mathrm{MS,fresco},j}\,f_{\mathrm{cenizas,fresco},j}}{f_{\mathrm{MS,precompostado},j}\,f_{\mathrm{cenizas,precompostado},j}};\quad \overline R=\frac{1}{n}\sum_{j=1}^{n}R_j;\quad \widehat m_{\mathrm{A2}}=m_{\mathrm{A1}}\,\overline R",
        "La transformación húmeda A1→A2 se calculó primero en cada jornada elegible mediante R_j y luego se integró con igual peso temporal. Las fracciones de materia seca (MS) se expresan respecto de la masa húmeda y las fracciones de cenizas respecto de la materia seca; el acento circunflejo identifica que la masa húmeda de A2 fue inferida, no pesada a la salida de A1.",
    )
    add_equation(
        document,
        counters,
        r"f_{\mathrm{SV,húmeda}}=\left(\frac{SV_{\mathrm{base\ seca}}}{100}\right)\left(\frac{MS}{100}\right)",
        "Antes de estimar CH₄, el porcentaje de sólidos volátiles (SV) en base seca se convirtió a fracción de SV en base húmeda mediante la materia seca gravimétrica de la etapa.",
    )
    add_equation(
        document,
        counters,
        r"N_{\mathrm{total,entrada}}=m_{\mathrm{fresca}}\,f_{\mathrm{N,húmeda}}",
        "En las fronteras frescas A1, A3 y B1, N_total,entrada se obtuvo multiplicando la masa fresca de estiércol —sin sumar el agua de lavado— por su fracción húmeda de N. Las mediciones intermedias se conservaron como referencias experimentales y no reinicializaron el balance.",
    )

    document.add_heading("4.6 Balance secuencial de nitrógeno y estimación de emisiones", level=2)
    add_text(
        document,
        [
            "El N total constituyó el balance físico principal y el nitrógeno amoniacal total (TAN, por sus siglas en inglés) una reserva subordinada sujeta a 0 ≤ TAN ≤ N total. El TAN se inicializó como 0,60 del N total únicamente en las fronteras de estiércol fresco y ambos componentes se propagaron entre etapas físicamente conectadas.",
            "En particular, A2 recibió el N total y el TAN remanentes de A1. La medición de N del precompostado se mantuvo como referencia de contraste experimental y no reinicializó estos flujos productivos.",
            "Las pérdidas explícitas de NH₃-N, NOx-N y N₂-N definidas por la guía conjunta del Programa cooperativo de seguimiento y evaluación del transporte a larga distancia de contaminantes atmosféricos en Europa (EMEP) y la Agencia Europea de Medio Ambiente (EEA, por sus siglas en inglés) redujeron el TAN y el N total. El N₂O-N directo y las pérdidas hídricas definidas por IPCC redujeron el N total una sola vez. El N₂O indirecto por volatilización se calculó con las especies explícitas NH₃-N y NOx-N; el NO₃⁻ se originó únicamente en rutas hídricas justificadas.",
            "El balance se aplicó de forma secuencial: A2 recibió el N total y la reserva residual de TAN a la salida de A1. Por ello, aplicar factores en ambas etapas no duplicó matemáticamente las reservas originales. FracGasMS permaneció exclusivamente como referencia de contraste y no generó otra volatilización ni alimentó EF4. Las duraciones específicas introducen incertidumbre de representatividad temporal y de transferencia de las aproximaciones, pero no justifican escalado lineal de los factores.",
            "A2: Lombricompostaje se representó mediante una arquitectura híbrida explícita y trazable: la categoría IPCC de compostaje en hileras pasivas se utilizó como aproximación para CH₄ y N₂O directo; Komakech et al. (2016), como aproximación experimental aprobada para NH₃; y EMEP/EEA de almacenamiento sólido, como aproximación metodológica aprobada provisionalmente para NO y N₂. La fracción de pérdida de N por lixiviación se estableció en cero para las condiciones operativas modeladas, sin cambiar el factor genérico de la categoría ni afirmar imposibilidad física universal. Las ecuaciones siguientes documentan el núcleo necesario para reproducir la lógica vigente.",
        ],
    )
    document.add_heading("4.6.1 Metano de las etapas de manejo", level=3)
    add_equation(
        document,
        counters,
        r"m_{\mathrm{CH_4}} = m_{\mathrm{manejada}} \times VS_{\mathrm{húmeda}} \times B_0 \times \rho_{\mathrm{CH_4}} \times \left(\frac{MCF}{100}\right) \times AWMS",
        "En la ecuación, m_CH₄ es la emisión de metano de la etapa; m_manejada es la masa húmeda manejada; VS_húmeda es la fracción de sólidos volátiles (SV) en base húmeda; B₀ es la capacidad máxima de producción de metano; ρ_CH₄ es el factor IPCC de conversión de volumen a masa, 0,67 kg CH₄/m³; MCF es el factor de conversión de metano (MCF, por sus siglas en inglés) y AWMS representa la fracción asignada al sistema de manejo de desechos animales (AWMS, por sus siglas en inglés).",
    )
    document.add_heading("4.6.2 Balance secuencial de N total y TAN", level=3)
    add_equation(
        document,
        counters,
        r"TAN_{\mathrm{fresco}} = 0{,}60 \times N_{\mathrm{total,fresco}}",
        "TAN_fresco es el nitrógeno amoniacal total en la frontera fresca y N_total,fresco es el nitrógeno total del estiércol fresco.",
    )
    add_equation(
        document,
        counters,
        r"N_{\mathrm{mineralizado}}=\left(N_{\mathrm{total,entrada}}-TAN_{\mathrm{entrada}}\right)f_{\mathrm{min}};\quad TAN_{\mathrm{disponible}}=TAN_{\mathrm{entrada}}+N_{\mathrm{mineralizado}}",
        "En A3 y B1, la mineralización se calculó sobre el N orgánico, definido como la diferencia entre N total y TAN de entrada, antes de estimar en paralelo las pérdidas EMEP/EEA sobre el TAN disponible.",
    )
    add_equation(
        document,
        counters,
        r"N_j = TAN_{\mathrm{disponible}} \times f_j,\quad j \in \{\mathrm{NH_3-N},\,\mathrm{NO-N},\,\mathrm{N_2-N}\}",
        "La expresión resume las rutas parametrizadas con factores EMEP/EEA. En A2, la masa de NH₃ se estima una sola vez con la aproximación experimental aprobada de Komakech et al. (2016), aplicada a la masa húmeda inferida de residuo orgánico que ingresa a la etapa, mientras NO-N y N₂-N conservan las aproximaciones para sólidos de EMEP/EEA aprobadas provisionalmente.",
    )
    add_equation(
        document,
        counters,
        r"TAN_{\mathrm{salida}}=TAN_{\mathrm{disponible}}-N_{\mathrm{NH_3}}-N_{\mathrm{NO_x}}-N_{\mathrm{N_2}}",
        "El cierre de TAN descuenta conjuntamente las tres pérdidas calculadas en paralelo sobre la misma reserva disponible; la ecuación no representa una secuencia ficticia de bases decrecientes.",
    )
    add_equation(
        document,
        counters,
        r"m_{\mathrm{NH_3,A2}}=\left(\frac{\widehat m_{\mathrm{A2}}}{1000\ \mathrm{kg/Mg}}\right)\left(12{,}8\ \frac{\mathrm{g\ NH_3}}{\mathrm{Mg}}\right)\left(\frac{1\ \mathrm{kg}}{1000\ \mathrm{g}}\right);\quad N_{\mathrm{NH_3,A2}}=m_{\mathrm{NH_3,A2}}\frac{14}{17}",
        "Como excepción exclusiva de A2, Komakech et al. (2016) aporta 12,8 g NH₃ por Mg de entrada húmeda; la masa de NH₃ se convierte después a NH₃-N mediante 14/17. Esta relación no reinicializa N total ni TAN, y NO-N y N₂-N continúan calculándose con EMEP/EEA.",
    )
    add_equation(
        document,
        counters,
        r"N_{\mathrm{N_2O-N,directo}} = N_{\mathrm{total,entrada}} \times EF_3",
        "El N₂O-N directo de las etapas de manejo se estimó con EF₃ sobre el N total de entrada.",
    )
    add_equation(
        document,
        counters,
        r"m_{\mathrm{N_2O,directo}} = N_{\mathrm{N_2O-N,directo}} \times \frac{44}{28}",
        "La masa de N₂O-N directo se convirtió a masa molecular de N₂O mediante la razón 44/28.",
    )
    add_equation(
        document,
        counters,
        r"N_{\mathrm{total,salida}} = N_{\mathrm{total,entrada}} - N_{\mathrm{NH_3}} - N_{\mathrm{NO_x}} - N_{\mathrm{N_2}} - N_{\mathrm{N_2O-N,directo}} - N_{\mathrm{pérdida,hídrica}}",
        "Esta identidad expresa el cierre secuencial de N total en las etapas de manejo; cada pérdida física se descuenta una sola vez.",
    )
    add_equation(
        document,
        counters,
        r"N_{\mathrm{precursor,vol}} = N_{\mathrm{NH_3}} + N_{\mathrm{NO_x}}",
        "Las especies explícitas NH₃-N y NOx-N se sumaron para definir el precursor volatilizado que alimenta EF₄; FracGasMS permaneció solo como referencia de contraste.",
    )
    add_equation(
        document,
        counters,
        r"m_{\mathrm{N_2O,ind,vol}} = N_{\mathrm{precursor,vol}} \times EF_4 \times \frac{44}{28}",
        "El N₂O indirecto por volatilización se obtuvo aplicando EF₄ al N precursor y convirtiendo N₂O-N a N₂O.",
    )
    document.add_heading("4.6.3 Rutas de N hacia el suelo y aplicación", level=3)
    add_text(
        document,
        [
            "A4 y B2 recibieron el N total y el TAN propagados desde sus etapas de almacenamiento. La volatilización de NH₃ se estimó sobre el TAN aplicado; el NOx, expresado como NO₂, se estimó sobre el N aplicado y se convirtió a masa de N. El N₂O directo y la lixiviación o escorrentía conservaron como base el N de estiércol aplicado.",
        ],
    )
    add_equation(
        document,
        counters,
        r"N_{\mathrm{drenaje,A1}} = N_{\mathrm{total,A1}} \times FracLeachMS_{\mathrm{A1}}",
        "El drenaje de A1 se trata como entrada de N al suelo y no como una masa de NO₃⁻ directa.",
    )
    add_equation(
        document,
        counters,
        r"N_{\mathrm{NH_3,aplic}} = TAN_{\mathrm{aplicado}} \times f_{\mathrm{NH_3}};\quad N_{\mathrm{NO_x,aplic}} = \left(N_{\mathrm{aplicado}} \times f_{\mathrm{NO_2}}\right) \times \frac{14}{46}",
        "En las aplicaciones al suelo, NH₃-N se estimó sobre el TAN propagado, mientras NOx-N se obtuvo sobre el N aplicado y se convirtió desde NO₂ mediante 14/46.",
    )
    add_equation(document, counters, r"m_{\mathrm{N_2O,directo,suelo}} = N_{\mathrm{aplicado}} \times EF_1 \times \frac{44}{28}", "El N₂O directo del suelo se estimó con EF₁ sobre el N propagado y aplicado, no sobre la masa equivalente de la mezcla.")
    add_equation(document, counters, r"N_{\mathrm{lix,esc}} = N_{\mathrm{entrada,suelo}} \times FracLEACH_{\mathrm{suelo}}", "El N lixiviado o escurrido se estimó únicamente en las rutas hídricas justificadas a partir del N que ingresa al suelo.")
    add_equation(document, counters, r"m_{\mathrm{NO_3^-}} = N_{\mathrm{lix,esc}} \times \frac{62}{14}", "La masa de N lixiviado o escurrido se expresó como NO₃⁻ mediante la razón estequiométrica 62/14.")
    add_equation(document, counters, r"m_{\mathrm{N_2O,ind,lix}} = N_{\mathrm{lix,esc}} \times EF_5 \times \frac{44}{28}", "El N₂O indirecto de la ruta hídrica se calculó con EF₅ y la conversión de N₂O-N a N₂O.")

    document.add_heading("4.7 Recursos operativos y evaluación de impactos", level=2)
    add_text(
        document,
        [
            "El método de Huella Ambiental 3.1 (EF 3.1, por sus siglas en inglés), desarrollado por la Comisión Europea y su Centro Común de Investigación (JRC, por sus siglas en inglés), se aplicó a las emisiones directas. El cambio climático se expresó en kg CO₂-eq, la eutrofización terrestre en mol N-eq y la eutrofización marina en kg N-eq; las categorías se interpretaron por separado.",
            "La electricidad de la bomba se evaluó con el factor agregado de consumo del IMN para 2025 como aproximación temporal del patrón observado en 2026. La combustión de diésel se representó mediante masas físicas de CO₂ fósil, CH₄ fósil y N₂O obtenidas con factores IMN y caracterizadas con EF 3.1. No se incorporaron cadenas completas de fondo.",
            "Los factores, la asignación de sistemas y los consumos operativos corresponden a las decisiones metodológicas vigentes. Esta integración documental no recalculó ni modificó el ACV.",
            "En A3/B1, el MCF de 38 % se mantuvo como aproximación conservadora del IPCC de la categoría tabulada de un mes para clima tropical húmedo. No corresponde a una medición específica del MCF para la residencia operativa de tres días y no se escaló como 38 % × 3/30. La mineralización EMEP del 10 % tampoco se escaló por tres días. El tiempo físico de operación, el intervalo específico de preparación de las muestras y la duración tabulada de la aproximación metodológica se trataron como conceptos distintos.",
            "El B₀ de 0,24 m³ CH₄/kg SV se mantuvo como valor por defecto del IPCC para ganado lechero de alta productividad en otras regiones. La evidencia histórica del mismo Módulo Lechero publicada por Conejo-Morales y WingChing-Jones (2020) respalda esa clasificación, pero no constituye una medición local de B₀ ni demuestra la productividad actual de 2026. El valor por defecto de baja productividad no sustituyó el valor central aprobado; la dependencia de B₀ respecto de la especie y la dieta permanece como incertidumbre paramétrica.",
        ],
    )
    add_equation(
        document,
        counters,
        r"E=\left(\frac{P_{\mathrm{mec}}}{\eta}\right)\left(\frac{365}{d_{\mathrm{ciclo}}}\right)n_{\mathrm{lavados}}\left(\frac{t_{\mathrm{lavado}}}{60}\right);\quad CC_{\mathrm{electricidad}}=E\,FE_{\mathrm{IMN,elec}}",
        "El consumo anual de electricidad E, en kWh/año, combina potencia mecánica, eficiencia, frecuencia y duración del lavado. Su contribución climática se obtiene con el factor agregado de consumo del IMN y no vuelve a caracterizarse como flujo elemental de EF 3.1.",
    )
    add_equation(
        document,
        counters,
        r"V_{\mathrm{diésel}}=\left(\frac{365}{d_{\mathrm{ciclo}}}\right)\left(\frac{t_{\mathrm{operación}}}{60}\right)q_{\mathrm{diésel}};\quad m_i=V_{\mathrm{diésel}}FE_{\mathrm{IMN},i}k_i,\quad k_i=1\ \mathrm{para\ kg/L},\ k_i=10^{-3}\ \mathrm{para\ g/L}",
        "El volumen anual de diésel V_diésel, en L/año, se obtiene de la frecuencia, duración y consumo horario. Los factores IMN producen masas físicas de CO₂ fósil, CH₄ fósil y N₂O; k_i hace explícita la conversión de g a kg cuando corresponde, y esas masas se caracterizan después con EF 3.1.",
    )
    add_equation(
        document,
        counters,
        r"I_c = \sum_i \left(m_i \times CF_{i,c}\right)",
        "I_c es el indicador de la categoría c, m_i es la masa del flujo elemental i y CF_i,c es su factor de caracterización en esa categoría.",
    )
    add_equation(document, counters, r"CC_{\mathrm{total}} = CC_{\mathrm{manejo}} + CC_{\mathrm{electricidad}} + CC_{\mathrm{diésel}}", "El cambio climático total suma una sola vez las contribuciones del manejo, la electricidad agregada y las emisiones físicas del diésel caracterizadas con EF 3.1.")
    factor_table = methodology_source.characterization_factors()
    table_3 = counters.table + 1
    figure_1 = counters.figure + 1
    add_text(
        document,
        [
            f"La Tabla {table_3} documenta los factores visibles principales y la Figura {figure_1} muestra la escala operacional de los flujos.",
        ],
    )
    table_3 = add_dataframe(
        document,
        profile,
        counters,
        "Factores de emisión IMN y caracterización EF 3.1.",
        factor_table,
        decimals=4,
    )
    figure_1 = add_figure(
        document,
        counters,
        "fig_04_flujos_masa_equivalente_total.png",
        "Masa equivalente total por etapa y escenario.",
    )

    document.add_heading("4.8 Verificación independiente de la caracterización", level=2)
    add_text(
        document,
        [
            "SimaPro es un programa informático especializado en análisis de ciclo de vida que permite trabajar con inventarios y métodos de evaluación de impacto. En este TFG su función se limita a una verificación independiente de la caracterización EF 3.1 implementada en Python. Python permanece como fuente productiva y reproducible del inventario, la estimación de emisiones, la caracterización, la agregación, la normalización y los resultados canónicos.",
            "La verificación se ha preparado mediante casos unitarios y cantidades elementales de la corrida PROVISIONAL M1–M2, pero su ejecución presencial en SimaPro permanece pendiente. No se reconstruirá el ACV completo ni los escenarios y etapas como procesos en ese programa; tampoco se incluirá la contribución eléctrica agregada del IMN como si fuera un flujo elemental. No se presentan resultados, concordancias ni discrepancias Python–SimaPro porque aún no existe evidencia de ejecución. La versión de SimaPro y la configuración exacta del método deberán registrarse cuando se realice la comprobación.",
        ],
    )

    document.add_heading("4.9 Supuestos, consistencia y limitaciones", level=2)
    add_text(
        document,
        [
            "Los supuestos dominantes incluyen la equivalencia entre litro de agua y kilogramo equivalente, la extrapolación anual de las operaciones, la generación teórica de estiércol durante la permanencia en sala, la conservación de cenizas, la asignación de sistemas de manejo y sus factores, la relación TAN/N inicial y la representación del almacenamiento líquido mediante un MCF de 38 %.",
            "La consistencia se controló mediante balances de masa y nitrógeno, normalización común, trazabilidad entre integración experimental y parámetros activos, sumas por etapa y escenario, y comprobaciones de dirección, signo, unidad, dominancia y redondeo de las comparaciones narrativas.",
            "Las limitaciones principales son la representatividad temporal de M1–M2, la ausencia de una medición directa del MCF para aproximadamente tres días de residencia y la incertidumbre documentada para los factores de conversión de metano de la guía IPCC (VanderZaag, 2018), la transferibilidad de Komakech, la representatividad de las categorías IPCC y del factor EMEP de N₂ en A2, la masa húmeda inferida de A2 y la ausencia de un balance cerrado de agua y sólidos. Son incertidumbres científicas de la arquitectura aprobada, no decisiones metodológicas abiertas ni impedimentos para el modelo pre-M3.",
        ],
    )

    add_chapter(document, "5. Resultados provisionales M1–M2")
    add_text(
        document,
        [
            "Todos los resultados de este capítulo corresponden a la corrida PROVISIONAL M1–M2. No constituyen una caracterización definitiva ni anticipan los resultados de M3.",
        ],
    )
    document.add_heading("5.1 Caracterización y flujos del inventario", level=2)
    characterization = results_source.characterization_summary()
    characterization_index = characterization.set_index("Tipo de muestra")
    fresh = characterization_index.loc["Estiércol fresco"]
    precomposted = characterization_index.loc["Estiércol precompostado"]
    add_text(
        document,
        [
            f"El estiércol fresco presentó {results_source.fmt(fresh['Humedad (%)'], 2)} % de humedad y {results_source.fmt(fresh['Materia seca (%)'], 2)} % de materia seca. El material precompostado presentó {results_source.fmt(precomposted['Humedad (%)'], 2)} % de humedad y {results_source.fmt(precomposted['Materia seca (%)'], 2)} % de materia seca.",
            "La distribución de flujos mantuvo el mismo flujo anual de referencia para ambos escenarios. La ruta A separó la fracción sólida recolectada de la fracción incorporada a las aguas verdes; la ruta B condujo el flujo completo al almacenamiento y posterior aplicación de purines.",
        ],
    )
    mass_table_number = counters.table + 1
    add_text(
        document,
        [
            f"La Tabla {mass_table_number} presenta la masa húmeda o equivalente gestionada en cada etapa. En A4 y B2, la masa equivalente integra el agua de lavado con la fracción de estiércol correspondiente; no constituye la base para inicializar N total.",
        ],
    )
    mass_table_number = add_dataframe(
        document,
        profile,
        counters,
        "Masas anuales gestionadas por etapa.",
        inventory_mass_table(),
        decimals=6,
    )
    figure_2 = counters.figure + 1
    add_text(document, [f"La Figura {figure_2} presenta la caracterización gravimétrica provisional."])
    figure_2 = add_figure(
        document,
        counters,
        "fig_01_caracterizacion_humedad_materia_seca.png",
        "Humedad y materia seca promedio por tipo de muestra.",
    )

    document.add_heading("5.2 Emisiones estimadas", level=2)
    emissions = results_source.emissions_summary()
    table_4 = counters.table + 1
    figure_3 = counters.figure + 1
    add_text(
        document,
        [
            f"La Tabla {table_4} resume las emisiones del manejo y la Figura {figure_3} muestra la distribución de CH₄. Las contribuciones operativas de electricidad y diésel se incorporaron en el indicador de cambio climático, manteniendo separada su trazabilidad. El Apéndice E presenta las rutas de N₂O directo e indirecto, NH₃, NOx y NO₃⁻ por etapa sin duplicar el inventario completo.",
            f"La combustión de {results_source.fmt(resource_context['diesel_l'], 2)} L/año de diésel produjo {results_source.fmt(resource_context['diesel_co2'], 6)} kg/año de CO₂ fósil, {results_source.fmt(resource_context['diesel_ch4'], 6)} kg/año de CH₄ fósil y {results_source.fmt(resource_context['diesel_n2o'], 6)} kg/año de N₂O en cada escenario. Estas masas se caracterizaron después con EF 3.1 y permanecen separadas de las emisiones del manejo resumidas en la Tabla {table_4}.",
        ],
    )
    table_4 = add_dataframe(
        document,
        profile,
        counters,
        "Emisiones anuales del manejo por escenario y sustancia.",
        emissions,
        decimals=4,
    )
    figure_3 = add_figure(
        document,
        counters,
        "fig_06_emisiones_ch4.png",
        "Emisiones anuales de CH₄ por etapa y escenario.",
    )

    document.add_heading("5.3 Impactos por etapa y por escenario", level=2)
    stage_impacts = results_source.impact_stage_summary()
    if {"Escenario", "Etapa", "Nombre de etapa"} <= set(stage_impacts.columns):
        stage_codes = stage_impacts["Escenario"].astype(str) + stage_impacts["Etapa"].astype(int).astype(str)
        stage_names = stage_impacts["Nombre de etapa"].astype(str).str.replace(
            r"^Etapa\s+\d+:\s*", "", regex=True
        )
        stage_impacts.insert(1, "Etapa del sistema", stage_codes + ": " + stage_names)
        stage_impacts = stage_impacts.drop(columns=["Etapa", "Nombre de etapa"])
    table_5 = counters.table + 1
    figure_4 = counters.figure + 1
    figure_5 = counters.figure + 2
    add_text(
        document,
        [
            f"La Tabla {table_5} presenta los impactos por etapa. En el Escenario A, {result_context['cg_dominant_a_name']} aportó {results_source.fmt(result_context['cg_dominant_a_percentage'], 2)} % del cambio climático; en el Escenario B, {result_context['cg_dominant_b_name']} aportó {results_source.fmt(result_context['cg_dominant_b_percentage'], 2)} %. Las Figuras {figure_4} y {figure_5} muestran la distribución por etapa de cambio climático y eutrofización terrestre.",
        ],
    )
    table_5 = add_dataframe(
        document,
        profile,
        counters,
        "Impactos ambientales por etapa.",
        stage_impacts,
        decimals=6,
    )
    figure_4 = add_figure(
        document,
        counters,
        "fig_11_impactos_cambio_climatico_etapa.png",
        "Cambio climático total por etapa y escenario.",
    )
    figure_5 = add_figure(
        document,
        counters,
        "fig_12_impactos_eutrofizacion_terrestre_etapa.png",
        "Eutrofización terrestre EF 3.1 por etapa y escenario.",
    )
    document.add_page_break()
    document.add_heading("5.3.1 Resultados totales y comparación entre escenarios", level=3)
    totals = results_source.total_impact_summary()
    table_6 = counters.table + 1
    table_resources = counters.table + 2
    table_7 = counters.table + 3
    table_8 = counters.table + 4
    figure_6 = counters.figure + 1
    add_text(
        document,
        [
            f"La Tabla {table_6} presenta la magnitud anual y la Tabla {table_resources} separa el cambio climático del manejo, la electricidad y el diésel. La Tabla {table_7} muestra los indicadores por unidad funcional. La Tabla {table_8} y la Figura {figure_6} presentan la comparación entre escenarios bajo la misma base funcional.",
        ],
    )
    table_6 = add_dataframe(
        document,
        profile,
        counters,
        "Impactos ambientales anuales por escenario.",
        totals.iloc[:, :4],
        decimals=6,
    )
    table_resources = add_dataframe(
        document,
        profile,
        counters,
        "Contribuciones al cambio climático del manejo y los recursos operativos.",
        climate_contribution_table(),
        decimals=6,
    )
    normalized_totals = totals[[totals.columns[0], *totals.columns[4:]]].copy()
    normalized_totals = normalized_totals.rename(
        columns={
            totals.columns[4]: "Cambio climático (kg CO₂-eq/kg)",
            totals.columns[5]: "Eutrofización terrestre (mol N-eq/kg)",
            totals.columns[6]: "Eutrofización marina (kg N-eq/kg)",
        }
    )
    table_7 = add_dataframe(
        document,
        profile,
        counters,
        "Impactos ambientales normalizados por kilogramo de estiércol fresco manejado.",
        normalized_totals,
        decimals=6,
    )
    comparisons = results_source.comparison_summary()
    table_8 = add_dataframe(
        document,
        profile,
        counters,
        "Comparación de impactos ambientales entre escenarios.",
        comparisons,
        decimals=4,
    )
    figure_6 = add_figure(
        document,
        counters,
        "fig_17_comparacion_diferencia_porcentual.png",
        "Diferencia porcentual del Escenario B respecto al Escenario A por categoría de impacto.",
    )

    document.add_heading("5.4 Contraste bibliográfico de A2", level=2)
    benchmark = results_source.a2_benchmark_summary()
    table_9 = counters.table + 1
    add_text(
        document,
        [
            f"La Tabla {table_9} contrasta las estimaciones oficiales de A2: Lombricompostaje con Jjagwe et al. (2019) sobre una base material armonizada. El contraste apoya la interpretación, pero no sustituye el inventario oficial ni constituye una validación formal del modelo.",
            "La fuente presenta una inconsistencia interna para N₂O: el resumen imprime 3,943 × 10⁻⁵ g/kg de materia seca, equivalentes matemáticamente a 0,03943 mg/kg, mientras la sección de resultados informa aproximadamente 40 mg/kg. La escala de la Figura 3 y el potencial de calentamiento global publicado de 324 kg CO₂-eq/t de residuo, calculado por los autores con factores de 1, 28 y 265 para CO₂, CH₄ y N₂O, respectivamente, son coherentes con el orden de decenas de miligramos. Conforme a la decisión metodológica vigente, el contraste conserva 39,43 mg/kg; esta selección documenta una inconsistencia editorial interna de la fuente y no modifica el inventario productivo de A2.",
        ],
    )
    table_9 = add_dataframe(
        document,
        profile,
        counters,
        "Contraste bibliográfico de A2 sobre materia seca de entrada.",
        benchmark,
        decimals=6,
    )

    add_chapter(document, "6. Discusión provisional")
    document.add_heading("6.1 Interpretación de la comparación", level=2)
    add_text(
        document,
        [
            f"Bajo la unidad funcional común, el {result_context['cg_comparison'].higher_label} presentó el mayor cambio climático y el {result_context['cg_comparison'].lower_label} el menor. La diferencia B menos A fue {results_source.fmt(result_context['cg_percentage'], 2)} % respecto al Escenario A.",
            f"En eutrofización terrestre, el {result_context['et_comparison'].higher_label} presentó el mayor indicador; en eutrofización marina, el {result_context['eu_comparison'].higher_label} presentó el mayor indicador. Estas comparaciones corresponden a categorías distintas y no se agregan entre sí.",
            "La concentración del impacto en etapas distintas confirma que la interpretación debe considerar la estructura de cada alternativa. El predominio climático de A3 y B1 coincide con la concentración de CH₄ en el almacenamiento líquido; el predominio de eutrofización marina de A4 y B2 coincide con las pérdidas de NO₃⁻ de la aplicación al suelo. Para eutrofización terrestre, las emisiones atmosféricas de NH₃ y NOx permiten interpretar la importancia relativa de A1 y B2 sin atribuir causalidad fuera de las relaciones de caracterización aplicadas.",
            f"Los dos escenarios incorporaron el mismo consumo anual de {results_source.fmt(resource_context['electricity_kwh'], 2)} kWh de electricidad y {results_source.fmt(resource_context['diesel_l'], 2)} L de diésel. Por ello, sus contribuciones operativas al cambio climático fueron iguales: {results_source.fmt(resource_context['electricity_climate'], 6)} kg CO₂-eq/año por electricidad y {results_source.fmt(resource_context['diesel_climate'], 6)} kg CO₂-eq/año por diésel. Estas cargas comunes no explican la diferencia entre escenarios, que se mantiene asociada con las emisiones del manejo dentro de la frontera estudiada.",
            "La evidencia provisional no permite generalizar una superioridad universal fuera de la lechería y de las condiciones modeladas.",
        ],
    )
    document.add_heading("6.2 Contraste con la literatura", level=2)
    add_text(
        document,
        [
            "El contraste con Jjagwe et al. (2019) mostró que las diferencias entre la estimación IPCC y la referencia experimental no siguieron una dirección uniforme para CH₄ y N₂O directo. Las diferencias de especie de lombriz, acondicionamiento, alimentación, humedad, duración, clima, escala y frecuencia de medición impiden interpretar esa comparación como equivalencia física entre sistemas.",
            "Las referencias de Komakech et al. (2016), Møller et al. (2004) y VanderZaag et al. (2013), junto con las directrices IPCC y EMEP/EEA, permiten trazar la selección y la interpretación de los factores empleados, pero no demuestran equivalencia física entre sus sistemas de origen y el sistema estudiado. En particular, el factor de NH₃ de Komakech procede de reactores pequeños en Kampala, con residuo predominantemente ganadero, concentraciones gaseosas medidas y un flujo de aire estimado mediante el índice respirométrico dinámico; su aplicación a la masa húmeda inferida de entrada a A2 es una aproximación experimental aprobada y una extrapolación con diferencias de escala, alimentación, clima, duración y operación. Estas limitaciones no convierten su selección en una decisión abierta para la fase pre-M3.",
        ],
    )
    document.add_heading("6.3 Sensibilidad y consistencia", level=2)
    sensitivity, maximum_change = sensitivity_summary()
    table_10 = counters.table + 1
    add_text(
        document,
        [
            f"La comprobación disponible para A2 varió el factor de N₂-N respecto al TAN entre 0 y 0,30. Frente al caso central de 0,30, el cambio máximo observado en el N total remanente equivalió a {results_source.fmt(maximum_change, 2)} % del N total de entrada. La Tabla {table_10} documenta esta comprobación de aseguramiento de la calidad; no constituye un análisis de sensibilidad completo de los impactos.",
            "Los supuestos con mayor capacidad material de afectar la comparación son el MCF del almacenamiento líquido, la caracterización de materia seca, sólidos volátiles y N después de M3, la relación TAN/N inicial, los factores de A2, la duración y frecuencia de los consumos operativos y los factores asociados a la aplicación al suelo.",
            "Después de M3 y antes de la interpretación final podrá evaluarse si una sensibilidad acotada de las aproximaciones de alta influencia, en particular N₂ de A2 y NH₃ de Komakech, aporta valor suficiente. Su ausencia no impide validar el modelo pre-M3. La consistencia continuará verificándose mediante cierre de balances, igualdad del flujo funcional e integridad temporal de la corrida.",
        ],
    )
    table_10 = add_dataframe(
        document,
        profile,
        counters,
        "Comprobación existente de sensibilidad del factor de N₂ en A2.",
        sensitivity,
        decimals=4,
    )

    add_chapter(document, "7. Conclusiones provisionales")
    add_text(
        document,
        [
            "Las siguientes conclusiones corresponden exclusivamente a la corrida PROVISIONAL M1–M2. M3 puede modificar las magnitudes, las etapas dominantes y la comparación; por tanto, estas conclusiones no representan el cierre experimental del TFG.",
        ],
    )
    conclusions = conclusion_items()
    for index, item in enumerate(conclusions, start=1):
        paragraph = document.add_paragraph(style="Normal")
        paragraph.add_run(f"Conclusión provisional {index}. ").bold = True
        paragraph.add_run(item["text"])

    add_chapter(document, "8. Recomendaciones")
    add_text(
        document,
        [
            "Incorporar M3 mediante la misma secuencia de ingestión, integración, ACV, tablas, figuras y documentos, y mantener la etiqueta provisional hasta completar las validaciones cruzadas.",
            "Priorizar, después de M3, una evaluación cuantitativa acotada del MCF del almacenamiento líquido y de los supuestos que controlan las etapas dominantes. Documentar como limitaciones los supuestos que no puedan resolverse con evidencia suficiente.",
            "Cotejar las referencias bibliográficas pendientes contra sus fuentes primarias y revisar institucionalmente la portada, los preliminares y la presentación final antes de generar el PDF de entrega.",
        ],
    )

    add_chapter(document, "9. Referencias")
    add_text(
        document,
        [
            "La bibliografía reúne únicamente las fuentes citadas en el documento y se consolida desde el registro integral versionado. La normalización editorial y la verificación de las entradas marcadas como pendientes deberán completarse antes de la versión final.",
        ],
    )
    for entry in references:
        paragraph = document.add_paragraph(entry["reference"], style="Normal")
        paragraph.paragraph_format.first_line_indent = Inches(-0.25)
        paragraph.paragraph_format.left_indent = Inches(0.25)

    add_chapter(
        document,
        "Apéndice A. Trazabilidad entre objetivos y evidencia provisional",
    )
    traceability = pd.DataFrame(
        [
            [
                "Objetivo general",
                "Metodología ACV, comparación bajo unidad funcional común y evaluación por etapa",
                "Impactos por etapa, totales y comparación provisional M1–M2",
                "Conclusión provisional 5",
            ],
            [
                "Objetivo específico 1",
                "Caracterización, flujos, balances y construcción del inventario",
                "Caracterización, flujos y emisiones provisionales",
                "Conclusión provisional 1",
            ],
            [
                "Objetivo específico 2",
                "Caracterización EF 3.1 y agregación por etapa y escenario",
                "Cambio climático y eutrofización por etapa, escenario y unidad funcional",
                "Conclusiones provisionales 2 a 4",
            ],
        ],
        columns=["Objetivo", "Respuesta metodológica", "Evidencia integrada", "Conclusión relacionada"],
    )
    table_11 = counters.table + 1
    add_text(
        document,
        [
            f"La Tabla {table_11} muestra cómo la metodología, los resultados y las conclusiones provisionales responden a los objetivos invariantes del estudio.",
        ],
    )
    table_11 = add_dataframe(
        document,
        profile,
        counters,
        "Trazabilidad entre objetivos y evidencia provisional.",
        traceability,
        decimals=2,
    )

    add_chapter(
        document,
        "Apéndice B. Matriz detallada de procedencia de los datos del inventario",
    )
    provenance_appendix_table = counters.table + 1
    add_text(
        document,
        [
            f"La Tabla {provenance_appendix_table} conserva la trazabilidad detallada por familia sin convertir los cálculos derivados en una nueva categoría de fuente.",
        ],
    )
    provenance_appendix_table = add_dataframe(
        document,
        profile,
        counters,
        "Matriz detallada de procedencia y tratamiento de los datos del inventario.",
        methodology_source.provenance_detail(),
        decimals=2,
    )

    add_chapter(
        document,
        "Apéndice C. Matriz detallada de trazabilidad metodológica por etapa A1–B2",
    )
    methodology_appendix_table = counters.table + 1
    add_text(
        document,
        [
            f"La Tabla {methodology_appendix_table} permite seguir cada etapa individualmente desde el proceso y el dato de actividad hasta la relación de cálculo, la fuente metodológica y la salida utilizada posteriormente. Las relaciones se recuperan de las fuentes responsables vigentes y no constituyen un modelo paralelo.",
        ],
    )
    methodology_appendix_table = add_dataframe(
        document,
        profile,
        counters,
        "Matriz detallada de trazabilidad metodológica por etapa A1–B2.",
        methodology_source.methodological_detail(),
        decimals=2,
    )

    add_chapter(
        document,
        "Apéndice D. Trazabilidad experimental de las campañas M1–M2",
    )
    campaign_appendix_table = counters.table + 1
    add_text(
        document,
        [
            f"La Tabla {campaign_appendix_table} documenta el diseño físico ejecutado en M1 y M2, la relación entre muestras compartidas o independientes y la condición de uso de cada determinación. La vista resume la evidencia necesaria para reproducir el diseño sin reemplazar los registros analíticos primarios.",
        ],
    )
    campaign_appendix_table = add_dataframe(
        document,
        profile,
        counters,
        "Diseño de muestreo y distribución analítica de las campañas M1–M2.",
        experimental_campaign_table(),
        decimals=2,
    )
    parameter_appendix_table = counters.table + 1
    add_text(
        document,
        [
            f"La Tabla {parameter_appendix_table} reúne los resultados experimentales intermedios necesarios para seguir la construcción de los parámetros del modelo. Los valores corresponden a la integración vigente y se presentan redondeados solo para lectura; los cálculos conservan la precisión interna de sus fuentes.",
        ],
    )
    parameter_appendix_table = add_dataframe(
        document,
        profile,
        counters,
        "Resultados experimentales esenciales y función en el modelo.",
        experimental_parameter_table(),
        decimals=4,
    )

    appendix_section = document.add_section(WD_SECTION.NEW_PAGE)
    portrait_width = appendix_section.page_width
    portrait_height = appendix_section.page_height
    appendix_section.orientation = WD_ORIENT.LANDSCAPE
    appendix_section.page_width = portrait_height
    appendix_section.page_height = portrait_width
    add_chapter(
        document,
        "Apéndice E. Balances intermedios y emisiones desagregadas",
        first=True,
    )
    nitrogen_appendix_table = counters.table + 1
    add_text(
        document,
        [
            "Las tres vistas de este apéndice se leen de manera secuencial y cumplen funciones distintas: primero se presenta la propagación contable en base N, después se detallan las pérdidas físicas también en base N y, por último, se muestran las emisiones expresadas como las especies moleculares utilizadas por el inventario.",
            f"La Tabla {nitrogen_appendix_table} permite seguir la propagación del N total y del TAN entre las etapas conectadas. En A4 y B2, la columna de transferencia presenta el N retornado al suelo según EMEP; el N residual después de las pérdidas directas se conserva por separado y no lo sustituye.",
        ],
    )
    nitrogen_appendix_table = add_dataframe(
        document,
        profile,
        counters,
        "Propagación anual de N total y TAN por etapa.",
        nitrogen_propagation_table(),
        decimals=6,
    )
    nitrogen_loss_table = counters.table + 1
    add_text(
        document,
        [
            f"La Tabla {nitrogen_loss_table} expresa sobre una base común de N las pérdidas directas que permiten conciliar el N de entrada con la transferencia o el remanente de cada etapa. El N₂ se conserva en el balance físico, aunque no recibe caracterización en las categorías evaluadas.",
        ],
    )
    nitrogen_loss_table = add_dataframe(
        document,
        profile,
        counters,
        "Pérdidas físicas anuales de N por etapa.",
        nitrogen_direct_loss_table(),
        decimals=6,
    )
    emissions_appendix_table = counters.table + 1
    add_text(
        document,
        [
            f"La Tabla {emissions_appendix_table} desagrega las emisiones que explican los impactos por etapa. Los valores proceden de la tabla canónica de emisiones; la vista no añade rutas ni recalcula factores.",
        ],
    )
    emissions_appendix_table = add_dataframe(
        document,
        profile,
        counters,
        "Emisiones anuales desagregadas por etapa y ruta.",
        detailed_emission_table(),
        decimals=6,
    )
    populate_acronym_list(document, acronym_marker)
    finalize_document_format(document, profile)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    document.save(OUT_DOCX)
    return counters.table, counters.figure, counters.equation, len(references)


def all_document_text(document: Document) -> str:
    paragraphs = [paragraph.text for paragraph in document.paragraphs]
    cells = [cell.text for table in document.tables for row in table.rows for cell in row.cells]
    return "\n".join(paragraphs + cells)


def body_elements(document: Document) -> list[dict[str, object]]:
    elements: list[dict[str, object]] = []
    for child in document.element.body.iterchildren():
        text = "".join(node.text or "" for node in child.iter(qn("w:t"))).strip()
        elements.append(
            {
                "tag": child.tag,
                "text": text,
                "image": any(True for _ in child.iter(qn("a:blip"))),
                "math": any(True for _ in child.iter(qn("m:oMath"))),
            }
        )
    return elements


def acronym_scope(document: Document) -> list[str]:
    """Texto académico visible, sin la lista ni las referencias bibliográficas."""
    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs]
    list_start = paragraphs.index("Lista de siglas y abreviaturas")
    body_start = next(
        index
        for index, value in enumerate(paragraphs[list_start + 1 :], start=list_start + 1)
        if value == "1. Introducción"
    )
    references_start = next(
        index
        for index, value in enumerate(paragraphs[body_start + 1 :], start=body_start + 1)
        if value == "9. Referencias"
    )
    visible = paragraphs[:list_start] + paragraphs[body_start:references_start]
    visible.extend(
        cell.text
        for table in document.tables
        for row in table.rows
        for cell in row.cells
    )
    return visible


def acronym_list_state(document: Document) -> tuple[list[str], list[str]]:
    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs]
    list_start = paragraphs.index("Lista de siglas y abreviaturas")
    body_start = next(
        index
        for index, value in enumerate(paragraphs[list_start + 1 :], start=list_start + 1)
        if value == "1. Introducción"
    )
    listed = [
        text.split(" — ", 1)[0]
        for text in paragraphs[list_start + 1 : body_start]
        if " — " in text
    ]
    return listed, acronym_scope(document)


def first_mentions_are_valid(scope: list[str]) -> bool:
    """Comprueba automáticamente cada entrada gobernada realmente utilizada."""
    scope_text = "\n".join(scope)
    for entry in ACRONYMS:
        if not acronym_is_used(scope_text, entry.code):
            continue
        first_paragraph = next(
            (value for value in scope if acronym_is_used(value, entry.code)),
            "",
        )
        if entry.spanish_name.casefold() not in first_paragraph.casefold():
            return False
        escaped_code = re.escape(entry.code)
        if entry.requires_english_notice:
            expected = rf"\({escaped_code}, por sus siglas en inglés(?:[;)])"
        else:
            expected = rf"\({escaped_code}\)"
        if not re.search(expected, first_paragraph):
            return False
        if not entry.requires_english_notice and re.search(
            rf"\({escaped_code}, por sus siglas en inglés",
            first_paragraph,
        ):
            return False
    return True


def validate_editorial_order(
    document: Document, tables: int, figures: int, equations: int
) -> bool:
    elements = body_elements(document)
    for label, count in (("Tabla", tables), ("Figura", figures)):
        for number in range(1, count + 1):
            pattern = re.compile(rf"\b{label}s?\b[^.!?]{{0,80}}\b{number}\b")
            caption_index = next(
                i
                for i, element in enumerate(elements)
                if str(element["text"]) == f"{label} {number}"
            )
            if not any(pattern.search(str(element["text"])) for element in elements[:caption_index]):
                return False
            if label == "Tabla":
                if not any(element["tag"] == qn("w:tbl") for element in elements[caption_index + 1 :]):
                    return False
            elif not any(bool(element["image"]) for element in elements[caption_index + 1 :]):
                return False

    equation_indexes = [i for i, element in enumerate(elements) if bool(element["math"])]
    if len(equation_indexes) != equations:
        return False
    for index in equation_indexes:
        previous = elements[index - 1] if index else {}
        if not str(previous.get("text", "")).strip() or bool(previous.get("math")):
            return False
    return True


def validate_document(
    master_hash_before: str,
    master_hash_after: str,
    expected_tables: int,
    expected_figures: int,
    expected_equations: int,
    expected_references: int,
) -> None:
    with zipfile.ZipFile(OUT_DOCX) as archive:
        bad_member = archive.testzip()
        if bad_member:
            raise RuntimeError(f"El DOCX contiene un miembro ZIP corrupto: {bad_member}")

    document = Document(str(OUT_DOCX))
    text = all_document_text(document)
    academic_text = text.split("9. Referencias", 1)[0]
    listed_acronyms, acronym_paragraphs = acronym_list_state(document)
    non_list_text = "\n".join(acronym_paragraphs)
    campaign_unit_corruptions = find_campaign_unit_corruptions(text)
    expected_acronyms = [entry.code for entry in used_acronyms(non_list_text)]
    first_mentions_ok = first_mentions_are_valid(acronym_paragraphs)
    unknown_acronyms = unregistered_acronym_candidates(acronym_paragraphs)
    omml_count = len(document.element.body.xpath(".//m:oMath"))
    equation_texts = [
        "".join(node.text or "" for node in paragraph._p.iter(qn("m:t")))
        for paragraph in document.paragraphs
        if paragraph._p.xpath(".//m:oMath")
    ]
    normalized_equations = [re.sub(r"\s+", "", value).casefold() for value in equation_texts]
    equation_corpus = "\n".join(normalized_equations)
    traceability = pd.read_csv(
        ROOT / "outputs" / "tablas_tesis" / "tabla_11_trazabilidad_metodologica_a1_b2.csv",
        encoding="utf-8-sig",
    )
    trace_ids = set(traceability["identificador_ecuacion"].astype(str))
    mass_source = (ROOT / "scripts" / "compute_masa_etapas_escenarios.py").read_text(encoding="utf-8")
    dry_source = (ROOT / "scripts" / "acv_masa_seca.py").read_text(encoding="utf-8")
    nitrogen_source = (ROOT / "scripts" / "reactive_n_ledger.py").read_text(encoding="utf-8")
    operational_source = (ROOT / "scripts" / "compute_operational_inventory.py").read_text(encoding="utf-8")
    imn_source = (ROOT / "scripts" / "imn_operational_factors.py").read_text(encoding="utf-8")
    boundary_svg = SYSTEM_BOUNDARY_SVG.read_text(encoding="utf-8")
    state_index = next(i for i, paragraph in enumerate(document.paragraphs) if paragraph.text == "Estado del documento")
    cover_manual_blanks = [
        paragraph
        for paragraph in document.paragraphs[:state_index]
        if not paragraph.text.strip() and not paragraph._p.xpath('.//w:br[@w:type="page"]')
    ]
    cover_paragraphs = document.paragraphs[:state_index]
    cover_page_breaks = [
        index
        for index, paragraph in enumerate(cover_paragraphs)
        if paragraph._p.xpath('.//w:br[@w:type="page"]')
    ]
    cover_nonempty = [paragraph for paragraph in cover_paragraphs if paragraph.text.strip()]
    cover_spacing_pt = sum(
        (paragraph.paragraph_format.space_before.pt if paragraph.paragraph_format.space_before else 0)
        + (paragraph.paragraph_format.space_after.pt if paragraph.paragraph_format.space_after else 0)
        for paragraph in cover_nonempty
    )
    grammar_regressions = (
        "el referencia",
        "el mismo secuencia",
        "El balance secuencial fue secuencial",
        "el reserva",
        "los reservas",
        "el aproximación",
        "del aproximación",
        "un aproximación",
    )
    paragraph_texts = [paragraph.text for paragraph in document.paragraphs]
    list_index = paragraph_texts.index("Lista de siglas y abreviaturas")
    body_intro_index = next(
        index
        for index, value in enumerate(paragraph_texts[list_index + 1 :], start=list_index + 1)
        if value == "1. Introducción"
    )
    references_index = next(
        index
        for index, value in enumerate(paragraph_texts[body_intro_index + 1 :], start=body_intro_index + 1)
        if value == "9. Referencias"
    )
    appendix_index = next(
        index
        for index, value in enumerate(paragraph_texts[references_index + 1 :], start=references_index + 1)
        if value.startswith("Apéndice A.")
    )
    reference_registry = read_reference_registry()
    visible_references = visible_reference_entries(reference_registry)
    expected_reference_texts = [entry["reference"] for entry in visible_references]
    candidate_reference_texts = [
        entry["reference"]
        for entry in reference_registry
        if entry["key"] in INTERNAL_CANDIDATE_REFERENCE_KEYS
    ]
    bibliography_paragraphs = [
        value
        for value in paragraph_texts[references_index + 1 : appendix_index]
        if value and not value.startswith("La bibliografía reúne únicamente")
    ]
    content_index = paragraph_texts.index("Contenido")
    math_paragraphs = [paragraph for paragraph in document.paragraphs if paragraph._p.xpath(".//m:oMath")]
    table_headers = [cell.text.strip() for table in document.tables for cell in table.rows[0].cells]
    campaign_scenario_mislabel = False
    for value in acronym_paragraphs:
        words = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+", value)
        if any(
            left.casefold() in {"campaña", "campañas"} and right in {"A", "B"}
            for left, right in zip(words, words[1:])
        ):
            campaign_scenario_mislabel = True
            break
    checks: list[tuple[str, bool]] = [
        ("El DOCX abre como paquete válido", True),
        ("El objetivo general se conserva literalmente", OBJECTIVE_GENERAL in text),
        ("El primer objetivo específico se conserva literalmente", OBJECTIVE_SPECIFIC_1 in text),
        ("El segundo objetivo específico se conserva literalmente", OBJECTIVE_SPECIFIC_2 in text),
        ("La etiqueta PROVISIONAL M1–M2 es visible", PROVISIONAL_LABEL in text),
        ("M3 se identifica como pendiente", "M3" in text and "pendiente" in text.lower()),
        ("Las campañas M2/M3 no se confunden con unidades m²/m³", not campaign_unit_corruptions),
        ("La jerarquía académica prevista está completa", all(title in text for title in EXPECTED_HEADINGS)),
        (
            "La bibliografía visible coincide con las referencias citadas gobernadas",
            bibliography_paragraphs == expected_reference_texts
            and len(bibliography_paragraphs) == expected_references == 40,
        ),
        (
            "Las candidatas internas no aparecen en la bibliografía visible",
            not any(reference in bibliography_paragraphs for reference in candidate_reference_texts),
        ),
        (
            "El registro conserva 43 entradas clasificadas sin claves duplicadas",
            len(reference_registry) == 43
            and len({entry["key"] for entry in reference_registry}) == 43,
        ),
        ("La procedencia y el tratamiento se distinguen", "La procedencia y el tratamiento se registraron por separado" in text),
        ("Los análisis externos del TFG se conservan como fuente primaria", "servicio analítico externo" in text and "Primaria" in text),
        ("No se fuerza una fuente terciaria cuantitativa", "no se asignó a ninguna entrada cuantitativa activa" in text),
        ("No hay marcadores accidentales", not re.search(r"\{\{|\}\}|\bTODO\b|\bTBD\b|Lorem ipsum|\[PENDIENTE\]", text)),
        ("No hay rutas internas visibles", not re.search(r"(?:processed|outputs|scripts|MASTER_escrito)[/\\]|\.csv\b", text, re.IGNORECASE)),
        (
            "No hay etiquetas técnicas internas prohibidas",
            not any(
                token.lower() in text.lower()
                for token in [
                    "dry_lot",
                    "uncovered_anaerobic_lagoon",
                    "composting_invessel",
                    "modelo_calculo",
                    "sistema_manejo_ipcc",
                    "n_ex_pct",
                    "n_ex_fraction",
                    "masa_total_kg_eq",
                    "hardcodeado",
                    "auditado",
                ]
            ),
        ),
        ("No hay errores visibles de codificación", not any(marker in text for marker in ["AnÃ", "metodologÃ", "estiÃ", "nitrÃ", "�"])),
        ("Las unidades anuales conservan la tilde", not re.search(r"/(?:ano|aNo)\b", text)),
        ("No hay etapas con decimales", not re.search(r"\b[AB][1-4][,.]0+\b", text)),
        ("No hay delimitadores visibles de ecuaciones", "\\[" not in text and "\\]" not in text and "$$" not in text),
        ("Las ecuaciones formales seleccionadas son objetos OMML", omml_count == expected_equations == 26),
        ("No hay ecuaciones OMML duplicadas", len(normalized_equations) == len(set(normalized_equations))),
        (
            "Las relaciones obligatorias de masa están cubiertas",
            all(token in equation_corpus for token in ("ma1", "mb1", "ma3", "meq,a4", "meq,b2")),
        ),
        (
            "La transformación A1→A2 conserva cálculo por jornada e integración temporal",
            all(token in equation_corpus for token in ("rj", "r―", "m^a2", "fms,fresco,j", "fcenizas,precompostado,j")),
        ),
        ("La conversión de SV a base húmeda es explícita", "fsv,húmeda" in equation_corpus and "svbaseseca100" in equation_corpus),
        ("La inicialización de N total desde masa fresca es explícita", "ntotal,entrada=mfresca" in equation_corpus and "fn,húmeda" in equation_corpus),
        ("La mineralización antecede al TAN disponible", "nmineralizado" in equation_corpus and "fmin" in equation_corpus),
        ("El cierre conjunto de TAN es explícito", "tansalida=tandisponible" in equation_corpus),
        ("Komakech aparece una sola vez y solo para A2", equation_corpus.count("12,8") == 1 and "mnh3,a2" in equation_corpus),
        ("Las relaciones operativas distinguen electricidad y diésel", all(token in equation_corpus for token in ("pmec", "feimn,elec", "vdiésel", "qdiésel", "10−3"))),
        ("M3 no interviene en las ecuaciones", "m3" not in equation_corpus),
        (
            "La masa equivalente no se usa como base de N",
            not any("meq" in eq and ("ntotal" in eq or "tan" in eq) for eq in normalized_equations),
        ),
        (
            "La cobertura documental se vincula con los identificadores metodológicos vigentes",
            {"M11", "M12", "M13", "M14", "M15", "M16", "M02", "N01", "N02", "N03K", "O01", "O02", "C01"} <= trace_ids,
        ),
        (
            "Las ecuaciones recuperadas conservan correspondencia con las fuentes productivas",
            all(
                (
                    "total_depositado = params.estiercol_recolectado_anual / fraccion_recolectada" in mass_source,
                    "remanente = total_depositado - params.estiercol_recolectado_anual" in mass_source,
                    "params.estiercol_recolectado_anual * factor_a2" in mass_source,
                    "return (float(vs_pct_base_seca) / 100.0) * float(fraccion_masa_seca)" in dry_source,
                    "fresh_n_a1 = float(masses[(\"A\", 1)][\"masa_total_kg_eq\"]) * fresh_fraction" in nitrogen_source,
                    "mineralised = (n_total - tan) * p[\"emep_slurry_mineralisation_fraction\"]" in nitrogen_source,
                    "a2_mass / 1000.0 * p[\"komakech_nh3_factor\"] / 1000.0 / KG_N_TO_NH3" in nitrogen_source,
                    "electricity = pump_input_kw * pump_hours" in operational_source,
                    "diesel = tractor_hours * parameters[\"tractor_diesel_l_per_hour\"]" in operational_source,
                    "quantity * float(factors.loc[ident, \"valor\"]) / grams_per_kg" in imn_source,
                )
            ),
        ),
        ("No queda sintaxis LaTeX fuente visible", not re.search(r"\\(?:frac|mathrm|times|sum|left|right)|_\{", text)),
        ("La lista de siglas y abreviaturas está presente", "Lista de siglas y abreviaturas" in text),
        ("La lista de siglas cierra los preliminares", content_index < list_index < body_intro_index),
        ("La lista de siglas deriva del registro y contiene solo usos reales", listed_acronyms == expected_acronyms),
        ("Todas las entradas utilizadas del registro tienen primera aparición válida", first_mentions_ok),
        ("No hay candidatos reales a sigla sin clasificar", not unknown_acronyms),
        ("TAN se identifica como sigla de origen inglés", acronym_by_code("TAN").first_mention in non_list_text),
        ("CIA se desarrolla como Centro de Investigaciones Agronómicas", acronym_by_code("CIA").first_mention in non_list_text),
        ("CIA no se desarrolla como Ciudad de la Investigación", "Ciudad de la Investigación (CIA)" not in text),
        ("ISO se presenta sin atribuirle siglas inglesas", acronym_by_code("ISO").first_mention in non_list_text and "ISO, por sus siglas en inglés" not in text),
        ("EMEP usa su denominación abreviada oficial sin expansión mecánica", acronym_by_code("EMEP").first_mention in non_list_text and "EMEP, por sus siglas en inglés" not in text),
        ("EEA conserva el tratamiento de sigla inglesa", acronym_by_code("EEA").first_mention in non_list_text),
        (
            "No se usa campaña A/B para las alternativas",
            not campaign_scenario_mislabel,
        ),
        ("No quedan anglicismos editoriales acordados", not re.search(r"\b(?:benchmark|ledger|pool|subpool|default|pipeline|proxy|proxies|QA)\b", non_list_text, re.IGNORECASE)),
        ("No quedan formas planas auditadas de unidades o fórmulas", not re.search(r"(?<![\w])(?:m2|m3|kg\s*CO2|g\s*PO4-?3)(?![\w])", non_list_text)),
        ("Las magnitudes de superficie auditadas usan espacio y superíndice", all(value in non_list_text for value in ("15 m²", "60 m²", "81 m²"))),
        ("No quedan m2 o m3 planos junto a magnitudes", not re.search(r"\d\s*m[23](?![\w])", non_list_text)),
        ("Las potencias científicas negativas usan exponentes compuestos", "1,18 × 10⁻⁸" in non_list_text and "2,17 × 10⁻⁹" in non_list_text and not re.search(r"×\s*10\s*\^?[-−]\s*\d+", non_list_text)),
        ("No queda la forma ortográfica incorrecta húmedad", "húmedad" not in non_list_text),
        ("No quedan regresiones gramaticales del normalizador", not any(phrase.casefold() in non_list_text.casefold() for phrase in grammar_regressions)),
        ("Las etiquetas NOx están en español y con notación química", "NOx as NO2" not in non_list_text and "NOx as NO₂" not in non_list_text and "NOx como NO₂" in non_list_text),
        ("Las fórmulas principales conservan notación científica", all(value in non_list_text for value in ("CO₂", "CH₄", "N₂O", "NH₃", "NO₃⁻", "PO₄³⁻", "m²", "m³"))),
        ("El comité asesor completo procede del MASTER", all(name in text and role in text for name, role in committee_from_master(Document(str(MASTER))))),
        ("La portada no usa párrafos vacíos como separadores", not cover_manual_blanks),
        ("La portada distribuye sus bloques mediante espaciado estructural", cover_spacing_pt >= 250),
        ("La portada conserva un único salto al terminar y una cadena indivisible", cover_page_breaks == [len(cover_paragraphs) - 1] and all(paragraph.paragraph_format.keep_with_next for paragraph in cover_nonempty[:-1])),
        ("La numeración de ecuaciones usa tabulaciones estructurales", all(len(paragraph._p.xpath("./w:pPr/w:tabs/w:tab")) == 2 for paragraph in math_paragraphs)),
        ("La Figura 1 representa emisiones en A1–A4 y B1–B2", boundary_svg.count("Emisiones") >= 6),
        ("La prosa antecede a tablas, figuras y todas las ecuaciones", validate_editorial_order(document, expected_tables, expected_figures, expected_equations)),
        ("El MASTER conserva su hash registrado", master_hash_before == master_hash_after == REGISTERED_REFERENCE_SHA256),
        ("La salida está fuera del directorio protegido", MASTER.parent not in OUT_DOCX.parents),
        ("Las fuentes reproducibles del diagrama de fronteras existen", SYSTEM_BOUNDARY_PNG.exists() and SYSTEM_BOUNDARY_SVG.exists()),
        ("Las figuras insertadas coinciden con las previstas", len(document.inline_shapes) == expected_figures),
        ("Las tablas insertadas coinciden con las previstas", len(document.tables) == expected_tables),
        ("El Escenario A se identifica como operación habitual", "Escenario A" in text and "operación habitual" in text),
        ("El Escenario B se identifica como materializado temporalmente", "Escenario B" in text and "materializarlo temporalmente" in text),
        ("La tanqueta y el cañón tienen funciones distintas", "La tanqueta almacena" in text and "el cañón aplica" in text),
        ("Se distingue el intervalo previo al muestreo", all(term in text for term in ["jueves por la tarde", "lunes por la mañana", "entradas"])),
        ("M1 y M2 se identifican como campañas experimentales elegibles", all(term in text for term in ["actividades de campo de M1 el 10 de noviembre de 2025", "Para M2", "M1 y M2 recibieron igual peso"])),
        ("M3 permanece pendiente y fuera de los datos y parámetros", "M3 está pendiente y no interviene en los datos, parámetros, ecuaciones o resultados" in text),
        ("La muestra de precompostado se ubica antes de A2", "representa la salida de A1 y la entrada a A2, no una muestra de lombricompost terminado" in text),
        ("La procedencia física de sólidos y líquidos está documentada", all(term in text for term in ["sala de espera", "pila con mayor tiempo de permanencia", "cinco alícuotas consecutivas", "una misma abertura"])),
        ("La distribución de laboratorios es coherente", all(term in text for term in ["LASA determinó el N total del estiércol fresco", "Para el precompostado, el CIA", "Bioenergía determinó humedad, materia seca, cenizas y sólidos volátiles"])),
        ("El protocolo de Bioenergía conserva condiciones confirmadas", all(term in text for term in ["105 °C durante 16 h", "575 °C durante 4 h", "se enfrió en desecador", "tres réplicas analíticas por muestra compuesta"])),
        ("Leitner sustenta el procedimiento adoptado de sólidos volátiles", all(term in text for term in ["respaldo en el protocolo de Leitner et al. (2020)", "sin atribuirle el carácter de norma universal", "575 °C durante 4 h"])),
        ("Jjagwe sustenta las condiciones adoptadas de sólidos totales", "también empleadas por Jjagwe et al. (2019) para determinar sólidos totales" in text),
        ("La discrepancia documental de la mufla M1 se declara sin equiparar tiempos", all(term in text for term in ["ventana de operación de seis horas", "confirmación consolidada del ejecutor de cuatro horas", "no se reinterpretó como exposición continua"])),
        ("Las bases analíticas del precompostado se mantienen separadas", all(term in text for term in ["80 °C durante 48 h", "no fue una determinación de humedad", "gravimetría independiente de Bioenergía a 105 °C durante 16 h"])),
        ("El N del precompostado no reinicializa A2", "A2 recibió productivamente el N total y el nitrógeno amoniacal total propagados desde A1" in text),
        ("El muestreo líquido no sustituye la frecuencia anual", "Esta condición específica de campaña se mantuvo separada de la frecuencia operativa anual" in text),
        ("Los datos productivos y de contraste se distinguen", all(term in text for term in ["inicializó el N total en A1, A3 y B1", "se conservó como contraste sin reinicializar las cadenas propagadas"])),
        ("La integración conserva la jerarquía y el peso temporal", all(term in text for term in ["réplica analítica, muestra compuesta, promedio de campaña e integración entre campañas", "M1 y M2 recibieron igual peso"])),
        ("La transformación A1→A2 se calcula primero por campaña", "se calculó primero por campaña" in text and "no se construyó a partir de un promedio global previo" in text),
        ("La trazabilidad experimental del cuerpo está presente", all(header in table_headers for header in ["Material", "Procedencia física", "Determinaciones", "Laboratorio", "Relación con el sistema", "Función metodológica"])),
        ("El apéndice experimental contiene diseño y resultados esenciales", all(title in text for title in ["Diseño de muestreo y distribución analítica de las campañas M1–M2", "Resultados experimentales esenciales y función en el modelo"])),
        (
            "El apéndice de balances permite auditar la propagación de N total y TAN",
            all(
                header in table_headers
                for header in [
                    "N total de entrada (kg N/año)",
                    "TAN de entrada (kg N/año)",
                    "N transferido o retornado según EMEP (kg N/año)",
                    "TAN de salida (kg N/año)",
                ]
            ),
        ),
        (
            "Las masas gestionadas por etapa son visibles",
            all(
                header in table_headers
                for header in ["Masa gestionada (kg eq/año)", "Significado físico"]
            )
            and all(
                term in text
                for term in [
                    "Estiércol fresco recolectado; masa húmeda anual",
                    "Precompostado de entrada; masa húmeda inferida mediante la transformación A1→A2",
                    "no es masa de estiércol medida ni base de N",
                ]
            ),
        ),
        (
            "Las pérdidas físicas de N permiten conciliar el balance por etapa",
            all(
                header in table_headers
                for header in [
                    "NH₃-N (kg N/año)",
                    "NOx-N (kg N/año)",
                    "N₂-N (kg N/año)",
                    "N₂O-N directo (kg N/año)",
                    "N perdido en agua durante el manejo (kg N/año)",
                    "N por lixiviación o escorrentía (kg N/año)",
                    "Base de TAN para las pérdidas",
                ]
            ),
        ),
        (
            "Las rutas de emisiones se presentan de forma desagregada por etapa",
            all(
                header in table_headers
                for header in [
                    "N₂O directo (kg/año)",
                    "N₂O indirecto por volatilización (kg/año)",
                    "N₂O indirecto por lixiviación (kg/año)",
                    "NH₃ (kg/año)",
                    "NO₃⁻ (kg/año)",
                ]
            ),
        ),
        (
            "Las contribuciones climáticas de manejo, electricidad y diésel permanecen separadas",
            all(
                header in table_headers
                for header in [
                    "Manejo del estiércol (kg CO₂-eq/año)",
                    "Electricidad (kg CO₂-eq/año)",
                    "Diésel (kg CO₂-eq/año)",
                ]
            ),
        ),
        (
            "Las emisiones físicas de la combustión del diésel son visibles",
            all(term in text for term in ["kg/año de CO₂ fósil", "kg/año de CH₄ fósil", "kg/año de N₂O en cada escenario"]),
        ),
        (
            "La inconsistencia interna de N₂O en Jjagwe se declara sin cambiar el valor aprobado",
            all(
                term in text
                for term in [
                    "3,943 × 10⁻⁵ g/kg",
                    "0,03943 mg/kg",
                    "39,43 mg/kg",
                    "no modifica el inventario productivo de A2",
                ]
            ),
        ),
        ("La identificación instrumental no añade modelos no confirmados", "Elementar Vario Macro Cube" in text and "No se consignan fabricante, modelo, placa o número de serie porque esa identificación no está confirmada" in text),
        ("A1 se describe sin precisión falsa", "21 días" in text and "tres a cuatro semanas" in text),
        ("A2 se describe como operación regular posterior a A1", "13 semanas" in text and "operación regular" in text and "después de A1" in text),
        ("No se atribuye una muestra de lombricompost terminado", "no muestreó lombricompost terminado" in text),
        ("El MCF se identifica como aproximación no medida a tres días", "MCF de 38 %" in text and "aproximación conservadora del IPCC" in text and "No corresponde a una medición específica" in text),
        ("El marco teórico separa inventario, modelado de emisiones y evaluación de impactos", all(term in text for term in ["El inventario reúne datos de actividad", "El modelado de emisiones relaciona esos datos", "La evaluación de impactos se realiza después"])),
        ("El marco teórico distingue factores metodológicos de datos de actividad", all(term in text for term in ["son datos de actividad", "cumplen una función metodológica", "no constituyen mediciones directas de la lechería"])),
        ("El IPCC se presenta con sus funciones activas", all(term in text for term in ["B₀ expresa", "EF₃ relaciona", "EF₁ cumple", "EF₄ transforma", "EF₅ se aplica", "FracLEACH representa"])),
        ("EMEP/EEA complementa y no sustituye al IPCC", all(term in text for term in ["Esta guía conjunta no sustituye al IPCC", "nitrógeno amoniacal total constituye la base de actividad", "almacenamiento líquido", "aplicación al suelo"])),
        ("Komakech permanece acotado a NH₃ de A2", all(term in text for term in ["A2 constituye una excepción acotada", "masa húmeda de residuo que ingresa a la etapa", "no sustituye las aproximaciones EMEP/EEA", "no reinicializa las reservas propagadas"])),
        ("EF 3.1 se describe como caracterización y no como generación de emisiones", all(term in text for term in ["pertenece a la fase de Evaluación del Impacto del Ciclo de Vida", "flujo elemental por factor de caracterización", "EF 3.1 no estima ni genera las emisiones"])),
        ("Python permanece como fuente productiva del ACV", all(term in text for term in ["La implementación productiva y reproducible de esta relación se realiza en Python", "Python permanece como fuente productiva y reproducible del inventario"])),
        ("SimaPro se limita a verificación pendiente sin resultados atribuidos", all(term in text for term in ["su función se limita a una verificación independiente", "su ejecución presencial en SimaPro permanece pendiente", "No se presentan resultados, concordancias ni discrepancias Python–SimaPro"])),
        ("No se afirman resultados positivos inexistentes de SimaPro", not any(term in text for term in ["SimaPro confirmó", "SimaPro demostró", "SimaPro reprodujo", "resultados de SimaPro mostraron", "se obtuvo en SimaPro"])),
        ("SimaPro no sustituye ni reconstruye el ACV productivo", all(term in text for term in ["No se reconstruirá el ACV completo", "Python permanece como fuente productiva y reproducible"])),
        ("Los factores IMN conservan funciones diferenciadas", all(term in text for term in ["Para la electricidad se utiliza un factor agregado de consumo", "Para el diésel se emplean factores físicos de combustión", "sí se caracterizan posteriormente con EF 3.1"])),
        ("No se presenta 3,5 días como parámetro canónico", "3,5 días" not in text and "3.5 días" not in text),
    ]

    labels = [
        paragraph.text.strip()
        for paragraph in document.paragraphs
        if re.fullmatch(r"(?:Tabla|Figura) \d+", paragraph.text.strip())
    ]
    checks.append(("No hay rótulos duplicados", len(labels) == len(set(labels))))
    checks.append(("La numeración global de tablas es continua", sorted(int(x.split()[1]) for x in labels if x.startswith("Tabla")) == list(range(1, expected_tables + 1))))
    checks.append(("La numeración global de figuras es continua", sorted(int(x.split()[1]) for x in labels if x.startswith("Figura")) == list(range(1, expected_figures + 1))))
    equation_numbers = [
        int(match.group(1))
        for paragraph in document.paragraphs
        if paragraph._p.xpath(".//m:oMath")
        and (match := re.fullmatch(r"\s*\((\d+)\)", paragraph.text))
    ]
    checks.append(("La numeración global de ecuaciones es continua", equation_numbers == list(range(1, expected_equations + 1))))
    checks.append(("Las tablas no duplican columnas de etapa", not ({"Etapa", "Nombre de etapa"} <= set(table_headers))))

    paragraph_text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    clause_text = re.split(r"(?<=[.!?])\s+", paragraph_text)
    table_rows = [" ".join(cell.text for cell in row.cells) for table in document.tables for row in table.rows]
    clauses_without_b = [
        re.sub(r"\bB[12]:.*$", "", clause, flags=re.IGNORECASE)
        for clause in clause_text + table_rows
    ]
    scenario_a_mislabel = any(
        re.search(r"\bA[1-4]:", clause)
        and re.search(r"\bpur[ií]n(?:es)?\b", clause, flags=re.IGNORECASE)
        for clause in clauses_without_b
    )
    checks.append(("No se asocian purines con etapas del Escenario A", not scenario_a_mislabel))

    failures = [name for name, passed in checks if not passed]
    status = "PASS" if not failures else "FAIL"
    lines = [
        "# Validación del documento integral provisional",
        "",
        f"- Estado general: **{status}**.",
        f"- Documento: `{OUT_DOCX.name}`.",
        f"- Tablas con numeración global: {expected_tables}.",
        f"- Figuras con numeración global: {expected_figures}.",
        f"- Ecuaciones con numeración global: {expected_equations}.",
        f"- Entradas conservadas en el registro bibliográfico: {len(reference_registry)}.",
        f"- Referencias citadas incluidas en la bibliografía visible: {expected_references}.",
        f"- SHA-256 del MASTER antes: `{master_hash_before}`.",
        f"- SHA-256 del MASTER después: `{master_hash_after}`.",
        "",
        "## Comprobaciones",
        "",
    ]
    lines.extend(f"- {'PASS' if passed else 'FAIL'} — {name}." for name, passed in checks)
    lines.extend(
        [
            "",
            "## Auditoría de siglas y abreviaturas",
            "",
            f"- Entradas registradas y utilizadas: {len(expected_acronyms)}.",
            f"- Candidatos no registrados: {', '.join(unknown_acronyms) if unknown_acronyms else 'ninguno'}.",
            f"- Exclusiones clasificadas disponibles: {len(IGNORED_ACRONYM_CANDIDATES)}.",
            "",
            "## Alcance de la validación",
            "",
            "- La validación comprueba estructura, objetivos, identificación provisional, integridad del paquete, numeración editorial, rutas visibles, figuras, tablas e integridad del MASTER.",
            "- La revisión visual y la validación científica supervisora permanecen separadas de estas comprobaciones programáticas.",
            "- La bibliografía visible contiene únicamente las referencias citadas; las candidatas no utilizadas permanecen gobernadas en el registro integral.",
        ]
    )
    OUT_VALIDATION.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if failures:
        raise RuntimeError(f"Falló la validación del documento integral: {failures}")


def main() -> None:
    validate_inputs()
    master_hash_before = sha256_file(MASTER)
    table_count, figure_count, equation_count, reference_count = build_document()
    master_hash_after = assert_reference_docx_intact(MASTER, master_hash_before)
    validate_document(
        master_hash_before,
        master_hash_after,
        table_count,
        figure_count,
        equation_count,
        reference_count,
    )
    print(f"Documento integral generado: {OUT_DOCX.relative_to(ROOT)}")
    print(f"Validación generada: {OUT_VALIDATION.relative_to(ROOT)}")
    print(f"MASTER sin cambios: {master_hash_after}")


if __name__ == "__main__":
    main()
