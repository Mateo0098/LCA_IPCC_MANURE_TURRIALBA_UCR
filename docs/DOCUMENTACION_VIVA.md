# Registro de documentación viva y generada

## Propósito

Este registro identifica la función, responsabilidad y disparador de revisión de
la documentación versionada del repositorio. Es un índice de orientación: no
duplica las reglas, decisiones ni resultados contenidos en cada fuente.
Representa el estado actual del repositorio y evoluciona con él: los documentos
pueden incorporarse, integrarse, reclasificarse o retirarse según cambien sus
funciones y responsabilidades.

Las categorías son:

- **A. Documento vivo canónico:** gobierna o describe el estado general vigente.
- **B. Documento especializado vivo:** describe un componente concreto.
- **C. Manifiesto generado:** lo escribe un generador o validador y debe corresponder a sus artefactos.
- **D. Revisión pendiente:** conserva información única que aún requiere una decisión y no se interpreta como estado vigente.

## Regla de mantenimiento

Todo documento versionado que describa el estado vigente de un componente debe
formar parte de la revisión de cierre cuando ese componente cambie. La selección
es contextual: este registro orienta la búsqueda, pero no sustituye la inspección
de referencias y documentación específica del componente afectado.

Los manifiestos generados se actualizan mediante su generador y se validan contra
los artefactos de la misma corrida. Una revisión puntual no se conserva como
auditoría histórica cuando sus hallazgos ya fueron resueltos y la información
permanente reside en su fuente responsable: Git permite recuperar ese estado si
fuera necesario. Si contiene una decisión todavía abierta, se mantiene solo
hasta resolverla y nunca se interpreta como fuente del estado vigente.

## Documentos vivos

| Documento | Función | Clasificación | Fuente responsable | Se revisa cuando cambia | Mantenimiento | Estado |
|---|---|---|---|---|---|---|
| `README.md` | Estado y ejecución del pipeline canónico | A | Pipeline vigente | Arquitectura, secuencia, fronteras, parámetros activos, outputs o validadores | Manual | Vigente |
| `AGENTS.md` | Reglas obligatorias para agentes | A | Gobernanza de agentes | Reglas operativas, académicas, documentales o de validación | Manual | Vigente |
| `CHATGPT_CODEX_WORKFLOW.md` | Coordinación Mateo–ChatGPT–Codex | A | Flujo de coordinación | Objetivos, cierre, reportes, Git o transiciones de contexto | Manual | Vigente |
| `DECISIONES_METODOLOGICAS_TFG.md` | Decisiones científicas aprobadas | A | Investigador | Metodología sustantiva, supuestos, sistemas IPCC o integración estadística aprobada | Manual, con aprobación | Vigente |
| `README_METODOLOGIA.md` | Explicación técnica detallada del método y pipeline | B | Implementación metodológica | Ingestión, integración, ecuaciones, parámetros, orden de ejecución o salidas | Manual | Potencialmente desactualizado; evaluar integración o reestructuración |
| `DICCIONARIO_TRAZABILIDAD_VARIABLES.md` | Mapa de variables, fuentes, fórmulas y salidas | B | Capas de datos y cálculo | Variables, unidades, fuentes canónicas, fórmulas o consumidores | Manual | Revisado para la representación IPCC, la base de N y el contraste bibliográfico de A2 |
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

## Revisiones pendientes de decisión

Estas revisiones conservan hallazgos aún no cerrados y no describen por sí solas
el estado vigente:

- `auditoria_alineacion_tfg.md`: vacíos de alineación entre objetivos, resultados
  y conclusiones que requieren seguimiento académico.
- `auditoria_eutrofizacion_B1.md`: observación científica sobre la representación
  del nitrógeno potencialmente eutrofizante que requiere criterio del investigador.

Una vez resuelta cada decisión, su resultado permanente debe incorporarse en la
fuente responsable y la auditoría debe retirarse, sin crear una carpeta histórica
por defecto.

## Selección contextual al cierre

La revisión no parte de una lista fija idéntica para todas las tareas:

- Un cambio metodológico importante exige revisar las decisiones metodológicas,
  la documentación especializada, la configuración y ejecución del pipeline,
  la trazabilidad y los manifiestos o productos regenerados afectados.
- Un cambio exclusivo de generación de figuras exige revisar el generador, el
  manifiesto de gráficos y las reglas documentales aplicables, pero no modifica
  por sí mismo las decisiones metodológicas.

ChatGPT identifica el conjunto documental afectado durante la revisión de
cierre. Codex inspecciona los documentos indicados en el prompt, comprueba sus
referencias inmediatas y reporta cualquier documento adicional que resulte
afectado o potencialmente obsoleto.
