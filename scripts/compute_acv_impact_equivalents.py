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


def load_factors(path: Path) -> dict[str, dict[str, float]]:
    df = pd.read_csv(path)
    required = {"compuesto", "equivalente_co2", "equivalente_po4"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Faltan columnas en factores: {sorted(missing)}")

    out: dict[str, dict[str, float]] = {}
    for _, row in df.iterrows():
        compuesto = str(row["compuesto"]).strip().upper()
        if not compuesto:
            continue
        out[compuesto] = {
            "co2": float(row["equivalente_co2"]) if pd.notna(row["equivalente_co2"]) else 0.0,
            "po4": float(row["equivalente_po4"]) if pd.notna(row["equivalente_po4"]) else 0.0,
        }
    return out


def load_emissions(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in ["CO2_medido", "CH4_ec1"] + N2O_COLS + NH3_COLS + NO3_COLS:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    df["Escenario"] = df["Escenario"].astype(str).str.strip().str.upper()
    df["Etapa"] = pd.to_numeric(df["Etapa"], errors="coerce").fillna(0).astype(int)
    return df


def resolve_emissions_path(base: Path) -> Path:
    candidates = [
        base / "processed" / "ACV_resumen_emisiones.csv",
        base / "processed" / "ACV_resumen_emisiones_updated.csv",
        base / "ACV_resumen_emisiones" / "ACV_resumen_emisiones.csv",
        base / "ACV_resumen_emisiones" / "ACV_resumen_emisiones_updated.csv",
    ]
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def compute_impacts(df: pd.DataFrame, factors: dict[str, dict[str, float]]) -> pd.DataFrame:
    out = df.copy()
    out["n2o_total_kg"] = out[N2O_COLS].sum(axis=1)
    out["nh3_total_kg"] = out[NH3_COLS].sum(axis=1)
    out["no3_total_kg"] = out[NO3_COLS].sum(axis=1)
    out["co2_total_kg"] = out["CO2_medido"]
    out["ch4_total_kg"] = out["CH4_ec1"]

    f_ch4_co2 = factors.get("CH4", {}).get("co2", 0.0)
    f_n2o_co2 = factors.get("N2O", {}).get("co2", 0.0)
    f_co2_co2 = factors.get("CO2", {}).get("co2", 0.0)
    f_nh3_po4 = factors.get("NH3", {}).get("po4", 0.0)
    f_no3_po4 = factors.get("NO3", {}).get("po4", 0.0)

    out["impacto_calentamiento_global_kg_co2eq"] = (
        out["ch4_total_kg"] * f_ch4_co2
        + out["n2o_total_kg"] * f_n2o_co2
        + out["co2_total_kg"] * f_co2_co2
    )
    out["impacto_eutrofizacion_kg_po4eq"] = (
        out["nh3_total_kg"] * f_nh3_po4 + out["no3_total_kg"] * f_no3_po4
    )

    cols = [
        "Escenario",
        "Etapa",
        "ch4_total_kg",
        "n2o_total_kg",
        "co2_total_kg",
        "nh3_total_kg",
        "no3_total_kg",
        "impacto_calentamiento_global_kg_co2eq",
        "impacto_eutrofizacion_kg_po4eq",
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
    emissions_path = resolve_emissions_path(base)

    factors = load_factors(factors_path)
    emissions = load_emissions(emissions_path)
    impact_stage = compute_impacts(emissions, factors)

    stage_out = processed / "acv_impacto_por_etapa_escenario.csv"
    impact_stage.to_csv(stage_out, index=False, encoding="utf-8-sig")

    totals = (
        impact_stage.groupby("Escenario", as_index=False)[
            ["impacto_calentamiento_global_kg_co2eq", "impacto_eutrofizacion_kg_po4eq"]
        ]
        .sum()
        .sort_values("Escenario")
    )
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
        "impacto_eutrofizacion_kg_po4eq",
        r"Impacto de Eutrofizacion (PO$_4^{3-}$-eq) por Etapa y Escenario",
        r"kg PO$_4^{3-}$",
        graphics_dir / "ACV_impacto_eutrofizacion",
    )
    plot_total_by_scenario(
        totals,
        "impacto_calentamiento_global_kg_co2eq",
        r"Impacto Total de Calentamiento Global (CO$_2$-eq) por Escenario",
        r"kg CO$_2$",
        graphics_dir / "ACV_impacto_total_calentamiento_global_por_escenario",
    )
    plot_total_by_scenario(
        totals,
        "impacto_eutrofizacion_kg_po4eq",
        r"Impacto Total de Eutrofizacion (PO$_4^{3-}$-eq) por Escenario",
        r"kg PO$_4^{3-}$",
        graphics_dir / "ACV_impacto_total_eutrofizacion_por_escenario",
    )

    print(f"Factores: {factors_path}")
    print(f"Tabla etapa/escenario: {stage_out}")
    print(f"Tabla total escenario: {totals_out}")
    print(f"Graficos: {graphics_dir / 'ACV_impacto_calentamiento_global'}(.png/.pdf)")
    print(f"Graficos: {graphics_dir / 'ACV_impacto_eutrofizacion'}(.png/.pdf)")
    print(
        f"Graficos: {graphics_dir / 'ACV_impacto_total_calentamiento_global_por_escenario'}(.png/.pdf)"
    )
    print(f"Graficos: {graphics_dir / 'ACV_impacto_total_eutrofizacion_por_escenario'}(.png/.pdf)")


if __name__ == "__main__":
    main()
