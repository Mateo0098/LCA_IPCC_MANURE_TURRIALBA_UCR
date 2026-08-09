# Auditoría de cierre documental de metodología (2026)

## 1. Cambios realizados

Se corrigió la definición textual de la unidad funcional en el documento de resultados y se reforzó su separación conceptual respecto al flujo anual común. En metodología se incorporó una distinción explícita entre las etapas de manejo del estiércol A3/B1 y las etapas subsecuentes de aplicación del efluente al suelo A4/B2. Las modificaciones se implementaron en los generadores y ambos documentos Word fueron regenerados.

También se creó `DECISIONES_METODOLOGICAS_TFG.md` como registro interno persistente de las decisiones validadas por el investigador.

## 2. Texto corregido de la unidad funcional

La unidad funcional quedó expresada inequívocamente como **1 kg de estiércol fresco manejado**. Se eliminó de resultados la formulación “tal y como fue recolectado del módulo lechero”.

El flujo anual común de aproximadamente 26 278,725181 kg de estiércol fresco/año se presenta separadamente como escala operacional utilizada para anualizar el inventario. Este flujo no redefine la unidad funcional.

## 3. Explicación final de A3/B1

A3: Almacenamiento de aguas verdes y B1: Almacenamiento de purines se documentaron como etapas en las que se aplican ecuaciones IPCC asociadas con el manejo del estiércol.

- En A3 se utiliza como masa de actividad el estiércol remanente sometido al sistema de manejo.
- En B1 se utiliza como masa de actividad la totalidad del estiércol teóricamente depositado.
- En ambas etapas se emplea la caracterización química del estiércol fresco y los factores correspondientes al sistema IPCC seleccionado.
- El agua de lavado presente físicamente en los sistemas no se suma como masa de estiércol en las ecuaciones de manejo.

Esta aclaración es documental y no alteró las masas utilizadas por el modelo.

## 4. Explicación final de A4/B2

A4: Aplicación de aguas verdes en campos de pastoreo y B2: Aplicación de purines en campo de pastoreo se documentaron como etapas subsecuentes de aplicación del efluente al suelo, representadas mediante las ecuaciones asociadas con suelos gestionados según la implementación vigente.

- A4 integra el agua de lavado y el estiércol remanente incorporado a las aguas verdes, con la caracterización química específica de las aguas verdes.
- B2 integra el agua de lavado y la totalidad del estiércol incorporado al purín, con la caracterización química específica del purín.

No se eliminó el agua de los flujos de aplicación A4/B2.

## 5. Creación de `DECISIONES_METODOLOGICAS_TFG.md`

El nuevo archivo registra de forma persistente:

- la unidad funcional y el flujo anual común;
- la fuente operativa Sánchez-Romero y Brenes-Gamboa (2026);
- el supuesto conservador de 7 % y el balance 66,69/33,31;
- el balance de masa entre escenarios;
- la distinción A3/B1 frente a A4/B2;
- las definiciones de `N_G`, `N_L` y `N_eut`;
- la adaptación 50/50 entre N asociado a NH₃ y N asociado a NO₃⁻;
- el alcance correcto del antecedente de Komakech et al. (2016);
- las reglas de interpretación ambiental, decisiones protegidas y estado provisional del muestreo.

## 6. Persistencia en los generadores

`scripts/generate_methodology_docx.py` contiene la definición inequívoca de la unidad funcional, la diferenciación entre las familias de ecuaciones de A3/B1 y A4/B2, las definiciones de Nᴳ, Nᴸ y Nₑᵤₜ, el reparto 50/50 y la presentación de Komakech et al. (2016) como antecedente de una adaptación propia del TFG.

`scripts/generate_results_docx.py` genera la definición corregida de la unidad funcional e incluye validaciones que detectan la formulación “tal y como fue recolectado”, la ausencia de “1 kg de estiércol fresco manejado”, una interpretación incorrecta del NO₃⁻ de B1 y la pérdida de la distinción sobre el agua de lavado en A3/B1.

Los Word regenerados no dependen de correcciones manuales posteriores.

## 7. Confirmación de que ningún cálculo cambió

No se modificaron ecuaciones del ACV, factores, sistemas IPCC seleccionados, datos crudos o procesados, resultados numéricos, flujos, tablas fuente, gráficos ni parámetros de laboratorio.

Los hashes SHA-256 de las principales salidas procesadas permanecieron iguales antes y después:

| Archivo | SHA-256 |
|---|---|
| `processed/ACV_resumen_emisiones.csv` | `A904EDF4F77D21F99D3683E24A91FD475B702CE711D4100A2E6643B80B2C0C8B` |
| `processed/acv_impacto_por_etapa_escenario.csv` | `CE164CD555B230CF96BDBE6DAB084D6D0C48027B0AB1B79760E93FC444186181` |
| `processed/acv_impacto_total_por_escenario.csv` | `7040A111CC5AE067C9510A83262D653BB96CD4F305994086821316EF147E038B` |
| `processed/masa_total_escenario_etapa.csv` | `FA243E995D1F013D521371A59AB2404D35BC0C7A410F2780DC0E8E61CD6B2596` |

El master conservó el hash `98ABDE3EC5A22FA052EFA595AAC26729EA070EACA670BDC41097C4BF2E5E327C`. El documento de conclusiones conservó el hash `B9532051838DF29FBD40830DAC0A94850D91F8449EC8564BA311813FFCCBCC84`.

## 8. Archivos modificados

Archivos modificados o creados durante la fase documental acumulada pendiente de commit:

- `.gitignore`.
- `scripts/generate_methodology_docx.py`.
- `scripts/generate_results_docx.py`.
- `outputs/documentos_tfg/metodologia_desarrollada_tfg.docx`.
- `outputs/documentos_tfg/resultados_desarrollados_tfg.docx`.
- `outputs/documentos_tfg/README_DOCUMENTOS_GENERADOS.md`.
- `outputs/documentos_tfg/reporte_validacion_documentos.md`.
- `outputs/documentos_tfg/reporte_correccion_factor_estequiometrico_NO3.md`.
- `DECISIONES_METODOLOGICAS_TFG.md`.
- `auditoria_regeneracion_metodologia_resultados_2026.md`.
- `auditoria_cierre_documental_metodologia_2026.md`.

`auditoria_eutrofizacion_B1.md` y el archivo temporal de bloqueo de Excel ya figuraban como no rastreados antes de esta corrección final; no fueron modificados en ella. Se añadió la regla `~$*.xlsx` al `.gitignore` para impedir que los archivos temporales de Microsoft Office se incluyan accidentalmente en futuras instrucciones de commit.

## 9. Validaciones y estado de Git

- Ambos generadores superaron la compilación sintáctica y se ejecutaron correctamente.
- Los dos DOCX superaron la comprobación de integridad de su estructura ZIP y la apertura mediante `python-docx`.
- Se confirmó la presencia de la unidad funcional corregida y la ausencia de la formulación anterior.
- Se confirmó la presencia de la explicación A3/B1, A4/B2, Nₑᵤₜ y Komakech et al. (2016).
- El reporte automático no presentó verificaciones fallidas; la línea “Se recalcularon los resultados relacionados con NO₃⁻: No” es una confirmación, no una alerta.
- No se realizó commit ni push.

Estado de Git al cerrar la tarea:

```text
 M .gitignore
 M outputs/documentos_tfg/README_DOCUMENTOS_GENERADOS.md
 M outputs/documentos_tfg/metodologia_desarrollada_tfg.docx
 M outputs/documentos_tfg/reporte_correccion_factor_estequiometrico_NO3.md
 M outputs/documentos_tfg/reporte_validacion_documentos.md
 M outputs/documentos_tfg/resultados_desarrollados_tfg.docx
 M scripts/generate_methodology_docx.py
 M scripts/generate_results_docx.py
?? DECISIONES_METODOLOGICAS_TFG.md
?? auditoria_cierre_documental_metodologia_2026.md
?? auditoria_eutrofizacion_B1.md
?? auditoria_regeneracion_metodologia_resultados_2026.md
```

## 10. Corrección de la presentación del marco de cálculo en A4/B2

### Causa de la etiqueta

La etiqueta “Laguna anaerobia descubierta” aparecía en A4 y B2 porque la tabla documental leía directamente el campo de sistema IPCC almacenado en la tabla de parámetros. Ese campo se conserva en las etapas de aplicación como referencia al sistema de manejo u origen previo del efluente. Al titular la columna únicamente “Sistema de manejo”, la presentación podía interpretarse erróneamente como si definiera la familia de ecuaciones aplicada en A4/B2.

### Corrección documental

No se cambió el campo fuente. En los generadores, la columna se presenta ahora como **Sistema de manejo u origen previo** y se añadió **Marco de cálculo de la etapa**. La nueva columna clasifica:

- A3 y B1 como **Manejo del estiércol**.
- A4 y B2 como **Suelos gestionados**.
- A2 como **Factores experimentales publicados**.

Así, “Laguna anaerobia descubierta” permanece visible cuando aporta trazabilidad sobre el origen previo, pero ya no se presenta como el marco de cálculo de las etapas de aplicación.

### Confirmación de integridad numérica

La corrección se aplicó únicamente al DataFrame de presentación construido en memoria por los generadores. No se modificó `tabla_04_parametros_modelo_acv.csv`, ninguna salida procesada, ningún parámetro, factor, flujo, ecuación ni resultado. Los cuatro hashes de control consignados en la sección 7 permanecieron idénticos después de regenerar.

### Estado final

El estado reproducido en la sección 9 incorpora `.gitignore` y ya no muestra el archivo temporal `~$*.xlsx`, porque ahora queda ignorado. No se realizó commit ni push.
