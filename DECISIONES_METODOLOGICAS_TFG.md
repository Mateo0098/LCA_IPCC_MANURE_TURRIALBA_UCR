# Decisiones metodológicas del TFG

## 1. Propósito del documento

Este documento interno registra decisiones metodológicas validadas por el investigador para el TFG sobre el análisis de ciclo de vida del manejo de estiércol bovino en la lechería de la Sede del Atlántico de la Universidad de Costa Rica. Estas decisiones deben conservarse en futuras regeneraciones documentales y ejecuciones del modelo, salvo que el investigador autorice expresamente una modificación posterior. Este archivo no sustituye la metodología académica de la tesis.

## 2. Unidad funcional

- La unidad funcional es **1 kg de estiércol fresco manejado**.
- El flujo anual común de referencia es aproximadamente 26 278,725181 kg de estiércol fresco/año.
- El flujo anual representa la escala operacional utilizada para anualizar el inventario; no redefine la unidad funcional.
- No debe describirse la unidad funcional como estiércol únicamente recolectado ni como 1 kg/año.

## 3. Fuente operativa Sánchez-Romero y Brenes-Gamboa (2026)

Sánchez-Romero y Brenes-Gamboa (2026) estudiaron la misma lechería de la Sede del Atlántico de la Universidad de Costa Rica evaluada en este TFG. Los parámetros operativos publicados utilizados son:

- peso vivo promedio: 396,6 kg/animal;
- población media: 18 vacas en ordeño;
- permanencia aproximada en sala: 3,5 h/día;
- estiércol fresco recolectado: 2,7 kg/animal;
- estiércol fresco recolectado total: 17 525,1 kg/año;
- agua de lavado: 686,5 L/día, equivalente a 250 572,5 L/año.

Los 17 525,1 kg/año representan el estiércol efectivamente recolectado durante las actividades de ordeño, no la excreción fisiológica total diaria.

## 4. Supuesto de generación de estiércol

El artículo citado refiere bibliográficamente un intervalo de producción diaria de estiércol equivalente al 7–10 % del peso vivo. El presente TFG adoptó el límite inferior de 7 % como supuesto conservador para evitar sobreestimar una fracción no medida directamente.

El balance derivado produjo aproximadamente 33,31 % de estiércol remanente y 66,69 % de estiércol recolectado. Estas fracciones no son mediciones directas realizadas por Sánchez-Romero y Brenes-Gamboa (2026); son estimaciones metodológicas del TFG.

## 5. Balance entre escenarios

En el Escenario A:

- 17 525,1 kg/año ingresan primero a A1: Precomposteo;
- la masa resultante de A1 continúa posteriormente hacia A2: Lombricompostaje;
- 8 753,625181 kg/año constituyen el remanente estimado incorporado a las aguas verdes;
- la suma corresponde al flujo común de 26 278,725181 kg/año.

En el Escenario B, el 100 % del flujo común de 26 278,725181 kg/año ingresa a B1: Almacenamiento de purines. Ambos escenarios representan alternativas para el mismo flujo anual de referencia.

## 6. Representación A3/B1 frente a A4/B2

### A3 y B1: manejo del estiércol

A3: Almacenamiento de aguas verdes y B1: Almacenamiento de purines utilizan las ecuaciones IPCC asociadas con el manejo del estiércol.

- En A3, la masa de actividad es la masa de estiércol remanente sometida al sistema de manejo.
- En B1, la masa de actividad es la totalidad del estiércol teóricamente depositado.
- En ambas etapas se utiliza la caracterización química del estiércol fresco y los factores del sistema IPCC seleccionado.
- El agua de lavado se excluye de la masa de actividad de estas ecuaciones.

El agua existe físicamente en los sistemas de almacenamiento. Su exclusión significa únicamente que no se introduce como masa de estiércol en las ecuaciones IPCC de manejo.

### A4 y B2: aplicación del efluente al suelo

A4: Aplicación de aguas verdes en campos de pastoreo y B2: Aplicación de purines en campo de pastoreo son etapas subsecuentes de aplicación del efluente al suelo y utilizan las ecuaciones asociadas con suelos gestionados según la implementación vigente.

- En A4, el flujo aplicado integra el agua de lavado y el estiércol remanente incorporado a las aguas verdes; se utiliza la caracterización química específica de las aguas verdes.
- En B2, el flujo aplicado integra el agua de lavado y la totalidad del estiércol incorporado al purín; se utiliza la caracterización química específica del purín.

## 7. Adaptación para eutrofización

Las cantidades de nitrógeno se definen de la siguiente manera:

- `N_G`: N remanente de la ruta de volatilización después de descontar el N₂O-N indirecto.
- `N_L`: N remanente de la ruta de lixiviación después de descontar el N₂O-N indirecto.
- `N_eut = N_G + N_L`: pool de N remanente considerado potencialmente contribuyente a eutrofización.

El supuesto metodológico del TFG asigna:

- 50 % de `N_eut` a N asociado a NH₃;
- 50 % de `N_eut` a N asociado a NO₃⁻.

Después de esta asignación se aplican las conversiones estequiométricas de N a masa de NH₃ y NO₃⁻.

## 8. Uso de Komakech et al. (2016)

Komakech et al. (2016) constituye el antecedente del reparto 50/50. El texto de dicho estudio se refiere al N del estiércol que alcanza cuerpos de agua y asume su transformación en 50 % nitrato y 50 % amoníaco.

La aplicación de ese reparto al pool integrado `N_eut` es una adaptación metodológica propia del presente TFG. No debe atribuirse a Komakech et al. la ecuación completa utilizada en este proyecto, ni debe atribuirse al IPCC la adaptación para eutrofización.

## 9. Interpretación ambiental del supuesto de eutrofización

- El enfoque considera conservadoramente el N remanente como potencialmente contribuyente a eutrofización.
- No implica que el 100 % del N volatilizado alcance físicamente cuerpos de agua.
- NH₃ y NO₃⁻ son representaciones utilizadas para caracterizar el pool `N_eut` dentro del ACV; no constituyen una predicción directa de la especiación química final en el ambiente.
- La presencia de NO₃⁻ en B1 no implica lixiviación física cuando `N_L = 0`, porque el NO₃⁻ equivalente procede del supuesto de reparto de `N_eut`.

## 10. Decisiones que no deben cambiarse automáticamente

No deben cambiarse automáticamente:

- los sistemas IPCC seleccionados;
- los factores IPCC y de caracterización;
- el tratamiento del CO₂ del lombricompostaje;
- la unidad funcional;
- el supuesto de 7 %;
- el balance 66,69/33,31;
- la adaptación basada en `N_eut`;
- el reparto 50/50 entre N asociado a NH₃ y N asociado a NO₃⁻.

Estas decisiones solo deben modificarse por decisión expresa del investigador o como resultado de una revisión académica posterior autorizada.

## 11. Estado provisional

Actualmente, parte de los resultados experimentales incorporados procede principalmente del primer muestreo. Las jornadas siguientes deberán integrarse estadísticamente cuando estén disponibles, y los documentos deberán regenerarse conservando las decisiones metodológicas aquí registradas.

## 12. Regla para futuras regeneraciones

Los generadores de metodología y resultados deben conservar estas decisiones. Si se detecta una discrepancia entre los documentos generados, la implementación del modelo y este archivo, debe reportarse al investigador antes de modificar cálculos, parámetros, factores, flujos o decisiones metodológicas.

## 13. Aclaraciones CIA sobre reporte de N y preparación de N/C

### Política de precisión y redondeo

- Para N de aguas verdes y purines, el CIA aclaró que reporta el resultado hasta el segundo decimal, tal como aparece en el informe.
- Los decimales adicionales almacenados en las celdas corresponden a la lectura que conserva el equipo. Deben mantenerse en la ingestión y en los cálculos para evitar redondeo prematuro y asegurar reproducibilidad.
- El redondeo se aplica únicamente en la presentación final, respetando la precisión de reporte del laboratorio.
- Los decimales adicionales no deben interpretarse ni describirse como mayor precisión analítica formal.
- No deben sustituirse por `0,01 %` valores internos diferentes que el informe muestre redondeados de la misma forma.

### N y C del estiércol precompostado

- El CIA determinó N y C por Dumas (combustión seca) después de secar la muestra a 80 °C durante 48 h y realizar la preparación establecida por su metodología.
- El CIA no determinó humedad a 105 °C como parte de ese análisis porque no fue solicitada.
- La humedad y materia seca del TFG proceden de ensayos gravimétricos independientes, con aproximadamente 10 g a 105 °C hasta masa constante o durante el tiempo establecido.
- El secado CIA a 80 °C es una condición de preparación para N/C; no debe mezclarse con la determinación gravimétrica del TFG a 105 °C.
- No se debe etiquetar el N/C del precompostado como base fresca ni afirmar automáticamente base seca. La base formal del porcentaje no está especificada explícitamente en los reportes.
- No deben realizarse conversiones automáticas de N usando la materia seca determinada a 105 °C sin evidencia documental y aprobación metodológica expresa.
