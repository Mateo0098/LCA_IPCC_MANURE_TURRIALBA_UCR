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

B2, correspondiente a la Etapa 2: Aplicación de purines en campo de pastoreo, presenta la mayor masa equivalente total. En el escenario A, A4 corresponde a la Etapa 4: Aplicación de aguas verdes en campos de pastoreo y domina la masa equivalente.

## 6.4 Emisiones estimadas por etapa y escenario

| Escenario | Sustancia | Emision total anual |
|---|---|---:|
| A | CH4 | 139.23463637335524 |
| A | N2O | 4.976344420740896 |
| A | NH3 | 44.55079034604405 |
| A | NO3 | 162.41436128553823 |
| B | CH4 | 389.4643414947861 |
| B | N2O | 1.7504371342481058 |
| B | NH3 | 38.93616508636328 |
| B | NO3 | 141.945683438846 |

B1, correspondiente a la Etapa 1: Almacenamiento de purines, es la mayor fuente de CH4, NH3 y NO3. A1, correspondiente a la Etapa 1: Precomposteo, es la mayor fuente de N2O. A2, correspondiente a la Etapa 2: Lombricompostaje, se estimó mediante ecuaciones IPCC.

## 6.5 Impactos ambientales por etapa

| Escenario | Etapa | Codigo | Nombre de etapa | Calentamiento global | Eutrofizacion |
|---|---:|---|---|---:|---:|
| A | 1 | A1 | Etapa 1: Precomposteo | 1189.6041709349145 | 12.68246985818677 |
| A | 2 | A2 | Etapa 2: Lombricompostaje | 308.9408352465669 | 7.213468681036463 |
| A | 3 | A3 | Etapa 3: Almacenamiento de aguas verdes | 2832.6458116004305 | 6.616319745709744 |
| A | 4 | A4 | Etapa 4: Aplicación de aguas verdes en campos de pastoreo | 135.40331648822615 | 4.509882658308575 |
| B | 1 | B1 | Etapa 1: Almacenamiento de purines | 8503.71352199646 | 19.86245066609851 |
| B | 2 | B2 | Etapa 2: Aplicación de purines en campo de pastoreo | 217.67316101096097 | 7.2500470408190045 |

B1, correspondiente a la Etapa 1: Almacenamiento de purines, es la etapa dominante en calentamiento global y eutrofizacion.

## 6.6 Impactos totales por escenario

| escenario | categoria_impacto | resultado_total | unidad | fuente | observaciones |
| --- | --- | --- | --- | --- | --- |
| A | Calentamiento global | 4466.594134270137 | kg CO2-eq/año | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |
| A | Eutrofizacion | 31.02214094324156 | kg PO4-eq/año | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |
| B | Calentamiento global | 8721.386683007422 | kg CO2-eq/año | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |
| B | Eutrofizacion | 27.11249770691752 | kg PO4-eq/año | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |

## 6.7 Comparacion entre escenarios

| categoria_impacto | escenario_A | escenario_B | unidad | diferencia_absoluta_B_menos_A | diferencia_porcentual_B_vs_A | escenario_con_mayor_impacto | fuente | observaciones |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Calentamiento global | 4466.594134270137 | 8721.386683007422 | kg CO2-eq/año | 4254.792548737285 | 95.25809645636268 | B | processed/acv_impacto_total_por_escenario.csv | Comparación entre escenarios con la fracción másica efectiva como entrada de nitrógeno |
| Eutrofizacion | 31.02214094324156 | 27.11249770691752 | kg PO4-eq/año | -3.9096432363240368 | -12.602751188182538 | A | processed/acv_impacto_total_por_escenario.csv | Comparación entre escenarios con la fracción másica efectiva como entrada de nitrógeno |
