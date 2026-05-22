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
| B | 2 | B2 | Etapa 2: Aplicación en campo |

## 6.2 Flujos del inventario de ciclo de vida

| Escenario | Etapa | Codigo | Nombre de etapa | Masa equivalente total (kg eq/ano) |
|---|---:|---|---|---:|
| A | 1 | A1 | Etapa 1: Precomposteo | 4767.45683 |
| A | 2 | A2 | Etapa 2: Lombricompostaje | 1472.39567 |
| A | 3 | A3 | Etapa 3: Almacenamiento de aguas verdes | 358.840837 |
| A | 4 | A4 | Etapa 4: Aplicación de aguas verdes en campos de pastoreo | 71789.81012 |
| B | 1 | B1 | Etapa 1: Almacenamiento de purines | 5126.297667 |
| B | 2 | B2 | Etapa 2: Aplicación en campo | 76557.26695 |

B2, correspondiente a la Etapa 2: Aplicación en campo, presenta la mayor masa equivalente total. En el escenario A, A4 corresponde a la Etapa 4: Aplicación de aguas verdes en campos de pastoreo y domina la masa equivalente.

## 6.4 Emisiones estimadas por etapa y escenario

| Escenario | Sustancia | Emision total anual |
|---|---|---:|
| A | CH4 | 9.553739792210887 |
| A | CO2 | 33.65174159028255 |
| A | N2O | 0.7887052407443644 |
| A | NH3 | 5.225984426798057 |
| A | NO3 | 19.059472615381146 |
| B | CH4 | 80.58733518133177 |
| B | N2O | 0.30599583920197904 |
| B | NH3 | 6.353966547610867 |
| B | NO3 | 23.173289761874926 |

B1, correspondiente a la Etapa 1: Almacenamiento de purines, es la mayor fuente de CH4, NH3 y NO3. A1, correspondiente a la Etapa 1: Precomposteo, es la mayor fuente de N2O. A2, correspondiente a la Etapa 2: Lombricompostaje, reporta CO2 por uso de factor medido.

## 6.5 Impactos ambientales por etapa

| Escenario | Etapa | Codigo | Nombre de etapa | Calentamiento global | Eutrofizacion |
|---|---:|---|---|---:|---:|
| A | 1 | A1 | Etapa 1: Precomposteo | 241.72060664266405 | 2.4756760096956123 |
| A | 2 | A2 | Etapa 2: Lombricompostaje | 86.31085230736173 | 0.0 |
| A | 3 | A3 | Etapa 3: Almacenamiento de aguas verdes | 121.6469050946848 | 0.19462297388400168 |
| A | 4 | A4 | Etapa 4: Aplicación de aguas verdes en campos de pastoreo | 29.100537812753565 | 0.9694454642609143 |
| B | 1 | B1 | Etapa 1: Almacenamiento de purines | 1737.8129284227848 | 2.780328195940978 |
| B | 2 | B2 | Etapa 2: Aplicación en campo | 49.37982053779582 | 1.6450226231009433 |

B1, correspondiente a la Etapa 1: Almacenamiento de purines, es la etapa dominante en calentamiento global y eutrofizacion.

## 6.6 Impactos totales por escenario

| escenario | categoria_impacto | resultado_total | unidad | fuente | observaciones |
| --- | --- | --- | --- | --- | --- |
| A | Calentamiento global | 478.7789018574642 | kg CO2-eq/ano | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |
| A | Eutrofizacion | 3.639744447840529 | kg PO4-eq/ano | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |
| B | Calentamiento global | 1787.1927489605807 | kg CO2-eq/ano | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |
| B | Eutrofizacion | 4.425350819041921 | kg PO4-eq/ano | processed/acv_impacto_total_por_escenario.csv | Suma de impactos por etapa |

## 6.7 Comparacion entre escenarios

| categoria_impacto | escenario_A | escenario_B | unidad | diferencia_absoluta_B_menos_A | diferencia_porcentual_B_vs_A | escenario_con_mayor_impacto | fuente | observaciones |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Calentamiento global | 478.7789018574642 | 1787.1927489605807 | kg CO2-eq/ano | 1308.4138471031165 | 273.2814336694896 | B | processed/acv_impacto_total_por_escenario.csv | Comparacion entre escenarios con n_ex_fraction como entrada de nitrogeno |
| Eutrofizacion | 3.639744447840529 | 4.425350819041921 | kg PO4-eq/ano | 0.7856063712013923 | 21.584107963060287 | B | processed/acv_impacto_total_por_escenario.csv | Comparacion entre escenarios con n_ex_fraction como entrada de nitrogeno |
