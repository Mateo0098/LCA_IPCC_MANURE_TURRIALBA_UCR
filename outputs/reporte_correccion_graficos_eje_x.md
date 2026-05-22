# Reporte de correcciÃ³n de etiquetas del eje X en grÃ¡ficos

## Script modificado

- `scripts/generate_thesis_graphics.py`

Nota: en este repositorio el generador de figuras se llama `generate_thesis_graphics.py`; no existe `scripts/generate_thesis_figures.py`.

## Estrategia aplicada

- Se ajustÃ³ la funciÃ³n reutilizable `stage_axis_label()` para que las etiquetas visibles de grÃ¡ficos usen cÃ³digo y nombre corto del proceso.
- Se eliminÃ³ la palabra `Etapa` solo de las etiquetas y tÃ­tulos visibles en los grÃ¡ficos.
- Las etiquetas conservan los cÃ³digos A1, A2, A3, A4, B1 y B2.
- Las etiquetas largas se mantienen con saltos de lÃ­nea y ajuste automÃ¡tico de tamaÃ±o/rotaciÃ³n para evitar traslape.

Ejemplos de etiquetas grÃ¡ficas aplicadas:

- `A1: Precomposteo`
- `A2: Lombricompostaje`
- `A3: Almacenamiento de aguas verdes`
- `A4: AplicaciÃ³n de aguas verdes en campos de pastoreo`
- `B1: Almacenamiento de purines`
- `B2: AplicaciÃ³n en campo`

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

TambiÃ©n se regenerÃ³ `outputs/graficos_tesis/README_GRAFICOS.md`.

## ValidaciÃ³n

- La bÃºsqueda en los SVG generados confirmÃ³ que la palabra `Etapa` no aparece en el texto visible de los grÃ¡ficos.
- TambiÃ©n se verificÃ³ la ausencia de `etapa` en minÃºscula dentro del texto SVG visible.
- Los cÃ³digos A1, A2, A3, A4, B1 y B2 se conservaron en los SVG generados.
- No se modificaron tablas fuente ni valores numÃ©ricos; las huellas SHA-256 de las tablas usadas para generar grÃ¡ficos coinciden antes y despuÃ©s.
- Se usaron las tablas finales vigentes del repositorio.

## Tratamiento especial

- Las figuras con etiquetas largas de proceso usan saltos de lÃ­nea.
- Las figuras agrupadas aplican rotaciÃ³n moderada solo si la validaciÃ³n automÃ¡tica detecta traslape.
- La eliminaciÃ³n de `Etapa` se aplicÃ³ Ãºnicamente a la presentaciÃ³n grÃ¡fica; no se modificaron tablas finales ni documento Word.

