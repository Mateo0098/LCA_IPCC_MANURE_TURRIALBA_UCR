from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal


AcronymKind = Literal[
    "sigla_espanola",
    "sigla_inglesa",
    "abreviatura_institucional",
    "denominacion_convencional",
]


@dataclass(frozen=True)
class AcronymEntry:
    code: str
    spanish_name: str
    original_name: str | None
    origin_language: str
    first_mention: str
    include_in_list: bool = True
    kind: AcronymKind = "sigla_espanola"

    @property
    def requires_english_notice(self) -> bool:
        return self.kind == "sigla_inglesa"

    @property
    def list_definition(self) -> str:
        if self.kind == "abreviatura_institucional":
            return (
                f"{self.spanish_name}; {self.original_name} "
                "(denominación oficial en inglés; ISO es la forma abreviada universal)"
            )
        if self.kind == "denominacion_convencional":
            return (
                f"{self.spanish_name}; {self.original_name} "
                "(denominación oficial en inglés; EMEP es la denominación abreviada establecida)"
            )
        if self.requires_english_notice and self.original_name:
            return (
                f"{self.spanish_name}; {self.original_name} "
                "(denominación original en inglés)"
            )
        return self.spanish_name


ACRONYMS: tuple[AcronymEntry, ...] = (
    AcronymEntry("ACV", "análisis de ciclo de vida", None, "español", "análisis de ciclo de vida (ACV)"),
    AcronymEntry("AWMS", "sistema de manejo de desechos animales", "animal waste management system", "inglés", "sistema de manejo de desechos animales (AWMS, por sus siglas en inglés)", kind="sigla_inglesa"),
    AcronymEntry("CIA", "Centro de Investigaciones Agronómicas", None, "español", "Centro de Investigaciones Agronómicas (CIA)"),
    AcronymEntry("DA", "digestión anaeróbica", None, "español", "digestión anaeróbica (DA)"),
    AcronymEntry("EEA", "Agencia Europea de Medio Ambiente", "European Environment Agency", "inglés", "Agencia Europea de Medio Ambiente (EEA, por sus siglas en inglés)", kind="sigla_inglesa"),
    AcronymEntry("EF 3.1", "método de Huella Ambiental 3.1", "Environmental Footprint 3.1", "inglés", "método de Huella Ambiental 3.1 (EF 3.1, por sus siglas en inglés)", kind="sigla_inglesa"),
    AcronymEntry("EICV", "evaluación del impacto del ciclo de vida", None, "español", "evaluación del impacto del ciclo de vida (EICV)"),
    AcronymEntry("EMEP", "Programa cooperativo de seguimiento y evaluación del transporte a larga distancia de contaminantes atmosféricos en Europa", "Co-operative Programme for Monitoring and Evaluation of the Long-range Transmission of Air Pollutants in Europe", "inglés", "Programa cooperativo de seguimiento y evaluación del transporte a larga distancia de contaminantes atmosféricos en Europa (EMEP)", kind="denominacion_convencional"),
    AcronymEntry("GEI", "gases de efecto invernadero", None, "español", "gases de efecto invernadero (GEI)"),
    AcronymEntry("ICV", "inventario del ciclo de vida", None, "español", "inventario del ciclo de vida (ICV)"),
    AcronymEntry("IMN", "Instituto Meteorológico Nacional", None, "español", "Instituto Meteorológico Nacional (IMN)"),
    AcronymEntry("INEC", "Instituto Nacional de Estadística y Censos", None, "español", "Instituto Nacional de Estadística y Censos (INEC)"),
    AcronymEntry("IPCC", "Grupo Intergubernamental de Expertos sobre el Cambio Climático", "Intergovernmental Panel on Climate Change", "inglés", "Grupo Intergubernamental de Expertos sobre el Cambio Climático (IPCC, por sus siglas en inglés)", kind="sigla_inglesa"),
    AcronymEntry("ISO", "Organización Internacional de Normalización", "International Organization for Standardization", "universal", "Organización Internacional de Normalización (ISO)", kind="abreviatura_institucional"),
    AcronymEntry("JRC", "Centro Común de Investigación", "Joint Research Centre", "inglés", "Centro Común de Investigación (JRC, por sus siglas en inglés)", kind="sigla_inglesa"),
    AcronymEntry("LASA", "Laboratorios de Servicios Analíticos de la Escuela de Química", None, "español", "Laboratorios de Servicios Analíticos de la Escuela de Química (LASA)"),
    AcronymEntry("MAG", "Ministerio de Agricultura y Ganadería", None, "español", "Ministerio de Agricultura y Ganadería (MAG)"),
    AcronymEntry("MCF", "factor de conversión de metano", "methane conversion factor", "inglés", "factor de conversión de metano (MCF, por sus siglas en inglés)", kind="sigla_inglesa"),
    AcronymEntry("MO", "materia orgánica", None, "español", "materia orgánica (MO)"),
    AcronymEntry("MS", "materia seca", None, "español", "materia seca (MS)"),
    AcronymEntry("NRCS", "Servicio de Conservación de Recursos Naturales de los Estados Unidos", "Natural Resources Conservation Service", "inglés", "Servicio de Conservación de Recursos Naturales de los Estados Unidos (NRCS, por sus siglas en inglés)", kind="sigla_inglesa"),
    AcronymEntry("PCG", "potencial de calentamiento global", None, "español", "potencial de calentamiento global (PCG)"),
    AcronymEntry("PIB", "producto interno bruto", None, "español", "producto interno bruto (PIB)"),
    AcronymEntry("SV", "sólidos volátiles", None, "español", "sólidos volátiles (SV)"),
    AcronymEntry("TAN", "nitrógeno amoniacal total", "Total Ammoniacal Nitrogen", "inglés", "nitrógeno amoniacal total (TAN, por sus siglas en inglés)", kind="sigla_inglesa"),
    AcronymEntry("TFG", "trabajo final de graduación", None, "español", "trabajo final de graduación (TFG)"),
    AcronymEntry("UCR", "Universidad de Costa Rica", None, "español", "Universidad de Costa Rica (UCR)"),
    AcronymEntry("USDA", "Departamento de Agricultura de los Estados Unidos", "United States Department of Agriculture", "inglés", "Departamento de Agricultura de los Estados Unidos (USDA, por sus siglas en inglés)", kind="sigla_inglesa"),
)


# Exclusiones deliberadas para la auditoría conservadora del texto académico.
# Cada elemento pertenece a una categoría que no debe alimentar la lista de siglas.
IGNORED_ACRONYM_CANDIDATES: dict[str, str] = {
    **{code: "código de etapa" for code in ("A1", "A2", "A3", "A4", "B1", "B2")},
    **{code: "código de jornada" for code in ("M1", "M2", "M3")},
    "CF": "símbolo de factor de caracterización en una ecuación",
    "CC": "símbolo de cambio climático en una ecuación",
    "FE": "símbolo de factor de emisión en una ecuación",
    "EF1": "identificador de factor en las directrices IPCC",
    "EF3": "identificador de factor en las directrices IPCC",
    "EF4": "identificador de factor en las directrices IPCC",
    "EF5": "identificador de factor en las directrices IPCC",
    "ISO/TC": "identificador de comité técnico asociado a una norma",
    "MBA": "grado académico",
    "NO": "fórmula química",
    "NO-N": "especie química expresada como nitrógeno",
    "NO2": "fórmula química",
    "N2": "fórmula química",
    "PDF": "formato de archivo de uso convencional",
    "PROVISIONAL": "rótulo de estado documental",
    "TAN/N": "relación entre variables científicas",
    "MCF/100": "factor expresado como fracción en una ecuación",
    "MS/100": "porcentaje convertido a fracción en una ecuación",
    "SV/100": "porcentaje convertido a fracción en una ecuación",
    "VAIA": "marca del equipo",
    "VS": "símbolo de variable en una ecuación",
}

_CANDIDATE_PATTERN = re.compile(
    r"(?<![\w])(?:[A-ZÁÉÍÓÚÜÑ]{1,5}\s\d(?:\.\d+)+|"
    r"[A-ZÁÉÍÓÚÜÑ]{2,}(?:[-/][A-ZÁÉÍÓÚÜÑ0-9]{1,})*|"
    r"[A-ZÁÉÍÓÚÜÑ]{1,3}\d)(?![\w])"
)


def acronym_is_used(text: str, code: str) -> bool:
    return bool(re.search(rf"(?<![\w]){re.escape(code)}(?![\w])", text))


def used_acronyms(text: str) -> list[AcronymEntry]:
    return [entry for entry in ACRONYMS if entry.include_in_list and acronym_is_used(text, entry.code)]


def acronym_by_code(code: str) -> AcronymEntry:
    return next(entry for entry in ACRONYMS if entry.code == code)


def unregistered_acronym_candidates(texts: list[str]) -> dict[str, str]:
    """Devuelve candidatos no clasificados y su primer contexto visible."""
    known = {entry.code for entry in ACRONYMS}
    unknown: dict[str, str] = {}
    for text in texts:
        for match in _CANDIDATE_PATTERN.finditer(text):
            candidate = match.group(0)
            if candidate in known or candidate in IGNORED_ACRONYM_CANDIDATES:
                continue
            if "/" in candidate and all(part in known for part in candidate.split("/")):
                continue
            # Evita reportar una parte de una entrada compuesta, por ejemplo EF en EF 3.1.
            if any(
                entry.code != candidate
                and acronym_is_used(text, entry.code)
                and match.start() >= found.start()
                and match.end() <= found.end()
                for entry in ACRONYMS
                for found in re.finditer(rf"(?<![\w]){re.escape(entry.code)}(?![\w])", text)
            ):
                continue
            unknown.setdefault(candidate, text.strip())
    return dict(sorted(unknown.items()))
