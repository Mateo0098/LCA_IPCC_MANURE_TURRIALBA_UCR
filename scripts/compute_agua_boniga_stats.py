from __future__ import annotations

import argparse
import unicodedata
from pathlib import Path

import pandas as pd


def normalize(text: object) -> str:
    raw = str(text) if text is not None else ""
    return "".join(
        ch for ch in unicodedata.normalize("NFKD", raw) if not unicodedata.combining(ch)
    ).lower()


def find_input_file(default_dir: Path) -> Path:
    matches = sorted(default_dir.glob("Datos*proy_AS.xlsx"))
    if not matches:
        raise FileNotFoundError(f"No se encontro archivo 'Datos*proy_AS.xlsx' en: {default_dir}")
    return matches[0]


def find_sheet(path: Path, keyword: str) -> str:
    xl = pd.ExcelFile(path)
    for sheet in xl.sheet_names:
        if keyword in normalize(sheet):
            return sheet
    raise ValueError(f"No se encontro hoja para '{keyword}' en {path.name}. Hojas: {xl.sheet_names}")


def find_value_column(df: pd.DataFrame, variable_keyword: str, unit_keyword: str) -> str:
    col_valor = None

    for col in df.columns:
        col_norm = normalize(col)
        if col_valor is None and (
            variable_keyword in col_norm or unit_keyword in col_norm or "cantidad" in col_norm
        ):
            col_valor = col

    if col_valor is None:
        raise ValueError(f"No se detectaron columnas esperadas. Columnas: {list(df.columns)}")
    return col_valor


def load_series(
    input_path: Path, sheet_keyword: str, variable_keyword: str, unit_keyword: str
) -> pd.Series:
    sheet_name = find_sheet(input_path, sheet_keyword)
    df = pd.read_excel(input_path, sheet_name=sheet_name)
    col_valor = find_value_column(df, variable_keyword, unit_keyword)
    values = pd.to_numeric(df[col_valor], errors="coerce").dropna().reset_index(drop=True)
    return values


def stats_row(series: pd.Series, variable: str, unidad: str) -> dict[str, object]:
    if series.empty:
        return {
            "variable": variable,
            "unidad": unidad,
            "promedio": 0.0,
            "mediana": 0.0,
            "minimo": 0.0,
            "maximo": 0.0,
            "desviacion_estandar": 0.0,
            "n_datos": 0,
        }
    return {
        "variable": variable,
        "unidad": unidad,
        "promedio": round(float(series.mean()), 6),
        "mediana": round(float(series.median()), 6),
        "minimo": round(float(series.min()), 6),
        "maximo": round(float(series.max()), 6),
        "desviacion_estandar": round(float(series.std(ddof=1)) if len(series) > 1 else 0.0, 6),
        "n_datos": int(series.shape[0]),
    }


def add_mass_flow_columns(resumen: pd.DataFrame, duracion_muestreo_dias: float) -> pd.DataFrame:
    if duracion_muestreo_dias <= 0:
        raise ValueError("La duracion del muestreo debe ser mayor que cero.")

    df = resumen.copy()
    flujo_dia = pd.to_numeric(df["promedio"], errors="coerce").fillna(0.0) / duracion_muestreo_dias
    df["duracion_muestreo_dias"] = round(float(duracion_muestreo_dias), 6)
    df["flujo_por_dia"] = flujo_dia.round(6)
    df["flujo_por_semana"] = (flujo_dia * 7.0).round(6)
    df["flujo_por_ano"] = (flujo_dia * 365.0).round(6)
    return df


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Calcula media, mediana, desviacion estandar, minimo y maximo de toda la "
            "serie disponible de consumo de agua y generacion de boniga."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Ruta al Excel de entrada. Si no se define, busca en Academic_documents.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("processed"),
        help="Directorio de salida para CSV.",
    )
    parser.add_argument(
        "--duracion-muestreo-dias",
        type=float,
        default=3.5,
        help=(
            "Duracion del periodo que representa el valor promedio de consumo/generacion "
            "(en dias). Por defecto: 3.5."
        ),
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    input_path = args.input or find_input_file(project_root / "Academic_documents")
    output_dir = args.output_dir if args.output_dir.is_absolute() else project_root / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    agua = load_series(
        input_path=input_path,
        sheet_keyword="agua",
        variable_keyword="agua",
        unit_keyword="l",
    )
    boniga = load_series(
        input_path=input_path,
        sheet_keyword="boniga",
        variable_keyword="boniga",
        unit_keyword="kg",
    )

    resumen = pd.DataFrame(
        [
            stats_row(agua, "agua", "L"),
            stats_row(boniga, "boniga", "kg"),
        ]
    )
    resumen = add_mass_flow_columns(resumen, duracion_muestreo_dias=args.duracion_muestreo_dias)
    resumen["archivo_fuente"] = str(input_path)

    resumen_path = output_dir / "agua_boniga_estadistica_descriptiva.csv"
    resumen.to_csv(resumen_path, index=False, encoding="utf-8-sig")

    print(f"Resumen guardado en: {resumen_path}")
    for row in resumen.to_dict(orient="records"):
        print()
        print(f"Variable: {row['variable']} ({row['unidad']})")
        print(f"  N datos: {row['n_datos']}")
        print(f"  Promedio: {row['promedio']}")
        print(f"  Mediana: {row['mediana']}")
        print(f"  Minimo: {row['minimo']}")
        print(f"  Maximo: {row['maximo']}")
        print(f"  Desviacion estandar: {row['desviacion_estandar']}")
        print(f"  Duracion muestreo (dias): {row['duracion_muestreo_dias']}")
        print(f"  Flujo por dia: {row['flujo_por_dia']}")
        print(f"  Flujo por semana: {row['flujo_por_semana']}")
        print(f"  Flujo por ano: {row['flujo_por_ano']}")


if __name__ == "__main__":
    main()
