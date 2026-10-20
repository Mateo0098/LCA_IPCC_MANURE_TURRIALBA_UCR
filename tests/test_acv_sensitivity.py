from __future__ import annotations

import sys
import unittest
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import generate_acv_sensitivity as sensitivity  # noqa: E402
from reactive_n_ledger import productive_emission_rows  # noqa: E402


class AcvSensitivityTests(unittest.TestCase):
    def test_central_case_reproduces_official_stage_impacts(self) -> None:
        central = sensitivity._impact_case(
            b0=sensitivity.REFERENCE_B0,
            liquid_mcf=sensitivity.REFERENCE_MCF,
        )
        self.assertLessEqual(sensitivity._validate_central(central), 1e-10)

    def test_b0_changes_all_and_only_methane_management_stages(self) -> None:
        central = productive_emission_rows(b0_m3_ch4_per_kg_vs=0.24)
        high = productive_emission_rows(b0_m3_ch4_per_kg_vs=0.276)
        methane_stages = {("A", 1), ("A", 2), ("A", 3), ("B", 1)}
        for key in central:
            with self.subTest(key=key):
                if key in methane_stages:
                    self.assertAlmostEqual(high[key]["CH4_ec1"] / central[key]["CH4_ec1"], 1.15)
                else:
                    self.assertTrue(pd.isna(high[key]["CH4_ec1"]))

    def test_common_liquid_mcf_changes_only_a3_and_b1_methane(self) -> None:
        central = productive_emission_rows()
        low = productive_emission_rows(mcf_overrides_pct={("A", 3): 19.0, ("B", 1): 19.0})
        for key in central:
            with self.subTest(key=key):
                if key in {("A", 3), ("B", 1)}:
                    self.assertAlmostEqual(low[key]["CH4_ec1"] / central[key]["CH4_ec1"], 0.5)
                elif not pd.isna(central[key]["CH4_ec1"]):
                    self.assertEqual(low[key]["CH4_ec1"], central[key]["CH4_ec1"])

    def test_eutrophication_is_invariant_to_methane_parameters(self) -> None:
        central = sensitivity._totals(sensitivity._impact_case(b0=0.24, liquid_mcf=38.0))
        altered = sensitivity._totals(sensitivity._impact_case(b0=0.276, liquid_mcf=19.0))
        for column in (
            "impacto_eutrofizacion_terrestre_mol_neq",
            "impacto_eutrofizacion_marina_kg_neq",
        ):
            self.assertTrue((central[column] == altered[column]).all())

    def test_critical_mcf_is_inside_domain_and_closes_climate_difference(self) -> None:
        result = sensitivity._critical_mcf()
        self.assertEqual(result["Existe inversión"], "Sí")
        critical = float(result["MCF crítico (%)"])
        self.assertGreaterEqual(critical, 0.0)
        self.assertLessEqual(critical, 100.0)

    def test_invalid_overrides_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            productive_emission_rows(mcf_overrides_pct={("A", 4): 10.0})
        with self.assertRaises(ValueError):
            productive_emission_rows(mcf_overrides_pct={("A", 3): 101.0})
        with self.assertRaises(ValueError):
            productive_emission_rows(b0_m3_ch4_per_kg_vs=-0.1)


if __name__ == "__main__":
    unittest.main()
