"""Taxonomía y matriz académica de procedencia de los datos del ICV.

La procedencia académica y el tratamiento aplicado dentro del TFG son dimensiones
independientes. Este módulo no recalcula el inventario: verifica fuentes vigentes y
genera una vista por familias para los documentos académicos.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ACTIVE_SOURCES = {
    "integration": ROOT / "processed" / "muestreos_integracion_interjornada_provisional.csv",
    "mass_transformation": ROOT / "processed" / "muestreos_transformacion_masa_interjornada.csv",
    "active_parameters": ROOT / "processed" / "acv_parametros_escenario_etapa.csv",
    "active_masses": ROOT / "processed" / "masa_total_escenario_etapa.csv",
    "operational": ROOT / "processed" / "acv_parametros_operativos.csv",
    "published_operations": ROOT / "Academic_documents" / "references" / "parametros_operativos_sanchez_2026.csv",
    "ledger_parameters": ROOT / "processed" / "reactive_n_ledger_parameters.csv",
    "characterization_factors": ROOT / "processed" / "acv_factores_equivalencia.csv",
    "imn_factors": ROOT / "processed" / "acv_factores_imn_recursos_operativos.csv",
    "primary_evidence": ROOT / "Academic_documents" / "registro_evidencia_experimental_primaria.md",
}

ACADEMIC_PROVENANCE = {
    "Primaria",
    "Secundaria",
    "Terciaria",
    "Mixta: primaria y secundaria",
    "No aplica: supuesto del estudio",
    "No aplica: convención del estudio",
}

EXPECTED_FAMILY_IDS = {
    "experimental_characterization",
    "field_operations",
    "equipment_plate",
    "published_farm_operations",
    "literature_assumption",
    "field_based_assumptions",
    "temporal_conventions",
    "mass_transformation",
    "ipcc_factors",
    "emep_factors",
    "literature_factor",
    "imn_factors",
    "ef31_factors",
    "calculated_inventory_flows",
    "propagated_nitrogen",
}

MACROFAMILY_DEFINITIONS = (
    {
        "macrofamilia": "Caracterización experimental",
        "family_ids": ("experimental_characterization",),
        "procedencia_general": "Primaria: mediciones de muestras del TFG",
        "tratamiento_general": "Medido e integrado estadísticamente",
        "funcion_icv": "Caracterizar los materiales y promover parámetros experimentales",
    },
    {
        "macrofamilia": "Observaciones y registros operativos de la finca",
        "family_ids": ("field_operations", "equipment_plate"),
        "procedencia_general": "Primaria: observación, comunicación y registro de campo",
        "tratamiento_general": "Observado, comunicado o anualizado",
        "funcion_icv": "Representar tiempos, frecuencias y características nominales de equipos",
    },
    {
        "macrofamilia": "Datos previamente publicados",
        "family_ids": ("published_farm_operations",),
        "procedencia_general": "Secundaria: datos publicados del sitio",
        "tratamiento_general": "Publicado, usado directamente o anualizado",
        "funcion_icv": "Completar los parámetros operativos preexistentes de la lechería",
    },
    {
        "macrofamilia": "Factores metodológicos oficiales y literatura científica",
        "family_ids": (
            "ipcc_factors",
            "emep_factors",
            "literature_factor",
            "imn_factors",
            "ef31_factors",
        ),
        "procedencia_general": "Secundaria: guías oficiales y literatura científica",
        "tratamiento_general": "Factor metodológico, de emisión o de caracterización",
        "funcion_icv": "Estimar emisiones, consumos agregados y categorías de impacto",
    },
    {
        "macrofamilia": "Supuestos y convenciones del estudio",
        "family_ids": ("literature_assumption", "field_based_assumptions", "temporal_conventions"),
        "procedencia_general": "Secundaria cuando existe base bibliográfica; no aplica para supuestos propios y convenciones",
        "tratamiento_general": "Supuesto del estudio o convención de cálculo",
        "funcion_icv": "Explicitar elecciones numéricas y bases temporales del modelo",
    },
    {
        "macrofamilia": "Datos calculados, integrados o propagados",
        "family_ids": ("mass_transformation", "calculated_inventory_flows", "propagated_nitrogen"),
        "procedencia_general": "Heredada de entradas primarias y, cuando corresponde, secundarias",
        "tratamiento_general": "Calculado, integrado estadísticamente o propagado entre etapas",
        "funcion_icv": "Construir flujos de actividad y mantener la continuidad de masa y nitrógeno",
    },
)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _require_sources() -> None:
    missing = [path.relative_to(ROOT).as_posix() for path in ACTIVE_SOURCES.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Faltan fuentes vigentes de procedencia:\n" + "\n".join(missing))


def _scope(rows: list[dict[str, str]], column: str = "alcance") -> str:
    stages: set[str] = set()
    for row in rows:
        raw = row.get(column, "")
        for value in raw.replace(",", ";").split(";"):
            value = value.strip()
            if value in {"A1", "A2", "A3", "A4", "B1", "B2"}:
                stages.add(value)
    order = ["A1", "A2", "A3", "A4", "B1", "B2"]
    return ", ".join(item for item in order if item in stages)


def build_provenance_rows() -> list[dict[str, str]]:
    """Construye la matriz por familias desde las fuentes estructuradas vigentes."""

    _require_sources()
    integration = _read_csv(ACTIVE_SOURCES["integration"])
    transformations = _read_csv(ACTIVE_SOURCES["mass_transformation"])
    active_parameters = _read_csv(ACTIVE_SOURCES["active_parameters"])
    active_masses = _read_csv(ACTIVE_SOURCES["active_masses"])
    operational = _read_csv(ACTIVE_SOURCES["operational"])
    published = _read_csv(ACTIVE_SOURCES["published_operations"])
    ledger = _read_csv(ACTIVE_SOURCES["ledger_parameters"])
    characterization = _read_csv(ACTIVE_SOURCES["characterization_factors"])
    imn = _read_csv(ACTIVE_SOURCES["imn_factors"])

    experimental_variables = sorted({row["variable"] for row in integration})
    experimental_materials = sorted({row["material"] for row in integration})
    field_rows = [row for row in operational if row["tipo_dato"] == "Dato primario de campo"]
    plate_rows = [row for row in operational if row["tipo_dato"] == "Observado en placa"]
    field_assumptions = [
        row for row in operational
        if row["tipo_dato"] == "Supuesto del estudio" and row["parametro"] != "model_year_days"
    ]
    operational_conventions = [row for row in operational if row["parametro"] == "model_year_days"]
    published_rows = [row for row in published if row["tipo"] == "dato_publicado"]
    literature_assumptions = [row for row in published if row["tipo"] == "supuesto_tfg"]
    temporal_rows = [row for row in published if row["tipo"] == "identidad_temporal"]
    ipcc_rows = [row for row in ledger if row["source_location"].startswith("IPCC ")]
    emep_rows = [row for row in ledger if row["source_location"].startswith("EMEP/EEA ")]
    literature_rows = [row for row in ledger if row["source_location"].startswith("Komakech ")]
    integration_row = next(row for row in transformations if row["tipo_fila"] == "integracion")

    rows = [
        {
            "id_familia": "experimental_characterization",
            "variable_o_familia": "Caracterización fisicoquímica de los materiales del estudio",
            "etapas": "A1, A2, A3, A4, B1 y B2",
            "valor_o_tipo_informacion": f"{len(experimental_variables)} variables integradas en {len(experimental_materials)} tipos de material; corrida M1–M2",
            "procedencia_academica": "Primaria",
            "subtipo_procedencia": "Medición experimental del TFG y servicio analítico externo sobre sus muestras",
            "tratamiento_tfg": "Medido; resumido por muestra y jornada; integrado estadísticamente cuando es compatible",
            "fuente_concreta": "Muestreo del investigador, Bioenergía y reportes CIA/LASA de las muestras del TFG",
            "uso_metodologico": "Caracterización, parámetros experimentales y referencias de contraste del inventario",
        },
        {
            "id_familia": "field_operations",
            "variable_o_familia": "Tiempos, frecuencias y operación observada de la finca",
            "etapas": _scope(field_rows),
            "valor_o_tipo_informacion": f"{len(field_rows)} parámetros operativos de campo",
            "procedencia_academica": "Primaria",
            "subtipo_procedencia": "Observación o registro de campo específico del estudio",
            "tratamiento_tfg": "Observado o comunicado; anualizado de forma reproducible",
            "fuente_concreta": "Nota de campo y comunicación con operarios del 25 de agosto de 2026",
            "uso_metodologico": "Duración y frecuencia de bombeo, almacenamiento y aplicación",
        },
        {
            "id_familia": "equipment_plate",
            "variable_o_familia": "Características nominales observadas en equipos",
            "etapas": _scope(plate_rows),
            "valor_o_tipo_informacion": f"{len(plate_rows)} característica nominal de equipo",
            "procedencia_academica": "Primaria",
            "subtipo_procedencia": "Observación directa de placa",
            "tratamiento_tfg": "Observado",
            "fuente_concreta": "Placa de la bomba Aermotor 20HBP200-01",
            "uso_metodologico": "Estimación del consumo eléctrico del bombeo",
        },
        {
            "id_familia": "published_farm_operations",
            "variable_o_familia": "Parámetros operativos publicados de la misma lechería",
            "etapas": "A1, A2, A3, A4, B1 y B2",
            "valor_o_tipo_informacion": f"{len(published_rows)} parámetros publicados",
            "procedencia_academica": "Secundaria",
            "subtipo_procedencia": "Datos publicados previamente para el sitio de estudio",
            "tratamiento_tfg": "Publicado; usado directamente o anualizado",
            "fuente_concreta": "Sánchez-Romero y Brenes-Gamboa (2026)",
            "uso_metodologico": "Población, permanencia, estiércol recolectado y agua de lavado",
        },
        {
            "id_familia": "literature_assumption",
            "variable_o_familia": "Fracción de generación de estiércol durante la permanencia en sala",
            "etapas": "A1, A3, B1",
            "valor_o_tipo_informacion": f"{len(literature_assumptions)} supuesto basado en intervalo publicado",
            "procedencia_academica": "Secundaria",
            "subtipo_procedencia": "Literatura aplicada como base de un supuesto explícito",
            "tratamiento_tfg": "Supuesto del estudio",
            "fuente_concreta": "Límite inferior del intervalo bibliográfico citado por Sánchez-Romero y Brenes-Gamboa (2026)",
            "uso_metodologico": "Estimación conservadora del estiércol depositado durante la permanencia en sala",
        },
        {
            "id_familia": "field_based_assumptions",
            "variable_o_familia": "Eficiencia de bomba, consumo de diésel y anualización operativa",
            "etapas": _scope(field_assumptions),
            "valor_o_tipo_informacion": f"{len(field_assumptions)} supuestos explícitos con contexto de campo",
            "procedencia_academica": "No aplica: supuesto del estudio",
            "subtipo_procedencia": "Supuesto numérico definido para el modelo",
            "tratamiento_tfg": "Supuesto del estudio",
            "fuente_concreta": "Definición explícita del estudio; la nota de campo aporta contexto operativo, no el valor numérico supuesto",
            "uso_metodologico": "Cálculo de consumos de electricidad y diésel",
        },
        {
            "id_familia": "temporal_conventions",
            "variable_o_familia": "Identidades temporales para prorrateo y anualización",
            "etapas": "A1, A2, A3, A4, B1 y B2",
            "valor_o_tipo_informacion": f"{len(temporal_rows) + len(operational_conventions)} registros estructurados de convenciones temporales",
            "procedencia_academica": "No aplica: convención del estudio",
            "subtipo_procedencia": "Identidad temporal, no fuente empírica ni bibliográfica",
            "tratamiento_tfg": "Convención de cálculo",
            "fuente_concreta": "Definición temporal del modelo",
            "uso_metodologico": "Prorrateo diario y expresión anual de los flujos",
        },
        {
            "id_familia": "mass_transformation",
            "variable_o_familia": "Transformación de masa de estiércol fresco a precompostado",
            "etapas": "A1 y A2",
            "valor_o_tipo_informacion": f"Factor integrado de {integration_row['numero_jornadas']} jornadas elegibles",
            "procedencia_academica": "Primaria",
            "subtipo_procedencia": "Derivación a partir de mediciones experimentales del TFG",
            "tratamiento_tfg": "Calculado por jornada e integrado estadísticamente",
            "fuente_concreta": "Materia seca y cenizas determinadas en Bioenergía durante M1 y M2",
            "uso_metodologico": "Conversión de masa húmeda entre A1 y A2",
        },
        {
            "id_familia": "ipcc_factors",
            "variable_o_familia": "Factores y procedimientos IPCC para manejo y suelos",
            "etapas": "A1, A2, A3, A4, B1 y B2",
            "valor_o_tipo_informacion": f"{len(ipcc_rows)} parámetros activos o de QA/QC con fuente IPCC",
            "procedencia_academica": "Secundaria",
            "subtipo_procedencia": "Guía metodológica oficial internacional",
            "tratamiento_tfg": "Factor metodológico",
            "fuente_concreta": "Refinamiento 2019 de las Directrices IPCC de 2006",
            "uso_metodologico": "Estimación de CH₄, N₂O y rutas hídricas de nitrógeno",
        },
        {
            "id_familia": "emep_factors",
            "variable_o_familia": "Factores EMEP/EEA de nitrógeno reactivo",
            "etapas": "A1, A2, A3, A4, B1 y B2",
            "valor_o_tipo_informacion": f"{len(emep_rows)} parámetros activos",
            "procedencia_academica": "Secundaria",
            "subtipo_procedencia": "Guía metodológica oficial de inventarios de emisiones",
            "tratamiento_tfg": "Factor metodológico",
            "fuente_concreta": "EMEP/EEA Air Pollutant Emission Inventory Guidebook 2023",
            "uso_metodologico": "Inicialización y pérdidas explícitas de TAN, NH₃, NO y N₂",
        },
        {
            "id_familia": "literature_factor",
            "variable_o_familia": "Factor experimental de NH₃ utilizado como aproximación en A2",
            "etapas": "A2",
            "valor_o_tipo_informacion": f"{len(literature_rows)} factor activo de literatura científica",
            "procedencia_academica": "Secundaria",
            "subtipo_procedencia": "Artículo científico utilizado como aproximación cuantitativa",
            "tratamiento_tfg": "Factor metodológico de literatura",
            "fuente_concreta": "Komakech et al. (2016)",
            "uso_metodologico": "Estimación de NH₃ en A2",
        },
        {
            "id_familia": "imn_factors",
            "variable_o_familia": "Factores nacionales para recursos energéticos",
            "etapas": "A3, A4, B1 y B2",
            "valor_o_tipo_informacion": f"{len(imn)} factores aprobados",
            "procedencia_academica": "Secundaria",
            "subtipo_procedencia": "Documento técnico oficial nacional",
            "tratamiento_tfg": "Factor de emisión o consumo agregado",
            "fuente_concreta": "Instituto Meteorológico Nacional, Factores de emisión de gases de efecto invernadero (2026)",
            "uso_metodologico": "Emisiones asociadas con electricidad y combustión de diésel",
        },
        {
            "id_familia": "ef31_factors",
            "variable_o_familia": "Factores de caracterización de impacto",
            "etapas": "A1, A2, A3, A4, B1 y B2",
            "valor_o_tipo_informacion": f"{len(characterization)} correspondencias flujo–categoría",
            "procedencia_academica": "Secundaria",
            "subtipo_procedencia": "Método oficial de evaluación de impacto",
            "tratamiento_tfg": "Factor de caracterización",
            "fuente_concreta": "Environmental Footprint 3.1 de la Comisión Europea y el JRC",
            "uso_metodologico": "Cambio climático, eutrofización terrestre y eutrofización marina",
        },
        {
            "id_familia": "calculated_inventory_flows",
            "variable_o_familia": "Masas, volúmenes y consumos del inventario",
            "etapas": "A1, A2, A3, A4, B1 y B2",
            "valor_o_tipo_informacion": f"{len(active_masses)} flujos por etapa construidos reproduciblemente",
            "procedencia_academica": "Mixta: primaria y secundaria",
            "subtipo_procedencia": "Procedencia heredada y separable de componentes primarios y secundarios; no constituye una tercera clase de fuente",
            "tratamiento_tfg": "Calculado o derivado",
            "fuente_concreta": "Caracterización y registros primarios, junto con publicaciones y bases bibliográficas secundarias, conservados en sus familias de origen",
            "uso_metodologico": "Datos de actividad del inventario por etapa; la futura matriz metodológica A1–B2 aportará trazabilidad más fina",
        },
        {
            "id_familia": "propagated_nitrogen",
            "variable_o_familia": "N total y TAN propagados entre etapas",
            "etapas": "A1→A2, A3→A4 y B1→B2",
            "valor_o_tipo_informacion": f"Parámetros experimentales promovidos en {len(active_parameters)} etapas y factores metodológicos",
            "procedencia_academica": "Mixta: primaria y secundaria",
            "subtipo_procedencia": "Procedencia heredada y separable de caracterización primaria y factores metodológicos secundarios; no constituye una tercera clase de fuente",
            "tratamiento_tfg": "Calculado y propagado entre etapas",
            "fuente_concreta": "Integración experimental M1–M2 (primaria) y factores IPCC, EMEP/EEA o de literatura (secundarios), conservados por componente",
            "uso_metodologico": "Cierre secuencial de nitrógeno y estimación de emisiones; la futura matriz metodológica A1–B2 aportará trazabilidad más fina",
        },
    ]
    validate_provenance_rows(rows)
    return rows


def validate_provenance_rows(rows: list[dict[str, str]]) -> None:
    """Aplica controles semánticos y de cobertura a la matriz generada."""

    ids = {row["id_familia"] for row in rows}
    assert ids == EXPECTED_FAMILY_IDS, f"Cobertura de familias inesperada: {sorted(ids ^ EXPECTED_FAMILY_IDS)}"
    assert all(row["procedencia_academica"] in ACADEMIC_PROVENANCE for row in rows)
    assert all(row["fuente_concreta"].strip() for row in rows)
    assert not any("M3" in " ".join(row.values()) for row in rows), "M3 no puede integrar la matriz activa"
    assert not any(
        row["procedencia_academica"] == "Terciaria"
        and any(token in row["tratamiento_tfg"].casefold() for token in ("calculado", "derivado", "integrado", "propagado"))
        for row in rows
    ), "Un tratamiento derivado no puede reclasificarse como fuente terciaria"

    integration = _read_csv(ACTIVE_SOURCES["integration"])
    for row in integration:
        eligible = {item for item in row["jornadas_elegibles"].split(";") if item}
        assert eligible <= {"M1", "M2"}, f"La integración activa contiene una jornada no autorizada: {eligible}"
        assert row["estado_integracion"] in {
            "provisional_M1_M2",
            "provisional_M2_pendiente_M3",
            "solo_caracterizacion",
        }

    evidence = ACTIVE_SOURCES["primary_evidence"].read_text(encoding="utf-8")
    for phrase in ("Mateo realizó personalmente", "Bioenergía", "CIA", "LASA"):
        assert phrase in evidence, f"Falta evidencia primaria esperada: {phrase}"


def build_provenance_summary_rows(
    detailed_rows: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Agrupa la matriz detallada en seis macrofamilias para el cuerpo académico."""

    rows = detailed_rows if detailed_rows is not None else build_provenance_rows()
    validate_provenance_rows(rows)
    available_ids = {row["id_familia"] for row in rows}
    grouped_ids = [
        family_id
        for definition in MACROFAMILY_DEFINITIONS
        for family_id in definition["family_ids"]
    ]
    assert len(grouped_ids) == len(set(grouped_ids)), "Una familia detallada aparece en más de una macrofamilia"
    assert set(grouped_ids) == available_ids, "La síntesis no cubre exactamente las familias detalladas"
    return [
        {
            "macrofamilia": str(definition["macrofamilia"]),
            "procedencia_general": str(definition["procedencia_general"]),
            "tratamiento_general": str(definition["tratamiento_general"]),
            "funcion_icv": str(definition["funcion_icv"]),
        }
        for definition in MACROFAMILY_DEFINITIONS
    ]


def academic_columns() -> list[str]:
    return [
        "variable_o_familia",
        "etapas",
        "valor_o_tipo_informacion",
        "procedencia_academica",
        "subtipo_procedencia",
        "tratamiento_tfg",
        "fuente_concreta",
        "uso_metodologico",
    ]
