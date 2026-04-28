"""Graficos de barras de emisiones ACV: comparacion Escenarios A y B por etapa."""

from __future__ import annotations

import os
from typing import Iterable

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import numpy as np
import pandas as pd


EMISSION_COLS = [
    "CO2_medido",
    "CH4_ec1",
    "N2O_ec14",
    "N2O_ec2",
    "N2O_ec5",
    "N2O_ec6",
    "N2O_ec16",
    "N2O_ec18",
    "NH3_ec12",
    "NH3_ec20",
    "NO3_ec13",
    "NO3_ec21",
]
ETAPAS = [1, 2, 3, 4]
ESCENARIOS = ["A", "B"]
DISPLAY_ETAPAS = [1, 2, 3, 4]
DISPLAY_LABELS = {
    1: "1",
    2: "2",
    3: "3",
    4: "4",
}
DISPLAY_MAP = {
    ("A", 1): 1,
    ("A", 2): 2,
    ("A", 3): 3,
    ("A", 4): 4,
    ("B", 1): 1,
    ("B", 2): 2,
}
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


def pretty_number(value: float) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.2f}k"
    return f"{value:.2f}"


def y_axis_formatter(value: float, _pos: float) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.0f}k"
    return f"{value:.0f}"


def resolve_csv_path(project_dir: str) -> str:
    candidates = [
        os.path.join(project_dir, "processed", "ACV_resumen_emisiones.csv"),
        os.path.join(project_dir, "processed", "ACV_resumen_emisiones_updated.csv"),
        os.path.join(project_dir, "ACV_resumen_emisiones", "ACV_resumen_emisiones.csv"),
        os.path.join(project_dir, "ACV_resumen_emisiones", "ACV_resumen_emisiones_updated.csv"),
        os.path.join(project_dir, "ACV_resumen_emisiones.csv"),
        os.path.join(project_dir, "Academic_documents", "ACV_resumen_emisiones.csv"),
    ]
    found = next((p for p in candidates if os.path.exists(p)), None)
    if found is None:
        raise FileNotFoundError(
            "No se encontro ACV_resumen_emisiones.csv en rutas esperadas: " f"{candidates}"
        )
    return found


def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    for col in EMISSION_COLS:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df[EMISSION_COLS] = df[EMISSION_COLS].fillna(0.0)
    df["Escenario"] = df["Escenario"].astype(str).str.strip().str.upper()
    df["Etapa"] = pd.to_numeric(df["Etapa"], errors="coerce")
    df = df.dropna(subset=["Etapa"])
    df["Etapa"] = df["Etapa"].astype(int)
    return df


def build_plot_frame(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    cols = list(columns)
    data = df.copy()
    if len(cols) > 1:
        data["valor"] = data[cols].sum(axis=1)
    else:
        data["valor"] = data[cols[0]]

    data["Etapa_display"] = data.apply(
        lambda r: DISPLAY_MAP.get((str(r["Escenario"]), int(r["Etapa"])), int(r["Etapa"])),
        axis=1,
    )
    grouped = (
        data.groupby(["Escenario", "Etapa_display"], as_index=False)["valor"]
        .sum()
        .rename(columns={"valor": "Emision"})
    )

    full_index = pd.MultiIndex.from_product(
        [ESCENARIOS, DISPLAY_ETAPAS], names=["Escenario", "Etapa_display"]
    )
    grouped = (
        grouped.set_index(["Escenario", "Etapa_display"])
        .reindex(full_index, fill_value=0.0)
        .reset_index()
    )
    grouped["Escenario"] = pd.Categorical(grouped["Escenario"], ESCENARIOS, ordered=True)
    grouped["Etapa_display"] = pd.Categorical(
        grouped["Etapa_display"], DISPLAY_ETAPAS, ordered=True
    )
    grouped["Etapa_label"] = grouped["Etapa_display"].astype(int).map(DISPLAY_LABELS)
    return grouped


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


def plot_emission_bars(
    df_plot: pd.DataFrame, title: str, ylabel: str, filename_base: str, out_dir: str
) -> None:
    fig, ax = plt.subplots(figsize=(9.0, 5.4))
    fig.patch.set_facecolor(FIG_BG)
    ax.set_facecolor(AX_BG)
    x = np.arange(len(DISPLAY_ETAPAS))
    width = 0.36
    vals_a = df_plot[df_plot["Escenario"] == "A"]["Emision"].to_numpy()
    vals_b = df_plot[df_plot["Escenario"] == "B"]["Emision"].to_numpy()
    ax.bar(
        x - width / 2,
        vals_a,
        width,
        label="A",
        color=PALETTE["A"],
        edgecolor=BAR_EDGE_COLOR,
        linewidth=0.8,
    )
    ax.bar(
        x + width / 2,
        vals_b,
        width,
        label="B",
        color=PALETTE["B"],
        edgecolor=BAR_EDGE_COLOR,
        linewidth=0.8,
    )
    ax.set_xticks(x)
    ax.set_xticklabels([DISPLAY_LABELS[e] for e in DISPLAY_ETAPAS])

    ax.set_title(title, pad=12)
    ax.set_xlabel("Etapa")
    ax.set_ylabel(ylabel)
    ax.legend(title="Escenario", ncol=2, loc="upper right")
    ax.grid(axis="y")
    ax.grid(axis="x", visible=False)
    ax.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))

    ymax = float(df_plot["Emision"].max()) if not df_plot.empty else 0.0
    ax.set_ylim(0, ymax * 1.22 if ymax > 0 else 1.0)
    annotate_bars(ax)

    fig.tight_layout()
    for ext in ("png", "pdf"):
        path = os.path.join(out_dir, f"{filename_base}.{ext}")
        fig.savefig(path, dpi=300 if ext == "png" else None, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    configure_style()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(script_dir)
    out_dir = os.path.join(project_dir, "graphics_results")
    os.makedirs(out_dir, exist_ok=True)
    csv_path = resolve_csv_path(project_dir)
    df = load_data(csv_path)
    print("Motor de graficos: matplotlib")

    plot_emission_bars(
        build_plot_frame(df, ["CO2_medido"]),
        title=r"CO$_2$ Emissions by Stage and Scenario",
        ylabel=r"CO$_2$ (kg yr$^{-1}$)",
        filename_base="ACV_emisiones_CO2",
        out_dir=out_dir,
    )
    plot_emission_bars(
        build_plot_frame(df, ["CH4_ec1"]),
        title=r"CH$_4$ Emissions by Stage and Scenario",
        ylabel=r"CH$_4$ (kg yr$^{-1}$)",
        filename_base="ACV_emisiones_CH4",
        out_dir=out_dir,
    )
    plot_emission_bars(
        build_plot_frame(df, ["N2O_ec14", "N2O_ec2", "N2O_ec5", "N2O_ec6", "N2O_ec16", "N2O_ec18"]),
        title=r"N$_2$O Emissions by Stage and Scenario",
        ylabel=r"N$_2$O (kg yr$^{-1}$)",
        filename_base="ACV_emisiones_N2O",
        out_dir=out_dir,
    )
    plot_emission_bars(
        build_plot_frame(df, ["NH3_ec12", "NH3_ec20"]),
        title=r"NH$_3$ Emissions by Stage and Scenario",
        ylabel=r"NH$_3$ (kg yr$^{-1}$)",
        filename_base="ACV_emisiones_NH3",
        out_dir=out_dir,
    )
    plot_emission_bars(
        build_plot_frame(df, ["NO3_ec13", "NO3_ec21"]),
        title=r"NO$_3^-$ Emissions by Stage and Scenario",
        ylabel=r"NO$_3^-$ (kg yr$^{-1}$)",
        filename_base="ACV_emisiones_NO3",
        out_dir=out_dir,
    )

    print("Graficos guardados en:", out_dir)
    print("  ACV_emisiones_CO2.pdf / .png")
    print("  ACV_emisiones_CH4.pdf / .png")
    print("  ACV_emisiones_N2O.pdf / .png")
    print("  ACV_emisiones_NH3.pdf / .png")
    print("  ACV_emisiones_NO3.pdf / .png")


if __name__ == "__main__":
    main()
