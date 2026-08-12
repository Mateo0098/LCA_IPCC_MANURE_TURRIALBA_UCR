# Decisiones metodológicas del TFG

## 1. Propósito del documento

Este documento interno registra decisiones metodológicas validadas por el investigador para el TFG sobre el análisis de ciclo de vida del manejo de estiércol bovino en la lechería de la Sede del Atlántico de la Universidad de Costa Rica. Estas decisiones deben conservarse en futuras regeneraciones documentales y ejecuciones del modelo, salvo que el investigador autorice expresamente una modificación posterior. Este archivo no sustituye la metodología académica de la tesis.

## 2. Unidad funcional

- La unidad funcional es **1 kg de estiércol fresco manejado**.
- El flujo anual común de referencia es aproximadamente 26 278,725181 kg de estiércol fresco/año.
- El flujo anual representa la escala operacional utilizada para anualizar el inventario; no redefine la unidad funcional.
- No debe describirse la unidad funcional como estiércol únicamente recolectado ni como 1 kg/año.

## 3. Fuente operativa Sánchez-Romero y Brenes-Gamboa (2026)

Sánchez-Romero y Brenes-Gamboa (2026) estudiaron la misma lechería de la Sede del Atlántico de la Universidad de Costa Rica evaluada en este TFG. Los parámetros operativos publicados utilizados son:

- peso vivo promedio: 396,6 kg/animal;
- población media: 18 vacas en ordeño;
- permanencia aproximada en sala: 3,5 h/día;
- estiércol fresco recolectado: 2,7 kg/animal;
- estiércol fresco recolectado total: 17 525,1 kg/año;
- agua de lavado: 686,5 L/día, equivalente a 250 572,5 L/año.

Los 17 525,1 kg/año representan el estiércol efectivamente recolectado durante las actividades de ordeño, no la excreción fisiológica total diaria.

## 4. Supuesto de generación de estiércol

El artículo citado refiere bibliográficamente un intervalo de producción diaria de estiércol equivalente al 7–10 % del peso vivo. El presente TFG adoptó el límite inferior de 7 % como supuesto conservador para evitar sobreestimar una fracción no medida directamente.

El balance derivado produjo aproximadamente 33,31 % de estiércol remanente y 66,69 % de estiércol recolectado. Estas fracciones no son mediciones directas realizadas por Sánchez-Romero y Brenes-Gamboa (2026); son estimaciones metodológicas del TFG.

## 5. Balance entre escenarios

En el Escenario A:

- 17 525,1 kg/año ingresan primero a A1: Precomposteo;
- la masa resultante de A1 continúa posteriormente hacia A2: Lombricompostaje;
- 8 753,625181 kg/año constituyen el remanente estimado incorporado a las aguas verdes;
- la suma corresponde al flujo común de 26 278,725181 kg/año.

En el Escenario B, el 100 % del flujo común de 26 278,725181 kg/año ingresa a B1: Almacenamiento de purines. Ambos escenarios representan alternativas para el mismo flujo anual de referencia.

## 6. Representación A3/B1 frente a A4/B2

### A3 y B1: manejo del estiércol

A3: Almacenamiento de aguas verdes y B1: Almacenamiento de purines utilizan las ecuaciones IPCC asociadas con el manejo del estiércol.

- En A3, la masa de actividad es la masa de estiércol remanente sometida al sistema de manejo.
- En B1, la masa de actividad es la totalidad del estiércol teóricamente depositado.
- En ambas etapas se utiliza la caracterización química del estiércol fresco y los factores del sistema IPCC seleccionado.
- El agua de lavado se excluye de la masa de actividad de estas ecuaciones.

El agua existe físicamente en los sistemas de almacenamiento. Su exclusión significa únicamente que no se introduce como masa de estiércol en las ecuaciones IPCC de manejo.

### A4 y B2: aplicación del efluente al suelo

A4: Aplicación de aguas verdes en campos de pastoreo y B2: Aplicación de purines en campo de pastoreo son etapas subsecuentes de aplicación del efluente al suelo y utilizan las ecuaciones asociadas con suelos gestionados según la implementación vigente.

- En A4, el flujo aplicado integra el agua de lavado y el estiércol remanente incorporado a las aguas verdes; se utiliza la caracterización química específica de las aguas verdes.
- En B2, el flujo aplicado integra el agua de lavado y la totalidad del estiércol incorporado al purín; se utiliza la caracterización química específica del purín.

## 7. Adaptación para eutrofización

Las cantidades de nitrógeno se definen de la siguiente manera:

- `N_G`: N remanente de la ruta de volatilización después de descontar el N₂O-N indirecto.
- `N_L`: N remanente de la ruta de lixiviación después de descontar el N₂O-N indirecto.
- `N_eut = N_G + N_L`: pool de N remanente considerado potencialmente contribuyente a eutrofización.

El supuesto metodológico del TFG asigna:

- 50 % de `N_eut` a N asociado a NH₃;
- 50 % de `N_eut` a N asociado a NO₃⁻.

Después de esta asignación se aplican las conversiones estequiométricas de N a masa de NH₃ y NO₃⁻.

## 8. Uso de Komakech et al. (2016)

Komakech et al. (2016) constituye el antecedente del reparto 50/50. El texto de dicho estudio se refiere al N del estiércol que alcanza cuerpos de agua y asume su transformación en 50 % nitrato y 50 % amoníaco.

La aplicación de ese reparto al pool integrado `N_eut` es una adaptación metodológica propia del presente TFG. No debe atribuirse a Komakech et al. la ecuación completa utilizada en este proyecto, ni debe atribuirse al IPCC la adaptación para eutrofización.

## 9. Interpretación ambiental del supuesto de eutrofización

- El enfoque considera conservadoramente el N remanente como potencialmente contribuyente a eutrofización.
- No implica que el 100 % del N volatilizado alcance físicamente cuerpos de agua.
- NH₃ y NO₃⁻ son representaciones utilizadas para caracterizar el pool `N_eut` dentro del ACV; no constituyen una predicción directa de la especiación química final en el ambiente.
- La presencia de NO₃⁻ en B1 no implica lixiviación física cuando `N_L = 0`, porque el NO₃⁻ equivalente procede del supuesto de reparto de `N_eut`.

## 10. Decisiones que no deben cambiarse automáticamente

No deben cambiarse automáticamente:

- los sistemas IPCC seleccionados;
- los factores IPCC y de caracterización;
- el tratamiento del CO₂ del lombricompostaje;
- la unidad funcional;
- el supuesto de 7 %;
- el balance 66,69/33,31;
- la adaptación basada en `N_eut`;
- el reparto 50/50 entre N asociado a NH₃ y N asociado a NO₃⁻.

Estas decisiones solo deben modificarse por decisión expresa del investigador o como resultado de una revisión académica posterior autorizada.

### Representación aprobada de A2

A2: Lombricompostaje utiliza las ecuaciones IPCC de manejo de estiércol y la
categoría `composting_pasive` (Composting – Passive Windrow) como aproximación
al proceso estudiado. La selección responde al manejo de material sólido sin
reactor cerrado, aireación forzada ni volteo mecánico intensivo, con movilización
y aireación no intensiva asociada a la actividad de las lombrices.

Para A2 se establece `FracLeachMS = 0` como parámetro específico del sistema;
no modifica el valor genérico de `composting_pasive`. Vargas Sarmiento (2023)
documentó para el mismo lombricario camas bajo techo, completamente construidas
con piso y paredes de cemento y sin drenajes. El riego descrito en esa tesis
perteneció a su protocolo experimental para mantener una humedad objetivo. De
forma independiente, las giras del presente TFG registraron exclusión de lluvia
directa y ausencia de riego operacional regular. En consecuencia, no se modela
una pérdida de N hacia el ambiente por lixiviación durante A2; esto no equivale
a afirmar que no exista movimiento de agua dentro del sustrato.

### Contraste bibliográfico experimental de A2

La metodología oficial de A2 continúa siendo el modelo IPCC con la categoría
`composting_pasive` y `FracLeachMS = 0`. Los datos de Jjagwe et al. (2019;
DOI 10.3390/su11195173) se utilizan exclusivamente como contraste experimental
bibliográfico para interpretar A2; no constituyen un modelo `medido`, no
sustituyen el inventario oficial y no crean un segundo ACV.

La frontera común es la materia seca del estiércol precompostado al ingreso de
A2, derivada como `masa_humeda_A2 × fraccion_materia_seca_A2`. El contraste
principal incluye CH₄ y N₂O directo (`N2O_ec2`) por kg de esa materia seca. Las
vías indirectas de N₂O permanecen en el inventario oficial, pero se excluyen del
contraste experimental directo. El indicador climático armonizado incluye solo
CH₄ y N₂O directo y aplica a ambos lados los factores de caracterización
vigentes del TFG; no se denomina impacto climático total.

Para Jjagwe et al. se adoptan 7,6 g CH₄/kg MS y 39,43 mg N₂O/kg MS. El valor de
N₂O resuelve explícitamente una inconsistencia interna: el resumen presenta
`3,943 × 10⁻⁵ g/kg MS`, mientras los resultados, la Figura 3 y el GWP publicado
respaldan el orden de decenas de mg/kg MS. También se usa TKN inicial de 1,44 %
MS para el indicador complementario N₂O-N/N inicial. La pérdida atmosférica de
N de 18,18 % es solo un contraste conceptual y no se equipara con `FracGasMS`.

No se calcula eutrofización experimental: el NH₃ no fue detectado, el balance
atmosférico no quedó completamente especiado y la adaptación de `N_eut` del TFG
no representa una especiación experimental equivalente.

## 11. Estado provisional

La caracterización experimental activa es provisional: las variables sólidas metodológicamente comparables integran M1 y M2 con igual peso temporal; el N total de aguas verdes y purines procede únicamente de M2 mediante Kjeldahl; y la transformación de masa de estiércol fresco a precompostado integra los factores calculados primero para M1 y M2 por separado. La corrida del ACV fue regenerada con estos estimadores y se identifica expresamente como **PROVISIONAL M1–M2**. M3 permanece pendiente para completar la integración final según las reglas de la sección 14.

## 12. Regla para futuras regeneraciones

Las tablas, los gráficos, la metodología, los resultados, las conclusiones y la validación cruzada deben corresponder a una misma corrida vigente y conservar estas decisiones. Si se detecta una discrepancia entre los productos generados, la implementación del modelo y este archivo, debe reportarse al investigador antes de modificar cálculos, parámetros, factores, flujos o decisiones metodológicas.

## 13. Aclaraciones CIA sobre reporte de N y preparación de N/C

### Política de precisión y redondeo

- Para N de aguas verdes y purines, el CIA aclaró que reporta el resultado hasta el segundo decimal, tal como aparece en el informe.
- Los decimales adicionales almacenados en las celdas corresponden a la lectura que conserva el equipo. Deben mantenerse en la ingestión y en los cálculos para evitar redondeo prematuro y asegurar reproducibilidad.
- El redondeo se aplica únicamente en la presentación final, respetando la precisión de reporte del laboratorio.
- Los decimales adicionales no deben interpretarse ni describirse como mayor precisión analítica formal.
- No deben sustituirse por `0,01 %` valores internos diferentes que el informe muestre redondeados de la misma forma.

### N y C del estiércol precompostado

- El CIA determinó N y C por Dumas (combustión seca) después de secar la muestra a 80 °C durante 48 h y realizar la preparación establecida por su metodología.
- El CIA no determinó humedad a 105 °C como parte de ese análisis porque no fue solicitada.
- La humedad y materia seca del TFG proceden de ensayos gravimétricos independientes, con aproximadamente 10 g a 105 °C hasta masa constante o durante el tiempo establecido.
- El secado CIA a 80 °C es una condición de preparación para N/C; no debe mezclarse con la determinación gravimétrica del TFG a 105 °C.
- Para el uso aprobado en A2, el porcentaje de N se interpreta como concentración determinada sobre el material preparado/seco por el CIA. Esta interpretación metodológica no modifica el valor analítico integrado ni se extiende automáticamente al carbono.
- La fracción efectiva de N sobre la masa húmeda de precompostado se calcula como `N_fraction_wet = (n_ex_pct / 100) × (materia_seca_pct / 100)`, usando la materia seca gravimétrica integrada del TFG.
- El secado CIA a 80 °C y la determinación gravimétrica del TFG a 105 °C cumplen funciones distintas. La conversión no reconstruye ni corrige retrospectivamente posibles pérdidas de N durante la preparación CIA.
- El N Kjeldahl M2 del estiércol fresco, determinado directamente sobre una alícuota homogénea sin secado reportado, conserva su tratamiento vigente (`n_ex_pct / 100`). La conversión específica del precompostado tampoco se aplica a aguas verdes ni purines.

## 14. Integración temporal de jornadas

### Jerarquía estadística e igual peso temporal

La jerarquía de análisis es: réplica analítica → muestra compuesta → promedio de jornada → integración entre jornadas. Las réplicas analíticas no constituyen observaciones temporales independientes.

Para variables metodológicamente comparables, cada jornada aporta su promedio de jornada con igual peso temporal. La integración no se pondera por el número de réplicas analíticas ni por el número de muestras compuestas. Por tanto, aunque M1 contenga generalmente dos muestras compuestas y M2 o M3 contengan tres, cada jornada recibe el mismo peso temporal.

### Variables sólidas

Para N total, humedad, materia seca, cenizas y sólidos volátiles del estiércol fresco y del estiércol precompostado, M1, M2 y la futura M3 son integrables si mantienen compatibilidad metodológica. Actualmente, el valor provisional corresponde a la media de los promedios de M1 y M2.

El valor final requerirá obligatoriamente M1, M2 y M3 con métodos compatibles. Una combinación incompleta, como M1 + M3 o M2 + M3, no podrá considerarse final.

### N de aguas verdes y purines

En M1, el N de aguas verdes y purines corresponde a especiación, se conserva únicamente para trazabilidad y se excluye del estimador de N total. M2, determinado mediante Kjeldahl, es elegible. M3 será elegible si utiliza una metodología Kjeldahl compatible.

El valor final será la media de los promedios de M2 y M3; M1 no se incorporará. Hasta disponer de M3, el N líquido permanecerá en estado `pendiente_M3`.

### Variabilidad e inferencia estadística

La variabilidad intrajornada, calculada entre muestras compuestas, debe mantenerse separada de la variabilidad interjornada, calculada entre promedios de jornada. La desviación estándar interjornada no debe combinarse automáticamente con la desviación estándar intrajornada.

Con las jornadas actuales no se realizarán automáticamente ANOVA, pruebas t, pruebas de normalidad, modelos mixtos ni declaraciones de diferencia estadísticamente significativa. Las diferencias entre M1 y M2 tienen carácter exclusivamente descriptivo.

### Estado actual y relación con el ACV

La integración M1–M2 constituye la caracterización experimental provisional activa. Los parámetros elegibles se promueven hacia el ACV y la corrida resultante se identifica expresamente como **PROVISIONAL M1–M2**. Cuando exista M3 metodológicamente compatible, se actualizará la integración y se regenerará el mismo pipeline. No deben crearse perfiles históricos, snapshots del modelo ni pipelines paralelos para incorporar M3.

El factor de transformación de masa de estiércol fresco a estiércol precompostado se calcula primero de forma independiente para cada jornada a partir de sus promedios gravimétricos validados. Los factores de jornada reciben igual peso temporal y el parámetro integrado principal es `mass_ratio_precomp_over_fresh`. La pérdida porcentual integrada se deriva de ese factor mediante `(1 - mass_ratio_precomp_over_fresh) × 100`; no se promedia por una ruta independiente. El resultado M1–M2 es provisional y el valor definitivo requerirá M1, M2 y M3 metodológicamente elegibles.
