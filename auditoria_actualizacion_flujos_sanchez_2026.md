# Auditoría de actualización de flujos con Sánchez-Romero y Brenes-Gamboa (2026)

**Fecha:** 8 de agosto de 2026  
**Alcance:** actualización y validación del modelo de cálculo; no se regeneraron ni modificaron documentos Word.

## 1. Fuente documental principal

La fuente principal es `Academic_documents/references/Sanchez-ganado.pdf`, correspondiente al artículo *Cuantificación y caracterización de residuos generados durante el ordeño de ganado Jersey*, de Carlos A. Sánchez-Romero y Saúl Brenes-Gamboa, publicado en *Agronomía Mesoamericana*, volumen 37, 2026.

El PDF fue leído localmente y se verificó que contiene los valores operativos usados en esta actualización. Los parámetros computables y su clasificación documental se registraron en `Academic_documents/references/parametros_operativos_sanchez_2026.csv`. Los Excel con datos crudos permanecen en el repositorio y no fueron eliminados ni modificados.

## 2. Auditoría del modelo anterior

Antes de esta actualización, `scripts/compute_agua_boniga_stats.py` calculaba promedios desde `Academic_documents/Datos boñiga y agua proy_AS.xlsx`. El archivo resultante, `processed/agua_boniga_estadistica_descriptiva.csv`, suministraba:

- estiércol fresco: 5 126,297667 kg/año;
- agua: 71 430,969286 L/año;
- promedio del conjunto crudo de estiércol: 49,156279 kg para el periodo interpretado por el script;
- promedio del conjunto crudo de agua: 684,9545 L para el periodo interpretado por el script;
- duración aplicada a ambos promedios: 3,5 días.

Después, `processed/masa_total_factor_overrides.csv` asignaba 93 % del estiércol a A1/A2 y 7 % a A3/A4. B1/B2 recibían 100 %. El 7 % era un supuesto de reparto del flujo anual recolectado y no una estimación física del remanente.

La propagación seguía esta secuencia:

1. `scripts/compute_agua_boniga_stats.py`;
2. `scripts/compute_masa_etapas_escenarios.py`;
3. scripts `ACV_EscenarioA_etapa1.py` a `ACV_EscenarioB_etapa2.py`;
4. `scripts/acv_resumen_emisiones_csv.py`;
5. `scripts/compute_acv_impact_equivalents.py`;
6. `scripts/generate_thesis_tables.py` y `scripts/generate_thesis_graphics.py`.

## 3. Parámetros anteriores y nuevos

| Parámetro/resultado | Antes | Después | Variación | Razón del cambio |
|---|---:|---:|---:|---|
| Estiércol fresco recolectado | 5 126,297667 kg/año | 17 525,100000 kg/año | +12 398,802333 kg/año | Uso directo del total anual publicado |
| Agua de lavado | 71 430,969286 L/año | 250 572,500000 L/año | +179 141,530714 L/año | Uso de 686,5 L/día publicados y anualización por 365 días |
| Fracción asignada anteriormente a aguas verdes | 0,07 del flujo recolectado | No aplica | Eliminada | Se sustituyó el reparto supuesto por un balance físico derivado |
| Peso vivo promedio | No era entrada del flujo | 396,6 kg/animal | — | Dato publicado |
| Población media | No era entrada del flujo | 18 vacas | — | Dato publicado; se conserva para trazabilidad, pero no se recalcula el total anual |
| Permanencia en sala | No era entrada del flujo | 3,5 h/día | — | Dato publicado |
| Estiércol recolectado por animal | No era entrada del flujo | 2,7 kg/animal | — | Dato publicado |
| Fracción diaria teórica | No existía en este balance | 0,07 del peso vivo/día | — | Supuesto conservador del TFG basado en el límite inferior del intervalo bibliográfico 7–10 % |
| Fracción recolectada | No calculada | 0,666893080984 | — | Derivada de los parámetros anteriores |
| Fracción remanente | 0,07 aplicada al recolectado | 0,333106919016 del total depositado | No comparable directamente | Nueva base conceptual y matemática |
| Estiércol total depositado en sala | No calculado | 26 278,725181 kg/año | — | Derivado del total recolectado y la fracción recolectada |
| Estiércol remanente | 358,840837 kg/año | 8 753,625181 kg/año | +8 394,784344 kg/año | Diferencia entre depósito teórico y recolección |

## 4. Trazabilidad bibliográfica de los nuevos parámetros

### Datos directamente publicados en Sánchez-Romero y Brenes-Gamboa (2026)

- peso vivo promedio: 396,6 kg/animal;
- población media: 18 vacas en ordeño;
- permanencia aproximada: 3,5 h/día;
- estiércol fresco recolectado: 2,7 kg/animal durante las actividades evaluadas;
- producción total publicada de estiércol fresco recolectado: 17 525,1 kg/año;
- consumo promedio de agua de lavado: 686,5 L/día;
- intervalo bibliográfico mencionado para producción diaria: 7–10 % del peso vivo.

Los 17 525,1 kg/año se interpretan exclusivamente como estiércol efectivamente recolectado durante las actividades de ordeño evaluadas, no como excreción fisiológica de 24 horas.

### Valores derivados o supuestos metodológicos del presente TFG

- adopción de 0,07 como fracción diaria: supuesto conservador del investigador basado en el límite inferior del intervalo citado; no es una medición de Sánchez-Romero y Brenes-Gamboa;
- distribución temporal uniforme de la excreción para prorratear 3,5 horas de permanencia;
- generación diaria teórica: 396,6 × 0,07 = 27,762 kg/animal/día;
- depósito teórico durante la permanencia: 27,762 × (3,5/24) = 4,048625 kg/animal;
- remanente por animal: 4,048625 − 2,7 = 1,348625 kg/animal;
- fracción recolectada: 2,7/4,048625 = 0,666893080984;
- fracción remanente: 1 − 0,666893080984 = 0,333106919016;
- consumo anual de agua: 686,5 × 365 = 250 572,5 L/año;
- total depositado anual y remanente anual derivados del total recolectado publicado.

## 5. Ecuaciones implementadas

Las ecuaciones se implementaron en `scripts/compute_masa_etapas_escenarios.py` a partir de parámetros fundamentales:

```text
g_diaria = peso_vivo × fracción_diaria
g_sala = g_diaria × permanencia_sala / horas_día
f_recolectada = estiércol_recolectado_animal / g_sala
f_remanente = 1 − f_recolectada
M_total_depositado = M_recolectado / f_recolectada
M_remanente = M_total_depositado − M_recolectado
agua_anual = agua_diaria × días_año
```

También se incorporaron comprobaciones automáticas de positividad, rango de fracciones, permanencia temporal y cierre del balance.

## Verificación del balance del estiércol en sala

La relación correcta usa el total anual publicado como masa recolectada:

```text
M_recolectado = 17 525,100000 kg/año
f_recolectada = 0,666893080984
M_total_depositado = 17 525,1 / 0,666893080984
M_total_depositado = 26 278,725181 kg/año

M_remanente = 26 278,725181 − 17 525,100000
M_remanente = 8 753,625181 kg/año

26 278,725181 = 17 525,100000 + 8 753,625181
```

El error de cierre calculado con precisión interna fue 0,0 kg/año. No se utilizó la operación incorrecta `17 525,1 × 0,333106919`. La forma equivalente aplicada es:

```text
M_remanente = M_recolectado × (f_remanente / f_recolectada)
```

La masa remanente aparece en A3 y continúa hacia A4; no se suma a A1 ni se interpreta como generación adicional. En el balance físico global, el estiércol recolectado y el remanente son partes excluyentes del total depositado.

## 7. Flujos por etapa

| Parámetro/resultado | Antes | Después | Variación | Razón del cambio |
|---|---:|---:|---:|---|
| A1: Precomposteo | 4 767,456830 kg/año | 17 525,100000 kg/año | +12 757,643170 | Masa recolectada publicada, sin descuento del 7 % anterior |
| A2: Lombricompostaje | 1 472,395670 kg/año | 5 412,504459 kg/año | +3 940,108789 | Nueva masa de A1 por el factor preexistente 0,308843 |
| A3: Almacenamiento de aguas verdes | 358,840837 kg/año | 8 753,625181 kg/año | +8 394,784344 | Remanente derivado del balance |
| A4: Aplicación de aguas verdes | 71 789,810120 kg eq/año | 259 326,125181 kg eq/año | +187 536,315061 | 250 572,5 L/año de agua + remanente |
| B1: Almacenamiento de purines | 5 126,297667 kg/año | 17 525,100000 kg/año | +12 398,802333 | Mantiene su definición basada en el estiércol recolectado |
| B2: Aplicación de purines | 76 557,266950 kg eq/año | 268 097,600000 kg eq/año | +191 540,333050 | 250 572,5 L/año de agua + estiércol recolectado |

La definición matemática de B no incorporaba la antigua fracción A de 7 %. Por ello B1 y B2 cambiaron solamente por las nuevas entradas publicadas de estiércol recolectado y agua; no se añadió a B el remanente calculado específicamente para representar aguas verdes en A.

## 8. Cambios en emisiones

Las ecuaciones, factores y parámetros químicos no cambiaron. Las emisiones cambiaron únicamente por el nuevo escalamiento másico.

| Sustancia | Escenario A antes | Escenario A después | Escenario B antes | Escenario B después |
|---|---:|---:|---:|---:|
| CH₄ (kg/año) | 9,55 | 151,99 | 80,59 | 275,50 |
| N₂O (kg/año) | 0,79 | 3,11 | 0,31 | 1,06 |
| NH₃ (kg/año) | 5,23 | 24,91 | 6,35 | 21,92 |
| NO₃⁻ (kg/año) | 19,05 | 90,82 | 23,16 | 79,91 |
| CO₂ (kg/año) | 33,65 | 123,70 | 0,00 | 0,00 |

La mayor ampliación relativa dentro de A ocurre en A3 porque el antiguo 7 % del flujo recolectado fue sustituido por el remanente derivado respecto al total teórico depositado.

## 9. Cambios en impactos

### Impactos por etapa

| Etapa | Calentamiento global antes | Calentamiento global después | Eutrofización antes | Eutrofización después |
|---|---:|---:|---:|---:|
| A1 | 241,720607 | 888,561335 | 2,475183 | 9,098737 |
| A2 | 86,310852 | 317,277402 | 0,000000 | 0,000000 |
| A3 | 121,646905 | 2 967,475554 | 0,194584 | 4,746722 |
| A4 | 29,100538 | 105,119789 | 0,969253 | 3,501228 |
| B1 | 1 737,812928 | 5 941,002129 | 2,779775 | 9,503122 |
| B2 | 49,379821 | 172,924294 | 1,644695 | 5,759595 |

Las unidades son kg CO₂-eq/año para calentamiento global y kg PO₄-eq/año para eutrofización.

### Impactos totales y normalizados

| Escenario | Calentamiento global anual | Eutrofización anual | Calentamiento global normalizado | Eutrofización normalizada |
|---|---:|---:|---:|---:|
| A | 4 278,434080 kg CO₂-eq/año | 17,346687 kg PO₄-eq/año | 0,244131793 kg CO₂-eq/kg de estiércol fresco | 0,000989820 kg PO₄-eq/kg de estiércol fresco |
| B | 6 113,926423 kg CO₂-eq/año | 15,262717 kg PO₄-eq/año | 0,348866849 kg CO₂-eq/kg de estiércol fresco | 0,000870906 kg PO₄-eq/kg de estiércol fresco |

La referencia de normalización es 17 525,1 kg/año de estiércol fresco recolectado. Esto no redefine la unidad funcional: permanece como **1 kg de estiércol fresco manejado**. `processed/acv_impacto_por_etapa_escenario.csv` y `processed/acv_impacto_total_por_escenario.csv` contienen simultáneamente resultados anuales y normalizados.

Con la actualización, B supera a A en calentamiento global por 1 835,492343 kg CO₂-eq/año (42,901 % respecto a A). Para eutrofización, B queda 2,083970 kg PO₄-eq/año por debajo de A (−12,014 % respecto a A). Este cambio de orden es un resultado de la propagación del nuevo flujo remanente y no una modificación de factores o ecuaciones.

## 10. Elementos que no cambiaron

- documento master, objetivos y alcance conceptual;
- estructura de escenarios A1–A4 y B1–B2;
- unidad funcional;
- sistemas de manejo IPCC asignados;
- ecuaciones IPCC y conversiones estequiométricas;
- factores de emisión y caracterización;
- factor de transformación de estiércol fresco a material precompostado en A2;
- tratamiento y fuente del CO₂ de A2;
- datos analíticos de laboratorio y campañas de muestreo;
- archivos Excel crudos;
- todos los documentos `.docx`.

## 11. Archivos modificados o creados

### Entradas, configuración y trazabilidad

- `Academic_documents/references/parametros_operativos_sanchez_2026.csv` (nuevo);
- `processed/masa_total_factor_overrides.csv`;
- `DICCIONARIO_TRAZABILIDAD_VARIABLES.md`.

### Código

- `ACV_orquestador.py`;
- `scripts/compute_masa_etapas_escenarios.py`;
- `scripts/compute_acv_impact_equivalents.py`;
- `scripts/generate_methodology_docx.py`;
- `scripts/generate_results_docx.py`.

Los dos generadores Word se actualizaron para evitar que una regeneración futura recupere el supuesto de 7 % o cifras obsoletas; no se ejecutaron en esta tarea.

### Resultados intermedios del modelo

- `processed/masa_total_escenario_etapa.csv`;
- `processed/ACV_resumen_emisiones.csv`;
- `processed/acv_impacto_por_etapa_escenario.csv`;
- `processed/acv_impacto_total_por_escenario.csv`.

### Tablas de tesis actualizadas

- `outputs/tablas_tesis/tabla_03_flujos_icv.csv`;
- `outputs/tablas_tesis/tabla_04_parametros_modelo_acv.csv`;
- `outputs/tablas_tesis/tabla_06_emisiones_por_etapa.csv`;
- `outputs/tablas_tesis/tabla_07_impactos_por_etapa.csv`;
- `outputs/tablas_tesis/tabla_08_impactos_totales_por_escenario.csv`;
- `outputs/tablas_tesis/tabla_09_comparacion_escenarios.csv`;
- `outputs/tablas_tesis/resumen_resultados_para_redaccion.md`;
- `outputs/tablas_tesis/tablas_word/apendice_E_flujos_icv_word.csv`;
- `outputs/tablas_tesis/tablas_word/apendice_H_emisiones_word.csv`;
- `outputs/tablas_tesis/tablas_word/apendice_I_impactos_por_etapa_word.csv`;
- `outputs/tablas_tesis/tablas_word/apendice_J_impactos_totales_word.csv`;
- `outputs/tablas_tesis/tablas_word/apendice_K_comparacion_escenarios_word.csv`.

### Gráficos de tesis actualizados

Se actualizaron las versiones PNG y SVG de `fig_04` a `fig_15` en `outputs/graficos_tesis/`, porque representan flujos, emisiones o impactos. No se conservaron cambios accidentales en las figuras 1–3 de caracterización.

El orquestador también actualizó las salidas auxiliares PNG/PDF de emisiones e impactos en `graphics_results/`.

### Informe

- `auditoria_actualizacion_flujos_sanchez_2026.md`.

## 12. Validaciones ejecutadas

1. ejecución completa de `ACV_orquestador.py`, incluidas seis etapas, emisiones e impactos;
2. ejecución de `scripts/generate_thesis_tables.py`;
3. ejecución de `scripts/generate_thesis_graphics.py`;
4. análisis sintáctico de los scripts modificados sin generar documentos Word;
5. comprobación de `M_total_depositado = M_recolectado + M_remanente` con error 0,0;
6. comprobación de `f_recolectada + f_remanente = 1`;
7. comprobación de que A3 y A4 usan el mismo remanente y que A4 suma una sola vez agua y remanente;
8. comprobación de que B2 suma una sola vez agua y estiércol recolectado;
9. búsqueda de constantes operativas obsoletas en scripts activos;
10. verificación local del texto del artículo;
11. control de hashes de documentos Word antes y después.

La cadena terminó sin errores. Se observaron advertencias de compatibilidad futura de pandas durante la generación de tablas; no afectaron los resultados y no se modificó esa lógica por estar fuera del alcance metodológico solicitado.

## 13. Inconsistencias encontradas

### Diferencia entre indicadores publicados

La operación `2,7 kg/animal × 18 animales × 365 días` produce 17 739,0 kg/año y no 17 525,1 kg/año. Esto no impidió la implementación porque se instruyó usar directamente el total anual publicado y evitar recalcularlo innecesariamente. En consecuencia:

- 17 525,1 kg/año es la entrada anual de masa recolectada;
- 2,7 kg/animal se usa únicamente para derivar la fracción recolectada respecto al depósito teórico;
- 18 animales se conserva como parámetro documental y no se usa para reemplazar el total publicado.

### Cambio de orden en eutrofización

El nuevo balance hace que A tenga mayor eutrofización total que B, contrario al resultado anterior. La cadena aritmética es consistente y el cambio se explica por el incremento de A3/A4. Debe revisarse científicamente antes de redactar conclusiones, pero no constituye por sí solo un error computacional.

### Archivos procesados no mostrados por Git

Algunas salidas intermedias y auxiliares están ignoradas por la configuración de Git. Se regeneraron y validaron en el entorno local, aunque `git status` solo enumera las salidas rastreadas. Esta condición preexistente no se modificó.

## 14. Dictamen

La actualización se implementó con una fuente operativa publicada, conserva los datos crudos y elimina el reparto asumido 93/7. El remanente se deriva de parámetros fundamentales y se incorpora una sola vez al balance de aguas verdes. La propagación hasta emisiones e impactos es reproducible mediante el orquestador. Los resultados anualizados y normalizados coexisten sin cambiar la unidad funcional ni las demás decisiones metodológicas protegidas.
