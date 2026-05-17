# Resumen de resultados para redaccion

Este documento usa unicamente las tablas finales actuales de `outputs/tablas_tesis/`:

- `tabla_02_caracterizacion_muestras.csv`
- `tabla_03_flujos_icv.csv`
- `tabla_04_parametros_modelo_acv.csv`
- `tabla_05_factores_emision_y_caracterizacion.csv`
- `tabla_06_emisiones_por_etapa.csv`
- `tabla_07_impactos_por_etapa.csv`
- `tabla_08_impactos_totales_por_escenario.csv`
- `tabla_09_comparacion_escenarios.csv`

No se usaron archivos con sufijo `antes_correccion_nitrogeno`.

## 6.1 Caracterizacion de las muestras analizadas

**Tabla fuente:** `tabla_02_caracterizacion_muestras.csv`.

**Que muestra la tabla:** resume la caracterizacion de las muestras de estiercol fresco y estiercol precompostado. Incluye humedad, materia seca, cenizas, solidos volatiles y nitrogeno total, con unidades explicitas.

**Valores principales:**

| Tipo de muestra | Humedad (% masa humeda) | Materia seca (% masa humeda) | Cenizas (% base seca) | Solidos volatiles (% base seca) | N total (% N total) | N total (mg N/kg) |
|---|---:|---:|---:|---:|---:|---:|
| Fresh manure | 85.769829 | 14.230171 | 14.123008 | 85.876992 | 0.371666667 | 3716.666667 |
| Precomposted manure | 77.593045 | 22.406955 | 29.041353 | 70.958647 | 2.425 | 24250.0 |

**Valor maximo y minimo:**

- Humedad maxima: estiercol fresco, 85.769829 %. Minima: precompostado, 77.593045 %.
- Materia seca maxima: precompostado, 22.406955 %. Minima: estiercol fresco, 14.230171 %.
- Solidos volatiles maximos: estiercol fresco, 85.876992 %. Minimos: precompostado, 70.958647 %.
- Nitrogeno total maximo: precompostado, 2.425 %. Minimo: estiercol fresco, 0.371666667 %.

**Diferencias entre escenario A y escenario B:** esta seccion no compara escenarios directamente; compara tipos de muestra que luego alimentan etapas de los escenarios. El estiercol fresco alimenta A1, A3 y B1; el precompostado alimenta A2.

**Etapa que mas contribuye:** no aplica directamente; esta tabla caracteriza muestras. Para trazabilidad, el precompostado es relevante para A2 y el estiercol fresco para A1, A3 y B1.

**Resultado que requiere discusion cuidadosa:** el precompostado muestra mayor materia seca y mayor nitrogeno total que el estiercol fresco, pero menores solidos volatiles. Esto debe discutirse como efecto del tratamiento/concentracion de la fraccion solida, no como emision por si mismo.

**Figura o grafico recomendado:** grafico de barras agrupadas por tipo de muestra para humedad, materia seca, solidos volatiles y nitrogeno total.

## 6.2 Flujos del inventario de ciclo de vida

**Tabla fuente:** `tabla_03_flujos_icv.csv`.

**Que muestra la tabla:** presenta los flujos por escenario y etapa: estiercol/fraccion solida, aguas verdes, masa equivalente total y factor restante de fresco a precompostado.

**Valores principales de masa equivalente total:**

| Escenario | Etapa | Nombre de etapa | Masa equivalente total (kg eq/ano) |
|---|---:|---|---:|
| A | 1 | Manejo inicial de estiercol fresco | 4767.45683 |
| A | 2 | Precompostaje de fraccion solida | 1472.39567 |
| A | 3 | Manejo posterior de fraccion solida | 358.840837 |
| A | 4 | Aplicacion o manejo de aguas verdes en suelo | 71789.81012 |
| B | 1 | Manejo de estiercol fresco sin precompostaje | 5126.297667 |
| B | 2 | Manejo o aplicacion de purines | 76557.26695 |

**Valor maximo y minimo:**

- Maximo: B2, 76557.26695 kg eq/ano.
- Minimo: A3, 358.840837 kg eq/ano.

**Diferencias entre escenario A y escenario B:**

- Suma de masas equivalentes por etapas A: 78388.503457 kg eq/ano.
- Suma de masas equivalentes por etapas B: 81683.564617 kg eq/ano.
- Diferencia B - A: 3295.06116 kg eq/ano, aproximadamente 4.2 % mayor en B.
- La comparacion debe tratarse con cuidado porque A esta dividido en cuatro etapas y B en dos etapas.

**Etapa que mas contribuye:** B2 es la etapa con mayor masa equivalente total; en el escenario A, A4 domina la masa equivalente.

**Resultado que requiere discusion cuidadosa:** la masa equivalente combina boniga y agua bajo el supuesto `1 L agua = 1 kg eq`. Esto es util para escalamiento, pero debe declararse como supuesto de inventario.

**Figura o grafico recomendado:** barras apiladas por etapa con `Estiercol/fraccion solida` y `Aguas verdes`; alternativamente, barras simples de masa equivalente total por etapa.

## 6.3 Parametros utilizados en el modelo ACV

**Tablas fuente:** `tabla_04_parametros_modelo_acv.csv` y `tabla_05_factores_emision_y_caracterizacion.csv`.

**Que muestran las tablas:** integran parametros de laboratorio, masa equivalente, modelo de calculo, sistema IPCC, factores de manejo, factores medidos y factores de caracterizacion.

**Valores principales:**

- `n_ex_pct` se conserva como nitrogeno total reportado en porcentaje.
- `n_ex_fraction` se usa como fraccion masica en ecuaciones de nitrogeno.
- A1 usa sistema `dry_lot`, modelo `ipcc`.
- A2 usa modelo `medido`; su sistema IPCC queda documentado como `composting_invessel` si se quisiera evaluar la rama IPCC.
- A3, A4, B1 y B2 usan `uncovered_anaerobic_lagoon` en la tabla actual de asignacion.
- Factores de caracterizacion usados: CH4 = 21 kg CO2-eq/kg, N2O = 310 kg CO2-eq/kg, CO2 = 1 kg CO2-eq/kg, NH3 = 0.35 kg PO4-eq/kg y NO3 = 0.095 kg PO4-eq/kg.

**Valor maximo y minimo:**

- `n_ex_fraction` maxima: A2, 0.02425 kg N/kg muestra.
- `n_ex_fraction` minima: A4, 0.0000718577 kg N/kg muestra.
- MCF maximo: 80 %, usado en A3, A4, B1 y B2.
- MCF minimo: 0.5 %, documentado para A2 en el sistema `composting_invessel`.
- EF3 maximo: 0.02 kg N2O-N/kg N en A1.
- EF3 minimo: 0 en etapas con `uncovered_anaerobic_lagoon` segun la tabla actual.

**Diferencias entre escenario A y escenario B:**

- El escenario A combina etapas con estiercol fresco, precompostaje, fraccion solida posterior y aguas verdes.
- El escenario B concentra el manejo en estiercol fresco y purines.
- A2 se diferencia metodologicamente porque usa factores medidos, no la rama IPCC.

**Etapa que mas contribuye:** como parametros, no hay contribucion ambiental directa. Sin embargo, B1 combina alta masa de estiercol fresco con MCF alto, lo cual explica su peso posterior en CH4 e impacto climatico.

**Resultado que requiere discusion cuidadosa:** los factores IPCC y factores de caracterizacion tienen fuente bibliografica pendiente en la tabla de factores. Deben citarse antes de cerrar la redaccion formal.

**Figura o grafico recomendado:** tabla metodologica, no figura principal. Si se grafica, usar un mapa de calor de parametros por etapa: `n_ex_fraction`, `MCF`, `EF3`, masa total.

## 6.4 Emisiones estimadas por etapa y escenario

**Tabla fuente:** `tabla_06_emisiones_por_etapa.csv`.

**Que muestra la tabla:** emisiones por escenario, etapa, sustancia, ecuacion utilizada, fuente del factor y masa total usada para escalamiento.

**Valores principales por escenario y sustancia:**

| Escenario | CH4 (kg/ano) | N2O (kg/ano) | NH3 (kg/ano) | NO3 (kg/ano) | CO2 (kg/ano) |
|---|---:|---:|---:|---:|---:|
| A | 9.553739792 | 0.788705241 | 5.225984427 | 19.059472615 | 33.651741590 |
| B | 80.587335181 | 0.305995839 | 6.353966548 | 23.173289762 | 0 |

**Valor maximo y minimo:**

- CH4 maximo: B1, 80.587335181 kg CH4/ano.
- N2O maximo por etapa: A1, suma de rutas N2O = 0.684550103 kg N2O/ano.
- NH3 maximo por etapa: B1, 3.992025281 kg NH3/ano.
- NO3 maximo por etapa: B1, 14.559151026 kg NO3/ano.
- CO2 solo aparece en A2, 33.651741590 kg CO2/ano, por uso de factor medido.
- Valores minimos: varias rutas son 0 o no aplican segun etapa y modelo.

**Diferencias entre escenario A y escenario B:**

- B emite mucho mas CH4 que A: 80.587335181 frente a 9.553739792 kg/ano.
- A emite mas N2O total que B: 0.788705241 frente a 0.305995839 kg/ano.
- B emite mas NH3 y NO3 totales que A.
- A incluye CO2 medido por A2; B no reporta CO2 en las tablas actuales.

**Etapa que mas contribuye:**

- CH4: B1.
- N2O: A1.
- NH3: B1.
- NO3: B1.
- CO2: A2.

**Resultado que requiere discusion cuidadosa:** B1 domina CH4 debido al sistema y al MCF asignado. La interpretacion depende fuertemente de justificar la asignacion del sistema IPCC para B1.

**Figura o grafico recomendado:** barras por sustancia y etapa, separadas por escenario. Usar paneles para CH4, N2O, NH3, NO3 y CO2.

## 6.5 Impactos ambientales por etapa

**Tabla fuente:** `tabla_07_impactos_por_etapa.csv`.

**Que muestra la tabla:** contribuciones por sustancia al calentamiento global y eutrofizacion por etapa y escenario. Incluye emision, factor de caracterizacion y resultado equivalente.

**Valores principales por etapa:**

| Escenario | Etapa | Calentamiento global (kg CO2-eq/ano) | Eutrofizacion (kg PO4-eq/ano) |
|---|---:|---:|---:|
| A | 1 | 241.720606643 | 2.475676010 |
| A | 2 | 86.310852307 | 0 |
| A | 3 | 121.646905095 | 0.194622974 |
| A | 4 | 29.100537813 | 0.969445464 |
| B | 1 | 1737.812928423 | 2.780328196 |
| B | 2 | 49.379820538 | 1.645022623 |

**Valor maximo y minimo:**

- Calentamiento global maximo: B1, 1737.812928423 kg CO2-eq/ano.
- Calentamiento global minimo: A4, 29.100537813 kg CO2-eq/ano.
- Eutrofizacion maxima: B1, 2.780328196 kg PO4-eq/ano.
- Eutrofizacion minima: A2, 0 kg PO4-eq/ano.

**Diferencias entre escenario A y escenario B:**

- En calentamiento global, B1 por si solo supera ampliamente a cualquier etapa del escenario A.
- En eutrofizacion, B1 tambien es la mayor etapa individual, pero A1 queda cerca y es la principal etapa de A.

**Etapa que mas contribuye:** B1 es la etapa dominante en ambas categorias de impacto.

**Resultado que requiere discusion cuidadosa:** en A2, la eutrofizacion es 0 porque las emisiones NH3 y NO3 se reportan como 0 en la tabla final. Esto no debe interpretarse como ausencia fisica absoluta sin revisar el alcance del factor medido usado para A2.

**Figura o grafico recomendado:** dos graficos de barras por etapa: uno para kg CO2-eq/ano y otro para kg PO4-eq/ano.

## 6.6 Impactos totales por escenario

**Tabla fuente:** `tabla_08_impactos_totales_por_escenario.csv`.

**Que muestra la tabla:** suma de impactos por categoria ambiental para cada escenario.

**Valores principales:**

| Escenario | Calentamiento global (kg CO2-eq/ano) | Eutrofizacion (kg PO4-eq/ano) |
|---|---:|---:|
| A | 478.778901857 | 3.639744448 |
| B | 1787.192748961 | 4.425350819 |

**Valor maximo y minimo:**

- Calentamiento global maximo: B, 1787.192748961 kg CO2-eq/ano.
- Calentamiento global minimo: A, 478.778901857 kg CO2-eq/ano.
- Eutrofizacion maxima: B, 4.425350819 kg PO4-eq/ano.
- Eutrofizacion minima: A, 3.639744448 kg PO4-eq/ano.

**Diferencias entre escenario A y escenario B:**

- B es mayor que A en ambas categorias.
- La diferencia absoluta es mucho mayor en calentamiento global que en eutrofizacion.

**Etapa que mas contribuye:** B1 explica la mayor parte del impacto total del escenario B; A1 explica la mayor parte del calentamiento global y eutrofizacion del escenario A.

**Resultado que requiere discusion cuidadosa:** el resultado total de B esta dominado por CH4 de B1, por lo que la comparacion depende especialmente de la validez del sistema IPCC asignado y del MCF usado para esa etapa.

**Figura o grafico recomendado:** barras comparativas A vs B para cada categoria de impacto.

## 6.7 Comparacion entre escenarios

**Tabla fuente:** `tabla_09_comparacion_escenarios.csv`.

**Que muestra la tabla:** comparacion directa entre escenario A y B, diferencia absoluta, diferencia porcentual y escenario con mayor impacto.

**Valores principales:**

| Categoria | Escenario A | Escenario B | Diferencia B - A | Diferencia porcentual B vs A | Mayor impacto |
|---|---:|---:|---:|---:|---|
| Calentamiento global | 478.778901857 | 1787.192748961 | 1308.413847103 | 273.281433669 % | B |
| Eutrofizacion | 3.639744448 | 4.425350819 | 0.785606371 | 21.584107963 % | B |

**Valor maximo y minimo:**

- Mayor diferencia relativa: calentamiento global, 273.281433669 %.
- Menor diferencia relativa: eutrofizacion, 21.584107963 %.

**Diferencias entre escenario A y escenario B:**

- B presenta mayor impacto total en ambas categorias.
- La brecha entre escenarios es marcada para calentamiento global y moderada para eutrofizacion.

**Etapa que mas contribuye:** B1 es la etapa que mas explica la diferencia de calentamiento global entre escenarios. Para eutrofizacion, B1 tambien es la etapa individual mas alta, aunque B2 aporta una fraccion relevante.

**Resultado que requiere discusion cuidadosa:** la comparacion no debe presentarse como conclusion final sin discutir la sensibilidad a factores IPCC, asignacion de sistemas de manejo y supuestos de masa equivalente.

**Figura o grafico recomendado:** grafico de barras A vs B por categoria, con etiqueta de diferencia porcentual.

