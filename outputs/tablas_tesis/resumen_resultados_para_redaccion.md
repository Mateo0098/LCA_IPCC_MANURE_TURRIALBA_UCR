# Resumen de resultados para redaccion

Este documento usa unicamente las tablas finales actuales de `outputs/tablas_tesis/`.

El nitrógeno total reportado en porcentaje se expresa como fracción másica. En A2 se aplica además la materia seca gravimétrica para llevar el N del material preparado/seco a base húmeda.

## Nomenclatura oficial de etapas

| Escenario | Etapa | Codigo | Nombre oficial |
|---|---:|---|---|
| A | 1 | A1 | Etapa 1: Precomposteo |
| A | 2 | A2 | Etapa 2: Lombricompostaje |
| A | 3 | A3 | Etapa 3: Almacenamiento de aguas verdes |
| A | 4 | A4 | Etapa 4: Aplicación de aguas verdes en campos de pastoreo |
| B | 1 | B1 | Etapa 1: Almacenamiento de purines |
| B | 2 | B2 | Etapa 2: Aplicación de purines en campo de pastoreo |

## 6.2 Flujos del inventario de ciclo de vida

| Escenario | Etapa | Codigo | Nombre de etapa | Masa equivalente total (kg eq/año) |
|---|---:|---|---|---:|
| A | 1 | A1 | Etapa 1: Precomposteo | 17525.1 |
| A | 2 | A2 | Etapa 2: Lombricompostaje | 7429.968647 |
| A | 3 | A3 | Etapa 3: Almacenamiento de aguas verdes | 8753.625181 |
| A | 4 | A4 | Etapa 4: Aplicación de aguas verdes en campos de pastoreo | 259326.125181 |
| B | 1 | B1 | Etapa 1: Almacenamiento de purines | 26278.725181 |
| B | 2 | B2 | Etapa 2: Aplicación de purines en campo de pastoreo | 276851.225181 |

B2: Aplicación de purines en campo de pastoreo presenta la mayor masa equivalente total, con 276851.225181 kg eq/año.

## 6.4 Emisiones estimadas por etapa y escenario

| Escenario | Sustancia | Emision total anual |
|---|---|---:|
| A | CH4 | 74.3713097014547 |
| A | N2O | 2.4897893242667326 |
| A | NH3 | 44.55007006606425 |
| A | NO3 | 44.251501666566774 |
| A | NOx | 3.981753220187405 |
| B | CH4 | 184.99556221002345 |
| B | N2O | 2.8463417022458843 |
| B | NH3 | 69.91143819435695 |
| B | NO3 | 121.2572835051862 |
| B | NOx | 4.592074113208644 |

B1: Almacenamiento de purines es la mayor fuente de CH4; B2: Aplicación de purines en campo de pastoreo de NH3; B2: Aplicación de purines en campo de pastoreo de NO3; y B2: Aplicación de purines en campo de pastoreo de N2O. A2, correspondiente a la Etapa 2: Lombricompostaje, se estimó mediante ecuaciones IPCC.

## 6.5 Impactos ambientales por etapa

| Escenario | Etapa | Codigo | Nombre de etapa | Cambio climático | Eutrofización terrestre | Eutrofización marina |
|---|---:|---|---|---:|---:|---:|
| A | 1 | A1 | Etapa 1: Precomposteo | 525.971196842475 | 292.74403973078574 | 3.515944771802143 |
| A | 2 | A2 | Etapa 2: Lombricompostaje | 239.09634368577974 | 4.102215167300438 | 0.26636338333224296 |
| A | 3 | A3 | Etapa 3: Almacenamiento de aguas verdes | 1707.424809447395 | 118.71931473552537 | 0.8142841467529305 |
| A | 4 | A4 | Etapa 4: Aplicación de aguas verdes en campos de pastoreo | 215.24549748844524 | 201.48614287427233 | 11.051755523487586 |
| B | 1 | B1 | Etapa 1: Almacenamiento de purines | 5125.756061851811 | 356.40002640084657 | 2.444512858308245 |
| B | 2 | B2 | Etapa 2: Aplicación de purines en campo de pastoreo | 646.1754025319487 | 604.8692817994104 | 33.17780235778284 |

En cambio climático dominan A3: Almacenamiento de aguas verdes en el Escenario A y B1: Almacenamiento de purines en el Escenario B. En eutrofización terrestre dominan A1: Precomposteo y B2: Aplicación de purines en campo de pastoreo; en eutrofización marina dominan A4: Aplicación de aguas verdes en campos de pastoreo y B2: Aplicación de purines en campo de pastoreo.

## 6.6 Impactos totales por escenario

| escenario | categoria_impacto | resultado_total | unidad | fuente | observaciones |
| --- | --- | --- | --- | --- | --- |
| A | Cambio climático | 2687.737847464095 | kg CO2-eq/año | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |
| A | Eutrofización terrestre | 617.0517125078838 | mol N-eq/año | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |
| A | Eutrofización marina | 15.648347825374902 | kg N-eq/año | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |
| B | Cambio climático | 5771.93146438376 | kg CO2-eq/año | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |
| B | Eutrofización terrestre | 961.269308200257 | mol N-eq/año | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |
| B | Eutrofización marina | 35.62231521609108 | kg N-eq/año | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |

## 6.7 Comparacion entre escenarios

| categoria_impacto | escenario_A | escenario_B | unidad | diferencia_absoluta_B_menos_A | diferencia_porcentual_B_vs_A | escenario_con_mayor_impacto | fuente | observaciones |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Cambio climático | 2687.737847464095 | 5771.93146438376 | kg CO2-eq/año | 3084.1936169196647 | 114.75053714147118 | B | processed/acv_impacto_total_por_escenario.csv | Comparación entre escenarios con la fracción másica efectiva como entrada de nitrógeno |
| Eutrofización terrestre | 617.0517125078838 | 961.269308200257 | mol N-eq/año | 344.21759569237315 | 55.78423796821975 | B | processed/acv_impacto_total_por_escenario.csv | Comparación entre escenarios con la fracción másica efectiva como entrada de nitrógeno |
| Eutrofización marina | 15.648347825374902 | 35.62231521609108 | kg N-eq/año | 19.97396739071618 | 127.64265987446277 | B | processed/acv_impacto_total_por_escenario.csv | Comparación entre escenarios con la fracción másica efectiva como entrada de nitrógeno |
