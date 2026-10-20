"""Sensibilidad determinística OFAT del ACV para MCF líquido y B0.

La evaluación reutiliza el inventario productivo y la caracterización EF 3.1 en
memoria. No modifica los parámetros, las emisiones ni los impactos canónicos.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
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
    fig.savefig(svg_path, bbox_inches="tight")
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
    stage.to_csv(OUTPUT / "sensibilidad_impactos_por_etapa.csv", index=False, encoding="utf-8-sig")
    scenarios.to_csv(OUTPUT / "sensibilidad_impactos_por_escenario.csv", index=False, encoding="utf-8-sig")
    comparison.to_csv(OUTPUT / "sensibilidad_comparacion_escenarios.csv", index=False, encoding="utf-8-sig")
    critical.to_csv(OUTPUT / "sensibilidad_umbral_mcf.csv", index=False, encoding="utf-8-sig")
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
`figura_sensibilidad_climatica` en formatos PNG y SVG.
"""
    (OUTPUT / "README.md").write_text(manifest, encoding="utf-8")
    print(
        "Sensibilidad ACV PASS: caso central reproducido; "
        f"MCF crítico={fixed(critical_value, 3)} %; salidas canónicas intactas."
    )


if __name__ == "__main__":
    main()
