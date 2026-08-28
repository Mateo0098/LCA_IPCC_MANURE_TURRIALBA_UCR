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

El Escenario A mantiene dos corrientes físicamente separadas:

- la fracción paleada, correspondiente a 17 525,1 kg/año de estiércol fresco,
  ingresa a A1: Precomposteo y la masa resultante continúa hacia A2:
  Lombricompostaje;
- la fracción no paleada o remanente, correspondiente a 8 753,625181 kg/año,
  permanece en el piso, se incorpora al agua de lavado y continúa hacia A3:
  Almacenamiento de aguas verdes y A4: Aplicación de aguas verdes en campos de
  pastoreo;
- la suma corresponde al flujo común de 26 278,725181 kg/año.

El drenaje producido durante A1 no se representa como un flujo hacia A3. La
corriente de aguas verdes procede del estiércol no paleado que permanece en el
piso y se incorpora al lavado.

En el Escenario B, el 100 % del flujo común de 26 278,725181 kg/año ingresa a B1: Almacenamiento de purines. Ambos escenarios representan alternativas para el mismo flujo anual de referencia.

## 6. Representación de A1, A3 y B1

### A1: Precomposteo

A1 representa el precomposteo del estiércol paleado durante aproximadamente
cuatro semanas, equivalentes a unos 28 días. La pila permanece sin volteo
mecánico y sin aireación forzada. Durante esta etapa existe pérdida de humedad y
drenaje. El drenaje no dispone de una infraestructura estable de tratamiento y,
para la frontera del sistema modelado, termina depositándose sobre el suelo
agrícola o matorral adyacente. La recolección ocasional en recipientes no se
considera una operación representativa.

Se aprueba `Composting – Passive Windrow` como proxy de la categoría IPCC más
próxima a estas condiciones. La selección no afirma que el manejo real
constituya literalmente un windrow. Para vaca lechera se adoptan los siguientes
factores IPCC:

- MCF = 2,5 % para CH₄;
- EF3 = 0,005 kg N₂O-N/kg N para N₂O directo;
- FracGasMS = 0,45 únicamente como benchmark IPCC y control QA/QC de orden de
  magnitud;
- FracLeachMS = 0,04 para el N perdido mediante lixiviación o escorrentía.

Estos factores no se multiplican por `28/365` ni por otro ajuste lineal de
duración. FracGasMS no genera una segunda masa física de volatilización ni se
utiliza para calcular el N₂O indirecto objetivo. El precursor de EF4 es
exclusivamente `NH₃-N_explícito + NOx-N_explícito`.

FracLeachMS = 0,04 se interpreta como la fracción de N que abandona el sistema
de manejo A1 mediante drenaje, lixiviación o escorrentía:

`N_drenaje_A1 = N_manejado_A1 × FracLeachMS`

Ese N no se convierte directamente a NO₃⁻. Debido a que el drenaje termina
depositándose sobre el suelo agrícola o matorral adyacente, se representa como
una entrada de N al compartimento suelo. La secuencia física aprobada es:

`N_A1 → FracLeachMS → N_drenaje_A1 → suelo`

Una vez incorporado al suelo, el N del drenaje debe pasar al mismo marco IPCC
de suelos gestionados que se utiliza para representar otras entradas de N al
suelo. La secuencia metodológica objetivo es:

`N_drenaje_A1 → entrada de N al suelo → lixiviación/escorrentía IPCC desde suelo → N_lixiviado_suelo → conversión estequiométrica a NO₃⁻ → flujo explícito de NO₃⁻ en el ICV → caracterización EF 3.1`

## 15. Caracterización EF 3.1 e inventario operativo

Environmental Footprint 3.1 es el único método activo de caracterización de las
emisiones directas del modelo. Se aplican cambio climático (kg CO₂-eq),
eutrofización terrestre (mol N-eq) y eutrofización marina (kg N-eq). CH₄ se
representa como biogénico; N₂O como masa molecular; NH₃ y NOx como NO₂ se
asignan al aire; NO₃⁻ se asigna a agua dulce como receptor continental final.

El agua de lavado es pluvial y se almacena en un reservorio existente. No recibe
cargas municipales y no se duplica al pasar de almacenamiento a aplicación. La
bomba consume 53,2292 kWh/año en A3 o B1. El tractor y cañón consumen 182,50 L
diésel/año en A4 o B2; el cañón no recibe energía independiente. Los procesos
de fondo de electricidad y diésel permanecen pendientes.

Python es la fuente de verdad del foreground, ledger, normalización y control
EF 3.1 de emisiones directas. SimaPro caracterizará posteriormente el inventario
completo y sus resultados se reimportarán al mismo pipeline. El total de SimaPro
no se sumará a los impactos directos de Python si ya los contiene.

FracLeachMS y la fracción de lixiviación o escorrentía del modelo IPCC de
suelos representan fronteras físicas sucesivas y no deben confundirse.
FracLeachMS determina cuánto N sale del sistema de manejo de estiércol A1 y
llega al suelo. El parámetro de suelos determina posteriormente qué fracción
del N ya depositado abandona el suelo por lixiviación o escorrentía. Esta
secuencia no aplica dos veces una misma pérdida: el NO₃⁻ del ICV se deriva
únicamente de la segunda pérdida, desde el suelo, y no directamente del 4 % que
sale de A1.

Esta representación es coherente con la frontera de A4 y B2: en A1 el N llega
al suelo mediante una descarga incidental de drenaje, mientras que en A4 y B2
llega mediante la aplicación deliberada de efluentes. Una vez introducido en
el suelo, la lixiviación o escorrentía se representa mediante el marco IPCC de
suelos gestionados. Esta equivalencia de frontera no implica que los líquidos
tengan composición química idéntica ni que el drenaje de A1 haya sido
caracterizado químicamente.

### A3 y B1: manejo del estiércol

A3: Almacenamiento de aguas verdes y B1: Almacenamiento de purines se
representan como `Liquid/Slurry without natural crust`, no como `Uncovered
Anaerobic Lagoon`. En ambos casos la condición operativa representativa es una
tanqueta de concreto destinada a contener líquidos, bajo una estructura o
techo y con recepción periódica o continua de nuevas aguas durante el ciclo.
La superficie no tiene una cubierta directa ni un sellado hermético, no se
agita y no se documentó una costra natural. Predominan condiciones anaerobias.
La residencia operacional aproximada es de tres días.

Se adopta la zona climática `Tropical Wet`, de acuerdo con la caracterización
climática documentada para el sitio. Para CH₄ se utiliza MCF = 38 %, valor IPCC
de un mes para `Liquid/Slurry` en `Tropical Wet`, como proxy conservador de la
residencia real de unos tres días. Un mes es el menor periodo tabulado por IPCC
para esta parametrización. El valor de 38 % no se interpreta como una
estimación del MCF verdadero a tres días y no se escala como `38 % × 3/30` ni
mediante otra relación lineal.

La revisión de Møller, Sommer y Ahring (2004), VanderZaag et al. (2013),
VanderZaag (2018) y el Refinamiento 2019 del IPCC, volumen 4, capítulo 10,
respalda que la temperatura y el tiempo de retención influyen en el MCF y que
la respuesta temporal no debe simplificarse mediante una proporcionalidad
lineal. No se identificó una ecuación o un factor validado que proporcione
directamente un MCF oficial para una residencia de aproximadamente tres días.
El modelo o spreadsheet publicado por IPCC trabaja con una resolución temporal
que no ofrece directamente esa parametrización. Por ello se adopta el valor
tabulado de un mes como proxy conservador, sin cuantificar cuánto menor podría
ser el MCF real a tres días.

En operación normal no se modela una ruta de infiltración o lixiviación desde
la fosa contenida. Se establece FracLeachMS = 0 tanto para A3 como para B1. El
cero expresa la ausencia de esa ruta en la operación normal modelada; no afirma
que sean físicamente imposibles fugas accidentales.

Para el ledger de N/TAN se utiliza EF3 = 0, correspondiente a
`Liquid/Slurry without natural crust`. El modelo EMEP mineraliza antes del
almacenamiento el 10 % del N orgánico (`fmin = 0,10`) y calcula las pérdidas de
NH₃-N, NO-N y N₂-N sobre el TAN disponible. Se aprueba mantener `fmin = 0,10`
como aproximación EMEP por defecto y no escalarlo linealmente por los tres días.
La decisión metodológica está cerrada; la incertidumbre sobre su
representatividad para una residencia tan corta debe acompañar los resultados.

- En A3, la masa de actividad es la masa de estiércol remanente sometida al sistema de manejo.
- En B1, la masa de actividad es la totalidad del estiércol teóricamente depositado.
- En ambas etapas se utiliza la caracterización química del estiércol fresco y los factores del sistema IPCC seleccionado.
- El agua de lavado se excluye de la masa de actividad de estas ecuaciones.

El agua existe físicamente en los sistemas de almacenamiento. Su exclusión significa únicamente que no se introduce como masa de estiércol en las ecuaciones IPCC de manejo.

### A4 y B2: aplicación del efluente al suelo

A4: Aplicación de aguas verdes en campos de pastoreo y B2: Aplicación de
purines en campo de pastoreo representan la aplicación al suelo de estiércol
líquido previamente manejado. No representan excretas depositadas directamente
por animales durante el pastoreo. A4 recibe exactamente el N total y el TAN que
salen de A3; B2 recibe exactamente los que salen de B1. Las mediciones de aguas
verdes y purines se conservan como benchmarks y no reinicializan esos pools.

La volatilización de NH₃ durante la aplicación utiliza el factor EMEP/EEA Tier
2 para `dairy cattle slurry`, 0,55 kg NH₃-N/kg TAN aplicado. El NOx utiliza el
factor Tier 1 de EMEP/EEA para N aplicado en fertilizante, estiércol y excretas:
0,04 kg NO₂/kg N aplicado; para el ledger se convierte a N mediante 14/46. El
precursor del N₂O indirecto por volatilización es exclusivamente la suma de
NH₃-N y NOx-N explícitos.

El N₂O directo y la lixiviación/escorrentía del suelo se calculan con el marco
IPCC del capítulo 11 y conservan como base el N de estiércol aplicado, no el N
remanente después de la volatilización. El N realmente lixiviado o escurrido se
convierte a NO₃⁻ mediante 62/14; el N₂O indirecto derivado mediante EF5 no se
descuenta después de esa masa de NO₃⁻.

## 7. Arquitectura objetivo del ICV nitrogenado

### Retiro de la adaptación artificial 50/50

Queda retirada como metodología objetivo vigente la adaptación que sumaba
`N_G + N_L` en un pool `N_eut` y asignaba artificialmente 50 % a N asociado a
NH₃ y 50 % a N asociado a NO₃⁻. Esa adaptación no pertenece al IPCC y no debe
utilizarse para construir el nuevo ICV.

El pipeline productivo representa rutas y especies reactivas explícitas sin
reparto 50/50. Las funciones históricas que construían `N_eut` y lo dividían en
partes iguales fueron retiradas de la ruta ejecutable. El módulo canónico del
ledger alimenta directamente las seis etapas y el orquestador principal.

Komakech et al. (2016) permanece como antecedente bibliográfico del supuesto
histórico, pero no valida la construcción integrada `N_eut` ni una especiación
general del ICV. La adaptación histórica tampoco debe atribuirse al IPCC.

### Ledger secuencial de N total y TAN

El N total es el ledger físico principal. El TAN es un subpool contable dentro
del N total requerido por EMEP. En la frontera de estiércol fresco se establece
`TAN/N = 0,60`, valor para vaca lechera de EMEP/EEA 2023. En todo momento debe
cumplirse `0 ≤ TAN ≤ N_total`; A2, A4 y B2 reciben ambos pools de la etapa
anterior y nunca se reinicializan con mediciones intermedias.

Las pérdidas EMEP definidas sobre TAN —NH₃-N, NO-N y N₂-N— reducen a la vez TAN
y N total. Las pérdidas IPCC definidas sobre N total reducen N total, pero no
TAN automáticamente si la fuente no asigna la pérdida a ese pool. Por tanto,
el N₂O-N directo IPCC y el drenaje de A1 se descuentan una sola vez de N total,
sin partición proporcional ni descuento automático de TAN. N₂ permanece como
pérdida física central del ledger, aunque no se caracteriza en LCIA.

En A1 se aplican sobre TAN los factores EMEP de almacenamiento sólido: 0,32 kg
NH₃-N/kg TAN, 0,010 kg NO-N/kg TAN y 0,300 kg N₂-N/kg TAN. En A2 el NH₃ procede
de Komakech et al. (2016), 12,8 g NH₃/Mg de residuo orgánico de entrada, y NO y
N₂ utilizan provisionalmente los factores EMEP sólidos porque EMEP no contiene
una categoría explícita de lombricompostaje. El N₂O directo de A1 y A2 se
calcula una sola vez con EF3 IPCC = 0,005 kg N₂O-N/kg N total de entrada.

En A3 y B1, tras la mineralización EMEP, se aplican sobre TAN disponible los
factores `slurry`: 0,25 kg NH₃-N/kg TAN, 0,0001 kg NO-N/kg TAN y 0,003 kg
N₂-N/kg TAN. EF3 y FracLeachMS son cero. Fugas, reboses y pérdidas accidentales
no se representan como lixiviación sistemática.

FracGasMS se conserva exclusivamente como benchmark IPCC y control de orden de
magnitud. El `FracGas_modelado` se calcula como `(NH₃-N + NOx-N) / N_total_in`;
no se fuerza coincidencia. EF4 utiliza exclusivamente el precursor explícito
`NH₃-N + NOx-N`; FracGasMS no se utiliza para calcular el N₂O indirecto objetivo.

Las concentraciones experimentales de precompostado, aguas verdes y purines se
mantienen como benchmarks independientes. Para A4/B2 se calcula además una
concentración teórica diluida como `N_propagado / masa_total_mezcla`, usando los
flujos anuales de estiércol y agua de lavado. Es una comparación diagnóstica de
plausibilidad química, no una validación estricta de M2, porque no reconstruye
la dilución, lluvia, animales, residencia ni posibles reboses del día muestreado.

## 8. Decisiones que no deben cambiarse automáticamente

No deben cambiarse automáticamente:

- los sistemas IPCC seleccionados;
- los factores IPCC y de caracterización;
- el tratamiento del CO₂ del lombricompostaje;
- la unidad funcional;
- el supuesto de 7 %;
- el balance 66,69/33,31;
- la separación física de las dos corrientes del Escenario A;
- los proxies y factores IPCC aprobados para A1, A3 y B1;
- el retiro del reparto 50/50 como metodología objetivo.

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

No se calcula eutrofización experimental: el NH₃ no fue detectado y el balance
atmosférico no quedó completamente especiado. El reparto histórico basado en
`N_eut`, ya retirado como metodología objetivo, tampoco representaba una
especiación experimental equivalente.

### N retornado en A4/B2

En la aplicación al suelo, `N_returned_EMEP = N_applic - NH3-N_application` representa exclusivamente el N que EMEP considera retornado al suelo después de la volatilización de NH3. NOx-N, N2O-N directo y lixiviación/escorrentía no se descuentan de esta variable. El ledger mantiene por separado `N_soil_remaining`, una cantidad contable para el cierre físico después de NH3-N, NOx-N, N2O-N directo y N lixiviado/escorrentía; esta segunda variable no es una definición oficial EMEP ni IPCC y no reemplaza N aplicado como base de EF1 o FracLEACH.

## 9. Estado provisional

La caracterización experimental activa es provisional: las variables sólidas metodológicamente comparables integran M1 y M2 con igual peso temporal; el N total de aguas verdes y purines procede únicamente de M2 mediante Kjeldahl; y la transformación de masa de estiércol fresco a precompostado integra los factores calculados primero para M1 y M2 por separado. La corrida del ACV fue regenerada con estos estimadores y se identifica expresamente como **PROVISIONAL M1–M2**. M3 permanece pendiente para completar la integración final según las reglas de la sección 12.

## 10. Regla para futuras regeneraciones

Las tablas, los gráficos, la metodología, los resultados, las conclusiones y la validación cruzada deben corresponder a una misma corrida vigente y conservar estas decisiones. Si se detecta una discrepancia entre los productos generados, la implementación del modelo y este archivo, debe reportarse al investigador antes de modificar cálculos, parámetros, factores, flujos o decisiones metodológicas.

## 11. Aclaraciones CIA sobre reporte de N y preparación de N/C

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

## 12. Integración temporal de jornadas

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
