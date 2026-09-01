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
        ("CH4", "air unspecified", "Cambio climático"): 27.0,
        ("N2O", "air unspecified", "Cambio climático"): 273.0,
        ("NH3", "air unspecified", "Eutrofización terrestre"): 13.47,
        ("NH3", "air unspecified", "Eutrofización marina"): 0.092,
        ("NOx as NO2", "air unspecified", "Eutrofización terrestre"): 4.26,
        ("NOx as NO2", "air unspecified", "Eutrofización marina"): 0.389,
        ("NO3", "fresh water", "Eutrofización marina"): 0.226,
    }
    assert {key: float(value["factor"]) for key, value in factors.items()} == expected
    assert all(value["unidad"] == EXPECTED_FACTOR_METADATA[key] for key, value in factors.items())
    assert all(value["metodo"] == "Environmental Footprint" for value in factors.values())
    assert all(value["version"] == "3.1" for value in factors.values())

    emissions = load_emissions(P / "ACV_resumen_emisiones.csv")
    reference = load_functional_reference(P / "masa_total_escenario_etapa.csv")
    assert close(reference, 26278.725181)
    calculated = compute_impacts(emissions, factors, reference)
    stored = pd.read_csv(P / "acv_impacto_por_etapa_escenario.csv")
    pd.testing.assert_frame_equal(calculated, stored, check_exact=False, rtol=1e-12, atol=1e-12)
    assert not any("po4" in column.lower() for column in stored.columns)

    resources = pd.read_csv(P / "acv_inventario_recursos_operativos.csv")
    values = {(r.escenario, int(r.etapa), r.flujo): float(r.cantidad_anual) for r in resources.itertuples()}
    assert close(values[("A", 3, "Electricidad")], 53.229166666666664)
    assert values[("A", 3, "Electricidad")] == values[("B", 1, "Electricidad")]
    assert values[("A", 4, "Diésel")] == values[("B", 2, "Diésel")] == 182.5
    assert not any("cañón" in key[2].lower() for key in values)
    assert resources["estado_lcia_actual"].str.contains("pendiente", case=False).all()

    foreground = pd.read_csv(P / "acv_foreground_intercambio.csv")
    assert {"emisión directa", "entrada tecnosférica", "transferencia"} <= set(foreground["tipo_flujo"])
    assert not foreground.loc[foreground["nombre_flujo"].isin(["Electricidad", "Diésel"]),
                              "condicion_caracterizacion"].str.contains("Caracterizado en Python", case=False).any()
    assert foreground["observaciones_doble_conteo"].str.contains("cañón|agua|SimaPro", case=False, regex=True).any()
    print("VALIDACIÓN EF 3.1 E INVENTARIO OPERATIVO: PASS")


if __name__ == "__main__":
    main()
