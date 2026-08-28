"""Genera el contraste bibliográfico de A2 sin modificar el modelo ACV oficial."""

from __future__ import annotations

import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Academic_documents" / "references" / "jjagwe_2019_benchmark.csv"
PARAMS = ROOT / "processed" / "acv_parametros_escenario_etapa.csv"
MASSES = ROOT / "processed" / "masa_total_escenario_etapa.csv"
EMISSIONS = ROOT / "processed" / "ACV_resumen_emisiones.csv"
FACTORS = ROOT / "processed" / "acv_factores_equivalencia.csv"
OUTPUT = ROOT / "processed" / "a2_ipcc_jjagwe_benchmark.csv"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def one(rows: list[dict[str, str]], **conditions: object) -> dict[str, str]:
    selected = [row for row in rows if all(str(row.get(column, "")).strip() == str(value) for column, value in conditions.items())]
    if len(selected) != 1:
        raise ValueError(f"Se esperaba una fila para {conditions}, se encontraron {len(selected)}")
    return selected[0]


def number(row: dict[str, str], column: str) -> float:
    value = float(row[column])
    if not math.isfinite(value):
        raise ValueError(f"Valor no finito: {column}={row[column]}")
    return value


def comparison_row(indicator: str, ipcc: float, experimental: float, unit: str, dry_mass: float, note: str) -> dict[str, str | float]:
    difference = ipcc - experimental
    return {
        "indicador": indicator,
        "valor_ipcc": ipcc,
        "valor_experimental": experimental,
        "unidad": unit,
        "diferencia_absoluta_ipcc_menos_experimental": difference,
        "razon_ipcc_experimental": ipcc / experimental,
        "diferencia_porcentual_relativa_experimental": difference / experimental * 100.0,
        "masa_seca_entrada_a2_kg_anio": dry_mass,
        "base_comun": "materia seca del estiércol precompostado al ingreso de A2",
        "fuente_ipcc": "inventario oficial vigente de A2 y factores de caracterización del TFG",
        "fuente_experimental": "Jjagwe et al. (2019), DOI 10.3390/su11195173",
        "observacion": note,
    }


def build_rows() -> list[dict[str, str | float]]:
    literature = {row["sustancia_indicador"]: row for row in read_rows(SOURCE)}
    required = {"CH4 acumulado", "N2O acumulado", "Pérdida atmosférica de N", "N en vermicompost", "N en biomasa de lombrices", "TKN inicial del estiércol", "NH3"}
    if set(literature) != required:
        raise ValueError(f"Indicadores bibliográficos inesperados: {set(literature) ^ required}")
    if literature["NH3"]["valor"].strip().lower() != "no detectado":
        raise ValueError("El dato cualitativo de NH3 debe permanecer como no detectado")

    params = one(read_rows(PARAMS), escenario="A", etapa="2")
    mass = one(read_rows(MASSES), escenario="A", etapa="2")
    emissions = one(read_rows(EMISSIONS), Escenario="A", Etapa="2")
    factors = {(row["especie_quimica"], row["categoria_impacto"]): row for row in read_rows(FACTORS)}
    wet_mass = number(mass, "masa_total_kg_eq")
    dry_fraction = number(params, "materia_seca_pct") / 100.0
    dry_mass = wet_mass * dry_fraction
    n_effective_fraction = (number(params, "n_ex_pct") / 100.0) * dry_fraction
    initial_n = wet_mass * n_effective_fraction
    ch4_kg = number(emissions, "CH4_ec1")
    n2o_direct_kg = number(emissions, "N2O_ec2")
    ch4_ipcc = ch4_kg * 1000.0 / dry_mass
    n2o_ipcc = n2o_direct_kg * 1_000_000.0 / dry_mass
    ch4_exp = number(literature["CH4 acumulado"], "valor")
    n2o_exp = number(literature["N2O acumulado"], "valor")
    ipcc_n_ratio = (n2o_direct_kg * 28.0 / 44.0) / initial_n
    exp_n_ratio = (n2o_exp / 1_000_000.0 * 28.0 / 44.0) / (number(literature["TKN inicial del estiércol"], "valor") / 100.0)
    cf_ch4 = number(factors[("CH4", "Cambio climático")], "factor")
    cf_n2o = number(factors[("N2O", "Cambio climático")], "factor")
    climate_ipcc = ch4_ipcc / 1000.0 * cf_ch4 + n2o_ipcc / 1_000_000.0 * cf_n2o
    climate_exp = ch4_exp / 1000.0 * cf_ch4 + n2o_exp / 1_000_000.0 * cf_n2o
    return [
        comparison_row("CH4 por materia seca de entrada", ch4_ipcc, ch4_exp, "g CH4/kg MS entrada A2", dry_mass, "El valor IPCC usa exclusivamente CH4_ec1 del inventario oficial de A2."),
        comparison_row("N2O directo por materia seca de entrada", n2o_ipcc, n2o_exp, "mg N2O/kg MS entrada A2", dry_mass, "El contraste usa únicamente N2O_ec2; excluye las vías indirectas IPCC."),
        comparison_row("N2O-N directo por N inicial", ipcc_n_ratio, exp_n_ratio, "kg N2O-N/kg N inicial", dry_mass, "Indicador complementario; no constituye validación formal del modelo."),
        comparison_row("Contraste armonizado de CH4 y N2O directo", climate_ipcc, climate_exp, "kg CO2-eq/kg MS entrada A2", dry_mass, f"Incluye solo CH4 y N2O directo con factores TFG vigentes: CH4={cf_ch4:g}; N2O={cf_n2o:g}."),
    ]


def write_rows(rows: list[dict[str, str | float]]) -> None:
    with OUTPUT.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    rows = build_rows()
    write_rows(rows)
    print(f"Benchmark A2 generado: {OUTPUT}")
    print(f"Indicadores comparativos: {len(rows)}")


if __name__ == "__main__":
    main()
