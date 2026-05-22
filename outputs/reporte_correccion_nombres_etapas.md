# Reporte de correcciÃ³n de nombres de etapas

## Scripts modificados

- `scripts/generate_thesis_tables.py`
- `scripts/generate_thesis_graphics.py`
- `scripts/generate_results_docx.py`

Nota: no existe `scripts/generate_thesis_figures.py`; el generador de figuras del proyecto es `scripts/generate_thesis_graphics.py`.

## Tablas regeneradas

- `outputs/tablas_tesis/tabla_01_etapas_escenarios.csv`
- `outputs/tablas_tesis/tabla_02_caracterizacion_muestras.csv`
- `outputs/tablas_tesis/tabla_03_flujos_icv.csv`
- `outputs/tablas_tesis/tabla_04_parametros_modelo_acv.csv`
- `outputs/tablas_tesis/tabla_05_factores_emision_y_caracterizacion.csv`
- `outputs/tablas_tesis/tabla_06_emisiones_por_etapa.csv`
- `outputs/tablas_tesis/tabla_07_impactos_por_etapa.csv`
- `outputs/tablas_tesis/tabla_08_impactos_totales_por_escenario.csv`
- `outputs/tablas_tesis/tabla_09_comparacion_escenarios.csv`
- `outputs/tablas_tesis/diccionario_variables.csv`
- `outputs/tablas_tesis/resumen_resultados_para_redaccion.md`
- Tablas reducidas en `outputs/tablas_tesis/tablas_word/`

## Figuras regeneradas

Se regeneraron las figuras finales en PNG y SVG mediante `scripts/generate_thesis_graphics.py`, incluidas:

- `fig_04_flujos_masa_equivalente_total`
- `fig_06_emisiones_ch4`
- `fig_07_emisiones_n2o`
- `fig_08_emisiones_nh3`
- `fig_09_emisiones_no3`
- `fig_10_emisiones_co2`
- `fig_11_impactos_calentamiento_global_etapa`
- `fig_12_impactos_eutrofizacion_etapa`

TambiÃ©n se regenerÃ³ `outputs/graficos_tesis/README_GRAFICOS.md`.

## Documento Word

Se regenerÃ³ `outputs/resultados_tfg.docx` con la nomenclatura oficial de etapas en texto y tablas reducidas.

## ValidaciÃ³n numÃ©rica

No se modificaron valores numÃ©ricos. La comparaciÃ³n de huellas SHA-256 de columnas numÃ©ricas antes y despuÃ©s coincidiÃ³ para:

- `tabla_01_etapas_escenarios.csv`
- `tabla_03_flujos_icv.csv`
- `tabla_04_parametros_modelo_acv.csv`
- `tabla_06_emisiones_por_etapa.csv`
- `tabla_07_impactos_por_etapa.csv`
- `tabla_08_impactos_totales_por_escenario.csv`
- `tabla_09_comparacion_escenarios.csv`

## Archivos no usados

Se usaron las tablas finales vigentes del repositorio. Existen archivos archivados con ese sufijo dentro de una carpeta histÃ³rica, pero no son insumos de los scripts ejecutados.

## BÃºsqueda final de nombres antiguos

Se buscaron los tÃ©rminos:

- `Manejo inicial`
- `Manejo posterior`
- `fracciÃ³n sÃ³lida`
- `AplicaciÃ³n o manejo`
- `Manejo de estiÃ©rcol fresco sin precompostaje`
- `Manejo o aplicaciÃ³n de purines`

Resultado: no se encontraron coincidencias en:

- `outputs/tablas_tesis/`
- `outputs/graficos_tesis/README_GRAFICOS.md`
- `outputs/tablas_tesis/resumen_resultados_para_redaccion.md`
- `outputs/resultados_tfg.docx`

## Nomenclatura oficial aplicada

- A1: `Etapa 1: Precomposteo`
- A2: `Etapa 2: Lombricompostaje`
- A3: `Etapa 3: Almacenamiento de aguas verdes`
- A4: `Etapa 4: AplicaciÃ³n de aguas verdes en campos de pastoreo`
- B1: `Etapa 1: Almacenamiento de purines`
- B2: `Etapa 2: AplicaciÃ³n en campo`

