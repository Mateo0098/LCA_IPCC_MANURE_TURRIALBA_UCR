# Auditoría de ingestión multijornada M1–M2

## Alcance

Se construyó una capa nueva e independiente para ingestión y resumen de M1 y M2. Las salidas nuevas no están conectadas con los parámetros ni con los scripts del modelo ACV. No se calcularon promedios entre jornadas.

La jerarquía aplicada fue:

```text
fuente original
→ observación primaria normalizada
→ réplica o submuestra analítica
→ promedio de muestra compuesta
→ resumen independiente de la jornada
→ futura integración entre jornadas
→ futura aprobación para uso en el modelo ACV
```

## Estructura actual del libro gravimétrico M2

Se reinspeccionó `Academic_documents/resultados CIA y LASA muestreo 2/muestreo2_solidos_volatiles.xlsx` antes de programar el lector.

- Hojas: `Procedure`, `Data` y `Equipement`.
- La hoja `Data` tiene actualmente 67 filas y 15 columnas.
- En el archivo disponible todavía aparece `CRISOL ID` en la columna B; sus celdas de datos están vacías. El lector no depende de esta columna ni implementa una regla especial para ella.
- Las masas primarias de secado se localizaron por encabezado: crisol vacío, crisol con muestra húmeda y crisol con muestra seca.
- Las masas primarias de incineración se localizaron por encabezado: crisol vacío, crisol con muestra seca y crisol con muestra incinerada.
- Secado: `A11`–`A33` y `B11`–`B33`.
- Incineración: `AI11`–`AI33` y `BI11`–`BI33`.
- A identifica estiércol fresco; B identifica estiércol precompostado. El primer dígito identifica la muestra compuesta y el segundo la submuestra analítica.
- Se confirmaron tres muestras compuestas por material y tres submuestras por muestra.

Las fórmulas y resúmenes internos del libro no se consumen. El código exige valores numéricos primarios y reconstruye en Python las mismas ecuaciones vigentes para M1:

- humedad = `((masa húmeda - masa seca) / masa húmeda) × 100`;
- materia seca = `(masa seca / masa húmeda) × 100`;
- cenizas = `(masa de ceniza / masa seca para incineración) × 100`;
- sólidos volátiles = `100 - cenizas`.

La comparación contra la salida gravimétrica histórica de M1 confirmó que se preservaron las ecuaciones; las diferencias posibles se limitan al redondeo de presentación de la tabla histórica.

## Arquitectura implementada

- `scripts/sampling_ingestion_config.py` declara cada fuente, jornada, material, laboratorio, método, elegibilidad y justificación.
- `scripts/extract_analysis_results.py` incorpora lectores normalizados para CIA y LASA sin retirar su interfaz histórica.
- `scripts/compute_sample_parameters.py` incorpora el lector gravimétrico por encabezados sin alterar las ecuaciones existentes.
- `scripts/build_sampling_ingestion.py` genera las observaciones y el resumen jerárquico.
- `scripts/validate_sampling_ingestion.py` verifica conteos, claves, unidades, jerarquía y decisiones metodológicas.

## Salidas nuevas

### Observaciones normalizadas

`processed/muestreos_observaciones_normalizadas.csv` contiene 176 observaciones:

| Jornada | Observaciones |
|---|---:|
| M1 | 74 |
| M2 | 102 |

Conteos por material:

| Jornada | Material | Observaciones | Muestras compuestas | Pares muestra–réplica analítica recuperados |
|---|---|---:|---:|---:|
| M1 | Estiércol fresco | 30 | 2 | 6 |
| M1 | Estiércol precompostado | 28 | 2 | 6 |
| M1 | Aguas verdes | 8 | 2 | 0 reportadas |
| M1 | Purines | 8 | 2 | 0 reportadas |
| M2 | Estiércol fresco | 45 | 3 | 9 |
| M2 | Estiércol precompostado | 45 | 3 | 9 |
| M2 | Aguas verdes | 6 | 3 | 0 reportadas |
| M2 | Purines | 6 | 3 | 0 reportadas |

Los conteos de observaciones incluyen una fila por variable. En los sólidos, cada submuestra origina cuatro observaciones gravimétricas. En los informes CIA de líquidos, la densidad reportada se conserva además de las variables de N.

### Resumen intrajornada

`processed/muestreos_resumen_intrajornada.csv` contiene 35 filas. Para datos con réplicas analíticas, primero se calculó el promedio de cada muestra compuesta y después el promedio de los promedios de muestra. La desviación estándar principal es la variación entre muestras compuestas, no entre todas las submuestras agrupadas.

## Comparación descriptiva M1–M2

La tabla siguiente compara únicamente variables consideradas metodológicamente comparables. `DE` es la desviación estándar entre muestras compuestas. La diferencia absoluta es `|M2 − M1|`; la diferencia porcentual conserva el signo de `(M2 − M1) / M1`.

| Material | Variable | n M1 | Promedio M1 | DE M1 | n M2 | Promedio M2 | DE M2 | Diferencia absoluta | Diferencia porcentual | Unidad |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Estiércol fresco | N total | 2 | 0,371667 | 0,044783 | 3 | 0,664444 | 0,013472 | 0,292778 | +78,77 % | % masa |
| Estiércol fresco | Humedad | 2 | 85,769829 | 0,620520 | 3 | 87,030254 | 0,049725 | 1,260425 | +1,47 % | % |
| Estiércol fresco | Materia seca | 2 | 14,230171 | 0,620520 | 3 | 12,969746 | 0,049725 | 1,260425 | −8,86 % | % |
| Estiércol fresco | Cenizas | 2 | 14,123008 | 0,667661 | 3 | 16,451095 | 1,866611 | 2,328087 | +16,48 % | % base seca |
| Estiércol fresco | Sólidos volátiles | 2 | 85,876992 | 0,667661 | 3 | 83,548905 | 1,866611 | 2,328087 | −2,71 % | % base seca |
| Estiércol precompostado | N total | 2 | 2,425000 | 0,021213 | 3 | 2,583333 | 0,211266 | 0,158333 | +6,53 % | % masa |
| Estiércol precompostado | Carbono | 2 | 35,745000 | 0,077782 | 3 | 36,866667 | 0,840079 | 1,121667 | +3,14 % | % masa |
| Estiércol precompostado | Humedad | 2 | 77,593045 | 3,926927 | 3 | 81,071068 | 0,897946 | 3,478023 | +4,48 % | % |
| Estiércol precompostado | Materia seca | 2 | 22,406955 | 3,926927 | 3 | 18,928932 | 0,897946 | 3,478023 | −15,52 % | % |
| Estiércol precompostado | Cenizas | 2 | 29,041353 | 4,255965 | 3 | 20,909650 | 1,231713 | 8,131703 | −28,00 % | % base seca |
| Estiércol precompostado | Sólidos volátiles | 2 | 70,958647 | 4,255965 | 3 | 79,090350 | 1,231713 | 8,131703 | +11,46 % | % base seca |
| Aguas verdes | Densidad | 2 | 1,000000 | 0,000000 | 3 | 1,000000 | 0,000000 | 0,000000 | 0,00 % | g/mL |
| Purines | Densidad | 2 | 1,000000 | 0,000000 | 3 | 1,000000 | 0,000000 | 0,000000 | 0,00 % | g/mL |

Estos resultados son descriptivos por jornada y no constituyen una integración temporal ni sustituyen parámetros del modelo.

## N de aguas verdes y purines

No se calculó una diferencia porcentual entre M1 y M2 para N de líquidos.

| Jornada | Material | Resultado conservado | Método registrado | Uso previsto |
|---|---|---|---|---|
| M1 | Aguas verdes | N amoniacal, N nítrico y N ureico, por separado, en mg/L | Especiación | Solo trazabilidad |
| M1 | Purines | N amoniacal, N nítrico y N ureico, por separado, en mg/L | Especiación | Solo trazabilidad |
| M2 | Aguas verdes | N total en % masa | Kjeldahl | Elegible |
| M2 | Purines | N total en % masa | Kjeldahl | Elegible |

M1 no se sumó, convirtió ni transformó para crear un N total artificialmente comparable. El método de M2 quedó registrado como Kjeldahl con la siguiente fuente metodológica proporcionada por el investigador: metodología oficial CIA para abonos líquidos, basada en 10 g de muestra, digestión húmeda con H₂SO₄ mediante Kjeldahl, volumen final de 250 mL y determinación colorimétrica con FIA.

## Validación automática

`scripts/validate_sampling_ingestion.py` confirmó:

- M1: dos muestras compuestas por material;
- M2: tres muestras compuestas por material;
- sólidos: tres submuestras por muestra y variable;
- LASA: tres réplicas analíticas de N por muestra;
- ausencia de claves duplicadas;
- ausencia de fórmulas de Excel en la columna de valores;
- unidades únicas dentro de cada grupo jornada–material–variable–método;
- N de líquidos M1 como especiación y solo trazabilidad;
- N de líquidos M2 como Kjeldahl y elegible.

Resultado: `VALIDACIÓN CORRECTA: 176 observaciones y 35 resúmenes intrajornada`.

## Datos no interpretables inequívocamente

- La fecha exacta de muestreo M2 no aparece en todos los informes; se conservaron las fechas documentales disponibles sin convertir automáticamente la recepción en fecha de muestreo.
- El laboratorio emisor de los libros gravimétricos no está identificado inequívocamente; se registró `no documentado`.
- Los reportes CIA no indican inequívocamente si los porcentajes de N y C del precompostado están expresados en base seca o fresca. La aclaración posterior confirma Dumas después de secar la muestra a 80 °C durante 48 h y que el CIA no determinó humedad a 105 °C; esta preparación no basta para definir la base formal final reportada, por lo que ambas condiciones se conservan separadamente en la metadata.
- El libro gravimétrico M2 disponible aún muestra la columna vacía `CRISOL ID`, pese a que se informó su eliminación. Esto no afecta el lector basado en encabezados.
- No se asignó réplica analítica a los resultados CIA cuando el informe solo presenta una fila por muestra compuesta.

## Archivos creados

- `scripts/sampling_ingestion_config.py`
- `scripts/build_sampling_ingestion.py`
- `scripts/validate_sampling_ingestion.py`
- `processed/muestreos_observaciones_normalizadas.csv`
- `processed/muestreos_resumen_intrajornada.csv`
- `auditoria_ingestion_m1_m2.md`

## Archivos modificados

- `scripts/extract_analysis_results.py`
- `scripts/compute_sample_parameters.py`
- `DICCIONARIO_TRAZABILIDAD_VARIABLES.md`
- `README_METODOLOGIA.md`

`DECISIONES_METODOLOGICAS_TFG.md` no se modificó. Conviene incorporar en una fase documental aprobada la decisión sobre la no comparabilidad del N líquido M1 y la elegibilidad de M2 por Kjeldahl.

## Verificación de no impacto en el ACV

Hashes SHA-256 previos a la implementación:

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

No se regeneraron emisiones, impactos, tablas de tesis, gráficos ni documentos académicos. El documento maestro no fue usado como salida ni modificado.

`git diff --check` terminó con código 0 y sin errores.

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
?? auditoria_ingestion_m1_m2.md
?? auditoria_integracion_muestreo_2.md
?? processed/muestreos_observaciones_normalizadas.csv
?? processed/muestreos_resumen_intrajornada.csv
?? scripts/build_sampling_ingestion.py
?? scripts/sampling_ingestion_config.py
?? scripts/validate_sampling_ingestion.py
```

Los cinco archivos de M2 y `auditoria_integracion_muestreo_2.md` ya estaban sin rastrear al inicio de esta fase. No se hizo commit ni push.
