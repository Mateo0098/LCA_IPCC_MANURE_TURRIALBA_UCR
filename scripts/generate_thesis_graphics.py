from __future__ import annotations

from pathlib import Path
from textwrap import fill

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from academic_text_utils import clean_academic_label


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
    text = clean_academic_label(value)
    wrapped_lines = []
    for line in text.splitlines() or [""]:
        line = line.strip()
        if not line:
            wrapped_lines.append("")
        else:
            wrapped_lines.append(fill(line, width=width, break_long_words=False))
    return "\n".join(wrapped_lines)


def stage_axis_label(row: pd.Series) -> str:
    code = f"{row['escenario']}{int(row['etapa'])}"
    name = str(row["nombre_etapa"])
    expected_prefix = f"Etapa {int(row['etapa'])}: "
    if name.startswith(expected_prefix):
        name = name[len(expected_prefix):]
    name = name.replace("Aplicación de aguas verdes en campos de pastoreo", "Aplicación de aguas verdes\nen campos de pastoreo")
    name = name.replace("Aplicación de purines en campo de pastoreo", "Aplicación de purines\nen campo de pastoreo")
    name = name.replace("Almacenamiento de purines", "Almacenamiento\nde purines")
    return f"{code}:\n{name}"


def formatted_labels(values, width: int) -> list[str]:
    return [clean_label(value, width=width) for value in values]


def label_line_count(label: str) -> int:
    return max(1, len(str(label).splitlines()))


def figure_size_for_labels(
    labels: list[str],
    base_width: float,
    base_height: float,
    per_label_width: float = 1.45,
) -> tuple[float, float]:
    max_lines = max((label_line_count(label) for label in labels), default=1)
    width = max(base_width, per_label_width * max(len(labels), 1))
    height = base_height + max(0, max_lines - 2) * 0.28
    return width, height


def apply_x_tick_labels(ax: plt.Axes, labels: list[str], rotation: float = 0) -> None:
    max_lines = max((label_line_count(label) for label in labels), default=1)
    fontsize = 8 if max_lines <= 3 else 7
    ax.set_xticklabels(labels, rotation=rotation, ha="center", fontsize=fontsize)
    ax.tick_params(axis="x", pad=6)


def tick_labels_overlap(fig: plt.Figure, ax: plt.Axes) -> bool:
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    labels = [label for label in ax.get_xticklabels() if label.get_visible() and label.get_text()]
    boxes = [label.get_window_extent(renderer=renderer).expanded(1.03, 1.0) for label in labels]
    return any(left.overlaps(right) for left, right in zip(boxes, boxes[1:]))


def resolve_x_tick_overlaps(fig: plt.Figure) -> None:
    for _ in range(3):
        fig.canvas.draw()
        overlapping_axes = [ax for ax in fig.axes if tick_labels_overlap(fig, ax)]
        if not overlapping_axes:
            return
        width, height = fig.get_size_inches()
        fig.set_size_inches(width * 1.12, height + 0.25, forward=True)
        for ax in overlapping_axes:
            for label in ax.get_xticklabels():
                label.set_rotation(25)
                label.set_ha("right")
                label.set_fontsize(7)
    fig.canvas.draw()


def finish_figure(fig: plt.Figure, filename: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    resolve_x_tick_overlaps(fig)
    fig.tight_layout()
    png_path = OUT_DIR / f"{filename}.png"
    svg_path = OUT_DIR / f"{filename}.svg"
    fig.savefig(png_path, bbox_inches="tight", dpi=300)
    fig.savefig(svg_path, bbox_inches="tight", dpi=300, metadata={"Date": None})
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n",
        encoding="utf-8",
    )
    plt.close(fig)


def grouped_bar(
    df: pd.DataFrame,
    x_col: str,
    group_col: str,
    value_col: str,
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
    x_labels = formatted_labels(pivot.index, x_width)
    fig, ax = plt.subplots(figsize=figure_size_for_labels(x_labels, base_width=7, base_height=4.9))
    x = np.arange(len(pivot.index))
    groups = list(pivot.columns)
    width = min(0.8 / max(len(groups), 1), 0.36)
    offsets = (np.arange(len(groups)) - (len(groups) - 1) / 2) * width

    for i, (offset, group) in enumerate(zip(offsets, groups)):
        style = style_for(group, i)
        legend_label = clean_academic_label(
            f"{group_label_prefix} {group}" if group_label_prefix else group
        )
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

    ax.set_ylabel(clean_academic_label(ylabel))
    ax.set_xticks(x)
    apply_x_tick_labels(ax, x_labels)
    ax.legend(frameon=False)
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.7)
    ax.set_axisbelow(True)
    finish_figure(fig, filename)


def simple_bar(
    df: pd.DataFrame,
    x_col: str,
    value_col: str,
    ylabel: str,
    filename: str,
    color_col: str | None = None,
    x_width: int = 24,
    figsize: tuple[float, float] | None = None,
    bottom_margin: float | None = None,
) -> None:
    x_labels = formatted_labels(df[x_col], x_width)
    fig_size = figsize or figure_size_for_labels(x_labels, base_width=6.5, base_height=4.7)
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

    ax.set_ylabel(clean_academic_label(ylabel))
    ax.set_xticks(x)
    apply_x_tick_labels(ax, x_labels)
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.7)
    ax.set_axisbelow(True)
    if bottom_margin is not None:
        fig.subplots_adjust(bottom=bottom_margin)
    finish_figure(fig, filename)


def characterization_series(df: pd.DataFrame, variables: list[str]) -> pd.DataFrame:
    """Selecciona y valida los valores numéricos que alimentan una figura de caracterización."""
    subset = df[df["variable"].isin(variables)].copy()
    subset["valor"] = pd.to_numeric(subset["valor"], errors="coerce")
    subset = subset.dropna(subset=["valor"])
    missing = [variable for variable in variables if subset[subset["variable"] == variable].empty]
    if missing:
        raise ValueError(f"Series de caracterización vacías en tabla_02: {missing}")
    if subset.empty:
        raise ValueError("No existen datos numéricos para la figura de caracterización")
    return subset


def plot_sample_characterization(readme: list[dict[str, str]]) -> None:
    df = read_table("muestras")

    specs = [
        (
            ["Humedad", "Materia seca"],
            "% masa humeda",
            "Porcentaje de masa humeda (%)",
            "fig_01_caracterizacion_humedad_materia_seca",
            "Compara humedad y materia seca promedio por tipo de muestra.",
        ),
        (
            ["Solidos volatiles", "Cenizas"],
            "% base seca",
            "Porcentaje en base seca (%)",
            "fig_02_caracterizacion_solidos_volatiles_cenizas",
            "Compara solidos volatiles y cenizas por tipo de muestra.",
        ),
        (
            ["Nitrogeno total"],
            "% N total",
            "Nitrogeno total (%)",
            "fig_03_caracterizacion_nitrogeno_total",
            "Presenta nitrogeno total promedio por tipo de muestra.",
        ),
    ]

    for variables, unit, ylabel, filename, description in specs:
        subset = characterization_series(df, variables)
        grouped_bar(
            subset,
            x_col="tipo_muestra",
            group_col="variable",
            value_col="valor",
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
    mass["etiqueta_etapa"] = mass.apply(stage_axis_label, axis=1)
    simple_bar(
        mass.sort_values(["escenario", "etapa"]),
        x_col="etiqueta_etapa",
        value_col="valor",
        ylabel="Masa equivalente total (kg eq/año)",
        filename="fig_04_flujos_masa_equivalente_total",
        color_col="escenario",
        x_width=30,
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
    stage_labels = formatted_labels(
        components.drop_duplicates(["escenario", "etapa"]).sort_values(["escenario", "etapa"]).apply(stage_axis_label, axis=1),
        30,
    )
    fig_width, _ = figure_size_for_labels(stage_labels, base_width=11.5, base_height=4.2, per_label_width=1.55)
    fig, axes = plt.subplots(
        len(units), 1, figsize=(fig_width, 4.4 * len(units)), sharex=False, squeeze=False
    )
    for ax, unit in zip(axes.ravel(), units):
        subset = components[components["unidad"] == unit].copy()
        subset["etiqueta_etapa"] = subset.apply(stage_axis_label, axis=1)
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
        ax.set_ylabel(clean_academic_label(unit))
        ax.set_xticks(x)
        apply_x_tick_labels(ax, formatted_labels(pivot.index, 30))
        ax.grid(axis="y", color="#d9d9d9", linewidth=0.7)
        ax.set_axisbelow(True)
        ax.legend(frameon=False)
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
    for i, substance in enumerate(order, start=6):
        subset = df[df["sustancia"] == substance].copy()
        if subset.empty:
            if substance != "CO2":
                continue
            subset = (
                df[["escenario", "etapa", "nombre_etapa"]]
                .drop_duplicates()
                .assign(unidad="kg CO2/año", valor=0.0)
            )
        grouped = (
            subset.groupby(["escenario", "etapa", "nombre_etapa", "unidad"], as_index=False)["valor"]
            .sum()
            .sort_values(["escenario", "etapa"])
        )
        grouped["etiqueta_etapa"] = grouped.apply(stage_axis_label, axis=1)
        unit = grouped["unidad"].iloc[0]
        filename = f"fig_{i:02d}_emisiones_{substance.lower()}"
        grouped_bar(
            grouped,
            x_col="etiqueta_etapa",
            group_col="escenario",
            value_col="valor",
            ylabel=unit,
            filename=filename,
            x_width=30,
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
        ("Cambio climático", "fig_11_impactos_cambio_climatico_etapa"),
        ("Eutrofización terrestre", "fig_12_impactos_eutrofizacion_terrestre_etapa"),
        ("Eutrofización marina", "fig_13_impactos_eutrofizacion_marina_etapa"),
    ]
    for category, filename in specs:
        subset = df[df["categoria_impacto"] == category].copy()
        grouped = (
            subset.groupby(["escenario", "etapa", "nombre_etapa", "unidad_equivalente"], as_index=False)[
                "resultado_equivalente"
            ]
            .sum()
            .sort_values(["escenario", "etapa"])
        )
        grouped["etiqueta_etapa"] = grouped.apply(stage_axis_label, axis=1)
        unit = grouped["unidad_equivalente"].iloc[0]
        grouped_bar(
            grouped,
            x_col="etiqueta_etapa",
            group_col="escenario",
            value_col="resultado_equivalente",
            ylabel=unit,
            filename=filename,
            x_width=30,
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
            "Cambio climático",
            "fig_14_comparacion_total_cambio_climatico",
            "Resultados: comparacion de escenarios",
        ),
        (
            "Eutrofización terrestre",
            "fig_15_comparacion_total_eutrofizacion_terrestre",
            "Resultados: comparacion de escenarios",
        ),
        (
            "Eutrofización marina",
            "fig_16_comparacion_total_eutrofizacion_marina",
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
        ylabel="Diferencia B respecto a A (%)",
        filename="fig_17_comparacion_diferencia_porcentual",
        x_width=18,
    )
    readme.append(
        {
            "archivo": "fig_17_comparacion_diferencia_porcentual",
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
        "Todos los graficos fueron generados exclusivamente a partir de las tablas finales validadas en `outputs/tablas_tesis/` indicadas en cada registro.",
        "Las imagenes no incluyen titulos internos; el titulo formal se incorpora como caption en los documentos Word.",
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


def main(output_dir: Path | None = None, table_dir: Path | None = None) -> None:
    global OUT_DIR, TABLE_DIR
    original_output_dir = OUT_DIR
    original_table_dir = TABLE_DIR
    if output_dir is not None:
        OUT_DIR = Path(output_dir)
    if table_dir is not None:
        TABLE_DIR = Path(table_dir)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "xtick.labelsize": 8,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "svg.fonttype": "none",
            "svg.hashsalt": "tfg-acv-provisional-m1-m2",
        }
    )

    try:
        readme_rows: list[dict[str, str]] = []
        plot_sample_characterization(readme_rows)
        plot_inventory_flows(readme_rows)
        plot_emissions(readme_rows)
        plot_impacts_by_stage(readme_rows)
        plot_scenario_comparison(readme_rows)
        write_readme(readme_rows)
    finally:
        OUT_DIR = original_output_dir
        TABLE_DIR = original_table_dir


if __name__ == "__main__":
    main()
