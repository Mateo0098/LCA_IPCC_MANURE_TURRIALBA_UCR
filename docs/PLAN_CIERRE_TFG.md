# Plan operativo de cierre del TFG

## Estado

TFG en espera de M3. Existe una corrida científica **PROVISIONAL M1–M2** y un
documento integral provisional. Las unidades documentales pre-M3 de
reconciliación metodológica, marco teórico, referencias, metodología experimental
y completitud de resultados y apéndices ya fueron ejecutadas. El pipeline
científico y computacional permanece validado, sin bloqueantes científicos ni de
reproducibilidad identificados para el estado provisional.

## Reconciliación documental final pre-M3

La auditoría confirmó la coherencia del pipeline completo, la comparabilidad de
los escenarios, la conciliación de N total y TAN, la continuidad entre inventario,
EF 3.1 e impactos, la integración de los recursos IMN y la correspondencia entre
tablas, gráficos, resultados y conclusiones. Esta unidad cierra la reconciliación
documental científica pre-M3; las mejoras posteriores al integral se limitan a
trazabilidad académica y no modifican el modelo ni los resultados científicos.

## Unidad preparatoria de M3

El diseño experimental, los datos irrepetibles, las fuentes futuras y los
criterios de completitud se documentan en `docs/CONTRATO_EXPERIMENTAL_M3.md`.
La preparación no declara M3 disponible ni modifica resultados. La ingestión
queda protegida contra una declaración parcial de fuentes.

M3 continúa `no_disponible`; esta preparación no autoriza simularla ni retirar
la etiqueta **PROVISIONAL M1–M2**.

## Unidad activa independiente: QA/QC Python–SimaPro de EF 3.1

La metodología y los insumos reproducibles para verificar externamente la
caracterización EF 3.1 se encuentran en
`docs/PROTOCOLO_QA_QC_SIMAPRO_EF31.md` y
`outputs/qa_qc_simapro_ef31/`. La verificación presencial continúa pendiente y
no existen todavía resultados SimaPro. Esta unidad no altera el inventario, los
factores, la arquitectura IMN ni los resultados científicos canónicos.

## Siguiente unidad prevista

Después de ejecutar M3 y recibir el libro de Bioenergía y los informes CIA/LASA,
la siguiente unidad incorporará exclusivamente las fuentes reales al pipeline
canónico, comprobará compatibilidad y regenerará en secuencia todas las capas.

## Dependencias y bloqueos

- Dependencia principal: resultados analíticos de M3.
- La caracterización definitiva, la discusión completa y las conclusiones finales permanecen bloqueadas hasta integrar y validar M3.
- La trazabilidad final objetivos–resultados–conclusiones se realizará después de M3 sobre la corrida definitiva.
- La normalización bibliográfica, editorial e institucional final requiere revisión académica del documento integral.
- La verificación EF 3.1 requiere acceso presencial a una instalación UCR de
  SimaPro y el registro de la versión y configuración disponibles.

## Próximos hitos

1. Ejecutar M3 conforme al contrato experimental y conservar la evidencia primaria.
2. Incorporar las fuentes reales M3 mediante el pipeline vigente.
3. Completar la trazabilidad final entre objetivos, resultados y conclusiones.
4. Completar la verificación final de las referencias marcadas como pendientes en
   `docs/REFERENCIAS_TFG.md`.
5. Efectuar la revisión editorial e institucional final del documento integral.
6. Definir, si aporta valor después de M3, la evaluación cuantitativa mínima de sensibilidad para los supuestos
   dominantes, sin crear una ruta de cálculo paralela.
7. Ejecutar los casos unitarios y la comprobación agregada EF 3.1 en SimaPro,
   conservar la evidencia y, tras revisarla, incorporar metodología y resultados
   limitados al QA/QC en el documento integral.

## Paso de provisional a definitivo

Después de M3: integración estadística final → ACV → tablas y gráficos → metodología, resultados y conclusiones definitivos → actualización del documento integral → evaluación acotada de sensibilidad y consistencia → revisión académica → PDF.

La etiqueta **PROVISIONAL M1–M2** solo podrá retirarse cuando la corrida final incluya M3, las validaciones cruzadas hayan superado sus controles y la revisión académica confirme el cierre de resultados, discusión, conclusiones y referencias.
