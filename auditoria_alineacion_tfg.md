# Auditoría de alineación investigativa del TFG

**Fecha de la auditoría:** 8 de agosto de 2026  
**Naturaleza del informe:** diagnóstico documental; no constituye una corrección de los documentos evaluados ni una evaluación exhaustiva de la calidad científica del modelo.

## 1. Archivos analizados

Se identificaron y analizaron, en modo de solo lectura, los siguientes documentos:

| Categoría | Archivo |
|---|---|
| Propuesta master del TFG | `MASTER_escrito/TFG_ACV_Estiercol_MASTER.docx` |
| Metodología desarrollada | `outputs/documentos_tfg/metodologia_desarrollada_tfg.docx` |
| Resultados desarrollados | `outputs/documentos_tfg/resultados_desarrollados_tfg.docx` |

No se encontró ambigüedad respecto al master: existe un único archivo Word dentro de `MASTER_escrito/` y su nombre coincide con el documento master definido para el proyecto. Los otros archivos Word localizados en `docs/` y `prosas/` son documentos auxiliares y no se trataron como posibles versiones del master.

Como control de integridad, el SHA-256 del master antes del análisis fue `98ABDE3EC5A22FA052EFA595AAC26729EA070EACA670BDC41097C4BF2E5E327C`.

## 2. Objetivo general del master

> Desarrollar un Análisis de Ciclo de Vida del manejo del estiércol del ganado de una lechería especializada, para estimación del impacto ambiental.

## 3. Objetivos específicos del master

El master contiene **dos objetivos específicos**, transcritos completos:

1. > Realizar el inventario para el Análisis de Ciclo de Vida del estiércol bovino manejado mediante lombricompostaje y el aplicado como purines directamente en los campos de pastoreo.

2. > Evaluar el impacto ambiental del estiércol bovino manejado mediante lombricompostaje y el aplicado como purines directamente en los campos de pastoreo.

## 4. Alcance y compromisos rectores establecidos en el master

### 4.1 Alcance del estudio

El master establece un ACV del manejo de estiércol bovino en la lechería de la Sede del Atlántico de la Universidad de Costa Rica, en Turrialba. La comparación se organiza en dos escenarios:

- **Escenario A (escenario base):** precomposteo, lombricompostaje, almacenamiento de aguas verdes y aplicación de aguas verdes en campo.
- **Escenario B (escenario alternativo):** almacenamiento de purines y aplicación de purines directamente en campo.

La frontera declarada comprende desde el ingreso del estiércol bovino al módulo lechero hasta su aplicación en campo como enmienda agrícola. Se excluye la generación de excreta en campo. La unidad funcional declarada es **1 kg de estiércol fresco, tal como fue recolectado del módulo lechero**.

El master limita la evaluación ambiental a dos categorías de impacto de punto medio:

- potencial de calentamiento global, expresado en unidades equivalentes de CO₂;
- potencial de eutrofización, expresado en unidades equivalentes de PO₄³⁻.

Además de comparar los escenarios, el master compromete la identificación de las etapas que generan las mayores cargas ambientales.

### 4.2 Procesos, variables y datos comprometidos

Los elementos rectores relevantes para comprobar el cumplimiento son:

- generación de estiércol fresco y uso de agua de lavado;
- humedad, materia seca, cenizas, sólidos volátiles y nitrógeno total;
- nitrógeno total de estiércol fresco, aguas verdes y purines;
- flujos másicos por escenario y etapa;
- emisiones de CH₄, N₂O, NH₃ y NO₃⁻; el desarrollo posterior también incorpora CO₂ para el lombricompostaje;
- pérdidas directas e indirectas de nitrógeno por volatilización y lixiviación;
- factores de emisión y ecuaciones del IPCC (2019), además de factores bibliográficos aplicables al lombricompostaje;
- factores de caracterización de calentamiento global y eutrofización;
- impactos por etapa y totales por escenario;
- comparación de los dos escenarios e identificación de etapas críticas.

### 4.3 Compromisos metodológicos explícitos

El master indica, entre otros compromisos:

1. usar registros de los seis meses previos para estimar la generación promedio de estiércol;
2. realizar, durante seis meses y con frecuencia de tres veces, el muestreo para materia seca, sólidos volátiles y nitrógeno total;
3. formar tres muestras compuestas a partir de cinco muestras simples tomadas al azar para los análisis descritos;
4. caracterizar el nitrógeno total del estiércol fresco, las aguas verdes y los purines;
5. aplicar ecuaciones IPCC para estimar emisiones directas e indirectas asociadas al manejo y a los suelos gestionados;
6. clasificar y caracterizar las emisiones en las dos categorías de impacto;
7. comparar los indicadores por etapa, integrar los resultados e identificar las etapas de mayor carga;
8. considerar la sensibilidad y la consistencia de los datos durante la interpretación.

Los puntos 2, 3, 4 y 8 son especialmente importantes porque su ejecución completa no queda evidenciada en los resultados actuales.

## 5. Análisis de la metodología desarrollada por objetivo

### 5.1 Objetivo específico 1: inventario de ciclo de vida

Las secciones metodológicas relacionadas son principalmente: 1, *Enfoque metodológico general del ACV*; 3, *Meta, alcance y unidad funcional*; 4 a 7, escenarios, fronteras y etapas; 8, *Datos de entrada usados para el ICV*; 9, *Muestreo y análisis de laboratorio*; 10, *Organización y procesamiento de datos*; 11 a 14, cálculos fisicoquímicos y conservación de cenizas; 15, *Construcción de flujos del inventario*; 16, *Normalización respecto a la unidad funcional*; 17 y 18, aplicación de ecuaciones IPCC y estimación de emisiones.

Los procedimientos descritos incluyen:

- organización de datos por escenario, etapa, material y variable;
- caracterización de estiércol fresco, material precompostado, aguas verdes y purines;
- cálculo de humedad, materia seca, cenizas, sólidos volátiles y nitrógeno total;
- estimación de la masa seca remanente mediante conservación de cenizas;
- construcción de flujos anuales y masas equivalentes;
- uso de la equivalencia operativa de 1 L de agua con 1 kg equivalente;
- estimación de emisiones por etapa mediante ecuaciones IPCC y factores bibliográficos para A2: Lombricompostaje;
- normalización declarada respecto de 1 kg de estiércol fresco.

Los productos metodológicos esperados son la caracterización de materiales, el inventario de flujos, los parámetros y factores del modelo y las emisiones desagregadas por etapa y sustancia. En el documento se materializan como Tablas 1 a 4, Figura M1 y Tablas M1 a M3 de los apéndices internos.

### 5.2 Objetivo específico 2: evaluación del impacto ambiental

Las secciones relacionadas son 18, *Estimación de emisiones*; 19, *Evaluación de impacto de ciclo de vida*; 20, *Supuestos metodológicos*; y 21, *Limitaciones metodológicas*.

El procedimiento convierte las emisiones de CH₄, N₂O, NH₃, NO₃⁻ y CO₂ en indicadores equivalentes mediante factores de caracterización. Los impactos se calculan primero por etapa, se agregan por escenario y se comparan mediante diferencias absolutas y porcentuales. Los productos esperados son:

- potencial de calentamiento global por etapa y escenario;
- potencial de eutrofización por etapa y escenario;
- totales por escenario;
- diferencias absolutas y relativas entre escenarios;
- identificación de las etapas de mayor contribución.

La metodología desarrollada menciona supuestos y limitaciones, pero no presenta un procedimiento operativo de análisis de sensibilidad ni criterios concretos para evaluar la consistencia, pese a que el master los menciona en la fase de interpretación.

## 6. Análisis de los resultados por objetivo

### 6.1 Evidencia para el objetivo específico 1

Las secciones 1 a 4 de resultados aportan caracterización, flujos, parámetros y emisiones. La evidencia principal es:

- **Tabla 1**, Figuras 1 y 2, y **Tabla R1**: caracterización fisicoquímica de estiércol fresco y precompostado;
- **Tabla 2**, Figura 3, **Tabla R2** y Figura R2: flujos del inventario por etapa;
- **Tabla 3**, **Tablas R3 y R4**: parámetros y factores usados en el modelo;
- **Tabla 4**, Figura 4, **Tabla R5** y Figuras R3 a R6: emisiones por escenario, etapa y sustancia.

Hallazgos numéricos relevantes:

- A4 presenta 71 789,81 kg eq/año y B2 presenta 76 557,27 kg eq/año;
- el Escenario A presenta 9,55 kg CH₄/año, 0,79 kg N₂O/año, 5,23 kg NH₃/año, aproximadamente 19,05 kg NO₃⁻/año y 33,65 kg CO₂/año;
- el Escenario B presenta 80,59 kg CH₄/año, 0,31 kg N₂O/año, 6,35 kg NH₃/año y aproximadamente 23,16 kg NO₃⁻/año;
- B1 concentra la mayor emisión de CH₄; A1 concentra la mayor emisión de N₂O; A2 reporta CO₂ mediante un factor bibliográfico.

Existe un inventario amplio y estructurado, pero la evidencia es **parcial** frente a los compromisos completos del master: la Tabla R1 muestra una única jornada (`2025-11-10`), dos muestras de sólidos y dos de nitrógeno, y solo estiércol fresco y precompostado. No demuestra las tres campañas durante seis meses, las tres muestras compuestas formadas con cinco muestras simples ni la caracterización de nitrógeno de aguas verdes y purines. Aunque aparecen valores de nitrógeno para A4 y B2 en R3, su procedencia experimental no queda trazada en R1.

### 6.2 Evidencia para el objetivo específico 2

Las secciones 5 a 7 presentan impactos por etapa, totales y comparación. La evidencia principal es:

- **Tabla 5**, Figuras 5 y 6, y **Tabla R6**: impactos por etapa;
- **Tabla 6**, **Tabla R7**, Figuras R7 y R8: impactos totales por escenario;
- **Tabla 7**, Figura 7 y **Tabla R8**: diferencias absolutas y porcentuales entre escenarios.

Hallazgos numéricos principales:

- Escenario A: 478,78 kg CO₂-eq/año y 3,64 kg PO₄-eq/año;
- Escenario B: 1 787,19 kg CO₂-eq/año y 4,42 kg PO₄-eq/año;
- diferencia B menos A: 1 308,41 kg CO₂-eq/año (273,28 % respecto de A) y 0,785 kg PO₄-eq/año (21,58 % respecto de A);
- B1 es la etapa de mayor contribución en ambas categorías; dentro del Escenario A, A1 es la mayor contribuyente al calentamiento global y también supera las otras etapas de A en eutrofización.

La evidencia cuantitativa responde materialmente al objetivo, pero **requiere revisión** antes de considerarla lista para conclusiones. Los resultados solo muestran unidades anuales, mientras la metodología afirma que la comparación se normalizó a la unidad funcional de 1 kg de estiércol fresco. No se presenta el cálculo normalizado ni se demuestra que los escenarios comparados representen el mismo flujo de referencia. Tampoco se muestra un análisis de sensibilidad o consistencia.

## 7. Matriz de trazabilidad

| Objetivo del master | Metodología relacionada | Resultados relacionados | Tablas/Figuras relevantes | Estado de cumplimiento | Observaciones |
|---|---|---|---|---|---|
| **OE1.** Realizar el inventario para el ACV del estiércol bovino manejado mediante lombricompostaje y aplicado como purines directamente en campos de pastoreo. | Secciones 3 a 18: unidad funcional; escenarios y fronteras; entradas; muestreo; cálculos de humedad, materia seca, cenizas, sólidos volátiles y N; conservación de cenizas; flujos; normalización; ecuaciones IPCC y emisiones. | Secciones 1 a 4: caracterización, flujos, parámetros y emisiones por etapa y escenario. | Metodología: Tablas 1–4, M1–M3 y Figura M1. Resultados: Tablas 1–4, R1–R5; Figuras 1–4 y R1–R6. | **PARCIAL** | El inventario existe y cubre ambos escenarios, pero no se evidencia el plan de muestreo completo ni la caracterización líquida comprometida. Los resultados no muestran valores normalizados por la unidad funcional. |
| **OE2.** Evaluar el impacto ambiental del estiércol bovino manejado mediante lombricompostaje y aplicado como purines directamente en campos de pastoreo. | Secciones 18 a 21: emisiones, caracterización, agregación por escenario, comparación, supuestos y limitaciones. | Secciones 5 a 7: impactos por etapa, totales y comparación de escenarios. | Tablas 5–7 y R6–R8; Figuras 5–7 y R7–R8. | **REQUIERE REVISIÓN** | Hay resultados para calentamiento global y eutrofización e identificación de etapas críticas, pero la comparación se expresa solo por año y no demuestra la normalización declarada a 1 kg de estiércol fresco. Falta sensibilidad/consistencia y persisten discrepancias puntuales de trazabilidad y redondeo. |

**Resumen de estados:** 0 COMPLETOS; 1 PARCIAL; 0 NO EVIDENCIADOS; 1 REQUIERE REVISIÓN.

## 8. Inconsistencias detectadas

### 8.1 Compromisos del master no demostrados

1. **Diseño de muestreo.** El master establece tres repeticiones durante seis meses y muestras compuestas formadas a partir de cinco muestras simples. R1 documenta una sola fecha y dos muestras. La diferencia puede obedecer a información aún no incorporada, pero el documento actual no permite comprobarlo.
2. **Caracterización de líquidos.** El master promete N total de aguas verdes y purines. R1 solo contiene estiércol fresco y precompostado. Los valores 0,0072 % para A4 y 0,0114 % para B2 aparecen en R3 sin que R1 muestre las observaciones que los sustentan.
3. **Sensibilidad y consistencia.** El master dice que estos aspectos se considerarían en la interpretación. No se encontró un método operativo ni resultados de sensibilidad o consistencia.

### 8.2 Unidad funcional y base de comparación

La metodología afirma repetidamente que flujos, emisiones e impactos fueron normalizados a 1 kg de estiércol fresco. Sin embargo, todas las tablas de resultados relevantes presentan cantidades anuales. No aparece una tabla con unidades tales como kg de emisión o kg equivalente de impacto por kg de estiércol fresco. Además, los totales de masa equivalente de los escenarios no son iguales, por lo que la comparación anual no demuestra por sí misma equivalencia funcional.

**Implicación:** la dirección de los resultados anuales es descriptiva de la operación modelada, pero no debería presentarse todavía como comparación concluyente del desempeño ambiental por unidad funcional sin reconstruir o mostrar la normalización.

### 8.3 Correspondencia entre instalaciones reales y sistemas de manejo modelados

El master describe aguas verdes almacenadas bajo techo durante dos o tres días en un tanque y el escenario alternativo almacenado también en tanque. La metodología desarrollada asigna a A3, A4, B1 y B2 el sistema de manejo denominado “laguna anaerobia descubierta”, con MCF de 80 %. No se encontró una justificación explícita de la equivalencia entre el tanque descrito y ese sistema IPCC; además, las etapas de aplicación en suelo conservan esa asignación en la tabla de parámetros aunque las ecuaciones descritas para aplicación corresponden a suelos gestionados.

**Implicación:** esta selección influye directamente en las emisiones, especialmente el CH₄ de B1, y debe justificarse o revisarse antes de usar la diferencia entre escenarios como base de una conclusión.

### 8.4 Cambios o ampliaciones metodológicas respecto al master

- La metodología desarrollada incorpora una estimación de conservación de cenizas para obtener la masa seca remanente del material precompostado. Es una ampliación útil para el inventario, pero no aparece como compromiso explícito del master y debe quedar explicada como desarrollo metodológico posterior, no como requisito original.
- Para A2 se usan factores de emisión de Jjagwe et al. (2019), además del esquema IPCC. El uso está relacionado con el objetivo, pero la expresión visible “Factor Factor medido” es terminológicamente defectuosa y puede inducir a pensar que se trata de una medición propia cuando es un factor bibliográfico.
- Se incorpora CO₂ de A2 en calentamiento global. La ampliación está vinculada al objetivo, pero conviene aclarar el tratamiento del CO₂ de origen biogénico y su coherencia con la categoría evaluada antes de concluir.

### 8.5 Datos metodológicos sin reflejo suficiente en resultados

- La metodología declara muestras líquidas de aguas verdes y purines, pero sus observaciones de laboratorio no aparecen en R1.
- Declara normalización a la unidad funcional, pero no reporta resultados normalizados.
- Declara organización trazable desde mediciones hasta ecuaciones; sin embargo, R1 no permite seguir el origen de todos los valores de N empleados en R3.
- Declara consideración de sensibilidad y consistencia en la interpretación original, pero no presenta productos correspondientes.

### 8.6 Resultados sin relación con objetivos

No se identificaron bloques sustantivos de resultados completamente ajenos a los objetivos. La caracterización, los flujos, parámetros, emisiones e impactos son necesarios para OE1 u OE2. La Tabla R10 de correspondencia cumple una función documental auxiliar, no un resultado investigativo adicional.

### 8.7 Inconsistencias internas puntuales

- El texto de la sección 4 redondea NO₃⁻ a 19,06 kg/año para A y 23,17 kg/año para B, mientras la Tabla 4 muestra 19,05 y 23,16; R5 permite calcular aproximadamente 19,0519 y 23,1640. Debe establecerse un criterio único de redondeo.
- R6 muestra para A2 una emisión de N₂O igual a 0 kg, pero un resultado equivalente de 0,004 kg CO₂-eq/año. Aunque sea un efecto del redondeo, la presentación impide verificar la multiplicación con los valores visibles.
- En metodología y resultados aparece “Factor Factor medido” y variantes repetidas. No altera por sí solo el alcance, pero oscurece la procedencia bibliográfica del factor.
- La metodología desarrollada resume el sitio como una lechería de Turrialba sin conservar en ese apartado la identificación institucional detallada de la Sede del Atlántico. No cambia necesariamente el universo de estudio, pero conviene restituir la trazabilidad del sitio en la futura integración.

## 9. Vacíos pendientes

Antes de redactar conclusiones se necesita, como mínimo, comprobar documentalmente:

1. si existen las tres campañas de muestreo comprometidas y dónde están sus resultados;
2. si se formaron las muestras compuestas conforme al master o si hubo un cambio de diseño que deba declararse como desviación;
3. cuáles son los resultados primarios de N total para aguas verdes y purines y cómo alimentan A4 y B2;
4. cuál es el denominador exacto usado para normalizar cada escenario a 1 kg de estiércol fresco;
5. los resultados de emisiones e impactos expresados por unidad funcional;
6. la justificación de representar tanques de almacenamiento y etapas asociadas mediante factores de una laguna anaerobia descubierta;
7. la razón para asignar el sistema de almacenamiento a las etapas de aplicación, o la confirmación de que las ecuaciones de suelo sustituyen efectivamente esa asignación;
8. un control de sensibilidad y consistencia, o una declaración explícita y justificada de que no se realizó;
9. la política de inclusión del CO₂ del lombricompostaje en calentamiento global;
10. la conciliación de redondeos y del valor residual de N₂O en A2.

## 10. Preparación para redactar conclusiones

| Objetivo | Evidencia disponible | Preparación actual | Uso prudente en futuras conclusiones |
|---|---|---|---|
| OE1: inventario | Amplia evidencia de flujos, parámetros y emisiones para A1–A4 y B1–B2. | **No está listo para cierre definitivo.** Puede afirmarse provisionalmente que se construyó un inventario, pero no que se cumplió íntegramente el diseño de datos del master. | Tras completar la trazabilidad, podrían sintetizarse los flujos dominantes y las sustancias dominantes por etapa. La ausencia de campañas o datos líquidos debe tratarse como vacío o limitación, no como hallazgo ambiental. |
| OE2: evaluación de impacto | Impactos por etapa y escenario para calentamiento global y eutrofización, con diferencias absolutas y porcentuales. | **No está listo para una conclusión comparativa definitiva.** La evidencia anual permite una lectura operativa provisional, pero falta demostrar comparabilidad por unidad funcional y revisar la selección del sistema de manejo. | Si se valida la base funcional y los factores, las cargas totales, las diferencias A–B y la identificación de B1 y A1 como etapas dominantes serían los principales insumos para conclusiones. |

### 10.1 Resultados que probablemente alimentarán las conclusiones

Una vez resueltos los vacíos, los resultados con mayor potencial conclusivo son:

- inventario de flujos por las seis etapas;
- emisiones dominantes de CH₄ y N₂O por etapa;
- impactos de calentamiento global y eutrofización por etapa;
- impactos totales comparables por unidad funcional;
- magnitud y sentido de las diferencias entre A y B;
- identificación de las etapas críticas B1 y A1, si se confirma la pertinencia de los factores asignados.

### 10.2 Elementos que no deberían convertirse directamente en conclusiones

- la falta de campañas o de trazabilidad de muestras: corresponde a limitaciones y acciones pendientes;
- la representatividad de muestras, duración del muestreo y uso de equivalencias de masa: corresponde a limitaciones metodológicas;
- propuestas para cambiar factores, ampliar monitoreo o mejorar instalaciones: corresponden a recomendaciones;
- explicaciones causales no probadas de por qué un escenario resulta mayor: corresponden a discusión;
- cualquier afirmación de superioridad ambiental basada solo en totales anuales antes de demostrar equivalencia funcional;
- cualquier generalización a otras lecherías, porque el alcance corresponde al sistema modelado y sus condiciones.

## 11. Recomendaciones antes de generar el documento de conclusiones

1. **Detener la redacción de conclusiones comparativas** hasta documentar la normalización a la unidad funcional.
2. **Conciliar el diseño de muestreo** del master con las observaciones efectivamente disponibles. Si no se ejecutó completo, declararlo como desviación o limitación sin alterar el objetivo original.
3. **Incorporar o localizar la evidencia de aguas verdes y purines** que sustenta los valores de N usados en el modelo.
4. **Revisar y justificar la correspondencia IPCC** entre tanque, almacenamiento líquido, aplicación al suelo y los factores seleccionados.
5. **Ejecutar o documentar la sensibilidad y consistencia** previstas en el master, priorizando los factores que controlan CH₄ en B1, nitrógeno, volumen de agua y equivalencia de masa.
6. **Aclarar el tratamiento del CO₂** atribuido a A2 antes de consolidar el potencial de calentamiento global.
7. **Conciliar redondeos y trazabilidad aritmética** entre tablas resumidas y apéndices.
8. Después de resolver lo anterior, **actualizar primero los generadores y los documentos de metodología/resultados** conforme a las reglas del repositorio; solo entonces preparar conclusiones. Esta recomendación no autoriza cambios dentro de la presente tarea diagnóstica.

## 12. Dictamen diagnóstico

La estructura actual mantiene una alineación temática clara con el master: estudia los dos escenarios previstos, construye un inventario y presenta calentamiento global y eutrofización por etapa y escenario. No obstante, la trazabilidad investigativa todavía no permite declarar cumplimiento completo. El principal problema no es la ausencia total de resultados, sino la falta de demostración de que los resultados comparativos corresponden a la unidad funcional definida y de que los datos primarios satisfacen el muestreo y la caracterización comprometidos. Por ello, OE1 se clasifica como **PARCIAL** y OE2 como **REQUIERE REVISIÓN** antes de redactar conclusiones definitivas.
