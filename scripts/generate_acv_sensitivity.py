"""Sensibilidad determinística OFAT del ACV para MCF líquido y B0.

La evaluación reutiliza el inventario productivo y la caracterización EF 3.1 en
memoria. No modifica los parámetros, las emisiones ni los impactos canónicos.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
matplotlib.rcParams["svg.hashsalt"] = "lca-ipcc-manure-sensitivity"
import matplotlib.pyplot as plt
import pandas as pd

from compute_acv_impact_equivalents import (
    compute_impacts,
    load_factors,
    load_functional_reference,
)
from reactive_n_ledger import productive_emission_rows
from scientific_numeric_presentation import axis_tick, fixed, significant


ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "processed"
OUTPUT = ROOT / "outputs" / "sensibilidad_acv"
CANONICAL_STAGE_IMPACTS = PROCESSED / "acv_impacto_por_etapa_escenario.csv"
CANONICAL_SCENARIO_IMPACTS = PROCESSED / "acv_impacto_total_por_escenario.csv"
SENSITIVITY_STAGE_IMPACTS = OUTPUT / "sensibilidad_impactos_por_etapa.csv"
SENSITIVITY_SCENARIO_IMPACTS = OUTPUT / "sensibilidad_impactos_por_escenario.csv"
SENSITIVITY_COMPARISON = OUTPUT / "sensibilidad_comparacion_escenarios.csv"
SENSITIVITY_THRESHOLD = OUTPUT / "sensibilidad_umbral_mcf.csv"
SENSITIVITY_FIGURE = OUTPUT / "figura_sensibilidad_climatica.png"
SENSITIVITY_PROVENANCE = OUTPUT / "vigencia_sensibilidad.json"
REFERENCE_B0 = 0.24
REFERENCE_MCF = 38.0
LIQUID_STAGES = {("A", 3): REFERENCE_MCF, ("B", 1): REFERENCE_MCF}
MCF_SCREENING_VALUES = (0.0, 19.0, 38.0, 57.0, 76.0, 100.0)
B0_VALUES = (REFERENCE_B0 * 0.85, REFERENCE_B0, REFERENCE_B0 * 1.15)
IMPACT_COLUMNS = {
    "Cambio climático": ("impacto_calentamiento_global_kg_co2eq", "kg CO₂-eq/año"),
    "Eutrofización terrestre": ("impacto_eutrofizacion_terrestre_mol_neq", "mol N-eq/año"),
    "Eutrofización marina": ("impacto_eutrofizacion_marina_kg_neq", "kg N-eq/año"),
}
CANONICAL_GUARDS = (
    PROCESSED / "reactive_n_ledger_parameters.csv",
    PROCESSED / "ipcc_sistemas_manejo_estiercol_factores.csv",
    PROCESSED / "ipcc_factores_manejo_overrides_etapa.csv",
    PROCESSED / "ACV_resumen_emisiones.csv",
    PROCESSED / "acv_impacto_por_etapa_escenario.csv",
    PROCESSED / "acv_impacto_total_por_escenario.csv",
)
FRESHNESS_REL_TOL = 1e-11
FRESHNESS_ABS_TOL = 1e-12


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _impact_case(*, b0: float | None = None, liquid_mcf: float | None = None) -> pd.DataFrame:
    mcf = None
    if liquid_mcf is not None:
        mcf = {key: liquid_mcf for key in LIQUID_STAGES}
    emission_rows = productive_emission_rows(
        b0_m3_ch4_per_kg_vs=b0,
        mcf_overrides_pct=mcf,
    )
    emissions = pd.DataFrame(emission_rows.values()).sort_values(["Escenario", "Etapa"])
    emission_columns = [column for column in emissions if column not in {"Escenario", "Etapa"}]
    emissions[emission_columns] = emissions[emission_columns].apply(
        pd.to_numeric, errors="coerce"
    ).fillna(0.0)
    factors = load_factors(PROCESSED / "acv_factores_equivalencia.csv")
    reference = load_functional_reference(PROCESSED / "masa_total_escenario_etapa.csv")
    resources = pd.read_csv(PROCESSED / "acv_inventario_recursos_operativos.csv")
    return compute_impacts(emissions, factors, reference, resources)


def _case_definitions() -> list[dict[str, object]]:
    cases: list[dict[str, object]] = []
    for value in MCF_SCREENING_VALUES:
        cases.append({
            "id": f"MCF_{value:g}",
            "factor": "MCF del almacenamiento líquido",
            "case": "Referencia" if value == REFERENCE_MCF else f"Exploración {value:g} %",
            "value": value,
            "unit": "%",
            "b0": REFERENCE_B0,
            "mcf": value,
        })
    for label, value in (("−15 %", B0_VALUES[0]), ("Referencia", B0_VALUES[1]), ("+15 %", B0_VALUES[2])):
        cases.append({
            "id": f"B0_{value:.3f}",
            "factor": "Potencial máximo de producción de metano (B₀)",
            "case": label,
            "value": value,
            "unit": "m³ CH₄/kg SV",
            "b0": value,
            "mcf": REFERENCE_MCF,
        })
    return cases


def _freshness_error(detail: str) -> RuntimeError:
    return RuntimeError(
        "Los resultados de sensibilidad MCF/B₀ están incompletos, son incompatibles "
        f"o no corresponden al ACV canónico vigente: {detail} "
        "Regenerarlos antes del manuscrito con: "
        "python scripts/generate_acv_sensitivity.py"
    )


def _require_columns(frame: pd.DataFrame, required: set[str], label: str) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise _freshness_error(f"{label} no contiene las columnas requeridas {missing}.")


def _finite_float(value: object, context: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise _freshness_error(f"{context} no es numérico: {value!r}.") from exc
    if not math.isfinite(number):
        raise _freshness_error(f"{context} no es finito: {value!r}.")
    return number


def _assert_fresh_close(actual: object, expected: object, context: str) -> float:
    actual_number = _finite_float(actual, context)
    expected_number = _finite_float(expected, f"referencia canónica de {context}")
    if not math.isclose(
        actual_number,
        expected_number,
        rel_tol=FRESHNESS_REL_TOL,
        abs_tol=FRESHNESS_ABS_TOL,
    ):
        raise _freshness_error(
            f"{context} difiere del valor canónico "
            f"({actual_number!r} frente a {expected_number!r})."
        )
    return abs(actual_number - expected_number)


def _provenance_payload(
    *,
    canonical_stage_path: Path,
    canonical_scenario_path: Path,
    sensitivity_stage_path: Path,
    sensitivity_scenario_path: Path,
    comparison_path: Path,
    threshold_path: Path,
    figure_path: Path,
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "reference_parameters": {
            "mcf_pct": REFERENCE_MCF,
            "b0_m3_ch4_per_kg_sv": REFERENCE_B0,
        },
        "canonical_sha256": {
            "stage_impacts": sha256(canonical_stage_path),
            "scenario_impacts": sha256(canonical_scenario_path),
        },
        "sensitivity_sha256": {
            "stage_impacts": sha256(sensitivity_stage_path),
            "scenario_impacts": sha256(sensitivity_scenario_path),
            "comparison": sha256(comparison_path),
            "threshold": sha256(threshold_path),
            "climate_figure_png": sha256(figure_path),
        },
    }


def write_sensitivity_provenance(
    *,
    provenance_path: Path = SENSITIVITY_PROVENANCE,
    canonical_stage_path: Path = CANONICAL_STAGE_IMPACTS,
    canonical_scenario_path: Path = CANONICAL_SCENARIO_IMPACTS,
    sensitivity_stage_path: Path = SENSITIVITY_STAGE_IMPACTS,
    sensitivity_scenario_path: Path = SENSITIVITY_SCENARIO_IMPACTS,
    comparison_path: Path = SENSITIVITY_COMPARISON,
    threshold_path: Path = SENSITIVITY_THRESHOLD,
    figure_path: Path = SENSITIVITY_FIGURE,
) -> None:
    """Registra huellas de la corrida sin recalcular el modelo científico."""

    payload = _provenance_payload(
        canonical_stage_path=canonical_stage_path,
        canonical_scenario_path=canonical_scenario_path,
        sensitivity_stage_path=sensitivity_stage_path,
        sensitivity_scenario_path=sensitivity_scenario_path,
        comparison_path=comparison_path,
        threshold_path=threshold_path,
        figure_path=figure_path,
    )
    provenance_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def validate_sensitivity_freshness(
    *,
    provenance_path: Path = SENSITIVITY_PROVENANCE,
    canonical_stage_path: Path = CANONICAL_STAGE_IMPACTS,
    canonical_scenario_path: Path = CANONICAL_SCENARIO_IMPACTS,
    sensitivity_stage_path: Path = SENSITIVITY_STAGE_IMPACTS,
    sensitivity_scenario_path: Path = SENSITIVITY_SCENARIO_IMPACTS,
    comparison_path: Path = SENSITIVITY_COMPARISON,
    threshold_path: Path = SENSITIVITY_THRESHOLD,
    figure_path: Path = SENSITIVITY_FIGURE,
) -> dict[str, float]:
    """Comprueba que la sensibilidad pertenece a los impactos canónicos vigentes.

    La tolerancia relativa de 1e-11 y la absoluta de 1e-12 solo absorben ruido
    de punto flotante de doble precisión. Los valores internos no se redondean.
    """

    paths = {
        "registro de vigencia": provenance_path,
        "impactos canónicos por etapa": canonical_stage_path,
        "impactos canónicos por escenario": canonical_scenario_path,
        "sensibilidad por etapa": sensitivity_stage_path,
        "sensibilidad por escenario": sensitivity_scenario_path,
        "comparación de sensibilidad": comparison_path,
        "umbral MCF": threshold_path,
        "figura climática": figure_path,
    }
    missing = [f"{label}: {path}" for label, path in paths.items() if not path.is_file()]
    if missing:
        raise _freshness_error("faltan archivos requeridos: " + "; ".join(missing) + ".")

    try:
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise _freshness_error(f"el registro de vigencia no es legible: {exc}.") from exc
    expected_provenance = _provenance_payload(
        canonical_stage_path=canonical_stage_path,
        canonical_scenario_path=canonical_scenario_path,
        sensitivity_stage_path=sensitivity_stage_path,
        sensitivity_scenario_path=sensitivity_scenario_path,
        comparison_path=comparison_path,
        threshold_path=threshold_path,
        figure_path=figure_path,
    )
    if provenance != expected_provenance:
        raise _freshness_error(
            "las huellas del registro de vigencia no coinciden con los impactos "
            "canónicos o con los productos de sensibilidad presentes."
        )

    canonical_stage = pd.read_csv(canonical_stage_path)
    canonical_scenario = pd.read_csv(canonical_scenario_path)
    stage = pd.read_csv(sensitivity_stage_path, encoding="utf-8-sig")
    scenario = pd.read_csv(sensitivity_scenario_path, encoding="utf-8-sig")
    comparison = pd.read_csv(comparison_path, encoding="utf-8-sig")
    threshold = pd.read_csv(threshold_path, encoding="utf-8-sig")

    impact_columns = {category: column for category, (column, _unit) in IMPACT_COLUMNS.items()}
    impact_units = {category: unit for category, (_column, unit) in IMPACT_COLUMNS.items()}
    categories = set(impact_columns)
    expected_stages = {("A", stage_number) for stage_number in range(1, 5)} | {
        ("B", stage_number) for stage_number in range(1, 3)
    }
    expected_scenarios = {"A", "B"}

    _require_columns(
        canonical_stage,
        {"Escenario", "Etapa", *impact_columns.values()},
        "la salida canónica por etapa",
    )
    _require_columns(
        canonical_scenario,
        {"Escenario", *impact_columns.values()},
        "la salida canónica por escenario",
    )
    canonical_stage_keys = {
        (str(row.Escenario), int(row.Etapa))
        for row in canonical_stage[["Escenario", "Etapa"]].itertuples(index=False)
    }
    if canonical_stage_keys != expected_stages or len(canonical_stage) != len(expected_stages):
        raise _freshness_error("la salida canónica no contiene exactamente las seis etapas A1–B2.")
    canonical_scenarios = set(canonical_scenario["Escenario"].astype(str))
    if canonical_scenarios != expected_scenarios or len(canonical_scenario) != 2:
        raise _freshness_error("la salida canónica no contiene exactamente los escenarios A y B.")

    common_columns = {
        "Caso",
        "Factor evaluado",
        "Caso del factor",
        "Valor del parámetro",
        "Unidad del parámetro",
        "Categoría de impacto",
    }
    _require_columns(
        stage,
        common_columns | {"Escenario", "Etapa", "Impacto", "Unidad del impacto"},
        "la sensibilidad por etapa",
    )
    _require_columns(
        scenario,
        common_columns | {"Escenario", "Impacto", "Unidad del impacto"},
        "la sensibilidad por escenario",
    )
    _require_columns(
        comparison,
        common_columns
        | {
            "Impacto escenario A",
            "Impacto escenario B",
            "Diferencia B − A",
            "Unidad del impacto",
        },
        "la comparación de sensibilidad",
    )

    definitions = {str(item["id"]): item for item in _case_definitions()}
    case_ids = set(definitions)
    expected_stage_keys = {
        (case_id, scenario_key, f"{scenario_key}{stage_number}", category)
        for case_id in case_ids
        for scenario_key, stage_number in expected_stages
        for category in categories
    }
    actual_stage_keys = set(
        zip(
            stage["Caso"].astype(str),
            stage["Escenario"].astype(str),
            stage["Etapa"].astype(str),
            stage["Categoría de impacto"].astype(str),
        )
    )
    if actual_stage_keys != expected_stage_keys or len(stage) != len(expected_stage_keys):
        raise _freshness_error(
            "la sensibilidad por etapa tiene una categoría, etapa, caso o clave duplicada faltante."
        )
    expected_scenario_keys = {
        (case_id, scenario_key, category)
        for case_id in case_ids
        for scenario_key in expected_scenarios
        for category in categories
    }
    actual_scenario_keys = set(
        zip(
            scenario["Caso"].astype(str),
            scenario["Escenario"].astype(str),
            scenario["Categoría de impacto"].astype(str),
        )
    )
    if actual_scenario_keys != expected_scenario_keys or len(scenario) != len(expected_scenario_keys):
        raise _freshness_error(
            "la sensibilidad por escenario tiene una categoría, escenario, caso o clave duplicada faltante."
        )
    expected_comparison_keys = {
        (case_id, category) for case_id in case_ids for category in categories
    }
    actual_comparison_keys = set(
        zip(
            comparison["Caso"].astype(str),
            comparison["Categoría de impacto"].astype(str),
        )
    )
    if actual_comparison_keys != expected_comparison_keys or len(comparison) != len(
        expected_comparison_keys
    ):
        raise _freshness_error(
            "la comparación tiene una categoría, caso o clave duplicada faltante."
        )

    for case_id, definition in definitions.items():
        for frame_label, frame in (
            ("sensibilidad por etapa", stage),
            ("sensibilidad por escenario", scenario),
            ("comparación", comparison),
        ):
            rows = frame[frame["Caso"].astype(str).eq(case_id)]
            for column, expected in (
                ("Factor evaluado", definition["factor"]),
                ("Caso del factor", definition["case"]),
                ("Unidad del parámetro", definition["unit"]),
            ):
                if not rows[column].astype(str).eq(str(expected)).all():
                    raise _freshness_error(
                        f"{frame_label}, caso {case_id}, contiene metadatos incompatibles en {column}."
                    )
            for value in rows["Valor del parámetro"]:
                _assert_fresh_close(
                    value,
                    definition["value"],
                    f"valor del parámetro de {frame_label}, caso {case_id}",
                )
            for category, unit in impact_units.items():
                category_rows = rows[rows["Categoría de impacto"].eq(category)]
                if not category_rows["Unidad del impacto"].astype(str).eq(unit).all():
                    raise _freshness_error(
                        f"{frame_label}, caso {case_id}, usa una unidad incompatible para {category}."
                    )

    canonical_stage_index = canonical_stage.set_index(["Escenario", "Etapa"])
    canonical_scenario_index = canonical_scenario.set_index("Escenario")
    reference_case_ids = ("MCF_38", "B0_0.240")
    maximum_stage_error = 0.0
    maximum_scenario_error = 0.0
    maximum_comparison_error = 0.0
    for case_id in reference_case_ids:
        for scenario_key, stage_number in sorted(expected_stages):
            for category, canonical_column in impact_columns.items():
                row = stage[
                    stage["Caso"].eq(case_id)
                    & stage["Escenario"].eq(scenario_key)
                    & stage["Etapa"].eq(f"{scenario_key}{stage_number}")
                    & stage["Categoría de impacto"].eq(category)
                ].iloc[0]
                error = _assert_fresh_close(
                    row["Impacto"],
                    canonical_stage_index.loc[(scenario_key, stage_number), canonical_column],
                    f"{case_id}, {scenario_key}{stage_number}, {category}",
                )
                maximum_stage_error = max(maximum_stage_error, error)
        for category, canonical_column in impact_columns.items():
            comparison_row = comparison[
                comparison["Caso"].eq(case_id)
                & comparison["Categoría de impacto"].eq(category)
            ].iloc[0]
            values: dict[str, float] = {}
            for scenario_key in sorted(expected_scenarios):
                scenario_row = scenario[
                    scenario["Caso"].eq(case_id)
                    & scenario["Escenario"].eq(scenario_key)
                    & scenario["Categoría de impacto"].eq(category)
                ].iloc[0]
                canonical_value = canonical_scenario_index.loc[scenario_key, canonical_column]
                error = _assert_fresh_close(
                    scenario_row["Impacto"],
                    canonical_value,
                    f"{case_id}, escenario {scenario_key}, {category}",
                )
                maximum_scenario_error = max(maximum_scenario_error, error)
                comparison_value = comparison_row[f"Impacto escenario {scenario_key}"]
                error = _assert_fresh_close(
                    comparison_value,
                    canonical_value,
                    f"comparación {case_id}, escenario {scenario_key}, {category}",
                )
                maximum_comparison_error = max(maximum_comparison_error, error)
                values[scenario_key] = _finite_float(comparison_value, "impacto comparado")
            _assert_fresh_close(
                comparison_row["Diferencia B − A"],
                values["B"] - values["A"],
                f"diferencia B − A de {case_id}, {category}",
            )

    _require_columns(
        threshold,
        {"Existe inversión", "MCF crítico (%)"},
        "la tabla del umbral MCF",
    )
    if len(threshold) != 1 or str(threshold.iloc[0]["Existe inversión"]) != "Sí":
        raise _freshness_error("la tabla del umbral MCF no contiene el cruce vigente esperado.")
    climate = comparison[comparison["Categoría de impacto"].eq("Cambio climático")].set_index(
        "Caso"
    )
    difference_zero = _finite_float(climate.loc["MCF_0", "Diferencia B − A"], "MCF 0 %")
    difference_hundred = _finite_float(
        climate.loc["MCF_100", "Diferencia B − A"], "MCF 100 %"
    )
    if difference_zero * difference_hundred >= 0.0:
        raise _freshness_error("la comparación MCF no conserva el cambio de signo del umbral.")
    expected_threshold = -difference_zero * 100.0 / (difference_hundred - difference_zero)
    threshold_error = _assert_fresh_close(
        threshold.iloc[0]["MCF crítico (%)"],
        expected_threshold,
        "MCF crítico",
    )

    return {
        "maximum_stage_error": maximum_stage_error,
        "maximum_scenario_error": maximum_scenario_error,
        "maximum_comparison_error": maximum_comparison_error,
        "threshold_error": threshold_error,
    }


def _totals(impacts: pd.DataFrame) -> pd.DataFrame:
    columns = [column for column, _ in IMPACT_COLUMNS.values()]
    return impacts.groupby("Escenario", as_index=False)[columns].sum().sort_values("Escenario")


def _lower_scenario(a: float, b: float, tolerance: float = 1e-12) -> str:
    if abs(b - a) <= tolerance * max(1.0, abs(a), abs(b)):
        return "Empate numérico"
    return "A" if a < b else "B"


def _validate_central(central: pd.DataFrame) -> float:
    official = pd.read_csv(PROCESSED / "acv_impacto_por_etapa_escenario.csv")
    official = official.sort_values(["Escenario", "Etapa"]).reset_index(drop=True)
    central = central.sort_values(["Escenario", "Etapa"]).reset_index(drop=True)
    if list(zip(official["Escenario"], official["Etapa"])) != list(zip(central["Escenario"], central["Etapa"])):
        raise AssertionError("El caso central no conserva las seis etapas canónicas.")
    maximum = 0.0
    for column, _ in IMPACT_COLUMNS.values():
        error = (central[column] - official[column]).abs()
        maximum = max(maximum, float(error.max()))
        scale = official[column].abs().clip(lower=1.0)
        if not (error <= 1e-11 * scale).all():
            raise AssertionError(f"El caso central no reproduce la salida oficial en {column}.")
    return maximum


def _critical_mcf() -> dict[str, object]:
    def difference(value: float) -> float:
        totals = _totals(_impact_case(b0=REFERENCE_B0, liquid_mcf=value)).set_index("Escenario")
        column = IMPACT_COLUMNS["Cambio climático"][0]
        return float(totals.loc["B", column] - totals.loc["A", column])

    at_zero = difference(0.0)
    at_hundred = difference(100.0)
    if at_zero == 0.0:
        critical = 0.0
    elif at_zero * at_hundred > 0.0:
        return {
            "Dominio explorado": "0–100 %",
            "Existe inversión": "No",
            "MCF crítico (%)": "",
            "Diferencia B − A en 0 % (kg CO₂-eq/año)": at_zero,
            "Diferencia B − A en 100 % (kg CO₂-eq/año)": at_hundred,
            "Interpretación": "No existe cruce climático dentro del dominio físico explorado.",
        }
    else:
        critical = -at_zero * 100.0 / (at_hundred - at_zero)
    residual = difference(critical)
    if abs(residual) > 1e-8:
        raise AssertionError(f"El MCF crítico no cierra la diferencia climática: {residual}")
    return {
        "Dominio explorado": "0–100 %",
        "Existe inversión": "Sí",
        "MCF crítico (%)": critical,
        "Diferencia B − A en 0 % (kg CO₂-eq/año)": at_zero,
        "Diferencia B − A en 100 % (kg CO₂-eq/año)": at_hundred,
        "Interpretación": (
            "Por debajo del valor crítico, B presenta menor cambio climático; "
            "por encima, A presenta menor cambio climático. El umbral es matemático "
            "y no constituye un MCF experimental para tres días."
        ),
    }


def _write_figure(comparison: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.6))
    selections = [
        ("MCF del almacenamiento líquido", "%", axes[0]),
        ("Potencial máximo de producción de metano (B₀)", "m³ CH₄/kg SV", axes[1]),
    ]
    for factor, unit, ax in selections:
        data = comparison[
            comparison["Factor evaluado"].eq(factor)
            & comparison["Categoría de impacto"].eq("Cambio climático")
        ].sort_values("Valor del parámetro")
        ax.plot(data["Valor del parámetro"], data["Diferencia B − A"], marker="o", color="#1f4e79")
        ax.axhline(0.0, color="#333333", linewidth=0.8)
        ax.set_xlabel(f"Valor del parámetro ({unit})")
        ax.set_ylabel("Diferencia B − A (kg CO₂-eq/año)")
        ax.grid(axis="y", color="#d9d9d9", linewidth=0.6)
        ax.spines[["top", "right"]].set_visible(False)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda value, _pos: axis_tick(value)))
    fig.tight_layout()
    fig.savefig(OUTPUT / "figura_sensibilidad_climatica.png", dpi=300, bbox_inches="tight")
    svg_path = OUTPUT / "figura_sensibilidad_climatica.svg"
    fig.savefig(svg_path, bbox_inches="tight", metadata={"Date": None})
    plt.close(fig)

    # Matplotlib conserva espacios finales en algunas líneas de los SVG. Se
    # normalizan en el generador para que el artefacto regenerable satisfaga
    # los controles de higiene de Git sin alterar su contenido gráfico.
    svg_lines = svg_path.read_text(encoding="utf-8").splitlines()
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_lines) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    before = {path: sha256(path) for path in CANONICAL_GUARDS}
    central = _impact_case(b0=REFERENCE_B0, liquid_mcf=REFERENCE_MCF)
    maximum_central_error = _validate_central(central)
    central_stage = central.set_index(["Escenario", "Etapa"])
    central_totals = _totals(central).set_index("Escenario")
    reference_lower = {
        category: _lower_scenario(
            float(central_totals.loc["A", column]),
            float(central_totals.loc["B", column]),
        )
        for category, (column, _unit) in IMPACT_COLUMNS.items()
    }

    stage_rows: list[dict[str, object]] = []
    scenario_rows: list[dict[str, object]] = []
    comparison_rows: list[dict[str, object]] = []
    for definition in _case_definitions():
        impacts = _impact_case(b0=float(definition["b0"]), liquid_mcf=float(definition["mcf"]))
        totals = _totals(impacts).set_index("Escenario")
        indexed = impacts.set_index(["Escenario", "Etapa"])
        for (scenario, stage), row in indexed.iterrows():
            for category, (column, unit) in IMPACT_COLUMNS.items():
                value = float(row[column])
                reference = float(central_stage.loc[(scenario, stage), column])
                variation = 0.0 if reference == 0.0 and value == 0.0 else ((value / reference - 1.0) * 100.0 if reference else float("nan"))
                stage_rows.append({
                    "Caso": definition["id"], "Factor evaluado": definition["factor"],
                    "Caso del factor": definition["case"], "Valor del parámetro": definition["value"],
                    "Unidad del parámetro": definition["unit"], "Escenario": scenario,
                    "Etapa": f"{scenario}{stage}", "Categoría de impacto": category,
                    "Impacto": value, "Unidad del impacto": unit,
                    "Variación respecto a referencia (%)": variation,
                })
        for category, (column, unit) in IMPACT_COLUMNS.items():
            a = float(totals.loc["A", column])
            b = float(totals.loc["B", column])
            lower = _lower_scenario(a, b)
            for scenario, value in (("A", a), ("B", b)):
                reference = float(central_totals.loc[scenario, column])
                scenario_rows.append({
                    "Caso": definition["id"], "Factor evaluado": definition["factor"],
                    "Caso del factor": definition["case"], "Valor del parámetro": definition["value"],
                    "Unidad del parámetro": definition["unit"], "Escenario": scenario,
                    "Categoría de impacto": category, "Impacto": value,
                    "Unidad del impacto": unit,
                    "Variación respecto a referencia (%)": (value / reference - 1.0) * 100.0,
                })
            comparison_rows.append({
                "Caso": definition["id"], "Factor evaluado": definition["factor"],
                "Caso del factor": definition["case"], "Valor del parámetro": definition["value"],
                "Unidad del parámetro": definition["unit"], "Categoría de impacto": category,
                "Impacto escenario A": a, "Impacto escenario B": b,
                "Diferencia B − A": b - a,
                "Diferencia B respecto a A (%)": (b / a - 1.0) * 100.0,
                "Escenario de menor impacto": lower,
                "Clasificación estable respecto a referencia": "Sí" if lower == reference_lower[category] else "No",
                "Unidad del impacto": unit,
            })

    OUTPUT.mkdir(parents=True, exist_ok=True)
    stage = pd.DataFrame(stage_rows)
    scenarios = pd.DataFrame(scenario_rows)
    comparison = pd.DataFrame(comparison_rows)
    critical = pd.DataFrame([_critical_mcf()])
    stage.to_csv(SENSITIVITY_STAGE_IMPACTS, index=False, encoding="utf-8-sig")
    scenarios.to_csv(SENSITIVITY_SCENARIO_IMPACTS, index=False, encoding="utf-8-sig")
    comparison.to_csv(SENSITIVITY_COMPARISON, index=False, encoding="utf-8-sig")
    critical.to_csv(SENSITIVITY_THRESHOLD, index=False, encoding="utf-8-sig")
    _write_figure(comparison)

    after = {path: sha256(path) for path in CANONICAL_GUARDS}
    if before != after:
        changed = [str(path.relative_to(ROOT)) for path in before if before[path] != after[path]]
        raise AssertionError(f"La sensibilidad modificó salidas canónicas: {changed}")
    critical_value = critical.iloc[0]["MCF crítico (%)"]
    manifest = f"""# Evaluación determinística de sensibilidad del ACV

Estado: **PROVISIONAL M1–M2**.

Se aplicó sensibilidad determinística de un factor a la vez. El MCF de A3 y B1
se varió conjuntamente en un dominio matemático de 0–100 %, con referencia de
38 %. Los extremos no se interpretan como valores medidos o validados para la
residencia operativa de tres días. B₀ se varió ±15 % alrededor de 0,24 m³
CH₄/kg SV, conforme a la incertidumbre de la tabla 10.16A del Refinamiento 2019
del IPCC, en todas las etapas que consumen el parámetro.

- Máxima diferencia absoluta entre el caso central y los impactos oficiales:
  {maximum_central_error:.12g}.
- MCF crítico climático calculado: {significant(critical_value, 4)} %.
- El umbral es un resultado matemático del modelo, no una estimación empírica.
- Los factores EF 3.1, la unidad funcional, los balances de N/TAN y los recursos
  operativos se conservaron.
- Los archivos canónicos protegidos por huella permanecieron sin cambios.

Archivos regenerables: `sensibilidad_impactos_por_etapa.csv`,
`sensibilidad_impactos_por_escenario.csv`,
`sensibilidad_comparacion_escenarios.csv`, `sensibilidad_umbral_mcf.csv` y
`figura_sensibilidad_climatica` en formatos PNG y SVG. El registro
`vigencia_sensibilidad.json` enlaza por huellas estos productos con los impactos
canónicos que reprodujo el caso central; el manuscrito integral rechaza una
corrida incompleta, alterada u obsoleta y solicita regenerarla.
"""
    (OUTPUT / "README.md").write_text(manifest, encoding="utf-8")
    write_sensitivity_provenance()
    validate_sensitivity_freshness()
    print(
        "Sensibilidad ACV PASS: caso central reproducido; "
        f"MCF crítico={fixed(critical_value, 3)} %; salidas canónicas intactas."
    )


if __name__ == "__main__":
    main()
