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

| Escenario | Etapa | Codigo | Nombre de etapa | Calentamiento global | Eutrofizacion |
|---|---:|---|---|---:|---:|
| A | 1 | A1 | Etapa 1: Precomposteo | 518.8557038555156 | 7.775130787114285 |
| A | 2 | A2 | Etapa 2: Lombricompostaje | 226.76495777803757 | 0.0332862595385599 |
| A | 3 | A3 | Etapa 3: Almacenamiento de aguas verdes | 1343.5935684386643 | 3.0837076262622776 |
| A | 4 | A4 | Etapa 4: Aplicación de aguas verdes en campos de pastoreo | 244.4179641810184 | 8.904292508531208 |
| B | 1 | B1 | Etapa 1: Almacenamiento de purines | 4033.5204455173243 | 9.257410909595611 |
| B | 2 | B2 | Etapa 2: Aplicación de purines en campo de pastoreo | 733.7522885893924 | 26.731034391422007 |

En calentamiento global dominan A3: Almacenamiento de aguas verdes en el Escenario A y B1: Almacenamiento de purines en el Escenario B. En eutrofización dominan A4: Aplicación de aguas verdes en campos de pastoreo en el Escenario A y B2: Aplicación de purines en campo de pastoreo en el Escenario B.

## 6.6 Impactos totales por escenario

| escenario | categoria_impacto | resultado_total | unidad | fuente | observaciones |
| --- | --- | --- | --- | --- | --- |
| A | Calentamiento global | 2333.632194253236 | kg CO2-eq/año | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |
| A | Eutrofizacion | 19.79641718144633 | kg PO4-eq/año | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |
| B | Calentamiento global | 4767.272734106717 | kg CO2-eq/año | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |
| B | Eutrofizacion | 35.98844530101762 | kg PO4-eq/año | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |

## 6.7 Comparacion entre escenarios

| categoria_impacto | escenario_A | escenario_B | unidad | diferencia_absoluta_B_menos_A | diferencia_porcentual_B_vs_A | escenario_con_mayor_impacto | fuente | observaciones |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Calentamiento global | 2333.632194253236 | 4767.272734106717 | kg CO2-eq/año | 2433.6405398534807 | 104.28552305057 | B | processed/acv_impacto_total_por_escenario.csv | Comparación entre escenarios con la fracción másica efectiva como entrada de nitrógeno |
| Eutrofizacion | 19.79641718144633 | 35.98844530101762 | kg PO4-eq/año | 16.19202811957129 | 81.79272022387384 | B | processed/acv_impacto_total_por_escenario.csv | Comparación entre escenarios con la fracción másica efectiva como entrada de nitrógeno |
