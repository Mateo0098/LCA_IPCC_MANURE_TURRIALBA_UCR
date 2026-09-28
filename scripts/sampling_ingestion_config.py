"""Configuración explícita de fuentes para la ingestión multijornada.

Las decisiones metodológicas sensibles se declaran aquí y nunca se infieren
solamente a partir del nombre de un archivo.
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCE_STATE_NOT_AVAILABLE = "no_disponible"
SOURCE_STATE_DECLARED_INCOMPLETE = "declarada_incompleta"
SOURCE_STATE_COMPLETE = "completa"

# Contrato de fuentes de una jornada con el diseño físico de M2. No contiene
# rutas ni resultados ficticios: sirve para distinguir una jornada todavía no
# disponible de una declaración parcial y de un conjunto real completo.
M3_SOURCE_CONTRACT = (
    {
        "kind": "lasa_pdf",
        "material": "estiércol fresco",
        "laboratorio": "LASA",
        "metodo": "Kjeldahl",
        "expected_samples": 3,
        "expected_replicates": 3,
    },
    {
        "kind": "cia_xlsx",
        "material": "estiércol precompostado",
        "laboratorio": "CIA",
        "metodo": "Dumas (combustión seca)",
        "expected_samples": 3,
    },
    {
        "kind": "cia_xlsx",
        "material": "aguas verdes",
        "laboratorio": "CIA",
        "metodo": "Kjeldahl",
        "expected_samples": 3,
    },
    {
        "kind": "cia_xlsx",
        "material": "purines",
        "laboratorio": "CIA",
        "metodo": "Kjeldahl",
        "expected_samples": 3,
    },
    {
        "kind": "gravimetric_xlsx",
        "material": "",
        "laboratorio": "Bioenergía",
        "metodo": "gravimetría",
        "expected_samples_by_material": 3,
        "expected_replicates": 3,
    },
)

_COMMON_SOURCE_SLOTS = tuple(
    (item["kind"], item["material"]) for item in M3_SOURCE_CONTRACT
)
EXPECTED_SOURCE_SLOTS_BY_JOURNEY = {
    "M1": _COMMON_SOURCE_SLOTS,
    "M2": _COMMON_SOURCE_SLOTS,
    "M3": _COMMON_SOURCE_SLOTS,
}

CIA_LIQUID_N_METHOD_SOURCE = (
    "Metodología oficial del Laboratorio de Suelos y Foliares de la Ciudad de "
    "la Investigación (CIA), suministrada por el investigador: para abonos "
    "líquidos se digieren 10 g con H2SO4 mediante Kjeldahl, se llevan a 250 mL "
    "y se determina N por colorimetría con FIA."
)

CIA_LIQUID_REPORTING_CLARIFICATION = (
    "Aclaración oficial del CIA suministrada por el investigador: el laboratorio "
    "reporta el resultado hasta el segundo decimal, como se observa en el informe; "
    "los decimales adicionales de la celda corresponden a la lectura almacenada por "
    "el equipo. Se conservan internamente sin atribuirles mayor precisión analítica "
    "formal y el redondeo se reserva para la presentación final."
)

CIA_SOLID_CN_METHOD_SOURCE = (
    "Metodología oficial del Laboratorio de Suelos y Foliares de la Ciudad de "
    "la Investigación (CIA), suministrada por el investigador: la muestra de "
    "abono sólido se seca a 80 °C durante 48 h, se muele, se criba a 1 mm, se pesan "
    "aproximadamente 80–100 mg y se determina N y C por combustión seca de "
    "Dumas en un autoanalizador Elementar Vario Macro Cube. El CIA aclaró que no "
    "determinó humedad a 105 °C porque no fue solicitada. Los porcentajes se "
    "refieren a la muestra seca/acondicionada por el CIA a 80 °C durante 48 h; "
    "la humedad y la materia seca usadas por el TFG proceden de la gravimetría "
    "independiente de Bioenergía a 105 °C durante 16 h."
)


SOURCES = [
    {
        "jornada": "M1",
        "kind": "lasa_pdf",
        "path": "Academic_documents/resultados CIA y LASA muestreo 1/129-25 Contenido de nitrogeno - firmado.pdf",
        "material": "estiércol fresco",
        "laboratorio": "LASA",
        "metodo": "Kjeldahl",
        "fuente_metodo": "Procedimiento descrito en las páginas 1 y 2 del informe LASA 129-25.",
        "uso_modelo": "elegible",
        "motivo_uso": "N total determinado por Kjeldahl en estiércol fresco.",
        "expected_samples": 2,
        "expected_replicates": 3,
    },
    {
        "jornada": "M1",
        "kind": "cia_xlsx",
        "path": "Academic_documents/resultados CIA y LASA muestreo 1/AO-00476-00477 (97600) ESCUELA INGENIERIA y de BIOSISTEMAS.xlsx",
        "material": "estiércol precompostado",
        "laboratorio": "CIA",
        "metodo": "Dumas (combustión seca)",
        "fuente_metodo": CIA_SOLID_CN_METHOD_SOURCE,
        "condicion_muestra": "Muestra secada a 80 °C durante 48 h; el CIA no determinó humedad a 105 °C porque no fue solicitada.",
        "uso_modelo": "elegible",
        "motivo_uso": "Caracterización de N y C de estiércol precompostado.",
        "expected_samples": 2,
    },
    {
        "jornada": "M1",
        "kind": "cia_xlsx",
        "path": "Academic_documents/resultados CIA y LASA muestreo 1/AO-00478-00479 (97601) ESCUELA INGENIERIA y de BIOSISTEMAS.xlsx",
        "material": "aguas verdes",
        "laboratorio": "CIA",
        "metodo": "especiación",
        "fuente_metodo": "El informe CIA 97601 reporta por separado N-NH4+, N-NO3- y N ureico.",
        "uso_modelo": "solo_trazabilidad",
        "motivo_uso": "La especiación de M1 no es directamente comparable con el N total Kjeldahl de M2/M3.",
        "expected_samples": 2,
    },
    {
        "jornada": "M1",
        "kind": "cia_xlsx",
        "path": "Academic_documents/resultados CIA y LASA muestreo 1/AO-00504-00505 (97679) MATEO CERDAS BARBOZA.xlsx",
        "material": "purines",
        "laboratorio": "CIA",
        "metodo": "especiación",
        "fuente_metodo": "El informe CIA 97679 reporta por separado N-NH4+, N-NO3- y N ureico.",
        "uso_modelo": "solo_trazabilidad",
        "motivo_uso": "La especiación de M1 no es directamente comparable con el N total Kjeldahl de M2/M3.",
        "expected_samples": 2,
    },
    {
        "jornada": "M1",
        "kind": "gravimetric_xlsx",
        "path": "Academic_documents/resultados CIA y LASA muestreo 1/Material_laboratorio_copy_to_work_python.xlsx",
        "laboratorio": "Bioenergía",
        "metodo": "gravimetría",
        "fuente_metodo": "Procedimiento y masas primarias registrados en las hojas Procedure y Data.",
        "uso_modelo": "elegible",
        "motivo_uso": "Caracterización gravimétrica primaria de sólidos.",
        "expected_samples_by_material": 2,
        "expected_replicates": 3,
        "sampling_date": "2025-11-10",
    },
    {
        "jornada": "M2",
        "kind": "lasa_pdf",
        "path": "Academic_documents/resultados CIA y LASA muestreo 2/043-26 Contenido de Nitrogeno-firmado.pdf",
        "material": "estiércol fresco",
        "laboratorio": "LASA",
        "metodo": "Kjeldahl",
        "fuente_metodo": "Procedimiento descrito en las páginas 1 y 2 del informe LASA 043-26.",
        "uso_modelo": "elegible",
        "motivo_uso": "N total determinado por Kjeldahl en estiércol fresco.",
        "expected_samples": 3,
        "expected_replicates": 3,
    },
    {
        "jornada": "M2",
        "kind": "cia_xlsx",
        "path": "Academic_documents/resultados CIA y LASA muestreo 2/AO-00330-00332 (100750) SEDE DEL ATLANTICO.xlsx",
        "material": "aguas verdes",
        "laboratorio": "CIA",
        "metodo": "Kjeldahl",
        "fuente_metodo": CIA_LIQUID_N_METHOD_SOURCE,
        "nota_precision": CIA_LIQUID_REPORTING_CLARIFICATION,
        "uso_modelo": "elegible",
        "motivo_uso": "N total de abono líquido por el método oficial CIA confirmado por el investigador.",
        "expected_samples": 3,
    },
    {
        "jornada": "M2",
        "kind": "cia_xlsx",
        "path": "Academic_documents/resultados CIA y LASA muestreo 2/AO-00333-00335 (100751) SEDE DEL ATLANTICO.xlsx",
        "material": "estiércol precompostado",
        "laboratorio": "CIA",
        "metodo": "Dumas (combustión seca)",
        "fuente_metodo": CIA_SOLID_CN_METHOD_SOURCE,
        "condicion_muestra": "Muestra secada a 80 °C durante 48 h; el CIA no determinó humedad a 105 °C porque no fue solicitada.",
        "uso_modelo": "elegible",
        "motivo_uso": "Caracterización de N y C de estiércol precompostado.",
        "expected_samples": 3,
    },
    {
        "jornada": "M2",
        "kind": "cia_xlsx",
        "path": "Academic_documents/resultados CIA y LASA muestreo 2/AO-00337-00339 (100788) SEDE DEL ATLANTICO.xlsx",
        "material": "purines",
        "laboratorio": "CIA",
        "metodo": "Kjeldahl",
        "fuente_metodo": CIA_LIQUID_N_METHOD_SOURCE,
        "nota_precision": CIA_LIQUID_REPORTING_CLARIFICATION,
        "uso_modelo": "elegible",
        "motivo_uso": "N total de abono líquido por el método oficial CIA confirmado por el investigador.",
        "expected_samples": 3,
    },
    {
        "jornada": "M2",
        "kind": "gravimetric_xlsx",
        "path": "Academic_documents/resultados CIA y LASA muestreo 2/muestreo2_solidos_volatiles.xlsx",
        "laboratorio": "Bioenergía",
        "metodo": "gravimetría",
        "fuente_metodo": "Procedimiento y masas primarias registrados en las hojas Procedure y Data.",
        "uso_modelo": "elegible",
        "motivo_uso": "Caracterización gravimétrica primaria de sólidos.",
        "expected_samples_by_material": 3,
        "expected_replicates": 3,
    },
]


def _source_slot(source: dict) -> tuple[str, str]:
    return str(source.get("kind", "")), str(source.get("material", ""))


def journey_source_status(
    jornada: str,
    sources: Iterable[dict] | None = None,
    project_root: Path = PROJECT_ROOT,
) -> dict:
    """Clasifica la declaración de fuentes sin crear observaciones.

    ``no_disponible`` significa que no se ha declarado ninguna fuente de la
    jornada. ``declarada_incompleta`` bloquea la ingestión para impedir que una
    parte de M3 entre en estadísticas. ``completa`` exige los cinco tipos de
    fuente, metadatos compatibles y archivos reales existentes, y significa que
    la declaración está lista para intentar la ingestión. La estructura y la
    cardinalidad observadas se acreditan después mediante extracción y
    validación, no por la mera existencia de las rutas.
    """
    selected = [
        dict(source)
        for source in (SOURCES if sources is None else sources)
        if str(source.get("jornada", "")) == jornada
    ]
    expected_slots = EXPECTED_SOURCE_SLOTS_BY_JOURNEY.get(jornada)
    if expected_slots is None:
        return {
            "jornada": jornada,
            "estado": SOURCE_STATE_DECLARED_INCOMPLETE,
            "errores": [f"Jornada no configurada: {jornada}"],
            "fuentes_declaradas": len(selected),
        }
    if not selected:
        return {
            "jornada": jornada,
            "estado": SOURCE_STATE_NOT_AVAILABLE,
            "errores": [],
            "fuentes_declaradas": 0,
        }

    errors: list[str] = []
    expected = Counter(expected_slots)
    observed = Counter(_source_slot(source) for source in selected)
    missing = list((expected - observed).elements())
    extra = list((observed - expected).elements())
    if missing:
        errors.append(f"Faltan fuentes: {missing}")
    if extra:
        errors.append(f"Sobran o se duplican fuentes: {extra}")

    for source in selected:
        slot = _source_slot(source)
        raw_path = str(source.get("path", "")).strip()
        if not raw_path:
            errors.append(f"Fuente sin ruta real: {slot}")
        else:
            source_path = Path(raw_path)
            if source_path.is_absolute():
                errors.append(f"La ruta debe ser relativa al repositorio: {raw_path}")
            elif not (project_root / source_path).is_file():
                errors.append(f"Archivo declarado inexistente: {raw_path}")

    if jornada == "M3":
        declared_paths = Counter(
            str(source.get("path", "")).strip()
            for source in selected
            if str(source.get("path", "")).strip()
        )
        duplicated_paths = [
            path for path, count in declared_paths.items() if count > 1
        ]
        if duplicated_paths:
            errors.append(
                "M3 no puede simular fuentes lógicas duplicando rutas: "
                f"{duplicated_paths}"
            )
        contract_by_slot = {
            (item["kind"], item["material"]): item for item in M3_SOURCE_CONTRACT
        }
        for source in selected:
            slot = _source_slot(source)
            contract = contract_by_slot.get(slot)
            if contract is None:
                continue
            for field, expected_value in contract.items():
                if field in {"kind", "material"}:
                    continue
                if source.get(field) != expected_value:
                    errors.append(
                        f"M3 {slot}: {field}={source.get(field)!r}; "
                        f"se requiere {expected_value!r}"
                    )
            for field in ("fuente_metodo", "uso_modelo", "motivo_uso"):
                if not str(source.get(field, "")).strip():
                    errors.append(f"M3 {slot}: falta {field}")
            if source.get("uso_modelo") != "elegible":
                errors.append(f"M3 {slot}: uso_modelo debe ser 'elegible'")
            if slot == ("cia_xlsx", "estiércol precompostado") and not str(
                source.get("condicion_muestra", "")
            ).strip():
                errors.append("M3 precompostado requiere condicion_muestra")
            if slot[0] == "cia_xlsx" and slot[1] in {"aguas verdes", "purines"}:
                if not str(source.get("nota_precision", "")).strip():
                    errors.append(f"M3 {slot}: falta nota_precision")
            if slot == ("gravimetric_xlsx", "") and not str(
                source.get("sampling_date", "")
            ).strip():
                errors.append("M3 gravimétrica requiere sampling_date real")

    return {
        "jornada": jornada,
        "estado": SOURCE_STATE_COMPLETE if not errors else SOURCE_STATE_DECLARED_INCOMPLETE,
        "errores": errors,
        "fuentes_declaradas": len(selected),
    }


def assert_configured_journeys_ready() -> None:
    """Impide ingerir jornadas activas incompletas o una M3 parcial."""
    errors: list[str] = []
    for jornada in ("M1", "M2", "M3"):
        status = journey_source_status(jornada)
        if jornada in {"M1", "M2"} and status["estado"] != SOURCE_STATE_COMPLETE:
            errors.extend(status["errores"] or [f"{jornada} no está completa"])
        elif status["estado"] == SOURCE_STATE_DECLARED_INCOMPLETE:
            errors.extend(
                status["errores"]
                or [f"{jornada} está declarada de forma incompleta"]
            )
    if errors:
        raise ValueError("Configuración de fuentes no apta para ingestión:\n- " + "\n- ".join(errors))


def configured_sources(kind: str | None = None) -> list[dict]:
    rows = SOURCES if kind is None else [row for row in SOURCES if row["kind"] == kind]
    return [{**row, "absolute_path": PROJECT_ROOT / row["path"]} for row in rows]
