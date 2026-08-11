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
o continúa trabajo anterior y, si ya existe, señalar el commit que la cierra.
Esta información facilita la revisión, pero sigue siendo temporal.

Una vez validada y autorizada la unidad, uno o varios commits coherentes se
convierten en sus checkpoints históricos permanentes. Sus mensajes deben
expresar el propósito real del cambio; Git conserva la evolución sin necesidad
de ledgers, inventarios manuales de commits, copias de conversaciones ni
registros de sesiones. Si la unidad todavía no se ha consolidado en un commit,
permanece explícitamente abierta como trabajo pendiente en la rama y no debe
presentarse como cerrada.

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
Mateo + ChatGPT → prompt para Codex → ejecución por Codex → reporte Markdown
→ revisión por ChatGPT → solicitud selectiva de archivos → validación
```

1. Mateo y ChatGPT discuten primero la decisión o el cambio.
2. ChatGPT prepara un prompt concreto para Codex.
3. Mateo ejecuta ese prompt en Codex.
4. Codex realiza el trabajo autorizado y crea el reporte solicitado en `.codex_reports/`.
5. Mateo entrega ese archivo a ChatGPT en lugar de copiar largas salidas de terminal o de Codex al chat.
6. ChatGPT analiza primero el reporte.
7. A partir del reporte, ChatGPT solicita únicamente los archivos concretos que necesite inspeccionar para validar el trabajo.
8. La afirmación de Codex de que una tarea terminó correctamente no sustituye la revisión posterior cuando esta sea necesaria.
9. ChatGPT aplica la revisión de cierre y recomienda explícitamente cómo continuar.

### Contexto de rama

Cada reporte de Codex debe incluir el contexto Git obligatorio definido en
`AGENTS.md`: rama, commit `HEAD` y estado general del working tree al inicio y
al final, además de cualquier cambio de rama y su causa. Al recibir el reporte,
ChatGPT debe considerar la rama allí indicada como la referencia vigente para
las consultas, prompts y validaciones relacionadas con esa tarea.

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

### Recomendación de commit y mensaje

Cuando la revisión de cierre determine que corresponde realizar un commit, un
push o ambos, ChatGPT debe proponer también un mensaje de commit descriptivo y
coherente con el conjunto de cambios que se consolidará. La recomendación no
implica que toda tarea deba terminar inmediatamente en un commit.

No es necesario hacer commit después de cada modificación pequeña. Un commit
debe representar un checkpoint coherente y suficientemente validado; antes de
crearlo se ejecutan las validaciones pertinentes al alcance y se confirma qué
archivos integran realmente la unidad de trabajo.

El mensaje debe resumir el propósito real del cambio, corresponder al alcance
efectivamente validado y permitir comprender la intención principal sin revisar
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
vigentes. ChatGPT propone los mensajes como parte de la supervisión; Mateo
autoriza el commit y Codex solo utiliza el mensaje cuando recibe esa instrucción
explícita. Se mantiene la prohibición de que Codex haga commits automáticamente.

## Criterios de transición

### Nuevo chat de ChatGPT

ChatGPT puede recomendar un nuevo chat cuando el objetivo anterior ya se cerró
y comienza una línea de trabajo diferente, cuando el contexto acumulado puede
dificultar el seguimiento o cuando una fase importante se beneficia de una
conversación limpia. No debe recomendarlo solo por la longitud del chat si el
objetivo sigue siendo el mismo y el contexto continúa siendo útil.

### Nueva rama Git

ChatGPT puede recomendar una nueva rama de avance después de que el trabajo
anterior se haya integrado a `main`, o excepcionalmente cuando una necesidad
real justifique aislar cambios. Por defecto no mantiene varias ramas activas en
paralelo ni crea una rama por unidad o categoría de trabajo.

Antes del cambio debe aplicar la revisión de cierre, comprobar documentación y
validaciones, revisar el estado Git y recomendar commit y push cuando
corresponda. Codex nunca debe cambiar de rama por iniciativa propia.

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
