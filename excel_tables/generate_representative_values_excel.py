from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


ROOT_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = ROOT_DIR / "processed"
DEFAULT_OUTPUT = Path(__file__).resolve().parent / "tablas_valores_representativos_para_docx_acentos_corregidos.xlsx"

SAMPLE_TYPE_ES = {
    "Fresh manure": "Estiércol fresco",
    "Precomposted manure": "Estiércol precompostado",
}

TREATMENT_LABELS = {
    "A": "A - estiércol fresco",
    "B": "B - estiércol precompostado",
}

N_TREATMENT_ES = {
    "ESTIERCOL FRESCO": "Estiércol fresco",
    "LIQ: AGUA VERDE": "Líquido: agua verde",
    "LIQ: PURINES": "Líquido: purines",
    "SOL: PRECOMPOSTADO": "Sólido precompostado",
}


def read_csv(name: str) -> list[dict[str, str]]:
    path = PROCESSED_DIR / name
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def fmt_date(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    for pattern in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, pattern).strftime("%d/%m/%Y")
        except ValueError:
            continue
    return value


def number(value: str, digits: int = 3) -> float | int | str:
    value = value.strip()
    if not value:
        return ""
    parsed = round(float(value), digits)
    return int(parsed) if parsed.is_integer() else parsed


def add_rows(ws, rows: list[list[Any]], title_rows: set[int] | None = None, header_rows: set[int] | None = None) -> None:
    title_rows = title_rows or set()
    header_rows = header_rows or set()
    header_fill = PatternFill("solid", fgColor="D9EAF7")

    for row_index, row in enumerate(rows, start=1):
        ws.append(row)
        for cell in ws[row_index]:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            if row_index in title_rows:
                cell.font = Font(bold=True, size=12)
            if row_index in header_rows:
                cell.font = Font(bold=True)
                cell.fill = header_fill


def autofit(ws) -> None:
    for column_cells in ws.columns:
        max_length = 0
        column = get_column_letter(column_cells[0].column)
        for cell in column_cells:
            value = "" if cell.value is None else str(cell.value)
            max_length = max(max_length, len(value))
        ws.column_dimensions[column].width = min(max(max_length + 2, 12), 34)


def build_workbook() -> Workbook:
    solids_by_sample = read_csv("volatile_solids_representative_table.csv")
    solids_by_treatment = read_csv("volatile_solids_treatment_table.csv")
    nitrogen_samples = read_csv("CIA_samples_table_v6.csv")
    nitrogen_summary = read_csv("CIA_samples_table_v6_treatment_summary.csv")

    nitrogen_by_treatment = {row["treatment"]: row for row in nitrogen_summary}

    wb = Workbook()
    ws_docx = wb.active
    ws_docx.title = "Tablas para docx"

    table_1_header = [
        "Muestra",
        "Tipo de muestra",
        "Fecha de análisis de sólidos",
        "Número de muestras de sólidos (n)",
        "Contenido de masa seca promedio (% base húmeda)",
        "Desviación estándar de masa seca (%)",
        "Sólidos volátiles promedio (% base seca)",
        "Desviación estándar de sólidos volátiles (%)",
        "Fecha de análisis de nitrógeno",
        "Número de muestras de nitrógeno (n)",
        "Nitrógeno total promedio (% masa)",
        "Nitrógeno total promedio (mg/kg)",
    ]
    nitrogen_lookup = {
        "A": nitrogen_by_treatment["ESTIERCOL FRESCO"],
        "B": nitrogen_by_treatment["SOL: PRECOMPOSTADO"],
    }
    table_1 = [["Tabla 1. Valores representativos por tipo de muestra sólida"], table_1_header]
    for row in solids_by_treatment:
        treatment = row["treatment"]
        n_row = nitrogen_lookup[treatment]
        table_1.append(
            [
                TREATMENT_LABELS[treatment],
                SAMPLE_TYPE_ES[row["sample_type"]],
                fmt_date(row["sampling_date"]),
                number(row["sample_count"], 0),
                number(row["dry_matter_treatment_mean_pct"]),
                number(row["dry_matter_treatment_sd_pct"]),
                number(row["volatile_solids_treatment_mean_pct"]),
                number(row["volatile_solids_treatment_sd_pct"]),
                fmt_date(n_row["date"]),
                number(n_row["n_samples"], 0),
                number(n_row["mean_n_percentage"]),
                number(n_row["mean_n_total_mg_kg"]),
            ]
        )

    table_2_header = [
        "Muestra",
        "Fecha de análisis",
        "Número de réplicas (n)",
        "Contenido de masa seca promedio (% base húmeda)",
        "Desviación estándar de masa seca (%)",
        "Coeficiente de variación de masa seca (%)",
        "Sólidos volátiles promedio (% base seca)",
        "Desviación estándar de sólidos volátiles (%)",
        "Coeficiente de variación de sólidos volátiles (%)",
    ]
    table_2 = [[], [], ["Tabla 2. Contenido de masa seca y sólidos volátiles por muestra"], table_2_header]
    for row in solids_by_sample:
        sample_type = SAMPLE_TYPE_ES[row["sample_type"]]
        table_2.append(
            [
                f"{row['sample_group']} - {sample_type}",
                fmt_date(row["sampling_date"]),
                number(row["replicate_count"], 0),
                number(row["dry_matter_mean_pct"]),
                number(row["dry_matter_sd_pct"]),
                number(row["dry_matter_cv_pct"]),
                number(row["volatile_solids_mean_pct"]),
                number(row["volatile_solids_sd_pct"]),
                number(row["volatile_solids_cv_pct"]),
            ]
        )

    table_3_header = [
        "Muestra o tratamiento",
        "Fecha de análisis",
        "Número de muestras (n)",
        "Nitrógeno total promedio (% masa)",
        "Nitrógeno total promedio (mg/kg)",
        "Mediana de nitrógeno total (% masa)",
        "Mediana de nitrógeno total (mg/kg)",
        "Valor mínimo de nitrógeno total (mg/kg)",
        "Valor máximo de nitrógeno total (mg/kg)",
    ]
    table_3 = [[], [], ["Tabla 3. Nitrógeno total representativo por muestra o tratamiento"], table_3_header]
    for row in nitrogen_summary:
        table_3.append(nitrogen_summary_row(row))

    add_rows(
        ws_docx,
        table_1 + table_2 + table_3,
        title_rows={1, 7, 15},
        header_rows={2, 8, 16},
    )
    autofit(ws_docx)

    ws_solids = wb.create_sheet("Sólidos y masa seca")
    solids_rows = [["Contenido de masa seca y sólidos volátiles por muestra"]]
    solids_rows.append(
        [
            "Muestra",
            "Tipo de muestra",
            "Fecha de análisis",
            "Número de réplicas (n)",
            "Contenido de masa seca promedio (% base húmeda)",
            "Desviación estándar de masa seca (%)",
            "Coeficiente de variación de masa seca (%)",
            "Sólidos volátiles promedio (% base seca)",
            "Desviación estándar de sólidos volátiles (%)",
            "Coeficiente de variación de sólidos volátiles (%)",
        ]
    )
    for row in solids_by_sample:
        solids_rows.append(
            [
                row["sample_group"],
                SAMPLE_TYPE_ES[row["sample_type"]],
                fmt_date(row["sampling_date"]),
                number(row["replicate_count"], 0),
                number(row["dry_matter_mean_pct"]),
                number(row["dry_matter_sd_pct"]),
                number(row["dry_matter_cv_pct"]),
                number(row["volatile_solids_mean_pct"]),
                number(row["volatile_solids_sd_pct"]),
                number(row["volatile_solids_cv_pct"]),
            ]
        )
    add_rows(ws_solids, solids_rows, title_rows={1}, header_rows={2})
    autofit(ws_solids)

    ws_n = wb.create_sheet("Nitrógeno total")
    n_rows = [["Nitrógeno total por muestra individual"]]
    n_rows.append(["Muestra", "Tipo de análisis", "Fecha de análisis", "Nitrógeno total (% masa)", "Nitrógeno total (mg/kg)"])
    for row in nitrogen_samples:
        n_rows.append(
            [
                row["sample_id"],
                row["analysis_type"],
                fmt_date(row["date"]),
                number(row["n_total_porcentaje"]),
                number(row["n_total_mg_kg"]),
            ]
        )
    n_rows.extend([[], [], ["Nitrógeno total representativo por muestra o tratamiento"], table_3_header])
    for row in nitrogen_summary:
        n_rows.append(nitrogen_summary_row(row))
    add_rows(ws_n, n_rows, title_rows={1, 13}, header_rows={2, 14})
    autofit(ws_n)

    ws_notes = wb.create_sheet("Notas")
    add_rows(
        ws_notes,
        [
            ["Criterio de cálculo"],
            [
                "Los valores de contenido de masa seca y sólidos volátiles provienen de "
                "processed/volatile_solids_representative_table.csv y processed/volatile_solids_treatment_table.csv."
            ],
            [
                "El contenido de masa seca representativo por muestra corresponde al promedio de las réplicas "
                "agrupadas por código base de muestra (por ejemplo, A1, A2, B1, B2)."
            ],
            ["Los sólidos volátiles se calcularon como 100 menos el porcentaje de cenizas, en base seca."],
            [
                "El nitrógeno total representativo proviene de processed/CIA_samples_table_v6_treatment_summary.csv "
                "y corresponde al promedio por tratamiento usado por el script."
            ],
            ["Las unidades están indicadas en cada encabezado para facilitar la copia directa al documento académico."],
        ],
        title_rows={1},
    )
    ws_notes.column_dimensions["A"].width = 120
    for row in ws_notes.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")

    return wb


def nitrogen_summary_row(row: dict[str, str]) -> list[Any]:
    return [
        N_TREATMENT_ES[row["treatment"]],
        fmt_date(row["date"]),
        number(row["n_samples"], 0),
        number(row["mean_n_percentage"]),
        number(row["mean_n_total_mg_kg"]),
        number(row["n_total_pct_median"]),
        number(row["n_total_mg_kg_median"]),
        number(row["n_total_mg_kg_min"]),
        number(row["n_total_mg_kg_max"]),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera el Excel de tablas de valores representativos con acentos corregidos."
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Ruta del archivo .xlsx de salida. Valor por defecto: {DEFAULT_OUTPUT}",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = args.output if args.output.is_absolute() else ROOT_DIR / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    workbook = build_workbook()
    workbook.save(output)
    print(output)


if __name__ == "__main__":
    main()
