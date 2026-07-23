# Reporte de corrección de etiquetas del eje X en gráficos

## Script modificado

- `scripts/generate_thesis_graphics.py`

Nota: en este repositorio el generador de figuras se llama `generate_thesis_graphics.py`; no existe `scripts/generate_thesis_figures.py`.

## Estrategia aplicada

- Se ajustó la función reutilizable `stage_axis_label()` para que las etiquetas visibles de gráficos usen código y nombre corto del proceso.
- Se eliminó la palabra `Etapa` solo de las etiquetas y títulos visibles en los gráficos.
- Las etiquetas conservan los códigos A1, A2, A3, A4, B1 y B2.
- Las etiquetas largas se mantienen con saltos de línea y ajuste automático de tamaño/rotación para evitar traslape.

Ejemplos de etiquetas gráficas aplicadas:

- `A1: Precomposteo`
- `A2: Lombricompostaje`
- `A3: Almacenamiento de aguas verdes`
- `A4: Aplicación de aguas verdes en campos de pastoreo`
- `B1: Almacenamiento de purines`
- `B2: Aplicación en campo`

## Figuras regeneradas

Se regeneraron todas las figuras finales en PNG y SVG:

- `fig_01_caracterizacion_humedad_materia_seca`
- `fig_02_caracterizacion_solidos_volatiles_cenizas`
- `fig_03_caracterizacion_nitrogeno_total`
- `fig_04_flujos_masa_equivalente_total`
- `fig_05_flujos_distribucion_componentes`
- `fig_06_emisiones_ch4`
- `fig_07_emisiones_n2o`
- `fig_08_emisiones_nh3`
- `fig_09_emisiones_no3`
- `fig_10_emisiones_co2`
- `fig_11_impactos_calentamiento_global_etapa`
- `fig_12_impactos_eutrofizacion_etapa`
- `fig_13_comparacion_total_calentamiento_global`
- `fig_14_comparacion_total_eutrofizacion`
- `fig_15_comparacion_diferencia_porcentual`

También se regeneró `outputs/graficos_tesis/README_GRAFICOS.md`.

## Validación

- La búsqueda en los SVG generados confirmó que la palabra `Etapa` no aparece en el texto visible de los gráficos.
- También se verificó la ausencia de `etapa` en minúscula dentro del texto SVG visible.
- Los códigos A1, A2, A3, A4, B1 y B2 se conservaron en los SVG generados.
- No se modificaron tablas fuente ni valores numéricos; las huellas SHA-256 de las tablas usadas para generar gráficos coinciden antes y después.
- Se usaron las tablas finales vigentes del repositorio.

## Tratamiento especial

- Las figuras con etiquetas largas de proceso usan saltos de línea.
- Las figuras agrupadas aplican rotación moderada solo si la validación automática detecta traslape.
- La eliminación de `Etapa` se aplicó únicamente a la presentación gráfica; no se modificaron tablas finales ni documento Word.

