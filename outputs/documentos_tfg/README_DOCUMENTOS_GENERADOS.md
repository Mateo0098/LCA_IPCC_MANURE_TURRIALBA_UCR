# Documentos generados para el TFG

## 1. Documentos generados

- `metodologia_desarrollada_tfg.docx`
- `resultados_desarrollados_tfg.docx`
- `README_DOCUMENTOS_GENERADOS.md`
- `reporte_validacion_documentos.md`
- `reporte_formato_master.md`
- `reporte_relacion_apendices.md`
- `reporte_referencias_factores.md`
- `reporte_correccion_factor_estequiometrico_NO3.md`

## 2. Scripts usados

- `scripts/generate_methodology_docx.py`
- `scripts/generate_results_docx.py`

## 3. Tablas utilizadas

- `tabla_02_caracterizacion_muestras.csv`
- `tabla_03_flujos_icv.csv`
- `tabla_04_parametros_modelo_acv.csv`
- `tabla_05_factores_emision_y_caracterizacion.csv`
- `tabla_06_emisiones_por_etapa.csv`
- `tabla_07_impactos_por_etapa.csv`
- `tabla_08_impactos_totales_por_escenario.csv`
- `tabla_09_comparacion_escenarios.csv`

## 4. Figuras utilizadas

Figuras principales:

- `fig_01_caracterizacion_humedad_materia_seca.png`
- `fig_02_caracterizacion_solidos_volatiles_cenizas.png`
- `fig_04_flujos_masa_equivalente_total.png`
- `fig_06_emisiones_ch4.png`
- `fig_11_impactos_calentamiento_global_etapa.png`
- `fig_12_impactos_eutrofizacion_etapa.png`
- `fig_15_comparacion_diferencia_porcentual.png`

Figuras complementarias en apéndices:

- `fig_03_caracterizacion_nitrogeno_total.png`
- `fig_05_flujos_distribucion_componentes.png`
- `fig_07_emisiones_n2o.png`
- `fig_08_emisiones_nh3.png`
- `fig_09_emisiones_no3.png`
- `fig_10_emisiones_co2.png`
- `fig_13_comparacion_total_calentamiento_global.png`
- `fig_14_comparacion_total_eutrofizacion.png`

## 5. Confirmaciones

- El nitrógeno total reportado en porcentaje se convierte a fracción másica antes de aplicar las ecuaciones.
- La unidad funcional del estudio es 1 kg de estiércol fresco manejado.
- El flujo anual de referencia es común para los escenarios A y B.
- La metodología propaga N total y TAN entre las etapas físicamente conectadas.
- NH₃, NOx y NO₃⁻ proceden de especies explícitas o rutas hídricas justificadas; no se usa reparto 50/50.
- Se usó la nomenclatura oficial de etapas: A1, A2, A3, A4, B1 y B2.
- El documento maestro protegido se encuentra en `MASTER_escrito/TFG_ACV_Estiercol_MASTER.docx` y se usa únicamente como referencia de formato.
- Los documentos generados se guardan en `outputs/documentos_tfg/`; ningún generador escribe dentro de `MASTER_escrito/`.
- No se modificó el documento maestro de referencia. Hash antes: `98ABDE3EC5A22FA052EFA595AAC26729EA070EACA670BDC41097C4BF2E5E327C`. Hash después: `98ABDE3EC5A22FA052EFA595AAC26729EA070EACA670BDC41097C4BF2E5E327C`.

## 6. Mejoras de formato académico aplicadas

- Subíndices y superíndices en fórmulas químicas y unidades principales.
- Ecuaciones LaTeX explicativas para humedad, materia seca, cenizas, sólidos volátiles, ledger de nitrógeno, conservación de cenizas y especies reactivas.
- Referencias explícitas a tablas y figuras en la prosa.
- Tablas con encabezados en negrita.
- Tablas con bordes horizontales únicamente.
- Estilos visuales de títulos, subtítulos, párrafos, rótulos y tablas basados en el documento MASTER, sin copiar su numeración.
- Títulos, subtítulos y rótulos académicos en color negro.
- Unidades anuales escritas con `año`, por ejemplo `kg/año` y `kg CO₂-eq/año`.
- Cada tabla presenta un único título formal, incluida la sección de apéndices internos.
- Los títulos formales de las figuras se ubican encima de cada imagen.
- Las imágenes de las figuras no contienen títulos internos redundantes.

## 7. Tablas y figuras incluidas en el cuerpo

Metodología:

- Tabla de unidad funcional, supuestos y advertencias metodológicas.
- Tabla de etapas oficiales por escenario.
- Tabla de caracterización resumida de muestras.
- Tabla de factores de caracterización resumidos.
- Figura de masa equivalente total como apoyo metodológico.

Resultados:

- Tabla de caracterización resumida.
- Tabla de masa equivalente total por etapa.
- Tabla de parámetros principales por etapa.
- Tabla de emisiones anuales por escenario y sustancia.
- Tabla de impactos ambientales por etapa.
- Tabla de impactos ambientales totales por escenario.
- Tabla de comparación de impactos entre escenarios.
- Figuras principales 1 a 7.

## 7. Tablas y figuras enviadas a apéndices

Metodología:

- Parámetros completos del modelo ACV.
- Factores técnicos completos.
- Diccionario de variables.
- Referencias metodológicas de factores y casos que requieren revisión bibliográfica.

Resultados:

- Tablas completas 02 a 09.
- Figuras complementarias R1 a R8.
- Correspondencia entre tablas, figuras y archivos fuente.

## 8. Advertencias para revisión humana

- Los resultados anuales se presentan como escala de inventario operacional y no sustituyen la unidad funcional del ACV.
- Las conversiones basadas en relaciones de masa se documentan como cálculos estequiométricos y no requieren una cita bibliográfica externa.
- Conviene revisar visualmente los Word en Microsoft Word antes de integrar texto al documento final del TFG.
