# README_METODOLOGIA

## Objetivo del proyecto

Este repositorio calcula un Analisis de Ciclo de Vida (ACV) del manejo de
estiercol bovino en una lecheria. El flujo procesa datos de laboratorio y de
campo, construye parametros por escenario y etapa, estima emisiones con
ecuaciones IPCC o factores medidos, calcula impactos ambientales y exporta
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
- `processed/factores_emision_medidos.csv`: factores medidos para la etapa A2.
- `processed/acv_factores_equivalencia.csv`: factores de caracterizacion para
  calentamiento global y eutrofizacion.

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
oficial CIA suministrada por el investigador: secado a 80 °C, molienda, criba
de 1 mm, pesada aproximada de 80–100 mg y análisis en un autoanalizador
Elementar Vario Macro Cube. Los reportes y la metodología no declaran
inequívocamente si el porcentaje final está en base seca o fresca; la capa
normalizada registra `base_medicion = no especificada en el reporte` y no
altera los valores.

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
- Nitrogeno total como fraccion masica: `n_ex_fraction = n_ex_pct / 100`.
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

## Ecuaciones IPCC

Las funciones de ecuaciones estan en `scripts/ecuaciones_acv.py`. Las etapas se
calculan en:

- `scripts/ACV_EscenarioA_etapa1.py`
- `scripts/ACV_EscenarioA_etapa2.py`
- `scripts/ACV_EscenarioA_etapa3.py`
- `scripts/ACV_EscenarioA_etapa4.py`
- `scripts/ACV_EscenarioB_etapa1.py`
- `scripts/ACV_EscenarioB_etapa2.py`

Las ecuaciones aplicadas incluyen:

- CH4 por manejo de estiercol: `ef_ch4`.
- N2O directo por manejo de estiercol: `n2o_direct_mm`.
- N volatilizado y lixiviado: `n_volatilization_mms`, `n_lixiviado_mms`.
- N2O indirecto por volatilizacion y lixiviacion:
  `n2o_indirect_volatilization`, `n2o_indirect_leaching`.
- NH3 y NO3 derivados de rutas de N: `nh3_direct_mm`, `no3_direct_mm`,
  `nh3_direct_sm`, `no3_direct_sm`.
- Suelos gestionados: `n2o_n_inputs`, `n2o_atd_n`, `n2o_l_n`.

Los factores hardcodeados pendientes de fuente bibliografica estan auditados en:

- `outputs/tablas_tesis/tabla_auditoria_factores_hardcodeados.csv`

## Estimacion de emisiones

Las emisiones se consolidan en:

- `processed/ACV_resumen_emisiones.csv`

La tabla contiene emisiones por escenario y etapa para CO2, CH4, N2O, NH3 y
NO3. Las ecuaciones de N usan `n_ex_fraction` como fraccion masica y no
`n_ex_pct` directamente.

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
- Mantener `n_ex_pct` como porcentaje reportado y `n_ex_fraction` como fraccion
  masica usada en ecuaciones de nitrogeno.
