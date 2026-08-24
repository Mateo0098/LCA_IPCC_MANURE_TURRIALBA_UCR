import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("reactive_n_ledger", ROOT / "scripts" / "reactive_n_ledger.py")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ReactiveNLedgerTests(unittest.TestCase):
    def setUp(self):
        self.management, self.applications, self.experimental = MODULE.build_ledger()
        self.m = {row.stage[:2]: row for row in self.management}
        self.a = {row.stage[:2]: row for row in self.applications}
        self.p, _, _ = MODULE.load_inputs()

    def test_mass_conservation_and_nonnegative_pools(self):
        MODULE.validate(self.management, self.applications)

    def test_ipcc_direct_n2o_reduces_total_but_not_tan(self):
        a1 = self.m["A1"]
        expected_tan = a1.tan_in_kg - a1.nh3_n_kg - a1.no_n_kg - a1.n2_n_kg
        self.assertAlmostEqual(a1.tan_out_kg, expected_tan)
        self.assertIn(a1.n2o_n_direct_ipcc_kg, [a1.n_total_in_kg * self.p["a1_ef3"]])

    def test_a1_water_loss_reduces_total_not_tan(self):
        a1 = self.m["A1"]
        tan_without_ipcc_losses = a1.tan_in_kg - a1.nh3_n_kg - a1.no_n_kg - a1.n2_n_kg
        self.assertAlmostEqual(a1.tan_out_kg, tan_without_ipcc_losses)
        self.assertAlmostEqual(a1.water_n_loss_ipcc_kg, a1.n_total_in_kg * self.p["a1_frac_leach_ms"])

    def test_no_proportional_water_partition_exists(self):
        source = (ROOT / "scripts" / "reactive_n_ledger.py").read_text(encoding="utf-8")
        self.assertNotIn("tan_water", source)
        self.assertNotIn("organic_water", source)

    def test_emep_losses_reduce_tan_and_total(self):
        for row in self.management:
            emep = row.nh3_n_kg + row.no_n_kg + row.n2_n_kg
            self.assertAlmostEqual(row.tan_out_kg, row.tan_available_kg - emep)
            self.assertAlmostEqual(row.n_total_out_kg, row.n_total_in_kg - emep - row.n2o_n_direct_ipcc_kg - row.water_n_loss_ipcc_kg)

    def test_tan_never_exceeds_total(self):
        for row in self.management:
            self.assertLessEqual(row.tan_out_kg, row.n_total_out_kg)
        for row in self.applications:
            self.assertLessEqual(row.tan_after_application_kg, row.n_returned_after_atmospheric_losses_kg)

    def test_direct_n2o_is_debited_once(self):
        for row in self.management:
            reconstructed = row.n_total_out_kg + row.nh3_n_kg + row.no_n_kg + row.n2_n_kg + row.n2o_n_direct_ipcc_kg + row.water_n_loss_ipcc_kg
            self.assertAlmostEqual(reconstructed, row.n_total_in_kg)

    def test_slurry_ef3_and_leaching_are_zero(self):
        for key in ("A3", "B1"):
            self.assertEqual(self.m[key].n2o_n_direct_ipcc_kg, 0.0)
            self.assertEqual(self.m[key].water_n_loss_ipcc_kg, 0.0)

    def test_slurry_default_mineralisation_remains_active(self):
        self.assertEqual(self.p["emep_slurry_mineralisation_fraction"], 0.10)
        for key in ("A3", "B1"):
            expected = self.m[key].non_tan_n_in_kg * 0.10
            self.assertAlmostEqual(self.m[key].mineralised_n_kg, expected)

    def test_applications_receive_exact_storage_outputs(self):
        for storage, application in (("A3", "A4"), ("B1", "B2")):
            self.assertEqual(self.a[application].n_applic_kg, self.m[storage].n_total_out_kg)
            self.assertEqual(self.a[application].tan_applic_kg, self.m[storage].tan_out_kg)

    def test_application_nh3_uses_tan_and_055(self):
        for row in self.applications:
            self.assertAlmostEqual(row.nh3_n_app_kg, row.tan_applic_kg * 0.55)

    def test_application_nox_uses_official_total_n_basis(self):
        for row in self.applications:
            self.assertAlmostEqual(row.no2_reported_kg, row.n_applic_kg * 0.04)
            self.assertAlmostEqual(row.nox_n_app_kg, row.no2_reported_kg * 14.0 / 46.0)

    def test_ef4_uses_explicit_precursor(self):
        for row in self.management:
            self.assertAlmostEqual(row.n2o_n_indirect_vol_kg, (row.nh3_n_kg + row.no_n_kg) * self.p["ef4_ipcc"])
        for row in self.applications:
            self.assertAlmostEqual(row.n2o_n_indirect_vol_kg, (row.nh3_n_app_kg + row.nox_n_app_kg) * self.p["ef4_ipcc"])

    def test_no_artificial_fifty_fifty(self):
        productive_sources = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (ROOT / "scripts").glob("*.py")
            if path.name != "generate_methodology_docx.py"
        )
        self.assertNotIn("def nh3_direct_mm", productive_sources)
        self.assertNotIn("def no3_direct_mm", productive_sources)
        source = (ROOT / "scripts" / "reactive_n_ledger.py").read_text(encoding="utf-8")
        self.assertNotIn("0.5 *", source)
        self.assertNotIn("* 0.5", source)

    def test_nitrate_only_comes_from_water_path(self):
        self.assertAlmostEqual(self.m["A1"].no3_from_soil_leach_kg, self.m["A1"].soil_leach_runoff_n_kg * 62.0 / 14.0)
        for row in self.applications:
            self.assertAlmostEqual(row.no3_leach_runoff_kg, row.n_leach_runoff_kg * 62.0 / 14.0)

    def test_stoichiometric_conversions(self):
        self.assertAlmostEqual(MODULE.KG_N_TO_NH3, 17.0 / 14.0)
        self.assertAlmostEqual(MODULE.KG_NO2_TO_N, 14.0 / 46.0)
        self.assertAlmostEqual(MODULE.KG_N_TO_N2O, 44.0 / 28.0)
        self.assertAlmostEqual(MODULE.KG_N_TO_NO3, 62.0 / 14.0)

    def test_physical_chains_are_independent(self):
        self.assertNotAlmostEqual(self.m["A3"].n_total_in_kg, self.m["A1"].n_total_out_kg)
        self.assertGreater(self.m["B1"].n_total_in_kg, self.m["A3"].n_total_in_kg)

    def test_diluted_concentration_reproduces_mass_flow(self):
        comparisons = MODULE.concentration_comparison(self.applications)
        for item, app in zip(comparisons, self.applications, strict=True):
            reconstructed = item["modelled_n_mass_fraction"] * item["theoretical_mixture_mass_kg"]
            self.assertAlmostEqual(reconstructed, app.n_applic_kg)

    def test_komakech_nh3_does_not_exceed_a2_tan(self):
        self.assertLessEqual(self.m["A2"].nh3_n_kg, self.m["A2"].tan_in_kg)

    def test_application_ipcc_bases_remain_n_applied(self):
        for row in self.applications:
            self.assertAlmostEqual(row.n2o_n_direct_soil_kg, row.n_applic_kg * self.p["soil_ef1"])
            self.assertAlmostEqual(row.n_leach_runoff_kg, row.n_applic_kg * self.p["soil_frac_leach"])

    def test_tan_is_initialized_only_at_fresh_boundaries(self):
        self.assertAlmostEqual(self.m["A1"].tan_in_kg, self.m["A1"].n_total_in_kg * 0.60)
        self.assertAlmostEqual(self.m["A3"].tan_in_kg, self.m["A3"].n_total_in_kg * 0.60)
        self.assertAlmostEqual(self.m["B1"].tan_in_kg, self.m["B1"].n_total_in_kg * 0.60)
        self.assertEqual(self.m["A2"].tan_in_kg, self.m["A1"].tan_out_kg)

    def test_intermediate_measurements_do_not_reset_productive_inputs(self):
        self.assertNotAlmostEqual(self.m["A2"].n_total_in_kg, self.experimental["A2"])
        self.assertNotAlmostEqual(self.a["A4"].n_applic_kg, self.experimental["A4"])
        self.assertNotAlmostEqual(self.a["B2"].n_applic_kg, self.experimental["B2"])

    def test_indirect_n2o_is_not_subtracted_from_nitrate(self):
        for row in self.applications:
            self.assertAlmostEqual(row.no3_leach_runoff_kg, row.n_leach_runoff_kg * 62.0 / 14.0)

    def test_productive_emissions_match_ledger(self):
        rows = MODULE.productive_emission_rows()
        self.assertAlmostEqual(rows[("A", 1)]["NH3_ec12"], self.m["A1"].nh3_n_kg * 17.0 / 14.0)
        self.assertAlmostEqual(rows[("A", 4)]["NOx_as_NO2"], self.a["A4"].no2_reported_kg)
        self.assertAlmostEqual(rows[("B", 2)]["NO3_ec21"], self.a["B2"].no3_leach_runoff_kg)

    def test_fracgas_does_not_create_productive_volatilisation(self):
        source = (ROOT / "scripts" / "reactive_n_ledger.py").read_text(encoding="utf-8")
        emission_section = source[source.index("def productive_emission_rows"):]
        self.assertNotIn("frac_gas_ms_benchmark", emission_section)
        self.assertNotIn("soil_frac_gas_current", emission_section)


if __name__ == "__main__":
    unittest.main()
