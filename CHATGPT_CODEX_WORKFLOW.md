# Flujo de coordinación entre Mateo, ChatGPT y Codex

## Propósito

Este documento regula la coordinación entre Mateo, ChatGPT y Codex: discusión
de decisiones, preparación de instrucciones, ejecución dentro del repositorio,
generación de reportes y revisión posterior. No sustituye las reglas técnicas
de `README.md` y `AGENTS.md`, las decisiones metodológicas ni la documentación
específica del pipeline.

## Roles

### Mateo

- Es el autor y responsable del TFG.
- Discute con ChatGPT las decisiones metodológicas, técnicas y documentales.
- Ejecuta en Codex los prompts preparados por ChatGPT.
- Entrega a ChatGPT los reportes de ejecución solicitados.

### ChatGPT

ChatGPT cumple dos funciones: asesor del TFG y experto en diseño de prompts y
supervisión del trabajo encargado a Codex. Ayuda a Mateo a resolver decisiones
y las transforma en instrucciones concretas, verificables y acotadas para
Codex. No debe delegar a Codex decisiones metodológicas sustantivas que Mateo y
ChatGPT todavía no hayan resuelto.

### Codex

Codex es el agente que trabaja directamente dentro del repositorio. Según el
alcance autorizado, puede inspeccionar archivos, modificar código y
documentación, ejecutar comandos, regenerar productos, efectuar verificaciones
y documentar lo realizado. Debe respetar las decisiones y reglas vigentes del
repositorio, especialmente `AGENTS.md`, `README.md` y los documentos de
decisiones metodológicas aplicables.

## Tres niveles de continuidad

El flujo distingue tres niveles relacionados, pero no equivalentes:

- **Chat de ChatGPT:** espacio de decisión, supervisión y seguimiento de un objetivo principal.
- **Rama Git:** unidad de aislamiento y versionado de un conjunto coherente de cambios.
- **Sesión de Codex:** contexto operativo del agente que inspecciona y modifica el repositorio.

No existe una relación obligatoria 1:1 entre ellos. Un chat puede requerir varias
sesiones de Codex, una rama puede abarcar varios chats relacionados y una nueva
sesión de Codex puede continuar sobre la misma rama. Un cambio de rama sí debe
motivar la evaluación de si conviene iniciar una nueva sesión de Codex.

## Objetivos del trabajo

### Unidad de trabajo y trazabilidad mínima

Una **unidad de trabajo** es un conjunto coherente de cambios orientado a un
objetivo concreto y susceptible de revisión conjunta. No requiere un
identificador numerado: el nombre semántico de la rama, el reporte temporal y
el historial Git aportan el contexto suficiente.

Durante la ejecución, el reporte de Codex conecta brevemente el objetivo con la
rama, el `HEAD` y el estado del working tree. Puede indicar que la unidad inicia
o continúa trabajo anterior y, si existe, identificar el checkpoint publicado
que queda pendiente de revisión o el commit que consolida su cierre. Esta
información facilita la revisión, pero sigue siendo temporal.

Un commit normal publicado en la rama activa puede funcionar como **checkpoint
reproducible para revisión** antes de que ChatGPT valide la unidad. Representa
un estado coherente que Codex considera técnicamente preparado para revisión y
permite recuperarlo desde GitHub mediante rama y SHA. No implica aprobación
metodológica, científica, documental ni supervisora, no valida la unidad, no la
cierra y no autoriza su integración a `main`.

Una unidad puede acumular varios checkpoints publicados mientras se corrigen
observaciones. Sus mensajes deben expresar el propósito real del cambio; Git
conserva la evolución sin ledgers, inventarios manuales, copias de conversaciones
ni registros de sesiones. La unidad solo se considera validada después de la
revisión supervisora satisfactoria de ChatGPT.

Una sesión nueva de Codex puede continuar la misma unidad y rama. No se guardan
IDs internos de sesión: cuando el cambio de contexto resulte relevante, basta
con indicarlo en el reporte. Cambiar de rama obliga a reevaluar si conviene una
sesión nueva, pero iniciar una sesión nueva no obliga a crear otra rama.

### Objetivo principal del chat

Al comenzar una nueva línea de trabajo, ChatGPT debe identificar y mantener
claro el objetivo principal del chat. Puede ser, por ejemplo, diagnosticar una
inconsistencia, actualizar documentación, corregir un componente o validar un
conjunto coherente de cambios. No se exige una fórmula ni un formulario rígido:
el objetivo funciona como criterio práctico de seguimiento y cierre.

Si el objetivo cambia de manera significativa, ChatGPT debe evaluar si el nuevo
trabajo continúa naturalmente en el mismo chat, si conviene abrir otro o si
también requiere una rama separada.

### Preguntas aclaratorias dinámicas

ChatGPT puede preguntar a Mateo en cualquier momento de una unidad de trabajo
cuando la respuesta ayude materialmente a comprender el objetivo, resuelva una
ambigüedad importante, evite una decisión potencialmente incorrecta o requiera
un criterio que corresponda al investigador. La pregunta puede surgir al inicio,
después de una inspección o diagnóstico de Codex, al revisar un reporte, durante
una implementación o antes del cierre. No constituye una fase obligatoria del
flujo ni requiere un cuestionario fijo.

ChatGPT debe evitar preguntas cuya respuesta pueda obtenerse del repositorio,
verificarse mediante Codex, ya esté documentada, pueda inferirse con seguridad
suficiente o corresponda a un detalle menor que no cambie materialmente la
solución. Cuando resulte más eficiente, puede encargar primero a Codex una
inspección del estado del repositorio y formular después una pregunta más
precisa a partir de los hallazgos. Si existen varias dudas, debe priorizar las
que condicionen realmente el siguiente paso y no acumular preguntas menores.

El principio general es avanzar autónomamente cuando sea seguro y preguntar a
Mateo cuando su intención o criterio sea realmente necesario. Estas
intervenciones pueden aparecer dinámicamente dentro del flujo existente, sin
alterar su secuencia general ni añadir una fase rígida.

### Objetivo de la rama

El objetivo del chat y el objetivo de la rama Git no tienen que ser idénticos.
Normalmente existe una sola rama activa de avance, que puede reunir cambios
científicos, metodológicos, documentales, técnicos y de gobernanza del TFG.
ChatGPT debe conocerla mediante el contexto Git de los reportes de Codex. No se
requiere una rama distinta para cada unidad ni una separación estricta por tipo
de cambio.

### Cierre conceptual de una rama

El cierre de una unidad de trabajo no implica por sí solo cerrar la rama. Una
rama queda conceptualmente terminada cuando su propósito actual está
suficientemente completo: las unidades previstas para ese propósito están
cerradas, los cambios relevantes cuentan con las validaciones y actualizaciones
documentales aplicables, los commits forman checkpoints coherentes y publicados,
el working tree está limpio y no quedan pendientes que pertenezcan naturalmente
al mismo objetivo. No es necesario agotar toda mejora futura relacionada con el
tema; esas mejoras pueden constituir una línea posterior independiente.

La decisión se basa en el estado acumulado, no en días, cantidad de tareas,
número de commits ni categorías de cambios. Mateo determina cuándo el avance es
considerable, coherente y suficientemente validado para integrar completa la
rama a `main`.

### Modelo Git simplificado

Este repositorio se utiliza principalmente como proyecto individual y como
sistema de respaldo y recuperación. `main` representa la versión estable e
integrada del TFG que pueden consultar los asesores. El flujo habitual es:

```text
main estable → una rama activa de avance → trabajo y validaciones
→ promoción completa a main cuando el avance sea significativo
→ nueva rama de avance cuando corresponda
```

Después de la integración, `main` vuelve a ser la referencia vigente y el
siguiente avance relevante puede comenzar desde ese estado actualizado. Las
ramas anteriores pueden conservarse como respaldo o referencia histórica sin
eliminarse automáticamente; una rama histórica no es fuente vigente ni línea
activa de trabajo. No se imponen ramas estrictamente temáticas, varias ramas
activas en paralelo, releases ni estrategias avanzadas de Git salvo que surja
una necesidad real.

## Flujo general de trabajo

```text
Mateo + ChatGPT → prompt para Codex → implementación
→ verificaciones técnicas de Codex → checkpoint commit + push → reporte
→ ChatGPT recupera archivos desde GitHub → validación de ChatGPT
```

1. Mateo y ChatGPT discuten primero la decisión o el cambio.
2. ChatGPT prepara un prompt concreto para Codex.
3. Mateo ejecuta ese prompt en Codex.
4. Codex implementa el alcance y realiza las verificaciones técnicas pertinentes.
5. Si el prompt lo autoriza expresamente y las verificaciones permiten continuar,
   Codex crea un checkpoint normal, lo publica sin reescribir la historia y genera
   el reporte solicitado en `.codex_reports/`.
6. Mateo entrega el reporte a ChatGPT en lugar de copiar largas salidas de terminal.
7. ChatGPT revisa primero el reporte, selecciona los archivos necesarios y procura
   recuperarlos directamente desde GitHub por repositorio, SHA exacto y ruta.
8. ChatGPT valida el estado inmutable del checkpoint. Las comprobaciones técnicas
   de Codex no sustituyen esta revisión supervisora.
9. Si hay problemas, ChatGPT evalúa la estrategia de recuperación descrita a
   continuación y prepara un prompt específico; el ciclo produce un nuevo
   checkpoint para otra revisión. Si valida, la unidad puede considerarse validada
   y pasar posteriormente a su revisión de cierre.

### Codex verifica; ChatGPT valida

La verificación técnica de Codex se limita a comprobaciones mecánicas y
reproducibles proporcionales al alcance: confirmar la implementación, revisar el
diff, detectar archivos accidentales, ejecutar `git diff --check`, comprobar
sintaxis o compilación, ejecutar validadores existentes pertinentes, regenerar
productos afectados, revisar coherencia básica y excluir `.codex_reports/` y
temporales del commit. Superar esas verificaciones solo significa que el estado
está técnicamente preparado para revisión.

La validación de ChatGPT puede evaluar la correspondencia con las decisiones de
Mateo, la interpretación metodológica, la coherencia científica, el código, la
documentación, la consistencia entre archivos, las omisiones y la necesidad de
correcciones. Un checkpoint no queda validado por el solo hecho de que las
verificaciones técnicas hayan pasado.

Si un validador falla, existe un error conocido, se detecta un cambio accidental,
aparece un resultado inesperado sin resolver o falta una decisión de Mateo o
ChatGPT, Codex no crea el checkpoint salvo autorización excepcional y explícita.
Debe dejar la unidad pendiente y describir el problema en el reporte.

### Recuperación ante un checkpoint rechazado

Cuando ChatGPT no valida un checkpoint publicado, debe preferir una corrección
hacia adelante si el defecto está claramente localizado, la mayor parte del
cambio continúa siendo válida, pueden identificarse los archivos o cálculos
afectados, la reparación puede verificarse razonablemente y continuar no propaga
supuestos incorrectos. Esto comprende, por ejemplo, una ecuación o condición
puntual, una actualización documental omitida, una etiqueta o redacción
incorrecta, un producto que deba regenerarse, una validación faltante o un error
pequeño de implementación con alcance identificable. El flujo ordinario conserva
el checkpoint rechazado y añade el correctivo para someter el nuevo SHA a revisión.

ChatGPT debe considerar regresar al último estado validado cuando el checkpoint
rechazado parta de una interpretación metodológica fundamentalmente incorrecta,
altere varias capas bajo un supuesto equivocado, mezcle cambios independientes
difíciles de separar, introduzca modificaciones extensas fuera del alcance o deje
resultados y productos cuya confiabilidad ya no pueda aislarse. También procede
considerarlo cuando ya no sea claro qué partes siguen siendo correctas o cuando
corregir encima resulte más riesgoso o costoso que reconstruir desde el último
estado confiable. Volver atrás es una herramienta legítima de control, no un
fracaso del flujo, y no existe una preferencia artificial por nunca retroceder.

La decisión debe minimizar el riesgo de propagar errores, la pérdida de trabajo
válido, el retrabajo, la contaminación metodológica o técnica y la pérdida de
trazabilidad. Antes de ordenar un regreso, ChatGPT identifica explícitamente el
último SHA satisfactoriamente validado: no presume que sea el checkpoint
inmediatamente anterior, `main` ni cualquier commit publicado en la rama. El
reporte temporal y el historial Git deben permitir distinguir el último estado
validado conocido, los checkpoints pendientes o rechazados y el estado actual de
la rama, sin crear un ledger permanente.

ChatGPT elige el mecanismo Git después de evaluar el checkpoint y el historial.
Según el caso, puede autorizar un commit que restaure explícitamente el estado
validado, `git revert` de uno o varios checkpoints, recomenzar desde un commit
validado en la rama activa sin perder trabajo relevante u otra estrategia segura
y trazable. Por defecto no se usa `reset --hard` sobre historia publicada ni se
emplean `force-push`, `rebase` o `amend` para borrar la existencia del checkpoint
rechazado. Una excepción requiere una razón real y autorización explícita de Mateo
o ChatGPT.

Codex no escoge autónomamente entre corregir hacia adelante y volver atrás. Puede
advertir que el estado parece ampliamente contaminado o que una reparación local
sería arriesgada, pero ChatGPT determina la estrategia y prepara un prompt
específico. Codex ejecuta solo esa estrategia, verifica técnicamente el nuevo
estado y, si el prompt lo autoriza y las verificaciones pasan, crea y publica un
nuevo checkpoint. Mateo entrega el reporte y ChatGPT vuelve a validar.

```text
checkpoint → revisión de ChatGPT → rechazado
                 ↓
     ¿problema localizado y estado confiable?
           ↙                         ↘
         sí                            no
corregir hacia adelante       considerar volver al
                              último estado validado
           ↘                         ↙
                 nuevo checkpoint
                        ↓
                  nueva revisión
```

### Recuperación directa para revisión desde GitHub

Cuando el checkpoint esté publicado, el reporte identifica el repositorio
completo `owner/repository`, la rama, el SHA completo, si fue publicado, el
resultado de las verificaciones técnicas, la revisión pendiente de ChatGPT y la
ausencia de autorización para integrar a `main`. También enumera los archivos
potencialmente relevantes, con ruta, tipo y motivo del cambio, inclusión en el
checkpoint y posible interés supervisor, sin decidir por ChatGPT cuáles debe
revisar definitivamente.

ChatGPT revisa primero el reporte y prefiere obtener cada versión desde el SHA
inmutable, no desde el `HEAD` cambiante de la rama. Solo pide a Mateo una carga
manual si la versión necesaria no puede recuperarse o inspeccionarse
adecuadamente mediante GitHub, por ejemplo por tratarse de un binario, un
artefacto demasiado grande, un archivo no versionado o deliberadamente excluido,
o por un fallo real de acceso. No solicita archivos manualmente por rutina cuando
el checkpoint ya contiene una versión accesible.

### Contexto de rama

Cada reporte de Codex debe incluir el contexto Git obligatorio definido en
`AGENTS.md`: rama, commit `HEAD` y estado general del working tree al inicio y
al final, además de cualquier cambio de rama y su causa. Al recibir el reporte,
ChatGPT debe usar la rama allí indicada como contexto inicial para las consultas,
prompts y validaciones relacionadas con esa tarea, pero no asumir solo por estar
checkout que continúa siendo la referencia vigente. Debe contrastar si contiene
avance abierto, si su propósito sigue activo y si es compatible con la unidad.
Una rama histórica, cerrada, experimental, abandonada o ya integrada no se vuelve
vigente por el mero hecho de estar checkout.

Si ChatGPT sabe que el trabajo relevante todavía vive en otra rama, no debe
consultar `main` como fuente vigente de esa tarea. Esta regla evita preparar
prompts o validar cambios usando código o documentación desactualizados. Si la
rama inicial y la final difieren, ChatGPT debe tomar en cuenta la explicación
registrada antes de continuar la coordinación.

## Reportes temporales de Codex

Salvo que no resulte aplicable, los prompts para Codex deberían solicitar un
reporte con una ruta como:

```text
.codex_reports/YYYY-MM-DD_descripcion_tarea.md
```

Los reportes son artefactos temporales de coordinación y auditoría. No son
fuente de verdad, entrada del pipeline, documentación metodológica oficial,
datos del TFG ni resultados permanentes. Pueden eliminarse posteriormente sin
afectar la reproducibilidad del proyecto y no deben incluirse en commits
ordinarios.

La carpeta completa `.codex_reports/` está excluida mediante `.gitignore`. Puede
vaciarse o recrearse sin afectar la ejecución ni la comprensión del proyecto;
ningún script, validador o documento permanente debe depender de su contenido.

El contenido mínimo que Codex debe aportar para facilitar el cierre se define en
`AGENTS.md`. El prompt puede solicitar información adicional según el alcance de
la tarea, sin convertir el reporte en un formulario extenso.

No es necesario conservar indiscriminadamente logs completos cuando un resumen
reproducible sea suficiente. Los hechos permanentes necesarios para ejecutar o
comprender el proyecto deben quedar en la documentación versionada apropiada,
no solamente en un reporte temporal.

### Ciclo de vida y limpieza de la bandeja temporal

`.codex_reports/` funciona como una bandeja temporal de coordinación, no como
un archivo histórico. No se aplica una retención rígida por antigüedad o número
de archivos. Se conservan los reportes que todavía sostienen una unidad abierta,
una revisión o validación pendiente, un cierre Git aún no confirmado o un
diagnóstico que condiciona una decisión vigente.

Un reporte puede retirarse cuando la unidad ya fue validada, consolidada,
publicada o integrada según correspondiera, no quedan decisiones pendientes y
los hechos permanentes necesarios ya residen en Git o en la documentación
responsable. Los reportes retirados no se trasladan a archivos históricos:
Git, los commits y la documentación viva constituyen el historial permanente.

Codex debe evaluar esta limpieza de forma contextual al comenzar una unidad,
durante el trabajo y después de confirmar su cierre o integración. La limpieza
es conservadora: ante duda se conserva el reporte, nunca se elimina el que el
prompt vigente solicita devolver y, si un hecho permanente existe únicamente
allí, primero se traslada a su fuente responsable. Esta regla solo permite
actuar dentro de `.codex_reports/`; no requiere scripts, tareas programadas,
hooks, índices, manifiestos, copias de respaldo ni carpetas de archivo.

## Documentación viva del repositorio

El registro canónico `docs/DOCUMENTACION_VIVA.md` clasifica los documentos
vivos, especializados, generados y estáticos, e indica su fuente responsable y
sus disparadores de revisión. El registro orienta el cierre, pero no sustituye
la búsqueda contextual de documentación del componente afectado.

Cuando una decisión de Mateo y ChatGPT cambie la metodología, arquitectura,
fuente de verdad, estructura de datos, pipeline, flujo entre scripts, comandos
de regeneración, nomenclatura, reproducibilidad, tratamiento de muestreos,
estructura de salidas o reglas permanentes para Codex, el prompt debe considerar
explícitamente qué documentación versionada necesita actualizarse. El objetivo
es evitar que el código y el pipeline evolucionen mientras sus instrucciones
quedan obsoletas.

Antes de cerrar una tarea importante, ChatGPT debe identificar qué documentación
viva, especializada o generada resulta afectada; no basta con revisar siempre
los mismos documentos generales. Debe consultar el registro canónico, las
referencias inmediatas y la documentación específica del componente. Esta
revisión suele ser necesaria ante cambios
de metodología, arquitectura, fuentes de datos, pipeline, comandos, parámetros
activos, modelos o sistemas IPCC, integración estadística, tratamiento de
muestreos, convenciones, gobernanza, reglas para agentes o generación y
validación documental.

Cada contenido debe actualizarse en su fuente responsable. No se deben duplicar
decisiones metodológicas en documentos operativos ni reglas de coordinación en
el registro de decisiones científicas. Los manifiestos generados deben
regenerarse con su productor y corresponder a la misma corrida que los outputs.
Si un documento deja de cumplir una función diferenciada, ChatGPT debe proponer
su integración, sustitución, traslado o retiro; la decisión debe documentarse
antes de eliminarlo.

Git es la fuente ordinaria para recuperar revisiones históricas. Una auditoría
puntual debe retirarse de la rama vigente cuando sus hallazgos estén resueltos,
la información permanente ya resida en su fuente responsable y el archivo no
sea necesario para reproducibilidad. No se crea un archivo histórico paralelo
sin una necesidad operativa concreta.

## Revisión de cierre

Antes de recomendar otra tarea, chat, rama o sesión de Codex, ChatGPT debe
evaluar, en la medida aplicable al alcance real del trabajo:

- si el cambio solicitado fue implementado;
- si Codex produjo el reporte solicitado y ChatGPT lo revisó;
- si se inspeccionaron los archivos necesarios para validar el cambio;
- si se ejecutaron las validaciones pertinentes;
- si se regeneraron los productos afectados;
- si los documentos académicos afectados quedaron actualizados;
- si las decisiones metodológicas permanentes y las instrucciones para Codex permanecen actualizadas y coherentes;
- si los documentos vivos, especializados y generados afectados fueron revisados o actualizados conforme al registro canónico y al contexto del componente;
- si se conoce la rama, el commit `HEAD` y el estado del working tree;
- si una unidad coherente de cambios está lista y corresponde hacer commit, push o ambos;
- si el working tree quedó limpio o existe una razón documentada para mantener cambios.

La revisión es proporcional: una tarea trivial no exige recorrer pasos que no
le aplican. Una tarea importante no debe considerarse cerrada si el código, el
pipeline o la metodología cambiaron y la documentación que orienta a Codex
quedó obsoleta.

### Checkpoint de revisión y prompt operativo para Codex

Un prompt de implementación preparado por ChatGPT puede autorizar expresamente,
en una sola instrucción, implementar, verificar técnicamente, crear un checkpoint
de revisión, publicarlo y generar el reporte. No hace falta un segundo prompt de
commit y push antes de la primera revisión cuando esa autorización ya existe.
También puede emitirse después un prompt específico para commit, push o
integración, según el estado real.

El prompt autorizado solicita, en la medida aplicable:

- comprobar rama, `HEAD`, working tree, upstream y remoto;
- identificar los archivos de la unidad y detectar cambios accidentales o temporales;
- ejecutar las validaciones pertinentes;
- excluir `.codex_reports/` y otros artefactos temporales;
- añadir únicamente los archivos expresamente autorizados;
- crear el commit con el mensaje recomendado;
- publicar los commits y configurar upstream cuando resulte necesario;
- verificar los SHA local y remoto y el estado final;
- generar el reporte temporal en la ruta indicada.

El prompt específico preparado por ChatGPT constituye la autorización operativa
para las acciones Git que describe. Codex no puede ampliarla a otros archivos,
ramas u operaciones y no realiza commit, push, integración ni cambio de rama por
iniciativa propia. La autorización de checkpoint no autoriza integración a
`main` ni permite confundir la verificación de Codex con la validación de
ChatGPT. La recomendación no implica que toda tarea deba terminar inmediatamente
en un commit.

No es necesario hacer commit después de cada modificación pequeña. Un checkpoint
de revisión debe representar un estado coherente y técnicamente verificado;
antes de crearlo se ejecutan las comprobaciones pertinentes al alcance y se
confirma qué archivos integran realmente la unidad de trabajo.

El mensaje debe resumir el propósito real del cambio, corresponder al alcance
efectivamente verificado y permitir comprender la intención principal sin revisar
de inmediato el diff. Debe evitar mensajes genéricos como `update files`,
`changes`, `fix` o `misc updates`. Puede emplear prefijos breves como `docs:`,
`fix:`, `feat:`, `refactor:`, `test:` o `chore:` cuando resulten naturales, sin
convertir Conventional Commits en una obligación rígida.

Si el working tree contiene cambios conceptualmente independientes, ChatGPT
debe advertirlo, proponer una separación lógica y sugerir un mensaje distinto
para cada commit, en vez de ocultarlos bajo un único mensaje. Por ejemplo:

- `docs: clarify task closure and context transition workflow`
- `fix: correct validation of generated artifacts`

Los ejemplos son ilustrativos y no constituyen decisiones metodológicas
vigentes. Mateo ejecuta el prompt que autoriza el alcance concreto y Codex debe
respetar literalmente esos límites.

El ciclo de revisión aplica la estrategia de recuperación definida en el flujo
general y siempre somete el nuevo estado a otra revisión:

```text
checkpoint inicial → revisión de ChatGPT → estrategia autorizada
→ nuevo checkpoint → revisión del nuevo SHA
```

La historia ordinaria conserva los checkpoints y las acciones de recuperación;
no se reescribe para hacer parecer que el error nunca ocurrió.

## Criterios de transición

### Nuevo chat de ChatGPT

ChatGPT puede recomendar un nuevo chat cuando el objetivo anterior ya se cerró
y comienza una línea de trabajo diferente, cuando el contexto acumulado puede
dificultar el seguimiento o cuando una fase importante se beneficia de una
conversación limpia. No debe recomendarlo solo por la longitud del chat si el
objetivo sigue siendo el mismo y el contexto continúa siendo útil.

### Nueva rama Git

Antes de recomendar una nueva rama, ChatGPT debe determinar si ya existe una
rama activa de avance no integrada a `main`. Si no conoce el estado Git con
suficiente certeza, no debe asumir que `main` es la referencia vigente: debe
solicitar a Codex la comprobación mediante el contexto Git del repositorio.
Cambiar de chat no implica cambiar de rama; ambos son contextos independientes.

Si existe una rama activa de avance, ChatGPT debe evaluar primero si la nueva
unidad encaja naturalmente en su línea de trabajo. Cuando encaje, debe preferir
continuar en ella: una unidad nueva no implica una rama nueva. Cuando no encaje,
debe evaluar el cierre y la integración del avance existente o justificar una
excepción real antes de abrir una línea paralela. Si el objetivo de la rama ya
está terminado, debe revisar antes las validaciones, los commits y el push
pendientes y su integración a `main`. Mientras contenga trabajo abierto, debe
preferir mantener una sola rama activa, incluso si la nueva tarea se discute en
otro chat o pertenece a otra categoría científica, técnica o documental.

Solo debe recomendar una nueva rama después de comprobar que el avance anterior
se integró y que `main` volvió a ser la referencia vigente, o cuando exista una
razón excepcional y explícita que haga realmente necesario mantener
temporalmente más de una rama activa. El flujo ordinario no crea una rama por
unidad o categoría de trabajo. Antes del cambio debe aplicar la revisión de
cierre, comprobar documentación y validaciones, revisar el estado Git y
recomendar commit y push cuando corresponda. Codex nunca debe cambiar de rama
por iniciativa propia.

Si la rama checkout es histórica, ya cerrada, experimental, abandonada o
incompatible con la unidad, ChatGPT no debe confundirla con la rama activa de
avance. Antes de autorizar modificaciones debe determinar la referencia vigente
y decidir explícitamente si corresponde continuar, cambiar de rama o crear otra.
Codex inspecciona la discrepancia, la informa y ejecuta una transición únicamente
cuando el prompt la autoriza y delimita.

Para una tarea puramente diagnóstica o de inspección de solo lectura normalmente
no se crea ni se cambia de rama: Git permite consultar las referencias pertinentes
sin modificar el checkout. Si el diagnóstico concluye que hace falta implementar,
ChatGPT decide después el contexto de rama correspondiente. Esta separación evita
introducir complejidad Git antes de que exista una necesidad de escritura.

### Integración a `main`

`main` representa el estado integrado y estable del repositorio. Mientras un
trabajo viva únicamente en una rama, esa rama es su referencia vigente. Antes
de recomendar su integración, ChatGPT debe comprobar de forma proporcional al
alcance:

- que el working tree esté limpio;
- que la rama esté sincronizada con su remoto y los commits relevantes estén publicados;
- que se hayan superado las validaciones pertinentes, sin exigir el pipeline científico completo a cambios exclusivamente documentales o de gobernanza;
- que la documentación viva afectada sea coherente;
- que no haya archivos temporales versionados ni cambios accidentales fuera del propósito;
- que se conozcan las divergencias relevantes respecto de `main` y no se mezcle trabajo pendiente o no validado.

No se impone por defecto `merge`, `squash` ni `rebase + merge`. Mateo y ChatGPT
pueden escoger la forma apropiada según el historial y las herramientas
disponibles, siempre que la integración conserve una historia comprensible y
no incorpore trabajo no validado.

La existencia de checkpoints publicados no obliga a integrar inmediatamente la
rama. Se distinguen tres estados: el checkpoint de revisión puede publicarse
antes de la validación de ChatGPT; la unidad queda validada solo tras una revisión
supervisora satisfactoria; y la integración a `main` ocurre después de la revisión
de cierre, cuando el avance acumulado sea coherente, validado y apto para
integración.

Después de confirmar la integración, debe verificarse que `main` contiene los
cambios esperados; desde entonces, `main` vuelve a ser la referencia vigente
para el TFG. El siguiente avance relevante puede comenzar desde ese `main`
actualizado en otra rama. Las ramas anteriores pueden conservarse como respaldo
o referencia histórica y no necesitan eliminarse automáticamente, pero no se
interpretan como fuente vigente ni como líneas activas de trabajo.

### Nueva sesión de Codex

ChatGPT puede recomendar una nueva sesión de Codex cuando cambia de manera
importante el objetivo técnico o metodológico, cambia la rama, podrían
arrastrarse supuestos obsoletos, una fase nueva se beneficia de contexto limpio,
conviene separar diagnóstico de implementación o implementación de una auditoría
independiente, o comienza una tarea claramente independiente.

Debe preferir continuar en la sesión actual cuando la tarea es una continuación
directa, Codex acaba de inspeccionar los archivos pertinentes, el contexto sigue
siendo correcto y útil y no existe un riesgo significativo de conservar
supuestos obsoletos. Una nueva sesión no debe proponerse mecánicamente en cada
prompt.

## Recomendación de continuidad

Cuando ChatGPT determine que el objetivo principal se completó, debe comunicar
una recomendación explícita y basada en el estado real: continuar en el mismo
chat o abrir otro; mantener la rama o crear una nueva; continuar la sesión de
Codex o iniciar otra; y realizar commit o push antes de avanzar cuando
corresponda. Si recomienda commit o push, debe incluir el mensaje de commit
sugerido conforme a la regla anterior. La recomendación se formula después de
la revisión de cierre, no como una transición automática.

## Separación de responsabilidades documentales

Este documento se limita principalmente a la coordinación Mateo ↔ ChatGPT ↔
Codex, la preparación de prompts, los reportes y la revisión posterior. Las
referencias técnicas y metodológicas siguen siendo:

- `README.md`: estado y ejecución del pipeline;
- `AGENTS.md`: reglas obligatorias para agentes;
- `DECISIONES_METODOLOGICAS_TFG.md`: decisiones metodológicas aprobadas;
- documentación específica: reglas y explicaciones del componente correspondiente.

Cuando exista información relacionada, debe preferirse una referencia clara a
la fuente responsable en vez de duplicar grandes bloques entre documentos.
