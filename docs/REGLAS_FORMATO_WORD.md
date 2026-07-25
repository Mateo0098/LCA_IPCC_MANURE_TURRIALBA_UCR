# Reglas de formato para documentos Word generados

Estas reglas se aplican a:

- `outputs/documentos_tfg/metodologia_desarrollada_tfg.docx`
- `outputs/documentos_tfg/resultados_desarrollados_tfg.docx`

Los scripts generadores deben aplicarlas automáticamente. No se deben corregir manualmente los Word finales cuando el ajuste pueda implementarse en el generador.

## 1. Documento maestro protegido

El documento de referencia visual es:

`MASTER_escrito/TFG_ACV_Estiercol_MASTER.docx`

El MASTER se utiliza únicamente para identificar y reproducir fuente, tamaño, interlineado, espaciado, sangrías, alineación y estilos académicos. Nunca debe modificarse, sobrescribirse ni utilizarse como archivo de salida.

Los generadores deben verificar su hash antes y después de cualquier generación documental. Los archivos generados deben guardarse únicamente en `outputs/documentos_tfg/`.

## 2. Numeración independiente de documentos generados

Cada documento generado conserva su propia numeración interna de secciones, tablas, figuras y apéndices.

No se debe:

- continuar la numeración del MASTER;
- renumerar contenido para hacerlo coincidir con el MASTER;
- copiar la configuración de listas del MASTER como una obligación de continuidad;
- sincronizar tablas, figuras o apéndices con el documento maestro.

Correcto: metodología y resultados tienen secuencias internas coherentes e independientes.

Incorrecto: cambiar “Tabla 1” por “Tabla 14” únicamente porque el MASTER termina en la Tabla 13.

## 3. Títulos y subtítulos

Los títulos principales, subtítulos de todos los niveles, encabezados de apéndices y captions deben:

- seguir el estilo visual equivalente del MASTER;
- estar en color negro explícito;
- mantener fuente, tamaño, negrita, interlineado y espaciado coherentes;
- evitar estilos improvisados o heredados en color azul.

Incorrecto: un subtítulo con color azul por herencia de `Heading 2`.

Correcto: el mismo subtítulo con el formato académico del MASTER y color negro.

## 4. Tablas

El orden obligatorio es:

1. Prosa introductoria, si corresponde.
2. Un único título formal encima de la tabla.
3. Tabla.
4. Nota de tabla, solo cuando corresponda.

Cada tabla debe cumplir:

- un solo caption formal visible;
- caption encima de la tabla;
- encabezados académicos en español y en negrita;
- únicamente bordes horizontales, sin bordes verticales;
- texto y tamaño coherentes con las tablas del MASTER;
- valores numéricos alineados de forma consistente;
- ausencia de rutas, nombres de scripts, nombres de CSV y etiquetas internas.

Incorrecto:

```text
Tabla 3. Flujos del inventario.
Tabla 3. Flujos del inventario.
[tabla]
```

Correcto:

```text
En la Tabla 3 se resumen los flujos utilizados en el ICV.
Tabla 3. Flujos del inventario.
[tabla]
```

Incorrecto:

```text
Escenario | Etapa | Nombre etapa
```

Correcto:

```text
Escenario | Etapa del sistema
```

Las tablas académicas no deben mostrar `snake_case`, `dry_lot`, `n_ex_pct`, `n_ex_fraction`, `masa_total_kg_eq`, `processed`, `outputs`, `scripts`, `.csv` ni rutas internas.

## 5. Figuras

El orden obligatorio es:

1. Prosa introductoria, si corresponde.
2. Un único caption formal encima de la figura.
3. Imagen.
4. Nota o fuente, solo cuando corresponda.

Las imágenes deben conservar ejes, unidades, leyendas, valores y etiquetas necesarias, pero no deben contener un título interno generado por `plt.title()`, `ax.set_title()` o `fig.suptitle()`.

Incorrecto:

```text
Figura 4. Flujo de masa equivalente total por etapa.
[imagen que también contiene el título “Flujo de masa equivalente total por etapa”]
```

Correcto:

```text
Figura 4. Flujo de masa equivalente total por etapa.
[imagen sin título interno]
```

Cada figura debe tener exactamente un caption, situado encima de la imagen y sin duplicados.

## 6. Idioma

Todo texto visible debe estar en español académico, incluidos:

- prosa;
- encabezados y celdas de tablas;
- captions y notas;
- apéndices;
- ejes, leyendas y anotaciones de figuras.

Se permiten siglas aceptadas internacional o institucionalmente, como IPCC, ACV, ICV, EICV, CIA, LASA y UCR. También se conservan las fórmulas químicas y símbolos científicos.

Incorrecto: `Fresh manure`, `dry lot`, `global warming`.

Correcto: `Estiércol fresco`, `Sistema de manejo en corral seco`, `Calentamiento global`.

## 7. Unidades y símbolos

Las unidades anuales deben escribirse con `año`.

Incorrecto:

```text
L/ano
kg/ano
kg eq/ano
```

Correcto:

```text
L/año
kg/año
kg eq/año
kg CO₂-eq/año
kg PO₄-eq/año
```

Se deben conservar tildes, eñes, subíndices, superíndices y símbolos científicos correctos, como CH₄, N₂O, NH₃, NO₃⁻ y CO₂.

## 8. Nomenclatura de escenarios y etapas

Las denominaciones oficiales son:

- A1: Precomposteo
- A2: Lombricompostaje
- A3: Almacenamiento de aguas verdes
- A4: Aplicación de aguas verdes en campos de pastoreo
- B1: Almacenamiento de purines
- B2: Aplicación de purines en campo de pastoreo

No se deben mostrar etapas con decimales ni columnas redundantes.

En el Escenario A no debe aparecer `purín` ni `purines` asociado a flujos de A1, A2, A3 o A4.

En B1 y B2 no debe utilizarse `Aguas verdes` cuando el flujo corresponda a purín.

## 9. Relación entre prosa y apéndices

Cada apéndice interno debe mencionarse al menos una vez antes del bloque de apéndices, en la sección principal donde aporta información complementaria.

La mención debe:

- usar el código correcto;
- incluir el título real o una descripción clara del contenido;
- estar integrada naturalmente en la prosa;
- evitar referencias a apéndices inexistentes.

Incorrecto: “Ver apéndices.”

Correcto: “Los factores empleados en las estimaciones se detallan en el Apéndice interno B, Factores de emisión y caracterización.”

No se debe modificar la numeración de apéndices para hacerla coincidir con el MASTER.

## 10. Ecuaciones

Las ecuaciones deben:

- permanecer como texto LaTeX seleccionable;
- estar centradas;
- conservar su contenido matemático;
- evitar imágenes;
- evitar delimitadores visibles `\[` y `\]`;
- evitar delimitadores visibles `$$`.

Los cambios de formato nunca deben alterar factores, variables, operadores, valores ni resultados.

## 11. Validaciones obligatorias

Cuando se regeneren los documentos, `outputs/documentos_tfg/reporte_validacion_documentos.md` debe confirmar como mínimo:

- coincidencia visual de títulos, subtítulos y párrafos con el MASTER;
- color negro en títulos, subtítulos y captions;
- títulos de tablas y figuras encima;
- ausencia de captions duplicados;
- figuras sin títulos internos;
- español académico en Word, tablas y figuras;
- unidades anuales escritas con `año`;
- ausencia de etiquetas técnicas, rutas internas y `snake_case`;
- una sola columna `Etapa del sistema`;
- nomenclatura oficial de A1–A4 y B1–B2;
- uso correcto de aguas verdes y purines;
- relación completa entre prosa y apéndices;
- ecuaciones LaTeX seleccionables y sin imágenes;
- conservación de valores numéricos, cálculos y resultados;
- conservación del hash del MASTER antes y después de la generación;
- numeración interna independiente del MASTER.

Si una validación falla, se debe corregir primero el script generador y volver a ejecutar la validación. El documento MASTER no debe modificarse en ningún caso.
