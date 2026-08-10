# Auditoría de aclaraciones CIA sobre precisión y base de N/C

## Alcance

Esta fase registra dos aclaraciones oficiales del CIA y ajusta únicamente metadata, documentación y la escritura numérica de la capa multijornada. No se modificaron el modelo ACV, ecuaciones, parámetros operativos, emisiones, impactos, masas por etapa, productos finales ni documentos Word.

## 1. Aclaraciones oficiales del CIA

### Decimales de N en aguas verdes y purines

> “Las cifras significativas serían hasta el segundo decimal, así como se observa en el reporte. La cantidad de decimales que se observan en la celda son los totales que lee el equipo.”

Para evitar la ambigüedad del término “cifras significativas”, la regla técnica del proyecto se registra así: **el CIA reporta el resultado hasta el segundo decimal, tal como aparece en el informe**. Los decimales adicionales almacenados en la celda corresponden a la lectura conservada por el equipo, pero no representan por sí mismos mayor precisión analítica formal.

### Preparación para N/C del estiércol precompostado

> “El porcentaje de N se determinó en la muestra secada a 80 °C durante 48 horas. No se determinó el % de humedad a 105 °C debido a que no se solicitó.”

Esta aclaración complementa la metodología CIA ya documentada para Dumas: después del secado a 80 °C durante 48 h, la muestra se muele, se pasa por criba de 1 mm, se pesan aproximadamente 80–100 mg y se analiza en un autoanalizador Elementar Vario Macro Cube mediante combustión seca.

## 2. Política adoptada de precisión y redondeo

La política registrada en `DECISIONES_METODOLOGICAS_TFG.md` y en la configuración de ingestión es:

1. conservar los valores numéricos completos disponibles en las celdas fuente;
2. calcular observaciones y resúmenes con esos valores, sin redondeo previo;
3. aplicar el redondeo únicamente al presentar resultados finales;
4. respetar que el CIA reporta hasta el segundo decimal;
5. no atribuir a los decimales adicionales mayor precisión analítica formal;
6. no reemplazar por `0,01 %` valores internos distintos aunque el informe los muestre con el mismo redondeo.

Por ejemplo, la capa conserva por separado valores como `0.00886066666666667` y `0.0137733333333333`, en lugar de sustituirlos anticipadamente por `0,01`.

## 3. Auditoría del redondeo en la capa nueva

La agregación en `scripts/build_sampling_ingestion.py` ya utilizaba los valores `float` completos para:

- promediar réplicas dentro de cada muestra compuesta;
- calcular promedios de jornada;
- calcular desviaciones estándar, mínimos y máximos.

Se detectó una limitación exclusivamente al escribir los CSV: los valores `float` se formateaban con `.10g`. Esto no alteraba el cálculo efectuado en memoria, pero truncaba la representación persistida e impedía conservar todos los decimales recuperados del archivo fuente.

Se sustituyó ese formato por la escritura decimal reversible estándar de Python. No se cambió ninguna ecuación ni regla estadística. La comparación contra la versión anterior mostró:

| Archivo | Filas | Campos numéricos comparados | Diferencia absoluta máxima atribuible al antiguo formato |
|---|---:|---:|---:|
| `processed/muestreos_observaciones_normalizadas.csv` | 176 | 543 | 4,97 × 10⁻⁹ |
| `processed/muestreos_resumen_intrajornada.csv` | 35 | 263 | 4,38 × 10⁻⁹ |

Las diferencias son de representación por la antigua limitación a 10 cifras, no de ecuaciones, jerarquía o fuentes.

## 4. Preparación CIA frente a humedad y materia seca del TFG

Se documentan como procedimientos distintos:

### Caracterización gravimétrica del TFG

- aproximadamente 10 g de muestra;
- 105 °C;
- hasta masa constante o durante el tiempo experimental establecido;
- finalidad: calcular humedad y materia seca del proyecto.

### Preparación CIA para N/C

- secado a 80 °C durante 48 h;
- molienda y criba de 1 mm;
- pesada aproximada de 80–100 mg;
- finalidad: preparación para N/C por Dumas;
- el CIA no determinó humedad a 105 °C porque no fue solicitada.

Ambos resultados pueden coexistir como caracterizaciones del material, pero no proceden de la misma preparación. La materia seca del TFG a 105 °C no se usa automáticamente para convertir los porcentajes CIA de N/C.

## 5. Metadata final para N/C del precompostado

Para M1 y M2 se conserva:

```text
metodo_analitico = Dumas (combustión seca)
condicion_muestra = Muestra secada a 80 °C durante 48 h; el CIA no determinó humedad a 105 °C porque no fue solicitada.
base_medicion = muestra previamente secada a 80 °C durante 48 h; base final del porcentaje no especificada formalmente por el reporte
```

La formulación distingue la condición física de la muestra analizada de la base metrológica de expresión. No se etiqueta como masa fresca ni se afirma formalmente base seca. Los valores de N y C no cambiaron.

## 6. Metadata final para N líquido M2

Las seis observaciones de N total M2 conservan:

- `metodo_analitico = Kjeldahl`;
- `uso_modelo = elegible`;
- unidad original `% masa`;
- lectura numérica completa de la celda;
- una `nota_precision_reporte` que explica la presentación hasta el segundo decimal y la ausencia de precisión formal adicional.

La política de líquidos M1 no cambió: sus especies permanecen separadas, por especiación y con `uso_modelo = solo_trazabilidad`.

## 7. Archivos modificados y creado

Se creó:

- `auditoria_aclaraciones_cia_precision_base_n.md`.

Se modificaron:

- `DECISIONES_METODOLOGICAS_TFG.md`;
- `README_METODOLOGIA.md`;
- `DICCIONARIO_TRAZABILIDAD_VARIABLES.md`;
- `scripts/sampling_ingestion_config.py`;
- `scripts/extract_analysis_results.py`;
- `scripts/validate_sampling_ingestion.py`;
- `scripts/build_sampling_ingestion.py`, únicamente para eliminar el formateo `.10g` al escribir;
- `auditoria_base_n_precompostado.md`;
- `auditoria_ingestion_m1_m2.md`;
- `processed/muestreos_observaciones_normalizadas.csv`;
- `processed/muestreos_resumen_intrajornada.csv`.

No se modificó `scripts/compute_sample_parameters.py` en esta fase.

## 8. Validación y conteos

La regeneración produjo:

- 176 observaciones normalizadas;
- 35 resúmenes intrajornada.

El validador confirmó:

- valores internos completos de N líquido M2;
- política de reporte hasta el segundo decimal;
- N/C por Dumas después de secado a 80 °C durante 48 h;
- ausencia de afirmación de base fresca o seca formal;
- separación entre condición de muestra y base de medición;
- líquidos M1 como especiación y solo trazabilidad;
- líquidos M2 como Kjeldahl y elegibles;
- jerarquía y conteos M1/M2 sin cambios.

## 9. Cuestiones pendientes

- El CIA no ha expresado formalmente los porcentajes de N/C como “base seca” o “base fresca”; debe mantenerse la formulación prudente adoptada.
- Una futura presentación en tablas o documentos deberá implementar el redondeo al segundo decimal sin modificar los datos internos. Esos productos no se regeneraron en esta fase.
- No se ha aprobado ninguna conversión del N/C CIA mediante la materia seca gravimétrica del TFG.

## 10. Protección del ACV

Hashes SHA-256 antes de la fase:

| Archivo | SHA-256 antes |
|---|---|
| `processed/ACV_resumen_emisiones.csv` | `A904EDF4F77D21F99D3683E24A91FD475B702CE711D4100A2E6643B80B2C0C8B` |
| `processed/acv_impacto_por_etapa_escenario.csv` | `CE164CD555B230CF96BDBE6DAB084D6D0C48027B0AB1B79760E93FC444186181` |
| `processed/acv_impacto_total_por_escenario.csv` | `7040A111CC5AE067C9510A83262D653BB96CD4F305994086821316EF147E038B` |
| `processed/masa_total_escenario_etapa.csv` | `FA243E995D1F013D521371A59AB2404D35BC0C7A410F2780DC0E8E61CD6B2596` |

Hashes SHA-256 después de la fase:

| Archivo | SHA-256 después | Resultado |
|---|---|---|
| `processed/ACV_resumen_emisiones.csv` | `A904EDF4F77D21F99D3683E24A91FD475B702CE711D4100A2E6643B80B2C0C8B` | Idéntico |
| `processed/acv_impacto_por_etapa_escenario.csv` | `CE164CD555B230CF96BDBE6DAB084D6D0C48027B0AB1B79760E93FC444186181` | Idéntico |
| `processed/acv_impacto_total_por_escenario.csv` | `7040A111CC5AE067C9510A83262D653BB96CD4F305994086821316EF147E038B` | Idéntico |
| `processed/masa_total_escenario_etapa.csv` | `FA243E995D1F013D521371A59AB2404D35BC0C7A410F2780DC0E8E61CD6B2596` | Idéntico |

El SHA-256 del documento maestro permaneció idéntico: `98ABDE3EC5A22FA052EFA595AAC26729EA070EACA670BDC41097C4BF2E5E327C`.

Las consultas limitadas a `MASTER_escrito/`, `outputs/`, archivos Word y las cuatro salidas ACV no mostraron cambios. `git diff --check` terminó con código 0.

Estado final de Git:

```text
 M DECISIONES_METODOLOGICAS_TFG.md
 M DICCIONARIO_TRAZABILIDAD_VARIABLES.md
 M README_METODOLOGIA.md
 M auditoria_base_n_precompostado.md
 M auditoria_ingestion_m1_m2.md
 M processed/muestreos_observaciones_normalizadas.csv
 M processed/muestreos_resumen_intrajornada.csv
 M scripts/build_sampling_ingestion.py
 M scripts/extract_analysis_results.py
 M scripts/sampling_ingestion_config.py
 M scripts/validate_sampling_ingestion.py
?? auditoria_aclaraciones_cia_precision_base_n.md
```

No se hizo commit ni push.
