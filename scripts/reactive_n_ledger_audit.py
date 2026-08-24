"""Productos QA/QC del ledger productivo de N total y TAN.

Este archivo no implementa ecuaciones físicas: consume exclusivamente el
módulo canónico ``reactive_n_ledger``.
"""

from dataclasses import asdict
from pathlib import Path

from reactive_n_ledger import (
    _write,
    build_ledger,
    climate_comparison,
    concentration_comparison,
    n2_sensitivity,
    species_emissions,
    validate,
)


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "outputs" / "auditoria_n_reactivo"


def main() -> None:
    management, applications, experimental = build_ledger()
    validate(management, applications)
    _write(OUTPUT_DIR / "ledger_secuencial_n_tan.csv", [asdict(row) for row in management])
    _write(OUTPUT_DIR / "aplicacion_suelo_n_tan.csv", [asdict(row) for row in applications])
    _write(OUTPUT_DIR / "emisiones_especies_nitrogenadas.csv", species_emissions(management))
    _write(OUTPUT_DIR / "comparacion_concentracion_diluida.csv", concentration_comparison(applications))
    _write(
        OUTPUT_DIR / "comparacion_ipcc_actual_vs_n_propagado.csv",
        climate_comparison(management, applications, experimental),
    )
    a2 = next(row for row in management if row.stage.startswith("A2"))
    _write(OUTPUT_DIR / "sensibilidad_n2_a2.csv", n2_sensitivity(a2))
    residuals = [abs(row.mass_balance_residual_kg) for row in management + applications]
    print(f"QA/QC ledger PASS: 6 etapas; residuo máximo={max(residuals):.3e} kg N")


if __name__ == "__main__":
    main()
