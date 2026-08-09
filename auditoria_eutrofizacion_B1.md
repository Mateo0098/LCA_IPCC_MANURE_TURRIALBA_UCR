# Auditoría de eutrofización de B1

**Alcance:** análisis de solo lectura de la implementación y de las salidas vigentes. No se modificaron ni regeneraron scripts, parámetros, ecuaciones, factores, resultados, tablas, gráficos o documentos.

## 1. Archivos y ecuaciones involucradas

La etapa **B1: Almacenamiento de purines** se calcula en `scripts/ACV_EscenarioB_etapa1.py`. El script obtiene el nitrógeno y los sólidos volátiles mediante `obtener_parametros_etapa("B", 1)` y los factores del sistema de manejo mediante `obtener_factores_manejo_ipcc("B", 1)`.

La cadena relevante para el nitrógeno es:

1. `processed/acv_parametros_escenario_etapa.csv`: aporta `n_ex_pct = 0,371666667 % N total` para B1. Este valor procede de `processed/CIA_samples_table_v6_treatment_summary.csv`, tratamiento `ESTIERCOL FRESCO`, fecha 19/11/2025.
2. `processed/ipcc_sistema_manejo_por_etapa.csv`: asigna a B1 el sistema `uncovered_anaerobic_lagoon`, descrito en las salidas académicas como almacenamiento de purines.
3. `processed/ipcc_sistemas_manejo_estiercol_factores.csv`: para ese sistema declara `EF3 = 0`, `frac_gas_ms = 0,35` y `frac_leach_ms = 0`.
4. `scripts/ACV_EscenarioB_etapa1.py`: fija `EF4 = 0,014` y `EF5 = 0,011`, llama las ecuaciones 2 a 8, 12 y 13, y entrega los resultados a `exportar_fila()`.
5. `scripts/ecuaciones_acv.py`: implementa las ecuaciones y las conversiones `FACTOR_N_A_N2O = 44/28`, `FACTOR_N_A_NH3 = 17/14` y `FACTOR_N_A_NO3 = 4,4268`.
6. `scripts/acv_resumen_emisiones_csv.py`: multiplica los resultados unitarios por `masa_total_kg_eq` de la etapa, tomada de `processed/masa_total_escenario_etapa.csv`.
7. `processed/ACV_resumen_emisiones.csv`: registra las emisiones anuales escaladas de B1 por ecuación.
8. `processed/acv_factores_equivalencia.csv`: contiene los factores de eutrofización de NH₃ (`0,35 kg PO₄-eq/kg NH₃`) y NO₃⁻ (`0,095 kg PO₄-eq/kg NO₃⁻`). CH₄, N₂O y CO₂ tienen factor de eutrofización nulo o vacío.
9. `scripts/compute_acv_impact_equivalents.py`: suma `NH3_ec12 + NH3_ec20` y `NO3_ec13 + NO3_ec21`, y calcula `NH3 × 0,35 + NO3 × 0,095`.
10. `processed/acv_impacto_por_etapa_escenario.csv`, `outputs/tablas_tesis/tabla_06_emisiones_por_etapa.csv` y `outputs/tablas_tesis/tabla_07_impactos_por_etapa.csv`: registran las emisiones y los impactos finales por etapa.

Funciones utilizadas directamente por B1:

- `n2o_direct_mm()` — ecuación 2;
- `n_volatilization_mms()` — ecuación 3;
- `n_lixiviado_mms()` — ecuación 4;
- `n2o_indirect_volatilization()` — ecuación 5;
- `n2o_indirect_leaching()` — ecuación 6;
- `n_indirect_volatilization()` — ecuación 7;
- `n_indirect_leaching()` — ecuación 8;
- `nh3_direct_mm()` — ecuación 12;
- `no3_direct_mm()` — ecuación 13.

## 2. Balance de N de entrada

La masa anual de entrada registrada para B1 es:

```text
M_B1 = 26 278,725181 kg/año
```

El parámetro de nitrógeno se convierte de porcentaje a fracción másica:

```text
n_ex_pct = 0,371666667 %
n_ex_fraction = 0,371666667 / 100
              = 0,00371666667 kg N/kg de muestra
```

En el script, las ecuaciones se evalúan primero con `N = 1`, `AWMS = 1` y `N_cdg = 0`; posteriormente `exportar_fila()` multiplica cada resultado por la masa de B1. La forma anual equivalente es:

```text
N_entrada = M_B1 × n_ex_fraction
          = 26 278,725181 × 0,00371666667
          = 97,66926201031242 kg N/año
```

El mismo `N_entrada` es la base susceptible para las ecuaciones de volatilización y lixiviación. Las fracciones seleccionadas determinan cuánto se asigna a cada ruta:

```text
N_volatilizado = N_entrada × frac_gas_ms
               = 97,66926201031242 × 0,35
               = 34,184241703609345 kg N/año

N_lixiviado = N_entrada × frac_leach_ms
            = 97,66926201031242 × 0
            = 0 kg N/año
```

La pérdida directa como N₂O de la gestión del estiércol también es cero porque `EF3 = 0`:

```text
N2O_directo_B1 = N_entrada × EF3 × (44/28) = 0 kg N₂O/año
```

B1 no ejecuta las ecuaciones 22 a 24 y, por tanto, no calcula en esta etapa una pérdida adicional como N₂ ni un balance de N disponible para aplicación.

## 3. Ruta de volatilización

La ecuación 3 implementada es:

```text
N_volatilizado = ((N × Nex) × AWMS + N_cdg) × frac_gas_ms
```

Después del escalamiento anual, B1 volatiliza `34,184241703609345 kg N/año`.

La ecuación 5 transforma una fracción de este N en N₂O indirecto:

```text
N2O-N_vol = N_volatilizado × EF4
          = 34,184241703609345 × 0,014
          = 0,47857938385053084 kg N₂O-N/año

N2O_vol = N2O-N_vol × (44/28)
        = 0,47857938385053084 × (44/28)
        = 0,7520533174794056 kg N₂O/año
```

La ecuación 7 calcula el N remanente de esta ruta después de reservar la fracción `EF4`:

```text
N_G_mm = N_volatilizado × (1 − EF4)
       = 34,184241703609345 × 0,986
       = 33,705662319758815 kg N/año
```

Por tanto, la implementación sí descuenta de la ruta volatilizada el N empleado para formar N₂O-N indirecto antes de pasarlo a las ecuaciones 12 y 13.

## 4. Ruta de lixiviación

La ecuación 4 implementada es:

```text
N_lixiviado = (N × N_ex × AWMS + N_cdg) × frac_leach_ms
```

Para B1, `frac_leach_ms = 0`, de modo que:

```text
N_lixiviado = 97,66926201031242 × 0 = 0 kg N/año
N2O-N_lix = N_lixiviado × EF5 = 0 kg N₂O-N/año
N2O_lix = N2O-N_lix × (44/28) = 0 kg N₂O/año
N_L_mm = N_lixiviado × (1 − EF5) = 0 kg N/año
```

En consecuencia, la ruta de lixiviación no aporta N ni N₂O indirecto a B1. No obstante, como se muestra en las secciones 6 y 7, la función que genera NO₃⁻ no depende exclusivamente de `N_L_mm`.

## 5. N₂O indirecto

| Ruta | N perdido inicialmente (kg N/año) | Factor | N₂O-N (kg/año) | N₂O (kg/año) | Calentamiento global (kg CO₂-eq/año) |
|---|---:|---:|---:|---:|---:|
| Volatilización | 34,184241703609345 | EF4 = 0,014 | 0,478579383850531 | 0,752053317479406 | 233,13652841861574 |
| Lixiviación | 0 | EF5 = 0,011 | 0 | 0 | 0 |
| **Total indirecto de B1** | — | — | **0,478579383850531** | **0,752053317479406** | **233,13652841861574** |

El calentamiento global se obtiene con el factor `310 kg CO₂-eq/kg N₂O`:

```text
0,7520533174794056 × 310 = 233,13652841861574 kg CO₂-eq/año
```

Estos N₂O indirectos pertenecen exclusivamente a la categoría de calentamiento global en la implementación vigente. `compute_acv_impact_equivalents.py` no incluye N₂O en la ecuación de eutrofización; por tanto, su contribución directa a eutrofización es cero.

## 6. Formación de NH₃

La función `nh3_direct_mm()` no convierte únicamente el remanente de volatilización. Su ecuación real es:

```text
NH3 = ((N_G_mm + N_L_mm) / 2) × (17/14)
```

Para B1:

```text
N_promedio = (33,705662319758815 + 0) / 2
           = 16,852831159879408 kg N/año

NH3_B1 = 16,852831159879408 × (17/14)
        = 20,464152122710708 kg NH₃/año
```

Caracterización de eutrofización:

```text
Eutrofización_NH3_B1
= 20,464152122710708 × 0,35
= 7,162453242948748 kg PO₄-eq/año
```

La implementación sí resta `EF4` antes de formar NH₃. Sin embargo, también promedia el remanente de volatilización con el remanente de lixiviación, que en B1 es cero; por ello utiliza la mitad de `N_G_mm`.

## 7. Formación de NO₃⁻

La función `no3_direct_mm()` usa exactamente el mismo promedio de remanentes que la función de NH₃:

```text
NO3 = ((N_G_mm + N_L_mm) / 2) × 4,4268
```

Para B1:

```text
N_promedio = (33,705662319758815 + 0) / 2
           = 16,852831159879408 kg N/año

NO3_B1 = 16,852831159879408 × 4,4268
        = 74,60411297855416 kg NO₃⁻/año
```

Caracterización de eutrofización:

```text
Eutrofización_NO3_B1
= 74,60411297855416 × 0,095
= 7,087390732962644 kg PO₄-eq/año
```

La ecuación 8 descontaría `EF5` del N lixiviado antes de la conversión, pero en B1 el N lixiviado es cero. El NO₃⁻ distinto de cero se genera porque la ecuación 13 incorpora también `N_G_mm`, es decir, el remanente de la ruta de volatilización. En la implementación vigente no puede atribuirse este NO₃⁻ exclusivamente a lixiviación.

## 8. Descomposición del impacto de eutrofización de B1

| Sustancia | Ruta de origen en la implementación | Emisión B1 (kg/año) | Factor de caracterización (kg PO₄-eq/kg) | Impacto de eutrofización (kg PO₄-eq/año) | % del total B1 |
|---|---|---:|---:|---:|---:|
| NH₃ | Promedio de N remanente de volatilización y lixiviación; en B1 solo el término de volatilización es distinto de cero | 20,464152122710708 | 0,35 | 7,162453242948748 | 50,2633801118 % |
| NO₃⁻ | El mismo promedio de remanentes; en B1 se genera aun con lixiviación igual a cero | 74,60411297855416 | 0,095 | 7,087390732962644 | 49,7366198882 % |
| Otras sustancias | No existen otras sustancias con factor de eutrofización distinto de cero | 0 | — | 0 | 0 % |
| **Total B1** | — | — | — | **14,249843975911393** | **100 %** |

Comprobación del cierre:

```text
Eutrofización_B1
= Eutrofización_NH3 + Eutrofización_NO3
= 7,162453242948748 + 7,087390732962644
= 14,249843975911393 kg PO₄-eq/año
```

El cierre contra `processed/acv_impacto_por_etapa_escenario.csv` es exacto con la precisión de punto flotante mostrada.

## 9. Comparación B1 vs B2

B2 utiliza `n_ex_pct = 0,011434 %`, una masa equivalente de `276 851,225181 kg/año`, `frac_gasm = 0,21`, `frac_leach_h = 0,24`, `EF4 = 0,014` y `EF5 = 0,011`. Su N anual de entrada calculado es `31,65516908719554 kg N/año`. Las ecuaciones 17 y 19 dejan `6,554519311194708 kg N/año` y `7,513670934536733 kg N/año`, respectivamente; las ecuaciones 20 y 21 promedian estos valores y convierten el mismo promedio a NH₃ y NO₃⁻.

| Sustancia | Eutrofización B1 (kg PO₄-eq/año) | Eutrofización B2 (kg PO₄-eq/año) |
|---|---:|---:|
| NH₃ | 7,162453242948748 | 2,989490427217931 |
| NO₃⁻ | 7,087390732962644 | 2,958160567540688 |
| **Total** | **14,249843975911393** | **5,947650994758619** |

B1 supera a B2 en:

```text
Diferencia total = 14,249843975911393 − 5,947650994758619
                 = 8,302192981152775 kg PO₄-eq/año
```

La diferencia se descompone en `4,172962815730816 kg PO₄-eq/año` adicionales por NH₃ y `4,129230165421957 kg PO₄-eq/año` adicionales por NO₃⁻. El impacto de B1 equivale a `2,3958776311` veces el de B2, o `139,5877631097 %` más. Numéricamente, esto ocurre porque las ecuaciones de B1 producen mayores masas de ambas sustancias: `20,464152122710708 frente a 8,54140122062266 kg NH₃/año` y `74,60411297855416 frente a 31,138532289901978 kg NO₃⁻/año`.

## 10. Respuesta a la pregunta principal

Por sustancia caracterizada, la eutrofización de B1 procede de **NH₃ y NO₃⁻ en magnitudes prácticamente iguales**:

- NH₃: `7,162453242948748 kg PO₄-eq/año`, equivalente a `50,2633801118 %` del total;
- NO₃⁻: `7,087390732962644 kg PO₄-eq/año`, equivalente a `49,7366198882 %` del total;
- diferencia absoluta: `0,075062509986104 kg PO₄-eq/año`, con NH₃ ligeramente mayor.

Por ruta primaria de pérdida de N, la interpretación es distinta: **todo el N que alimenta esas dos emisiones en B1 procede del término de volatilización**, porque `frac_leach_ms = 0` y `N_L_mm = 0`. La salida de NO₃⁻ no demuestra una contribución de lixiviación en B1; se origina matemáticamente porque la ecuación 13 convierte el promedio de `N_G_mm` y `N_L_mm`, y `N_G_mm` es distinto de cero.

## 11. Observaciones que requieren revisión del investigador

### Elementos comprobados de la implementación

1. **La lixiviación explícita de B1 es cero.** El sistema asignado tiene `frac_leach_ms = 0`; por tanto, las ecuaciones 4, 6 y 8 producen cero.
2. **El N₂O indirecto no contribuye a eutrofización.** Solo se caracteriza para calentamiento global.
3. **NH₃ y NO₃⁻ usan el mismo N promedio.** Las ecuaciones 12 y 13 reciben `N_G_mm` y `N_L_mm`, calculan `(N_G_mm + N_L_mm)/2` y convierten ese mismo valor a dos compuestos diferentes.
4. **B1 genera NO₃⁻ aun sin lixiviación.** El término que sostiene ese resultado es `N_G_mm`, derivado de la volatilización.

### Elemento llamativo que requiere evaluación científica

La implementación asigna el mismo promedio de N remanente simultáneamente a NH₃ y NO₃⁻. En B1, ambos compuestos se derivan de `16,852831159879408 kg N/año`, pese a que la ruta explícita de lixiviación es cero. Esto puede representar una decisión metodológica de reparto o una posible duplicación conceptual del N entre sustancias; determinar su validez científica corresponde al investigador.

### Clasificación del hallazgo

- **Error computacional comprobado:** no se detectó un error de ejecución, suma o aplicación aritmética. Las salidas reproducen exactamente las funciones y factores codificados, y el impacto cierra sin residuo.
- **Decisión metodológica existente:** uso de los factores `frac_gas_ms`, `frac_leach_ms`, `EF4`, `EF5` y de caracterización tal como están configurados.
- **Punto que requiere revisión científica:** que las ecuaciones 12 y 13 conviertan el mismo promedio de N a NH₃ y NO₃⁻, y que ello produzca NO₃⁻ en B1 cuando la lixiviación explícita es nula.
