# Reglas de formato para documentos Word generados

Estas reglas se aplican a:

- `outputs/documentos_tfg/metodologia_desarrollada_tfg.docx`
- `outputs/documentos_tfg/resultados_desarrollados_tfg.docx`
- `outputs/documentos_tfg/conclusiones_desarrolladas_tfg.docx`
- `outputs/documentos_tfg/TFG_ACV_Estiercol_INTEGRAL_PROVISIONAL_M1_M2.docx`

Los scripts generadores deben aplicarlas automáticamente. No se deben corregir manualmente los Word finales cuando el ajuste pueda implementarse en el generador.

## 1. Documento maestro protegido

El documento de referencia visual es:

`MASTER_escrito/TFG_ACV_Estiercol_MASTER.docx`

El MASTER se utiliza únicamente para identificar y reproducir fuente, tamaño, interlineado, espaciado, sangrías, alineación y estilos académicos. Nunca debe modificarse, sobrescribirse ni utilizarse como archivo de salida.

Los generadores deben verificar su hash antes y después de cualquier generación documental. Los archivos generados deben guardarse únicamente en `outputs/documentos_tfg/`.

La portada del documento integral debe recuperar desde el MASTER los nombres y
cargos del comité asesor y fallar de forma explícita si deja de reconocerse la
estructura autorizada. Su distribución vertical debe resolverse mediante
espaciado de párrafo, estilos, secciones o estructuras sin bordes; no mediante
párrafos vacíos, cadenas de espacios ni duplicación manual de los nombres.

Los preliminares del integral deben contener, como mínimo, el estado del
documento, el contenido y la **Lista de siglas y abreviaturas**, en ese orden,
antes del cuerpo. Si se incorporan índices independientes de figuras o tablas,
la lista de siglas se ubica después de esos índices y antes de la introducción.

## 2. Numeración independiente de documentos generados

Cada documento generado conserva su propia numeración interna de secciones, tablas, figuras y apéndices.

No se debe:

- continuar la numeración del MASTER;
- renumerar contenido para hacerlo coincidir con el MASTER;
- copiar la configuración de listas del MASTER como una obligación de continuidad;
- sincronizar tablas, figuras o apéndices con el documento maestro.

Correcto: metodología y resultados tienen secuencias internas coherentes e independientes.

El documento integral constituye una unidad editorial propia: sus capítulos, tablas, figuras, ecuaciones y apéndices mantienen una única numeración global dentro de ese archivo. Los módulos parciales conservan su numeración independiente y no se insertan mediante concatenación binaria.

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

1. Prosa que introduce, menciona o contextualiza la tabla.
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

1. Prosa que introduce, menciona o contextualiza la figura.
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

Se prefiere terminología científica en español frente a anglicismos evitables.
En la prosa visible deben emplearse, según el contexto, expresiones como
`referencia de contraste`, `balance secuencial`, `reserva`, `valor por defecto`,
`secuencia de procesamiento`, `aproximación` y `aseguramiento de la calidad`,
en lugar de vocabulario inglés usado como sustantivo común. Esta regla no
traduce nombres propios, software, marcas, denominaciones oficiales ni títulos
bibliográficos.

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

Se deben conservar tildes, eñes, subíndices, superíndices y símbolos científicos correctos, como m², m³, CH₄, N₂O, NH₃, NO₃⁻, CO₂ y PO₄³⁻. La normalización se aplica al texto académico visible —prosa, tablas, captions, ejes, leyendas y anotaciones— y nunca mediante sustituciones globales sobre rutas, código, identificadores o datos fuente.

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

Cuando A y B designan las alternativas del ACV se escribe `escenario A`,
`escenario B` o `escenarios A y B`; `campaña` se reserva para campañas de
muestreo o actividades experimentales reales.

Los gráficos cuyo eje representa etapas usan únicamente A1–A4 y B1–B2. Los
nombres completos permanecen en la prosa, la tabla que define las etapas, los
captions cuando aportan contexto y la figura conceptual de fronteras.

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

## 10. Siglas y abreviaturas

Las siglas gobernadas por los documentos se mantienen en un único registro
controlado que conserva su desarrollo en español, denominación original cuando
corresponde, idioma de origen, forma de primera aparición e inclusión en la
lista. La lista del DOCX se deriva de ese registro y contiene solo entradas
realmente utilizadas; no se mantiene una lista manual paralela.

La primera aparición pertinente sigue la forma `nombre completo (SIGLA)`. La
expresión `(SIGLA, por sus siglas en inglés)` se reserva para siglas o acrónimos
realmente derivados de una denominación inglesa; TAN se presenta como
`nitrógeno amoniacal total (TAN, por sus siglas en inglés)`. No se aplica esa
fórmula de manera mecánica a toda denominación extranjera. Las formas
institucionales o universales, como ISO, se presentan conforme a su definición
oficial sin atribuirles una expansión inglesa; las denominaciones abreviadas
convencionales, como EMEP, siguen la fuente institucional y no reciben una
expansión artificial para hacer coincidir sus letras.

La validación comprueba automáticamente la primera aparición de todas las
entradas del registro que se utilizan en el cuerpo. También audita candidatos
no registrados de forma conservadora y exige clasificarlos, distinguiéndolos de
fórmulas químicas, unidades, variables, marcas, grados académicos, códigos de
normas y los códigos A1–A4, B1–B2 y M1–M3.

## 11. Ecuaciones

Las ecuaciones deben:

- aparecer como objetos matemáticos nativos de Word (OMML), seleccionables y editables;
- estar centradas;
- conservar su contenido matemático;
- evitar imágenes;
- ocultar por completo la sintaxis fuente LaTeX;
- alinear su número mediante tabulación o estructura estable, no mediante espacios manuales;
- estar precedidas por prosa que introduzca o defina la expresión, sin crear párrafos redundantes.

La conversión canónica es `LaTeX canónico → MathML → OMML` mediante la utilidad
compartida del repositorio. Los generadores no deben mantener implementaciones
paralelas de esa conversión.

Los cambios de formato nunca deben alterar factores, variables, operadores, valores ni resultados.

## 12. Validaciones obligatorias

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
- lista de siglas consistente con el registro controlado y primeras apariciones correctas;
- tratamiento explícito y terminológicamente preciso de siglas inglesas,
  abreviaturas institucionales, denominaciones convencionales y TAN;
- ausencia contextual de anglicismos evitables y notación científica plana;
- comité asesor presente y portada sin separadores manuales arbitrarios;
- prosa anterior a cada tabla, figura y ecuación formal;
- etiquetas A1–A4 y B1–B2 en gráficos por etapa;
- ecuaciones OMML seleccionables, editables, sin imágenes ni LaTeX visible;
- conservación de valores numéricos, cálculos y resultados;
- consistencia de dirección, signo, porcentaje, unidad, dominancia y redondeo en comparaciones narrativas;
- conservación del hash del MASTER antes y después de la generación;
- numeración interna independiente del MASTER.

Si una validación falla, se debe corregir primero el script generador y volver a ejecutar la validación. El documento MASTER no debe modificarse en ningún caso.
## 13. Consistencia cuantitativa de la prosa

Las afirmaciones comparativas visibles —mayor, menor, aumento, reducción y
escenario o etapa dominante— deben derivarse de la misma fuente canónica que sus
cifras. Las diferencias y porcentajes se recalculan y se valida su signo, unidad
y dirección. Si el redondeo visible iguala valores internamente distintos, debe
aumentarse la precisión o redactarse la comparación como indistinguible a esa
precisión; no se conserva una dirección aparentemente categórica.
