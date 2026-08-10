# Auditoría para la integración del segundo muestreo experimental

## Alcance y criterio de auditoría

Esta fase fue exclusivamente de lectura, inventario y diseño de ingestión. No se ejecutaron los extractores ni se recalcularon parámetros, emisiones o impactos. Tampoco se regeneraron tablas, gráficos o documentos de tesis. La revisión se realizó en la rama `integrar-muestreo-2`.

El estado inicial de Git contenía únicamente la carpeta nueva del segundo muestreo como archivo no rastreado:

```text
?? "Academic_documents/resultados CIA y LASA muestreo 2/"
```

En este informe se distingue entre:

- **muestra de campo o repetición biológica**: material identificado de forma independiente, por ejemplo `Fresco 2,1` o `PRECOMPOSTADO - 2-1`;
- **réplica analítica o submuestra**: determinación repetida dentro de una misma muestra de campo, por ejemplo las réplicas 1, 2 y 3 del informe LASA o los identificadores `A11`, `A12` y `A13`;
- **jornada de muestreo**: campaña M1 o M2. Cuando el archivo no aporta una fecha inequívoca de recolección, no se equipara automáticamente la fecha de recepción con la fecha de muestreo.

## 1. Inventario de archivos de M1 y M2

### Muestreo 1

| Archivo | Extensión y tamaño | Origen identificable | Material y jornada | Repeticiones observables | Hojas o estructura general |
|---|---:|---|---|---|---|
| `129-25 Contenido de nitrogeno - firmado.pdf` | PDF; 361 648 bytes; 2 páginas | LASA, Escuela de Química, UCR | Estiércol fresco; muestreo indicado el 10/11/2025 | 2 muestras de campo (`A. Fresco 2` y `B. Fresco 3`), cada una analizada por triplicado | Informe firmado con identificación de muestras, resultados, método e incertidumbre; segunda página con procedimiento Kjeldahl |
| `AO-00476-00477 (97600) ESCUELA INGENIERIA y de BIOSISTEMAS.xlsx` | XLSX; 161 228 bytes | Laboratorio de Suelos y Foliares, Ciudad de la Investigación (CIA), UCR | Estiércol precompostado; M1; recepción 10/11/2025 | 2 muestras (`SOL: PRECOMPOSTADO 1` y `2`); el reporte no presenta réplicas analíticas internas | 3 hojas: `25-00476 - 25-00477` (60 × 24), `Hoja3` (60 × 24) y `Hoja4` (76 × 24). Solo la primera contiene resultados |
| `AO-00478-00479 (97601) ESCUELA INGENIERIA y de BIOSISTEMAS.xlsx` | XLSX; 172 343 bytes | CIA, UCR | Aguas verdes; M1; recepción 10/11/2025 | 2 muestras (`LIQ: AGUA VERDE 1` y `2`); sin réplicas analíticas internas visibles | 3 hojas: `25-00478 - 25-00479(2)` (60 × 25), `Hoja3` (60 × 24) y `Hoja4` (60 × 24). Solo la primera contiene resultados |
| `AO-00504-00505 (97679) MATEO CERDAS BARBOZA.xlsx` | XLSX; 174 557 bytes | CIA, UCR | Purines; M1; recepción 17/11/2025 | 2 muestras (`LIQ: PURINES 1` y `2`); sin réplicas analíticas internas visibles | 3 hojas: `25-00504 - 25-00505` (59 × 24), `Hoja3` (60 × 24) y `Hoja4` (60 × 24). Solo la primera contiene resultados |
| `Material_laboratorio_copy_to_work_python.xlsx` | XLSX; 221 921 bytes | Hoja de trabajo experimental; el archivo no identifica inequívocamente un laboratorio emisor | Estiércol fresco y precompostado; M1 | 2 muestras por material y 3 submuestras por muestra: 6 determinaciones por material en cada bloque | 3 hojas: `Procedure` (21 × 19), `Data` (57 × 14) y `Equipement` (14 × 3). Incluye procedimiento, masas, fórmulas, equipo y disposición espacial |
| `Resumen.xlsx` | XLSX; 10 226 bytes | Archivo derivado; laboratorio no indicado | Resumen de los cuatro tipos de material de M1 | No conserva las repeticiones: una fila resumida por material | 1 hoja: `Hoja1` (5 × 5), con N total, sólidos volátiles, humedad y materia seca según disponibilidad |

### Muestreo 2

| Archivo | Extensión y tamaño | Origen identificable | Material y jornada | Repeticiones observables | Hojas o estructura general |
|---|---:|---|---|---|---|
| `043-26 Contenido de Nitrogeno-firmado.pdf` | PDF; 286 276 bytes; 2 páginas | LASA, Escuela de Química, UCR | Estiércol fresco; M2 por identificadores `Fresco 2,1`, `2,2` y `2,3`; recepción 23/07/2026 | 3 muestras de campo (`A`, `B`, `C`), cada una analizada por triplicado | Informe firmado con resultados e incertidumbre; segunda página con procedimiento Kjeldahl |
| `AO-00330-00332 (100750) SEDE DEL ATLANTICO.xlsx` | XLSX; 650 018 bytes | CIA, UCR | Aguas verdes; M2; recepción 23/07/2026 | 3 muestras: `LIQ: AGUAS VERDES - 2-1`, `2-2` y `2-3`; sin réplicas analíticas internas visibles | 3 hojas: `26-00330 - 26-00332` (472 × 28), `Hoja2` (472 × 28) e `INTERPRETACION` (54 × 15). Solo la primera contiene resultados del lote |
| `AO-00333-00335 (100751) SEDE DEL ATLANTICO.xlsx` | XLSX; 650 406 bytes | CIA, UCR | Estiércol precompostado; M2; recepción 23/07/2026 | 3 muestras: `SOL: PRECOMPOSTADO - 2-1`, `2-2` y `2-3`; sin réplicas analíticas internas visibles | 3 hojas: `26-00333 - 26-00335` (472 × 28), `Hoja2` (472 × 28) e `INTERPRETACION` (54 × 15) |
| `AO-00337-00339 (100788) SEDE DEL ATLANTICO.xlsx` | XLSX; 585 511 bytes | CIA, UCR | Purines; M2; recepción 27/07/2026 | 3 muestras: `LIQ: PURINES - 2-1`, `2-2` y `2-3`; sin réplicas analíticas internas visibles | 3 hojas: `26-00337 - 26-00339` (472 × 28), `Hoja2` (472 × 28) e `INTERPRETACION` (54 × 15) |
| `muestreo2_solidos_volatiles.xlsx` | XLSX; 223 556 bytes | Hoja de trabajo experimental; el archivo no identifica inequívocamente un laboratorio emisor | Estiércol fresco y precompostado; M2 | 3 muestras por material y 3 submuestras por muestra: 9 determinaciones por material en cada bloque | 3 hojas: `Procedure` (21 × 19), `Data` (67 × 15) y `Equipement` (27 × 2). Incluye masas y fórmulas de secado e incineración |

No se encontraron subcarpetas ni otros archivos dentro de las dos carpetas auditadas.

## 2. Comparación estructural entre M1 y M2

### Informes CIA

Los formatos no son idénticos y no deben tratarse como una plantilla fija única.

| Elemento | M1 | M2 | Implicación para la ingestión |
|---|---|---|---|
| Nombre de hoja con resultados | Intervalo de muestras de 2025; además `Hoja3` y `Hoja4` vacías | Intervalo de muestras de 2026; además `Hoja2` e `INTERPRETACION` | Debe localizarse la tabla por contenido (`ID USUARIO`), no por nombre de hoja |
| Dimensiones de la hoja principal | Aproximadamente 59–60 filas y 24–25 columnas | 472 filas y 28 columnas | No es seguro usar dimensiones o números de hoja como criterio |
| Fila del encabezado de datos | Fila 22 | Fila 17 | Las posiciones fijas de fila fallan entre jornadas |
| Columna de identificación de laboratorio | D (`IDLAB`) | D (`ID LAB`) | El significado se conserva, pero cambia la ortografía |
| Posición del análisis y metadatos | Bloque derecho alrededor de J–O | Bloques alrededor de K–N y U–Z | Las fechas y el tipo de análisis deben buscarse por etiqueta normalizada |
| Identificación de muestras | Nombre de material seguido por `1` o `2` | Nombre de material seguido por `2-1`, `2-2` o `2-3` | M2 incorpora la jornada en el identificador visible; M1 no lo hace de forma equivalente |
| N de líquidos | Componentes `N-NH₄⁺`, `N-NO₃⁻`, `N-ureico` en mg/L y densidad en g/mL | Una columna `N` bajo análisis `N_Total`, en `% masa`, más densidad en g/mL | Cambian variable, unidad, método declarado y necesidad de conversión |
| N de precompostado | Columnas `N` y `C`, `% masa` | Columnas `C`, `N` y `C/N`, `%` | Cambia el orden de columnas y aparece la relación C/N |
| Número de muestras del lote | 2 | 3 | El lector no debe asumir dos filas de resultados |

Las hojas auxiliares vacías o de interpretación contienen encabezados potencialmente confundibles con la tabla real. La selección debe exigir filas de resultados válidas y no limitarse a encontrar el primer encabezado.

### Hojas de trabajo de humedad, materia seca, cenizas y sólidos volátiles

M1 y M2 conservan los nombres `Procedure`, `Data` y `Equipement`, y el principio de identificación A = estiércol fresco, B = estiércol precompostado e I = bloque de incineración. Sin embargo, la estructura de `Data` cambió:

- M1 tiene 14 columnas; M2 tiene 15 porque añadió `CRISOL ID` como columna B.
- Por ese desplazamiento, las masas que en M1 están en B, C y E pasan en M2 a C, D y F.
- El bloque de incineración comienza en la fila 16 de M1 y en la fila 21 de M2.
- M1 contiene `A11`–`A23` y `B11`–`B23`; M2 añade el tercer grupo `A31`–`A33` y `B31`–`B33`. El mismo patrón aparece como `AI..` y `BI..` en incineración.
- Las unidades y bases declaradas son comparables: masas en g, humedad y materia seca en porcentaje de masa fresca, y cenizas/sólidos volátiles en porcentaje de la submuestra seca.
- El procedimiento declarado es equivalente: secado de aproximadamente 10 g a 105 °C durante 16 horas o hasta masa constante; incineración de aproximadamente 1 g de masa seca a 575 °C. La hoja M1 registra seis horas de incineración en sus notas de equipo, aunque la descripción general indica cuatro horas; M2 conserva la descripción general, pero sus notas visibles no documentan con igual detalle la ejecución.

Se detectaron indicios de plantilla copiada que impiden confiar en los resúmenes internos de M2 sin validación:

- `Procedure` declara 3 muestras frescas y 3 precompostadas, pero las filas de procedimiento todavía usan `Cantidad muestras = 4`, `Cantidad de réplicas = 3` y textos que hablan de 12 muestras.
- Las fórmulas de resumen general en N2/O2 y N11/O11 promedian solo los resúmenes de los grupos 1 y 2; no incorporan el grupo 3.
- Varias celdas de “monitor a constante” de M2 repiten números presentes en M1 o presentan secuencias que requieren confirmación. Estas celdas no deben usarse automáticamente como mediciones válidas hasta que el investigador confirme su procedencia.
- En el bloque de incineración de M2, la columna del monitor a masa constante está vacía salvo en la primera fila, aunque la fórmula de diferencia se extiende al resto.

El archivo `Resumen.xlsx` de M1 no tiene equivalente en M2. Además, por haber perdido la identidad de las réplicas y contener fórmulas/resúmenes, no es una fuente primaria adecuada para la ingestión multijornada.

## 3. Diferencias encontradas

1. M2 pasa de dos a tres muestras independientes por tipo de material.
2. La plantilla CIA cambia nombres de hojas, filas, columnas, dimensiones y ortografía de encabezados.
3. El N de líquidos cambia de tres especies expresadas en mg/L en M1 a una determinación rotulada `N_Total` y expresada en porcentaje de masa en M2.
4. El N de precompostado mantiene porcentaje, pero cambia el orden de C y N y añade C/N.
5. El libro experimental de M2 añade una columna y un tercer grupo de muestras; por tanto, el mapa de celdas de M1 ya no aplica.
6. M2 no incluye un archivo resumen equivalente al de M1.
7. Los identificadores M2 codifican explícitamente la jornada con `2-`; los identificadores M1 dependen de la carpeta, las fechas y el contexto del archivo.
8. La fecha de recepción de los purines M2 (27/07/2026) difiere de la de los otros lotes M2 (23/07/2026). Los archivos no permiten concluir por sí solos si se trata de distinta fecha de recolección o solo de entrega posterior.

## 4. Número e identificación de repeticiones

### M1

- **Estiércol fresco, N por LASA:** 2 muestras de campo (`Fresco 2` y `Fresco 3`), con 3 réplicas analíticas por muestra. Total: 6 resultados analíticos trazables a dos muestras.
- **Estiércol fresco, propiedades gravimétricas:** 2 muestras (`A1` y `A2` implícitas), con 3 submuestras cada una (`A11`–`A13`, `A21`–`A23`). Total: 6 determinaciones por bloque.
- **Estiércol precompostado, N por CIA:** 2 muestras (`PRECOMPOSTADO 1` y `2`), sin réplica analítica interna informada.
- **Estiércol precompostado, propiedades gravimétricas:** 2 muestras (`B1`, `B2`) con 3 submuestras cada una. Total: 6 determinaciones por bloque.
- **Aguas verdes y purines, N por CIA:** 2 muestras por material, sin réplica analítica interna informada.

### M2

- **Estiércol fresco, N por LASA:** 3 muestras de campo (`Fresco 2,1`, `2,2`, `2,3`), con 3 réplicas analíticas por muestra. Total: 9 resultados analíticos trazables a tres muestras.
- **Estiércol fresco, propiedades gravimétricas:** 3 muestras (`A1`, `A2`, `A3`) con 3 submuestras cada una (`A11`–`A33`). Total: 9 determinaciones por bloque.
- **Estiércol precompostado, N por CIA:** 3 muestras (`2-1`, `2-2`, `2-3`), sin réplica analítica interna informada.
- **Estiércol precompostado, propiedades gravimétricas:** 3 muestras (`B1`, `B2`, `B3`) con 3 submuestras cada una. Total: 9 determinaciones por bloque.
- **Aguas verdes y purines, N por CIA:** 3 muestras por material, sin réplica analítica interna informada.

Por tanto, la expectativa de **tres repeticiones en M2 se confirma en el nivel de muestras de campo** para los cuatro materiales. En los ensayos gravimétricos y en el N de estiércol fresco existen además tres réplicas/submuestras analíticas dentro de cada muestra.

La trazabilidad a material y jornada es inequívoca si se conserva conjuntamente la carpeta, el archivo, la hoja y el identificador original. No es inequívoca si se retiene solo `A11` o `B11`, porque esos códigos se repiten entre M1 y M2. Tampoco debe inferirse la fecha exacta de recolección de M2 a partir de la fecha de recepción sin confirmación externa.

## 5. Variables analíticas disponibles

| Material | M1 | M2 | Observaciones |
|---|---|---|---|
| Estiércol fresco | Humedad, materia seca, cenizas, sólidos volátiles; N total por Kjeldahl | Humedad, materia seca, cenizas, sólidos volátiles; N total por Kjeldahl | Las variables son comparables conceptualmente, pero el libro gravimétrico cambió de columnas y cantidad de muestras |
| Estiércol precompostado | Humedad, materia seca, cenizas, sólidos volátiles; N y C | Humedad, materia seca, cenizas, sólidos volátiles; C, N y relación C/N | El reporte CIA rotula el análisis como `CN`; no se encontró una descripción del método de N en esos XLSX |
| Aguas verdes | N ureico, N amoniacal, N nítrico y densidad; el archivo deriva N total por suma | N rotulado como total y densidad | M1 está en mg/L por especie; M2 informa N en `% masa`. M2 no aporta en el libro una descripción del método |
| Purines | N amoniacal, N nítrico, N ureico y densidad; el archivo deriva N total por suma | N rotulado como total y densidad | M1 está en mg/L por especie; M2 informa N en `% masa`. M2 no aporta en el libro una descripción del método |

No se observaron determinaciones de humedad, materia seca, cenizas o sólidos volátiles para aguas verdes o purines en ninguna de las dos jornadas. Para los sólidos, cenizas y sólidos volátiles proceden de las hojas de trabajo experimentales; el N procede de LASA para estiércol fresco y de CIA para precompostado.

## 6. Comparación del análisis de N en líquidos

Los archivos confirman que M1 empleó un **esquema de especiación** para líquidos:

- aguas verdes: N ureico, N-NH₄⁺ y N-NO₃⁻, cada uno en mg/L, más densidad;
- purines: N-NH₄⁺, N-NO₃⁻ y N ureico, cada uno en mg/L, más densidad;
- el “N total” visible es una fórmula de suma incorporada al libro, no una columna primaria de una determinación total única.

Los informes CIA de M2 muestran una sola variable `N`, el análisis `N_Total`, unidad `% masa` y densidad. Esto demuestra que **la estructura analítica es distinta de M1** y que no se trata del mismo esquema explícito de especiación.

Sin embargo, los archivos M2 de aguas verdes y purines **no mencionan Kjeldahl ni describen el método analítico**. El único archivo M2 que documenta explícitamente “Nitrógeno (total) por el método Kjeldahl” es `043-26 Contenido de Nitrogeno-firmado.pdf`, y sus muestras son tres muestras de **estiércol fresco**, no líquidos. Por ello, con la evidencia disponible no puede confirmarse documentalmente que el N de aguas verdes y purines M2 haya sido determinado por Kjeldahl.

La decisión metodológica de conservar M1 sin mezclarlo automáticamente con M2/M3 es coherente con la diferencia observable, pero antes de usar M2 como jornada elegible de N en líquidos se requiere solicitar o confirmar con CIA el método asociado a los reportes 100750 y 100788 (por ejemplo, certificado, procedimiento, alcance del ensayo o comunicación formal del laboratorio).

## 7. Limitaciones del extractor actual

### `scripts/extract_analysis_results.py`

- El directorio predeterminado está fijado a `Academic_documents/resultados CIA y LASA muestreo 1`. Puede recibir otra ruta manualmente, pero no descubre ni combina jornadas de forma controlada.
- Descubre todos los XLSX del directorio inmediato, pero no conserva `archivo_origen`, `hoja_origen` ni laboratorio.
- Selecciona la primera hoja que contenga `ID USUARIO`. La lógica tolera cambios de nombre de hoja y fila, pero podría seleccionar una hoja auxiliar con encabezado y sin resultados; no valida suficientemente la presencia de filas de muestra.
- Normaliza encabezados y evita varias posiciones fijas, lo cual es favorable para los informes CIA. No obstante, la lectura de unidades mediante propagación horizontal puede asignar unidades incorrectas cuando las celdas combinadas o la plantilla cambian.
- No conserva réplicas analíticas como registros independientes para los PDF. Para cada muestra LASA promedia inmediatamente las réplicas 1–3 y descarta el número de réplica y la incertidumbre.
- El lector PDF está codificado para muestras `A` y `B`, descripciones `Fresco` seguidas por un entero y una suposición de sufijos `2`/`3`. No admite la muestra `C` de M2 ni interpreta correctamente identificadores con coma (`2,1`, `2,2`, `2,3`).
- Solo contempla dos muestras en `replicas_by_sample` y solo asigna como máximo dos medianas en el mecanismo alternativo.
- La búsqueda del PDF usa un patrón textual específico y procesa únicamente el primer candidato.
- No registra el método analítico de forma separada. El texto `N total (Kjeldahl)` se incorpora únicamente como tipo de análisis para el PDF de estiércol fresco; los XLSX solo guardan la etiqueta general del reporte.
- No incluye `jornada_muestreo`. La fecha tampoco es completamente robusta: busca etiquetas de emisión/recepción y el PDF usa la fecha del informe, no necesariamente la fecha de recolección.
- `infer_treatment()` elimina solo un entero final separado por espacio. No normaliza de forma segura sufijos M2 como `- 2-1`, por lo que los grupos quedarían fragmentados por repetición.
- `build_treatment_summary()` promedia todas las filas del grupo directamente. Si se combinaran jornadas con distinto número de muestras, la jornada con más filas tendría mayor peso.
- Escribe directamente en `processed`, por lo que no existe un modo de auditoría o salida intermedia que evite tocar los datos finales.
- Puede incorporar como resultados libros auxiliares como el resumen o la hoja gravimétrica si encuentra una tabla compatible, sin una clasificación explícita del tipo de fuente.

### `scripts/compute_sample_parameters.py`

- Está completamente fijado al libro M1 `Material_laboratorio_copy_to_work_python.xlsx` y a `xl/worksheets/sheet2.xml`.
- Usa posiciones fijas de columnas diseñadas para M1. La columna nueva B de M2 desplaza las masas y produciría lecturas incorrectas o pérdida de registros.
- Recorre un intervalo fijo de filas 2–57 y depende de expresiones regulares específicas para `A00`, `B00`, `AI00` y `BI00`.
- La fecha de muestreo está fijada como `2025-11-10`.
- El código reconoce la muestra y la submuestra en el identificador, pero no conserva jornada, archivo, hoja, laboratorio o método.
- El resumen agrupa primero por los dos primeros caracteres y después por A/B. Esta arquitectura puede representar muestras y submuestras dentro de una jornada, pero no separa jornadas antes del resumen ni impide ponderación desigual al combinarlas.
- Genera de inmediato productos en `processed`, incluido un resultado de pérdida de masa consumido por el modelo. Por esta razón no debe ejecutarse sobre M2 durante la fase de ingestión sin desacoplar antes las capas de datos crudos, control de calidad, resumen intrajornada y parámetros aprobados para el modelo.

Sí es técnicamente posible incorporar `jornada_muestreo`, pero debe asignarse durante la ingestión desde una configuración explícita por carpeta/archivo y no inferirse únicamente del nombre visible de la muestra.

## 8. Propuesta de estructura normalizada

Se recomienda una tabla larga de observaciones, una fila por resultado primario, con los siguientes campos:

| Campo propuesto | Contenido |
|---|---|
| `jornada_muestreo` | Identificador estable (`M1`, `M2`, `M3`) |
| `fecha_muestreo` | Fecha real de recolección; nula si no está documentada |
| `fecha_recepcion` | Fecha de recepción del laboratorio |
| `fecha_analisis` | Fecha o intervalo de análisis cuando esté disponible |
| `tipo_material` | Vocabulario controlado: estiércol fresco, estiércol precompostado, aguas verdes, purines |
| `identificador_muestra` | Identificador normalizado único dentro de la jornada |
| `identificador_muestra_origen` | Texto exacto reportado por el laboratorio o la hoja de trabajo |
| `repeticion_muestra` | Número de muestra de campo dentro de la jornada |
| `replica_analitica` | Número de réplica/submuestra dentro de la muestra; nulo cuando no se informa |
| `nivel_observacion` | `muestra_campo`, `replica_analitica` o `resumen_reportado` |
| `variable` | Vocabulario controlado: humedad, materia seca, cenizas, sólidos volátiles, N total, N amoniacal, N nítrico, N ureico, C, densidad, etc. |
| `valor` | Valor numérico tal como se ingiere, sin promedio entre jornadas |
| `unidad` | Unidad normalizada y explícita |
| `base_medicion` | Masa fresca, masa seca, volumen u otra base |
| `incertidumbre` | Incertidumbre reportada, cuando exista |
| `estadistico_reportado` | Mediana, media u otro; nulo para observación primaria |
| `laboratorio` | LASA, CIA o `no_determinado` |
| `metodo_analitico` | Método documentado; `no_documentado` en vez de inferirlo |
| `archivo_origen` | Ruta relativa del archivo fuente |
| `hoja_origen` | Nombre de hoja o número de página |
| `celda_o_fila_origen` | Coordenada o referencia de la observación |
| `id_reporte_laboratorio` | Número de informe o reporte |
| `uso_modelo` | Estado controlado: `elegible`, `solo_trazabilidad`, `pendiente_aprobacion`, `excluido` |
| `motivo_uso_modelo` | Justificación metodológica del estado |
| `bandera_calidad` | Observaciones de validación, fórmula sospechosa, método pendiente, etc. |

La clave lógica recomendada es la combinación de jornada, material, muestra, réplica, variable, laboratorio e informe. Debe conservarse siempre el identificador original para permitir reconstruir el dato.

Conviene separar tres capas:

1. **ingestión cruda normalizada**, sin promedios ni conversiones destructivas;
2. **control de calidad y resúmenes intrajornada**, reproducibles y con conteos;
3. **tabla de parámetros aprobados para el modelo**, actualizada solo después de la aprobación metodológica.

## 9. Propuesta de integración estadística de M2

No se calcularon valores finales en esta auditoría.

### Sólidos

1. Mantener cada réplica analítica como observación primaria.
2. Resumir primero las tres réplicas analíticas dentro de cada muestra de campo, usando un estimador predefinido y conservando dispersión, tamaño de muestra y banderas de calidad.
3. Resumir después las muestras de campo dentro de cada jornada para cada material y variable.
4. Integrar M1, M2 y eventualmente M3 a partir de los estimadores de jornada, asignando igual peso a cada jornada cuando el diseño las considere comparables.
5. Como análisis de sensibilidad, comparar el promedio no ponderado de jornadas con un modelo jerárquico o de efectos mixtos si hay suficientes jornadas. No agrupar todas las réplicas crudas en un promedio simple.
6. Antes de integrar M2, resolver las celdas de monitor a masa constante y las fórmulas de resumen incompletas. Los cálculos deben reconstruirse desde masas primarias validadas, no desde los resúmenes defectuosos del libro.

### Líquidos

1. Conservar todos los datos M1 y su especiación como registros de trazabilidad.
2. Marcar provisionalmente el N de líquidos M1 como `solo_trazabilidad` para la caracterización representativa futura, sin eliminarlo.
3. Marcar M2 como `pendiente_aprobacion` hasta confirmar documentalmente el método de los reportes CIA 100750 y 100788.
4. Si se confirma que M2 y M3 usan el método aprobado y son comparables, obtener primero un resumen por material y jornada y luego integrar los estimadores de M2 y M3 con igual peso por jornada.
5. No mezclar automáticamente valores de especiación en mg/L con N total en porcentaje. Cualquier armonización de unidades debe conservar valor, unidad, densidad, base y fórmula de conversión originales.

## 10. Riesgos y decisiones que requieren aprobación del investigador

1. Confirmar formalmente el método de N total usado por CIA en aguas verdes y purines M2; los archivos no demuestran que sea Kjeldahl.
2. Confirmar la fecha real de recolección de cada lote M2, especialmente por la diferencia entre fechas de recepción de purines y los demás materiales.
3. Confirmar la correspondencia entre códigos A/B de las hojas gravimétricas y las muestras nominadas en los informes LASA/CIA.
4. Definir si los tres identificadores M2 son repeticiones biológicas independientes, muestras compuestas o réplicas de otro nivel experimental.
5. Revisar con los cuadernos de laboratorio la procedencia de los valores de “monitor a constante” de M2 y corregir la documentación de tiempos de secado/incineración si corresponde.
6. Aprobar el estimador intramuestra e intrajornada (media o mediana) y el tratamiento de incertidumbre, valores atípicos y datos faltantes.
7. Aprobar que la integración entre jornadas use igual peso por jornada, salvo que el diseño experimental justifique otra ponderación.
8. Definir si C y C/N se conservarán solo como caracterización adicional o tendrán uso posterior.
9. Decidir si `uso_modelo` se administrará mediante una tabla de reglas versionada, evitando condiciones implícitas dentro del código.

## 11. Archivos exactos previstos para la siguiente fase

La implementación mínima y robusta requeriría modificar o crear exclusivamente los siguientes archivos antes de tocar el modelo:

- modificar `scripts/extract_analysis_results.py` para ingestión multijornada, trazabilidad de fuente, réplica, laboratorio y método;
- modificar `scripts/compute_sample_parameters.py` para descubrir las hojas por encabezado, mapear columnas por nombre y separar jornada/muestra/réplica;
- crear `scripts/sampling_ingestion_config.py` como registro explícito de jornadas, archivos, materiales, laboratorio, método documentado y elegibilidad; alternativamente, usar un archivo de configuración tabular con la misma función;
- crear `scripts/validate_sampling_ingestion.py` para validar claves únicas, unidades, conteos de muestras/réplicas, métodos y ausencia de mezcla entre jornadas;
- crear `processed/muestreos_observaciones_normalizadas.csv` como producto de ingestión cruda;
- crear `processed/muestreos_resumen_intrajornada.csv` como producto separado, sin actualizar todavía parámetros del modelo;
- actualizar `DICCIONARIO_TRAZABILIDAD_VARIABLES.md` y `README_METODOLOGIA.md` para documentar la arquitectura y las reglas aprobadas.

No sería necesario modificar en esa fase `generate_acv_parametros_escenario_etapa.py`, scripts de emisiones/impactos, tablas o documentos de tesis. La conexión con el modelo debe reservarse para una fase posterior y una aprobación explícita.

## 12. Estado de Git y verificación de no modificación

La comprobación final se ejecutó en la rama `integrar-muestreo-2`. `git diff --name-only` y `git diff --cached --name-only` no devolvieron archivos: no existen modificaciones rastreadas ni cambios preparados para commit. El estado detallado fue:

```text
?? "Academic_documents/resultados CIA y LASA muestreo 2/043-26 Contenido de Nitrogeno-firmado.pdf"
?? "Academic_documents/resultados CIA y LASA muestreo 2/AO-00330-00332 (100750) SEDE DEL ATLANTICO.xlsx"
?? "Academic_documents/resultados CIA y LASA muestreo 2/AO-00333-00335 (100751) SEDE DEL ATLANTICO.xlsx"
?? "Academic_documents/resultados CIA y LASA muestreo 2/AO-00337-00339 (100788) SEDE DEL ATLANTICO.xlsx"
?? "Academic_documents/resultados CIA y LASA muestreo 2/muestreo2_solidos_volatiles.xlsx"
?? auditoria_integracion_muestreo_2.md
```

La consulta de estado limitada a `processed`, `outputs`, `MASTER_escrito` y `scripts` no devolvió cambios. El SHA-256 observado para el documento maestro protegido fue `98ABDE3EC5A22FA052EFA595AAC26729EA070EACA670BDC41097C4BF2E5E327C`; no se abrió como salida ni se modificó durante esta fase. No se ejecutaron scripts generadores, no se hizo commit y no se hizo push.
