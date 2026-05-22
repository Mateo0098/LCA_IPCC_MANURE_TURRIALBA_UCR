# Reporte de limpieza de menciones históricas sobre nitrógeno

## 1. Auditoría y clasificación

Se revisaron `outputs/`, `outputs/tablas_tesis/`, `outputs/documentos_tfg/`, `README_METODOLOGIA.md`, `outputs/tablas_tesis/resumen_resultados_para_redaccion.md`, `outputs/graficos_tesis/README_GRAFICOS.md` y `scripts/`.

### A. Archivos obsoletos eliminados

- `outputs/tablas_tesis/tabla_auditoria_nitrogeno.csv`
- `outputs/tablas_tesis/tabla_comparacion_correccion_nitrogeno.csv`
- `outputs/tablas_tesis/outputstablas_tesisarchivadas_antes_correccion_nitrogeno/ACV_resumen_emisiones_antes_correccion_nitrogeno.csv`
- `outputs/tablas_tesis/outputstablas_tesisarchivadas_antes_correccion_nitrogeno/acv_impacto_por_etapa_escenario_antes_correccion_nitrogeno.csv`
- `outputs/tablas_tesis/outputstablas_tesisarchivadas_antes_correccion_nitrogeno/acv_impacto_total_por_escenario_antes_correccion_nitrogeno.csv`
- `outputs/tablas_tesis/outputstablas_tesisarchivadas_antes_correccion_nitrogeno/`
- `scripts/generate_nitrogen_correction_audit.py`

### B. Archivos útiles modificados para limpiar redacción

- `README_METODOLOGIA.md`
- `outputs/tablas_tesis/resumen_resultados_para_redaccion.md`
- `outputs/graficos_tesis/README_GRAFICOS.md`
- `outputs/documentos_tfg/README_DOCUMENTOS_GENERADOS.md`
- `outputs/documentos_tfg/reporte_validacion_documentos.md`
- `outputs/reporte_regeneracion_word_resultados.md`
- `outputs/reporte_correccion_graficos_eje_x.md`
- `outputs/reporte_correccion_nombres_etapas.md`
- `outputs/tablas_tesis/tabla_04_parametros_modelo_acv.csv`
- `outputs/tablas_tesis/tabla_06_emisiones_por_etapa.csv`
- `outputs/tablas_tesis/tabla_09_comparacion_escenarios.csv`
- `scripts/generate_methodology_docx.py`
- `scripts/generate_results_docx.py`
- `scripts/generate_thesis_tables.py`
- `scripts/generate_thesis_graphics.py`

### C. Archivos útiles conservados

- `outputs/tablas_tesis/tabla_02_caracterizacion_muestras.csv`
- `outputs/tablas_tesis/tabla_03_flujos_icv.csv`
- `outputs/tablas_tesis/tabla_04_parametros_modelo_acv.csv`
- `outputs/tablas_tesis/tabla_05_factores_emision_y_caracterizacion.csv`
- `outputs/tablas_tesis/tabla_06_emisiones_por_etapa.csv`
- `outputs/tablas_tesis/tabla_07_impactos_por_etapa.csv`
- `outputs/tablas_tesis/tabla_08_impactos_totales_por_escenario.csv`
- `outputs/tablas_tesis/tabla_09_comparacion_escenarios.csv`
- Figuras finales en `outputs/graficos_tesis/`
- `scripts/generate_thesis_tables.py`
- `scripts/generate_thesis_graphics.py`
- `scripts/generate_methodology_docx.py`
- `scripts/generate_results_docx.py`
- Documento maestro de referencia en `docs/referencia/TFG_ACV_Estiercol_MASTER.docx`

### D. Menciones metodológicas conservadas

Se conservó únicamente la formulación metodológica final:

- `n_ex_pct` es el nitrógeno total reportado en porcentaje.
- `n_ex_fraction = n_ex_pct / 100`.
- `n_ex_fraction` es la fracción másica usada en ecuaciones de nitrógeno.

## 2. Regeneración realizada

- Se regeneraron las tablas finales con `scripts/generate_thesis_tables.py`.
- Se regeneró `outputs/documentos_tfg/metodologia_desarrollada_tfg.docx`.
- Se regeneró `outputs/documentos_tfg/resultados_desarrollados_tfg.docx`.
- Se regeneraron `outputs/documentos_tfg/README_DOCUMENTOS_GENERADOS.md` y `outputs/documentos_tfg/reporte_validacion_documentos.md`.

## 3. Confirmación de tablas finales

Las tablas finales requeridas siguen existiendo:

- `tabla_02_caracterizacion_muestras.csv`: sí
- `tabla_03_flujos_icv.csv`: sí
- `tabla_04_parametros_modelo_acv.csv`: sí
- `tabla_05_factores_emision_y_caracterizacion.csv`: sí
- `tabla_06_emisiones_por_etapa.csv`: sí
- `tabla_07_impactos_por_etapa.csv`: sí
- `tabla_08_impactos_totales_por_escenario.csv`: sí
- `tabla_09_comparacion_escenarios.csv`: sí

## 4. Validación final

Se verificó que no aparecen menciones históricas sobre el proceso previo en:

- `outputs/documentos_tfg/metodologia_desarrollada_tfg.docx`
- `outputs/documentos_tfg/resultados_desarrollados_tfg.docx`
- `README_METODOLOGIA.md`
- `outputs/documentos_tfg/README_DOCUMENTOS_GENERADOS.md`
- `outputs/documentos_tfg/reporte_validacion_documentos.md`

La búsqueda final de los términos solicitados no encontró coincidencias en los archivos objetivo ni en `scripts/`, `outputs/tablas_tesis/`, `outputs/documentos_tfg/` y `outputs/graficos_tesis/README_GRAFICOS.md`, con excepción de este reporte, donde aparecen únicamente para documentar la limpieza realizada.

## 5. Observaciones

- No se cambiaron cálculos, ecuaciones, factores ni resultados numéricos.
- No se cambió la nomenclatura oficial de etapas.
- No se modificó el documento maestro de propuesta.
- No se hizo commit automáticamente.
