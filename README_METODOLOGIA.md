# README_METODOLOGIA

## Objetivo del proyecto

Este repositorio calcula un Analisis de Ciclo de Vida (ACV) del manejo de
estiercol bovino en una lecheria. El flujo procesa datos de laboratorio y de
campo, construye parametros por escenario y etapa, estima emisiones con
ecuaciones IPCC, calcula impactos ambientales y exporta
tablas finales para tesis en `outputs/tablas_tesis/`.

## Documento maestro protegido

El documento maestro usado exclusivamente como referencia de formato es
`MASTER_escrito/TFG_ACV_Estiercol_MASTER.docx`. No debe modificarse ni
sobrescribirse. Los generadores documentales verifican su hash antes y después
de la generación y guardan sus salidas en `outputs/documentos_tfg/`.

## Datos de entrada

Los datos crudos principales estan en `Academic_documents/`:

- `Academic_documents/resultados CIA y LASA muestreo 1/`: reportes de
  laboratorio CIA/LASA y archivo de trabajo para humedad, materia seca, cenizas,
  solidos volatiles y nitrogeno total.
- `Academic_documents/resultados CIA y LASA muestreo 2/`: segunda jornada con
  tres muestras compuestas por sólido, compartidas físicamente entre Bioenergía
  y el laboratorio externo mediante el envío del remanente.
- `Academic_documents/Datos boniga y agua proy_AS.xlsx`: mediciones de agua y
  boniga usadas para estimar flujos diarios, semanales y anuales.
- `processed/masa_total_factor_overrides.csv`: factores manuales para asignar
  boniga, agua y masa total por etapa.
- `processed/ipcc_sistemas_manejo_estiercol_factores.csv`: factores IPCC por
  sistema de manejo.
- `processed/ipcc_sistema_manejo_por_etapa.csv`: asignacion escenario/etapa a
  sistema IPCC.
- `processed/modelo_etapa_overrides.csv`: selección del núcleo de cálculo IPCC
  en las seis etapas vigentes. En A1/A2 esta tabla no describe por sí sola toda
  la arquitectura de N reactivo, que incorpora EMEP/EEA y Komakech según la
  decisión metodológica vigente. El lector actual rechaza `medido`; nombres
  históricos de columnas o capacidades auxiliares no constituyen un método
  alternativo ejecutado en el TFG.
- `processed/ipcc_factores_manejo_overrides_etapa.csv`: parámetros específicos por escenario y etapa; A2 establece `FracLeachMS = 0` sin modificar la categoría IPCC genérica.
- `processed/acv_factores_equivalencia.csv`: factores Environmental Footprint
  3.1 por identidad de flujo elemental, compartimento y categoría (origen fósil/biogénico explícito).
- `processed/acv_parametros_operativos.csv`: parámetros de bomba, lavado,
  tractor y frecuencia anual.
- `processed/acv_inventario_recursos_operativos.csv`: electricidad y diésel
  foreground anualizados y normalizados.
- `processed/acv_foreground_intercambio.csv`: intercambio neutral para la
  inspección del inventario y verificación externa opcional, sin importación obligatoria de resultados.

La caracterización activa de emisiones directas usa EF 3.1: cambio climático
en kg CO₂-eq, eutrofización terrestre en mol N-eq y eutrofización marina en kg
N-eq. La electricidad se evalúa con IMN de consumo 2025 (0,0415 kg CO₂-eq/kWh),
proxy temporal para el patrón operativo observado el 25-08-2026 y anualizado
a 365 días. El diésel usa factores físicos IMN y caracterización EF 3.1 de
CO₂ fósil, CH₄ fósil y N₂O molecular. La categoría residencial y agrícola es un
proxy sectorial aprobado, no una categoría literal de tractor. La selección y
su justificación se detallan en la sección 15 de `DECISIONES_METODOLOGICAS_TFG.md`.
No se incorporan cadenas completas ecoinvent; SimaPro es QA/QC independiente
opcional. El total climático combinado conserva la electricidad agregada IMN. El agua de lavado es pluvial; la captación y el reservorio existentes se
encuentran fuera de la frontera.

### Factores y resultados operativos

La fuente manual de factores de emisión por actividad es
`processed/acv_factores_imn_recursos_operativos.csv`, separada de los CF EF 3.1.
Conserva edición de portada/interiores, unidades originales, selección, año,
página, incertidumbres y hash. `scripts/imn_operational_factors.py` valida y
convierte factores físicos, invocado por el generador operativo existente.
La LCIA consume este inventario, caracteriza solo las masas del diésel con EF
y agrega electricidad una sola vez. Las salidas existentes por etapa y escenario
incluyen `clima_manejo_ef31_kg_co2eq`, `clima_electricidad_imn_kg_co2eq`,
`clima_diesel_ef31_kg_co2eq` y `clima_recursos_operativos_kg_co2eq`;
`impacto_calentamiento_global_kg_co2eq` es ahora el total combinado.
Las masas físicas quedan también en el inventario operativo y su exportación.

## Procesamiento de laboratorio

Las rutinas base de extracción y gravimetría son:

1. `scripts/extract_analysis_results.py`
   - Lee reportes CIA/LASA y PDF de nitrogeno.
   - Normaliza los reportes CIA/LASA cuando es invocado por la ingestión activa.
   - También puede generar tablas históricas M1 para trazabilidad; esas tablas no
     son fuente vigente del ACV.

2. `scripts/compute_sample_parameters.py`
   - Lee `Material_laboratorio_copy_to_work_python.xlsx`.
   - Calcula masa fresca, masa seca, humedad, materia seca, cenizas y solidos
     volatiles.
   - También conserva productos históricos de detalle M1:
     - `processed/volatile_solids_table.csv`
     - `processed/volatile_solids_representative_table.csv`
     - `processed/volatile_solids_treatment_table.csv`
     - `processed/volatile_solids_mass_loss_fresh_to_precomposted.csv`

La ruta canónica no consume esos resúmenes históricos: parte de las observaciones
normalizadas, resume por jornada, integra entre jornadas y promueve los resultados
vigentes al ACV.

### Capa multijornada activa

La ingestión de M1 y M2 se ejecuta con:

```powershell
.venv\Scripts\python.exe scripts\build_sampling_ingestion.py
.venv\Scripts\python.exe scripts\validate_sampling_ingestion.py
```

La configuración explícita está en `scripts/sampling_ingestion_config.py`.
Esta capa genera:

- `processed/muestreos_observaciones_normalizadas.csv`: una fila por
  observación primaria recuperable, con jornada, muestra compuesta, réplica
  analítica, variable, unidad, laboratorio, método y fuente;
- `processed/muestreos_resumen_intrajornada.csv`: primero promedia las
  submuestras dentro de cada muestra compuesta y después las muestras dentro de
  cada jornada.

La jerarquía es `réplica analítica -> muestra compuesta -> promedio de jornada
-> integración entre jornadas`. No se agrupan todas las réplicas como muestras
independientes. En M1, por cada sólido, las dos muestras de Bioenergía y las dos
muestras del laboratorio externo fueron conjuntos físicos independientes: LASA
para estiércol fresco y CIA para precompostado. Por ello, «dos muestras M1»
significa dos por fuente y flujo analítico, no dos muestras físicas totales por
material. En M2 hubo tres muestras compuestas por sólido, Bioenergía efectuó tres
réplicas gravimétricas por muestra y el remanente de esas mismas muestras se
envió a LASA o CIA. La integración multijornada vigente alimenta los parámetros
activos del ACV; las tablas históricas no sustituyen esta ruta.

Para N de aguas verdes y purines, M1 conserva por separado la especiación de N
amoniacal, N nítrico y N ureico con uso `solo_trazabilidad`. M2 conserva N total
con método `Kjeldahl` y uso `elegible`. La asignación de M2 se fundamenta en la
metodología oficial CIA suministrada por el investigador: digestión húmeda de
10 g de abono líquido con H2SO4 mediante Kjeldahl, volumen final de 250 mL y
determinación colorimétrica con FIA. La elegibilidad de M2 permite el contraste
experimental, pero no reinicializa el N total ni el TAN propagados por el ledger
en A4/B2.

Para N y C del estiércol precompostado, los reportes CIA 97600 y 100751 se
documentan con el método `Dumas (combustión seca)`, conforme a la metodología
oficial CIA suministrada por el investigador: secado a 80 °C durante 48 h, molienda, criba
de 1 mm, pesada aproximada de 80–100 mg y análisis en un autoanalizador
Elementar Vario Macro Cube. El porcentaje de N se refiere a la muestra
seca/acondicionada por el CIA a 80 °C durante 48 h. El CIA no determinó humedad
a 105 °C porque no fue solicitada; esa preparación no debe confundirse con la
gravimetría independiente de Bioenergía a 105 °C durante 16 h, que aporta la
humedad y materia seca del TFG. Para A2, el N integrado se convierte a base
húmeda únicamente para construir el benchmark experimental; no reinicializa el
ledger productivo, que recibe N total y TAN desde la salida de A1. No se fuerza
la coincidencia entre el benchmark y el N propagado. El carbono y la relación
C/N permanecen como caracterización descriptiva, sin conversión húmeda ni uso
productivo en el ACV.

Para N líquido M2, se conservan todos los decimales almacenados por el equipo
en los archivos CIA y se calculan los resúmenes antes de cualquier formato de
presentación. El CIA reporta el resultado hasta el segundo decimal; los
decimales adicionales no se interpretan como mayor precisión analítica formal.

El estado `solo_caracterizacion` se usa para densidad, carbono y relación C/N:
estas variables se conservan, pero no se presentan como parámetros consumidos
actualmente por el modelo. N, humedad, materia seca, cenizas y sólidos
volátiles mantienen su elegibilidad definida por fuente y método.

## Conversion de unidades

Las conversiones principales son:

- Humedad: `(masa_fresca - masa_seca) / masa_fresca * 100`.
- Materia seca: `masa_seca / masa_fresca * 100`.
- Cenizas: `masa_cenizas / masa_seca_calcinacion * 100`.
- Solidos volatiles: `100 - cenizas`.
- Nitrógeno total de estiércol fresco, aguas verdes y purines como fracción másica: `n_ex_fraction = n_ex_pct / 100`.
- Benchmark experimental de N del precompostado en A2 sobre masa húmeda: `N_fraction_wet = (n_ex_pct / 100) * (materia_seca_pct / 100)`; no reinicializa el ledger productivo.
- Solidos volatiles en base humeda: `(vs_t_pct / 100) * fraccion_masa_seca`.

## Realidad física y temporal de los escenarios

El Escenario A representa la operación habitual. La fracción paleada sigue A1:
Precomposteo y después A2: Lombricompostaje; el remanente del piso se incorpora
al agua de lavado, llega por drenaje o canal a la tanqueta y sigue A3:
Almacenamiento de aguas verdes → A4: Aplicación de aguas verdes en campos de
pastoreo. La tanqueta almacena. El cañón VAIA, accionado por el tractor, aplica.

El Escenario B es la alternativa comparativa del ACV y fue materializado
temporalmente, sin constituir la operación habitual permanente. Durante esa
condición se suspendió la desviación del sólido hacia A1/A2, se dirigió el
estiércol paleado a la tanqueta y el remanente se incorporó mediante lavado. Los
purines se observaron y muestrearon físicamente. Las campañas A y B ocurrieron
en momentos distintos con la misma tanqueta.

A1 dura aproximadamente tres a cuatro semanas: la observación abarca 21 días a
cerca de un mes y no constituye una medición exacta de 28 días. A2 comienza
después de A1 y su operación regular dura aproximadamente 13 semanas. Vargas
Sarmiento (2023, sección 5.2.2.1, p. 14; sección 6.1.3, p. 25) documenta en el
mismo lombricario 13 semanas desde la siembra de las lombrices y para procesar
toda la boñiga. El TFG muestreó estiércol precompostado listo para ingresar a A2,
no lombricompost terminado. Ninguna de estas duraciones escala factores.

La operación habitual de la tanqueta se representa mediante vaciado cada tres
días, dos lavados por ciclo, siete minutos por lavado y treinta minutos de
tractor/cañón por vaciado. Esta frecuencia anualiza los consumos operativos. El
intervalo jueves por la tarde–lunes por la mañana describe únicamente la
acumulación previa a cada muestreo líquido, con entradas continuas y dos lavados;
no es una carga estática ni un parámetro de residencia del modelo.

Para A3/B1, el MCF de 38 % es el proxy IPCC tabulado de un mes seleccionado como
aproximación conservadora, no un MCF medido para tres días. No se escala como
`38 % × 3/30`. La mineralización EMEP de 10 % tampoco se escala por la residencia.

## Normalizacion a unidad funcional

La unidad funcional del estudio es 1 kg de estiércol fresco, tal y como fue
recolectado del módulo lechero. Esta unidad permite comparar los escenarios de
manejo evaluados bajo una misma base funcional.

Algunos resultados se presentan como flujos anuales estimados para describir la
magnitud operacional del sistema durante el periodo evaluado. Esos valores no
sustituyen la unidad funcional del ACV. El código registra masas equivalentes
anuales por etapa mediante `masa_total_kg_eq` en:

- `scripts/compute_masa_etapas_escenarios.py`
- `processed/masa_total_escenario_etapa.csv`

La tabla `masa_total_escenario_etapa.csv` distingue masa de estiércol por etapa,
agua de lavado y mezcla equivalente. En A1/A2/A3/B1 la masa equivalente coincide
con la masa de actividad de estiércol pertinente; en A4/B2 incorpora agua para
representar la mezcla y su dilución, con el supuesto `1 L agua = 1 kg
equivalente`. Esa mezcla no es una masa funcional ni genera una segunda masa de
N o emisiones: el N aplicado en A4/B2 procede del ledger de A3/B1. La masa
funcional de referencia es el flujo anual común de estiércol fresco de los
escenarios, usado como denominador al expresar resultados por 1 kg.

### Estimación de la frontera A1→A2 y alcance del agua

La entrada de A1 es 17 525,1 kg/año de estiércol fresco recolectado. No se pesó
la salida completa de A1. En cada jornada elegible se usan la fracción de
materia seca sobre masa húmeda (`d`) y la fracción de cenizas sobre materia seca
(`a`) de estiércol fresco (`f`) y precompostado (`p`). Al **suponer** que la
ceniza mineral de la misma corriente se conserva,
`M_f d_f a_f = M_p d_p a_p`, y por tanto
`R_j = M_p/M_f = (d_f a_f)/(d_p a_p)` (kg/kg). Se promedian los factores de
jornada con igual peso temporal; `M_A2 = M_A1 × promedio(R_j)` es una **masa
húmeda anual inferida**, usada como actividad de A2. El resultado provisional
M1–M2 es 0,4239615549830651 kg/kg y 7 429,968647 kg/año. El 57,6038445 %
complementario es una diferencia estimada de masa húmeda, no una pérdida
medida ni una atribución a evaporación.

El cálculo requiere comparabilidad entre las muestras de entrada y salida y
ausencia de entradas o salidas minerales; no verifica experimentalmente esas
condiciones. En M1, las muestras compuestas de Bioenergía y de los laboratorios
externos son físicamente distintas; la ecuación emplea promedios de jornada,
no parejas de muestras ni un lote pesado. La media de razones de jornada no
garantiza conservación exacta al combinarla con porcentajes integrados por
separado.

La humedad de ambos materiales se midió en muestras, pero no hay caudales
cuantificados de agua añadida, evaporación, drenaje ni sólidos retirados entre
A1 y la entrada de A2. El balance de agua quedaría
`W_A2 = W_A1 + W_agregada − W_evaporada − W_drenada − W_otros`, con varias
incógnitas; el cambio de masa húmeda no permite resolverlas. Los 250 572,5
L/año de agua de lavado corresponden a las rutas de aguas verdes y purines,
no a A1/A2. En A2 se observó ausencia de riego operacional regular, sin
medición que pruebe aporte de agua exactamente nulo. Tampoco se muestreó el
lombricompost terminado. A1 dura tres a cuatro semanas y A2 comienza después,
con unas 13 semanas de operación regular independientes de los factores de
emisión.

La declaracion metodologica de unidad funcional y supuestos esta en:

- `outputs/tablas_tesis/tabla_00_unidad_funcional_y_supuestos.csv`

## Ecuaciones productivas

El ledger secuencial de N total y TAN reside exclusivamente en
`scripts/reactive_n_ledger.py`. Las seis etapas consumen sus resultados mediante:

- `scripts/ACV_EscenarioA_etapa1.py`
- `scripts/ACV_EscenarioA_etapa2.py`
- `scripts/ACV_EscenarioA_etapa3.py`
- `scripts/ACV_EscenarioA_etapa4.py`
- `scripts/ACV_EscenarioB_etapa1.py`
- `scripts/ACV_EscenarioB_etapa2.py`

El módulo inicializa TAN/N = 0,60 únicamente en estiércol fresco, propaga los
pools entre etapas, calcula NH₃-N, NOx-N y N₂-N explícitos, aplica una sola vez
el N₂O directo IPCC y limita el NO₃⁻ a rutas hídricas justificadas. FracGas se
conserva solo como benchmark y no alimenta EF4. El CH₄ conserva la ecuación IPCC
general de `scripts/ecuaciones_acv.py`.

Los factores, unidades y ubicaciones bibliográficas del ledger residen en
`processed/reactive_n_ledger_parameters.csv`; su salida física productiva es
`processed/reactive_n_ledger.csv`.

## Estimacion de emisiones

Las emisiones se consolidan en:

- `processed/ACV_resumen_emisiones.csv`

La tabla contiene emisiones por escenario y etapa para CO₂, CH₄, N₂O, NH₃ y
NO₃⁻. El N total y TAN productivos de A2 llegan desde A1 por
`scripts/reactive_n_ledger.py`; sus emisiones de N se calculan con esos pools
propagados y los factores correspondientes. La fracción húmeda derivada del
N Dumas y la materia seca gravimétrica del precompostado solo construye un
benchmark experimental. No se usa para reinicializar A2 ni se exige que
coincida con el N propagado. El N de aplicación en A4/B2 también procede de la
etapa precedente; la masa equivalente de la mezcla no multiplica de nuevo sus
emisiones. Para CH₄ de manejo, A1/A2/A3/B1 usan la masa de actividad pertinente,
que coincide allí con `masa_total_kg_eq` sin agua.

En A1, la masa húmeda de actividad es el estiércol fresco recolectado y los
sólidos volátiles se convierten de base seca a base húmeda antes de aplicar B₀,
MCF y la densidad de CH₄. En A2, esa misma ecuación utiliza la masa húmeda
inferida de entrada y la caracterización del precompostado. Para el N reactivo,
A2 no usa esa masa para reconstruir N total ni TAN: ambos pools llegan de A1.
La única ruta nitrogenada de A2 basada en masa húmeda es NH₃, mediante 12,8 g
NH₃/Mg de residuo orgánico de entrada de Komakech et al. (2016). El denominador
se interpreta como masa húmeda de entrada a partir de la unidad funcional y el
balance en base húmeda del artículo. La transferencia es un proxy experimental,
porque el factor se estimó en reactores pequeños de Kampala, con residuo
predominantemente ganadero y flujo de aire aproximado mediante el índice
respirométrico dinámico. NO-N y N₂-N usan provisionalmente factores EMEP/EEA de
almacenamiento sólido. La fracción IPCC de volatilización permanece solo como
benchmark y no crea otra masa de emisión.

Esta combinación constituye la arquitectura híbrida IPCC–EMEP–Komakech vigente:
IPCC cubre CH₄ y N₂O directo de A2, Komakech cubre NH₃ como proxy experimental
aprobado y EMEP/EEA cubre NO y N₂ mediante proxies metodológicos aprobados
provisionalmente. No es la aplicación íntegra de una sola guía ni una decisión
pendiente de armonización. El factor EMEP de N₂-N, 0,300 kg/kg TAN, tiene alta
influencia y permanece como incertidumbre de representatividad susceptible de
una sensibilidad futura, sin bloquear el modelo pre-M3.

El ledger secuencial impide interpretar por sí solo el uso de factores en A1 y
A2 como doble conteo: A2 actúa sobre el N total y el pool residual de TAN que
salen de A1. Las duraciones específicas introducen incertidumbre de
transferibilidad temporal, pero no escalan linealmente los factores. Jjagwe et
al. se conserva exclusivamente como benchmark interpretativo.

La tabla final limpia para tesis es:

- `outputs/tablas_tesis/tabla_06_emisiones_por_etapa.csv`

## Evaluacion de impactos

Los impactos se calculan con:

- `scripts/compute_acv_impact_equivalents.py`

Entradas:

- `processed/ACV_resumen_emisiones.csv`
- `processed/acv_factores_equivalencia.csv`

Salidas procesadas:

- `processed/acv_impacto_por_etapa_escenario.csv`
- `processed/acv_impacto_total_por_escenario.csv`

Tablas finales:

- `outputs/tablas_tesis/tabla_07_impactos_por_etapa.csv`
- `outputs/tablas_tesis/tabla_08_impactos_totales_por_escenario.csv`
- `outputs/tablas_tesis/tabla_09_comparacion_escenarios.csv`

## Contraste bibliográfico de A2

El producto `processed/a2_ipcc_jjagwe_benchmark.csv` es generado por
`scripts/generate_a2_jjagwe_benchmark.py` como postproceso del inventario
oficial. Lee los datos bibliográficos mínimos de
`Academic_documents/references/jjagwe_2019_benchmark.csv`, la masa y materia
seca activas de A2, `CH4_ec1`, `N2O_ec2` y los factores de caracterización
vigentes. No modifica emisiones ni impactos oficiales y no activa una ruta
`medido`.

La base común es la materia seca del precompostado al ingreso de A2. El producto
compara CH₄, N₂O directo, N₂O-N/N inicial y la contribución armonizada de CH₄ +
N₂O directo. No calcula eutrofización experimental ni incorpora CO₂
experimental o N₂O indirecto al indicador armonizado.

## Archivos finales generados para tesis

Las tablas finales se generan con:

```powershell
.venv\Scripts\python.exe scripts\generate_thesis_tables.py
```

Archivos en `outputs/tablas_tesis/`:

- `tabla_00_unidad_funcional_y_supuestos.csv`
- `tabla_01_etapas_escenarios.csv`
- `tabla_02_caracterizacion_muestras.csv`
- `tabla_03_flujos_icv.csv`
- `tabla_04_parametros_modelo_acv.csv`
- `tabla_05_factores_emision_y_caracterizacion.csv`
- `tabla_06_emisiones_por_etapa.csv`
- `tabla_07_impactos_por_etapa.csv`
- `tabla_08_impactos_totales_por_escenario.csv`
- `tabla_09_comparacion_escenarios.csv`
- `diccionario_variables.csv`
- `tabla_auditoria_factores_hardcodeados.csv`

Las figuras académicas se generan con
`scripts/generate_thesis_graphics.py` en `outputs/graficos_tesis/`. Los
documentos se generan con `scripts/generate_methodology_docx.py` y
`scripts/generate_results_docx.py` en `outputs/documentos_tfg/`. Los Word usan
el documento protegido de `MASTER_escrito/` únicamente como referencia de
formato.

## Orden recomendado de ejecución

Cuando cambian datos experimentales, se ejecuta el único pipeline vigente en
este orden. La ingestión normaliza observaciones y produce el resumen
intrajornada; la integración construye los estimadores interjornada y la
transformación de masa. `ACV_orquestador.py` parte de esa integración validada:
promueve parámetros activos, calcula masas, ledger, emisiones e impactos. No
ejecuta ingestión ni integración estadística.

```powershell
.venv\Scripts\python.exe scripts\build_sampling_ingestion.py
.venv\Scripts\python.exe scripts\validate_sampling_ingestion.py
.venv\Scripts\python.exe scripts\build_sampling_integration.py
.venv\Scripts\python.exe scripts\validate_sampling_integration.py
.venv\Scripts\python.exe ACV_orquestador.py
.venv\Scripts\python.exe scripts\generate_thesis_tables.py
.venv\Scripts\python.exe scripts\generate_thesis_graphics.py
.venv\Scripts\python.exe scripts\generate_methodology_docx.py
.venv\Scripts\python.exe scripts\generate_results_docx.py
.venv\Scripts\python.exe scripts\generate_conclusions_docx.py
.venv\Scripts\python.exe scripts\generate_integral_tfg_docx.py
.venv\Scripts\python.exe scripts\validate_provisional_m1_m2_outputs.py
```

Las tablas M1 `CIA_samples_table*` y `volatile_solids_*`, y la ejecución aislada
de `compute_sample_parameters.py`, se conservan para trazabilidad histórica;
no sustituyen las salidas multijornada vigentes. El orquestador solo puede
ejecutarse de forma abreviada si la ingestión y la integración activas ya
corresponden a los datos actuales y superaron sus validadores. Ante duda se
ejecuta la secuencia completa. Las tablas, figuras y documentos deben proceder
de la misma corrida validada.

## Observaciones metodologicas pendientes

- Completar fuentes bibliograficas para factores IPCC y factores de
  caracterizacion.
- Validar los nombres descriptivos de etapas en
  `tabla_01_etapas_escenarios.csv`.

## Factores históricos y caracterización vigente

Las constantes `CH_4_eq = 21`, `N_2_O_eq = 310`, `NH_3_eq = 0.35` y
`NO_3_eq = 0.095` conservadas en `scripts/ecuaciones_acv.py`, así como
`gwp_ch4 = 21` y `gwp_n2o = 310` en los parámetros del ledger, son legados o
valores de contraste diagnóstico; no son factores de caracterización productiva
EF 3.1. El impacto vigente se caracteriza con la identidad de flujo,
compartimento y categoría de `processed/acv_factores_equivalencia.csv`, además
del factor agregado IMN para electricidad descrito arriba.
