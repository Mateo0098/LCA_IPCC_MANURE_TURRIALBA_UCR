# Reporte de revisión de flujos A4 y B2

## Objetivo de la revisión

Se revisó la diferencia entre el flujo reportado como `Aguas verdes` y la `Masa equivalente total` en las etapas A4 y B2. La revisión se realizó sin modificar cálculos, tablas, figuras ni documentos Word.

Archivos revisados:

- `outputs/tablas_tesis/tabla_03_flujos_icv.csv`
- `outputs/tablas_tesis/tabla_04_parametros_modelo_acv.csv`
- `processed/agua_boniga_estadistica_descriptiva.csv`
- `processed/masa_total_escenario_etapa.csv`
- `processed/masa_total_factor_overrides.csv`
- `processed/acv_parametros_escenario_etapa.csv`
- `scripts/compute_masa_etapas_escenarios.py`
- `scripts/generate_thesis_tables.py`

No se usaron archivos con sufijo `antes_correccion_nitrogeno`.

## Origen de los valores base

El valor de aguas verdes usado en A4 y B2 proviene de `processed/agua_boniga_estadistica_descriptiva.csv`.

| Variable | Promedio medido | Duración de muestreo | Flujo por día | Flujo anual | Unidad | Archivo de origen |
|---|---:|---:|---:|---:|---|---|
| Agua | 684,954500 | 3,5 | 195,701286 | 71 430,969286 | L/año | `processed/agua_boniga_estadistica_descriptiva.csv` |
| Boñiga | 49,156279 | 3,5 | 14,044651 | 5 126,297667 | kg/año | `processed/agua_boniga_estadistica_descriptiva.csv` |

La equivalencia de agua se aplica como 1 L = 1 kg equivalente. Por tanto, 71 430,969 L/año de agua corresponden a 71 430,969 kg eq/año del componente líquido.

## Fórmula aplicada para masa equivalente total

La construcción de `processed/masa_total_escenario_etapa.csv` se realiza en `scripts/compute_masa_etapas_escenarios.py`. La función `apply_factor_overrides` aplica:

```text
masa_total_kg_eq = (boniga_kg + agua_l) * factor_masa_total
```

después de multiplicar previamente cada componente por sus factores de inclusión:

```text
boniga_kg = boniga_anual_kg * factor_boniga
agua_l = agua_anual_l * factor_agua
```

Los factores usados provienen de `processed/masa_total_factor_overrides.csv`.

## Tabla resumen de hallazgos

| Escenario | Etapa | Flujo reportado | Valor | Unidad | Archivo de origen | Explicación |
|---|---:|---|---:|---|---|---|
| A | 4 | Aguas verdes | 71 430,96929 | L/año | `processed/masa_total_escenario_etapa.csv`; `outputs/tablas_tesis/tabla_03_flujos_icv.csv` | Componente líquido de lavado incluido en A4 con `factor_agua = 1`. |
| A | 4 | Estiércol sólido o purín | 358,840837 | kg/año | `processed/masa_total_escenario_etapa.csv`; `outputs/tablas_tesis/tabla_03_flujos_icv.csv` | Fracción de boñiga fresca asignada a la línea de aguas verdes con `factor_boniga = 0,07`. |
| A | 4 | Masa equivalente total | 71 789,81012 | kg eq/año | `processed/masa_total_escenario_etapa.csv`; `outputs/tablas_tesis/tabla_03_flujos_icv.csv` | Suma del componente líquido convertido a kg equivalente y la fracción sólida asignada a la etapa. |
| B | 2 | Aguas verdes | 71 430,96929 | L/año | `processed/masa_total_escenario_etapa.csv`; `outputs/tablas_tesis/tabla_03_flujos_icv.csv` | Componente líquido de lavado incluido en B2 con `factor_agua = 1`. |
| B | 2 | Estiércol sólido o purín | 5 126,297667 | kg/año | `processed/masa_total_escenario_etapa.csv`; `outputs/tablas_tesis/tabla_03_flujos_icv.csv` | Masa anual total de boñiga fresca incluida en el escenario B con `factor_boniga = 1`. |
| B | 2 | Masa equivalente total | 76 557,26695 | kg eq/año | `processed/masa_total_escenario_etapa.csv`; `outputs/tablas_tesis/tabla_03_flujos_icv.csv` | Suma del componente líquido convertido a kg equivalente y la masa de boñiga fresca del purín. |

## Descomposición de A4

Etapa: A4, Aplicación de aguas verdes en campos de pastoreo.

Valores de `processed/masa_total_escenario_etapa.csv`:

- `agua_l` = 71 430,96929 L/año
- `boniga_kg` = 358,840837 kg/año
- `factor_agua_override` = 1
- `factor_boniga_override` = 0,07
- `factor_masa_total_override` = 1
- `masa_total_kg_eq` = 71 789,81012 kg eq/año

Cálculo:

```text
Masa equivalente total A4 = 71 430,96929 + 358,840837
Masa equivalente total A4 = 71 789,810127 kg eq/año
```

La diferencia observada:

```text
71 789,81012 - 71 430,96929 = 358,84083 kg eq/año
```

corresponde a la fracción de boñiga fresca asignada a A4. Esa fracción se obtiene como:

```text
5 126,297667 kg/año * 0,07 = 358,840837 kg/año
```

Relación con A3:

La etapa A3 reporta también 358,840837 kg eq/año. Por tanto, la diferencia entre la masa equivalente total de A4 y el volumen de aguas verdes corresponde al mismo componente sólido asignado a la línea de aguas verdes que aparece en A3 como almacenamiento. Es decir, A3 representa el almacenamiento de esa fracción y A4 representa su aplicación junto con el componente líquido.

## Descomposición de B2

Etapa: B2, Aplicación de purines en campo de pastoreo.

Valores de `processed/masa_total_escenario_etapa.csv`:

- `agua_l` = 71 430,96929 L/año
- `boniga_kg` = 5 126,297667 kg/año
- `factor_agua_override` = 1
- `factor_boniga_override` = 1
- `factor_masa_total_override` = 1
- `masa_total_kg_eq` = 76 557,26695 kg eq/año

Cálculo:

```text
Masa equivalente total B2 = 71 430,96929 + 5 126,297667
Masa equivalente total B2 = 76 557,266957 kg eq/año
```

La diferencia observada:

```text
76 557,26695 - 71 430,96929 = 5 126,29766 kg eq/año
```

corresponde a la masa anual de boñiga fresca incluida en el escenario B. En términos metodológicos, esta masa forma parte del purín aplicado en campo, entendido como mezcla de estiércol, orina, agua de lavado y otros residuos arrastrados.

Relación con B1:

La etapa B1 reporta 5 126,297667 kg eq/año. Por tanto, la diferencia entre la masa equivalente total de B2 y el volumen de aguas verdes corresponde al mismo componente de boñiga fresca almacenado en B1 y luego aplicado en B2 como parte del purín.

## Confirmación de la equivalencia 1 L = 1 kg

La equivalencia 1 L de agua = 1 kg equivalente se está aplicando correctamente al componente líquido:

- A4 incluye 71 430,96929 L/año de agua, equivalentes a 71 430,96929 kg eq/año.
- B2 incluye 71 430,96929 L/año de agua, equivalentes a 71 430,96929 kg eq/año.

La masa equivalente total no coincide exactamente con el volumen de aguas verdes porque no representa únicamente el componente líquido. Representa la suma del componente líquido más la fracción de boñiga o purín asignada a la etapa.

## Diagnóstico metodológico

Los valores son consistentes con la lógica de cálculo implementada:

- A4 = agua de lavado anual + 7 % de la boñiga fresca anual.
- B2 = agua de lavado anual + 100 % de la boñiga fresca anual.
- A4 tiene relación directa con A3, porque la diferencia de 358,840837 kg eq/año corresponde a la misma fracción sólida almacenada en A3.
- B2 tiene relación directa con B1, porque la diferencia de 5 126,297667 kg eq/año corresponde a la misma masa de boñiga fresca almacenada en B1.

No se detecta un error aritmético en la agregación de masa equivalente total.

Sí se detecta una posible fuente de ambigüedad de nomenclatura en `tabla_03_flujos_icv.csv`: el flujo `Aguas verdes` se usa como etiqueta del componente líquido `agua_l` tanto en A4 como en B2. En B2, metodológicamente el flujo aplicado se describe como purines, por lo que la etiqueta `Aguas verdes` puede inducir a pensar que B2 aplica únicamente aguas verdes. Según los datos, B2 integra agua de lavado y boñiga fresca como masa equivalente total del purín.

## Redacción metodológica sugerida para tesis

Si se mantiene el criterio actual, se recomienda explicar la diferencia de esta forma:

> La masa equivalente total de las etapas de aplicación no corresponde únicamente al volumen de agua de lavado expresado como kg equivalente. En estas etapas se integran también las fracciones de estiércol asociadas al flujo aplicado. Por ello, aun cuando se empleó la equivalencia 1 L de agua = 1 kg para el componente líquido, la masa equivalente total representa la suma del componente líquido y la fracción de estiércol correspondiente a la etapa. En A4 esta fracción corresponde al 7 % de la boñiga fresca anual asociada con la línea de aguas verdes; en B2 corresponde a la masa anual total de boñiga fresca integrada al purín aplicado en campo.

## Posibles acciones posteriores

No se recomienda modificar valores numéricos con base en esta revisión.

Sí conviene revisar, en una etapa posterior, si la etiqueta `Aguas verdes` en B2 debe cambiarse por una denominación más clara, por ejemplo:

- `Agua de lavado incorporada al purín`
- `Componente líquido del purín`
- `Agua de lavado`

Ese cambio sería de nomenclatura y claridad metodológica, no de cálculo. Si se cambiara, habría que actualizar `scripts/generate_thesis_tables.py`, regenerar `tabla_03_flujos_icv.csv`, revisar figuras asociadas a flujos y regenerar los Word.

## Cambios de nomenclatura aplicados después del diagnóstico

Después de confirmar que no existía un error aritmético, se aplicaron cambios de nomenclatura para mejorar la claridad metodológica de los flujos del ICV, sin modificar valores numéricos.

Cambios aplicados en la generación de `tabla_03_flujos_icv.csv`:

| Escenario | Etapa | Componente | Etiqueta anterior | Etiqueta actual | Valor conservado | Unidad |
|---|---:|---|---|---|---:|---|
| A | 4 | Boñiga asignada a la línea de aguas verdes | Estiércol sólido o purín | Fracción de boñiga asociada a aguas verdes | 358,840837 | kg/año |
| A | 4 | Componente líquido | Aguas verdes | Aguas verdes | 71 430,96929 | L/año |
| A | 4 | Masa agregada | Masa equivalente total | Masa equivalente total | 71 789,81012 | kg eq/año |
| B | 2 | Boñiga incorporada al purín | Estiércol sólido o purín | Boñiga incorporada al purín | 5 126,297667 | kg/año |
| B | 2 | Componente líquido del purín | Aguas verdes | Agua de lavado incorporada al purín | 71 430,96929 | L/año |
| B | 2 | Masa agregada | Masa equivalente total | Masa equivalente total | 76 557,26695 | kg eq/año |

La modificación se incorporó en `scripts/generate_thesis_tables.py` para que la tabla sea reproducible. También se regeneraron la tabla de flujos, las figuras de flujos y los documentos Word derivados.

La explicación metodológica incorporada en el documento de metodología aclara que la masa equivalente total de A4 y B2 integra el componente líquido convertido con la equivalencia 1 L = 1 kg y la fracción de estiércol correspondiente a cada etapa.
