"""Utilidades para convertir parametros en base seca a base humeda por etapa."""

from __future__ import annotations

from acv_parametros_etapa import obtener_parametros_etapa


def obtener_fraccion_masa_seca_etapa(escenario: str, etapa: int) -> float:
    """Devuelve la fracción de materia seca integrada (0-1) de la etapa."""
    params = obtener_parametros_etapa(escenario, etapa)
    dry_matter_pct = params.get("materia_seca_pct")
    if dry_matter_pct is None:
        raise ValueError(
            f"materia_seca_pct vacía para escenario={escenario}, etapa={etapa} "
            "en processed/acv_parametros_escenario_etapa.csv"
        )
    if dry_matter_pct <= 0:
        raise ValueError(
            f"materia_seca_pct debe ser > 0 para escenario={escenario}, etapa={etapa}"
        )
    return dry_matter_pct / 100.0


def convertir_vs_base_humeda(vs_pct_base_seca: float, fraccion_masa_seca: float) -> float:
    """Convierte %SV en base seca a fraccion SV en base humeda."""
    return (float(vs_pct_base_seca) / 100.0) * float(fraccion_masa_seca)


def convertir_n_material_preparado_a_base_humeda(
    n_pct_material_preparado: float,
    fraccion_masa_seca_gravimetrica: float,
) -> float:
    """Convierte %N del material preparado/seco a kg N/kg de material húmedo.

    La función no modifica el porcentaje analítico original ni intenta corregir
    pérdidas de N durante la preparación de la muestra. La fracción de materia
    seca procede de la determinación gravimétrica independiente del TFG.
    """
    n_pct = float(n_pct_material_preparado)
    dry_fraction = float(fraccion_masa_seca_gravimetrica)
    if not 0.0 <= n_pct <= 100.0:
        raise ValueError("El porcentaje analítico de N debe estar entre 0 y 100")
    if not 0.0 < dry_fraction <= 1.0:
        raise ValueError("La fracción gravimétrica de materia seca debe estar entre 0 y 1")
    return (n_pct / 100.0) * dry_fraction
