# Reporte técnico de referencias de factores

## Trazabilidad metodológica

- Los factores y las ecuaciones clasificados como IPCC fueron contrastados con su implementación en `scripts/ecuaciones_acv.py` y con las tablas de parámetros del proyecto.
- Los factores de caracterización de calentamiento global se referencian como IMN (2021).
- Los factores de caracterización de eutrofización se referencian como Ecobilan (1999, como se citó en Vallejo, 2004).
- El parámetro específico de lixiviación de A2 se documenta mediante Vargas Sarmiento (2023) y observación directa del investigador.
- Los factores sin fuente confirmada no recibieron una atribución inventada.

| Factor | Clasificación | Referencia asignada | Archivo o tabla donde aparece | Justificación | Estado |
|---|---|---|---|---|---|
| Potencial de eutrofizacion | Ecobilan (1999) citado en Vallejo (2004) | Ecobilan (1999, como se citó en Vallejo, 2004) | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Factor de caracterización del potencial de eutrofización. | Resuelto |
| Potencial de calentamiento global | IMN (2021) | IMN (2021) | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Factor de caracterización del potencial de calentamiento global. | Resuelto |
| EF3 | IPCC | IPCC | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Parámetro o ecuación de estimación de emisiones asociado con la metodología IPCC. | Resuelto |
| Fraccion lixiviada MMS | IPCC | IPCC | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Parámetro o ecuación de estimación de emisiones asociado con la metodología IPCC. | Resuelto |
| Fraccion volatilizada MMS | IPCC | IPCC | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Parámetro o ecuación de estimación de emisiones asociado con la metodología IPCC. | Resuelto |
| MCF | IPCC | IPCC | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Parámetro o ecuación de estimación de emisiones asociado con la metodología IPCC. | Resuelto |
| Fracción lixiviada efectiva | Supuesto del modelo | Vargas Sarmiento (2023) y observación directa del investigador | `tabla_05_factores_emision_y_caracterizacion.csv`; apéndices de factores de ambos Word | Supuesto explícito del modelo; no se presenta como factor bibliográfico. | Resuelto |

## Protección de resultados y del documento maestro

- No se modificaron valores numéricos, ecuaciones, cálculos ni resultados.
- El documento maestro protegido no fue modificado: Sí.
- Hash SHA-256 del documento maestro: `98ABDE3EC5A22FA052EFA595AAC26729EA070EACA670BDC41097C4BF2E5E327C`.
