import csv
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


class ReactiveNPipelineOutputTests(unittest.TestCase):
    CHECKPOINT_APPLICATION_EMISSIONS = {
        ("A", "4"): {
            "N2O_ec14": 0.3583129365306038,
            "N2O_ec16": 0.2724744171411512,
            "N2O_ec18": 0.1576576920734657,
            "NH3_ec20": 14.477390563776146,
            "NOx_as_NO2": 1.5201154883116528,
            "NO3_ec21": 40.391640117995344,
        },
        ("B", "2"): {
            "N2O_ec14": 1.0756694504492326,
            "N2O_ec16": 0.8179788577705001,
            "N2O_ec18": 0.4732945581976622,
            "NH3_ec20": 43.461692738369486,
            "NOx_as_NO2": 4.563446153420987,
            "NO3_ec21": 121.2572835051862,
        },
    }

    def test_productive_summary_contains_explicit_nox(self):
        rows = read_rows(ROOT / "processed" / "ACV_resumen_emisiones.csv")
        self.assertEqual(len(rows), 6)
        self.assertIn("NOx_as_NO2", rows[0])
        self.assertGreater(float(next(row for row in rows if row["Escenario"] == "A" and row["Etapa"] == "4")["NOx_as_NO2"]), 0.0)

    def test_productive_ledger_has_six_ordered_stages(self):
        rows = read_rows(ROOT / "processed" / "reactive_n_ledger.csv")
        self.assertEqual([row["stage"][:2] for row in rows], ["A1", "A2", "A3", "A4", "B1", "B2"])
        self.assertIn("n_returned_emep_kg", rows[0])
        self.assertIn("soil_n_remaining_after_direct_losses_kg", rows[0])
        self.assertNotIn("n_total_out_or_soil_kg", rows[0])

    def test_application_emissions_match_promotion_checkpoint(self):
        rows = {(row["Escenario"], row["Etapa"]): row for row in read_rows(ROOT / "processed" / "ACV_resumen_emisiones.csv")}
        for key, expected in self.CHECKPOINT_APPLICATION_EMISSIONS.items():
            for column, value in expected.items():
                self.assertAlmostEqual(float(rows[key][column]), value, places=12)

    def test_total_impacts_match_promotion_checkpoint(self):
        expected = {
            "A": (2333.632194253236, 19.79641718144633),
            "B": (4767.272734106717, 35.98844530101762),
        }
        rows = read_rows(ROOT / "processed" / "acv_impacto_total_por_escenario.csv")
        actual = {row["Escenario"]: row for row in rows}
        for scenario, (gwp, eutrophication) in expected.items():
            self.assertAlmostEqual(float(actual[scenario]["impacto_calentamiento_global_kg_co2eq"]), gwp, places=12)
            self.assertAlmostEqual(float(actual[scenario]["impacto_eutrofizacion_kg_po4eq"]), eutrophication, places=12)

    def test_stage_scripts_only_consume_canonical_ledger(self):
        for path in (ROOT / "scripts").glob("ACV_Escenario*_etapa*.py"):
            source = path.read_text(encoding="utf-8")
            self.assertIn("from reactive_n_ledger import emission_row", source)
            self.assertNotIn("frac_gas", source.lower())
            self.assertNotIn("nh3_direct", source.lower())

    def test_active_classifications_match_decisions(self):
        rows = {(row["escenario"], row["etapa"]): row["sistema_manejo"] for row in read_rows(ROOT / "processed" / "ipcc_sistema_manejo_por_etapa.csv")}
        self.assertEqual(rows[("A", "1")], "composting_pasive")
        self.assertEqual(rows[("A", "3")], "liquid_slurry_without_natural_crust")
        self.assertEqual(rows[("B", "1")], "liquid_slurry_without_natural_crust")
        self.assertEqual(rows[("A", "4")], "land_application_managed_liquid_slurry")
        self.assertEqual(rows[("B", "2")], "land_application_managed_liquid_slurry")

    def test_academic_documents_do_not_present_historical_route(self):
        forbidden = ["Nₑᵤₜ", "50 % como N asociado", "distribución de 50 %", "n_ex_fraction", "uncovered_anaerobic_lagoon"]
        for path in (ROOT / "outputs" / "documentos_tfg").glob("*.docx"):
            with zipfile.ZipFile(path) as archive:
                text = " ".join(
                    archive.read(name).decode("utf-8", errors="ignore")
                    for name in archive.namelist() if name.endswith(".xml")
                )
            for term in forbidden:
                self.assertNotIn(term.lower(), text.lower(), f"{term} aparece en {path.name}")


if __name__ == "__main__":
    unittest.main()
