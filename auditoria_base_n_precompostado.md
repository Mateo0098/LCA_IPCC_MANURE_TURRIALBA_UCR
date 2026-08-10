# Auditoría de la base del nitrógeno y carbono del estiércol precompostado

## Alcance

Esta revisión se limita a metadata analítica, evidencia documental y trazabilidad del valor histórico de N del estiércol precompostado. No se modificaron el modelo ACV, sus parámetros vigentes, ecuaciones, emisiones, impactos, flujos, documentos Word, tablas de tesis, gráficos ni el documento maestro.

## 1. Método CIA confirmado para N y C de abonos sólidos

La metodología oficial del Laboratorio de Suelos y Foliares de la Ciudad de la Investigación (CIA), aportada por el investigador, establece para N y C en abonos sólidos:

1. secado de la muestra a 80 °C durante 48 h;
2. molienda;
3. paso por criba de 1 mm;
4. pesada aproximada de 80–100 mg;
5. análisis en un autoanalizador Elementar Vario Macro Cube;
6. determinación mediante combustión seca de Dumas.

En consecuencia, los resultados de los reportes CIA 97600 y 100751 quedaron documentados como:

```text
metodo_analitico = Dumas (combustión seca)
```

La fuente se registra en `scripts/sampling_ingestion_config.py` como “metodología oficial CIA para N/C de abonos sólidos suministrada por el investigador”, junto con la preparación y el equipo indicados. No se encontró en el repositorio un archivo independiente de esa metodología; la trazabilidad disponible corresponde a la información documental proporcionada por el investigador en esta fase.

## 2. Evidencia de los reportes 97600 y 100751

### Reporte CIA 97600, M1

- Identifica el análisis como `CN` y el material como `ABONO SOLIDO`.
- Presenta dos muestras de precompostado.
- Encabezados analíticos: `N` y `C`.
- Unidad visible: `% masa`.
- No incluye nota que diga “base seca”, “base fresca”, “tal como recibido” ni una corrección posterior por humedad.
- No se modificaron los valores 2,41; 2,44; 35,8 y 35,69.

### Reporte CIA 100751, M2

- Identifica el análisis como `CN` y el material como `AO SOLIDO`.
- Presenta tres muestras de precompostado.
- Encabezados analíticos: `C`, `N` y `C/N`.
- La hoja principal muestra `%` para C y N; la hoja oculta `INTERPRETACION` contiene una plantilla con `% masa`.
- No incluye nota que diga “base seca”, “base fresca”, “tal como recibido” ni una corrección posterior por humedad.
- No se modificaron los valores de C, N o C/N reportados.

## 3. Base del porcentaje reportado

El secado a 80 °C durante 48 h forma parte del procedimiento de preparación para el análisis de Dumas. El CIA aclaró que no determinó humedad a 105 °C porque no fue solicitada. Por sí sola, esta preparación no demuestra que el laboratorio exprese el resultado final sobre base seca: el método podría incluir una convención de reporte o una corrección posterior no descrita en los archivos disponibles.

Los reportes solo declaran `% masa` o `%`; la metodología aportada describe el procedimiento, pero no especifica inequívocamente la base final de cálculo del porcentaje reportado. Por tanto, la conclusión documental es:

> **Base de medición no especificada en el reporte.**

La capa normalizada registra para N y C de precompostado M1 y M2:

```text
base_medicion = muestra previamente secada a 80 °C durante 48 h; base final del porcentaje no especificada formalmente por el reporte
```

No se afirma base seca ni base fresca y no se cambia ningún valor numérico.

## 4. Trazabilidad histórica exacta del N = 2,425 %

La ruta vigente anterior a la nueva capa multijornada es:

```text
Reporte CIA 97600
→ processed/CIA_samples_table_v6.csv
   muestras: 2,41 % y 2,44 %
→ processed/CIA_samples_table_v6_treatment_summary.csv
   mean_n_percentage = 2,425
→ scripts/generate_acv_parametros_escenario_etapa.py
→ processed/acv_parametros_escenario_etapa.csv
   escenario A, etapa 2, n_ex_pct = 2,425
→ scripts/acv_parametros_etapa.py
→ scripts/ACV_EscenarioA_etapa2.py
```

`scripts/generate_acv_parametros_escenario_etapa.py` copia directamente `mean_n_percentage` a `n_ex_pct`. La tabla vigente `processed/acv_parametros_escenario_etapa.csv` asigna 2,425 a `A,2,SOL: PRECOMPOSTADO` con unidad `% N total`.

En la ruta IPCC de `scripts/ACV_EscenarioA_etapa2.py` se ejecuta explícitamente:

```text
n_ex_pct = 2,425
n_ex_fraction = n_ex_pct / 100
n_ex_fraction = 0,02425 kg N/kg muestra
```

El código no aplica en ese punto una conversión de base seca a base fresca ni multiplica N por la fracción de materia seca. Por ello, la ruta IPCC presupone implícitamente que `0,02425 kg N/kg muestra` es compatible con la masa de muestra usada como base del cálculo y del escalado; operacionalmente se comporta como una concentración sobre la masa húmeda/equivalente del flujo.

## 5. Uso actual y alcance potencial

La selección vigente en `processed/modelo_etapa_overrides.csv` es:

```text
A,2,medido
```

Por tanto, la ejecución actual de A2 utiliza `_build_medido_row()`, cuyos factores de CO₂, CH₄ y N₂O se expresan por residuo seco y se convierten usando la fracción de materia seca. Esa rama no usa `n_ex_pct = 2,425` para generar la fila vigente de emisiones. El valor sigue presente en la tabla de parámetros, pero actualmente la rama IPCC que lo consumiría no es la seleccionada.

Si A2 se ejecutara con el modelo IPCC, `0,02425` alimentaría:

- N₂O directo de manejo (`N2O_ec2`);
- N volatilizado y N₂O indirecto por volatilización (`N2O_ec5`);
- N lixiviado y N₂O indirecto por lixiviación (`N2O_ec6`);
- NH₃ derivado de las rutas indirectas (`NH3_ec12`);
- NO₃ derivado de las rutas indirectas (`NO3_ec13`).

Esos resultados se escalarían con la masa equivalente de A2 en `scripts/acv_resumen_emisiones_csv.py` y podrían propagarse a:

- `processed/ACV_resumen_emisiones.csv`, fila A2;
- `processed/acv_impacto_por_etapa_escenario.csv`, A2;
- `processed/acv_impacto_total_por_escenario.csv`, total del escenario A;
- potencial de calentamiento global, por N₂O;
- potencial de eutrofización, por NH₃ y NO₃;
- gráficos, tablas y documentos que se regeneraran posteriormente desde esas salidas.

Independientemente de la rama de emisiones, el 2,425 % también es consumido como dato de caracterización por `scripts/generate_thesis_tables.py` y es citado por `scripts/generate_results_docx.py`. Estos productos no se regeneraron.

## 6. Cambios de metadata

- M1 y M2 de precompostado: `metodo_analitico = Dumas (combustión seca)`.
- N y C de precompostado: se registra el secado previo a 80 °C durante 48 h y que la base formal del porcentaje no fue especificada por el reporte.
- N de precompostado conserva `uso_modelo = elegible`, sin conexión nueva con el modelo.
- Carbono, relación C/N y densidad usan `uso_modelo = solo_caracterizacion`.
- N, humedad, materia seca, cenizas y sólidos volátiles no fueron excluidos por esta revisión.
- Los líquidos M1 conservan especiación y `solo_trazabilidad`.
- El N total de líquidos M2 conserva Kjeldahl y `elegible`.

El estado `solo_caracterizacion` significa que la variable se conserva íntegramente, pero no se presenta como parámetro consumido actualmente por el ACV.

## 7. Archivos modificados en esta revisión

- `scripts/sampling_ingestion_config.py`
- `scripts/extract_analysis_results.py`
- `scripts/validate_sampling_ingestion.py`
- `README_METODOLOGIA.md`
- `DICCIONARIO_TRAZABILIDAD_VARIABLES.md`
- `auditoria_ingestion_m1_m2.md`

Se regeneraron únicamente:

- `processed/muestreos_observaciones_normalizadas.csv`
- `processed/muestreos_resumen_intrajornada.csv`

Se creó este informe: `auditoria_base_n_precompostado.md`.

## 8. Recomendación documental sin modificar el modelo

Solicitar al CIA una aclaración escrita o el apartado del procedimiento que defina la base de expresión final de N y C (`base seca`, `base fresca/tal como recibido` u otra). Hasta contar con esa evidencia, mantener la base como no especificada y no convertir el 2,425 %.

Antes de una futura modificación del modelo, documentar y aprobar si `n_ex_fraction` debe representar kg N por kg de material húmedo, seco o tal como recibido. Esa decisión debe evaluarse junto con la selección de modelo de A2 y no resolverse mediante una conversión automática en la capa de ingestión.

`DECISIONES_METODOLOGICAS_TFG.md` no fue modificado. Sería conveniente registrar allí la confirmación de Dumas y la incertidumbre sobre la base cuando el investigador autorice una actualización documental.

## 9. Verificación de no impacto

Hashes SHA-256 registrados antes de la revisión:

| Archivo | SHA-256 antes |
|---|---|
| `processed/ACV_resumen_emisiones.csv` | `A904EDF4F77D21F99D3683E24A91FD475B702CE711D4100A2E6643B80B2C0C8B` |
| `processed/acv_impacto_por_etapa_escenario.csv` | `CE164CD555B230CF96BDBE6DAB084D6D0C48027B0AB1B79760E93FC444186181` |
| `processed/acv_impacto_total_por_escenario.csv` | `7040A111CC5AE067C9510A83262D653BB96CD4F305994086821316EF147E038B` |
| `processed/masa_total_escenario_etapa.csv` | `FA243E995D1F013D521371A59AB2404D35BC0C7A410F2780DC0E8E61CD6B2596` |

Hashes SHA-256 posteriores:

| Archivo | SHA-256 después | Resultado |
|---|---|---|
| `processed/ACV_resumen_emisiones.csv` | `A904EDF4F77D21F99D3683E24A91FD475B702CE711D4100A2E6643B80B2C0C8B` | Idéntico |
| `processed/acv_impacto_por_etapa_escenario.csv` | `CE164CD555B230CF96BDBE6DAB084D6D0C48027B0AB1B79760E93FC444186181` | Idéntico |
| `processed/acv_impacto_total_por_escenario.csv` | `7040A111CC5AE067C9510A83262D653BB96CD4F305994086821316EF147E038B` | Idéntico |
| `processed/masa_total_escenario_etapa.csv` | `FA243E995D1F013D521371A59AB2404D35BC0C7A410F2780DC0E8E61CD6B2596` | Idéntico |

Validaciones ejecutadas:

- compilación de los cinco scripts de ingestión;
- validación estructural de 176 observaciones y 35 resúmenes;
- comprobación de Dumas y base no especificada para N/C M1 y M2;
- comprobación de los valores originales de N: M1 = 2,41 y 2,44; M2 = 2,72, 2,34 y 2,69;
- comprobación de las reglas de N líquido M1 y M2;
- comprobación de `solo_caracterizacion` para densidad, carbono y C/N;
- `git diff --check`: código 0, sin errores;
- estado limitado a `MASTER_escrito`, `outputs`, archivos Word y las cuatro salidas ACV: sin cambios.

Estado final de Git:

```text
 M DICCIONARIO_TRAZABILIDAD_VARIABLES.md
 M README_METODOLOGIA.md
 M scripts/compute_sample_parameters.py
 M scripts/extract_analysis_results.py
?? "Academic_documents/resultados CIA y LASA muestreo 2/043-26 Contenido de Nitrogeno-firmado.pdf"
?? "Academic_documents/resultados CIA y LASA muestreo 2/AO-00330-00332 (100750) SEDE DEL ATLANTICO.xlsx"
?? "Academic_documents/resultados CIA y LASA muestreo 2/AO-00333-00335 (100751) SEDE DEL ATLANTICO.xlsx"
?? "Academic_documents/resultados CIA y LASA muestreo 2/AO-00337-00339 (100788) SEDE DEL ATLANTICO.xlsx"
?? "Academic_documents/resultados CIA y LASA muestreo 2/muestreo2_solidos_volatiles.xlsx"
?? auditoria_base_n_precompostado.md
?? auditoria_ingestion_m1_m2.md
?? auditoria_integracion_muestreo_2.md
?? processed/muestreos_observaciones_normalizadas.csv
?? processed/muestreos_resumen_intrajornada.csv
?? scripts/build_sampling_ingestion.py
?? scripts/sampling_ingestion_config.py
?? scripts/validate_sampling_ingestion.py
```

Los cambios distintos de `auditoria_base_n_precompostado.md` incluyen el trabajo no confirmado de la Fase 2 que ya estaba presente al iniciar esta revisión. No se hizo commit ni push.
