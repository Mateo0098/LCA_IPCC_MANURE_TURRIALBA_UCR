"""Genera insumos reproducibles para el QA/QC externo EF 3.1 en SimaPro.

El módulo no ejecuta SimaPro, no reconstruye los escenarios como procesos y no
modifica el inventario ni los resultados canónicos. Deriva casos unitarios y
cantidades de la corrida vigente desde las mismas fuentes que consume la LCIA
Python.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

from compute_acv_impact_equivalents import load_factors


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "processed"
OUTPUT_DIR = ROOT / "outputs" / "qa_qc_simapro_ef31"
FACTOR_PATH = PROCESSED / "acv_factores_equivalencia.csv"
FOREGROUND_PATH = PROCESSED / "acv_foreground_intercambio.csv"
IMPACT_PATH = PROCESSED / "acv_impacto_por_etapa_escenario.csv"

ALIASES = {
    "Methane biogenic": "Methane, biogenic; methane biogenic; CH4 biogenic",
    "Nitrous oxide": "Nitrous oxide; dinitrogen monoxide; N2O",
    "Ammonia": "Ammonia; NH3",
    "Nitrogen oxides": "Nitrogen oxides; nitrogen oxides as NO2; NOx as NO2",
    "Nitrate": "Nitrate; NO3-; nitrate ion",
    "Carbon dioxide (fossil)": "Carbon dioxide, fossil; carbon dioxide (fossil); CO2 fossil",
    "Methane (fossil)": "Methane, fossil; methane (fossil); CH4 fossil",
}

COMPARTMENTS = {
    "air unspecified": ("aire", "no especificado"),
    "fresh water": ("agua", "agua dulce"),
}

RESULT_UNITS = {
    "Cambio climático": "kg CO2-eq",
    "Eutrofización terrestre": "mol N-eq",
    "Eutrofización marina": "kg N-eq",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _factor_table() -> pd.DataFrame:
    validated = load_factors(FACTOR_PATH)
    table = pd.read_csv(FACTOR_PATH, keep_default_na=False)
    for row in table.itertuples(index=False):
        key = (row.flujo_elemental, row.compartimento, row.categoria_impacto)
        if not np.isclose(float(row.factor), float(validated[key]["factor"]), rtol=0, atol=0):
            raise AssertionError(f"El factor validado no coincide con la tabla canónica: {key}")
    return table


def _compartment_parts(value: str) -> tuple[str, str]:
    if value not in COMPARTMENTS:
        raise ValueError(f"Compartimento sin traducción controlada para SimaPro: {value}")
    return COMPARTMENTS[value]


def build_unit_cases() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for number, row in enumerate(_factor_table().itertuples(index=False), start=1):
        compartment, subcompartment = _compartment_parts(row.compartimento)
        rows.append(
            {
                "id_caso": f"EF31-U{number:02d}",
                "flujo_python": row.flujo_elemental,
                "especie_quimica": row.especie_quimica,
                "cantidad_entrada": 1.0,
                "unidad_entrada": "kg",
                "compartimento_python": row.compartimento,
                "compartimento_referencia": compartment,
                "subcompartimento_referencia": subcompartment,
                "categoria_ef31": row.categoria_impacto,
                "factor_python": float(row.factor),
                "unidad_factor_python": row.unidad_factor,
                "resultado_python_esperado": float(row.factor),
                "unidad_resultado": RESULT_UNITS[row.categoria_impacto],
                "metodo_python": row.metodo,
                "version_python": str(row.version),
                "formula_python": "resultado = cantidad elemental × factor de caracterización",
                "fuente_factor_python": "processed/acv_factores_equivalencia.csv",
                "referencia_factor": row.fuente_oficial,
                "implementacion_python": "scripts/compute_acv_impact_equivalents.py",
                "alias_busqueda_simapro": ALIASES[row.flujo_elemental],
                "alcance": (
                    "emisión elemental de combustión de diésel"
                    if row.flujo_elemental in {"Carbon dioxide (fossil)", "Methane (fossil)"}
                    else "emisión elemental del inventario"
                ),
            }
        )
    return pd.DataFrame(rows)


def _canonical_flow(row: pd.Series) -> tuple[str, str]:
    source = str(row["procedencia"])
    species = str(row["especie_quimica"])
    if source == "co2_fosil_diesel_kg":
        return "Carbon dioxide (fossil)", "combustión operacional de diésel"
    if source == "ch4_fosil_diesel_kg":
        return "Methane (fossil)", "combustión operacional de diésel"
    if source == "n2o_combustion_diesel_kg":
        return "Nitrous oxide", "combustión operacional de diésel"
    management = {
        "CH4": "Methane biogenic",
        "N2O": "Nitrous oxide",
        "NH3": "Ammonia",
        "NOx as NO2": "Nitrogen oxides",
        "NO3": "Nitrate",
    }
    if species not in management:
        raise ValueError(f"Emisión elemental EF 3.1 sin identidad controlada: {species}, {source}")
    return management[species], "manejo del estiércol"


def build_provisional_inventory() -> pd.DataFrame:
    foreground = pd.read_csv(FOREGROUND_PATH)
    direct = foreground[
        foreground["tipo_flujo"].eq("emisión directa")
        & foreground["condicion_caracterizacion"].str.contains("EF 3.1", regex=False, na=False)
    ].copy()
    if direct.empty:
        raise ValueError("El inventario foreground no contiene emisiones elementales EF 3.1.")

    identities = direct.apply(_canonical_flow, axis=1, result_type="expand")
    direct[["flujo_python", "origen_emision"]] = identities
    direct["cantidad_anual"] = pd.to_numeric(direct["cantidad_anual"], errors="raise")
    if not direct["unidad"].eq("kg/año").all():
        raise ValueError("Los casos reales EF 3.1 deben llegar en kg/año.")

    grouped = (
        direct.groupby(
            [
                "escenario",
                "etapa",
                "flujo_python",
                "especie_quimica",
                "compartimento",
                "origen_emision",
                "unidad",
            ],
            as_index=False,
        )
        .agg(
            cantidad_elemental=("cantidad_anual", "sum"),
            procedencias_python=("procedencia", lambda values: ";".join(sorted(set(values)))),
        )
    )

    factors = _factor_table().rename(
        columns={
            "flujo_elemental": "flujo_python",
            "categoria_impacto": "categoria_ef31",
            "factor": "factor_python",
            "unidad_factor": "unidad_factor_python",
        }
    )
    columns = [
        "flujo_python",
        "compartimento",
        "categoria_ef31",
        "factor_python",
        "unidad_factor_python",
        "metodo",
        "version",
        "fuente_oficial",
    ]
    merged = grouped.merge(factors[columns], on=["flujo_python", "compartimento"], how="left", validate="many_to_many")
    if merged["factor_python"].isna().any():
        missing = merged.loc[merged["factor_python"].isna(), ["flujo_python", "compartimento"]]
        raise ValueError(f"Emisiones sin factor EF 3.1: {missing.to_dict('records')}")
    merged["resultado_python_esperado"] = merged["cantidad_elemental"] * merged["factor_python"]
    merged["unidad_resultado"] = merged["categoria_ef31"].map(RESULT_UNITS)
    merged["corrida_python"] = "PROVISIONAL M1–M2"
    merged["incluir_en_simapro"] = "Sí"
    merged["electricidad_imn_excluida"] = "Sí; es un resultado agregado, no un flujo elemental"
    merged["procesos_fondo_excluidos"] = "Sí; no se modelan electricidad ni diésel de fondo"
    merged = merged.rename(columns={"compartimento": "compartimento_python"})
    parts = merged["compartimento_python"].map(_compartment_parts)
    merged["compartimento_referencia"] = parts.map(lambda value: value[0])
    merged["subcompartimento_referencia"] = parts.map(lambda value: value[1])
    merged["alias_busqueda_simapro"] = merged["flujo_python"].map(ALIASES)
    merged["fuente_inventario_python"] = "processed/acv_foreground_intercambio.csv"
    merged["fuente_factor_python"] = "processed/acv_factores_equivalencia.csv"
    return merged[
        [
            "corrida_python",
            "escenario",
            "etapa",
            "origen_emision",
            "flujo_python",
            "especie_quimica",
            "cantidad_elemental",
            "unidad",
            "compartimento_python",
            "compartimento_referencia",
            "subcompartimento_referencia",
            "categoria_ef31",
            "factor_python",
            "unidad_factor_python",
            "resultado_python_esperado",
            "unidad_resultado",
            "metodo",
            "version",
            "procedencias_python",
            "alias_busqueda_simapro",
            "incluir_en_simapro",
            "electricidad_imn_excluida",
            "procesos_fondo_excluidos",
            "fuente_inventario_python",
            "fuente_factor_python",
            "fuente_oficial",
        ]
    ].sort_values(["escenario", "etapa", "categoria_ef31", "flujo_python", "origen_emision"])


def build_summary(inventory: pd.DataFrame) -> pd.DataFrame:
    summary = (
        inventory.groupby(["escenario", "categoria_ef31", "unidad_resultado"], as_index=False)[
            "resultado_python_esperado"
        ]
        .sum()
        .sort_values(["escenario", "categoria_ef31"])
    )
    summary["corrida_python"] = "PROVISIONAL M1–M2"
    summary["alcance"] = "Solo caracterización EF 3.1 de flujos elementales; electricidad IMN excluida"
    summary["resultado_simapro_observado"] = ""
    summary["diferencia_absoluta"] = ""
    summary["diferencia_relativa"] = ""
    summary["clasificacion_A_H"] = ""
    return summary[
        [
            "corrida_python",
            "escenario",
            "categoria_ef31",
            "resultado_python_esperado",
            "unidad_resultado",
            "alcance",
            "resultado_simapro_observado",
            "diferencia_absoluta",
            "diferencia_relativa",
            "clasificacion_A_H",
        ]
    ]


def validate_against_canonical_impacts(inventory: pd.DataFrame) -> None:
    expected = (
        inventory.groupby(["escenario", "etapa", "categoria_ef31"])["resultado_python_esperado"]
        .sum()
        .to_dict()
    )
    impacts = pd.read_csv(IMPACT_PATH)
    for row in impacts.itertuples(index=False):
        keys_and_values = {
            "Cambio climático": float(row.clima_manejo_ef31_kg_co2eq) + float(row.clima_diesel_ef31_kg_co2eq),
            "Eutrofización terrestre": float(row.impacto_eutrofizacion_terrestre_mol_neq),
            "Eutrofización marina": float(row.impacto_eutrofizacion_marina_kg_neq),
        }
        for category, canonical_value in keys_and_values.items():
            generated = expected.get((row.Escenario, f"{row.Escenario}{int(row.Etapa)}: " + _stage_name(row.Escenario, int(row.Etapa)), category), 0.0)
            if not np.isclose(generated, canonical_value, rtol=1e-12, atol=1e-12):
                raise AssertionError(
                    f"El conjunto SimaPro no reproduce el subtotal EF activo para {row.Escenario}{row.Etapa}, "
                    f"{category}: {generated} != {canonical_value}"
                )


def _stage_name(scenario: str, stage: int) -> str:
    names = {
        ("A", 1): "Precomposteo",
        ("A", 2): "Lombricompostaje",
        ("A", 3): "Almacenamiento de aguas verdes",
        ("A", 4): "Aplicación de aguas verdes en campos de pastoreo",
        ("B", 1): "Almacenamiento de purines",
        ("B", 2): "Aplicación de purines en campo de pastoreo",
    }
    return names[(scenario, stage)]


def build_observation_template(unit_cases: pd.DataFrame) -> pd.DataFrame:
    template = unit_cases.copy()
    blank_columns = [
        "fecha_verificacion",
        "investigador",
        "version_simapro",
        "nombre_metodo_simapro",
        "version_metodo_simapro",
        "configuracion_metodo_simapro",
        "nombre_flujo_simapro",
        "unidad_simapro",
        "compartimento_simapro",
        "subcompartimento_simapro",
        "categoria_simapro",
        "factor_simapro_observado",
        "resultado_simapro_observado",
        "diferencia_absoluta",
        "diferencia_relativa",
        "clasificacion_A_H",
        "diferencia_nomenclatura",
        "evidencia_conservada",
        "observaciones",
    ]
    for column in blank_columns:
        template[column] = ""
    return template


def _write_manifest(unit_cases: pd.DataFrame, inventory: pd.DataFrame, summary: pd.DataFrame) -> None:
    source_hashes = {
        FACTOR_PATH.relative_to(ROOT).as_posix(): sha256(FACTOR_PATH),
        FOREGROUND_PATH.relative_to(ROOT).as_posix(): sha256(FOREGROUND_PATH),
        IMPACT_PATH.relative_to(ROOT).as_posix(): sha256(IMPACT_PATH),
    }
    lines = [
        "# Manifiesto de insumos QA/QC Python–SimaPro EF 3.1",
        "",
        "Estado: **preparado; verificación presencial pendiente**.",
        "",
        "Estos archivos se derivan de la corrida **PROVISIONAL M1–M2**. Python conserva la fuente de verdad; SimaPro se limita a una verificación externa de la caracterización de flujos elementales.",
        "",
        "## Archivos generados",
        "",
        f"- `casos_unitarios_python_ef31.csv`: {len(unit_cases)} combinaciones flujo–compartimento–categoría.",
        f"- `inventario_provisional_m1_m2_para_simapro.csv`: {len(inventory)} combinaciones reales por etapa, origen y categoría.",
        f"- `resumen_python_provisional_m1_m2_ef31.csv`: {len(summary)} subtotales por escenario y categoría.",
        "- `plantilla_registro_presencial_simapro.csv`: copia en blanco para registrar la visita; los resultados observados deben conservarse como evidencia primaria, no incorporarse al generador.",
        "",
        "## Exclusiones obligatorias",
        "",
        "- La contribución eléctrica IMN agregada no se exporta como emisión elemental ni se recaracteriza.",
        "- No se incorporan procesos de fondo de electricidad o diésel.",
        "- No se reconstruyen los escenarios ni las etapas como procesos de SimaPro.",
        "- No existen resultados SimaPro en este manifiesto.",
        "",
        "## Fuentes canónicas y SHA-256",
        "",
    ]
    lines.extend(f"- `{path}`: `{digest}`" for path, digest in source_hashes.items())
    lines.extend(
        [
            "",
            "La regeneración se realiza con `scripts/generate_simapro_ef31_qa.py`. El protocolo permanente reside en `docs/PROTOCOLO_QA_QC_SIMAPRO_EF31.md`.",
            "",
        ]
    )
    (OUTPUT_DIR / "MANIFIESTO_QA_QC.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    unit_cases = build_unit_cases()
    inventory = build_provisional_inventory()
    validate_against_canonical_impacts(inventory)
    summary = build_summary(inventory)
    template = build_observation_template(unit_cases)

    unit_cases.to_csv(OUTPUT_DIR / "casos_unitarios_python_ef31.csv", index=False, encoding="utf-8-sig")
    inventory.to_csv(OUTPUT_DIR / "inventario_provisional_m1_m2_para_simapro.csv", index=False, encoding="utf-8-sig")
    summary.to_csv(OUTPUT_DIR / "resumen_python_provisional_m1_m2_ef31.csv", index=False, encoding="utf-8-sig")
    template.to_csv(OUTPUT_DIR / "plantilla_registro_presencial_simapro.csv", index=False, encoding="utf-8-sig")
    _write_manifest(unit_cases, inventory, summary)
    print(f"Insumos QA/QC EF 3.1 generados en {OUTPUT_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
