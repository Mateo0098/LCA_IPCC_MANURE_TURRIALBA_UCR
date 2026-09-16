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
from imn_operational_factors import (  # noqa: E402
    add_operational_emissions, load_imn_factors, FACTOR_PATH,
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
        table = pd.read_csv(self.factor_path)
        fossil_notes = table.loc[
            table["flujo_elemental"].isin(["Carbon dioxide (fossil)", "Methane (fossil)"]),
            "observaciones",
        ]
        self.assertTrue(fossil_notes.str.contains("combustión de diésel", regex=False).all())
        self.assertFalse(fossil_notes.str.contains("?", regex=False).any())

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

    def operational_case(self):
        resources = add_operational_emissions(
            build_inventory(load_parameters(), 26278.725181), load_imn_factors())
        rows = [dict(self.base, Escenario=s, Etapa=e) for s,e in
                [("A",1),("A",2),("A",3),("A",4),("B",1),("B",2)]]
        return pd.DataFrame(rows), resources

    def test_energy_sanity_checks_and_no_double_count(self):
        emissions, resources = self.operational_case()
        result = compute_impacts(emissions, self.factors, 26278.725181, resources)
        for scenario, group in result.groupby("Escenario"):
            for col, expected in {
                "co2_fosil_diesel_kg": 476.8725, "ch4_fosil_diesel_kg": 0.069715,
                "n2o_combustion_diesel_kg": 0.00445665,
                "clima_electricidad_imn_kg_co2eq": 2.209010416666667,
                "clima_diesel_ef31_kg_co2eq": 480.16667245,
                "impacto_calentamiento_global_kg_co2eq": 482.3756828666667,
            }.items():
                self.assertAlmostEqual(group[col].sum(), expected, places=10)
            self.assertEqual(group["clima_manejo_ef31_kg_co2eq"].sum(), 0)
            self.assertEqual(group["n2o_total_kg"].sum(), 0)
            self.assertEqual(group["impacto_eutrofizacion_marina_kg_neq"].sum(), 0)
            self.assertEqual(group["impacto_eutrofizacion_terrestre_mol_neq"].sum(), 0)
        self.assertAlmostEqual(self.factors[("Methane (fossil)", "air unspecified", "Cambio climático")]["factor"], 29.8)
        self.assertAlmostEqual(self.factors[("Methane biogenic", "air unspecified", "Cambio climático")]["factor"], 27)

    def test_duplicate_operational_rows_fail(self):
        emissions, resources = self.operational_case()
        with self.assertRaises(ValueError):
            compute_impacts(emissions, self.factors, 26278.725181, pd.concat([resources, resources.iloc[:1]]))

    def test_imn_wrong_selection_units_year_and_hash_fail(self):
        for column, value in [("categoria_imn", "Generación de electricidad"),
                              ("ano_representado", "2024"), ("unidad_original", "kg CO2/L"),
                              ("estado_seleccion", "Pendiente"), ("sha256_fuente", "0" * 64)]:
            table = pd.read_csv(FACTOR_PATH, keep_default_na=False, dtype=str)
            table.loc[0, column] = value
            with self.subTest(column=column), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "factors.csv"
                table.to_csv(path, index=False, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_imn_factors(path)

    def test_imn_transport_category_rejected(self):
        table = pd.read_csv(FACTOR_PATH, keep_default_na=False, dtype=str)
        table.loc[table["especie_indicador"].eq("CH4"), "categoria_imn"] = "Transporte terrestre/diesel/sin catalizador"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "factors.csv"
            table.to_csv(path, index=False, encoding="utf-8")
            with self.assertRaises(ValueError):
                load_imn_factors(path)

    def test_fossil_formula_cannot_replace_flow_identity(self):
        table = pd.read_csv(self.factor_path)
        table.loc[table["flujo_elemental"].eq("Methane (fossil)"), "flujo_elemental"] = "Methane biogenic"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "factors.csv"
            table.to_csv(path, index=False, encoding="utf-8")
            with self.assertRaises(ValueError):
                load_factors(path)


if __name__ == "__main__":
    unittest.main()
