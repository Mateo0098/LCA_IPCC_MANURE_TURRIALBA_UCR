# Auditoría de corrección del balance del Escenario B y la unidad funcional

**Fecha:** 8 de agosto de 2026  
**Alcance:** corrección conceptual específica del Escenario B y del flujo anual de referencia para normalización. No se modificaron los supuestos ni la estructura del Escenario A.

## A. Problema corregido

La implementación documentada en `auditoria_actualizacion_flujos_sanchez_2026.md` calculaba correctamente:

- estiércol fresco recolectado: 17 525,100000 kg/año;
- estiércol remanente: 8 753,625181 kg/año;
- estiércol total teóricamente depositado: 26 278,725181 kg/año;
- agua de lavado: 250 572,500000 L/año.

Sin embargo, B1 y B2 utilizaban únicamente 17 525,1 kg/año, que corresponden a la fracción recuperada mediante paleado en el Escenario A. Esto hacía desaparecer del Escenario B la fracción remanente, aunque B representa una alternativa sin separación previa en la cual todo el estiércol depositado se incorpora al sistema de purines.

Además, los resultados se normalizaban usando 17 525,1 kg/año. Ese denominador solo representa la fracción recolectada en A y no el total de residuo que entra en la frontera común de los dos escenarios.

La corrección efectuada fue:

```text
B1 = M_total_depositado
B2 = agua_lavado + M_total_depositado
flujo_referencia_A = flujo_referencia_B = M_total_depositado
```

No se alteraron A1, A2, A3 ni A4.

## B. Balance definitivo de los escenarios

| Flujo | Escenario A | Escenario B |
|---|---:|---:|
| Estiércol total de referencia | 26 278,725181 kg/año | 26 278,725181 kg/año |
| Estiércol recolectado | 17 525,100000 kg/año | 0 kg/año como flujo separado |
| Estiércol remanente | 8 753,625181 kg/año | 0 kg/año como flujo separado |
| Estiércol enviado a precomposteo | 17 525,100000 kg/año | 0 kg/año |
| Estiércol incorporado al flujo líquido | 8 753,625181 kg/año | 26 278,725181 kg/año |
| Agua de lavado | 250 572,500000 L/año | 250 572,500000 L/año |

Los ceros de B en las filas “recolectado” y “remanente” indican que no existe separación física mediante paleado; no significan ausencia de estiércol. El 100 % del total depositado se incorpora directamente al flujo líquido.

### Verificaciones físicas

**Balance A:**

```text
17 525,100000 + 8 753,625181 = 26 278,725181 kg/año
```

**Balance B:**

```text
B1 = 26 278,725181 kg/año
```

**Aplicación A4:**

```text
250 572,500000 + 8 753,625181 = 259 326,125181 kg eq/año
```

**Aplicación B2:**

```text
250 572,500000 + 26 278,725181 = 276 851,225181 kg eq/año
```

El constructor de flujos contiene validaciones automáticas que detienen la ejecución si no cierran estos balances o si los escenarios no parten del mismo flujo anual de referencia.

## C. Resultados antes/después de esta corrección

“Antes” se refiere al estado inmediatamente posterior a `auditoria_actualizacion_flujos_sanchez_2026.md`, no al modelo anterior a la incorporación del artículo.

### Flujos B1 y B2

| Parámetro/resultado | Antes | Después | Variación | Razón |
|---|---:|---:|---:|---|
| B1: Almacenamiento de purines | 17 525,100000 kg/año | 26 278,725181 kg/año | +8 753,625181 kg/año | Inclusión del remanente que no se separa en B |
| B2: Aplicación de purines | 268 097,600000 kg eq/año | 276 851,225181 kg eq/año | +8 753,625181 kg eq/año | Agua más el total depositado |

### Emisiones totales del Escenario B

| Sustancia | Antes | Después | Variación |
|---|---:|---:|---:|
| CH₄ | 275,501190 kg/año | 413,111484 kg/año | +137,610293 kg/año |
| N₂O | 1,059359 kg/año | 1,328087 kg/año | +0,268727 kg/año |
| NH₃ | 21,918736 kg/año | 29,005553 kg/año | +7,086817 kg/año |
| NO₃⁻ | 79,906945 kg/año | 105,742645 kg/año | +25,835700 kg/año |
| CO₂ | 0 kg/año | 0 kg/año | 0 kg/año |

Las emisiones del Escenario A se compararon columna por columna con la instantánea previa y permanecieron idénticas dentro de una tolerancia absoluta de 1×10⁻⁹.

### Impactos del Escenario B por etapa

| Etapa | Categoría | Antes | Después | Variación |
|---|---|---:|---:|---:|
| B1 | Calentamiento global | 5 941,002129 | 8 908,477683 | +2 967,475554 kg CO₂-eq/año |
| B1 | Eutrofización | 9,503122 | 14,249844 | +4,746722 kg PO₄-eq/año |
| B2 | Calentamiento global | 172,924294 | 178,570427 | +5,646132 kg CO₂-eq/año |
| B2 | Eutrofización | 5,759595 | 5,947651 | +0,188056 kg PO₄-eq/año |

### Impactos totales

| Escenario y categoría | Antes | Después | Variación |
|---|---:|---:|---:|
| A — Calentamiento global | 4 278,434080 | 4 278,434080 | 0 kg CO₂-eq/año |
| A — Eutrofización | 17,346687 | 17,346687 | 0 kg PO₄-eq/año |
| B — Calentamiento global | 6 113,926423 | 9 087,048109 | +2 973,121686 kg CO₂-eq/año |
| B — Eutrofización | 15,262717 | 20,197495 | +4,934778 kg PO₄-eq/año |

### Comparación entre escenarios

| Categoría | Indicador | Antes | Después |
|---|---|---:|---:|
| Calentamiento global | Diferencia B − A | 1 835,492343 kg CO₂-eq/año | 4 808,614029 kg CO₂-eq/año |
| Calentamiento global | Diferencia porcentual respecto a A | 42,901031 % | 112,391916 % |
| Eutrofización | Diferencia B − A | −2,083970 kg PO₄-eq/año | 2,850808 kg PO₄-eq/año |
| Eutrofización | Diferencia porcentual respecto a A | −12,013646 % | 16,434308 % |

### Resultados normalizados

| Escenario y categoría | Antes, con 17 525,1 kg/año | Después, con 26 278,725181 kg/año |
|---|---:|---:|
| A — Calentamiento global | 0,244131793 kg CO₂-eq/kg | 0,162809803 kg CO₂-eq/kg |
| A — Eutrofización | 0,000989820 kg PO₄-eq/kg | 0,000660104 kg PO₄-eq/kg |
| B — Calentamiento global | 0,348866849 kg CO₂-eq/kg | 0,345794861 kg CO₂-eq/kg |
| B — Eutrofización | 0,000870906 kg PO₄-eq/kg | 0,000768587 kg PO₄-eq/kg |

## D. Unidad funcional

La unidad funcional permanece sin cambios:

> **1 kg de estiércol fresco manejado**

El flujo anual de referencia común es:

```text
UF_reference_A = UF_reference_B = 26 278,725181 kg estiércol fresco/año
```

Esto representa el total de estiércol fresco teóricamente depositado dentro de la frontera operacional. El Escenario A separa ese total en una fracción recuperada y otra remanente; el Escenario B dirige el total al sistema de purines.

La normalización se calcula para ambos escenarios como:

```text
Impacto_normalizado = Impacto_anual / 26 278,725181
```

Se verificó automáticamente, para calentamiento global y eutrofización de A y B, que:

```text
Impacto_normalizado × 26 278,725181 = Impacto_anual
```

La comprobación utilizó tolerancia relativa de 1×10⁻¹² y no produjo errores.

## E. Resultados ambientales actualizados

Los resultados numéricos definitivos de esta ejecución son:

| Categoría | Escenario A | Escenario B | Escenario con mayor valor |
|---|---:|---:|---|
| Calentamiento global anual | 4 278,434080 kg CO₂-eq/año | 9 087,048109 kg CO₂-eq/año | B |
| Eutrofización anual | 17,346687 kg PO₄-eq/año | 20,197495 kg PO₄-eq/año | B |
| Calentamiento global normalizado | 0,162809803 kg CO₂-eq/kg de estiércol fresco | 0,345794861 kg CO₂-eq/kg de estiércol fresco | B |
| Eutrofización normalizada | 0,000660104 kg PO₄-eq/kg de estiércol fresco | 0,000768587 kg PO₄-eq/kg de estiércol fresco | B |

Esta sección reporta resultados y no constituye una conclusión del TFG.

## F. Implementación y archivos afectados

### Lógica y trazabilidad

- `scripts/compute_masa_etapas_escenarios.py`: B1/B2 usan el total depositado; se valida el cierre A/B y la igualdad del flujo de referencia.
- `scripts/compute_acv_impact_equivalents.py`: toma el denominador desde el flujo de referencia declarado por ambos escenarios y falla si difieren.
- `processed/masa_total_factor_overrides.csv`: se actualizó la descripción física de B1/B2.
- `DICCIONARIO_TRAZABILIDAD_VARIABLES.md`: se corrigió la definición de los flujos de B.
- `scripts/generate_methodology_docx.py` y `scripts/generate_results_docx.py`: se actualizaron referencias y valores para una futura regeneración; no se ejecutaron.

### Salidas regeneradas

- `processed/masa_total_escenario_etapa.csv`;
- `processed/ACV_resumen_emisiones.csv`;
- `processed/acv_impacto_por_etapa_escenario.csv`;
- `processed/acv_impacto_total_por_escenario.csv`;
- tablas dependientes `tabla_03`, `tabla_04`, `tabla_06`, `tabla_07`, `tabla_08`, `tabla_09`, resumen de redacción y apéndices CSV relacionados en `outputs/tablas_tesis/`;
- figuras dependientes `fig_04` a `fig_15` en PNG y SVG dentro de `outputs/graficos_tesis/`;
- gráficos auxiliares de emisiones e impactos en `graphics_results/`.

Las salidas de caracterización y la tabla de definición de etapas, regeneradas incidentalmente por la cadena, se restauraron porque no dependen de esta corrección.

## G. Validaciones ejecutadas

1. `ACV_orquestador.py`: completado sin errores;
2. `scripts/generate_thesis_tables.py`: completado; solo emitió advertencias preexistentes de compatibilidad futura de pandas;
3. `scripts/generate_thesis_graphics.py`: completado sin errores;
4. cierre del balance A: correcto;
5. B1 igual al total depositado: correcto;
6. composición de A4 y B2: correcta;
7. referencia A igual a referencia B: correcta;
8. reconstrucción del impacto anual desde el normalizado: correcta para ambos escenarios y categorías;
9. ausencia de constantes obsoletas de B en scripts activos: verificada;
10. sintaxis de scripts modificados: verificada;
11. comparación contra la instantánea previa: A permaneció sin cambios;
12. documentos Word y master: no modificados.

## H. Fuente bibliográfica conservada

El artículo permanece en:

`Academic_documents/references/Sanchez-ganado.pdf`

No se introdujeron fuentes bibliográficas adicionales ni se modificaron el artículo o los datos crudos.
