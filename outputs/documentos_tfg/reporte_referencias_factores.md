# Reporte técnico de referencias de factores

## Trazabilidad metodológica

- Los factores y las ecuaciones clasificados como IPCC fueron contrastados con su implementación en `scripts/ecuaciones_acv.py` y con las tablas de parámetros del proyecto.
- Los factores de caracterización de calentamiento global se referencian como IMN (2021).
- Los factores de caracterización de eutrofización se referencian como Ecobilan (1999, como se citó en Vallejo, 2004).
- Los factores medidos por unidad de residuo seco o estiércol precompostado se referencian como Jjagwe et al. (2019).
- Referencia completa: Jjagwe, J., Komakech, A. J., Karungi, J., Amann, A., Wanyama, J., & Lederer, J. (2019). Assessment of a Cattle Manure Vermicomposting System Using Material Flow Analysis: A Case Study from Uganda. Sustainability, 11(19), 5173. https://doi.org/10.3390/su11195173
- Los factores sin fuente confirmada no recibieron una atribución inventada.

| Factor | Clasificación | Referencia asignada | Archivo o tabla donde aparece | Justificación | Estado |
|---|---|---|---|---|---|
| FACTOR_N_A_N2O | Conversión estequiométrica | Conversión estequiométrica de N₂O-N a N₂O (44/28) | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Relación derivada de masas molares; no requiere una fuente empírica. | Resuelto |
| FACTOR_N_A_NH3 | Conversión estequiométrica | Conversión estequiométrica de N a NH₃ (17/14) | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Relación derivada de masas molares; no requiere una fuente empírica. | Resuelto |
| NH_3_eq | Ecobilan (1999) citado en Vallejo (2004) | Ecobilan (1999, como se citó en Vallejo, 2004) | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Factor de caracterización del potencial de eutrofización. | Resuelto |
| NO_3_eq | Ecobilan (1999) citado en Vallejo (2004) | Ecobilan (1999, como se citó en Vallejo, 2004) | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Factor de caracterización del potencial de eutrofización. | Resuelto |
| Potencial de eutrofizacion | Ecobilan (1999) citado en Vallejo (2004) | Ecobilan (1999, como se citó en Vallejo, 2004) | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Factor de caracterización del potencial de eutrofización. | Resuelto |
| CH_4_eq | IMN (2021) | IMN (2021) | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Factor de caracterización del potencial de calentamiento global. | Resuelto |
| N_2_O_eq | IMN (2021) | IMN (2021) | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Factor de caracterización del potencial de calentamiento global. | Resuelto |
| Potencial de calentamiento global | IMN (2021) | IMN (2021) | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Factor de caracterización del potencial de calentamiento global. | Resuelto |
| B0_T | IPCC | IPCC, ecuación de estimación de CH₄ | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Parámetro o ecuación de estimación de emisiones asociado con la metodología IPCC. | Resuelto |
| EF1 | IPCC | IPCC, ecuación 14 | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Parámetro o ecuación de estimación de emisiones asociado con la metodología IPCC. | Resuelto |
| EF3 | IPCC | IPCC | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Parámetro o ecuación de estimación de emisiones asociado con la metodología IPCC. | Resuelto |
| EF4 | IPCC | IPCC, ecuaciones 5 y 16 | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Parámetro o ecuación de estimación de emisiones asociado con la metodología IPCC. | Resuelto |
| EF5 | IPCC | IPCC, ecuaciones 6 y 18 | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Parámetro o ecuación de estimación de emisiones asociado con la metodología IPCC. | Resuelto |
| Fraccion lixiviada MMS | IPCC | IPCC | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Parámetro o ecuación de estimación de emisiones asociado con la metodología IPCC. | Resuelto |
| Fraccion volatilizada MMS | IPCC | IPCC | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Parámetro o ecuación de estimación de emisiones asociado con la metodología IPCC. | Resuelto |
| MCF | IPCC | IPCC | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Parámetro o ecuación de estimación de emisiones asociado con la metodología IPCC. | Resuelto |
| R_N2_N2O | IPCC | IPCC, ecuación 24 | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Parámetro o ecuación de estimación de emisiones asociado con la metodología IPCC. | Resuelto |
| frac_gasm | IPCC | IPCC, ecuación 16 | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Parámetro o ecuación de estimación de emisiones asociado con la metodología IPCC. | Resuelto |
| frac_leach_h | IPCC | IPCC, ecuación 18 | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Parámetro o ecuación de estimación de emisiones asociado con la metodología IPCC. | Resuelto |
| Factor medido CH4 | Jjagwe et al. (2019) | Jjagwe et al. (2019) | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Factor medido por kilogramo de residuo en base seca reportado para vermicompostaje de estiércol bovino. | Resuelto |
| Factor medido CO2 | Jjagwe et al. (2019) | Jjagwe et al. (2019) | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Factor medido por kilogramo de residuo en base seca reportado para vermicompostaje de estiércol bovino. | Resuelto |
| Factor medido N2O | Jjagwe et al. (2019) | Jjagwe et al. (2019) | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Factor medido por kilogramo de residuo en base seca reportado para vermicompostaje de estiércol bovino. | Resuelto |
| ch4_kg_por_kg_residuo_seco | Jjagwe et al. (2019) | Jjagwe et al. (2019) | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Factor medido por kilogramo de residuo en base seca reportado para vermicompostaje de estiércol bovino. | Resuelto |
| co2_kg_por_kg_residuo_seco | Jjagwe et al. (2019) | Jjagwe et al. (2019) | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Factor medido por kilogramo de residuo en base seca reportado para vermicompostaje de estiércol bovino. | Resuelto |
| n2o_kg_por_kg_residuo_seco | Jjagwe et al. (2019) | Jjagwe et al. (2019) | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Factor medido por kilogramo de residuo en base seca reportado para vermicompostaje de estiércol bovino. | Resuelto |
| FACTOR_N_A_NO3 | Revisión manual | Requiere revisión bibliográfica y estequiométrica | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | El origen no pudo confirmarse sin introducir una referencia no sustentada. | Requiere revisión bibliográfica |
| AWMS | Supuesto del modelo | Supuesto del modelo con estructura IPCC | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Supuesto explícito del modelo; no se presenta como factor bibliográfico. | Resuelto |
| N | Supuesto del modelo | Supuesto de unidad equivalente del modelo | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Supuesto explícito del modelo; no se presenta como factor bibliográfico. | Resuelto |
| N_cdg | Supuesto del modelo | Supuesto de ausencia de codigestión | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Supuesto explícito del modelo; no se presenta como factor bibliográfico. | Resuelto |

## Protección de resultados y del documento maestro

- No se modificaron valores numéricos, ecuaciones, cálculos ni resultados.
- El documento maestro protegido no fue modificado: Sí.
- Hash SHA-256 del documento maestro: `98ABDE3EC5A22FA052EFA595AAC26729EA070EACA670BDC41097C4BF2E5E327C`.
