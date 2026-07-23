\# Instrucciones para Codex en este repositorio



\## Objetivo del proyecto



Este repositorio corresponde al TFG sobre análisis de ciclo de vida de desechos bovinos sólidos y líquidos producidos en una lechería especializada en Turrialba, Costa Rica.



El objetivo es generar tablas, figuras y documentos académicos para tesis, no reportes técnicos de programación.



\## Reglas generales



\- No modificar el documento maestro de propuesta salvo instrucción explícita.

\- No usar archivos con sufijo `antes\_correccion\_nitrogeno`.

\- No hacer commit automáticamente.

\- Antes de modificar archivos, revisar `git status` y confirmar la branch activa.

\- Mantener valores numéricos, factores, ecuaciones y resultados salvo que la tarea pida explícitamente recalcular.

\- Corregir los scripts generadores, no solo los archivos finales.

\- El documento maestro protegido está en `MASTER\_escrito/TFG\_ACV\_Estiercol\_MASTER.docx`.

\- No modificar, sobrescribir ni usar como archivo de salida ningún archivo dentro de `MASTER\_escrito/`.

\- Los generadores pueden usar el documento maestro únicamente como referencia de formato y deben verificar su hash antes y después de generar documentos.



\## Escritura académica



Los documentos Word deben usar redacción académica y científica.



No usar en prosa ni tablas académicas etiquetas internas como:



\- dry\_lot

\- uncovered\_anaerobic\_lagoon

\- composting\_invessel

\- modelo\_calculo

\- sistema\_manejo\_ipcc

\- n\_ex\_pct

\- n\_ex\_fraction

\- masa\_total\_kg\_eq

\- processed

\- outputs

\- scripts

\- .csv

\- hardcodeado

\- auditado



Reemplazar etiquetas técnicas por lenguaje académico claro.



\## Nomenclatura de escenarios y etapas



Usar siempre:



\- A1: Precomposteo

\- A2: Lombricompostaje

\- A3: Almacenamiento de aguas verdes

\- A4: Aplicación de aguas verdes en campos de pastoreo

\- B1: Almacenamiento de purines

\- B2: Aplicación de purines en campo de pastoreo



No mostrar etapas con decimales, por ejemplo:



\- 1,000

\- 2,000

\- 3,000

\- 4,000

\- 1.0000

\- 2.0000



\## Aguas verdes y purines



En el Escenario A no usar la palabra “purín” ni “purines” para nombrar flujos.



Para A4 usar:



\- Agua de lavado incorporada a las aguas verdes

\- Fracción de boñiga incorporada a las aguas verdes

\- Masa equivalente total



Para B2 usar:



\- Agua de lavado incorporada al purín

\- Boñiga incorporada al purín

\- Masa equivalente total



\## Tablas en documentos Word



Las tablas deben verse académicas.



\- No duplicar columnas relacionadas con etapa.

\- Evitar columnas como `Etapa` y `Nombre etapa` al mismo tiempo.

\- Usar preferiblemente una sola columna: `Etapa del sistema`.

\- Los valores deben verse como `A4: Aplicación de aguas verdes en campos de pastoreo`.

\- No incluir rutas internas, nombres de scripts, archivos CSV ni columnas técnicas innecesarias.

\- Encabezados en español, claros y académicos.

\- Solo bordes horizontales, sin bordes verticales.



\## Codificación



Todos los archivos de texto deben leerse y escribirse en UTF-8.



Evitar errores como:



\- AnÃ¡lisis

\- metodologÃ­a

\- estiÃ©rcol

\- nitrÃ³geno



El texto final debe mostrar correctamente tildes, eñes y símbolos científicos.



\## Documentos principales



El documento maestro protegido y de referencia de formato es:



\- MASTER\_escrito/TFG\_ACV\_Estiercol\_MASTER.docx



Los documentos generados deben guardarse en `outputs/documentos\_tfg/`, nunca en `MASTER\_escrito/`.



Los documentos principales generados son:



\- outputs/documentos\_tfg/metodologia\_desarrollada\_tfg.docx

\- outputs/documentos\_tfg/resultados\_desarrollados\_tfg.docx



Cuando se actualicen, también actualizar:



\- outputs/documentos\_tfg/reporte\_validacion\_documentos.md

\- outputs/documentos\_tfg/README\_DOCUMENTOS\_GENERADOS.md



\## Validación obligatoria



Después de regenerar documentos, verificar:



\- No hay etiquetas técnicas internas visibles.

\- No hay etapas con decimales.

\- No hay errores de codificación.

\- No hay rutas internas en prosa académica.

\- No se modificaron valores numéricos sin instrucción explícita.

\- No se modificó el documento maestro de propuesta.

