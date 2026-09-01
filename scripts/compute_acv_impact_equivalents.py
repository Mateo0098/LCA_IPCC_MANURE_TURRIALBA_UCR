from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd


N2O_COLS = ["N2O_ec14", "N2O_ec2", "N2O_ec5", "N2O_ec6", "N2O_ec16", "N2O_ec18"]
NH3_COLS = ["NH3_ec12", "NH3_ec20"]
NO3_COLS = ["NO3_ec13", "NO3_ec21"]
NOX_COLS = ["NOx_as_NO2"]

PALETTE = {"A": "#2a9d8f", "B": "#e76f51"}
FIG_BG = "#f4f7fb"
AX_BG = "#ffffff"
GRID_COLOR = "#d9e2ec"
TEXT_COLOR = "#1f2937"
SPINE_COLOR = "#94a3b8"
BAR_EDGE_COLOR = "#64748b"


def configure_style() -> None:
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Segoe UI", "Inter", "Arial", "DejaVu Sans"]
    plt.rcParams["figure.dpi"] = 120
    plt.rcParams["axes.titleweight"] = "semibold"
    plt.rcParams["axes.titlesize"] = 13
    plt.rcParams["axes.labelsize"] = 11
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["ytick.labelsize"] = 10
    plt.rcParams["text.color"] = TEXT_COLOR
    plt.rcParams["axes.labelcolor"] = TEXT_COLOR
    plt.rcParams["xtick.color"] = "#334155"
    plt.rcParams["ytick.color"] = "#334155"
    plt.rcParams["axes.edgecolor"] = SPINE_COLOR
    plt.rcParams["axes.linewidth"] = 0.9
    plt.rcParams["grid.linestyle"] = "--"
    plt.rcParams["grid.alpha"] = 0.5
    plt.rcParams["grid.color"] = GRID_COLOR
    plt.rcParams["legend.frameon"] = False


def y_axis_formatter(value: float, _pos: float) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.0f}k"
    return f"{value:.0f}"


def pretty_number(value: float) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.2f}k"
    return f"{value:.2f}"


def annotate_bars(ax: plt.Axes) -> None:
    for patch in ax.patches:
        h = patch.get_height()
        if np.isnan(h) or h <= 0:
            continue
        ax.annotate(
            pretty_number(float(h)),
            (patch.get_x() + patch.get_width() / 2, h),
            ha="center",
            va="bottom",
            fontsize=9,
            color="#334155",
            xytext=(0, 5),
            textcoords="offset points",
        )


EXPECTED_FACTOR_METADATA = {
    ("CH4", "air unspecified", "Cambio climático"): "kg CO2-eq/kg CH4",
    ("N2O", "air unspecified", "Cambio climático"): "kg CO2-eq/kg N2O",
    ("NH3", "air unspecified", "Eutrofización terrestre"): "mol N-eq/kg NH3",
    ("NH3", "air unspecified", "Eutrofización marina"): "kg N-eq/kg NH3",
    ("NOx as NO2", "air unspecified", "Eutrofización terrestre"): "mol N-eq/kg NOx as NO2",
    ("NOx as NO2", "air unspecified", "Eutrofización marina"): "kg N-eq/kg NOx as NO2",
    ("NO3", "fresh water", "Eutrofización marina"): "kg N-eq/kg NO3",
}


def load_factors(path: Path) -> dict[tuple[str, str, str], dict[str, object]]:
    df = pd.read_csv(path)
    required = {
        "especie_quimica", "compartimento", "categoria_impacto", "factor",
        "unidad_factor", "metodo", "version",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas en factores: {sorted(missing)}")

    out: dict[tuple[str, str, str], dict[str, object]] = {}
    for _, row in df.iterrows():
        key = (
            str(row["especie_quimica"]).strip(),
            str(row["compartimento"]).strip(),
            str(row["categoria_impacto"]).strip(),
        )
        if key in out:
            raise ValueError(f"Factor EF 3.1 duplicado: {key}")
        if key not in EXPECTED_FACTOR_METADATA:
            raise ValueError(f"Combinación especie–compartimento–categoría no admitida por EF 3.1: {key}")
        unit = str(row["unidad_factor"]).strip()
        if unit != EXPECTED_FACTOR_METADATA[key]:
            raise ValueError(f"Unidad de factor incompatible para {key}: {unit}")
        method = str(row["metodo"]).strip()
        version = str(row["version"]).strip()
        if method != "Environmental Footprint" or version != "3.1":
            raise ValueError(f"Método o versión incompatible para {key}: {method} {version}")
        out[key] = {"factor": float(row["factor"]), "unidad": unit,
                    "compartimento": key[1], "metodo": method, "version": version}
    if set(out) != set(EXPECTED_FACTOR_METADATA):
        missing = set(EXPECTED_FACTOR_METADATA) - set(out)
        raise ValueError(f"Conjunto incompleto de factores EF 3.1; faltan: {sorted(missing)}")
    return out


def load_emissions(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ["CO2_medido", "CH4_ec1"] + N2O_COLS + NH3_COLS + NO3_COLS + NOX_COLS:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    df["Escenario"] = df["Escenario"].astype(str).str.strip().str.upper()
    df["Etapa"] = pd.to_numeric(df["Etapa"], errors="coerce").fillna(0).astype(int)
    return df


def load_functional_reference(path: Path, tolerance: float = 1e-6) -> float:
    mass = pd.read_csv(path)
    required = {"escenario", "flujo_referencia_anual_kg"}
    missing = required - set(mass.columns)
    if missing:
        raise ValueError(f"Faltan columnas de referencia funcional: {sorted(missing)}")

    references: dict[str, float] = {}
    for scenario, group in mass.groupby(mass["escenario"].astype(str).str.upper()):
        values = pd.to_numeric(group["flujo_referencia_anual_kg"], errors="raise").unique()
        if len(values) != 1:
            raise ValueError(f"El escenario {scenario} tiene múltiples flujos de referencia: {values}")
        references[str(scenario)] = float(values[0])

    if set(references) != {"A", "B"}:
        raise ValueError(f"Se requieren referencias para A y B; se obtuvo {references}")
    if references["A"] <= 0 or references["B"] <= 0:
        raise ValueError("Los flujos de referencia deben ser positivos.")
    if abs(references["A"] - references["B"]) > tolerance:
        raise ValueError(
            "Los escenarios no parten del mismo flujo anual de referencia: "
            f"A={references['A']:.12f}; B={references['B']:.12f}"
        )
    return references["A"]


def resolve_emissions_path(base: Path) -> Path:
    path = base / "processed" / "ACV_resumen_emisiones.csv"
    if not path.exists():
        raise FileNotFoundError(f"No existe el resumen canónico de emisiones: {path}")
    return path


def compute_impacts(
    df: pd.DataFrame,
    factors: dict[tuple[str, str, str], dict[str, object]],
    functional_reference_kg: float,
) -> pd.DataFrame:
    out = df.copy()
    out["n2o_total_kg"] = out[N2O_COLS].sum(axis=1)
    out["nh3_total_kg"] = out[NH3_COLS].sum(axis=1)
    out["no3_total_kg"] = out[NO3_COLS].sum(axis=1)
    out["nox_total_kg_as_no2"] = out[NOX_COLS].sum(axis=1)
    out["co2_total_kg"] = out["CO2_medido"]
    out["ch4_total_kg"] = out["CH4_ec1"]

    def factor(species: str, compartment: str, category: str) -> float:
        return float(factors[(species, compartment, category)]["factor"])

    out["impacto_calentamiento_global_kg_co2eq"] = (
        out["ch4_total_kg"] * factor("CH4", "air unspecified", "Cambio climático")
        + out["n2o_total_kg"] * factor("N2O", "air unspecified", "Cambio climático")
    )
    out["impacto_eutrofizacion_terrestre_mol_neq"] = (
        out["nh3_total_kg"] * factor("NH3", "air unspecified", "Eutrofización terrestre")
        + out["nox_total_kg_as_no2"] * factor("NOx as NO2", "air unspecified", "Eutrofización terrestre")
    )
    out["impacto_eutrofizacion_marina_kg_neq"] = (
        out["nh3_total_kg"] * factor("NH3", "air unspecified", "Eutrofización marina")
        + out["nox_total_kg_as_no2"] * factor("NOx as NO2", "air unspecified", "Eutrofización marina")
        + out["no3_total_kg"] * factor("NO3", "fresh water", "Eutrofización marina")
    )
    out["referencia_funcional_estiercol_fresco_kg"] = functional_reference_kg
    out["impacto_calentamiento_global_kg_co2eq_por_kg_estiercol_fresco"] = (
        out["impacto_calentamiento_global_kg_co2eq"] / functional_reference_kg
    )
    out["impacto_eutrofizacion_terrestre_mol_neq_por_kg_estiercol_fresco"] = out["impacto_eutrofizacion_terrestre_mol_neq"] / functional_reference_kg
    out["impacto_eutrofizacion_marina_kg_neq_por_kg_estiercol_fresco"] = out["impacto_eutrofizacion_marina_kg_neq"] / functional_reference_kg

    cols = [
        "Escenario",
        "Etapa",
        "ch4_total_kg",
        "n2o_total_kg",
        "co2_total_kg",
        "nh3_total_kg",
        "no3_total_kg",
        "nox_total_kg_as_no2",
        "impacto_calentamiento_global_kg_co2eq",
        "impacto_eutrofizacion_terrestre_mol_neq",
        "impacto_eutrofizacion_marina_kg_neq",
        "referencia_funcional_estiercol_fresco_kg",
        "impacto_calentamiento_global_kg_co2eq_por_kg_estiercol_fresco",
        "impacto_eutrofizacion_terrestre_mol_neq_por_kg_estiercol_fresco",
        "impacto_eutrofizacion_marina_kg_neq_por_kg_estiercol_fresco",
    ]
    return out[cols].sort_values(["Escenario", "Etapa"]).reset_index(drop=True)


def plot_by_stage(df_stage: pd.DataFrame, col: str, title: str, ylabel: str, output_base: Path) -> None:
    scenarios = ["A", "B"]
    stages = [1, 2, 3, 4]
    pivot = (
        df_stage.pivot_table(index="Etapa", columns="Escenario", values=col, aggfunc="sum")
        .reindex(index=stages, columns=scenarios, fill_value=0.0)
    )
    x = np.arange(len(stages))
    width = 0.36

    fig, ax = plt.subplots(figsize=(9.0, 5.4))
    fig.patch.set_facecolor(FIG_BG)
    ax.set_facecolor(AX_BG)
    ax.bar(
        x - width / 2,
        pivot["A"].to_numpy(),
        width,
        label="A",
        color=PALETTE["A"],
        edgecolor=BAR_EDGE_COLOR,
        linewidth=0.8,
    )
    ax.bar(
        x + width / 2,
        pivot["B"].to_numpy(),
        width,
        label="B",
        color=PALETTE["B"],
        edgecolor=BAR_EDGE_COLOR,
        linewidth=0.8,
    )
    ax.set_xticks(x)
    ax.set_xticklabels([str(s) for s in stages])
    ax.set_xlabel("Etapa")
    ax.set_ylabel(ylabel)
    ax.set_title(title, pad=12)
    ax.legend(title="Escenario", ncol=2, loc="upper right")
    ax.grid(axis="y")
    ax.grid(axis="x", visible=False)
    ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))
    ymax = float(max(pivot["A"].max(), pivot["B"].max()))
    ax.set_ylim(0, ymax * 1.22 if ymax > 0 else 1.0)
    annotate_bars(ax)
    fig.tight_layout()
    fig.savefig(output_base.with_suffix(".png"), dpi=300, bbox_inches="tight")
    fig.savefig(output_base.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def plot_total_by_scenario(
    df_total: pd.DataFrame, col: str, title: str, ylabel: str, output_base: Path
) -> None:
    data = (
        df_total.set_index("Escenario")
        .reindex(index=["A", "B"])
        .fillna(0.0)
    )
    x = np.arange(2)
    vals = data[col].to_numpy()
    colors = ["#2a9d8f", "#e76f51"]

    fig, ax = plt.subplots(figsize=(9.0, 5.4))
    fig.patch.set_facecolor(FIG_BG)
    ax.set_facecolor(AX_BG)
    bars = ax.bar(x, vals, width=0.55, color=colors, edgecolor=BAR_EDGE_COLOR, linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(["A", "B"])
    ax.set_xlabel("Escenario")
    ax.set_ylabel(ylabel)
    ax.set_title(title, pad=12)
    ax.grid(axis="y")
    ax.grid(axis="x", visible=False)
    ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))
    ymax = float(vals.max()) if len(vals) else 0.0
    ax.set_ylim(0, ymax * 1.22 if ymax > 0 else 1.0)
    for b in bars:
        h = b.get_height()
        ax.annotate(
            pretty_number(float(h)),
            (b.get_x() + b.get_width() / 2, h),
            ha="center",
            va="bottom",
            fontsize=9,
            color="#334155",
            xytext=(0, 3),
            textcoords="offset points",
        )
    fig.tight_layout()
    fig.savefig(output_base.with_suffix(".png"), dpi=300, bbox_inches="tight")
    fig.savefig(output_base.with_suffix(".pdf"), bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    configure_style()
    base = Path(__file__).resolve().parent.parent
    processed = base / "processed"
    graphics_dir = base / "graphics_results"
    graphics_dir.mkdir(parents=True, exist_ok=True)
    factors_path = processed / "acv_factores_equivalencia.csv"
    mass_path = processed / "masa_total_escenario_etapa.csv"
    emissions_path = resolve_emissions_path(base)

    factors = load_factors(factors_path)
    functional_reference_kg = load_functional_reference(mass_path)
    emissions = load_emissions(emissions_path)
    impact_stage = compute_impacts(emissions, factors, functional_reference_kg)

    stage_out = processed / "acv_impacto_por_etapa_escenario.csv"
    impact_stage.to_csv(stage_out, index=False, encoding="utf-8-sig")

    totals = (
        impact_stage.groupby("Escenario", as_index=False)[
            ["impacto_calentamiento_global_kg_co2eq", "impacto_eutrofizacion_terrestre_mol_neq", "impacto_eutrofizacion_marina_kg_neq"]
        ]
        .sum()
        .sort_values("Escenario")
    )
    totals["referencia_funcional_estiercol_fresco_kg"] = functional_reference_kg
    totals["impacto_calentamiento_global_kg_co2eq_por_kg_estiercol_fresco"] = (
        totals["impacto_calentamiento_global_kg_co2eq"] / functional_reference_kg
    )
    totals["impacto_eutrofizacion_terrestre_mol_neq_por_kg_estiercol_fresco"] = totals["impacto_eutrofizacion_terrestre_mol_neq"] / functional_reference_kg
    totals["impacto_eutrofizacion_marina_kg_neq_por_kg_estiercol_fresco"] = totals["impacto_eutrofizacion_marina_kg_neq"] / functional_reference_kg
    totals_out = processed / "acv_impacto_total_por_escenario.csv"
    totals.to_csv(totals_out, index=False, encoding="utf-8-sig")

    plot_by_stage(
        impact_stage,
        "impacto_calentamiento_global_kg_co2eq",
        r"Impacto de Calentamiento Global (CO$_2$-eq) por Etapa y Escenario",
        r"kg CO$_2$",
        graphics_dir / "ACV_impacto_calentamiento_global",
    )
    plot_by_stage(
        impact_stage,
        "impacto_eutrofizacion_terrestre_mol_neq",
        "Eutrofización terrestre EF 3.1 por etapa y escenario",
        "mol N-eq",
        graphics_dir / "ACV_impacto_eutrofizacion_terrestre",
    )
    plot_by_stage(impact_stage, "impacto_eutrofizacion_marina_kg_neq",
                  "Eutrofización marina EF 3.1 por etapa y escenario", "kg N-eq",
                  graphics_dir / "ACV_impacto_eutrofizacion_marina")
    plot_total_by_scenario(
        totals,
        "impacto_calentamiento_global_kg_co2eq",
        r"Impacto Total de Calentamiento Global (CO$_2$-eq) por Escenario",
        r"kg CO$_2$",
        graphics_dir / "ACV_impacto_total_calentamiento_global_por_escenario",
    )
    plot_total_by_scenario(
        totals,
        "impacto_eutrofizacion_terrestre_mol_neq",
        "Eutrofización terrestre total EF 3.1 por escenario", "mol N-eq",
        graphics_dir / "ACV_impacto_total_eutrofizacion_terrestre_por_escenario",
    )
    plot_total_by_scenario(totals, "impacto_eutrofizacion_marina_kg_neq",
                           "Eutrofización marina total EF 3.1 por escenario", "kg N-eq",
                           graphics_dir / "ACV_impacto_total_eutrofizacion_marina_por_escenario")

    print(f"Factores: {factors_path}")
    print(f"Tabla etapa/escenario: {stage_out}")
    print(f"Tabla total escenario: {totals_out}")
    print(f"Graficos: {graphics_dir / 'ACV_impacto_calentamiento_global'}(.png/.pdf)")
    print(f"Gráficos EF 3.1 actualizados en: {graphics_dir}")
    print(
        f"Graficos: {graphics_dir / 'ACV_impacto_total_calentamiento_global_por_escenario'}(.png/.pdf)"
    )


if __name__ == "__main__":
    main()
