# Plan operativo de cierre del TFG

## Estado

Existe una corrida científica **PROVISIONAL M1–M2** y un documento integral
provisional. La preparación académica del manuscrito previa a M3 quedó cerrada
en la Unidad 6 tras la auditoría integral y la corrección supervisada de sus
hallazgos editoriales y documentales. Este cierre no finaliza el TFG ni retira
su carácter provisional. M3 dispone
parcialmente de evidencia física —un libro gravimétrico todavía no declarado,
validado ni integrado—, mientras continúan pendientes las demás fuentes
analíticas previstas. La integración definitiva M3 → SimaPro permanece
pendiente.

El pipeline científico y computacional conserva su estado provisional validado.
La sesión Python–SimaPro PROVISIONAL M1–M2 ya fue ejecutada y deberá repetirse
después de integrar M3. Las revisiones posteriores pueden identificar mejoras
menores de procedencia, presentación o interpretación sin que ello implique
modificar automáticamente el modelo o sus resultados.

La primera evaluación determinística de sensibilidad del MCF del almacenamiento
líquido y de B₀ quedó implementada sobre la corrida **PROVISIONAL M1–M2**. Esta
fase comprueba reproducibilidad, respuesta paramétrica y posibles inversiones
de clasificación, pero no sustituye su repetición después de integrar M3 ni
convierte el dominio exploratorio del MCF en incertidumbre empírica.

## Preparación académica del manuscrito previa a M3

La auditoría integral de la Unidad 0 confirmó la arquitectura reproducible e
identificó correcciones académicas y científicas que deben resolverse antes de la
integración final. Las unidades de preparación no retiran la etiqueta
PROVISIONAL M1–M2 ni anticipan resultados de M3 o de la repetición de SimaPro.

### Seguimiento compacto de observaciones

| ID | Unidad responsable | Estado actual | Fuente documental responsable |
|---|---|---|---|
| OBS-01 | Unidad 1 | Cerrada tras revisión supervisora | Generador integral y reglas de redacción académica |
| OBS-02 | Unidad 1 | Cerrada tras revisión supervisora | Generador integral y registro bibliográfico |
| OBS-03 | Unidad 1 | Cerrada tras revisión supervisora | Generador integral y documentación de gobierno |
| OBS-04 | Unidad 2 | Cerrada tras revisión supervisora | Generadores académicos, diccionario de trazabilidad y fuente operativa publicada |
| OBS-05 | Unidad 2 | Cerrada tras revisión supervisora | Registro primario, parámetros operativos y decisiones metodológicas |
| OBS-06 | Unidad 2 | Cerrada tras revisión supervisora | Registro primario, matriz de procedencia y generadores académicos |
| OBS-07 | Unidad 3A | Cerrada tras revisión supervisora | Registro primario y generador integral |
| OBS-08 | Unidad 4B | Cerrada tras revisión supervisora en la Unidad 6 | Generador integral y reglas de formato Word |
| OBS-09 | Unidad 4B | Cerrada tras revisión supervisora en la Unidad 6 | Generador integral y reglas de formato Word |
| OBS-10 | Unidad 3B | Cerrada tras revisión supervisora | Catálogo fotográfico y generador de figuras integrales |
| OBS-11 | Unidad 3A | Cerrada tras revisión supervisora | Registro primario y generadores académicos |
| OBS-12 | Unidad 3A | Cerrada tras revisión supervisora | Registro primario y generadores académicos |
| OBS-13 | Unidad 3B | Cerrada tras revisión supervisora; se conserva el límite de identificación del horno | Catálogo fotográfico, registro primario y generador de figuras integrales |
| OBS-14 | Unidad 4A | Cerrada tras revisión supervisora | Generador integral, utilidad OMML y reglas de formato Word |
| OBS-15 | Unidad 4B | Cerrada tras revisión supervisora en la Unidad 6 | Registro bibliográfico, factores IMN y generadores académicos |
| OBS-16 | Unidades 5A–5B y unidad de incorporación académica | Contraste provisional M1–M2 incorporado y validado técnicamente en metodología, resultados, discusión y conclusiones; revisión supervisora pendiente. La actualización científica definitiva permanece pendiente después de M3 | Generador integral, decisiones metodológicas, ledger de N, salidas auxiliares QA/QC y fuentes experimentales |

## Unidad preparatoria de M3

El diseño experimental, los datos irrepetibles, las fuentes futuras y los
criterios de completitud se documentan en `docs/CONTRATO_EXPERIMENTAL_M3.md`.
La preparación no declara M3 disponible ni modifica resultados. La ingestión
queda protegida contra una declaración parcial de fuentes.

M3 continúa `no_disponible` para el pipeline porque no se ha declarado el
conjunto completo de fuentes. La existencia física parcial de un libro no
autoriza simular la campaña, integrarla ni retirar la etiqueta **PROVISIONAL
M1–M2**.

## Incorporación académica Python–SimaPro de EF 3.1

La metodología y los insumos reproducibles para verificar externamente la
caracterización EF 3.1 se encuentran en
`docs/PROTOCOLO_QA_QC_SIMAPRO_EF31.md` y
`outputs/qa_qc_simapro_ef31/`. La sesión PROVISIONAL M1–M2 fue ejecutada el
2026-10-07 y su evidencia quedó integrada. Sus métodos, resultados, interpretación
y limitaciones se incorporaron al documento integral PROVISIONAL M1–M2 para la
revisión del comité asesor. Esta unidad no altera el inventario, los factores, la
arquitectura IMN ni los resultados científicos canónicos. La comprobación
agregada deberá repetirse después de incorporar y validar M3.

## Siguiente transición científica prevista

Con la preparación académica pre-M3 cerrada, la incorporación de M3 utilizará
exclusivamente las fuentes reales completas del pipeline
canónico, comprobará su compatibilidad y regenerará en secuencia todas las
capas. La unidad académica que siga a la presente será definida por Mateo y
ChatGPT conforme al flujo de coordinación; este plan no inicia esa transición.

## Dependencias y bloqueos

- Dependencia principal: resultados analíticos de M3.
- La caracterización definitiva, la discusión completa y las conclusiones finales permanecen bloqueadas hasta integrar y validar M3.
- La trazabilidad final objetivos–resultados–conclusiones se realizará después de M3 sobre la corrida definitiva.
- La verificación bibliográfica restante se limita a las fuentes activas aún
  marcadas de forma específica en `docs/REFERENCIAS_TFG.md`; no reabre las
  referencias ya cotejadas ni impide el cierre académico provisional pre-M3.
- La repetición definitiva de la verificación EF 3.1 requiere primero integrar
  y validar M3 y después acceder nuevamente a la instalación UCR de SimaPro.

## Próximos hitos

1. Completar y documentar las actividades experimentales pendientes de M3,
   reunir el paquete analítico requerido y verificar su suficiencia y compatibilidad.
2. Incorporar las fuentes reales M3 mediante el pipeline vigente.
3. Completar la trazabilidad final entre objetivos, resultados y conclusiones.
4. Completar, antes de la versión definitiva, los pendientes bibliográficos
   específicos conservados en `docs/REFERENCIAS_TFG.md`.
5. Efectuar después de M3 la revisión editorial e institucional final del
   documento integral definitivo.
6. Repetir después de M3 la sensibilidad determinística de MCF y B₀ mediante la
   interfaz canónica ya implementada y decidir, con rangos documentados, si se
   amplía a otros supuestos dominantes.
7. Repetir la comprobación agregada EF 3.1 en SimaPro después de integrar M3 y
   actualizar la sección académica antes de tratarla como verificación definitiva.

## Paso de provisional a definitivo

Después de M3: integración estadística final → ACV → tablas y gráficos → metodología, resultados y conclusiones definitivos → actualización del documento integral → evaluación acotada de sensibilidad y consistencia → revisión académica → PDF.

La etiqueta **PROVISIONAL M1–M2** solo podrá retirarse cuando la corrida final incluya M3, las validaciones cruzadas hayan superado sus controles y la revisión académica confirme el cierre de resultados, discusión, conclusiones y referencias.
