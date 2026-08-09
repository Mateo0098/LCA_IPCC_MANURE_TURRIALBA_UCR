# Auditoría de regeneración de metodología y resultados (2026)

## 1. Archivos modificados

La tarea regeneró o actualizó los siguientes archivos:

- `scripts/generate_methodology_docx.py`.
- `scripts/generate_results_docx.py`.
- `outputs/documentos_tfg/metodologia_desarrollada_tfg.docx`.
- `outputs/documentos_tfg/resultados_desarrollados_tfg.docx`.
- `outputs/documentos_tfg/README_DOCUMENTOS_GENERADOS.md`.
- `outputs/documentos_tfg/reporte_validacion_documentos.md`.
- `outputs/documentos_tfg/reporte_correccion_factor_estequiometrico_NO3.md`, actualizado automáticamente por el generador de resultados con los flujos vigentes, sin recalcular el modelo.
- `auditoria_regeneracion_metodologia_resultados_2026.md`.

No se modificaron el documento maestro, las conclusiones desarrolladas, los datos crudos, los resultados procesados, las ecuaciones ni los factores del modelo.

## 2. Cambios introducidos en metodología

Se actualizó la redacción para representar el estado vigente del estudio: procedencia de los parámetros operativos, balance común de los escenarios, unidad funcional, carácter parcial de las observaciones experimentales disponibles y adaptación metodológica empleada para representar el nitrógeno potencialmente eutrofizante. El Escenario A quedó descrito como una secuencia en la que la fracción recolectada ingresa primero al precomposteo y la masa resultante continúa al lombricompostaje; la fracción remanente se incorpora a las aguas verdes. El Escenario B quedó descrito con el 100 % del estiércol teóricamente depositado incorporado al sistema de purines.

Los valores operativos y los flujos de referencia se leen desde las fuentes tabulares vigentes del repositorio. No se introdujeron valores nuevos en los cálculos del ACV.

## 3. Cambios introducidos en resultados

Se actualizó la interpretación textual y la tabla de síntesis para distinguir la magnitud operacional anual de los indicadores normalizados por la unidad funcional. Los totales, comparaciones y contribuciones dominantes se obtienen dinámicamente de las salidas procesadas vigentes.

También se precisó la interpretación de B1: la lixiviación explícita utilizada para estimar N₂O indirecto es cero y el NO₃⁻ incluido en la eutrofización procede del supuesto de especiación del nitrógeno potencialmente eutrofizante; por tanto, su presencia no constituye evidencia de lixiviación física directa.

## 4. Documentación de Sánchez-Romero y Brenes-Gamboa (2026)

La metodología identifica que el estudio de Sánchez-Romero y Brenes-Gamboa (2026) corresponde a la misma Lechería de la Sede del Atlántico de la Universidad de Costa Rica. Se incorporaron como parámetros operativos publicados el peso vivo promedio de 396,6 kg/animal, la población media de 18 vacas en ordeño, la permanencia aproximada de 3,5 h/día, la recolección de 2,7 kg de estiércol fresco por animal, el total recolectado de 17 525,1 kg/año y el uso de 686,5 L de agua de lavado por día, equivalente a 250 572,5 L/año.

Se aclaró que 17 525,1 kg/año corresponde al estiércol efectivamente recolectado durante las actividades de ordeño y no a la excreción fisiológica total diaria.

## 5. Documentación del cálculo del remanente

El intervalo bibliográfico de 7–10 % del peso vivo se distinguió de la decisión metodológica del TFG. El 7 % se documentó como el límite inferior adoptado conservadoramente para evitar sobreestimar una fracción no medida de forma directa.

La metodología presenta la reconstrucción:

- 396,6 × 0,07 = 27,762 kg/animal/día.
- 27,762 × (3,5/24) = 4,048625 kg/animal durante la permanencia en sala.
- 4,048625 − 2,7 = 1,348625 kg/animal remanentes.
- 1,348625 / 4,048625 = 0,333106919, equivalente a aproximadamente 33,31 %.

El 33,31 % se identifica expresamente como una estimación derivada mediante balance y no como una medición directa. La fracción recolectada corresponde aproximadamente a 66,69 %.

## 6. Unidad funcional

La unidad funcional quedó definida como **1 kg de estiércol fresco manejado**. El flujo anual común de referencia, aproximadamente 26 278,725181 kg/año, se presenta separadamente como la escala operacional empleada para construir el inventario. Los indicadores anuales y los normalizados se distinguen por sus unidades y función interpretativa.

## 7. Definición de Nᴳ, Nᴸ y Nₑᵤₜ

Se definió Nᴳ como el nitrógeno remanente de la ruta de volatilización después de descontar la fracción transformada en N₂O-N indirecto. Se definió Nᴸ como el nitrógeno remanente de la ruta de lixiviación después del descuento equivalente. El pool potencialmente contribuyente a eutrofización se expresó como:

`Nₑᵤₜ = Nᴳ + Nᴸ`.

La metodología distingue estas cantidades de las pérdidas iniciales de nitrógeno y del N₂O indirecto empleado en la categoría de calentamiento global.

## 8. Documentación del supuesto 50/50

La especiación se documentó como un supuesto metodológico del presente TFG aplicado después de integrar Nᴳ y Nᴸ:

- 50 % de Nₑᵤₜ se asigna a N asociado a NH₃.
- 50 % de Nₑᵤₜ se asigna a N asociado a NO₃⁻.

Después se aplican las conversiones estequiométricas de N a masa de NH₃ y NO₃⁻. No se presenta una correspondencia directa Nᴳ→NH₃ ni Nᴸ→NO₃⁻.

## 9. Uso de Komakech et al. (2016)

Komakech et al. (2016) se incorporó como antecedente del reparto 50/50 del nitrógeno del estiércol que alcanza cuerpos de agua entre nitrato y amoníaco. La redacción aclara que aplicar ese reparto al pool Nₑᵤₜ integrado constituye una adaptación del presente TFG y no una prescripción literal atribuida a dicho artículo.

La referencia bibliográfica utilizada fue la ya registrada en el proyecto: Komakech, A. J., Zurbrügg, C., Miito, G. J., Wanyama, J., y Vinnerås, B. (2016). *Environmental impact from vermicomposting of organic waste in Kampala, Uganda*. *Journal of Environmental Management, 181*, 395–402. https://doi.org/10.1016/j.jenvman.2016.06.028.

## 10. Texto para evitar interpretar el NO₃⁻ de B1 como lixiviación directa

En resultados se incorporó la precisión de que, en B1, la lixiviación explícita utilizada en la estimación del N₂O indirecto fue nula y que el NO₃⁻ equivalente se obtuvo bajo el supuesto de especiación del Nₑᵤₜ. Se indicó expresamente que este resultado no constituye evidencia de lixiviación física directa en esa etapa.

## 11. Principales valores numéricos regenerados

| Indicador | Escenario A | Escenario B |
|---|---:|---:|
| Calentamiento global anual (kg CO₂-eq/año) | 4 278,434080 | 9 087,048109 |
| Eutrofización anual (kg PO₄-eq/año) | 17,346687 | 20,197495 |
| Calentamiento global normalizado (kg CO₂-eq/kg de estiércol fresco) | 0,162809803 | 0,345794861 |
| Eutrofización normalizada (kg PO₄-eq/kg de estiércol fresco) | 0,000660104 | 0,000768587 |

La diferencia B−A fue 112,39 % para calentamiento global y 16,43 % para eutrofización. Las contribuciones dominantes verificadas fueron A3 (69,36 %) y B1 (98,03 %) para calentamiento global, y A1 (52,45 %) y B1 (70,55 %) para eutrofización.

## 12. Validaciones ejecutadas

- Compilación sintáctica satisfactoria de ambos generadores.
- Ejecución satisfactoria de ambos generadores.
- Apertura estructural satisfactoria de ambos archivos DOCX como paquetes ZIP y mediante `python-docx`.
- Verificación de 132 párrafos, 7 tablas y 1 figura en metodología.
- Verificación de 120 párrafos, 16 tablas y 15 figuras en resultados.
- Aplicación de la propiedad de no división a las 189 filas de tablas de metodología y a las 265 filas de tablas de resultados.
- Verificación automática de términos metodológicos, resultados normalizados, comparaciones y etapas dominantes en el reporte de validación.
- Verificación de nomenclatura académica, referencias a tablas y figuras, bordes horizontales, encabezados y ausencia de rutas internas en la prosa académica.
- Hash SHA-256 del documento maestro antes y después: `98ABDE3EC5A22FA052EFA595AAC26729EA070EACA670BDC41097C4BF2E5E327C`.
- Hash SHA-256 de las conclusiones antes y después: `B9532051838DF29FBD40830DAC0A94850D91F8449EC8564BA311813FFCCBCC84`.
- Confirmación por hash de que las principales salidas procesadas de emisiones e impactos no cambiaron.

La revisión visual automatizada mediante exportación con Microsoft Word no se completó por bloqueo de la aplicación. Los archivos sí fueron abiertos en modo de solo lectura y, tras cerrar esa instancia, se validaron íntegramente su estructura, contenido, tablas, figuras y propiedades de paginación sin modificar su contenido.
