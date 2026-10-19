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

La normalización automática no debe sustituir palabras aisladas en prosa libre
cuando el cambio pueda alterar género, número, artículos, preposiciones o la
estructura sintáctica. Las frases controladas por los generadores se redactan
directamente en español correcto; el normalizador léxico se reserva para
etiquetas y expresiones completas cuya sustitución sea gramaticalmente segura.

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

Se deben conservar tildes, eñes, subíndices, superíndices y símbolos científicos correctos, como m², m³, CH₄, N₂O, NH₃, NO₃⁻, CO₂ y PO₄³⁻. Entre una magnitud y su unidad se deja un espacio (`15 m²`, no `15m2`). Las potencias de diez visibles usan exponentes compuestos (`1,18 × 10⁻⁸`, no `1,18 × 10-8`). La normalización se aplica al texto académico visible —prosa, tablas, captions, ejes, leyendas y anotaciones— y nunca mediante sustituciones globales sobre rutas, código, identificadores o datos fuente.

### 7.1 Precisión numérica científica

Esta política se aplica a toda cifra cuantitativa visible en el manuscrito —prosa,
tablas, notas, apéndices, ecuaciones, captions, ejes, escalas, etiquetas, leyendas y
anotaciones— salvo una excepción explícita y justificada. Los datos canónicos y las
operaciones intermedias conservan siempre su precisión completa; el redondeo ocurre
únicamente en la capa de presentación mediante la utilidad compartida
`scripts/scientific_numeric_presentation.py`.

La selección del formato es contextual:

- **Mediciones directas:** se respeta la resolución declarada por el laboratorio o
  instrumento. Los dígitos almacenados por un equipo no se presentan como precisión
  analítica adicional. Si solo existe una convención prudente de presentación, se
  declara como tal y no como incertidumbre.
- **Promedios y dispersión:** cuando se muestra una desviación estándar u otra
  incertidumbre disponible, esta se identifica por su nombre, se limita normalmente
  a una o dos cifras significativas y el estimador se redondea a la misma posición
  decimal. Una desviación entre campañas no se denomina incertidumbre expandida.
- **Resultados sin incertidumbre formal:** se usan normalmente cuatro cifras
  significativas para resultados derivados del inventario y del ACV, o menos cuando
  la resolución de las entradas lo exige. Esta es una convención editorial prudente,
  no una evaluación metrológica.
- **Fuentes bibliográficas:** una reproducción literal conserva la precisión y la
  notación de la fuente, salvo normalización inequívoca del separador decimal o de la
  potencia de diez. Un valor derivado de la fuente se identifica como cálculo y se
  presenta con precisión compatible con sus entradas.
- **Factores de emisión y caracterización:** se conservan los dígitos publicados o
  aprobados. Esos dígitos no se interpretan por sí solos como incertidumbre conocida.
  Los productos calculados con ellos siguen la regla de resultados derivados.
- **Parámetros operativos estimados:** se presentan conforme a la resolución de la
  observación o supuesto que los origina; no se añaden ceros decimales para aparentar
  exactitud.
- **Porcentajes, relaciones y diferencias:** se calculan desde valores internos sin
  redondear. Por regla general, los porcentajes comparativos se muestran con un
  decimal; se aumenta la precisión solo si resulta necesaria para conservar una
  diferencia científicamente relevante. Las diferencias absolutas conservan una
  precisión coherente con las magnitudes comparadas.
- **Valores pequeños, grandes y próximos a cero:** un valor físico no nulo nunca se
  vuelve `0` por redondeo. Se usa notación científica, en particular por debajo de
  `10⁻³` cuando mejora la lectura, y también para magnitudes muy grandes cuando evita
  cadenas de dígitos poco legibles. El signo se conserva y se elimina el cero negativo.
- **Números exactos:** conteos, años, fechas, códigos A1–B2 y M1–M3, números de tabla,
  figura o ecuación, referencias y constantes definidas no se someten al formato de
  mediciones. Las constantes y factores exactos deben estar identificados como tales.

Los totales se calculan con precisión completa. Se admite que la suma manual de
componentes ya redondeados difiera mínimamente del total visible; la nota editorial
debe aclararlo cuando pueda inducir a error, sin forzar ni redistribuir el resultado.
Las comparaciones deben conservar dirección y signo después del redondeo; si dos
valores quedan visualmente iguales, se aumenta la precisión o se declara que son
indistinguibles a la precisión presentada. Nunca se inventan desviaciones estándar,
intervalos de confianza, incertidumbres ni significancia estadística.

La implementación usa redondeo decimal al valor más próximo y, en empates exactos,
al dígito par. Este criterio y la separación entre cálculo y presentación se basan en:

- Joint Committee for Guides in Metrology. (2008). *JCGM 100:2008, Evaluation of
  measurement data—Guide to the expression of uncertainty in measurement*, apartado
  7.2.6: evita dígitos excesivos, presenta normalmente la incertidumbre con hasta dos
  cifras significativas y alinea la posición decimal del estimador. Fuente oficial:
  https://www.bipm.org/documents/20126/2071204/JCGM_100_2008_E.pdf
- National Institute of Standards and Technology. (2008). *NIST Special Publication
  811, Guide for the Use of the International System of Units (SI)*, apartados 7.1–7.10,
  10.5 y B.7.1–B.7.2: separación entre valor numérico y unidad, agrupación de dígitos,
  reglas de redondeo y conservación razonable de la precisión al convertir. Fuente
  oficial: https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication811e2008.pdf
- Taylor, B. N., & Kuyatt, C. E. (1994). *NIST Technical Note 1297, Guidelines for
  Evaluating and Expressing the Uncertainty of NIST Measurement Results*, apartado 7:
  una afirmación de incertidumbre debe identificar sus componentes, el procedimiento
  y, cuando corresponda, el factor de cobertura. Fuente oficial:
  https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-7-reporting-uncertainty

Estas referencias no imponen dos o tres cifras significativas a todo resultado ni
permiten inferir incertidumbre a partir del número de decimales impreso.

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

Las matrices de apéndice cuya amplitud impida una lectura normal deben resolverse
en el mismo documento mediante orientación horizontal por secciones y, cuando sea
necesario, mediante vistas temáticas enlazadas por una clave estable. Los
encabezados se repiten en cada página y el cuerpo no se reduce por debajo de 9 pt.
La división editorial debe conservar todas las filas y relaciones de la fuente
canónica; al terminar el apéndice se restablece la orientación que corresponda al
contenido siguiente.

Las notas de tabla deben distinguir expresamente, cuando exista riesgo de
confusión, entre cero cuantitativo, exclusión por frontera metodológica, valor no
aplicable y ausencia de información. Una nota explicativa no autoriza a cambiar
el inventario ni a incorporar flujos nuevos.

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
- estar precedidas por prosa breve que explique el propósito de la relación;
- estar seguidas, cuando introduzcan símbolos o unidades, por un párrafo
  `Donde:` que presente los símbolos con notación matemática nativa y defina su
  significado físico y sus unidades;
- distinguir el texto introductorio de las definiciones posteriores, sin crear
  glosarios repetitivos ni trasladar nombres internos del código a la prosa;
- mantener como matemática nativa los subíndices, superíndices, barras,
  sombreros e índices de los símbolos también cuando aparezcan en las
  definiciones; no representar esas variables mediante guiones bajos visibles.

La conversión canónica es `LaTeX canónico → MathML → OMML` mediante la utilidad
compartida del repositorio. Los generadores no deben mantener implementaciones
paralelas de esa conversión.

Las relaciones consecutivas pueden compartir definiciones cuando la proximidad
haga inequívoca la notación. Las unidades deben permitir comprobar la
coherencia dimensional y distinguir porcentajes de fracciones adimensionales,
kg de N de kg de una especie molecular y masas físicas de unidades equivalentes
de impacto. Los símbolos matemáticos insertados dentro de un párrafo también
son OMML, pero no se contabilizan como ecuaciones formales ni alteran su
numeración global.

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
- prosa introductoria antes de cada ecuación formal y definiciones posteriores
  de símbolos y unidades con notación OMML cuando correspondan;
- conteo de las ecuaciones formales separado de los símbolos matemáticos OMML
  insertados dentro de los párrafos de definición;
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
