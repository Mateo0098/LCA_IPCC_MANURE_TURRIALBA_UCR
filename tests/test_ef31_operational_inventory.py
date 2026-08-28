from __future__ import annotations

import math
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from compute_acv_impact_equivalents import compute_impacts, load_factors
from compute_operational_inventory import build_inventory, load_parameters, functional_reference


def test_ef31_unit_cases() -> None:
    factors = load_factors(ROOT / "processed" / "acv_factores_equivalencia.csv")
    import pandas as pd
    base = {"Escenario": "A", "Etapa": 1, "CO2_medido": 0.0, "CH4_ec1": 0.0,
            "N2O_ec14": 0.0, "N2O_ec2": 0.0, "N2O_ec5": 0.0, "N2O_ec6": 0.0,
            "N2O_ec16": 0.0, "N2O_ec18": 0.0, "NH3_ec12": 0.0, "NH3_ec20": 0.0,
            "NOx_as_NO2": 0.0, "NO3_ec13": 0.0, "NO3_ec21": 0.0}
    cases = [
        ("CH4_ec1", "impacto_calentamiento_global_kg_co2eq", 27.0),
        ("N2O_ec2", "impacto_calentamiento_global_kg_co2eq", 273.0),
        ("NH3_ec12", "impacto_eutrofizacion_terrestre_mol_neq", 13.47),
        ("NH3_ec12", "impacto_eutrofizacion_marina_kg_neq", 0.092),
        ("NOx_as_NO2", "impacto_eutrofizacion_terrestre_mol_neq", 4.26),
        ("NOx_as_NO2", "impacto_eutrofizacion_marina_kg_neq", 0.389),
        ("NO3_ec13", "impacto_eutrofizacion_marina_kg_neq", 0.226),
    ]
    for input_column, output_column, expected in cases:
        row = dict(base); row[input_column] = 1.0
        result = compute_impacts(pd.DataFrame([row]), factors, 1.0).iloc[0]
        assert math.isclose(float(result[output_column]), expected, rel_tol=0, abs_tol=1e-12)


def test_operational_inventory() -> None:
    inventory = build_inventory(load_parameters(), functional_reference())
    values = {(row.escenario, int(row.etapa), row.flujo): float(row.cantidad_anual)
              for row in inventory.itertuples()}
    assert math.isclose(values[("A", 3, "Electricidad")], 53.229166666666664)
    assert values[("A", 3, "Electricidad")] == values[("B", 1, "Electricidad")]
    assert values[("A", 4, "Diésel")] == values[("B", 2, "Diésel")] == 182.5
    assert not any("cañón" in flow.lower() for _, _, flow in values)
