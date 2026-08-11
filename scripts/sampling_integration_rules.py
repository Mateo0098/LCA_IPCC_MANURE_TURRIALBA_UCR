"""Reglas versionadas para la integración temporal de los muestreos del TFG.

Este módulo solo declara política metodológica. El cálculo consume estas reglas
y los promedios de jornada ya producidos por la ingestión validada.
"""

from __future__ import annotations


SOLID_MATERIALS = ("estiércol fresco", "estiércol precompostado")
SOLID_VARIABLES = ("N total", "humedad", "materia seca", "cenizas", "sólidos volátiles")
LIQUID_MATERIALS = ("aguas verdes", "purines")
FUTURE_JOURNEY = "M3"


def _journey(jornada: str, elegible: bool, motivo: str, metodo_requerido: str) -> dict:
    return {
        "jornada": jornada,
        "elegibilidad_temporal": elegible,
        "motivo": motivo,
        "metodo_requerido": metodo_requerido,
    }


INTEGRATION_RULES: list[dict] = []

for material in SOLID_MATERIALS:
    for variable in SOLID_VARIABLES:
        metodo = "Kjeldahl" if material == "estiércol fresco" and variable == "N total" else (
            "Dumas (combustión seca)" if variable == "N total" else "gravimetría"
        )
        observacion = ""
        if material == "estiércol precompostado" and variable == "N total":
            observacion = (
                "N determinado por el CIA mediante Dumas en muestra secada a 80 °C durante 48 h; "
                "la base formal final del porcentaje no está especificada. No se aplica conversión "
                "con la materia seca gravimétrica del TFG."
            )
        INTEGRATION_RULES.append(
            {
                "material": material,
                "variable": variable,
                "jornadas": [
                    _journey("M1", True, "Procedimiento metodológicamente comparable.", metodo),
                    _journey("M2", True, "Procedimiento metodológicamente comparable.", metodo),
                    _journey("M3", True, "Elegible si conserva el mismo procedimiento.", metodo),
                ],
                "politica_integracion": "media aritmética de promedios de jornada con igual peso temporal",
                "minimo_jornadas_necesarias": 2,
                "numero_jornadas_final_esperado": 3,
                "uso_previsto": "estimador experimental provisional vigente y elegible para promoción al ACV",
                "observacion_metodologica": observacion,
                "tipo_regla": "solido_integrable",
            }
        )

for material in LIQUID_MATERIALS:
    INTEGRATION_RULES.append(
        {
            "material": material,
            "variable": "N total",
            "jornadas": [
                _journey(
                    "M1",
                    False,
                    "La especiación de M1 se conserva solo para trazabilidad y no equivale a N total Kjeldahl.",
                    "Kjeldahl",
                ),
                _journey("M2", True, "N total determinado mediante Kjeldahl.", "Kjeldahl"),
                _journey("M3", True, "Requerida y elegible si se determina mediante Kjeldahl.", "Kjeldahl"),
            ],
            "politica_integracion": "media aritmética de los promedios M2 y M3 con igual peso temporal; M1 excluida",
            "minimo_jornadas_necesarias": 2,
            "numero_jornadas_final_esperado": 2,
            "uso_previsto": "estimador experimental provisional vigente para el modelo ACV; pendiente de integración final con M3",
            "observacion_metodologica": "M2 es el único estimador Kjeldahl elegible disponible y constituye el valor provisional vigente; M3 permanece pendiente para la integración final.",
            "tipo_regla": "liquido_n_provisional",
        }
    )

for material in LIQUID_MATERIALS:
    INTEGRATION_RULES.append(
        {
            "material": material,
            "variable": "densidad",
            "jornadas": [
                _journey("M1", True, "Caracterización descriptiva.", "densidad reportada"),
                _journey("M2", True, "Caracterización descriptiva.", "densidad reportada"),
                _journey("M3", True, "Caracterización descriptiva futura.", "densidad reportada"),
            ],
            "politica_integracion": "resumen descriptivo con igual peso por jornada; no usar como parámetro del modelo",
            "minimo_jornadas_necesarias": 1,
            "numero_jornadas_final_esperado": 3,
            "uso_previsto": "solo caracterización; no es parámetro representativo del modelo ACV",
            "observacion_metodologica": "La densidad solo podrá adquirir otro uso si un consumidor explícito lo requiere posteriormente.",
            "tipo_regla": "solo_caracterizacion",
        }
    )

for variable in ("carbono", "relación C/N"):
    INTEGRATION_RULES.append(
        {
            "material": "estiércol precompostado",
            "variable": variable,
            "jornadas": [
                _journey("M1", True, "Caracterización descriptiva cuando esté disponible.", "Dumas (combustión seca)"),
                _journey("M2", True, "Caracterización descriptiva cuando esté disponible.", "Dumas (combustión seca)"),
                _journey("M3", True, "Caracterización descriptiva futura.", "Dumas (combustión seca)"),
            ],
            "politica_integracion": "resumen descriptivo de promedios disponibles con igual peso por jornada",
            "minimo_jornadas_necesarias": 1,
            "numero_jornadas_final_esperado": 3,
            "uso_previsto": "solo caracterización; no es parámetro actual del modelo ACV",
            "observacion_metodologica": (
                "Muestra secada a 80 °C durante 48 h; la base formal final del porcentaje no está especificada. "
                "No se aplica conversión con la materia seca gravimétrica del TFG."
            ),
            "tipo_regla": "solo_caracterizacion",
        }
    )


RULES_BY_KEY = {(rule["material"], rule["variable"]): rule for rule in INTEGRATION_RULES}


MASS_TRANSFORMATION_RULE = {
    "nombre": "transformación de masa de estiércol fresco a precompostado",
    "variables_requeridas": (
        ("estiércol fresco", "materia seca"),
        ("estiércol precompostado", "materia seca"),
        ("estiércol fresco", "cenizas"),
        ("estiércol precompostado", "cenizas"),
    ),
    "metodo_requerido": "gravimetría",
    "jornadas_esperadas": ("M1", "M2", "M3"),
    "numero_jornadas_final_esperado": 3,
    "politica_integracion": (
        "calcular mass_ratio_precomp_over_fresh por jornada e integrar los factores "
        "de jornada con igual peso temporal"
    ),
    "parametro_integrado_principal": "mass_ratio_precomp_over_fresh",
    "perdida_integrada": "(1 - mass_ratio_integrado) × 100",
    "uso_previsto": "factor experimental integrado vigente consumido por el cálculo de masas",
}
