from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED = PROJECT_ROOT / "processed"
OUTPUTS = PROJECT_ROOT / "outputs" / "tablas_tesis"


EQUATIONS_BY_STAGE = {
    ("A", 1): "N2O_ec2; N2O_ec5 via N_volatilization_mms; N2O_ec6 via N_lixiviado_mms; NH3_ec12; NO3_ec13",
    ("A", 2): "No usado en modo medido actual; en rama IPCC: N2O_ec2; N2O_ec5; N2O_ec6; NH3_ec12; NO3_ec13",
    ("A", 3): "N2O_ec2; N2O_ec5 via N_volatilization_mms; N2O_ec6 via N_lixiviado_mms; NH3_ec12; NO3_ec13",
    ("A", 4): "N2O_ec14; N2O_ec16; N2O_ec18; NH3_ec20; NO3_ec21; n_mms_available interno",
    ("B", 1): "N2O_ec2; N2O_ec5 via N_volatilization_mms; N2O_ec6 via N_lixiviado_mms; NH3_ec12; NO3_ec13",
    ("B", 2): "N2O_ec14; N2O_ec16; N2O_ec18; NH3_ec20; NO3_ec21; n_mms_available interno",
}


OBS_BY_STAGE = {
    ("A", 2): "La etapa A2 esta configurada como modelo medido; n_ex_fraction queda corregido en la rama IPCC para trazabilidad si se cambia el modelo.",
}


def _stage_key(row: pd.Series) -> tuple[str, int]:
    return str(row["escenario"]).strip().upper(), int(row["etapa"])


def write_nitrogen_audit() -> Path:
    params = pd.read_csv(PROCESSED / "acv_parametros_escenario_etapa.csv")
    masses = pd.read_csv(PROCESSED / "masa_total_escenario_etapa.csv")

    df = params.merge(masses[["escenario", "etapa", "masa_total_kg_eq"]], on=["escenario", "etapa"], how="left")
    df["n_ex_pct"] = pd.to_numeric(df["n_ex_pct"], errors="coerce")
    df["masa_total_kg_eq"] = pd.to_numeric(df["masa_total_kg_eq"], errors="coerce")
    df["n_ex_fraction"] = df["n_ex_pct"] / 100.0
    df["n_total_kg_estimado"] = df["n_ex_fraction"] * df["masa_total_kg_eq"]
    df["ecuaciones_donde_se_usa"] = df.apply(lambda row: EQUATIONS_BY_STAGE.get(_stage_key(row), ""), axis=1)
    df["observaciones"] = df.apply(
        lambda row: OBS_BY_STAGE.get(
            _stage_key(row),
            "n_ex_pct se conserva como porcentaje reportado; n_ex_fraction se usa como fraccion masica para ecuaciones de N.",
        ),
        axis=1,
    )
    out = df.rename(columns={"tratamiento": "tipo_muestra"})[
        [
            "escenario",
            "etapa",
            "tipo_muestra",
            "n_ex_pct",
            "n_ex_fraction",
            "masa_total_kg_eq",
            "n_total_kg_estimado",
            "ecuaciones_donde_se_usa",
            "observaciones",
        ]
    ].sort_values(["escenario", "etapa"])

    output_path = OUTPUTS / "tabla_auditoria_nitrogeno.csv"
    out.to_csv(output_path, index=False, encoding="utf-8-sig")
    return output_path


def _load_table(path: Path, id_cols: list[str]) -> pd.DataFrame:
    df = pd.read_csv(path)
    for col in id_cols:
        if col not in df.columns:
            raise ValueError(f"Falta columna {col} en {path}")
    return df


def _compare_wide_tables(
    before_path: Path,
    after_path: Path,
    id_cols: list[str],
    table_name: str,
) -> pd.DataFrame:
    before = _load_table(before_path, id_cols)
    after = _load_table(after_path, id_cols)

    value_cols = [col for col in after.columns if col not in id_cols]
    before_long = before.melt(id_vars=id_cols, value_vars=[c for c in value_cols if c in before.columns], var_name="variable", value_name="valor_antes")
    after_long = after.melt(id_vars=id_cols, value_vars=value_cols, var_name="variable", value_name="valor_despues")
    merged = before_long.merge(after_long, on=id_cols + ["variable"], how="outer")
    merged["valor_antes"] = pd.to_numeric(merged["valor_antes"], errors="coerce")
    merged["valor_despues"] = pd.to_numeric(merged["valor_despues"], errors="coerce")
    merged["diferencia_absoluta"] = merged["valor_despues"] - merged["valor_antes"]
    merged["diferencia_porcentual"] = (merged["diferencia_absoluta"] / merged["valor_antes"].replace({0: pd.NA})) * 100.0
    merged.insert(0, "tabla_origen", table_name)
    return merged


def write_comparison() -> Path:
    comparisons = [
        _compare_wide_tables(
            OUTPUTS / "ACV_resumen_emisiones_antes_correccion_nitrogeno.csv",
            PROCESSED / "ACV_resumen_emisiones.csv",
            ["Escenario", "Etapa"],
            "ACV_resumen_emisiones",
        ),
        _compare_wide_tables(
            OUTPUTS / "acv_impacto_por_etapa_escenario_antes_correccion_nitrogeno.csv",
            PROCESSED / "acv_impacto_por_etapa_escenario.csv",
            ["Escenario", "Etapa"],
            "acv_impacto_por_etapa_escenario",
        ),
        _compare_wide_tables(
            OUTPUTS / "acv_impacto_total_por_escenario_antes_correccion_nitrogeno.csv",
            PROCESSED / "acv_impacto_total_por_escenario.csv",
            ["Escenario"],
            "acv_impacto_total_por_escenario",
        ),
    ]
    out = pd.concat(comparisons, ignore_index=True)
    output_path = OUTPUTS / "tabla_comparacion_correccion_nitrogeno.csv"
    out.to_csv(output_path, index=False, encoding="utf-8-sig")
    return output_path


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    audit_path = write_nitrogen_audit()
    comparison_path = write_comparison()
    print(f"Tabla auditoria nitrogeno: {audit_path}")
    print(f"Tabla comparacion correccion nitrogeno: {comparison_path}")


if __name__ == "__main__":
    main()
