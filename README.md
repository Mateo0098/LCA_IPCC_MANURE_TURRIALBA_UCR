# ACV Pipeline (ES/EN)

## ES - Objetivo
Este proyecto calcula emisiones e impactos ACV por etapa/escenario, a partir de tablas en `processed/`, y genera salidas tabulares y graficas.

## ES - Flujo operativo (resumen)
1. Preparar/actualizar tablas en `processed/` (solo si cambian muestreos o configuracion manual).
2. Ejecutar el modelo con `ACV_orquestador.py`.
3. Revisar resultados en `processed/` y `graphics_results/`.

## ES - Crear entorno virtual e instalar librerias
Desde la raiz del proyecto:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## ES - Cuando debo regenerar datos desde `Academic_documents`?
Regenera datos de muestreo cuando:
- se actualizan archivos fuente en `Academic_documents/`,
- cambian reportes de laboratorio,
- o falta alguna tabla derivada de muestreos.

Si no cambio nada de muestreos y las tablas ya existen, puedes correr directo el orquestador.

## ES - Paso A: Tablas derivadas de muestreos (no manuales)
Estas tablas se generan con scripts y no se editan manualmente:

- `processed/CIA_samples_table.csv`  
  Script: `scripts/extract_analysis_results.py`

- `processed/CIA_samples_table_treatment_summary.csv` (o `CIA_samples_table_v6_treatment_summary.csv`)  
  Script: `scripts/extract_analysis_results.py`

- `processed/volatile_solids_table.csv`  
  Script: `scripts/compute_sample_parameters.py`

- `processed/volatile_solids_representative_table.csv`  
  Script: `scripts/compute_sample_parameters.py`

- `processed/volatile_solids_treatment_table.csv`  
  Script: `scripts/compute_sample_parameters.py`

- `processed/volatile_solids_mass_loss_fresh_to_precomposted.csv`  
  Script: `scripts/compute_sample_parameters.py`

- `processed/agua_boniga_estadistica_descriptiva.csv`  
  Script: `scripts/compute_agua_boniga_stats.py`

- `processed/masa_total_escenario_etapa.csv`  
  Script: `scripts/compute_masa_etapas_escenarios.py`

- `processed/acv_parametros_escenario_etapa.csv`  
  Script: `scripts/generate_acv_parametros_escenario_etapa.py`

## ES - Paso B: Tablas manuales de configuracion del modelo
Estas tablas si son de manejo manual:

- `processed/modelo_etapa_overrides.csv`  
  Define que modelo usa cada etapa/escenario (por ejemplo IPCC vs medido).

- `processed/factores_emision_medidos.csv`  
  Factores de emision medidos (base seca) para etapas en modo medido.

- `processed/ipcc_sistemas_manejo_estiercol_factores.csv`  
  Catalogo IPCC de factores por sistema de manejo (`MCF`, `EF3`, `frac_gas_ms`, `frac_leach_ms`).

- `processed/ipcc_sistema_manejo_por_etapa.csv`  
  Mapeo escenario/etapa -> sistema de manejo IPCC.

- `processed/masa_total_factor_overrides.csv`  
  Ajustes manuales de masa por etapa/escenario (`factor_boniga`, `factor_agua`, `factor_masa_total`).

## ES - Orden de ejecucion recomendado
Desde la raiz del proyecto:

```powershell
.venv\Scripts\python.exe scripts\extract_analysis_results.py
.venv\Scripts\python.exe scripts\compute_sample_parameters.py
.venv\Scripts\python.exe scripts\compute_agua_boniga_stats.py
.venv\Scripts\python.exe scripts\compute_masa_etapas_escenarios.py
.venv\Scripts\python.exe scripts\generate_acv_parametros_escenario_etapa.py
.venv\Scripts\python.exe ACV_orquestador.py
```

## ES - Ejecucion rapida (sin actualizar muestreos)
Si `processed/` ya esta actualizado y validado:

```powershell
.venv\Scripts\python.exe ACV_orquestador.py
```

## ES - Salidas principales
- `processed/ACV_resumen_emisiones.csv`
- `processed/acv_impacto_por_etapa_escenario.csv`
- `processed/acv_impacto_total_por_escenario.csv`
- `graphics_results/*.png` y `graphics_results/*.pdf`

---

## EN - Goal
This project computes stage/scenario ACV emissions and impacts from `processed/` tables, then generates tabular and graphical outputs.

## EN - Operating flow (summary)
1. Prepare/update `processed/` tables (only if sampling inputs or manual config changed).
2. Run the model through `ACV_orquestador.py`.
3. Review outputs in `processed/` and `graphics_results/`.

## EN - Create virtual environment and install dependencies
From the project root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## EN - When should I regenerate data from `Academic_documents`?
Regenerate sampling-derived data when:
- source files in `Academic_documents/` change,
- lab reports are updated,
- or any sampling-derived table is missing.

If sampling inputs did not change and tables already exist, run the orchestrator directly.

## EN - Step A: Sampling-derived tables (non-manual)
These tables are script-generated and should not be manually edited:

- `processed/CIA_samples_table.csv`  
  Script: `scripts/extract_analysis_results.py`

- `processed/CIA_samples_table_treatment_summary.csv` (or `CIA_samples_table_v6_treatment_summary.csv`)  
  Script: `scripts/extract_analysis_results.py`

- `processed/volatile_solids_table.csv`  
  Script: `scripts/compute_sample_parameters.py`

- `processed/volatile_solids_representative_table.csv`  
  Script: `scripts/compute_sample_parameters.py`

- `processed/volatile_solids_treatment_table.csv`  
  Script: `scripts/compute_sample_parameters.py`

- `processed/volatile_solids_mass_loss_fresh_to_precomposted.csv`  
  Script: `scripts/compute_sample_parameters.py`

- `processed/agua_boniga_estadistica_descriptiva.csv`  
  Script: `scripts/compute_agua_boniga_stats.py`

- `processed/masa_total_escenario_etapa.csv`  
  Script: `scripts/compute_masa_etapas_escenarios.py`

- `processed/acv_parametros_escenario_etapa.csv`  
  Script: `scripts/generate_acv_parametros_escenario_etapa.py`

## EN - Step B: Manual model-configuration tables
These tables are manually maintained:

- `processed/modelo_etapa_overrides.csv`  
  Defines which model each stage/scenario uses (for example IPCC vs measured).

- `processed/factores_emision_medidos.csv`  
  Measured emission factors (dry basis) for stages running in measured mode.

- `processed/ipcc_sistemas_manejo_estiercol_factores.csv`  
  IPCC factor catalog by manure-management system (`MCF`, `EF3`, `frac_gas_ms`, `frac_leach_ms`).

- `processed/ipcc_sistema_manejo_por_etapa.csv`  
  Scenario/stage -> IPCC management system mapping.

- `processed/masa_total_factor_overrides.csv`  
  Manual mass-adjustment factors by scenario/stage (`factor_boniga`, `factor_agua`, `factor_masa_total`).

## EN - Recommended execution order
From the project root:

```powershell
.venv\Scripts\python.exe scripts\extract_analysis_results.py
.venv\Scripts\python.exe scripts\compute_sample_parameters.py
.venv\Scripts\python.exe scripts\compute_agua_boniga_stats.py
.venv\Scripts\python.exe scripts\compute_masa_etapas_escenarios.py
.venv\Scripts\python.exe scripts\generate_acv_parametros_escenario_etapa.py
.venv\Scripts\python.exe ACV_orquestador.py
```

## EN - Fast run (no sampling updates)
If `processed/` is already up to date and validated:

```powershell
.venv\Scripts\python.exe ACV_orquestador.py
```

## EN - Main outputs
- `processed/ACV_resumen_emisiones.csv`
- `processed/acv_impacto_por_etapa_escenario.csv`
- `processed/acv_impacto_total_por_escenario.csv`
- `graphics_results/*.png` and `graphics_results/*.pdf`
