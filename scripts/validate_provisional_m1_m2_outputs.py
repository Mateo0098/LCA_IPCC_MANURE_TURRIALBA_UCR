"""Validación cruzada de productos académicos de la corrida PROVISIONAL M1–M2."""

from __future__ import annotations

import csv
import hashlib
import math
from pathlib import Path

from docx import Document

import generate_conclusions_docx as conclusions_generator
import generate_a2_jjagwe_benchmark as benchmark_generator
import generate_thesis_graphics as graphics_generator
from quantitative_comparison import Comparison, dominant


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


def validate_a2_nitrogen_basis() -> None:
    params = {
        (row["escenario"], row["etapa"]): row
        for row in read_rows(PROCESSED / "acv_parametros_escenario_etapa.csv")
    }
    masses = {
        (row["escenario"], row["etapa"]): row
        for row in read_rows(PROCESSED / "masa_total_escenario_etapa.csv")
    }
    a2 = params[("A", "2")]
    integrated_n = next(
        row for row in read_rows(PROCESSED / "muestreos_integracion_interjornada_provisional.csv")
        if row["material"] == "estiércol precompostado" and row["variable"] == "N total"
    )
    assert close(a2["n_ex_pct"], integrated_n["valor_integrado_provisional"])
    assert a2["base_analitica_n_ex"] == "material preparado/seco por CIA a 80 °C durante 48 h"
    assert a2["transformacion_n_acv"] == "multiplicar_por_fraccion_materia_seca_gravimetrica_TFG_105C"
    effective_fraction = (float(a2["n_ex_pct"]) / 100.0) * (float(a2["materia_seca_pct"]) / 100.0)
    annual_n = float(masses[("A", "2")]["masa_total_kg_eq"]) * effective_fraction
    assert effective_fraction > 0.0 and annual_n > 0.0
    for key, row in params.items():
        if key != ("A", "2"):
            assert row["transformacion_n_acv"] == "ninguna"


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


def validate_a2_benchmark() -> None:
    generated = read_rows(PROCESSED / "a2_ipcc_jjagwe_benchmark.csv")
    expected = benchmark_generator.build_rows()
    assert len(generated) == len(expected) == 4
    for observed, calculated in zip(generated, expected):
        assert observed.keys() == calculated.keys()
        for key, value in calculated.items():
            if isinstance(value, float):
                assert close(observed[key], value)
            else:
                assert observed[key] == value
    assert all("eutrof" not in row["indicador"].lower() for row in generated)
    direct = next(row for row in generated if row["indicador"] == "N2O directo por materia seca de entrada")
    emissions = next(
        row for row in read_rows(PROCESSED / "ACV_resumen_emisiones.csv")
        if row["Escenario"] == "A" and row["Etapa"] == "2"
    )
    dry_mass = float(direct["masa_seca_entrada_a2_kg_anio"])
    assert close(direct["valor_ipcc"], float(emissions["N2O_ec2"]) * 1_000_000.0 / dry_mass)
    assert not close(direct["valor_ipcc"], finite_sum(emissions, ["N2O_ec2", "N2O_ec5", "N2O_ec6"]) * 1_000_000.0 / dry_mass)
    models = read_rows(PROCESSED / "modelo_etapa_overrides.csv")
    a2_model = next(row for row in models if row["escenario"] == "A" and row["etapa"] == "2")
    assert a2_model["modelo"] == "ipcc"
    assert all(row["modelo"] != "medido" for row in models)


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
        expected_higher = "B" if b > a else "A" if a > b else "Iguales"
        assert row["escenario_con_mayor_impacto"] == expected_higher
        expected_unit = "kg CO2-eq/año" if category == "Calentamiento global" else "kg PO4-eq/año"
        assert row["unidad"] == expected_unit
        comparison = Comparison("A", a, "B", b, expected_unit)
        comparison.assert_consistent(
            difference=float(row["diferencia_absoluta_B_menos_A"]),
            percentage=float(row["diferencia_porcentual_B_vs_A"]),
        )
        comparison.assert_rounding_unambiguous(6)


def validate_quantitative_narratives() -> None:
    results_text, _ = document_text(DOCS / "resultados_desarrollados_tfg.docx")
    conclusions_text, _ = document_text(DOCS / "conclusiones_desarrolladas_tfg.docx")
    totals = {
        (row["Escenario"], category): float(row[column])
        for row in read_rows(PROCESSED / "acv_impacto_total_por_escenario.csv")
        for category, column in {
            "Calentamiento global": "impacto_calentamiento_global_kg_co2eq",
            "Eutrofizacion": "impacto_eutrofizacion_kg_po4eq",
        }.items()
    }
    for category, visible_category in (("Calentamiento global", "calentamiento global"), ("Eutrofizacion", "eutrofización")):
        comparison = Comparison("Escenario A", totals[("A", category)], "Escenario B", totals[("B", category)], "kg/año")
        assert comparison.higher_label is not None and comparison.lower_label is not None
        if category == "Calentamiento global":
            assert f"mayor impacto de {visible_category} en el {comparison.higher_label}" in results_text
        else:
            assert f"el {comparison.higher_label} presentó el mayor impacto" in results_text
        assert f"el {comparison.higher_label} presentó el mayor impacto por unidad funcional" in conclusions_text
        assert f"el {comparison.lower_label} alcanzó el menor indicador" in conclusions_text or f"para el {comparison.lower_label} bajo" in conclusions_text

    synthetic = Comparison("A", 10.0, "B", 8.0, "kg/año")
    synthetic.assert_consistent(difference=-2.0, percentage=-20.0)
    assert synthetic.higher_label == "A" and synthetic.lower_label == "B"
    try:
        synthetic.assert_consistent(difference=2.0, percentage=-20.0)
    except RuntimeError:
        pass
    else:
        raise AssertionError("No se detectó una diferencia con signo contradictorio.")
    try:
        Comparison("A", 1.0004, "B", 1.0003, "kg/año").assert_rounding_unambiguous(3)
    except RuntimeError:
        pass
    else:
        raise AssertionError("No se detectó una comparación ambigua por redondeo.")
    assert dominant({"A1": 1.0, "A2": 2.0}, decimals=3) == ("A2", 2.0)
    benchmark = {row["indicador"]: row for row in read_rows(PROCESSED / "a2_ipcc_jjagwe_benchmark.csv")}
    benchmark_directions = []
    for indicator in ("CH4 por materia seca de entrada", "N2O directo por materia seca de entrada"):
        row = benchmark[indicator]
        benchmark_directions.append("menor" if float(row["valor_ipcc"]) < float(row["valor_experimental"]) else "mayor")
    assert f"estimación IPCC fue {benchmark_directions[0]} para" in results_text
    assert f"y {benchmark_directions[1]} para" in results_text


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
    validate_a2_nitrogen_basis()
    validate_emissions()
    validate_a2_benchmark()
    validate_impacts_and_comparison()
    validate_quantitative_narratives()
    validate_documents_and_conclusions()
    validate_graph_sources()
    master = ROOT / "MASTER_escrito" / "TFG_ACV_Estiercol_MASTER.docx"
    master_hash = hashlib.sha256(master.read_bytes()).hexdigest().upper()
    REPORT.write_text(
        "# Validación cruzada de la corrida PROVISIONAL M1–M2\n\n"
        "- Caracterización experimental contra integración vigente: PASS.\n"
        "- Factor fresco→precompostado contra `mass_ratio_integrado`: PASS.\n"
        "- Masas contra inventario canónico: PASS.\n"
        "- Base de N de A2, fórmula húmeda y exclusión de las demás etapas: PASS.\n"
        "- Emisiones contra resumen canónico: PASS.\n"
        "- Contraste Jjagwe reproducido, N2O directo aislado y sin ruta medida ni eutrofización experimental: PASS.\n"
        "- Impactos por etapa y totales contra salidas canónicas: PASS.\n"
        "- Comparación entre escenarios recalculada: PASS.\n"
        "- Dirección narrativa, signos, porcentajes, unidades, dominancia y ambigüedad por redondeo: PASS.\n"
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
