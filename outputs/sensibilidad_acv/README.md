# Evaluación determinística de sensibilidad del ACV

Estado: **PROVISIONAL M1–M2**.

Se aplicó sensibilidad determinística de un factor a la vez. El MCF de A3 y B1
se varió conjuntamente en un dominio matemático de 0–100 %, con referencia de
38 %. Los extremos no se interpretan como valores medidos o validados para la
residencia operativa de tres días. B₀ se varió ±15 % alrededor de 0,24 m³
CH₄/kg SV, conforme a la incertidumbre de la tabla 10.16A del Refinamiento 2019
del IPCC, en todas las etapas que consumen el parámetro.

- Máxima diferencia absoluta entre el caso central y los impactos oficiales:
  9.09494701773e-13.
- MCF crítico climático calculado: 2,816 %.
- El umbral es un resultado matemático del modelo, no una estimación empírica.
- Los factores EF 3.1, la unidad funcional, los balances de N/TAN y los recursos
  operativos se conservaron.
- Los archivos canónicos protegidos por huella permanecieron sin cambios.

Archivos regenerables: `sensibilidad_impactos_por_etapa.csv`,
`sensibilidad_impactos_por_escenario.csv`,
`sensibilidad_comparacion_escenarios.csv`, `sensibilidad_umbral_mcf.csv` y
`figura_sensibilidad_climatica` en formatos PNG y SVG. El registro
`vigencia_sensibilidad.json` enlaza por huellas estos productos con los impactos
canónicos que reprodujo el caso central; el manuscrito integral rechaza una
corrida incompleta, alterada u obsoleta y solicita regenerarla.
