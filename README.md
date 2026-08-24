# Pipeline del ACV

## Objetivo

Este proyecto calcula emisiones e impactos de análisis de ciclo de vida (ACV)
por etapa y escenario para el manejo de estiércol bovino en una lechería
especializada de Turrialba, Costa Rica. También genera tablas, gráficos y
documentos académicos para el TFG.

## Estado actual

La corrida vigente es **ACV PROVISIONAL M1–M2**:

- las variables comparables de los sólidos integran M1 y M2 con igual peso temporal;
- el N total de aguas verdes y purines procede únicamente de M2, determinado mediante Kjeldahl;
- la transformación de estiércol fresco a precompostado integra los factores calculados primero para M1 y M2 por separado.

Cuando exista una M3 metodológicamente compatible, el mismo pipeline integrará
M1+M2+M3 para sólidos y transformación de masa, y M2+M3 para N líquido. No hay
perfiles históricos, snapshots del modelo ni pipelines paralelos activos.

Las decisiones metodológicas aprobadas se registran en
`DECISIONES_METODOLOGICAS_TFG.md`. No deben reinterpretarse ni modificarse al
regenerar el proyecto sin autorización del investigador.

La coordinación entre Mateo, ChatGPT y Codex, incluido el uso de reportes
temporales no versionados en `.codex_reports/`, se describe en
`CHATGPT_CODEX_WORKFLOW.md`.

## Documento maestro protegido

El documento maestro de referencia de formato es
`MASTER_escrito/TFG_ACV_Estiercol_MASTER.docx`. Es una fuente inmutable: los
generadores solo pueden consultarlo como referencia de formato y deben verificar
su hash antes y después de generar documentos. Nunca debe modificarse,
sobrescribirse, regenerarse ni usarse como destino. Todos los documentos
generados se guardan en `outputs/documentos_tfg/`.

## Crear el entorno virtual

Desde la raíz del proyecto:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Pipeline canónico

Cuando cambien los datos experimentales, debe ejecutarse la secuencia completa
en este orden:

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
.venv\Scripts\python.exe scripts\validate_provisional_m1_m2_outputs.py
```

La validación cruzada reconstruye también las comparaciones narrativas desde las
fuentes canónicas: comprueba mayor/menor, signo de B menos A, porcentaje relativo,
unidad, etapa dominante y ambigüedad causada por el redondeo visible. Los
generadores deben obtener estas direcciones y porcentajes de los datos, no de
afirmaciones manuales sobre A o B.

`ACV_orquestador.py` parte de la integración experimental vigente. En orden,
genera `processed/acv_parametros_escenario_etapa.csv`, calcula las masas,
construye `processed/reactive_n_ledger.csv`, inicializa el resumen de emisiones,
ejecuta A1–B2, valida la presencia de las
seis etapas, calcula impactos, genera el contraste bibliográfico derivado de A2
y ejecuta el postproceso gráfico existente. El contraste no modifica el
inventario ni los impactos oficiales. No
ejecuta la ingestión, la integración estadística, los generadores académicos ni
la validación cruzada final.

El orquestador solo puede ejecutarse de forma abreviada cuando la ingestión y la
integración vigentes ya estén actualizadas y hayan superado sus validadores. Si
existe duda sobre su vigencia, debe ejecutarse la secuencia completa.

## Fronteras activas

- `processed/muestreos_integracion_interjornada_provisional.csv` contiene la integración experimental vigente.
- `processed/acv_parametros_escenario_etapa.csv` promueve N total, sólidos volátiles y materia seca hacia el ACV según las necesidades de cada etapa.
- `processed/muestreos_transformacion_masa_interjornada.csv` contiene los factores por jornada y el factor integrado fresco→precompostado.
- `processed/masa_total_escenario_etapa.csv` contiene las masas activas por etapa.

No todos los parámetros experimentales pasan por una sola tabla. La
caracterización química y la transformación de masa siguen fronteras separadas
que convergen en la corrida del ACV.

### Modelo activo de A2

A2 utiliza las ecuaciones IPCC compartidas y la categoría de manejo
`composting_pasive` como aproximación al lombricompostaje. Conserva los factores
genéricos de esa categoría, excepto `FracLeachMS = 0`, configurado como parámetro
específico de A2 en `processed/ipcc_factores_manejo_overrides_etapa.csv`. La masa
de A2 depende del factor integrado de transformación fresco→precompostado.
Su N total y TAN de entrada proceden exclusivamente de la salida de A1; la
medición del precompostado se conserva como benchmark y no reinicializa el
balance.

### Ledger productivo de N total y TAN

`scripts/reactive_n_ledger.py` es la única implementación de las ecuaciones de
N reactivo para las cadenas independientes A1→A2, A3→A4 y B1→B2. Inicializa TAN
como 0,60 del N total únicamente en las fronteras de estiércol fresco y propaga
ambos pools entre etapas. Las pérdidas EMEP de NH₃-N, NOx-N y N₂-N reducen TAN
y N total; las pérdidas IPCC reducen N total sin asignarse automáticamente a
TAN. EF4 utiliza las especies volatilizadas explícitas y el NO₃⁻ procede solo de
rutas hídricas justificadas. Las mediciones intermedias son benchmarks.

`scripts/reactive_n_ledger_audit.py` genera productos de QA/QC consumiendo ese
mismo módulo; no contiene una implementación alternativa.

## Configuración manual vigente

Estas tablas se mantienen manualmente y no sustituyen las capas experimentales:

- `processed/modelo_etapa_overrides.csv`: selecciona el modelo de cada etapa.
- `processed/ipcc_sistemas_manejo_estiercol_factores.csv`: factores por sistema de manejo IPCC.
- `processed/ipcc_sistema_manejo_por_etapa.csv`: asignación de sistemas IPCC por etapa.
- `processed/ipcc_factores_manejo_overrides_etapa.csv`: excepciones específicas por escenario y etapa sin alterar factores genéricos.
- `processed/masa_total_factor_overrides.csv`: ajustes controlados de masa por etapa.

## Incorporación futura de M3

M3 seguirá el mismo flujo: ingestión → validación de ingestión → integración
final → validación de integración → mismo ACV → tablas → gráficos → metodología
→ resultados → conclusiones → validación cruzada. Una integración incompleta no
debe presentarse como resultado experimental final.

## Salidas principales

- `processed/ACV_resumen_emisiones.csv`
- `processed/reactive_n_ledger.csv`
- `processed/acv_impacto_por_etapa_escenario.csv`
- `processed/acv_impacto_total_por_escenario.csv`
- `outputs/tablas_tesis/`: tablas académicas y versiones para Word.
- `outputs/graficos_tesis/`: figuras académicas en PNG y SVG.
- `outputs/documentos_tfg/metodologia_desarrollada_tfg.docx`
- `outputs/documentos_tfg/resultados_desarrollados_tfg.docx`
- `outputs/documentos_tfg/conclusiones_desarrolladas_tfg.docx`
- `outputs/documentos_tfg/reporte_validacion_provisional_m1_m2.md`

Los archivos generados son productos regenerables del pipeline vigente. Las
tablas históricas `CIA_samples_table*` y `volatile_solids_*` pueden conservarse
por trazabilidad o usos auxiliares, pero no constituyen la ruta canónica actual
hacia el ACV.
