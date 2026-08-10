"""Configuración explícita de fuentes para la ingestión multijornada.

Las decisiones metodológicas sensibles se declaran aquí y nunca se infieren
solamente a partir del nombre de un archivo.
"""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

CIA_LIQUID_N_METHOD_SOURCE = (
    "Metodología oficial del Laboratorio de Suelos y Foliares de la Ciudad de "
    "la Investigación (CIA), suministrada por el investigador: para abonos "
    "líquidos se digieren 10 g con H2SO4 mediante Kjeldahl, se llevan a 250 mL "
    "y se determina N por colorimetría con FIA."
)

CIA_SOLID_CN_METHOD_SOURCE = (
    "Metodología oficial del Laboratorio de Suelos y Foliares de la Ciudad de "
    "la Investigación (CIA), suministrada por el investigador: la muestra de "
    "abono sólido se seca a 80 °C, se muele, se criba a 1 mm, se pesan "
    "aproximadamente 80–100 mg y se determina N y C por combustión seca de "
    "Dumas en un autoanalizador Elementar Vario Macro Cube. La metodología y "
    "los reportes no especifican inequívocamente la base final del porcentaje."
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
        "laboratorio": "no documentado",
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
        "uso_modelo": "elegible",
        "motivo_uso": "N total de abono líquido por el método oficial CIA confirmado por el investigador.",
        "expected_samples": 3,
    },
    {
        "jornada": "M2",
        "kind": "gravimetric_xlsx",
        "path": "Academic_documents/resultados CIA y LASA muestreo 2/muestreo2_solidos_volatiles.xlsx",
        "laboratorio": "no documentado",
        "metodo": "gravimetría",
        "fuente_metodo": "Procedimiento y masas primarias registrados en las hojas Procedure y Data.",
        "uso_modelo": "elegible",
        "motivo_uso": "Caracterización gravimétrica primaria de sólidos.",
        "expected_samples_by_material": 3,
        "expected_replicates": 3,
    },
]


def configured_sources(kind: str | None = None) -> list[dict]:
    rows = SOURCES if kind is None else [row for row in SOURCES if row["kind"] == kind]
    return [{**row, "absolute_path": PROJECT_ROOT / row["path"]} for row in rows]
