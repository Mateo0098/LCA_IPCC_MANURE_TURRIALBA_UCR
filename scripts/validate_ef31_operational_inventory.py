"""Validación cruzada de EF 3.1, recursos operativos y foreground neutral."""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd

from compute_acv_impact_equivalents import (
    EXPECTED_FACTOR_METADATA,
    compute_impacts,
    load_emissions,
    load_factors,
    load_functional_reference,
)


ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "processed"


def close(a: float, b: float) -> bool:
    return math.isclose(float(a), float(b), rel_tol=1e-12, abs_tol=1e-12)


def main() -> None:
    factors = load_factors(P / "acv_factores_equivalencia.csv")
    expected = {
        ("Carbon dioxide (fossil)", "air unspecified", "Cambio climático"): 1.0,
        ("Methane (fossil)", "air unspecified", "Cambio climático"): 29.8,
        ("Methane biogenic", "air unspecified", "Cambio climático"): 27.0,
        ("Nitrous oxide", "air unspecified", "Cambio climático"): 273.0,
        ("Ammonia", "air unspecified", "Eutrofización terrestre"): 13.47,
        ("Ammonia", "air unspecified", "Eutrofización marina"): 0.092,
        ("Nitrogen oxides", "air unspecified", "Eutrofización terrestre"): 4.26,
        ("Nitrogen oxides", "air unspecified", "Eutrofización marina"): 0.389,
        ("Nitrate", "fresh water", "Eutrofización marina"): 0.226,
    }
    assert {key: float(value["factor"]) for key, value in factors.items()} == expected
    assert all(value["unidad"] == EXPECTED_FACTOR_METADATA[key] for key, value in factors.items())
    assert all(value["metodo"] == "Environmental Footprint" for value in factors.values())
    assert all(value["version"] == "3.1" for value in factors.values())

    emissions = load_emissions(P / "ACV_resumen_emisiones.csv")
    reference = load_functional_reference(P / "masa_total_escenario_etapa.csv")
    assert close(reference, 26278.725181)
    resources = pd.read_csv(P / "acv_inventario_recursos_operativos.csv")
    calculated = compute_impacts(emissions, factors, reference, resources)
    stored = pd.read_csv(P / "acv_impacto_por_etapa_escenario.csv")
    pd.testing.assert_frame_equal(calculated, stored, check_exact=False, rtol=1e-12, atol=1e-12)
    assert not any("po4" in column.lower() for column in stored.columns)

    resources = pd.read_csv(P / "acv_inventario_recursos_operativos.csv")
    values = {(r.escenario, int(r.etapa), r.flujo): float(r.cantidad_anual) for r in resources.itertuples()}
    assert close(values[("A", 3, "Electricidad")], 53.229166666666664)
    assert values[("A", 3, "Electricidad")] == values[("B", 1, "Electricidad")]
    assert values[("A", 4, "Diésel")] == values[("B", 2, "Diésel")] == 182.5
    assert not any("cañón" in key[2].lower() for key in values)
    assert not resources["estado_lcia_actual"].str.contains("pendiente", case=False).any()
    assert resources["dataset_background_pendiente"].eq("No").all()
    from imn_operational_factors import load_imn_factors, add_operational_emissions, DERIVED_COLUMNS
    from compute_operational_inventory import build_inventory, load_parameters
    imn = load_imn_factors()
    assert imn["valor"].to_dict() == {"imn_electricidad_consumo_2025": 0.0415, "imn_diesel_co2": 2.613,
        "imn_diesel_ch4_agricola": 0.382, "imn_diesel_n2o_agricola": 0.02442}
    rebuilt = add_operational_emissions(build_inventory(load_parameters(), reference), imn)
    pd.testing.assert_frame_equal(rebuilt, resources, check_exact=False, rtol=1e-12, atol=1e-12)
    totals = pd.read_csv(P / "acv_impacto_total_por_escenario.csv").set_index("Escenario")
    management = compute_impacts(emissions, factors, reference)
    for col in ["clima_manejo_ef31_kg_co2eq", "impacto_eutrofizacion_terrestre_mol_neq", "impacto_eutrofizacion_marina_kg_neq"]:
        assert all(close(a, b) for a, b in zip(management[col], stored[col]))
    for scenario in ("A", "B"):
        part = stored[stored["Escenario"].eq(scenario)]
        for col, expected_value in {"co2_fosil_diesel_kg": 476.8725, "ch4_fosil_diesel_kg": 0.069715,
            "n2o_combustion_diesel_kg": 0.00445665, "clima_electricidad_imn_kg_co2eq": 2.209010416666667,
            "clima_diesel_ef31_kg_co2eq": 480.16667245, "clima_recursos_operativos_kg_co2eq": 482.3756828666667}.items():
            assert close(part[col].sum(), expected_value), col
            assert close(totals.loc[scenario, col], expected_value), col
        for col in [c for c in part if c.startswith("clima_") or c.startswith("impacto_")]:
            assert close(part[col].sum(), totals.loc[scenario, col]), col
        assert close(totals.loc[scenario, "impacto_calentamiento_global_kg_co2eq"],
                     totals.loc[scenario, "clima_manejo_ef31_kg_co2eq"] + totals.loc[scenario, "clima_recursos_operativos_kg_co2eq"])
    for col in ["clima_manejo_ef31_kg_co2eq", "clima_electricidad_imn_kg_co2eq", "clima_diesel_ef31_kg_co2eq", "clima_recursos_operativos_kg_co2eq", "impacto_calentamiento_global_kg_co2eq"]:
        assert all(close(a / reference, b) for a,b in zip(stored[col], stored[col + "_por_kg_estiercol_fresco"]))
    for col in DERIVED_COLUMNS:
        assert all(close(a / reference, b) for a,b in zip(resources[col], resources[col + "_por_kg_estiercol_fresco"]))

    foreground = pd.read_csv(P / "acv_foreground_intercambio.csv")
    assert {"emisión directa", "entrada tecnosférica", "transferencia"} <= set(foreground["tipo_flujo"])
    assert foreground["dataset_background_pendiente"].eq("No").all()
    assert not foreground["condicion_caracterizacion"].str.contains("pendiente|ecoinvent", case=False).any()
    assert len(foreground[foreground["tipo_flujo"].eq("entrada tecnosférica")]) == 4
    aggregated = foreground[foreground["tipo_flujo"].eq("resultado agregado")]
    assert len(aggregated) == 2 and aggregated["especie_quimica"].isna().all()
    assert aggregated["unidad"].eq("kg CO2-eq/año").all()
    for column in ["co2_fosil_diesel_kg", "ch4_fosil_diesel_kg", "n2o_combustion_diesel_kg"]:
        exported = foreground[foreground["procedencia"].eq(column)]
        assert len(exported) == 2
        for row in exported.itertuples():
            assert close(row.cantidad_anual, totals.loc[row.escenario, column])
    assert not foreground.duplicated(["escenario", "etapa", "tipo_flujo", "procedencia"]).any()
    assert foreground["observaciones_doble_conteo"].str.contains("cañón|agua|SimaPro", case=False, regex=True).any()
    print("VALIDACIÓN EF 3.1 E INVENTARIO OPERATIVO: PASS")


if __name__ == "__main__":
    main()
