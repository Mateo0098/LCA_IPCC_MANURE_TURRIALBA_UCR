from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Optional


STAGE_TREATMENTS = [
    ("A", 1, "ESTIERCOL FRESCO", "A"),
    ("A", 2, "SOL: PRECOMPOSTADO", "B"),
    ("A", 3, "ESTIERCOL FRESCO", "A"),
    ("A", 4, "LIQ: AGUA VERDE", None),
    ("B", 1, "ESTIERCOL FRESCO", "A"),
    ("B", 2, "LIQ: PURINES", None),
]


def resolve_n_ex_summary_path(processed: Path) -> Path:
    candidates = [
        processed / "CIA_samples_table_v6_treatment_summary.csv",
        processed / "CIA_samples_table_treatment_summary.csv",
    ]
    for path in candidates:
        if path.exists():
            return path
    return candidates[0]


def load_n_ex_by_treatment(csv_path: Path) -> Dict[str, Dict[str, str]]:
    if not csv_path.exists():
        raise FileNotFoundError(f"No existe tabla de N total por tratamiento: {csv_path}")

    out: Dict[str, Dict[str, str]] = {}
    with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            treatment = str(row.get("treatment", "")).strip().upper()
            if not treatment:
                continue
            if treatment in out:
                raise ValueError(f"Tratamiento duplicado en {csv_path}: {treatment}")
            n_ex = str(row.get("mean_n_percentage", "")).strip()
            date = str(row.get("date", "")).strip()
            if n_ex == "":
                raise ValueError(
                    f"mean_n_percentage vacio para tratamiento '{treatment}' en {csv_path}"
                )
            out[treatment] = {
                "n_ex_pct": n_ex,
                "fecha_n_ex": date,
            }
    if not out:
        raise ValueError(f"Sin filas de tratamiento en {csv_path}")
    return out


def load_vs_by_treatment_code(csv_path: Path) -> Dict[str, Dict[str, str]]:
    if not csv_path.exists():
        raise FileNotFoundError(f"No existe tabla de solidos volatiles por tratamiento: {csv_path}")

    out: Dict[str, Dict[str, str]] = {}
    with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            treatment = str(row.get("treatment", "")).strip().upper()
            if not treatment:
                continue
            if treatment in out:
                raise ValueError(f"Tratamiento duplicado en {csv_path}: {treatment}")
            vs_t = str(row.get("volatile_solids_treatment_mean_pct", "")).strip()
            date = str(row.get("sampling_date", "")).strip()
            if vs_t == "":
                raise ValueError(
                    f"volatile_solids_treatment_mean_pct vacio para tratamiento '{treatment}' en {csv_path}"
                )
            out[treatment] = {
                "vs_t_pct": vs_t,
                "fecha_vs_t": date,
            }
    if not out:
        raise ValueError(f"Sin filas de tratamiento en {csv_path}")
    return out


def build_rows(
    n_ex_data: Dict[str, Dict[str, str]],
    vs_data: Dict[str, Dict[str, str]],
    fuente_n_ex: str,
    fuente_vs_t: str,
) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for escenario, etapa, treatment_name, vs_treatment_code in STAGE_TREATMENTS:
        n_key = treatment_name.strip().upper()
        n_row = n_ex_data.get(n_key)
        if n_row is None:
            raise KeyError(
                f"No existe tratamiento '{treatment_name}' en la tabla de N total."
            )

        vs_t_pct = ""
        fecha_vs_t = ""
        unidad_vs_t = ""
        fuente_vs_field = ""
        if vs_treatment_code is not None:
            vs_key = str(vs_treatment_code).strip().upper()
            vs_row = vs_data.get(vs_key)
            if vs_row is None:
                raise KeyError(
                    f"No existe tratamiento '{vs_treatment_code}' en la tabla de solidos volatiles."
                )
            vs_t_pct = vs_row["vs_t_pct"]
            fecha_vs_t = vs_row["fecha_vs_t"]
            unidad_vs_t = "% Solidos volatiles"
            fuente_vs_field = fuente_vs_t

        rows.append(
            {
                "escenario": escenario,
                "etapa": str(etapa),
                "tratamiento": treatment_name,
                "n_ex_pct": n_row["n_ex_pct"],
                "vs_t_pct": vs_t_pct,
                "fecha_n_ex": n_row["fecha_n_ex"],
                "fecha_vs_t": fecha_vs_t,
                "unidad_n_ex": "% N total",
                "unidad_vs_t": unidad_vs_t,
                "fuente_n_ex": fuente_n_ex,
                "fuente_vs_t": fuente_vs_field,
            }
        )
    return rows


def write_rows(rows: List[Dict[str, str]], output_path: Path) -> Path:
    fieldnames = [
        "escenario",
        "etapa",
        "tratamiento",
        "n_ex_pct",
        "vs_t_pct",
        "fecha_n_ex",
        "fecha_vs_t",
        "unidad_n_ex",
        "unidad_vs_t",
        "fuente_n_ex",
        "fuente_vs_t",
    ]
    try:
        with output_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return output_path
    except PermissionError:
        fallback = output_path.with_name(f"{output_path.stem}_updated{output_path.suffix}")
        with fallback.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        return fallback


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    processed = project_root / "processed"

    n_ex_path = resolve_n_ex_summary_path(processed)
    vs_path = processed / "volatile_solids_treatment_table.csv"
    output_path = processed / "acv_parametros_escenario_etapa.csv"

    n_ex_data = load_n_ex_by_treatment(n_ex_path)
    vs_data = load_vs_by_treatment_code(vs_path)
    rows = build_rows(
        n_ex_data=n_ex_data,
        vs_data=vs_data,
        fuente_n_ex=n_ex_path.name,
        fuente_vs_t=vs_path.name,
    )
    final_path = write_rows(rows, output_path)

    print(f"Tabla generada: {final_path}")
    print(f"Filas exportadas: {len(rows)}")
    print(f"Fuente N_ex: {n_ex_path}")
    print(f"Fuente VS_T: {vs_path}")


if __name__ == "__main__":
    main()
