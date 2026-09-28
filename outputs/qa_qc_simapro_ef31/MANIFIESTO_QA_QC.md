# Manifiesto de insumos QA/QC Python–SimaPro EF 3.1

Estado: **preparado; verificación presencial pendiente**.

Estos archivos se derivan de la corrida **PROVISIONAL M1–M2**. Python conserva la fuente de verdad; SimaPro se limita a una verificación externa de la caracterización de flujos elementales.

## Archivos generados

- `casos_unitarios_python_ef31.csv`: 9 combinaciones flujo–compartimento–categoría.
- `inventario_provisional_m1_m2_para_simapro.csv`: 43 combinaciones reales por etapa, origen y categoría.
- `resumen_python_provisional_m1_m2_ef31.csv`: 6 subtotales por escenario y categoría.
- `plantilla_registro_presencial_simapro.csv`: copia en blanco para registrar la visita; los resultados observados deben conservarse como evidencia primaria, no incorporarse al generador.

## Exclusiones obligatorias

- La contribución eléctrica IMN agregada no se exporta como emisión elemental ni se recaracteriza.
- No se incorporan procesos de fondo de electricidad o diésel.
- No se reconstruyen los escenarios ni las etapas como procesos de SimaPro.
- No existen resultados SimaPro en este manifiesto.

## Fuentes canónicas y SHA-256

- `processed/acv_factores_equivalencia.csv`: `6affb79992caf210c97714df801d8dea5c030df10d1c4cf0336db7627d0a88e9`
- `processed/acv_foreground_intercambio.csv`: `f1c0be8e3d16bd44552505e7184f0c72253a0cd43b4314266746fefe238b9c49`
- `processed/acv_impacto_por_etapa_escenario.csv`: `7857b3d15a537bfb83834a763182a24a01ebfb14d686e3cfa95e3f5d93ab567d`

La regeneración se realiza con `scripts/generate_simapro_ef31_qa.py`. El protocolo permanente reside en `docs/PROTOCOLO_QA_QC_SIMAPRO_EF31.md`.
