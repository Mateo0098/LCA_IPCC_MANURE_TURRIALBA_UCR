# Reporte de validación de documentos

## Validación de documento maestro protegido

- Ruta vigente del documento maestro: `MASTER_escrito/TFG_ACV_Estiercol_MASTER.docx`.
- Hash SHA-256 registrado: `98ABDE3EC5A22FA052EFA595AAC26729EA070EACA670BDC41097C4BF2E5E327C`.
- Los scripts generadores ya no apuntan a `docs/referencia/`: Sí.
- El documento maestro protegido no fue modificado: Sí.
- Los documentos generados se guardan en `outputs/documentos_tfg/`: Sí.

## Verificaciones

- `metodologia_desarrollada_tfg.docx` fue regenerado: Sí.
- `resultados_desarrollados_tfg.docx` fue regenerado: Sí.
- Las figuras principales fueron insertadas o están disponibles para inserción: Sí.
- Se conservaron subíndices y superíndices en fórmulas químicas principales: Sí.
- Se agregaron ecuaciones en sintaxis LaTeX válida para humedad, materia seca, cenizas, sólidos volátiles, nitrógeno total y conservación de cenizas: Sí.
- Las ecuaciones fueron insertadas con formato matemático centrado: Sí.
- La sección de datos de entrada del ICV incluye estiércol fresco, precompostado, aguas verdes y purines: Sí.
- La sección de muestreo y análisis de laboratorio referencia explícitamente las tablas mencionadas: Sí.
- La redacción principal evita lenguaje de documentación técnica interna: Sí.
- Todas las figuras insertadas son mencionadas en la prosa: Sí.
- Todas las tablas insertadas son mencionadas en la prosa: Sí.
- Los encabezados de tablas están en negrita: Sí.
- Las tablas usan solo bordes horizontales: Sí.
- No se modificaron valores numéricos: Sí; la regeneración aplicó formato y redacción sin cambiar cálculos.
- No se usaron archivos `antes_correccion_nitrogeno`: Sí.
- No aparecen nombres antiguos de etapas: Sí.
- No aparecen rutas internas del repositorio en la prosa principal: Sí
- La metodología de nitrógeno en los documentos usa `n_ex_fraction = n_ex_pct / 100`: Sí.
- El documento original de propuesta no fue modificado: Sí.

## Validación de unidad funcional

- La unidad funcional aparece claramente como 1 kg de estiércol fresco: Sí.
- No aparecen formulaciones ambiguas sobre la unidad funcional: Sí.
- Las unidades anuales se mantienen como unidades de reporte y no como unidad funcional: Sí.
- Los resultados anuales se presentan como escala de inventario operacional, no como unidad funcional: Sí.
- No se modificaron valores numéricos: Sí.
- No se modificó el documento maestro de propuesta: Sí.
- Los Word fueron regenerados: Sí.

## Validación de ecuaciones en sintaxis LaTeX

- Método usado: texto LaTeX válido, seleccionable, en párrafos independientes y centrados.
- Ecuaciones insertadas: materia seca; humedad; cenizas; sólidos volátiles; conversión de nitrógeno a fracción másica; masa de nitrógeno en el flujo; masa de cenizas del estiércol fresco; masa seca equivalente del material precompostado; factor de masa seca remanente.
- Las nueve ecuaciones LaTeX requeridas aparecen como texto seleccionable: Sí.
- No se usaron imágenes de ecuaciones ni archivos `eq_*.png`: Sí.
- No se usaron delimitadores visibles `\[`, `\]` ni `$$`: Sí.
- Las ecuaciones están centradas y son seleccionables en Word: Sí.
- No se modificaron valores numéricos ni resultados: Sí.

## Validación de codificación de caracteres

- Scripts modificados: `scripts/generate_thesis_tables.py`, `scripts/generate_methodology_docx.py`, `scripts/generate_results_docx.py` y `scripts/academic_text_utils.py`.
- Documentos regenerados: `metodologia_desarrollada_tfg.docx` y `resultados_desarrollados_tfg.docx`.
- Estrategia aplicada: lectura explícita UTF-8 de CSV y reparación controlada de mojibake solo cuando se detectan marcadores de codificación dañada.
- No quedan marcadores de mojibake en los documentos y reportes generados (U+00C3, U+00C2, secuencias de comillas dañadas ni carácter de reemplazo): Sí.
- Las tildes, eñes y términos académicos en español aparecen correctamente: Sí.
- No se modificaron valores numéricos ni resultados: Sí.
- No se modificó el documento maestro de propuesta: Sí.

## Validación de nomenclatura de aguas verdes y purines

- B2 ya no usa la etiqueta `Aguas verdes` para el componente líquido: Sí.
- B2 usa `Agua de lavado incorporada al purín` para el componente líquido: Sí.
- A4 mantiene `Aguas verdes` o una etiqueta equivalente para el componente líquido: Sí.
- B1 y B2 no presentan flujos denominados `Aguas verdes`: Sí.
- Las filas del Escenario A no presentan flujos denominados `purín` o `purines`: Sí.
- La masa equivalente total no fue modificada: Sí.
- No se modificaron valores numéricos de A4 ni B2: Sí.
- La explicación metodológica de masa equivalente total fue incorporada: Sí.
- No se mencionan scripts, rutas, repositorio ni diagnóstico de Codex en la prosa principal: Sí.

## Validación de escritura académica

- No aparece texto visible en formato `snake_case`: Sí.
- No aparecen encabezados internos o erratas de encabezado: Sí.
- Las etapas no aparecen con decimales: Sí.
- Las tablas del Word usan encabezados académicos: Sí.

## Validación de limpieza de etiquetas técnicas

- No aparecen etiquetas técnicas internas en la prosa ni en tablas de los Word: Sí.
- No hay columnas con rutas internas, scripts, archivos CSV, `processed`, `outputs` o referencias hardcodeadas: Sí.
- Los apéndices internos fueron limpiados para lectura académica: Sí.
- No se modificaron valores numéricos ni resultados: Sí.
- No se modificó el documento maestro de propuesta: Sí.

## Validación de tablas sin redundancia de etapas

- Ninguna tabla contiene simultáneamente columnas redundantes como `Etapa` y `Nombre etapa`: Sí.
- Ninguna tabla contiene la palabra `etapa` en más de un encabezado: Sí.
- Se usa `Etapa del sistema` como columna única cuando corresponde: Sí.
- Los valores aparecen con código y nombre oficial de etapa: Sí.
- No aparecen números de etapa con decimales: Sí.
- No hay uso de `purín` en filas del Escenario A ni de `aguas verdes` en filas del Escenario B: Sí.
- Las tablas académicas reducidas para Word fueron incluidas en la validación: Sí.
- No se modificaron valores numéricos: Sí.
- No se modificaron resultados: Sí.
- No se modificó el documento maestro de propuesta: Sí.

## Validación de nomenclatura oficial de etapas

- B2 aparece como `B2: Aplicación de purines en campo de pastoreo`: Sí.
- Ya no aparece `B2: Aplicación en campo`: Sí.
- No se modificaron valores numéricos: Sí.
- No se modificaron cálculos, factores, ecuaciones ni resultados ambientales: Sí.
- El documento maestro protegido no fue modificado: Sí.
- El hash SHA-256 del documento maestro permanece en `98ABDE3EC5A22FA052EFA595AAC26729EA070EACA670BDC41097C4BF2E5E327C`: Sí.
- No se hizo commit automáticamente: Sí.

## Validación de formato basado en documento MASTER

- Los estilos de títulos principales fueron ajustados según el formato visual del MASTER: Sí.
- Los estilos de subtítulos fueron ajustados según el formato visual del MASTER: Sí.
- Los párrafos normales usan formato consistente con el MASTER: Sí.
- Los pies de tabla y figura usan formato consistente con el MASTER: Sí.
- Las tablas mantienen formato académico: Sí.
- Las ecuaciones siguen siendo texto LaTeX seleccionable: Sí.
- No se intentó sincronizar la numeración de secciones con el MASTER: Sí.
- No se intentó sincronizar la numeración de tablas con el MASTER: Sí.
- No se intentó sincronizar la numeración de figuras con el MASTER: Sí.
- Cada documento generado conserva su propia numeración interna: Sí.
- No se modificaron valores numéricos: Sí.
- No se modificaron cálculos ni resultados: Sí.
- El documento maestro no fue modificado: Sí.
- El hash SHA-256 del documento maestro permanece en `98ABDE3EC5A22FA052EFA595AAC26729EA070EACA670BDC41097C4BF2E5E327C`: Sí.

## Validación de color de subtítulos y unidades anuales

- No hay títulos ni subtítulos en color azul en `metodologia_desarrollada_tfg.docx`: Sí.
- No hay títulos ni subtítulos en color azul en `resultados_desarrollados_tfg.docx`: Sí.
- Los títulos, subtítulos y rótulos académicos usan color negro: Sí.
- No aparece `/ano` ni `ano` como unidad temporal en tablas, prosa, pies o apéndices internos: Sí.
- Las unidades anuales aparecen como `/año`: Sí.
- No se modificaron valores numéricos: Sí.
- No se modificaron cálculos ni resultados: Sí.
- El documento maestro protegido no fue modificado: Sí.
- El hash SHA-256 del documento maestro permanece en `98ABDE3EC5A22FA052EFA595AAC26729EA070EACA670BDC41097C4BF2E5E327C`: Sí.

## Validación de títulos de tablas no duplicados

- `metodologia_desarrollada_tfg.docx` no contiene títulos de tabla duplicados: Sí.
- `resultados_desarrollados_tfg.docx` no contiene títulos de tabla duplicados: Sí.
- No hay dos párrafos consecutivos idénticos usados como título de tabla: Sí.
- No hay dos párrafos consecutivos que empiecen con `Tabla`: Sí.
- No hay captions repetidos antes y después de una misma tabla: Sí.
- Cada tabla tiene un solo título formal visible: Sí.
- Las referencias en la prosa no duplican exactamente el caption: Sí.
- No se modificaron valores numéricos: Sí.
- No se modificaron cálculos ni resultados: Sí.
- El documento maestro protegido no fue modificado: Sí.
- El hash SHA-256 del documento maestro permanece en `98ABDE3EC5A22FA052EFA595AAC26729EA070EACA670BDC41097C4BF2E5E327C`: Sí.

## Validación de títulos de figuras sobre la imagen

- En `metodologia_desarrollada_tfg.docx` todos los títulos de figura están encima de la imagen: Sí.
- En `resultados_desarrollados_tfg.docx` todos los títulos de figura están encima de la imagen: Sí.
- No quedan títulos de figura debajo de imágenes: Sí.
- No hay figuras sin título: Sí.
- No hay títulos de figura duplicados: Sí.
- Los títulos de figura están en color negro: Sí.
- No se modificaron valores numéricos: Sí.
- No se modificaron cálculos ni resultados: Sí.
- No se modificó el contenido técnico de las figuras: Sí.
- El documento maestro protegido no fue modificado: Sí.
- El hash SHA-256 del documento maestro permanece en `98ABDE3EC5A22FA052EFA595AAC26729EA070EACA670BDC41097C4BF2E5E327C`: Sí.

## Validación de figuras sin títulos internos

- Las figuras PNG y SVG finales no contienen títulos internos: Sí.
- No se usan `plt.title()`, `ax.set_title()` ni `fig.suptitle()` para las figuras finales: Sí.
- Los títulos formales de figura se conservan únicamente como captions de Word: Sí.
- Los captions de Word aparecen encima de las figuras: Sí.
- No hay captions duplicados: Sí.
- Se conservaron etiquetas de ejes, leyendas y unidades: Sí.
- No se modificaron valores numéricos: Sí.
- No se modificaron cálculos ni resultados: Sí.
- El documento maestro protegido no fue modificado: Sí.
- El hash SHA-256 del documento maestro permanece en `98ABDE3EC5A22FA052EFA595AAC26729EA070EACA670BDC41097C4BF2E5E327C`: Sí.

## Validación de idioma español en documentos generados

- `metodologia_desarrollada_tfg.docx` no contiene texto visible en inglés: Sí.
- `resultados_desarrollados_tfg.docx` no contiene texto visible en inglés: Sí.
- Las tablas insertadas en los Word están completamente en español: Sí.
- Las figuras insertadas en los Word no contienen etiquetas en inglés: Sí.
- Los captions, notas y apéndices están en español: Sí.
- Se conservaron las siglas aceptadas IPCC, ACV, ICV, EICV, CIA, LASA y UCR: Sí.
- Se conservaron las fórmulas químicas CH₄, N₂O, NH₃, NO₃⁻ y CO₂: Sí.
- No se modificaron valores numéricos: Sí.
- No se modificaron cálculos ni resultados: Sí.
- El documento maestro protegido no fue modificado: Sí.
- El hash SHA-256 del documento maestro permanece en `98ABDE3EC5A22FA052EFA595AAC26729EA070EACA670BDC41097C4BF2E5E327C`: Sí.

## Validación de relación entre prosa y apéndices

- Todos los apéndices internos de `metodologia_desarrollada_tfg.docx` están mencionados en la prosa principal: Sí.
- Todos los apéndices internos de `resultados_desarrollados_tfg.docx` están mencionados en la prosa principal: Sí.
- Cada mención describe brevemente el contenido del apéndice o incluye su título: Sí.
- No existen apéndices huérfanos: Sí.
- No existen referencias a apéndices inexistentes: Sí.
- No se modificó la numeración de tablas, figuras o apéndices para empatarla con el MASTER: Sí.
- Cada documento conserva su propia numeración interna: Sí.
- No se modificaron valores numéricos: Sí.
- No se modificaron cálculos ni resultados: Sí.
- El documento maestro protegido no fue modificado: Sí.
- El hash SHA-256 del documento maestro permanece en `98ABDE3EC5A22FA052EFA595AAC26729EA070EACA670BDC41097C4BF2E5E327C`: Sí.

## Validación de referencias de factores

- Los factores asociados con ecuaciones IPCC ya no aparecen como pendientes de referencia: Sí.
- Los factores IPCC se identifican como IPCC, Ecuaciones IPCC o Metodología IPCC: Sí.
- Los factores medidos relacionados con residuo seco, estiércol precompostado y emisiones de gases de efecto invernadero se referencian como Jjagwe et al. (2019): Sí.
- No se inventaron referencias para factores cuyo origen no pudo confirmarse: Sí.
- Los factores todavía pendientes se reportan explícitamente como `Requiere revisión bibliográfica`: Sí.
- No aparecen rutas internas ni `scripts/ecuaciones_acv.py` en los documentos Word finales: Sí.
- La trazabilidad a `scripts/ecuaciones_acv.py` aparece únicamente en el reporte técnico de referencias: Sí.
- No se modificaron valores numéricos: Sí.
- No se modificaron cálculos ni resultados: Sí.
- El documento maestro protegido no fue modificado: Sí.
- El hash SHA-256 del documento maestro permanece en `98ABDE3EC5A22FA052EFA595AAC26729EA070EACA670BDC41097C4BF2E5E327C`: Sí.

## Archivos validados

- `outputs/documentos_tfg/metodologia_desarrollada_tfg.docx`
- `outputs/documentos_tfg/resultados_desarrollados_tfg.docx`
- `outputs/documentos_tfg/README_DOCUMENTOS_GENERADOS.md`
- `outputs/documentos_tfg/reporte_formato_master.md`
- `outputs/documentos_tfg/reporte_relacion_apendices.md`
- `outputs/documentos_tfg/reporte_referencias_factores.md`
