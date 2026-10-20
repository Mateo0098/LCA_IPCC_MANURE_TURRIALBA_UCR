"""Ledger productivo y secuencial de N total y TAN del ACV.

Esta es la única implementación de las ecuaciones físicas de N reactivo para
A1→A2, A3→A4 y B1→B2. Todos los balances se realizan en kg N/año.
"""

from __future__ import annotations

import csv
import math
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PARAMETERS = ROOT / "processed" / "reactive_n_ledger_parameters.csv"
ACV_PARAMETERS = ROOT / "processed" / "acv_parametros_escenario_etapa.csv"
MASSES = ROOT / "processed" / "masa_total_escenario_etapa.csv"
PRODUCTIVE_LEDGER = ROOT / "processed" / "reactive_n_ledger.csv"

KG_N_TO_NH3 = 17.0 / 14.0
KG_NO2_TO_N = 14.0 / 46.0
KG_N_TO_N2O = 44.0 / 28.0
KG_N_TO_NO3 = 62.0 / 14.0
TOLERANCE = 1e-9


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_inputs() -> tuple[dict[str, float], dict[tuple[str, int], dict[str, str]], dict[tuple[str, int], dict[str, str]]]:
    params = {row["parameter"]: float(row["value"]) for row in _read_rows(PARAMETERS)}
    chemistry = {(row["escenario"], int(row["etapa"])): row for row in _read_rows(ACV_PARAMETERS)}
    masses = {(row["escenario"], int(row["etapa"])): row for row in _read_rows(MASSES)}
    return params, chemistry, masses


def wet_n_fraction(row: dict[str, str]) -> float:
    fraction = float(row["n_ex_pct"]) / 100.0
    if row["transformacion_n_acv"] == "multiplicar_por_fraccion_materia_seca_gravimetrica_TFG_105C":
        fraction *= float(row["materia_seca_pct"]) / 100.0
    return fraction


@dataclass
class ManagementRow:
    chain: str
    stage: str
    n_total_in_kg: float
    tan_in_kg: float
    non_tan_n_in_kg: float
    mineralised_n_kg: float
    tan_available_kg: float
    nh3_n_kg: float
    no_n_kg: float
    n2_n_kg: float
    n2o_n_direct_ipcc_kg: float
    water_n_loss_ipcc_kg: float
    n_total_out_kg: float
    tan_out_kg: float
    non_tan_n_out_kg: float
    derived_n_reference_kg: float | None
    derived_reference_kind: str
    derived_reference_basis: str
    model_minus_derived_reference_kg: float | None
    relative_difference_vs_derived_reference_pct: float | None
    frac_gas_modelled: float
    frac_gas_ms_benchmark: float
    frac_gas_difference: float
    n2o_n_indirect_vol_kg: float
    n2o_indirect_vol_kg: float
    soil_leach_runoff_n_kg: float
    n2o_n_indirect_leach_kg: float
    n2o_indirect_leach_kg: float
    no3_from_soil_leach_kg: float
    mass_balance_residual_kg: float


@dataclass
class ApplicationRow:
    chain: str
    stage: str
    n_applic_kg: float
    tan_applic_kg: float
    nh3_n_app_kg: float
    nh3_app_kg: float
    no2_reported_kg: float
    nox_n_app_kg: float
    n2o_n_direct_soil_kg: float
    n2o_direct_soil_kg: float
    n_precursor_vol_kg: float
    n2o_n_indirect_vol_kg: float
    n2o_indirect_vol_kg: float
    n_leach_runoff_kg: float
    no3_leach_runoff_kg: float
    n2o_n_indirect_leach_kg: float
    n2o_indirect_leach_kg: float
    n_returned_emep_kg: float
    tan_after_application_kg: float
    soil_n_remaining_after_direct_losses_kg: float
    mass_balance_residual_kg: float


def _management_stage(
    *, chain: str, stage: str, n_total_in: float, tan_in: float,
    mineralised_n: float, nh3_n: float, no_n: float, n2_n: float,
    n2o_n_direct: float, water_n_loss: float, frac_gas_benchmark: float,
    ef4: float, ef5: float, derived_reference_n: float | None = None,
    derived_reference_kind: str = "no_aplica",
    derived_reference_basis: str = "Sin referencia derivada para esta etapa.",
    soil_frac_leach: float = 0.0,
) -> ManagementRow:
    if not 0.0 <= tan_in <= n_total_in:
        raise ValueError(f"TAN de entrada fuera de N total en {stage}")
    non_tan_in = n_total_in - tan_in
    if not 0.0 <= mineralised_n <= non_tan_in:
        raise ValueError(f"Mineralización inválida en {stage}")
    tan_available = tan_in + mineralised_n
    emep_tan_losses = nh3_n + no_n + n2_n
    if emep_tan_losses > tan_available + TOLERANCE:
        raise ValueError(f"Las pérdidas EMEP exceden TAN en {stage}")
    tan_out = tan_available - emep_tan_losses
    n_total_out = n_total_in - emep_tan_losses - n2o_n_direct - water_n_loss
    non_tan_out = n_total_out - tan_out
    if n_total_out < -TOLERANCE or tan_out < -TOLERANCE or non_tan_out < -TOLERANCE:
        raise ValueError(f"Pool negativo en {stage}")
    residual = n_total_in - (
        nh3_n + no_n + n2_n + n2o_n_direct + water_n_loss + n_total_out
    )
    precursor = nh3_n + no_n
    indirect_vol_n = precursor * ef4
    soil_leach_n = water_n_loss * soil_frac_leach
    indirect_leach_n = soil_leach_n * ef5
    difference = None if derived_reference_n is None else n_total_out - derived_reference_n
    relative = (
        None
        if derived_reference_n in (None, 0.0)
        else difference / derived_reference_n * 100.0
    )
    frac_gas = precursor / n_total_in if n_total_in else 0.0
    return ManagementRow(
        chain, stage, n_total_in, tan_in, non_tan_in, mineralised_n,
        tan_available, nh3_n, no_n, n2_n, n2o_n_direct, water_n_loss,
        n_total_out, tan_out, non_tan_out, derived_reference_n,
        derived_reference_kind, derived_reference_basis, difference, relative,
        frac_gas, frac_gas_benchmark, frac_gas - frac_gas_benchmark,
        indirect_vol_n, indirect_vol_n * KG_N_TO_N2O, soil_leach_n,
        indirect_leach_n, indirect_leach_n * KG_N_TO_N2O,
        soil_leach_n * KG_N_TO_NO3, residual,
    )


def _soil_application(chain: str, stage: str, n_applic: float, tan_applic: float, p: dict[str, float]) -> ApplicationRow:
    if not 0.0 <= tan_applic <= n_applic:
        raise ValueError(f"TAN aplicado fuera de N total en {stage}")
    nh3_n = tan_applic * p["emep_application_nh3_n_fraction_tan"]
    no2 = n_applic * p["emep_soil_no2_fraction_n_applied"]
    nox_n = no2 * KG_NO2_TO_N
    direct_n = n_applic * p["soil_ef1"]
    precursor = nh3_n + nox_n
    indirect_vol_n = precursor * p["ef4_ipcc"]
    leach_n = n_applic * p["soil_frac_leach"]
    indirect_leach_n = leach_n * p["ef5_ipcc"]
    # EMEP mreturned_N descuenta únicamente el NH3-N de aplicación. Las demás
    # rutas conservan N_applic como base y se reflejan solo en el cierre físico.
    n_returned_emep = n_applic - nh3_n
    tan_after = tan_applic - nh3_n
    soil_remaining = n_applic - nh3_n - nox_n - direct_n - leach_n
    residual = n_applic - (nh3_n + nox_n + direct_n + leach_n + soil_remaining)
    if (
        min(n_returned_emep, tan_after, soil_remaining) < -TOLERANCE
        or tan_after > n_returned_emep + TOLERANCE
        or n_returned_emep > n_applic + TOLERANCE
        or soil_remaining > n_returned_emep + TOLERANCE
    ):
        raise ValueError(f"Balance de aplicación inválido en {stage}")
    return ApplicationRow(
        chain, stage, n_applic, tan_applic, nh3_n, nh3_n * KG_N_TO_NH3,
        no2, nox_n, direct_n, direct_n * KG_N_TO_N2O, precursor,
        indirect_vol_n, indirect_vol_n * KG_N_TO_N2O, leach_n,
        leach_n * KG_N_TO_NO3, indirect_leach_n,
        indirect_leach_n * KG_N_TO_N2O, n_returned_emep, tan_after,
        soil_remaining, residual,
    )


def build_ledger() -> tuple[list[ManagementRow], list[ApplicationRow], dict[str, float]]:
    p, chemistry, masses = load_inputs()
    fresh_fraction = wet_n_fraction(chemistry[("A", 1)])
    fresh_n_a1 = float(masses[("A", 1)]["masa_total_kg_eq"]) * fresh_fraction
    fresh_n_a3 = float(masses[("A", 3)]["masa_total_kg_eq"]) * fresh_fraction
    fresh_n_b1 = float(masses[("B", 1)]["masa_total_kg_eq"]) * fresh_fraction
    derived_references = {
        "A2": float(masses[("A", 2)]["masa_total_kg_eq"]) * wet_n_fraction(chemistry[("A", 2)]),
        "A4": float(masses[("A", 4)]["masa_total_kg_eq"]) * wet_n_fraction(chemistry[("A", 4)]),
        "B2": float(masses[("B", 2)]["masa_total_kg_eq"]) * wet_n_fraction(chemistry[("B", 2)]),
    }
    tan_a1 = fresh_n_a1 * p["fresh_manure_tan_fraction"]
    a1 = _management_stage(
        chain="A1→A2", stage="A1: Precomposteo", n_total_in=fresh_n_a1, tan_in=tan_a1,
        mineralised_n=0.0, nh3_n=tan_a1 * p["emep_solid_nh3_n_fraction_tan"],
        no_n=tan_a1 * p["emep_solid_no_n_fraction_tan"],
        n2_n=tan_a1 * p["emep_solid_n2_n_fraction_tan"],
        n2o_n_direct=fresh_n_a1 * p["a1_ef3"],
        water_n_loss=fresh_n_a1 * p["a1_frac_leach_ms"],
        frac_gas_benchmark=p["a1_frac_gas_ms_benchmark"], ef4=p["ef4_ipcc"],
        ef5=p["ef5_ipcc"], derived_reference_n=derived_references["A2"],
        derived_reference_kind="benchmark_parcial_masa_a2_inferida",
        derived_reference_basis=(
            "N Dumas del precompostado convertido a base húmeda y multiplicado "
            "por la masa A2 inferida mediante conservación supuesta de cenizas; "
            "no es una masa de salida medida directamente."
        ),
        soil_frac_leach=p["soil_frac_leach"],
    )
    a2_mass = float(masses[("A", 2)]["masa_total_kg_eq"])
    a2_nh3_n = a2_mass / 1000.0 * p["komakech_nh3_factor"] / 1000.0 / KG_N_TO_NH3
    a2 = _management_stage(
        chain="A1→A2", stage="A2: Lombricompostaje", n_total_in=a1.n_total_out_kg,
        tan_in=a1.tan_out_kg, mineralised_n=0.0, nh3_n=a2_nh3_n,
        no_n=a1.tan_out_kg * p["emep_solid_no_n_fraction_tan"],
        n2_n=a1.tan_out_kg * p["emep_solid_n2_n_fraction_tan"],
        n2o_n_direct=a1.n_total_out_kg * p["a2_ef3"], water_n_loss=0.0,
        frac_gas_benchmark=p["a2_frac_gas_ms_benchmark"], ef4=p["ef4_ipcc"], ef5=p["ef5_ipcc"],
    )

    def slurry(chain: str, stage: str, n_total: float, derived_reference_n: float) -> ManagementRow:
        tan = n_total * p["fresh_manure_tan_fraction"]
        mineralised = (n_total - tan) * p["emep_slurry_mineralisation_fraction"]
        tan_available = tan + mineralised
        return _management_stage(
            chain=chain, stage=stage, n_total_in=n_total, tan_in=tan,
            mineralised_n=mineralised,
            nh3_n=tan_available * p["emep_slurry_nh3_n_fraction_tan"],
            no_n=tan_available * p["emep_slurry_no_n_fraction_tan"],
            n2_n=tan_available * p["emep_slurry_n2_n_fraction_tan"],
            n2o_n_direct=n_total * p["slurry_ef3"], water_n_loss=0.0,
            frac_gas_benchmark=p["slurry_frac_gas_ms_benchmark"],
            ef4=p["ef4_ipcc"], ef5=p["ef5_ipcc"],
            derived_reference_n=derived_reference_n,
            derived_reference_kind="escenario_teorico_dilucion_liquida_m2",
            derived_reference_basis=(
                "Concentración experimental M2 multiplicada por la masa anual "
                "teórica de mezcla; no es una descarga ni una masa anual de N medida."
            ),
        )

    a3 = slurry("A3→A4", "A3: Almacenamiento de aguas verdes", fresh_n_a3, derived_references["A4"])
    b1 = slurry("B1→B2", "B1: Almacenamiento de purines", fresh_n_b1, derived_references["B2"])
    a4 = _soil_application("A3→A4", "A4: Aplicación de aguas verdes en campos de pastoreo", a3.n_total_out_kg, a3.tan_out_kg, p)
    b2 = _soil_application("B1→B2", "B2: Aplicación de purines en campo de pastoreo", b1.n_total_out_kg, b1.tan_out_kg, p)
    return [a1, a2, a3, b1], [a4, b2], derived_references


def concentration_comparison(applications: list[ApplicationRow]) -> list[dict[str, float | str]]:
    _, chemistry, masses = load_inputs()
    output: list[dict[str, float | str]] = []
    for row, key in zip(applications, (("A", 4), ("B", 2)), strict=True):
        mixture_mass = float(masses[key]["masa_total_kg_eq"])
        model_fraction = row.n_applic_kg / mixture_mass
        measured_m2_pct = float(chemistry[key]["n_ex_pct"])
        model_pct = model_fraction * 100.0
        difference = model_pct - measured_m2_pct
        output.append({
            "stage": row.stage,
            "manure_mass_kg_per_year": float(masses[key]["boniga_kg"]),
            "washing_water_l_per_year": float(masses[key]["agua_l"]),
            "theoretical_annual_mixture_mass_kg": mixture_mass,
            "propagated_n_kg_per_year": row.n_applic_kg,
            "modelled_n_mass_fraction_on_theoretical_mixture": model_fraction,
            "modelled_n_pct_on_theoretical_mixture": model_pct,
            "measured_m2_n_pct": measured_m2_pct,
            "difference_model_minus_m2_percentage_points": difference,
            "relative_difference_vs_m2_pct": difference / measured_m2_pct * 100.0,
            "measured_basis": "Concentración de N total medida por CIA en muestras M2.",
            "modelled_basis": (
                "N propagado dividido entre una masa anual teórica de mezcla; "
                "no usa una descarga real de efluente medida."
            ),
            "interpretation": (
                "Contraste diagnóstico de concentración y dilución. La diferencia "
                "no demuestra una pérdida física de N, no valida factores EMEP/EEA "
                "y no constituye una validación experimental del flujo anual."
            ),
        })
    return output


def climate_comparison(
    management: list[ManagementRow],
    applications: list[ApplicationRow],
    derived_references: dict[str, float],
) -> list[dict[str, float | str]]:
    p, _, _ = load_inputs()
    by_stage = {row.stage[:2]: row for row in management}
    app_by_stage = {row.stage[:2]: row for row in applications}
    comparisons: list[dict[str, float | str]] = []

    def append(
        stage: str,
        reference_n: float,
        sequential_n: float,
        reference_direct_n: float,
        reference_indirect_n: float,
        sequential_direct_n: float,
        sequential_indirect_n: float,
        note: str,
    ) -> None:
        reference_n2o = (reference_direct_n + reference_indirect_n) * KG_N_TO_N2O
        sequential_n2o = (sequential_direct_n + sequential_indirect_n) * KG_N_TO_N2O
        reference_climate = reference_n2o * p["gwp_n2o"]
        sequential_climate = sequential_n2o * p["gwp_n2o"]
        comparisons.append({
            "stage": stage,
            "comparison_scope": "Comparación entre formulación anterior de referencia y formulación secuencial vigente; no es validación experimental.",
            "reference_formulation_n_input_kg": reference_n,
            "sequential_formulation_n_input_kg": sequential_n,
            "n_input_absolute_difference_kg": sequential_n - reference_n,
            "n_input_relative_difference_pct": (sequential_n / reference_n - 1.0) * 100.0,
            "reference_formulation_direct_n2o_kg": reference_direct_n * KG_N_TO_N2O,
            "sequential_formulation_direct_n2o_kg": sequential_direct_n * KG_N_TO_N2O,
            "reference_formulation_indirect_n2o_kg": reference_indirect_n * KG_N_TO_N2O,
            "sequential_formulation_indirect_n2o_kg": sequential_indirect_n * KG_N_TO_N2O,
            "reference_formulation_n2o_climate_kg_co2_eq": reference_climate,
            "sequential_formulation_n2o_climate_kg_co2_eq": sequential_climate,
            "climate_absolute_difference_kg_co2_eq": sequential_climate - reference_climate,
            "climate_relative_difference_pct": (sequential_climate / reference_climate - 1.0) * 100.0,
            "comparison_note": note,
        })

    a2 = by_stage["A2"]
    append(a2.stage, derived_references["A2"], a2.n_total_in_kg,
           derived_references["A2"] * p["a2_ef3"], derived_references["A2"] * p["a2_frac_gas_ms_benchmark"] * p["ef4_ipcc"],
           a2.n2o_n_direct_ipcc_kg, a2.n2o_n_indirect_vol_kg,
           "Formulación anterior de referencia: benchmark parcial derivado de A2 y FracGasMS; formulación secuencial vigente: N de A1 y precursor explícito Komakech+EMEP. Ninguna diferencia constituye una medición directa de pérdida.")
    for key in ("A4", "B2"):
        app = app_by_stage[key]
        current_n = derived_references[key]
        current_indirect = current_n * (p["soil_frac_gas_current"] * p["ef4_ipcc"] + p["soil_frac_leach"] * p["ef5_ipcc"])
        target_indirect = app.n2o_n_indirect_vol_kg + app.n2o_n_indirect_leach_kg
        append(app.stage, current_n, app.n_applic_kg, current_n * p["soil_ef1"], current_indirect,
               app.n2o_n_direct_soil_kg, target_indirect,
               "Formulación anterior de referencia: masa de N construida con concentración M2 y mezcla anual teórica, más volatilización histórica; formulación secuencial vigente: N/TAN de almacenamiento y NH3-N+NOx-N explícitos. La referencia no es una masa anual observada.")
    return comparisons


def n2_sensitivity(a2: ManagementRow) -> list[dict[str, float]]:
    return [{
        "emep_n2_factor_fraction_tan": factor,
        "n2_n_kg": a2.tan_in_kg * factor,
        "n_total_out_kg": a2.n_total_out_kg + a2.n2_n_kg - a2.tan_in_kg * factor,
        "tan_out_kg": a2.tan_out_kg + a2.n2_n_kg - a2.tan_in_kg * factor,
        "change_vs_central_n_total_out_kg": a2.n2_n_kg - a2.tan_in_kg * factor,
        "change_vs_central_pct_n_total_in": (a2.n2_n_kg - a2.tan_in_kg * factor) / a2.n_total_in_kg * 100.0,
    } for factor in (0.0, 0.15, 0.30)]


def species_emissions(rows: list[ManagementRow]) -> list[dict[str, float | str]]:
    return [{
        "chain": row.chain, "stage": row.stage,
        "nh3_n_kg": row.nh3_n_kg, "nh3_kg": row.nh3_n_kg * KG_N_TO_NH3,
        "no_n_kg": row.no_n_kg, "n2_n_kg": row.n2_n_kg, "n2_kg": row.n2_n_kg,
        "n2o_n_direct_kg": row.n2o_n_direct_ipcc_kg,
        "n2o_direct_kg": row.n2o_n_direct_ipcc_kg * KG_N_TO_N2O,
        "n2o_n_indirect_vol_kg": row.n2o_n_indirect_vol_kg,
        "n2o_indirect_vol_kg": row.n2o_indirect_vol_kg,
        "n2o_n_indirect_leach_kg": row.n2o_n_indirect_leach_kg,
        "n2o_indirect_leach_kg": row.n2o_indirect_leach_kg,
    } for row in rows]


def productive_ledger_rows(
    management: list[ManagementRow], applications: list[ApplicationRow]
) -> list[dict[str, float | str]]:
    """Normaliza los seis balances para la salida productiva y trazable."""
    rows: list[dict[str, float | str]] = []
    for row in management:
        rows.append({
            "chain": row.chain,
            "stage": row.stage,
            "n_total_in_kg": row.n_total_in_kg,
            "tan_in_kg": row.tan_in_kg,
            "nh3_n_kg": row.nh3_n_kg,
            "nox_n_kg": row.no_n_kg,
            "n2_n_kg": row.n2_n_kg,
            "n2o_n_direct_kg": row.n2o_n_direct_ipcc_kg,
            "n2o_n_indirect_vol_kg": row.n2o_n_indirect_vol_kg,
            "n_water_loss_kg": row.water_n_loss_ipcc_kg,
            "n_leach_runoff_kg": row.soil_leach_runoff_n_kg,
            "n2o_n_indirect_leach_kg": row.n2o_n_indirect_leach_kg,
            "no3_kg": row.no3_from_soil_leach_kg,
            "n_total_out_kg": row.n_total_out_kg,
            "n_returned_emep_kg": "",
            "soil_n_remaining_after_direct_losses_kg": "",
            "tan_out_kg": row.tan_out_kg,
            "mass_balance_residual_kg": row.mass_balance_residual_kg,
        })
    for row in applications:
        rows.append({
            "chain": row.chain,
            "stage": row.stage,
            "n_total_in_kg": row.n_applic_kg,
            "tan_in_kg": row.tan_applic_kg,
            "nh3_n_kg": row.nh3_n_app_kg,
            "nox_n_kg": row.nox_n_app_kg,
            "n2_n_kg": 0.0,
            "n2o_n_direct_kg": row.n2o_n_direct_soil_kg,
            "n2o_n_indirect_vol_kg": row.n2o_n_indirect_vol_kg,
            "n_water_loss_kg": 0.0,
            "n_leach_runoff_kg": row.n_leach_runoff_kg,
            "n2o_n_indirect_leach_kg": row.n2o_n_indirect_leach_kg,
            "no3_kg": row.no3_leach_runoff_kg,
            "n_total_out_kg": "",
            "n_returned_emep_kg": row.n_returned_emep_kg,
            "soil_n_remaining_after_direct_losses_kg": row.soil_n_remaining_after_direct_losses_kg,
            "tan_out_kg": row.tan_after_application_kg,
            "mass_balance_residual_kg": row.mass_balance_residual_kg,
        })
    order = {"A1": 0, "A2": 1, "A3": 2, "A4": 3, "B1": 4, "B2": 5}
    return sorted(rows, key=lambda item: order[str(item["stage"])[:2]])


def _annual_ch4(
    escenario: str,
    etapa: int,
    *,
    b0_m3_ch4_per_kg_vs: float | None = None,
    mcf_pct: float | None = None,
) -> float:
    """Conserva el cálculo IPCC vigente de CH4 y lo anualiza con la masa activa."""
    from acv_factores_manejo_estiercol import obtener_factores_manejo_ipcc
    from acv_masa_seca import convertir_vs_base_humeda, obtener_fraccion_masa_seca_etapa
    from acv_parametros_etapa import obtener_parametros_etapa
    from ecuaciones_acv import ef_ch4

    params = obtener_parametros_etapa(escenario, etapa)
    factors = obtener_factores_manejo_ipcc(escenario, etapa)
    dry_fraction = obtener_fraccion_masa_seca_etapa(escenario, etapa)
    vs_wet = convertir_vs_base_humeda(params["vs_t_pct"], dry_fraction)
    ledger_parameters, _, masses = load_inputs()
    mass = float(masses[(escenario, etapa)]["masa_total_kg_eq"])
    b0 = (
        ledger_parameters["dairy_b0_m3_ch4_per_kg_vs"]
        if b0_m3_ch4_per_kg_vs is None
        else float(b0_m3_ch4_per_kg_vs)
    )
    mcf = float(factors["MCF"]) if mcf_pct is None else float(mcf_pct)
    if not math.isfinite(b0) or b0 < 0.0:
        raise ValueError(f"B0 inválido para sensibilidad: {b0}")
    if not math.isfinite(mcf) or not 0.0 <= mcf <= 100.0:
        raise ValueError(f"MCF inválido para sensibilidad: {mcf}")
    return ef_ch4(
        VS_T=vs_wet,
        B0_T=b0,
        MCF=mcf,
        AWMS=ledger_parameters["awms_assigned_stream_fraction"],
        ch4_density_kg_per_m3=ledger_parameters["ch4_density_kg_per_m3"],
    ) * mass


def productive_emission_rows(
    *,
    b0_m3_ch4_per_kg_vs: float | None = None,
    mcf_overrides_pct: dict[tuple[str, int], float] | None = None,
) -> dict[tuple[str, int], dict[str, float | int]]:
    """Construye emisiones anuales, con parametrización opcional sin efectos laterales.

    Los valores opcionales existen exclusivamente para evaluaciones controladas. No
    modifican tablas, parámetros ni salidas canónicas. B0 se aplica coherentemente a
    todas las etapas que producen CH4; los MCF solo sustituyen las claves indicadas.
    """
    mcf_overrides_pct = dict(mcf_overrides_pct or {})
    allowed_mcf_keys = {("A", 1), ("A", 2), ("A", 3), ("B", 1)}
    unexpected = set(mcf_overrides_pct) - allowed_mcf_keys
    if unexpected:
        raise ValueError(f"Overrides de MCF fuera de etapas con CH4: {sorted(unexpected)}")
    management, applications, _ = build_ledger()
    by_management = {row.stage[:2]: row for row in management}
    by_application = {row.stage[:2]: row for row in applications}
    result: dict[tuple[str, int], dict[str, float | int]] = {}
    keys = {"A1": ("A", 1), "A2": ("A", 2), "A3": ("A", 3), "A4": ("A", 4), "B1": ("B", 1), "B2": ("B", 2)}
    for code, key in keys.items():
        row: dict[str, float | int] = {
            "Escenario": key[0], "Etapa": key[1], "CO2_medido": math.nan,
            "CH4_ec1": math.nan, "N2O_ec14": math.nan, "N2O_ec2": math.nan,
            "N2O_ec5": math.nan, "N2O_ec6": math.nan, "N2O_ec16": math.nan,
            "N2O_ec18": math.nan, "NH3_ec12": math.nan, "NH3_ec20": math.nan,
            "NOx_as_NO2": math.nan, "NO3_ec13": math.nan, "NO3_ec21": math.nan,
        }
        if code in by_management:
            stage = by_management[code]
            row.update({
                "CH4_ec1": _annual_ch4(
                    *key,
                    b0_m3_ch4_per_kg_vs=b0_m3_ch4_per_kg_vs,
                    mcf_pct=mcf_overrides_pct.get(key),
                ),
                "N2O_ec2": stage.n2o_n_direct_ipcc_kg * KG_N_TO_N2O,
                "N2O_ec5": stage.n2o_indirect_vol_kg,
                "N2O_ec6": stage.n2o_indirect_leach_kg,
                "NH3_ec12": stage.nh3_n_kg * KG_N_TO_NH3,
                "NOx_as_NO2": stage.no_n_kg * 46.0 / 14.0,
                "NO3_ec13": stage.no3_from_soil_leach_kg,
            })
        else:
            stage = by_application[code]
            row.update({
                "N2O_ec14": stage.n2o_direct_soil_kg,
                "N2O_ec16": stage.n2o_indirect_vol_kg,
                "N2O_ec18": stage.n2o_indirect_leach_kg,
                "NH3_ec20": stage.nh3_app_kg,
                "NOx_as_NO2": stage.no2_reported_kg,
                "NO3_ec21": stage.no3_leach_runoff_kg,
            })
        result[key] = row
    return result


def emission_row(escenario: str, etapa: int) -> dict[str, float | int]:
    key = (escenario.upper(), int(etapa))
    try:
        return productive_emission_rows()[key]
    except KeyError as exc:
        raise KeyError(f"Etapa fuera del ledger productivo: {key}") from exc


def validate(management: list[ManagementRow], applications: list[ApplicationRow]) -> None:
    p, _, _ = load_inputs()
    for row in management:
        assert all(value >= -TOLERANCE for value in (row.nh3_n_kg, row.no_n_kg, row.n2_n_kg, row.n2o_n_direct_ipcc_kg, row.water_n_loss_ipcc_kg))
        assert 0.0 <= row.tan_out_kg <= row.n_total_out_kg + TOLERANCE
        assert row.non_tan_n_out_kg >= -TOLERANCE
        assert abs(row.mass_balance_residual_kg) <= TOLERANCE
        assert abs(row.n2o_n_indirect_vol_kg - (row.nh3_n_kg + row.no_n_kg) * p["ef4_ipcc"]) <= TOLERANCE
    for row in applications:
        assert 0.0 <= row.tan_after_application_kg <= row.n_returned_emep_kg + TOLERANCE
        assert row.n_returned_emep_kg <= row.n_applic_kg + TOLERANCE
        assert row.soil_n_remaining_after_direct_losses_kg <= row.n_returned_emep_kg + TOLERANCE
        assert abs(row.mass_balance_residual_kg) <= TOLERANCE
        assert abs(row.n2o_n_indirect_vol_kg - (row.nh3_n_app_kg + row.nox_n_app_kg) * p["ef4_ipcc"]) <= TOLERANCE
    by_m = {row.stage[:2]: row for row in management}
    by_a = {row.stage[:2]: row for row in applications}
    assert by_a["A4"].n_applic_kg == by_m["A3"].n_total_out_kg
    assert by_a["A4"].tan_applic_kg == by_m["A3"].tan_out_kg
    assert by_a["B2"].n_applic_kg == by_m["B1"].n_total_out_kg
    assert by_a["B2"].tan_applic_kg == by_m["B1"].tan_out_kg
    assert by_m["A3"].n_total_in_kg != by_m["A1"].n_total_out_kg
    assert by_m["B1"].n_total_in_kg > by_m["A3"].n_total_in_kg


def _write(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No hay filas para {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    management, applications, _ = build_ledger()
    validate(management, applications)
    _write(PRODUCTIVE_LEDGER, productive_ledger_rows(management, applications))
    residuals = [abs(row.mass_balance_residual_kg) for row in management + applications]
    print(f"Ledger productivo PASS: 6 etapas; residuo máximo={max(residuals):.3e} kg N")


if __name__ == "__main__":
    main()
