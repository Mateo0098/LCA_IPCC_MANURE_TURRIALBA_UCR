from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from extract_analysis_results import (  # noqa: E402
    _normalized_solid_sample_id,
    _sample_number,
)
import build_sampling_ingestion  # noqa: E402
import sampling_ingestion_config  # noqa: E402
from sampling_ingestion_config import (  # noqa: E402
    M3_SOURCE_CONTRACT,
    SOURCES,
    SOURCE_STATE_COMPLETE,
    SOURCE_STATE_DECLARED_INCOMPLETE,
    SOURCE_STATE_NOT_AVAILABLE,
    journey_source_status,
)
from validate_sampling_ingestion import _validate_source_cardinality  # noqa: E402


class M3PreparationTests(unittest.TestCase):
    def test_current_m3_is_explicitly_not_available(self) -> None:
        status = journey_source_status("M3")
        self.assertEqual(status["estado"], SOURCE_STATE_NOT_AVAILABLE)
        self.assertEqual(status["fuentes_declaradas"], 0)

    def test_current_configuration_has_no_fictitious_m3_paths(self) -> None:
        self.assertFalse(any(source.get("jornada") == "M3" for source in SOURCES))
        self.assertTrue(all("path" not in source for source in M3_SOURCE_CONTRACT))

    def test_partial_m3_declaration_is_not_accepted_as_complete(self) -> None:
        with tempfile.TemporaryDirectory(prefix="m3_partial_") as folder:
            root = Path(folder)
            path = root / "lasa.pdf"
            path.touch()
            source = {
                **M3_SOURCE_CONTRACT[0],
                "jornada": "M3",
                "path": path.name,
            }
            status = journey_source_status("M3", [source], root)
        self.assertEqual(status["estado"], SOURCE_STATE_DECLARED_INCOMPLETE)
        self.assertTrue(any("Faltan fuentes" in error for error in status["errores"]))

    def test_partial_m3_is_blocked_before_any_extractor_runs(self) -> None:
        partial = {
            **M3_SOURCE_CONTRACT[0],
            "jornada": "M3",
            "path": "fuente_parcial_que_no_debe_ingerirse.pdf",
        }
        with (
            patch.object(sampling_ingestion_config, "SOURCES", [*SOURCES, partial]),
            patch.object(
                build_sampling_ingestion,
                "extract_cia_normalized",
                side_effect=AssertionError("no debe ejecutarse"),
            ) as cia,
            patch.object(
                build_sampling_ingestion,
                "extract_lasa_normalized",
                side_effect=AssertionError("no debe ejecutarse"),
            ) as lasa,
            patch.object(
                build_sampling_ingestion,
                "extract_gravimetric_normalized",
                side_effect=AssertionError("no debe ejecutarse"),
            ) as gravimetric,
        ):
            with self.assertRaisesRegex(ValueError, "Configuración de fuentes no apta"):
                build_sampling_ingestion.ingest_all()
        cia.assert_not_called()
        lasa.assert_not_called()
        gravimetric.assert_not_called()

    def test_complete_m3_declaration_requires_five_real_compatible_sources(self) -> None:
        with tempfile.TemporaryDirectory(prefix="m3_complete_") as folder:
            root = Path(folder)
            sources = []
            for index, contract in enumerate(M3_SOURCE_CONTRACT, start=1):
                relative = Path(f"source_{index}.dat")
                (root / relative).touch()
                sources.append(
                    {
                        **contract,
                        "jornada": "M3",
                        "path": str(relative),
                        "sampling_date": "2026-10-05",
                        "fuente_metodo": "fuente metodológica real",
                        "uso_modelo": "elegible",
                        "motivo_uso": "fuente M3 compatible",
                        "condicion_muestra": "condición real documentada",
                        "nota_precision": "precisión documentada por CIA",
                    }
                )
            status = journey_source_status("M3", sources, root)
        self.assertEqual(status["estado"], SOURCE_STATE_COMPLETE)
        self.assertEqual(status["errores"], [])

    def test_m3_liquid_requires_n_total_for_each_composite_sample(self) -> None:
        source = {
            **M3_SOURCE_CONTRACT[2],
            "jornada": "M3",
            "path": "informe_real.xlsx",
        }
        rows = [
            {
                "identificador_muestra": f"M3-AV-{number}",
                "tipo_material": "aguas verdes",
                "variable": "densidad",
                "replica_analitica": "",
            }
            for number in (1, 2, 3)
        ]
        rows.extend(
            {
                "identificador_muestra": f"M3-AV-{number}",
                "tipo_material": "aguas verdes",
                "variable": "N total",
                "replica_analitica": "",
            }
            for number in (1, 2)
        )
        errors: list[str] = []
        _validate_source_cardinality(errors, source, rows)
        self.assertTrue(
            any("N total: 2 muestras con resultado; esperadas 3" in error for error in errors)
        )

    def test_combined_report_cannot_be_simulated_with_duplicated_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="m3_duplicate_") as folder:
            root = Path(folder)
            shared = root / "combined.dat"
            shared.touch()
            sources = [
                {
                    **contract,
                    "jornada": "M3",
                    "path": shared.name,
                    "sampling_date": "2026-10-05",
                    "fuente_metodo": "fuente metodológica real",
                    "uso_modelo": "elegible",
                    "motivo_uso": "fuente M3 compatible",
                    "condicion_muestra": "condición real documentada",
                    "nota_precision": "precisión documentada por CIA",
                }
                for contract in M3_SOURCE_CONTRACT
            ]
            status = journey_source_status("M3", sources, root)
        self.assertEqual(status["estado"], SOURCE_STATE_DECLARED_INCOMPLETE)
        self.assertTrue(any("duplicando rutas" in error for error in status["errores"]))

    def test_m3_report_labels_preserve_composite_sample_number(self) -> None:
        self.assertEqual(_sample_number("SOL: PRECOMPOSTADO - 3-2", "M3", 99), 2)
        self.assertEqual(_sample_number("LIQ: AGUAS VERDES - 3,3", "M3", 99), 3)

    def test_sample_number_preserves_history_and_ignores_unrelated_m3_numbers(self) -> None:
        self.assertEqual(_sample_number("Muestra fresca 2", "M1", 99), 2)
        self.assertEqual(_sample_number("SOL: FRESCO - 2-3", "M2", 99), 3)
        self.assertEqual(_sample_number("LOTE 2026", "M3", 7), 7)

    def test_m3_solid_identity_is_shared_between_laboratories(self) -> None:
        bio = _normalized_solid_sample_id(
            {"jornada": "M3", "laboratorio": "Bioenergía"},
            "estiércol fresco",
            1,
        )
        lasa = _normalized_solid_sample_id(
            {"jornada": "M3", "laboratorio": "LASA"},
            "estiércol fresco",
            1,
        )
        self.assertEqual(bio, "M3-EF-1")
        self.assertEqual(bio, lasa)


if __name__ == "__main__":
    unittest.main()
