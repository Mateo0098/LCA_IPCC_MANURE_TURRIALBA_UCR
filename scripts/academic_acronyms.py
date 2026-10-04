from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class AcronymEntry:
    code: str
    spanish_name: str
    original_name: str | None
    origin_language: str
    first_mention: str
    include_in_list: bool = True

    @property
    def list_definition(self) -> str:
        if self.origin_language == "inglés" and self.original_name:
            return (
                f"{self.spanish_name}; {self.original_name} "
                "(denominación original en inglés)"
            )
        return self.spanish_name


ACRONYMS: tuple[AcronymEntry, ...] = (
    AcronymEntry("ACV", "análisis de ciclo de vida", None, "español", "análisis de ciclo de vida (ACV)"),
    AcronymEntry("AWMS", "sistema de manejo de desechos animales", "animal waste management system", "inglés", "sistema de manejo de desechos animales (AWMS, por sus siglas en inglés)"),
    AcronymEntry("CIA", "Laboratorio de Suelos y Foliares de la Ciudad de la Investigación", None, "español", "Laboratorio de Suelos y Foliares de la Ciudad de la Investigación (CIA)"),
    AcronymEntry("EEA", "Agencia Europea de Medio Ambiente", "European Environment Agency", "inglés", "Agencia Europea de Medio Ambiente (EEA, por sus siglas en inglés)"),
    AcronymEntry("EF 3.1", "método de Huella Ambiental 3.1", "Environmental Footprint 3.1", "inglés", "método de Huella Ambiental 3.1 (EF 3.1, por sus siglas en inglés)"),
    AcronymEntry("EICV", "evaluación del impacto del ciclo de vida", None, "español", "evaluación del impacto del ciclo de vida (EICV)"),
    AcronymEntry("EMEP", "Programa cooperativo de seguimiento y evaluación del transporte a larga distancia de contaminantes atmosféricos en Europa", "Co-operative programme for monitoring and evaluation of the long-range transmission of air pollutants in Europe", "inglés", "Programa cooperativo de seguimiento y evaluación del transporte a larga distancia de contaminantes atmosféricos en Europa (EMEP, por sus siglas en inglés)"),
    AcronymEntry("GEI", "gases de efecto invernadero", None, "español", "gases de efecto invernadero (GEI)"),
    AcronymEntry("ICV", "inventario del ciclo de vida", None, "español", "inventario del ciclo de vida (ICV)"),
    AcronymEntry("IMN", "Instituto Meteorológico Nacional", None, "español", "Instituto Meteorológico Nacional (IMN)"),
    AcronymEntry("INEC", "Instituto Nacional de Estadística y Censos", None, "español", "Instituto Nacional de Estadística y Censos (INEC)"),
    AcronymEntry("IPCC", "Grupo Intergubernamental de Expertos sobre el Cambio Climático", "Intergovernmental Panel on Climate Change", "inglés", "Grupo Intergubernamental de Expertos sobre el Cambio Climático (IPCC, por sus siglas en inglés)"),
    AcronymEntry("ISO", "Organización Internacional de Normalización", "International Organization for Standardization", "inglés", "Organización Internacional de Normalización (ISO, por sus siglas en inglés)"),
    AcronymEntry("JRC", "Centro Común de Investigación", "Joint Research Centre", "inglés", "Centro Común de Investigación (JRC, por sus siglas en inglés)"),
    AcronymEntry("LASA", "Laboratorios de Servicios Analíticos de la Escuela de Química", None, "español", "Laboratorios de Servicios Analíticos de la Escuela de Química (LASA)"),
    AcronymEntry("MAG", "Ministerio de Agricultura y Ganadería", None, "español", "Ministerio de Agricultura y Ganadería (MAG)"),
    AcronymEntry("MCF", "factor de conversión de metano", "methane conversion factor", "inglés", "factor de conversión de metano (MCF, por sus siglas en inglés)"),
    AcronymEntry("MO", "materia orgánica", None, "español", "materia orgánica (MO)"),
    AcronymEntry("MS", "materia seca", None, "español", "materia seca (MS)"),
    AcronymEntry("NRCS", "Servicio de Conservación de Recursos Naturales de los Estados Unidos", "Natural Resources Conservation Service", "inglés", "Servicio de Conservación de Recursos Naturales de los Estados Unidos (NRCS, por sus siglas en inglés)"),
    AcronymEntry("PCG", "potencial de calentamiento global", None, "español", "potencial de calentamiento global (PCG)"),
    AcronymEntry("PIB", "producto interno bruto", None, "español", "producto interno bruto (PIB)"),
    AcronymEntry("SV", "sólidos volátiles", None, "español", "sólidos volátiles (SV)"),
    AcronymEntry("TAN", "nitrógeno amoniacal total", "Total Ammoniacal Nitrogen", "inglés", "nitrógeno amoniacal total (TAN, por sus siglas en inglés)"),
    AcronymEntry("TFG", "trabajo final de graduación", None, "español", "trabajo final de graduación (TFG)"),
    AcronymEntry("UCR", "Universidad de Costa Rica", None, "español", "Universidad de Costa Rica (UCR)"),
    AcronymEntry("USDA", "Departamento de Agricultura de los Estados Unidos", "United States Department of Agriculture", "inglés", "Departamento de Agricultura de los Estados Unidos (USDA, por sus siglas en inglés)"),
)


def acronym_is_used(text: str, code: str) -> bool:
    return bool(re.search(rf"(?<![\w]){re.escape(code)}(?![\w])", text))


def used_acronyms(text: str) -> list[AcronymEntry]:
    return [entry for entry in ACRONYMS if entry.include_in_list and acronym_is_used(text, entry.code)]


def acronym_by_code(code: str) -> AcronymEntry:
    return next(entry for entry in ACRONYMS if entry.code == code)
