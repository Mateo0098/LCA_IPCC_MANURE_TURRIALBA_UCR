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
- `Academic_documents/resultados CIA y LASA muestreo 2/`: segunda jornada de
  muestras compuestas independientes y sus determinaciones analiticas.
- `Academic_documents/Datos boniga y agua proy_AS.xlsx`: mediciones de agua y
  boniga usadas para estimar flujos diarios, semanales y anuales.
- `processed/masa_total_factor_overrides.csv`: factores manuales para asignar
  boniga, agua y masa total por etapa.
- `processed/ipcc_sistemas_manejo_estiercol_factores.csv`: factores IPCC por
  sistema de manejo.
- `processed/ipcc_sistema_manejo_por_etapa.csv`: asignacion escenario/etapa a
  sistema IPCC.
- `processed/modelo_etapa_overrides.csv`: seleccion de modelo por etapa
  (`ipcc` o `medido`).
- `processed/ipcc_factores_manejo_overrides_etapa.csv`: parámetros específicos por escenario y etapa; A2 establece `FracLeachMS = 0` sin modificar la categoría IPCC genérica.
- `processed/acv_factores_equivalencia.csv`: factores Environmental Footprint
  3.1 por especie, compartimento y categoría.
- `processed/acv_parametros_operativos.csv`: parámetros de bomba, lavado,
  tractor y frecuencia anual.
- `processed/acv_inventario_recursos_operativos.csv`: electricidad y diésel
  foreground anualizados y normalizados.
- `processed/acv_foreground_intercambio.csv`: intercambio neutral para la
  futura integración con SimaPro.

La caracterización activa de emisiones directas usa EF 3.1: cambio climático
en kg CO₂-eq, eutrofización terrestre en mol N-eq y eutrofización marina en kg
N-eq. Electricidad y diésel permanecen inventariados sin factores de impacto de
fondo. El agua de lavado es pluvial; la captación y el reservorio existentes se
encuentran fuera de la frontera.

## Procesamiento de laboratorio

El procesamiento de laboratorio se hace en dos rutas:

1. `scripts/extract_analysis_results.py`
   - Lee reportes CIA/LASA y PDF de nitrogeno.
   - Genera `processed/CIA_samples_table_v6.csv`.
   - Genera `processed/CIA_samples_table_v6_treatment_summary.csv`.
   - Variables principales: `n_total_mg_kg`, `n_total_porcentaje`,
     `mean_n_percentage`.

2. `scripts/compute_sample_parameters.py`
   - Lee `Material_laboratorio_copy_to_work_python.xlsx`.
   - Calcula masa fresca, masa seca, humedad, materia seca, cenizas y solidos
     volatiles.
   - Genera:
     - `processed/volatile_solids_table.csv`
     - `processed/volatile_solids_representative_table.csv`
     - `processed/volatile_solids_treatment_table.csv`
     - `processed/volatile_solids_mass_loss_fresh_to_precomposted.csv`

### Capa multijornada independiente del modelo

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

La jerarquía es `jornada -> muestra compuesta -> réplica analítica`. No se
agrupan todas las réplicas como muestras independientes y no se integran M1 y
M2 entre sí en esta fase. Estas dos salidas nuevas no alimentan todavía el
modelo ACV ni sustituyen los archivos históricos de parámetros.

Para N de aguas verdes y purines, M1 conserva por separado la especiación de N
amoniacal, N nítrico y N ureico con uso `solo_trazabilidad`. M2 conserva N total
con método `Kjeldahl` y uso `elegible`. La asignación de M2 se fundamenta en la
metodología oficial CIA suministrada por el investigador: digestión húmeda de
10 g de abono líquido con H2SO4 mediante Kjeldahl, volumen final de 250 mL y
determinación colorimétrica con FIA. La elegibilidad no implica conexión actual
con el modelo.

Para N y C del estiércol precompostado, los reportes CIA 97600 y 100751 se
documentan con el método `Dumas (combustión seca)`, conforme a la metodología
oficial CIA suministrada por el investigador: secado a 80 °C durante 48 h, molienda, criba
de 1 mm, pesada aproximada de 80–100 mg y análisis en un autoanalizador
Elementar Vario Macro Cube. Los reportes y la metodología no declaran
inequívocamente si el porcentaje final está en base seca o fresca. El CIA no
determinó humedad a 105 °C porque no fue solicitada; esa preparación no debe
confundirse con los ensayos gravimétricos independientes del TFG a 105 °C. La
capa normalizada registra la condición física de secado sin alterar los valores
analíticos. Para A2, la decisión metodológica vigente interpreta el N como
concentración del material preparado/seco y aplica la materia seca gravimétrica
independiente del TFG para expresarlo sobre la masa húmeda usada como actividad.
Esta conversión no intenta corregir pérdidas de N durante el secado CIA y no se
aplica al carbono.

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
- Nitrógeno efectivo del precompostado en A2 sobre masa húmeda: `N_fraction_wet = (n_ex_pct / 100) * (materia_seca_pct / 100)`.
- Solidos volatiles en base humeda: `(vs_t_pct / 100) * fraccion_masa_seca`.
- Flujos anuales: `(promedio / duracion_muestreo_dias) * 365`.

## Normalizacion a unidad funcional

La unidad funcional del estudio es 1 kg de estiércol fresco, tal y como fue
recolectado del módulo lechero. Esta unidad permite comparar los escenarios de
manejo evaluados bajo una misma base funcional.

Algunos resultados se presentan como flujos anuales estimados para describir la
magnitud operacional del sistema durante el periodo evaluado. Esos valores no
sustituyen la unidad funcional del ACV. El codigo calcula masas equivalentes
anuales por etapa mediante `masa_total_kg_eq`, calculada en:

- `scripts/compute_masa_etapas_escenarios.py`
- `processed/masa_total_escenario_etapa.csv`

La tabla `masa_total_escenario_etapa.csv` integra boniga, agua, factor de
precompostaje y factores manuales de asignacion por etapa. El supuesto operativo
actual es `1 L agua = 1 kg equivalente`.

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

La tabla contiene emisiones por escenario y etapa para CO2, CH4, N2O, NH3 y
NO3. Las ecuaciones de N usan una fracción másica y no `n_ex_pct` directamente.
En A2 esa fracción incorpora explícitamente la materia seca gravimétrica; las
demás etapas conservan la conversión directa de porcentaje a fracción.

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

## Orden recomendado de ejecucion

Si cambian datos crudos:

```powershell
.venv\Scripts\python.exe scripts\extract_analysis_results.py --out-prefix CIA_samples_table_v6
.venv\Scripts\python.exe scripts\compute_sample_parameters.py
.venv\Scripts\python.exe scripts\compute_agua_boniga_stats.py
.venv\Scripts\python.exe scripts\compute_masa_etapas_escenarios.py
.venv\Scripts\python.exe scripts\generate_acv_parametros_escenario_etapa.py
.venv\Scripts\python.exe ACV_orquestador.py
.venv\Scripts\python.exe scripts\generate_thesis_tables.py
```

Si `processed/` ya esta validado:

```powershell
.venv\Scripts\python.exe ACV_orquestador.py
.venv\Scripts\python.exe scripts\generate_thesis_tables.py
```

## Observaciones metodologicas pendientes

- Completar fuentes bibliograficas para factores IPCC y factores de
  caracterizacion.
- Validar los nombres descriptivos de etapas en
  `tabla_01_etapas_escenarios.csv`.
- Mantener `n_ex_pct` como porcentaje analítico reportado. La fracción efectiva
  de A2 incorpora la materia seca gravimétrica; las demás etapas conservan su
  tratamiento vigente.
