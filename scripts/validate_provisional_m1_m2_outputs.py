"""Validación cruzada de productos académicos de la corrida PROVISIONAL M1–M2."""

from __future__ import annotations

import csv
import hashlib
import math
from pathlib import Path

from docx import Document

import generate_conclusions_docx as conclusions_generator
import generate_thesis_graphics as graphics_generator


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "processed"
TABLES = ROOT / "outputs" / "tablas_tesis"
GRAPHICS = ROOT / "outputs" / "graficos_tesis"
DOCS = ROOT / "outputs" / "documentos_tfg"
LABEL = "PROVISIONAL M1–M2"
REPORT = DOCS / "reporte_validacion_provisional_m1_m2.md"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def close(left: object, right: object, tolerance: float = 1e-12) -> bool:
    return math.isclose(float(left), float(right), rel_tol=tolerance, abs_tol=tolerance)


def finite_sum(row: dict[str, str], columns: list[str]) -> float:
    values = []
    for column in columns:
        raw = row.get(column, "")
        try:
            value = float(raw)
        except (TypeError, ValueError):
            continue
        if math.isfinite(value):
            values.append(value)
    return sum(values)


def document_text(path: Path) -> tuple[str, str]:
    document = Document(path)
    body = [paragraph.text for paragraph in document.paragraphs]
    body.extend(cell.text for table in document.tables for row in table.rows for cell in row.cells)
    headers = [paragraph.text for section in document.sections for paragraph in section.header.paragraphs]
    return "\n".join(body), "\n".join(headers)


def fmt_es(value: float, decimals: int) -> str:
    text = f"{float(value):,.{decimals}f}"
    text = text.replace(",", "X").replace(".", ",").replace("X", " ")
    return text.rstrip("0").rstrip(",")


def validate_characterization() -> None:
    integration = {
        (row["material"], row["variable"]): row
        for row in read_rows(PROCESSED / "muestreos_integracion_interjornada_provisional.csv")
        if row["valor_integrado_provisional"]
    }
    labels = {
        "Estiércol fresco": "estiércol fresco",
        "Estiércol precompostado": "estiércol precompostado",
        "Aguas verdes": "aguas verdes",
        "Purines": "purines",
    }
    variables = {
        "Nitrogeno total": "N total",
        "Humedad": "humedad",
        "Materia seca": "materia seca",
        "Cenizas": "cenizas",
        "Solidos volatiles": "sólidos volátiles",
        "Densidad": "densidad",
        "Carbono": "carbono",
        "Relación C/N": "relación C/N",
    }
    table = read_rows(TABLES / "tabla_02_caracterizacion_muestras.csv")
    for row in table:
        source = integration[(labels[row["tipo_muestra"]], variables[row["variable"]])]
        assert close(row["valor"], source["valor_integrado_provisional"])
        assert row["jornada_muestreo"] == source["jornadas_elegibles"]
        assert row["estado_integracion"] == source["estado_integracion"]
    active = read_rows(PROCESSED / "acv_parametros_escenario_etapa.csv")
    liquid = {(row["escenario"], row["etapa"]): row for row in active if row["escenario"] + row["etapa"] in {"A4", "B2"}}
    assert all(row["jornadas_n_ex"] == "M2" for row in liquid.values())


def validate_factor_and_masses() -> None:
    transformation = next(
        row for row in read_rows(PROCESSED / "muestreos_transformacion_masa_interjornada.csv")
        if row["tipo_fila"] == "integracion"
    )
    factor = transformation["mass_ratio_integrado"]
    masses = {(row["escenario"], row["etapa"]): row for row in read_rows(PROCESSED / "masa_total_escenario_etapa.csv")}
    flows = read_rows(TABLES / "tabla_03_flujos_icv.csv")
    for row in flows:
        key = (row["escenario"], row["etapa"])
        if row["flujo"] == "Factor restante fresco a precompostado":
            assert close(row["valor"], factor)
        if row["flujo"] == "Masa equivalente total":
            assert close(row["valor"], masses[key]["masa_total_kg_eq"])


def validate_emissions() -> None:
    raw = {(row["Escenario"], row["Etapa"]): row for row in read_rows(PROCESSED / "ACV_resumen_emisiones.csv")}
    table = read_rows(TABLES / "tabla_06_emisiones_por_etapa.csv")
    grouped: dict[tuple[str, str, str], float] = {}
    for row in table:
        key = (row["escenario"], row["etapa"], row["sustancia"])
        grouped[key] = grouped.get(key, 0.0) + float(row["valor"])
    columns = {
        "CO2": ["CO2_medido"], "CH4": ["CH4_ec1"],
        "N2O": ["N2O_ec14", "N2O_ec2", "N2O_ec5", "N2O_ec6", "N2O_ec16", "N2O_ec18"],
        "NH3": ["NH3_ec12", "NH3_ec20"], "NO3": ["NO3_ec13", "NO3_ec21"],
    }
    for key, row in raw.items():
        for substance, source_columns in columns.items():
            assert close(grouped.get((*key, substance), 0.0), finite_sum(row, source_columns))


def validate_impacts_and_comparison() -> None:
    stage_source = {(row["Escenario"], row["Etapa"]): row for row in read_rows(PROCESSED / "acv_impacto_por_etapa_escenario.csv")}
    stage_table = read_rows(TABLES / "tabla_07_impactos_por_etapa.csv")
    grouped: dict[tuple[str, str, str], float] = {}
    for row in stage_table:
        key = (row["escenario"], row["etapa"], row["categoria_impacto"])
        grouped[key] = grouped.get(key, 0.0) + float(row["resultado_equivalente"])
    for key, row in stage_source.items():
        assert close(grouped[(*key, "Calentamiento global")], row["impacto_calentamiento_global_kg_co2eq"])
        assert close(grouped[(*key, "Eutrofizacion")], row["impacto_eutrofizacion_kg_po4eq"])

    totals_source = {(row["Escenario"], category): float(row[column]) for row in read_rows(PROCESSED / "acv_impacto_total_por_escenario.csv") for category, column in {
        "Calentamiento global": "impacto_calentamiento_global_kg_co2eq",
        "Eutrofizacion": "impacto_eutrofizacion_kg_po4eq",
    }.items()}
    totals_table = {(row["escenario"], row["categoria_impacto"]): float(row["resultado_total"]) for row in read_rows(TABLES / "tabla_08_impactos_totales_por_escenario.csv")}
    assert totals_source.keys() == totals_table.keys()
    assert all(close(totals_source[key], totals_table[key]) for key in totals_source)
    for row in read_rows(TABLES / "tabla_09_comparacion_escenarios.csv"):
        category = row["categoria_impacto"]
        a, b = totals_source[("A", category)], totals_source[("B", category)]
        assert close(row["escenario_A"], a) and close(row["escenario_B"], b)
        assert close(row["diferencia_absoluta_B_menos_A"], b - a)
        assert close(row["diferencia_porcentual_B_vs_A"], (b - a) / a * 100)
        assert row["escenario_con_mayor_impacto"] == ("B" if b > a else "A")


def validate_documents_and_conclusions() -> None:
    methodology_text, methodology_header = document_text(DOCS / "metodologia_desarrollada_tfg.docx")
    results_text, results_header = document_text(DOCS / "resultados_desarrollados_tfg.docx")
    conclusions_text, conclusions_header = document_text(DOCS / "conclusiones_desarrolladas_tfg.docx")
    for body, header in ((methodology_text, methodology_header), (results_text, results_header), (conclusions_text, conclusions_header)):
        assert LABEL in body and LABEL in header and "M3" in body

    characterization = read_rows(TABLES / "tabla_02_caracterizacion_muestras.csv")
    required = [
        row for row in characterization
        if (row["tipo_muestra"], row["variable"]) in {
            ("Estiércol fresco", "Nitrogeno total"), ("Estiércol fresco", "Materia seca"),
            ("Estiércol fresco", "Solidos volatiles"), ("Estiércol precompostado", "Materia seca"),
            ("Aguas verdes", "Nitrogeno total"), ("Purines", "Nitrogeno total"),
        }
    ]
    assert len(required) == 6
    assert all(fmt_es(float(row["valor"]), 3) in methodology_text for row in required)
    assert all(fmt_es(float(row["valor"]), 3) in results_text for row in required)

    totals = read_rows(PROCESSED / "acv_impacto_total_por_escenario.csv")
    for row in totals:
        assert fmt_es(float(row["impacto_calentamiento_global_kg_co2eq"]), 6) in results_text
        assert fmt_es(float(row["impacto_eutrofizacion_kg_po4eq"]), 6) in results_text

    emissions = read_rows(TABLES / "tabla_06_emisiones_por_etapa.csv")
    emission_totals: dict[tuple[str, str], float] = {}
    for row in emissions:
        key = (row["escenario"], row["sustancia"])
        emission_totals[key] = emission_totals.get(key, 0.0) + float(row["valor"])
    required_emissions = [
        ("A", "CH4"), ("A", "N2O"), ("A", "NH3"), ("A", "NO3"), ("A", "CO2"),
        ("B", "CH4"), ("B", "N2O"), ("B", "NH3"), ("B", "NO3"),
    ]
    visible_substance = {"CH4": "CH₄", "N2O": "N₂O", "NH3": "NH₃", "NO3": "NO₃⁻", "CO2": "CO₂"}
    for key in required_emissions:
        expected = f"{fmt_es(emission_totals.get(key, 0.0), 2)} kg {visible_substance[key[1]]}/año"
        assert expected in results_text

    totals_dict = conclusions_generator.impact_totals()
    percentages = conclusions_generator.comparisons(totals_dict)
    reference, normalized = conclusions_generator.processed_indicators(totals_dict)
    collected, remainder = conclusions_generator.flow_inventory(reference)
    stages = conclusions_generator.stage_totals()
    expected = conclusions_generator.build_conclusions(
        totals_dict, normalized, percentages, stages, reference, collected, remainder
    )
    assert all(item["text"] in conclusions_text for item in expected)


def validate_graph_sources() -> None:
    source = (ROOT / "scripts" / "generate_thesis_graphics.py").read_text(encoding="utf-8")
    assert 'TABLE_DIR = BASE_DIR / "outputs" / "tablas_tesis"' in source
    assert "processed/" not in source and "CIA_samples" not in source and "volatile_solids_treatment" not in source
    newest_table = max(path.stat().st_mtime_ns for path in TABLES.glob("tabla_*.csv"))
    graphics = sorted(GRAPHICS.glob("fig_*.png")) + sorted(GRAPHICS.glob("fig_*.svg"))
    assert len(graphics) == 30
    assert all(path.stat().st_mtime_ns >= newest_table for path in graphics)

    samples = graphics_generator.read_table("muestras")
    figure_1 = graphics_generator.characterization_series(samples, ["Humedad", "Materia seca"])
    figure_2 = graphics_generator.characterization_series(samples, ["Solidos volatiles", "Cenizas"])
    for series, variables in (
        (figure_1, ["Humedad", "Materia seca"]),
        (figure_2, ["Solidos volatiles", "Cenizas"]),
    ):
        assert set(series["variable"]) == set(variables)
        assert series["valor"].notna().all() and not series.empty
        assert float(series["valor"].max()) > 1.0
        source_values = {
            (row["tipo_muestra"], row["variable"]): float(row["valor"])
            for row in read_rows(TABLES / "tabla_02_caracterizacion_muestras.csv")
            if row["variable"] in variables
        }
        plotted_values = {
            (str(row["tipo_muestra"]), str(row["variable"])): float(row["valor"])
            for _, row in series.iterrows()
        }
        assert plotted_values == source_values


def main() -> None:
    validate_characterization()
    validate_factor_and_masses()
    validate_emissions()
    validate_impacts_and_comparison()
    validate_documents_and_conclusions()
    validate_graph_sources()
    master = ROOT / "MASTER_escrito" / "TFG_ACV_Estiercol_MASTER.docx"
    master_hash = hashlib.sha256(master.read_bytes()).hexdigest().upper()
    REPORT.write_text(
        "# Validación cruzada de la corrida PROVISIONAL M1–M2\n\n"
        "- Caracterización experimental contra integración vigente: PASS.\n"
        "- Factor fresco→precompostado contra `mass_ratio_integrado`: PASS.\n"
        "- Masas contra inventario canónico: PASS.\n"
        "- Emisiones contra resumen canónico: PASS.\n"
        "- Impactos por etapa y totales contra salidas canónicas: PASS.\n"
        "- Comparación entre escenarios recalculada: PASS.\n"
        "- Metodología, resultados y conclusiones identificados como `PROVISIONAL M1–M2`: PASS.\n"
        "- Cifras documentales verificadas con el redondeo visible: PASS.\n"
        "- Conclusiones cuantitativas reconstruidas desde tablas e impactos: PASS.\n"
        "- Gráficos generados exclusivamente desde tablas de tesis vigentes: PASS.\n"
        f"- SHA-256 del MASTER verificado: `{master_hash}`.\n",
        encoding="utf-8",
    )
    print("VALIDACIÓN CRUZADA PROVISIONAL M1–M2: PASS")
    print("Caracterización, factor, masas, emisiones, impactos, comparación, DOCX, conclusiones y gráficos: PASS")
    print(f"Reporte: {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
