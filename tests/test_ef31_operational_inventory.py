from __future__ import annotations

import math
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from compute_acv_impact_equivalents import (  # noqa: E402
    EXPECTED_FACTOR_METADATA, compute_impacts, load_factors, load_functional_reference,
)
from compute_operational_inventory import (  # noqa: E402
    build_inventory, functional_reference, load_parameters,
)


class EF31OperationalInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.factor_path = ROOT / "processed" / "acv_factores_equivalencia.csv"
        cls.factors = load_factors(cls.factor_path)
        cls.base = {
            "Escenario": "A", "Etapa": 1, "CO2_medido": 0.0, "CH4_ec1": 0.0,
            "N2O_ec14": 0.0, "N2O_ec2": 0.0, "N2O_ec5": 0.0, "N2O_ec6": 0.0,
            "N2O_ec16": 0.0, "N2O_ec18": 0.0, "NH3_ec12": 0.0, "NH3_ec20": 0.0,
            "NOx_as_NO2": 0.0, "NO3_ec13": 0.0, "NO3_ec21": 0.0,
        }

    def assert_unit_case(self, input_column: str, output_column: str, expected: float) -> None:
        row = dict(self.base)
        row[input_column] = 1.0
        result = compute_impacts(pd.DataFrame([row]), self.factors, 1.0).iloc[0]
        self.assertTrue(math.isclose(float(result[output_column]), expected, rel_tol=0, abs_tol=1e-12))

    def test_one_kg_biogenic_ch4(self) -> None:
        self.assert_unit_case("CH4_ec1", "impacto_calentamiento_global_kg_co2eq", 27.0)

    def test_one_kg_n2o(self) -> None:
        self.assert_unit_case("N2O_ec2", "impacto_calentamiento_global_kg_co2eq", 273.0)

    def test_one_kg_nh3_terrestrial(self) -> None:
        self.assert_unit_case("NH3_ec12", "impacto_eutrofizacion_terrestre_mol_neq", 13.47)

    def test_one_kg_nh3_marine(self) -> None:
        self.assert_unit_case("NH3_ec12", "impacto_eutrofizacion_marina_kg_neq", 0.092)

    def test_one_kg_nox_terrestrial(self) -> None:
        self.assert_unit_case("NOx_as_NO2", "impacto_eutrofizacion_terrestre_mol_neq", 4.26)

    def test_one_kg_nox_marine(self) -> None:
        self.assert_unit_case("NOx_as_NO2", "impacto_eutrofizacion_marina_kg_neq", 0.389)

    def test_one_kg_no3_fresh_water(self) -> None:
        self.assert_unit_case("NO3_ec13", "impacto_eutrofizacion_marina_kg_neq", 0.226)

    def test_factor_metadata_and_unique_triple(self) -> None:
        self.assertEqual(set(self.factors), set(EXPECTED_FACTOR_METADATA))
        for key, data in self.factors.items():
            self.assertEqual(data["compartimento"], key[1])
            self.assertEqual(data["unidad"], EXPECTED_FACTOR_METADATA[key])
            self.assertEqual(data["metodo"], "Environmental Footprint")
            self.assertEqual(data["version"], "3.1")

    def _assert_invalid_factor_table(self, column: str, value: str) -> None:
        table = pd.read_csv(self.factor_path)
        table[column] = table[column].astype(str)
        table.loc[table["especie_quimica"] == "NO3", column] = value
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "factors.csv"
            table.to_csv(path, index=False)
            with self.assertRaises(ValueError):
                load_factors(path)

    def test_wrong_compartment_fails(self) -> None:
        self._assert_invalid_factor_table("compartimento", "air unspecified")

    def test_wrong_unit_fails(self) -> None:
        self._assert_invalid_factor_table("unidad_factor", "mol N-eq/kg NO3")

    def test_wrong_method_fails(self) -> None:
        self._assert_invalid_factor_table("metodo", "Otro método")

    def test_wrong_version_fails(self) -> None:
        self._assert_invalid_factor_table("version", "3.0")

    def test_duplicate_species_compartment_category_fails(self) -> None:
        table = pd.read_csv(self.factor_path)
        table = pd.concat([table, table.iloc[[0]]], ignore_index=True)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "factors.csv"
            table.to_csv(path, index=False)
            with self.assertRaises(ValueError):
                load_factors(path)

    def test_functional_reference_checks_both_scenarios(self) -> None:
        reference = load_functional_reference(ROOT / "processed" / "masa_total_escenario_etapa.csv")
        self.assertTrue(math.isclose(reference, 26278.725181, rel_tol=0, abs_tol=1e-9))

    def test_operational_inventory(self) -> None:
        inventory = build_inventory(load_parameters(), functional_reference())
        values = {(row.escenario, int(row.etapa), row.flujo): float(row.cantidad_anual)
                  for row in inventory.itertuples()}
        self.assertTrue(math.isclose(values[("A", 3, "Electricidad")], 53.229166666666664))
        self.assertEqual(values[("A", 3, "Electricidad")], values[("B", 1, "Electricidad")])
        self.assertEqual(values[("A", 4, "Diésel")], 182.5)
        self.assertEqual(values[("A", 4, "Diésel")], values[("B", 2, "Diésel")])
        self.assertFalse(any("cañón" in flow.lower() for _, _, flow in values))


if __name__ == "__main__":
    unittest.main()
