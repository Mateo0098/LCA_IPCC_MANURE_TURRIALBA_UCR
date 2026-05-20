from __future__ import annotations

from pathlib import Path
from textwrap import fill

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
TABLE_DIR = BASE_DIR / "outputs" / "tablas_tesis"
OUT_DIR = BASE_DIR / "outputs" / "graficos_tesis"

TABLES = {
    "muestras": "tabla_02_caracterizacion_muestras.csv",
    "flujos": "tabla_03_flujos_icv.csv",
    "emisiones": "tabla_06_emisiones_por_etapa.csv",
    "impactos_etapa": "tabla_07_impactos_por_etapa.csv",
    "impactos_totales": "tabla_08_impactos_totales_por_escenario.csv",
    "comparacion": "tabla_09_comparacion_escenarios.csv",
}

STYLES = {
    "A": {"color": "#4d4d4d", "hatch": ""},
    "B": {"color": "#bdbdbd", "hatch": "///"},
}

STYLE_SEQUENCE = [
    {"color": "#404040", "hatch": ""},
    {"color": "#bdbdbd", "hatch": "///"},
    {"color": "#f0f0f0", "hatch": "..."},
    {"color": "#808080", "hatch": "\\\\\\"},
    {"color": "#d9d9d9", "hatch": "xxx"},
]


def read_table(name: str) -> pd.DataFrame:
    return pd.read_csv(TABLE_DIR / TABLES[name])


def style_for(value: object, index: int = 0) -> dict[str, str]:
    return STYLES.get(str(value), STYLE_SEQUENCE[index % len(STYLE_SEQUENCE)])


def clean_label(value: object, width: int = 24) -> str:
    text = str(value)
    return fill(text, width=width, break_long_words=False)


def finish_figure(fig: plt.Figure, filename: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "svg"):
        fig.savefig(OUT_DIR / f"{filename}.{ext}", bbox_inches="tight", dpi=300)
    plt.close(fig)


def grouped_bar(
    df: pd.DataFrame,
    x_col: str,
    group_col: str,
    value_col: str,
    title: str,
    ylabel: str,
    filename: str,
    x_width: int = 24,
    group_label_prefix: str | None = None,
) -> None:
    pivot = (
        df.pivot_table(index=x_col, columns=group_col, values=value_col, aggfunc="sum")
        .fillna(0)
        .sort_index()
    )
    fig, ax = plt.subplots(figsize=(max(7, 1.25 * len(pivot)), 4.8))
    x = np.arange(len(pivot.index))
    groups = list(pivot.columns)
    width = min(0.8 / max(len(groups), 1), 0.36)
    offsets = (np.arange(len(groups)) - (len(groups) - 1) / 2) * width

    for i, (offset, group) in enumerate(zip(offsets, groups)):
        style = style_for(group, i)
        legend_label = f"{group_label_prefix} {group}" if group_label_prefix else str(group)
        ax.bar(
            x + offset,
            pivot[group].values,
            width=width,
            label=legend_label,
            color=style["color"],
            edgecolor="black",
            linewidth=0.6,
            hatch=style["hatch"],
        )

    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xticks(x)
    ax.set_xticklabels([clean_label(v, x_width) for v in pivot.index], rotation=0)
    ax.legend(frameon=False)
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.7)
    ax.set_axisbelow(True)
    fig.tight_layout()
    finish_figure(fig, filename)


def simple_bar(
    df: pd.DataFrame,
    x_col: str,
    value_col: str,
    title: str,
    ylabel: str,
    filename: str,
    color_col: str | None = None,
    x_width: int = 24,
    figsize: tuple[float, float] | None = None,
    bottom_margin: float | None = None,
) -> None:
    fig_size = figsize or (max(6.5, 1.4 * len(df)), 4.6)
    fig, ax = plt.subplots(figsize=fig_size)
    x = np.arange(len(df))
    if color_col:
        styles = [style_for(v, i) for i, v in enumerate(df[color_col])]
    else:
        styles = [style_for(v, i) for i, v in enumerate(df[x_col])]
    colors = [style["color"] for style in styles]
    hatches = [style["hatch"] for style in styles]

    bars = ax.bar(x, df[value_col], color=colors, edgecolor="black", linewidth=0.6)
    for bar, hatch in zip(bars, hatches):
        bar.set_hatch(hatch)

    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xticks(x)
    ax.set_xticklabels([clean_label(v, x_width) for v in df[x_col]], rotation=0)
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.7)
    ax.set_axisbelow(True)
    fig.tight_layout()
    if bottom_margin is not None:
        fig.subplots_adjust(bottom=bottom_margin)
    finish_figure(fig, filename)


def plot_sample_characterization(readme: list[dict[str, str]]) -> None:
    df = read_table("muestras")

    specs = [
        (
            ["Humedad", "Materia seca"],
            "% masa humeda",
            "Caracterizacion de muestras: humedad y materia seca",
            "Porcentaje de masa humeda (%)",
            "fig_01_caracterizacion_humedad_materia_seca",
            "Compara humedad y materia seca promedio por tipo de muestra.",
        ),
        (
            ["Solidos volatiles", "Cenizas"],
            "% base seca",
            "Caracterizacion de muestras: solidos volatiles y cenizas",
            "Porcentaje en base seca (%)",
            "fig_02_caracterizacion_solidos_volatiles_cenizas",
            "Compara solidos volatiles y cenizas por tipo de muestra.",
        ),
        (
            ["Nitrogeno total"],
            "% N total",
            "Caracterizacion de muestras: nitrogeno total",
            "Nitrogeno total (%)",
            "fig_03_caracterizacion_nitrogeno_total",
            "Presenta nitrogeno total promedio por tipo de muestra.",
        ),
    ]

    for variables, unit, title, ylabel, filename, description in specs:
        subset = df[df["variable"].isin(variables) & (df["unidad"] == unit)].copy()
        grouped_bar(
            subset,
            x_col="tipo_muestra",
            group_col="variable",
            value_col="valor",
            title=title,
            ylabel=ylabel,
            filename=filename,
            x_width=18,
        )
        readme.append(
            {
                "archivo": filename,
                "tabla": TABLES["muestras"],
                "muestra": description,
                "seccion": "Resultados: caracterizacion fisicoquimica de muestras",
                "apendice": "Apendice de caracterizacion de muestras",
            }
        )


def plot_inventory_flows(readme: list[dict[str, str]]) -> None:
    df = read_table("flujos")
    mass = df[df["flujo"] == "Masa equivalente total"].copy()
    mass["etiqueta_etapa"] = mass["escenario"] + ": " + mass["nombre_etapa"]
    simple_bar(
        mass.sort_values(["escenario", "etapa"]),
        x_col="etiqueta_etapa",
        value_col="valor",
        title="Inventario: masa equivalente total por escenario y etapa",
        ylabel="Masa equivalente total (kg eq/ano)",
        filename="fig_04_flujos_masa_equivalente_total",
        color_col="escenario",
        x_width=16,
        figsize=(11.5, 6.2),
        bottom_margin=0.34,
    )
    readme.append(
        {
            "archivo": "fig_04_flujos_masa_equivalente_total",
            "tabla": TABLES["flujos"],
            "muestra": "Masa equivalente total para cada etapa y escenario.",
            "seccion": "Resultados: inventario de ciclo de vida",
            "apendice": "Apendice de flujos del inventario",
        }
    )

    components = df[
        ~df["flujo"].isin(["Masa equivalente total", "Factor restante fresco a precompostado"])
    ].copy()
    units = list(components["unidad"].dropna().unique())
    fig, axes = plt.subplots(
        len(units), 1, figsize=(9, 3.8 * len(units)), sharex=False, squeeze=False
    )
    for ax, unit in zip(axes.ravel(), units):
        subset = components[components["unidad"] == unit].copy()
        subset["etiqueta_etapa"] = subset["escenario"] + ": " + subset["nombre_etapa"]
        pivot = (
            subset.pivot_table(
                index="etiqueta_etapa", columns="flujo", values="valor", aggfunc="sum"
            )
            .fillna(0)
            .sort_index()
        )
        bottom = np.zeros(len(pivot))
        colors = ["#595959", "#bdbdbd", "#f0f0f0"]
        hatches = ["", "///", "..."]
        x = np.arange(len(pivot))
        for i, col in enumerate(pivot.columns):
            ax.bar(
                x,
                pivot[col],
                bottom=bottom,
                label=col,
                color=colors[i % len(colors)],
                edgecolor="black",
                linewidth=0.6,
                hatch=hatches[i % len(hatches)],
            )
            bottom += pivot[col].values
        ax.set_title(f"Componentes del inventario ({unit})")
        ax.set_ylabel(unit)
        ax.set_xticks(x)
        ax.set_xticklabels([clean_label(v, 24) for v in pivot.index], rotation=0)
        ax.grid(axis="y", color="#d9d9d9", linewidth=0.7)
        ax.set_axisbelow(True)
        ax.legend(frameon=False)
    fig.suptitle("Inventario: distribucion de flujos por etapa", y=1.01)
    fig.tight_layout()
    finish_figure(fig, "fig_05_flujos_distribucion_componentes")
    readme.append(
        {
            "archivo": "fig_05_flujos_distribucion_componentes",
            "tabla": TABLES["flujos"],
            "muestra": "Distribucion de componentes del inventario por etapa, separada por unidad.",
            "seccion": "Resultados: inventario de ciclo de vida",
            "apendice": "Apendice de flujos del inventario",
        }
    )


def plot_emissions(readme: list[dict[str, str]]) -> None:
    df = read_table("emisiones")
    order = ["CH4", "N2O", "NH3", "NO3", "CO2"]
    names = {
        "CH4": "metano",
        "N2O": "oxido nitroso",
        "NH3": "amoniaco",
        "NO3": "nitrato",
        "CO2": "dioxido de carbono",
    }
    for i, substance in enumerate(order, start=6):
        subset = df[df["sustancia"] == substance].copy()
        if subset.empty:
            continue
        grouped = (
            subset.groupby(["nombre_etapa", "escenario", "unidad"], as_index=False)["valor"]
            .sum()
            .sort_values(["nombre_etapa", "escenario"])
        )
        unit = grouped["unidad"].iloc[0]
        filename = f"fig_{i:02d}_emisiones_{substance.lower()}"
        grouped_bar(
            grouped,
            x_col="nombre_etapa",
            group_col="escenario",
            value_col="valor",
            title=f"Emisiones de {names[substance]} por etapa y escenario",
            ylabel=unit,
            filename=filename,
            x_width=24,
            group_label_prefix="Escenario",
        )
        readme.append(
            {
                "archivo": filename,
                "tabla": TABLES["emisiones"],
                "muestra": f"Emisiones anuales de {substance} por etapa y escenario.",
                "seccion": "Resultados: emisiones por etapa",
                "apendice": "Apendice de emisiones",
            }
        )


def plot_impacts_by_stage(readme: list[dict[str, str]]) -> None:
    df = read_table("impactos_etapa")
    specs = [
        ("Calentamiento global", "fig_11_impactos_calentamiento_global_etapa"),
        ("Eutrofizacion", "fig_12_impactos_eutrofizacion_etapa"),
    ]
    for category, filename in specs:
        subset = df[df["categoria_impacto"] == category].copy()
        grouped = (
            subset.groupby(["nombre_etapa", "escenario", "unidad_equivalente"], as_index=False)[
                "resultado_equivalente"
            ]
            .sum()
            .sort_values(["nombre_etapa", "escenario"])
        )
        unit = grouped["unidad_equivalente"].iloc[0]
        grouped_bar(
            grouped,
            x_col="nombre_etapa",
            group_col="escenario",
            value_col="resultado_equivalente",
            title=f"{category} por etapa y escenario",
            ylabel=unit,
            filename=filename,
            x_width=24,
            group_label_prefix="Escenario",
        )
        readme.append(
            {
                "archivo": filename,
                "tabla": TABLES["impactos_etapa"],
                "muestra": f"Impacto de {category.lower()} agregado por etapa y escenario.",
                "seccion": "Resultados: impactos ambientales por etapa",
                "apendice": "Apendice de impactos ambientales",
            }
        )


def plot_scenario_comparison(readme: list[dict[str, str]]) -> None:
    totals = read_table("impactos_totales")
    comparisons = read_table("comparacion")
    specs = [
        (
            "Calentamiento global",
            "fig_13_comparacion_total_calentamiento_global",
            "Resultados: comparacion de escenarios",
        ),
        (
            "Eutrofizacion",
            "fig_14_comparacion_total_eutrofizacion",
            "Resultados: comparacion de escenarios",
        ),
    ]
    for category, filename, section in specs:
        subset = totals[totals["categoria_impacto"] == category].copy()
        unit = subset["unidad"].iloc[0]
        subset["escenario_label"] = "Escenario " + subset["escenario"].astype(str)
        simple_bar(
            subset.sort_values("escenario"),
            x_col="escenario_label",
            value_col="resultado_total",
            title=f"Impacto total de {category.lower()}: escenarios A y B",
            ylabel=unit,
            filename=filename,
            color_col="escenario",
            x_width=16,
        )
        readme.append(
            {
                "archivo": filename,
                "tabla": TABLES["impactos_totales"],
                "muestra": f"Comparacion del impacto total de {category.lower()} entre A y B.",
                "seccion": section,
                "apendice": "Apendice de comparacion de escenarios",
            }
        )

    pct = comparisons.copy()
    simple_bar(
        pct,
        x_col="categoria_impacto",
        value_col="diferencia_porcentual_B_vs_A",
        title="Diferencia porcentual del escenario B respecto al A",
        ylabel="Diferencia B respecto a A (%)",
        filename="fig_15_comparacion_diferencia_porcentual",
        x_width=18,
    )
    readme.append(
        {
            "archivo": "fig_15_comparacion_diferencia_porcentual",
            "tabla": TABLES["comparacion"],
            "muestra": "Diferencia porcentual del escenario B respecto al A por categoria de impacto.",
            "seccion": "Resultados: comparacion de escenarios",
            "apendice": "Apendice de comparacion de escenarios",
        }
    )


def write_readme(rows: list[dict[str, str]]) -> None:
    lines = [
        "# Graficos finales para tesis",
        "",
        "Todos los graficos fueron generados exclusivamente a partir de las tablas finales validadas en `outputs/tablas_tesis/` indicadas en cada registro. No se usaron archivos con sufijo `antes_correccion_nitrogeno` ni tablas intermedias.",
        "",
        "| Archivo | Tabla fuente | Que muestra | Seccion recomendada | Apendice relacionado |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        png = f"{row['archivo']}.png"
        svg = f"{row['archivo']}.svg"
        lines.append(
            f"| `{png}` / `{svg}` | `{row['tabla']}` | {row['muestra']} | {row['seccion']} | {row['apendice']} |"
        )
    (OUT_DIR / "README_GRAFICOS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "xtick.labelsize": 8,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "svg.fonttype": "none",
        }
    )

    readme_rows: list[dict[str, str]] = []
    plot_sample_characterization(readme_rows)
    plot_inventory_flows(readme_rows)
    plot_emissions(readme_rows)
    plot_impacts_by_stage(readme_rows)
    plot_scenario_comparison(readme_rows)
    write_readme(readme_rows)


if __name__ == "__main__":
    main()
