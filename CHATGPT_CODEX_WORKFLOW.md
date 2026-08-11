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

Según la tarea, un reporte debería resumir:

- contexto Git obligatorio conforme a `AGENTS.md`;
- objetivo;
- archivos inspeccionados, modificados y creados;
- cambios implementados;
- comandos ejecutados;
- validaciones y sus resultados;
- documentación actualizada;
- advertencias y decisiones pendientes;
- estado final relevante del repositorio.

No es necesario conservar indiscriminadamente logs completos cuando un resumen
reproducible sea suficiente. Los hechos permanentes necesarios para ejecutar o
comprender el proyecto deben quedar en la documentación versionada apropiada,
no solamente en un reporte temporal.

## Documentación viva del repositorio

`README.md`, `AGENTS.md`, los documentos de decisiones metodológicas, la
documentación del pipeline y otras pautas equivalentes son documentos vivos:
describen el estado vigente y orientan el trabajo futuro de Codex.

Cuando una decisión de Mateo y ChatGPT cambie la metodología, arquitectura,
fuente de verdad, estructura de datos, pipeline, flujo entre scripts, comandos
de regeneración, nomenclatura, reproducibilidad, tratamiento de muestreos,
estructura de salidas o reglas permanentes para Codex, el prompt debe considerar
explícitamente qué documentación versionada necesita actualizarse. El objetivo
es evitar que el código y el pipeline evolucionen mientras sus instrucciones
quedan obsoletas.

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
