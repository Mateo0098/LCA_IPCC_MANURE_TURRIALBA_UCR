# Instrucciones para Codex en este repositorio



## Objetivo del proyecto



Este repositorio corresponde al TFG sobre análisis de ciclo de vida de desechos bovinos sólidos y líquidos producidos en una lechería especializada en Turrialba, Costa Rica.



El objetivo es generar tablas, figuras y documentos académicos para tesis, no reportes técnicos de programación.



## Reglas generales



- No modificar el documento maestro de propuesta salvo instrucción explícita.

- No usar archivos con sufijo `antes_correccion_nitrogeno`.

- No hacer commit automáticamente.

- Si la rama activa no parece corresponder con el contexto solicitado, señalarlo antes de realizar cambios potencialmente incorrectos.

- Mantener valores numéricos, factores, ecuaciones y resultados salvo que la tarea pida explícitamente recalcular.

- Corregir los scripts generadores, no solo los archivos finales.

- El documento maestro protegido está en `MASTER_escrito/TFG_ACV_Estiercol_MASTER.docx`.

- No modificar, sobrescribir ni usar como archivo de salida ningún archivo dentro de `MASTER_escrito/`.

- Los generadores pueden usar el documento maestro únicamente como referencia de formato y deben verificar su hash antes y después de generar documentos.

- El flujo de coordinación con Mateo y ChatGPT se documenta en `CHATGPT_CODEX_WORKFLOW.md`.

- Cuando un prompt solicite un reporte de ejecución, guardarlo en la ruta indicada dentro de `.codex_reports/`. Estos reportes son temporales, no constituyen fuente de verdad ni entrada del pipeline y no deben incluirse en commits ordinarios.

- No hacer commit, push, integración ni cambio de rama por iniciativa propia. Un prompt específico preparado por ChatGPT autoriza únicamente las operaciones Git, los archivos y las ramas que describe; no ampliar ese alcance.

- Un prompt de implementación puede autorizar expresamente a Codex a implementar, realizar verificaciones técnicas, crear y publicar un checkpoint de revisión y generar el reporte, sin requerir un segundo prompt de commit/push. Esta autorización no se presume, no se amplía y nunca autoriza por sí sola la integración a `main`.

- Antes de crear un checkpoint autorizado, revisar el alcance y el diff, detectar archivos accidentales, ejecutar `git diff --check`, aplicar las comprobaciones de sintaxis, validadores, regeneraciones y controles de coherencia pertinentes, y confirmar que `.codex_reports/` y temporales no entren al commit. La selección debe ser proporcional al cambio.

- Si fallan validadores, existen errores conocidos, cambios accidentales, resultados inesperados no resueltos o ambigüedades que requieren decisión de Mateo o ChatGPT, no crear el checkpoint salvo instrucción excepcional y explícita; generar el reporte y dejar la unidad pendiente.

- Un checkpoint publicado solo acredita un estado técnicamente preparado para revisión. No equivale a validación metodológica, científica, documental o supervisora, no cierra automáticamente la unidad y no autoriza integración a `main`. Codex verifica; ChatGPT valida.

- Ante un checkpoint rechazado, Codex no decide por sí mismo si corregir hacia adelante o regresar a un estado validado: ejecuta únicamente la estrategia y las operaciones Git especificadas por ChatGPT. Las correcciones se realizan normalmente sobre la misma rama activa mediante nuevos commits y nuevos SHA; no reescribir historia publicada con `reset --hard`, `rebase`, `amend` ni `force-push` salvo razón real y autorización excepcional y explícita de Mateo o ChatGPT.

- Tratar `.codex_reports/` como bandeja temporal. Al comenzar, durante y al cerrar una unidad, evaluar de forma conservadora si pueden eliminarse reportes de unidades ya cerradas. Conservar los necesarios para revisión, validación, cierre Git o decisiones vigentes; ante duda, conservar. No borrar el reporte solicitado por el prompt, no actuar fuera de `.codex_reports/` bajo esta regla y trasladar primero a su fuente responsable cualquier información permanente que solo exista en un reporte.



## Contexto Git obligatorio para tareas de Codex



Antes de realizar cualquier modificación, Codex debe:



1. Ejecutar `git branch --show-current`.
2. Registrar la rama activa, el commit `HEAD` y el estado general del working tree al inicio.
3. Trabajar exclusivamente sobre la rama activa encontrada.
4. No cambiar de rama por iniciativa propia, salvo que el prompt lo solicite explícitamente.
5. No interpretar una rama histórica conservada como respaldo como fuente vigente ni como línea activa de trabajo.



Antes de finalizar la tarea, Codex debe volver a ejecutar `git branch --show-current` y registrar la rama activa, el commit `HEAD` y el estado general del working tree al finalizar. Si la rama cambia durante la ejecución, debe indicarlo explícitamente en el reporte y explicar la causa.



Todo reporte dentro de `.codex_reports/` debe contener cerca del inicio una sección con este formato:



```markdown
## Contexto Git

- Rama al inicio: `...`
- HEAD inicial: `...`
- Working tree inicial: limpio / con cambios
- Rama al finalizar: `...`
- HEAD final: `...`
- Working tree final: limpio / con cambios
- Cambio de rama durante la tarea: sí / no
```



Si hubo un cambio de rama, se debe añadir una breve explicación. La rama indicada en el reporte permite que ChatGPT identifique la referencia vigente de la tarea y detecte cambios de rama sin una notificación manual separada.



## Cierre y reportes de tareas



Cuando una tarea genere un reporte, este debe permitir que ChatGPT conozca, como mínimo:



- el contexto Git obligatorio;
- el objetivo concreto de la unidad de trabajo y si inicia una unidad nueva o continúa una anterior;
- su estado de cierre y, cuando ya exista, el commit o los commits que la consolidan;
- los archivos inspeccionados, modificados y creados;
- los cambios implementados;
- los comandos ejecutados;
- las validaciones realizadas y sus resultados;
- la documentación actualizada;
- los pendientes y anomalías;
- cualquier decisión que todavía requiera intervención del investigador.

Cuando la tarea cree un checkpoint, el reporte debe añadir como mínimo:

```markdown
## Estado del checkpoint

- Repositorio: `owner/repository`
- Rama: `...`
- Commit de revisión: `SHA completo`
- Publicado en remoto: sí / no
- Validaciones técnicas de Codex: PASS / FAIL / parcial
- Revisión de ChatGPT: pendiente
- Integración a `main`: no autorizada
```

También debe incluir `## Archivos potencialmente relevantes para revisión de ChatGPT`. Para cada archivo modificado, creado, eliminado o generado potencialmente relevante, registrar la ruta exacta, el tipo y motivo del cambio, si está incluido en el checkpoint publicado y si Codex considera que contiene una decisión, implementación o resultado que merece revisión supervisora. Codex facilita la selección, pero no decide definitivamente qué debe revisar ChatGPT.



Si una tarea cambia metodología, pipeline, arquitectura, gobernanza o reglas permanentes y el prompt incluye actualización documental, Codex debe consultar `docs/DOCUMENTACION_VIVA.md`, revisar los documentos indicados y comprobar antes de reportarla como terminada que la documentación correspondiente quedó actualizada y coherente. La selección debe responder al componente afectado y no limitarse siempre a los mismos documentos generales. Si descubre otra guía o manifiesto afectado, debe indicarlo en el reporte. Los manifiestos generados se corrigen desde su generador cuando corresponda, no solo en el archivo final.



Codex debe reportar los documentos redundantes, obsoletos o sin función clara que detecte. No debe eliminarlos por iniciativa propia: su retiro, integración, sustitución o traslado requiere una instrucción y una decisión documentada. Codex tampoco debe decidir por iniciativa propia cuándo crear un nuevo chat, una nueva rama o una nueva sesión; esas transiciones pertenecen al flujo de coordinación entre Mateo y ChatGPT documentado en `CHATGPT_CODEX_WORKFLOW.md`. La prohibición de cambiar de rama sin solicitud explícita continúa vigente.



## Escritura académica



Los documentos Word deben usar redacción académica y científica.



No usar en prosa ni tablas académicas etiquetas internas como:



- `dry_lot`

- `uncovered_anaerobic_lagoon`

- `composting_invessel`

- `modelo_calculo`

- `sistema_manejo_ipcc`

- `n_ex_pct`

- `n_ex_fraction`

- `masa_total_kg_eq`

- `processed`

- `outputs`

- `scripts`

- `.csv`

- `hardcodeado`

- `auditado`



Reemplazar etiquetas técnicas por lenguaje académico claro.



## Nomenclatura de escenarios y etapas



Usar siempre:



- A1: Precomposteo

- A2: Lombricompostaje

- A3: Almacenamiento de aguas verdes

- A4: Aplicación de aguas verdes en campos de pastoreo

- B1: Almacenamiento de purines

- B2: Aplicación de purines en campo de pastoreo



No mostrar etapas con decimales, por ejemplo:



- 1,000

- 2,000

- 3,000

- 4,000

- 1.0000

- 2.0000



## Aguas verdes y purines



En el Escenario A no usar la palabra “purín” ni “purines” para nombrar flujos.



Para A4 usar:



- Agua de lavado incorporada a las aguas verdes

- Fracción de boñiga incorporada a las aguas verdes

- Masa equivalente total



Para B2 usar:



- Agua de lavado incorporada al purín

- Boñiga incorporada al purín

- Masa equivalente total



## Tablas en documentos Word



Las tablas deben verse académicas.



- No duplicar columnas relacionadas con etapa.

- Evitar columnas como `Etapa` y `Nombre etapa` al mismo tiempo.

- Usar preferiblemente una sola columna: `Etapa del sistema`.

- Los valores deben verse como `A4: Aplicación de aguas verdes en campos de pastoreo`.

- No incluir rutas internas, nombres de scripts, archivos CSV ni columnas técnicas innecesarias.

- Encabezados en español, claros y académicos.

- Solo bordes horizontales, sin bordes verticales.



## Codificación



Todos los archivos de texto deben leerse y escribirse en UTF-8.



Evitar errores como:



- AnÃ¡lisis

- metodologÃ­a

- estiÃ©rcol

- nitrÃ³geno



El texto final debe mostrar correctamente tildes, eñes y símbolos científicos.



## Documentos principales



El documento maestro protegido y de referencia de formato es:



- `MASTER_escrito/TFG_ACV_Estiercol_MASTER.docx`



Los documentos generados deben guardarse en `outputs/documentos_tfg/`, nunca en `MASTER_escrito/`.



Los documentos principales generados son:



- `outputs/documentos_tfg/metodologia_desarrollada_tfg.docx`

- `outputs/documentos_tfg/resultados_desarrollados_tfg.docx`

- `outputs/documentos_tfg/conclusiones_desarrolladas_tfg.docx`



Cuando se actualicen, también actualizar:



- `outputs/documentos_tfg/reporte_validacion_documentos.md`

- `outputs/documentos_tfg/README_DOCUMENTOS_GENERADOS.md`



## Validación obligatoria



Después de regenerar documentos, verificar:



- No hay etiquetas técnicas internas visibles.

- No hay etapas con decimales.

- No hay errores de codificación.

- No hay rutas internas en prosa académica.

- No se modificaron valores numéricos sin instrucción explícita.

- No se modificó el documento maestro de propuesta.


## Pipeline y decisiones metodológicas

### Fuentes canónicas y ejecución coherente

- Existe un único pipeline activo: datos experimentales → ingestión normalizada → resumen intrajornada → integración interjornada vigente → promoción a parámetros activos → ACV → tablas → gráficos → metodología → resultados → conclusiones → validación cruzada.
- No utilizar tablas históricas de M1, incluidas las familias `CIA_samples_table*` y `volatile_solids_*`, como sustituto de las salidas multijornada vigentes.
- Distinguir las fronteras activas: `processed/muestreos_integracion_interjornada_provisional.csv` contiene la integración de parámetros; `processed/muestreos_transformacion_masa_interjornada.csv` contiene la transformación de masa; `processed/acv_parametros_escenario_etapa.csv` contiene los parámetros activos del ACV; y `processed/masa_total_escenario_etapa.csv` contiene las masas activas.
- No generar documentos contra una integración, parámetros, emisiones, tablas o gráficos pertenecientes a corridas diferentes. Cuando cambien datos experimentales, regenerar en orden todas las capas afectadas para evitar productos híbridos.
- `ACV_orquestador.py` parte de la integración vigente; no ejecuta la ingestión ni la integración estadística.

### Jerarquía estadística

- La jerarquía es: réplica analítica → muestra compuesta → promedio de jornada → integración entre jornadas.
- Las réplicas analíticas no son observaciones temporales independientes.
- Las jornadas reciben igual peso temporal. No ponderar M2 más que M1 por contener más muestras compuestas o réplicas.
- Para sólidos metodológicamente comparables, el estado provisional actual integra M1+M2. El estado final futuro requerirá M1+M2+M3 compatible.

### N líquido y precisión

- En aguas verdes y purines, M1 corresponde a especiación y se conserva solo para trazabilidad. Nunca reconstruir N total M1 sumando especies.
- El valor activo provisional de N total líquido procede de M2 mediante Kjeldahl. La integración final futura utilizará M2+M3 compatible y excluirá M1.
- Conservar para cálculo los decimales internos almacenados por el CIA. No interpretarlos como mayor precisión analítica formal y reservar el redondeo para la presentación; no redondear prematuramente.

### N/C y transformación fresco→precompostado

- No convertir automáticamente los resultados de N/C determinados por Dumas tras preparación a 80 °C durante 48 h usando la materia seca gravimétrica determinada a 105 °C. Son procedimientos separados y la base formal final del porcentaje no fue especificada por el reporte.
- Calcular la transformación fresco→precompostado primero por jornada usando materia seca y cenizas de ambos materiales; después integrar los factores de jornada con igual peso temporal.
- No promediar primero las cuatro variables entre jornadas ni crear una segunda ruta principal basada en un promedio independiente de pérdidas. La pérdida integrada se deriva del factor integrado.

### Decisiones aprobadas

- Antes de cambiar la unidad funcional, sistemas IPCC, factores, adaptación de eutrofización, balance, integración estadística, tratamiento de N líquido o transformación de masa, consultar `DECISIONES_METODOLOGICAS_TFG.md`.
- Ante una discrepancia: inspeccionar el código vigente, consultar la decisión metodológica, reportar al investigador y no reinterpretar ni cambiar cálculos automáticamente.
- M3 debe incorporarse mediante el mismo pipeline: ingestión, validación, integración final, validación, ACV, productos académicos y validación cruzada. No crear perfiles históricos, snapshots del modelo ni pipelines paralelos.

### Validaciones por capa

- `scripts/validate_sampling_ingestion.py` valida estructura, fuentes y decisiones metodológicas de la ingestión y del resumen intrajornada.
- `scripts/validate_sampling_integration.py` valida la integración estadística y confirma que su ejecución no modifica las salidas protegidas del ACV.
- `scripts/validate_provisional_m1_m2_outputs.py` se ejecuta después de regenerar la corrida completa y comprueba la coherencia cruzada entre integración, masas, emisiones, impactos, tablas, gráficos, metodología, resultados, conclusiones y MASTER.
- No atribuir a un validador comprobaciones que corresponden a otra capa.


## Reglas de formato para documentos Word generados

Estas reglas son obligatorias, según corresponda a su contenido, para `outputs/documentos_tfg/metodologia_desarrollada_tfg.docx`, `outputs/documentos_tfg/resultados_desarrollados_tfg.docx` y `outputs/documentos_tfg/conclusiones_desarrolladas_tfg.docx`:

1. Seguir el estilo visual de `MASTER_escrito/TFG_ACV_Estiercol_MASTER.docx`.
2. Usar el MASTER únicamente como referencia de formato. Nunca modificarlo, sobrescribirlo ni usarlo como archivo de salida.
3. Mantener numeración interna independiente en cada documento generado. No sincronizar secciones, tablas, figuras ni apéndices con el MASTER.
4. Usar color negro en títulos, subtítulos, captions y encabezados; no dejar texto azul.
5. Colocar los títulos de tablas encima de las tablas.
6. Colocar los títulos de figuras encima de las figuras.
7. Generar figuras sin título interno dentro de la imagen. El único título visible debe ser el caption de Word.
8. Asignar un solo título formal visible a cada tabla; no duplicar captions.
9. Asignar un solo título formal visible a cada figura; no duplicar captions.
10. Escribir todo el texto visible en español académico. Se permiten siglas aceptadas como IPCC, ACV, ICV, EICV, CIA, LASA y UCR.
11. Escribir las unidades anuales con tilde: `L/año`, `kg/año`, `kg eq/año`, `kg CO₂-eq/año` y `kg PO₄-eq/año`. No usar `L/ano`, `kg/ano` ni `kg eq/ano`.
12. Excluir de las tablas lenguaje computacional o interno como `snake_case`, `dry_lot`, `n_ex_pct`, `n_ex_fraction`, `masa_total_kg_eq`, `processed`, `outputs`, `scripts`, `.csv` y rutas internas.
13. Evitar columnas redundantes de etapa. Usar una sola columna llamada `Etapa del sistema`.
14. Usar siempre `B2: Aplicación de purines en campo de pastoreo`.
15. No asociar `purín` ni `purines` con flujos de A1, A2, A3 o A4.
16. No usar `Aguas verdes` en B1 o B2 cuando el flujo corresponda a purín.
17. Mencionar cada apéndice interno al menos una vez en la prosa principal del documento correspondiente. La mención debe describir su contenido o incluir su título.
18. Mantener las ecuaciones como texto LaTeX seleccionable y centrado, sin imágenes y sin delimitadores visibles `\[` `\]` ni `$$`.
19. Aplicar estas reglas desde los scripts generadores. No corregir manualmente los Word finales cuando la corrección pueda implementarse en el generador.
20. Confirmar estas reglas en `outputs/documentos_tfg/reporte_validacion_documentos.md` cada vez que se regeneren los documentos.

La especificación detallada y los ejemplos están en `docs/REGLAS_FORMATO_WORD.md`.

