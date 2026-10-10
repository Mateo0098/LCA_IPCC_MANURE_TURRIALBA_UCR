# Protocolo de QA/QC Python–SimaPro para Environmental Footprint 3.1

## Propósito y estado

Este protocolo establece una verificación independiente de la caracterización
Environmental Footprint 3.1 aplicada por Python a los flujos elementales del
inventario del TFG. La sesión presencial correspondiente a la corrida
**PROVISIONAL M1–M2** se ejecutó el 2026-10-07 y su evidencia quedó integrada
en `outputs/qa_qc_simapro_ef31/evidencia_sesion_2026-10-07/`. La comprobación
deberá repetirse cuando M3 se encuentre incorporada y validada en el pipeline.

Python continúa siendo la fuente de verdad del inventario, la caracterización,
la agregación, la normalización y los resultados canónicos. SimaPro no sustituye
ni reconstruye el ACV: se utiliza solamente para contrastar factores y resultados
de caracterización a partir de las mismas cantidades elementales.

## Alcance y exclusiones

La verificación cubre las combinaciones activas de flujo elemental,
compartimento y categoría contenidas en
`processed/acv_factores_equivalencia.csv`. Incluye las emisiones elementales de
CO₂ fósil, CH₄ fósil y N₂O derivadas del consumo operacional de diésel, pero
no incorpora un proceso de producción o distribución de combustible.

Quedan fuera del contraste:

- la contribución climática agregada de electricidad calculada con el factor IMN,
  porque no es una emisión elemental y no debe recaracterizarse;
- procesos de fondo de electricidad o diésel;
- la reconstrucción de los escenarios A/B o de las etapas A1–A4/B1–B2 como
  procesos SimaPro;
- la normalización por unidad funcional, que permanece bajo responsabilidad del
  pipeline Python;
- cualquier dato o resultado de M3, que permanece `no_disponible`.

La comparación vigente corresponde exclusivamente a la corrida **PROVISIONAL
M1–M2**.

## Fuentes y artefactos reproducibles

`scripts/generate_simapro_ef31_qa.py` consume las fuentes canónicas y genera en
`outputs/qa_qc_simapro_ef31/`:

- `casos_unitarios_python_ef31.csv`: un caso de 1 kg por cada combinación activa
  flujo–compartimento–categoría;
- `inventario_provisional_m1_m2_para_simapro.csv`: cantidades elementales reales
  por escenario, etapa, origen y categoría, sin electricidad IMN;
- `resumen_python_provisional_m1_m2_ef31.csv`: subtotales EF 3.1 esperados por
  escenario y categoría;
- `plantilla_registro_presencial_simapro.csv`: campos en blanco para documentar
  la visita;
- `MANIFIESTO_QA_QC.md`: estado, exclusiones y huellas SHA-256 de los insumos
  reproducibles, sin incorporar el estado histórico de las sesiones.

La plantilla original permanece en blanco y regenerable. El registro factual de
la sesión ejecutada se conserva por separado en
`registro_presencial_simapro_2026-10-07.csv`. La carpeta fechada contiene 18
capturas, dos PDF de resultados agregados, un README descriptivo y el inventario
de huellas `SHA256SUMS.csv`.

La integridad de una carpeta histórica se comprueba de forma explícita e
independiente con:

`python scripts/validate_simapro_session_evidence.py <carpeta_de_sesion>`

El validador exige README, inventario sin duplicados, correspondencia exacta de
archivos y coincidencia de todas las huellas SHA-256. El generador de insumos no
lee ni valida evidencia presencial y funciona aunque no exista una carpeta de
sesión.

Los números no se mantienen manualmente en este protocolo. El generador obtiene
los factores de `processed/acv_factores_equivalencia.csv`, las cantidades de
`processed/acv_foreground_intercambio.csv` y verifica los productos contra
`processed/acv_impacto_por_etapa_escenario.csv`.

## Auditoría de la implementación Python

La caracterización se implementa en
`scripts/compute_acv_impact_equivalents.py`. La identidad del factor se define
por la terna flujo elemental–compartimento–categoría. El cargador exige el
método `Environmental Footprint`, versión `3.1`, las unidades previstas y el
conjunto completo de factores activos.

Antes de caracterizar, el inventario agrega por etapa las masas en kilogramos de
CH₄ biogénico, N₂O molecular, NH₃, NOx expresado como NO₂ y NO₃⁻. Para el
diésel, `scripts/imn_operational_factors.py` convierte litros en kg de CO₂
fósil y convierte los factores de CH₄ y N₂O desde g/L a kg/L. La electricidad
se calcula por separado como kWh multiplicados por el factor agregado IMN.

Para cada especie y categoría verificable se aplica:

`resultado de categoría = masa elemental en kg × factor de caracterización EF 3.1`

Los resultados por categoría son la suma de los productos correspondientes. El
cambio climático total publicado por Python añade después la electricidad IMN;
por eso no debe compararse directamente con un subtotal exclusivamente EF 3.1
obtenido en SimaPro.

La implementación cuenta con casos unitarios, controles de metadatos y pruebas de
inventario operativo en `tests/test_ef31_operational_inventory.py`, además del
validador `scripts/validate_ef31_operational_inventory.py`. Los insumos de esta
verificación externa añaden sus controles en
`tests/test_simapro_ef31_qa.py`.

Los factores alimentan `processed/acv_impacto_por_etapa_escenario.csv` y
`processed/acv_impacto_total_por_escenario.csv`; desde allí se propagan a las
tablas 07 y 08, las figuras de impactos y comparación climática, y los documentos
académicos de metodología, resultados, conclusiones e integral. Estos productos
permanecen canónicos y no son reemplazados por los archivos de QA/QC.

La tabla canónica identifica como fuente el libro
`EF-LCIAMethod_CF(EF-v3.1).xlsx`, pero la auditoría del repositorio no localizó
una copia versionada de ese archivo. El identificador se conserva sin
reinterpretarlo; recuperar y archivar la fuente oficial, si las condiciones de
distribución lo permiten, queda como pendiente de trazabilidad bibliográfica y
no se sustituye por una exportación de SimaPro.

## Ejecución presencial y registro de la sesión 2026-10-07

Antes de introducir datos, registrar la versión exacta de SimaPro instalada, el
nombre y versión exactos del método Environmental Footprint disponible y toda
configuración seleccionable que pueda alterar la caracterización. La ubicación
de estas funciones y los nombres de las opciones deben confirmarse en la
instalación UCR o en su ayuda local; este protocolo no presume una ruta de menú.

Para cada fila de `plantilla_registro_presencial_simapro.csv`:

1. Crear o utilizar un caso aislado que contenga exactamente 1 kg del flujo
   elemental indicado, sin procesos de fondo ni otros intercambios.
2. Buscar el flujo mediante el nombre y los alias propuestos, pero seleccionar
   solo una correspondencia cuya identidad química, origen fósil o biogénico,
   unidad, compartimento y subcompartimento hayan sido confirmados.
3. Aplicar el método Environmental Footprint disponible y registrar la categoría,
   el factor visible y el resultado del caso unitario. Si el factor no es visible,
   indicarlo y conservar el resultado unitario sin inferir metadatos no mostrados.
4. Registrar literalmente el nombre del flujo, la unidad, el compartimento y el
   subcompartimento usados por SimaPro, incluso cuando difieran de Python.
5. Conservar evidencia trazable: exportación o tabla cuando sea posible; en una
   instalación restringida, captura o fotografía legible que muestre versión,
   método, flujo, categoría y resultado. Anotar la ruta o identificador de la
   evidencia, sin reemplazarla por una transcripción sin respaldo.

La plantilla generada permanece en blanco y puede regenerarse. Para cada sesión
se conserva una copia fechada junto con la evidencia primaria; no se escriben
observaciones presenciales dentro del generador ni se sobrescriben al regenerar
los insumos.

La sesión del 2026-10-07 utilizó SimaPro 10.4.0.0 Educational, instalación UCR
004, el proyecto local `MATEO_TFG_TESTING` y el método `Environmental Footprint
3.1 (adapted)` V1.05. Se inspeccionaron directamente las nueve combinaciones
activas de factor. Se ejecutaron de extremo a extremo cinco procesos unitarios
de 1 kg: N₂O, CH₄ biogénico, NH₃, NOx y NO₃⁻. Los factores de CO₂ fósil y CH₄
fósil se inspeccionaron en la tabla del método, pero no se ejecutaron como
procesos unitarios independientes.

Los siete resultados de categoría observables en esos cinco procesos coincidieron
con Python dentro de la precisión de pantalla. Se clasificaron como A las
comparaciones de N₂O, CH₄ biogénico, NH₃ marino, NOx terrestre, NOx marino y
NO₃⁻ marino. El resultado terrestre de NH₃ se mostró como 13,5 mol N-eq frente
al factor 13,47 y se clasificó como B por redondeo de presentación. La captura
`07_factor_nh3_marino_0.092.png` muestra directamente el factor marino 0,092;
`07b_factor_nh3_terrestre_13.47.png` muestra directamente el factor terrestre
13,47; y `13_unitario_nh3_1kg_resultado.png` documenta el resultado visible
redondeado a 13,5.

## Protocolo de comparación

Para cada caso se calculan, sin redondeo prematuro:

- diferencia absoluta = resultado SimaPro − resultado Python;
- diferencia relativa = diferencia absoluta / resultado Python, cuando el
  resultado Python sea distinto de cero.

Cada comparación recibe exactamente una clasificación:

- **A. Identidad exacta o concordancia dentro del redondeo:** los valores
  coinciden exactamente o al número de cifras efectivamente mostrado por ambas
  herramientas.
- **B. Precisión o redondeo explicable:** la diferencia se reproduce al aplicar
  el factor visible o la precisión de presentación documentada.
- **C. Versión o configuración del método:** la instalación no ofrece la misma
  versión/configuración o esa diferencia explica el resultado.
- **D. Identidad del flujo:** la correspondencia química, el origen fósil o
  biogénico, o la sustancia de referencia no coincide.
- **E. Compartimento o subcompartimento:** el receptor ambiental difiere.
- **F. Unidad o conversión:** existe una diferencia de unidad, masa de sustancia
  de referencia o conversión previa.
- **G. Sin correspondencia verificable:** no se localiza un flujo SimaPro cuya
  identidad completa pueda justificarse.
- **H. Discrepancia no resuelta:** la diferencia persiste después de revisar todos
  los elementos anteriores y requiere investigación adicional.

Antes de modificar Python se deben revisar, en este orden, identidad química,
nombre del flujo, compartimento, subcompartimento, unidad, masa de sustancia de
referencia, origen fósil/biogénico, versión y configuración del método, factor,
conversiones, redondeo y limitaciones de la instalación SimaPro. Una diferencia
no demuestra por sí sola que alguno de los dos cálculos sea incorrecto.

## Segunda comprobación con cantidades PROVISIONAL M1–M2

Solo después de resolver o clasificar los casos unitarios se utilizan las filas
de `inventario_provisional_m1_m2_para_simapro.csv`. Deben introducirse las mismas
cantidades elementales, conservando identidad, unidad y compartimento. Puede
agruparse por escenario para obtener los tres subtotales contenidos en
`resumen_python_provisional_m1_m2_ef31.csv`; no es necesario ni deseable modelar
las etapas como procesos.

El subtotal de cambio climático para este contraste contiene CH₄ biogénico,
N₂O y las emisiones fósiles del diésel. Excluye expresamente la contribución
eléctrica IMN. Los subtotales de eutrofización se comparan en sus unidades EF
3.1 respectivas. Los resultados SimaPro no se reimportan como sustitutos de los
resultados Python.

La segunda comprobación se ejecutó el 2026-10-07 mediante dos procesos agregados
con las cantidades elementales preparadas por Python. Las diferencias siguientes
se definen como SimaPro menos Python y se deben exclusivamente a la precisión
decimal mostrada en los PDF:

| Escenario | Categoría EF 3.1 | Python | SimaPro | Diferencia absoluta | Diferencia relativa | Clasificación |
|---|---|---:|---:|---:|---:|:---:|
| A | Cambio climático (kg CO₂-eq) | 3167,904519914095 | 3167,9045 | -0,000019914095 | -6,286 × 10⁻⁹ | A |
| A | Eutrofización marina (kg N-eq) | 15,648347825374902 | 15,648348 | 0,000000174625098 | 1,116 × 10⁻⁸ | A |
| A | Eutrofización terrestre (mol N-eq) | 617,0517125078838 | 617,05171 | -0,0000025078838 | -4,064 × 10⁻⁹ | A |
| B | Cambio climático (kg CO₂-eq) | 6252,09813683376 | 6252,0981 | -0,00003683376 | -5,891 × 10⁻⁹ | A |
| B | Eutrofización marina (kg N-eq) | 35,62231521609108 | 35,622315 | -0,00000021609108 | -6,066 × 10⁻⁹ | A |
| B | Eutrofización terrestre (mol N-eq) | 961,269308200257 | 961,26931 | 0,000001799743 | 1,872 × 10⁻⁹ | A |

Esta concordancia comprueba únicamente la caracterización EF 3.1 de los flujos
elementales incluidos. No valida por sí sola el inventario, los procesos de
fondo, la contribución eléctrica IMN, la normalización funcional ni una corrida
con M3. La comprobación agregada se repetirá con los insumos definitivos después
de integrar y validar M3.

## Incorporación académica posterior

La evidencia de esta sesión se integra en el repositorio sin modificar ni
regenerar el documento escrito del TFG. Una incorporación académica posterior,
si se autoriza, deberá describir el propósito independiente, software y versión,
método exacto, selección de flujos, casos unitarios, criterios A–H, tratamiento
de discrepancias, alcance y exclusiones.

Los resultados deberán presentar una tabla Python–SimaPro con las identidades
verificadas, valores observados, diferencias, clasificaciones y explicaciones.
La conclusión se limitará a la validez de la caracterización comprobada; no se
extenderá a la corrección del inventario, a procesos de fondo, a la comparación
completa de escenarios ni a M3. La evidencia PROVISIONAL M1–M2 no debe
presentarse como comprobación definitiva después de incorporar M3.
