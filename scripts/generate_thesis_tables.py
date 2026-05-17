from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED = PROJECT_ROOT / "processed"
OUTPUTS = PROJECT_ROOT / "outputs" / "tablas_tesis"


STAGE_NAMES = {
    ("A", 1): "Manejo inicial de estiercol fresco",
    ("A", 2): "Precompostaje de fraccion solida",
    ("A", 3): "Manejo posterior de fraccion solida",
    ("A", 4): "Aplicacion o manejo de aguas verdes en suelo",
    ("B", 1): "Manejo de estiercol fresco sin precompostaje",
    ("B", 2): "Manejo o aplicacion de purines",
}

EMISSION_META = {
    "CO2_medido": ("CO2", "Dioxido de carbono medido", "kg CO2/ano", "factor medido", "processed/factores_emision_medidos.csv"),
    "CH4_ec1": ("CH4", "Metano", "kg CH4/ano", "Ecuacion 1 IPCC o factor medido en A2", "processed/ipcc_sistemas_manejo_estiercol_factores.csv; processed/factores_emision_medidos.csv"),
    "N2O_ec14": ("N2O", "N2O directo por entradas de N en suelos", "kg N2O/ano", "Ecuacion 14", "EF1 hardcodeado en scripts; pendiente fuente IPCC"),
    "N2O_ec2": ("N2O", "N2O directo por gestion de estiercol", "kg N2O/ano", "Ecuacion 2 IPCC o factor medido en A2", "processed/ipcc_sistemas_manejo_estiercol_factores.csv; processed/factores_emision_medidos.csv"),
    "N2O_ec5": ("N2O", "N2O indirecto por volatilizacion", "kg N2O/ano", "Ecuacion 5", "EF4 hardcodeado en scripts; pendiente fuente IPCC"),
    "N2O_ec6": ("N2O", "N2O indirecto por lixiviacion", "kg N2O/ano", "Ecuacion 6", "EF5 hardcodeado en scripts; pendiente fuente IPCC"),
    "N2O_ec16": ("N2O", "N2O indirecto por deposicion atmosferica en suelos", "kg N2O/ano", "Ecuacion 16", "EF4 y frac_gasm hardcodeados en scripts; pendiente fuente IPCC"),
    "N2O_ec18": ("N2O", "N2O indirecto por lixiviacion en suelos", "kg N2O/ano", "Ecuacion 18", "EF5 y frac_leach_h hardcodeados en scripts; pendiente fuente IPCC"),
    "NH3_ec12": ("NH3", "Amoniaco desde manejo de estiercol", "kg NH3/ano", "Ecuacion 12", "Derivado de N volatilizado/lixiviado; factores IPCC y conversion estequiometrica"),
    "NH3_ec20": ("NH3", "Amoniaco desde suelos gestionados", "kg NH3/ano", "Ecuacion 20", "Derivado de N en suelos; factores IPCC y conversion estequiometrica"),
    "NO3_ec13": ("NO3", "Nitrato desde manejo de estiercol", "kg NO3/ano", "Ecuacion 13", "Derivado de N volatilizado/lixiviado; conversion estequiometrica en codigo"),
    "NO3_ec21": ("NO3", "Nitrato desde suelos gestionados", "kg NO3/ano", "Ecuacion 21", "Derivado de N en suelos; conversion estequiometrica en codigo"),
}


def _read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / name)


def _stage_name(escenario: object, etapa: object) -> str:
    try:
        key = (str(escenario).strip().upper(), int(etapa))
    except (TypeError, ValueError):
        return ""
    return STAGE_NAMES.get(key, "")


def _write(df: pd.DataFrame, name: str) -> Path:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    path = OUTPUTS / name
    df.to_csv(path, index=False, encoding="utf-8-sig")
    return path


def tabla_02_caracterizacion_muestras() -> Path:
    vs = _read_csv("volatile_solids_treatment_table.csv")
    n = _read_csv("CIA_samples_table_v6_treatment_summary.csv")

    treatment_to_lab = {
        "A": "ESTIERCOL FRESCO",
        "B": "SOL: PRECOMPOSTADO",
    }
    rows: list[dict[str, object]] = []
    for _, row in vs.iterrows():
        treatment = str(row["treatment"]).strip().upper()
        lab_treatment = treatment_to_lab.get(treatment, treatment)
        n_match = n[n["treatment"].astype(str).str.strip().str.upper() == lab_treatment]
        n_row = n_match.iloc[0] if not n_match.empty else None
        common = {
            "tipo_muestra": row.get("sample_type", ""),
            "tratamiento_laboratorio": lab_treatment,
            "jornada_muestreo": row.get("sampling_date", ""),
            "numero_muestras_solidos": row.get("sample_count", ""),
            "numero_muestras_nitrogeno": n_row.get("n_samples", "") if n_row is not None else "",
            "fuente_dato": "processed/volatile_solids_treatment_table.csv; processed/CIA_samples_table_v6_treatment_summary.csv",
        }
        variables = [
            ("Humedad", row.get("moisture_content_treatment_mean_pct"), "% masa humeda", row.get("moisture_content_treatment_sd_pct"), "Promedio por tratamiento"),
            ("Materia seca", row.get("dry_matter_treatment_mean_pct"), "% masa humeda", row.get("dry_matter_treatment_sd_pct"), "Promedio por tratamiento"),
            ("Cenizas", row.get("ash_content_treatment_mean_pct"), "% base seca", row.get("ash_content_treatment_sd_pct"), "Promedio por tratamiento"),
            ("Solidos volatiles", row.get("volatile_solids_treatment_mean_pct"), "% base seca", row.get("volatile_solids_treatment_sd_pct"), "Calculado como 100 - cenizas"),
        ]
        if n_row is not None:
            variables.append(("Nitrogeno total", n_row.get("mean_n_percentage"), "% N total", "", "Promedio por tratamiento"))
            variables.append(("Nitrogeno total", n_row.get("mean_n_total_mg_kg"), "mg N/kg muestra", "", "Promedio por tratamiento"))
        for variable, value, unit, sd, obs in variables:
            rows.append({
                **common,
                "variable": variable,
                "valor": value,
                "unidad": unit,
                "desviacion_estandar": sd,
                "observaciones": obs,
            })

    return _write(pd.DataFrame(rows), "tabla_02_caracterizacion_muestras.csv")


def tabla_03_flujos_icv() -> Path:
    mass = _read_csv("masa_total_escenario_etapa.csv")
    rows = []
    flow_defs = [
        ("boniga_kg", "Estiercol fresco o fraccion solida", "kg/ano", "fuente_agua_boniga"),
        ("agua_l", "Aguas verdes", "L/ano", "fuente_agua_boniga"),
        ("masa_total_kg_eq", "Masa equivalente total", "kg eq/ano", "fuente_agua_boniga"),
        ("factor_restante_a2", "Factor restante fresco a precompostado", "kg/kg", "fuente_factor_a2"),
    ]
    for _, row in mass.iterrows():
        for col, flow_name, unit, source_col in flow_defs:
            rows.append({
                "escenario": row["escenario"],
                "etapa": int(row["etapa"]),
                "nombre_etapa": _stage_name(row["escenario"], row["etapa"]),
                "flujo": flow_name,
                "valor": row[col],
                "unidad": unit,
                "fuente": row.get(source_col, ""),
                "formula_origen": row.get("formula", ""),
                "observaciones": f"Overrides: boniga={row.get('factor_boniga_override')}; agua={row.get('factor_agua_override')}; masa={row.get('factor_masa_total_override')}",
            })
    return _write(pd.DataFrame(rows), "tabla_03_flujos_icv.csv")


def tabla_04_parametros_modelo_acv() -> Path:
    params = _read_csv("acv_parametros_escenario_etapa.csv")
    mass = _read_csv("masa_total_escenario_etapa.csv")
    selection = _read_csv("ipcc_sistema_manejo_por_etapa.csv")
    factors = _read_csv("ipcc_sistemas_manejo_estiercol_factores.csv")
    models = _read_csv("modelo_etapa_overrides.csv")

    df = params.merge(mass[["escenario", "etapa", "masa_total_kg_eq"]], on=["escenario", "etapa"], how="left")
    df = df.merge(selection[["escenario", "etapa", "sistema_manejo"]], on=["escenario", "etapa"], how="left")
    df = df.merge(models, on=["escenario", "etapa"], how="left")
    df = df.merge(factors, on="sistema_manejo", how="left")
    df["nombre_etapa"] = df.apply(lambda r: _stage_name(r["escenario"], r["etapa"]), axis=1)
    df["n_ex_fraction"] = pd.to_numeric(df["n_ex_pct"], errors="coerce") / 100.0

    rows = []
    param_defs = [
        ("n_ex_pct", "Nitrogeno total reportado", "% N total", "fuente_n_ex", "Valor de caracterizacion; no usar directamente en ecuaciones de N"),
        ("n_ex_fraction", "Nitrogeno total como fraccion masica", "kg N/kg muestra", "fuente_n_ex", "Usado en ecuaciones de N despues de correccion"),
        ("vs_t_pct", "Solidos volatiles", "% base seca", "fuente_vs_t", "Parametro para CH4 en etapas solidas"),
        ("masa_total_kg_eq", "Masa equivalente total", "kg eq/ano", "", "Base de escalamiento por etapa"),
        ("mcf_pct", "MCF", "%", "", "Factor IPCC por sistema de manejo"),
        ("ef3", "EF3", "kg N2O-N/kg N", "", "Factor IPCC por sistema de manejo"),
        ("frac_gas_ms", "Fraccion de N volatilizado en MMS", "adimensional", "", "Factor IPCC por sistema de manejo"),
        ("frac_leach_ms", "Fraccion de N lixiviado en MMS", "adimensional", "", "Factor IPCC por sistema de manejo"),
    ]
    for _, row in df.iterrows():
        for col, name, unit, source_col, obs in param_defs:
            rows.append({
                "escenario": row["escenario"],
                "etapa": int(row["etapa"]),
                "nombre_etapa": row["nombre_etapa"],
                "tipo_muestra": row["tratamiento"],
                "modelo_calculo": row.get("modelo", ""),
                "sistema_manejo_ipcc": row.get("sistema_manejo", ""),
                "parametro": name,
                "valor": row.get(col, ""),
                "unidad": unit,
                "fuente_dato": row.get(source_col, "") if source_col else "processed/ipcc_sistemas_manejo_estiercol_factores.csv; processed/masa_total_escenario_etapa.csv",
                "observaciones": obs,
            })
    return _write(pd.DataFrame(rows), "tabla_04_parametros_modelo_acv.csv")


def tabla_05_factores_emision_y_caracterizacion() -> Path:
    rows = []
    ipcc = _read_csv("ipcc_sistemas_manejo_estiercol_factores.csv")
    for _, row in ipcc.iterrows():
        for col, name, unit in [
            ("mcf_pct", "MCF", "%"),
            ("ef3", "EF3", "kg N2O-N/kg N"),
            ("frac_gas_ms", "Fraccion volatilizada MMS", "adimensional"),
            ("frac_leach_ms", "Fraccion lixiviada MMS", "adimensional"),
        ]:
            rows.append({
                "tipo_factor": "Factor IPCC por sistema de manejo",
                "sistema_o_compuesto": row["sistema_manejo"],
                "factor": name,
                "valor": row[col],
                "unidad": unit,
                "fuente_dato": "processed/ipcc_sistemas_manejo_estiercol_factores.csv",
                "fuente_bibliografica_pendiente": "Si",
                "observaciones": row.get("comentario", ""),
            })

    measured = _read_csv("factores_emision_medidos.csv")
    for _, row in measured.iterrows():
        for col, name, unit in [
            ("co2_kg_por_kg_residuo_seco", "Factor medido CO2", "kg CO2/kg residuo seco"),
            ("ch4_kg_por_kg_residuo_seco", "Factor medido CH4", "kg CH4/kg residuo seco"),
            ("n2o_kg_por_kg_residuo_seco", "Factor medido N2O", "kg N2O/kg residuo seco"),
        ]:
            rows.append({
                "tipo_factor": "Factor de emision medido",
                "sistema_o_compuesto": row["modelo"],
                "factor": name,
                "valor": row[col],
                "unidad": unit,
                "fuente_dato": "processed/factores_emision_medidos.csv",
                "fuente_bibliografica_pendiente": "Si",
                "observaciones": row.get("nota", ""),
            })

    eq = _read_csv("acv_factores_equivalencia.csv")
    for _, row in eq.iterrows():
        if pd.notna(row.get("equivalente_co2")):
            rows.append({
                "tipo_factor": "Factor de caracterizacion",
                "sistema_o_compuesto": row["compuesto"],
                "factor": "Potencial de calentamiento global",
                "valor": row["equivalente_co2"],
                "unidad": "kg CO2-eq/kg sustancia",
                "fuente_dato": "processed/acv_factores_equivalencia.csv",
                "fuente_bibliografica_pendiente": "Si",
                "observaciones": "Usado para calcular impacto_calentamiento_global_kg_co2eq",
            })
        if pd.notna(row.get("equivalente_po4")):
            rows.append({
                "tipo_factor": "Factor de caracterizacion",
                "sistema_o_compuesto": row["compuesto"],
                "factor": "Potencial de eutrofizacion",
                "valor": row["equivalente_po4"],
                "unidad": "kg PO4-eq/kg sustancia",
                "fuente_dato": "processed/acv_factores_equivalencia.csv",
                "fuente_bibliografica_pendiente": "Si",
                "observaciones": "Usado para calcular impacto_eutrofizacion_kg_po4eq",
            })

    hardcoded = OUTPUTS / "tabla_auditoria_factores_hardcodeados.csv"
    if hardcoded.exists():
        audit = pd.read_csv(hardcoded)
        for _, row in audit.iterrows():
            rows.append({
                "tipo_factor": "Factor hardcodeado auditado",
                "sistema_o_compuesto": "",
                "factor": row["factor"],
                "valor": row["valor"],
                "unidad": row["unidad"],
                "fuente_dato": row["script"],
                "fuente_bibliografica_pendiente": row["fuente_pendiente"],
                "observaciones": row["observaciones"],
            })

    return _write(pd.DataFrame(rows), "tabla_05_factores_emision_y_caracterizacion.csv")


def tabla_06_emisiones_por_etapa() -> Path:
    emissions = _read_csv("ACV_resumen_emisiones.csv")
    rows = []
    for _, row in emissions.iterrows():
        for col, meta in EMISSION_META.items():
            value = pd.to_numeric(row.get(col), errors="coerce")
            if pd.isna(value):
                continue
            substance, name, unit, equation, source = meta
            rows.append({
                "escenario": row["Escenario"],
                "etapa": int(row["Etapa"]),
                "nombre_etapa": _stage_name(row["Escenario"], row["Etapa"]),
                "sustancia": substance,
                "emision": name,
                "valor": value,
                "unidad": unit,
                "ecuacion_utilizada": equation,
                "fuente_factor_emision": source,
                "masa_total_kg_eq": row.get("masa_total_kg_eq", ""),
                "observaciones": "n_ex_fraction corregido para ecuaciones de nitrogeno" if substance in {"N2O", "NH3", "NO3"} else "",
            })
    return _write(pd.DataFrame(rows), "tabla_06_emisiones_por_etapa.csv")


def tabla_07_impactos_por_etapa() -> Path:
    impacts = _read_csv("acv_impacto_por_etapa_escenario.csv")
    factors = _read_csv("acv_factores_equivalencia.csv").set_index("compuesto")
    rows = []
    impact_defs = [
        ("ch4_total_kg", "CH4", "Calentamiento global", "equivalente_co2", "kg CO2-eq"),
        ("n2o_total_kg", "N2O", "Calentamiento global", "equivalente_co2", "kg CO2-eq"),
        ("co2_total_kg", "CO2", "Calentamiento global", "equivalente_co2", "kg CO2-eq"),
        ("nh3_total_kg", "NH3", "Eutrofizacion", "equivalente_po4", "kg PO4-eq"),
        ("no3_total_kg", "NO3", "Eutrofizacion", "equivalente_po4", "kg PO4-eq"),
    ]
    for _, row in impacts.iterrows():
        for emission_col, substance, category, factor_col, eq_unit in impact_defs:
            emission = pd.to_numeric(row.get(emission_col), errors="coerce")
            factor = pd.to_numeric(factors.loc[substance, factor_col], errors="coerce") if substance in factors.index else pd.NA
            if pd.isna(emission) or pd.isna(factor):
                continue
            rows.append({
                "escenario": row["Escenario"],
                "etapa": int(row["Etapa"]),
                "nombre_etapa": _stage_name(row["Escenario"], row["Etapa"]),
                "categoria_impacto": category,
                "sustancia": substance,
                "emision": emission,
                "unidad_emision": emission_col.replace("_total_kg", "").upper().replace("CO2", "kg CO2").replace("CH4", "kg CH4").replace("N2O", "kg N2O").replace("NH3", "kg NH3").replace("NO3", "kg NO3"),
                "factor_caracterizacion": factor,
                "unidad_factor": "kg CO2-eq/kg sustancia" if factor_col == "equivalente_co2" else "kg PO4-eq/kg sustancia",
                "resultado_equivalente": emission * factor,
                "unidad_equivalente": eq_unit + "/ano",
                "fuente_factor": "processed/acv_factores_equivalencia.csv",
                "observaciones": "",
            })
    return _write(pd.DataFrame(rows), "tabla_07_impactos_por_etapa.csv")


def tabla_08_impactos_totales_por_escenario() -> Path:
    totals = _read_csv("acv_impacto_total_por_escenario.csv")
    rows = []
    for _, row in totals.iterrows():
        rows.extend([
            {
                "escenario": row["Escenario"],
                "categoria_impacto": "Calentamiento global",
                "resultado_total": row["impacto_calentamiento_global_kg_co2eq"],
                "unidad": "kg CO2-eq/ano",
                "fuente": "processed/acv_impacto_total_por_escenario.csv",
                "observaciones": "Suma de impactos por etapa",
            },
            {
                "escenario": row["Escenario"],
                "categoria_impacto": "Eutrofizacion",
                "resultado_total": row["impacto_eutrofizacion_kg_po4eq"],
                "unidad": "kg PO4-eq/ano",
                "fuente": "processed/acv_impacto_total_por_escenario.csv",
                "observaciones": "Suma de impactos por etapa",
            },
        ])
    return _write(pd.DataFrame(rows), "tabla_08_impactos_totales_por_escenario.csv")


def tabla_09_comparacion_escenarios() -> Path:
    totals = _read_csv("acv_impacto_total_por_escenario.csv").set_index("Escenario")
    rows = []
    defs = [
        ("Calentamiento global", "impacto_calentamiento_global_kg_co2eq", "kg CO2-eq/ano"),
        ("Eutrofizacion", "impacto_eutrofizacion_kg_po4eq", "kg PO4-eq/ano"),
    ]
    for category, col, unit in defs:
        a = float(totals.loc["A", col])
        b = float(totals.loc["B", col])
        diff = b - a
        pct = (diff / a * 100.0) if a != 0 else pd.NA
        rows.append({
            "categoria_impacto": category,
            "escenario_A": a,
            "escenario_B": b,
            "unidad": unit,
            "diferencia_absoluta_B_menos_A": diff,
            "diferencia_porcentual_B_vs_A": pct,
            "escenario_con_mayor_impacto": "A" if a > b else "B" if b > a else "Iguales",
            "fuente": "processed/acv_impacto_total_por_escenario.csv",
            "observaciones": "Comparacion posterior a correccion de n_ex_pct a n_ex_fraction",
        })
    return _write(pd.DataFrame(rows), "tabla_09_comparacion_escenarios.csv")


def diccionario_variables() -> Path:
    rows = [
        ("escenario", "Identificador del escenario de manejo", "A o B", "Tablas de escenarios y resultados"),
        ("etapa", "Numero de etapa dentro del escenario", "adimensional", "Scripts ACV_Escenario*.py"),
        ("nombre_etapa", "Nombre descriptivo propuesto para la etapa", "texto", "outputs/tablas_tesis/tabla_01_etapas_escenarios.csv"),
        ("tipo_muestra", "Tratamiento o material representado", "texto", "processed/acv_parametros_escenario_etapa.csv"),
        ("n_ex_pct", "Nitrogeno total reportado en laboratorio", "% N total", "processed/acv_parametros_escenario_etapa.csv"),
        ("n_ex_fraction", "Nitrogeno total como fraccion masica", "kg N/kg muestra", "Calculado como n_ex_pct/100"),
        ("masa_total_kg_eq", "Masa equivalente usada para escalar emisiones", "kg eq/ano", "processed/masa_total_escenario_etapa.csv"),
        ("valor", "Valor numerico de la variable reportada", "depende de unidad", "Tablas finales"),
        ("unidad", "Unidad explicita del valor reportado", "texto", "Tablas finales"),
        ("fuente_dato", "Archivo o fuente de origen del valor", "texto", "Tablas finales"),
        ("observaciones", "Notas metodologicas o advertencias de uso", "texto", "Tablas finales"),
        ("factor_caracterizacion", "Factor para convertir emisiones a equivalentes", "kg equivalente/kg sustancia", "processed/acv_factores_equivalencia.csv"),
        ("resultado_equivalente", "Resultado de impacto ambiental por sustancia", "kg CO2-eq/ano o kg PO4-eq/ano", "tabla_07_impactos_por_etapa.csv"),
    ]
    df = pd.DataFrame(rows, columns=["variable", "definicion", "unidad", "fuente_o_calculo"])
    return _write(df, "diccionario_variables.csv")


def main() -> None:
    writers = [
        tabla_02_caracterizacion_muestras,
        tabla_03_flujos_icv,
        tabla_04_parametros_modelo_acv,
        tabla_05_factores_emision_y_caracterizacion,
        tabla_06_emisiones_por_etapa,
        tabla_07_impactos_por_etapa,
        tabla_08_impactos_totales_por_escenario,
        tabla_09_comparacion_escenarios,
        diccionario_variables,
    ]
    for writer in writers:
        path = writer()
        print(f"Generado: {path}")


if __name__ == "__main__":
    main()
