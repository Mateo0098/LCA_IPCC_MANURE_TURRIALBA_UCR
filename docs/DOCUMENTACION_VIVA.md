# Registro de documentación viva y generada

## Propósito

Este registro identifica la función, responsabilidad y disparador de revisión de
la documentación versionada del repositorio. Es un índice de orientación: no
duplica las reglas, decisiones ni resultados contenidos en cada fuente.

Las categorías son:

- **A. Documento vivo canónico:** gobierna o describe el estado general vigente.
- **B. Documento especializado vivo:** describe un componente concreto.
- **C. Manifiesto generado:** lo escribe un generador o validador y debe corresponder a sus artefactos.
- **D. Referencia estática:** conserva el contexto o resultado de una revisión histórica y no se actualiza como si describiera el estado vigente.
- **E. Candidato a retiro:** perdió una función diferenciada o duplica una fuente responsable; no se elimina sin documentar antes la decisión.

## Regla de mantenimiento

Todo documento versionado que describa el estado vigente de un componente debe
formar parte de la revisión de cierre cuando ese componente cambie. La selección
es contextual: este registro orienta la búsqueda, pero no sustituye la inspección
de referencias y documentación específica del componente afectado.

Los manifiestos generados se actualizan mediante su generador y se validan contra
los artefactos de la misma corrida. Las referencias estáticas conservan el estado
de la revisión que documentan y no se reinterpretan como fuentes vigentes. Si un
documento deja de ser necesario, debe proponerse su retiro, integración,
sustitución o traslado antes de eliminarlo, dejando documentada la decisión.

## Documentos vivos

| Documento | Función | Clasificación | Fuente responsable | Se revisa cuando cambia | Mantenimiento | Estado |
|---|---|---|---|---|---|---|
| `README.md` | Estado y ejecución del pipeline canónico | A | Pipeline vigente | Arquitectura, secuencia, fronteras, parámetros activos, outputs o validadores | Manual | Vigente |
| `AGENTS.md` | Reglas obligatorias para agentes | A | Gobernanza de agentes | Reglas operativas, académicas, documentales o de validación | Manual | Vigente |
| `CHATGPT_CODEX_WORKFLOW.md` | Coordinación Mateo–ChatGPT–Codex | A | Flujo de coordinación | Objetivos, cierre, reportes, Git o transiciones de contexto | Manual | Vigente |
| `DECISIONES_METODOLOGICAS_TFG.md` | Decisiones científicas aprobadas | A | Investigador | Metodología sustantiva, supuestos, sistemas IPCC o integración estadística aprobada | Manual, con aprobación | Vigente |
| `README_METODOLOGIA.md` | Explicación técnica detallada del método y pipeline | B | Implementación metodológica | Ingestión, integración, ecuaciones, parámetros, orden de ejecución o salidas | Manual | Potencialmente desactualizado; evaluar integración o reestructuración |
| `DICCIONARIO_TRAZABILIDAD_VARIABLES.md` | Mapa de variables, fuentes, fórmulas y salidas | B | Capas de datos y cálculo | Variables, unidades, fuentes canónicas, fórmulas o consumidores | Manual | Potencialmente desactualizado; requiere mantenimiento explícito |
| `docs/REGLAS_FORMATO_WORD.md` | Especificación de documentos Word | B | Generadores y validación documental | Formato, nomenclatura, captions, ecuaciones o validadores Word | Manual | Vigente |
| `docs/DOCUMENTACION_VIVA.md` | Índice de responsabilidad documental | A | Gobernanza documental | Se crea, retira, reclasifica o cambia de responsable un documento relevante | Manual | Vigente |

## Manifiestos y reportes generados

| Documento | Función | Fuente responsable | Se regenera cuando cambia | Estado |
|---|---|---|---|---|
| `auditoria_integracion_estadistica_m1_m2.md` | Reporte de integración estadística vigente | `scripts/build_sampling_integration.py` | Ingestión, reglas o datos integrados | Generado |
| `outputs/graficos_tesis/README_GRAFICOS.md` | Manifiesto de figuras y tablas fuente | `scripts/generate_thesis_graphics.py` | Figuras, tablas fuente o asignación documental | Generado y sujeto a validación contra outputs |
| `outputs/tablas_tesis/resumen_resultados_para_redaccion.md` | Resumen narrativo de tablas e impactos | `scripts/generate_thesis_tables.py` | Tablas o resultados | Generado |
| `outputs/documentos_tfg/README_DOCUMENTOS_GENERADOS.md` | Manifiesto de documentos, tablas y figuras | `scripts/generate_results_docx.py` | Documentos, tablas, figuras o formato | Generado; verificar cobertura del documento de conclusiones |
| `outputs/documentos_tfg/reporte_validacion_documentos.md` | Validación documental detallada | `scripts/generate_results_docx.py` | Cualquier documento Word generado o sus reglas | Generado |
| `outputs/documentos_tfg/reporte_formato_master.md` | Perfil aplicado desde el MASTER | `scripts/generate_results_docx.py` | Formato o generadores Word | Generado |
| `outputs/documentos_tfg/reporte_relacion_apendices.md` | Relación entre prosa y apéndices | `scripts/generate_results_docx.py` | Contenido o estructura de documentos | Generado |
| `outputs/documentos_tfg/reporte_referencias_factores.md` | Trazabilidad de factores citados | `scripts/generate_results_docx.py` | Factores, referencias o documentos | Generado |
| `outputs/documentos_tfg/reporte_correccion_factor_estequiometrico_NO3.md` | Control del factor estequiométrico | `scripts/generate_results_docx.py` | Cálculo o documentación de nitrato | Generado |
| `outputs/documentos_tfg/reporte_validacion_provisional_m1_m2.md` | Validación cruzada de la corrida completa | `scripts/validate_provisional_m1_m2_outputs.py` | Cualquier capa de la corrida vigente | Generado |
| `outputs/documentos_tfg/trazabilidad_conclusiones_tfg.md` | Matriz de conclusiones y objetivos | `scripts/generate_conclusions_docx.py` | Conclusiones, objetivos o resultados | Generado |

Los manifiestos generados no deben corregirse manualmente cuando la corrección
pueda aplicarse en su generador. Deben pertenecer a la misma corrida que los
outputs que describen.

## Referencias estáticas

Las siguientes auditorías conservan evidencia de tareas o decisiones en un
momento determinado. Se consultan cuando su asunto es relevante, pero no se
mantienen como descripciones del estado vigente:

- `auditoria_aclaraciones_cia_precision_base_n.md`
- `auditoria_actualizacion_flujos_sanchez_2026.md`
- `auditoria_alineacion_tfg.md`
- `auditoria_base_n_precompostado.md`
- `auditoria_cierre_documental_metodologia_2026.md`
- `auditoria_correccion_balance_escenario_B_y_UF.md`
- `auditoria_eutrofizacion_B1.md`
- `auditoria_ingestion_m1_m2.md`
- `auditoria_integracion_muestreo_2.md`
- `auditoria_mapa_parametros_experimentales_acv.md`
- `auditoria_regeneracion_metodologia_resultados_2026.md`
- `outputs/reporte_correccion_graficos_eje_x.md`
- `outputs/reporte_correccion_nombres_etapas.md`
- `outputs/reporte_limpieza_correccion_nitrogeno.md`
- `outputs/reporte_regeneracion_word_resultados.md`
- `outputs/reporte_revision_flujos_A4_B2.md`

Conviene evaluar en una tarea separada si estas referencias deben permanecer en
la raíz y en `outputs/`, trasladarse a un archivo histórico o retirarse después
de preservar la información permanente en su fuente canónica.

## Selección contextual al cierre

La revisión no parte de una lista fija idéntica para todas las tareas:

- Un cambio de sistema IPCC en A2 exige revisar las decisiones metodológicas,
  la metodología especializada, la configuración y ejecución del pipeline, el
  diccionario de trazabilidad y los manifiestos o documentos regenerados
  afectados.
- Un cambio exclusivo de generación de figuras exige revisar el generador, el
  manifiesto de gráficos y las reglas documentales aplicables, pero no modifica
  por sí mismo las decisiones metodológicas.

ChatGPT identifica el conjunto documental afectado durante la revisión de
cierre. Codex inspecciona los documentos indicados en el prompt, comprueba sus
referencias inmediatas y reporta cualquier documento adicional que resulte
afectado o potencialmente obsoleto.
