"""
Orquestador para ejecutar todas las etapas de ACV y regenerar
ACV_resumen_emisiones.csv en una sola corrida.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ETAPAS = [
    "scripts/ACV_EscenarioA_etapa1.py",
    "scripts/ACV_EscenarioA_etapa2.py",
    "scripts/ACV_EscenarioA_etapa3.py",
    "scripts/ACV_EscenarioA_etapa4.py",
    "scripts/ACV_EscenarioB_etapa1.py",
    "scripts/ACV_EscenarioB_etapa2.py",
]

PREPROCESO = [
    "scripts/generate_acv_parametros_escenario_etapa.py",
    "scripts/compute_masa_etapas_escenarios.py",
]

INICIALIZACION_EMISIONES = ["scripts/acv_resumen_emisiones_csv.py", "--initialize"]
VALIDACION_EMISIONES = ["scripts/acv_resumen_emisiones_csv.py", "--validate"]

POSTPROCESO = [
    "scripts/compute_acv_impact_equivalents.py",
    "scripts/ACV_graficos_emisiones.py",
]


def main() -> int:
    base_dir = Path(__file__).resolve().parent
    python_exec = Path(sys.executable)

    print(f"Python: {python_exec}")
    print(f"Working directory: {base_dir}")

    for script in PREPROCESO:
        script_path = base_dir / script
        print(f"\n[RUN] {script}")
        result = subprocess.run([str(python_exec), str(script_path)], cwd=base_dir, check=False)
        if result.returncode != 0:
            print(f"[ERROR] Fallo {script} con codigo {result.returncode}")
            return result.returncode

    print("\n[RUN] Inicialización limpia del resumen de emisiones")
    result = subprocess.run(
        [str(python_exec), *INICIALIZACION_EMISIONES], cwd=base_dir, check=False
    )
    if result.returncode != 0:
        print(f"[ERROR] Falló la inicialización con código {result.returncode}")
        return result.returncode

    for script in ETAPAS:
        script_path = base_dir / script
        if not script_path.exists():
            print(f"[ERROR] No existe: {script_path}")
            return 1

        print(f"\n[RUN] {script}")
        result = subprocess.run(
            [str(python_exec), str(script_path)],
            cwd=base_dir,
            check=False,
        )
        if result.returncode != 0:
            print(f"[ERROR] Fallo {script} con codigo {result.returncode}")
            return result.returncode

    print("\n[RUN] Validación del resumen completo de emisiones")
    result = subprocess.run(
        [str(python_exec), *VALIDACION_EMISIONES], cwd=base_dir, check=False
    )
    if result.returncode != 0:
        print(f"[ERROR] Falló la validación con código {result.returncode}")
        return result.returncode

    for script in POSTPROCESO:
        script_path = base_dir / script
        if not script_path.exists():
            print(f"[ERROR] No existe: {script_path}")
            return 1

        print(f"\n[RUN] {script}")
        result = subprocess.run(
            [str(python_exec), str(script_path)],
            cwd=base_dir,
            check=False,
        )
        if result.returncode != 0:
            print(f"[ERROR] Fallo {script} con codigo {result.returncode}")
            return result.returncode

    resumen_path = base_dir / "processed" / "ACV_resumen_emisiones.csv"
    print(f"\n[OK] Orquestacion completada.")
    print(f"Resumen actualizado: {resumen_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
