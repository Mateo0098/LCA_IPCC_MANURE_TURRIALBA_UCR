# Resumen de resultados para redaccion

Este documento usa unicamente las tablas finales actuales de `outputs/tablas_tesis/`.

El nitrogeno total reportado en porcentaje se expresa en el modelo como `n_ex_fraction = n_ex_pct / 100`.

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
| A | 2 | A2 | Etapa 2: Lombricompostaje | 5412.504459 |
| A | 3 | A3 | Etapa 3: Almacenamiento de aguas verdes | 8753.625181 |
| A | 4 | A4 | Etapa 4: Aplicación de aguas verdes en campos de pastoreo | 259326.125181 |
| B | 1 | B1 | Etapa 1: Almacenamiento de purines | 26278.725181 |
| B | 2 | B2 | Etapa 2: Aplicación de purines en campo de pastoreo | 276851.225181 |

B2, correspondiente a la Etapa 2: Aplicación de purines en campo de pastoreo, presenta la mayor masa equivalente total. En el escenario A, A4 corresponde a la Etapa 4: Aplicación de aguas verdes en campos de pastoreo y domina la masa equivalente.

## 6.4 Emisiones estimadas por etapa y escenario

| Escenario | Sustancia | Emision total anual |
|---|---|---:|
| A | CH4 | 151.99304934377002 |
| A | CO2 | 123.7032987271146 |
| A | N2O | 3.1060540165147428 |
| A | NH3 | 24.911517716136665 |
| A | NO3 | 90.81742898594783 |
| B | CH4 | 413.11148354338246 |
| B | N2O | 1.3280869515261153 |
| B | NH3 | 29.005553343333368 |
| B | NO3 | 105.74264526845613 |

B1, correspondiente a la Etapa 1: Almacenamiento de purines, es la mayor fuente de CH4, NH3 y NO3. A1, correspondiente a la Etapa 1: Precomposteo, es la mayor fuente de N2O. A2, correspondiente a la Etapa 2: Lombricompostaje, reporta CO2 por uso de factor medido.

## 6.5 Impactos ambientales por etapa

| Escenario | Etapa | Codigo | Nombre de etapa | Calentamiento global | Eutrofizacion |
|---|---:|---|---|---:|---:|
| A | 1 | A1 | Etapa 1: Precomposteo | 888.5613345917495 | 9.09873709676829 |
| A | 2 | A2 | Etapa 2: Lombricompostaje | 317.27740205435794 | 0.0 |
| A | 3 | A3 | Etapa 3: Almacenamiento de aguas verdes | 2967.47555414812 | 4.746721623431217 |
| A | 4 | A4 | Etapa 4: Aplicación de aguas verdes en campos de pastoreo | 105.11978927162774 | 3.50122823411337 |
| B | 1 | B1 | Etapa 1: Almacenamiento de purines | 8908.477682829647 | 14.249843975911393 |
| B | 2 | B2 | Etapa 2: Aplicación de purines en campo de pastoreo | 178.57042655448 | 5.947650994758619 |

B1, correspondiente a la Etapa 1: Almacenamiento de purines, es la etapa dominante en calentamiento global y eutrofizacion.

## 6.6 Impactos totales por escenario

| escenario | categoria_impacto | resultado_total | unidad | fuente | observaciones |
| --- | --- | --- | --- | --- | --- |
| A | Calentamiento global | 4278.434080065856 | kg CO2-eq/año | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |
| A | Eutrofizacion | 17.346686954312876 | kg PO4-eq/año | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |
| B | Calentamiento global | 9087.048109384126 | kg CO2-eq/año | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |
| B | Eutrofizacion | 20.19749497067001 | kg PO4-eq/año | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |

## 6.7 Comparacion entre escenarios

| categoria_impacto | escenario_A | escenario_B | unidad | diferencia_absoluta_B_menos_A | diferencia_porcentual_B_vs_A | escenario_con_mayor_impacto | fuente | observaciones |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Calentamiento global | 4278.434080065856 | 9087.048109384126 | kg CO2-eq/año | 4808.614029318271 | 112.39191581150304 | B | processed/acv_impacto_total_por_escenario.csv | Comparacion entre escenarios con n_ex_fraction como entrada de nitrogeno |
| Eutrofizacion | 17.346686954312876 | 20.19749497067001 | kg PO4-eq/año | 2.850808016357135 | 16.43430831412072 | B | processed/acv_impacto_total_por_escenario.csv | Comparacion entre escenarios con n_ex_fraction como entrada de nitrogeno |
