# Evidencia de sesión SimaPro — 2026-10-07

## Alcance

Esta carpeta conserva evidencia primaria de la sesión presencial de QA/QC Python–SimaPro realizada para contrastar la caracterización Environmental Footprint 3.1 de la corrida **PROVISIONAL M1–M2**.

No modifica ni sustituye los resultados canónicos del pipeline Python y no implica todavía incorporar esta verificación al documento escrito final del TFG.

## Entorno verificado

- SimaPro Faculty / Educational, versión 10.4.0.0, instalación UCR 004.
- Proyecto local de trabajo: `MATEO_TFG_TESTING`.
- Método utilizado: `Environmental Footprint 3.1 (adapted)`, V1.05.
- La biblioteca ecoinvent instalada fue identificada durante la sesión, pero no se utilizó para reconstruir fondos ni para sustituir los factores operacionales canónicos del TFG.

## Verificación directa de factores

Se inspeccionaron directamente en la tabla de caracterización de SimaPro las nueve combinaciones activas relevantes para el contraste:

- CH4 biogénico: 27 kg CO2-eq/kg.
- N2O: 273 kg CO2-eq/kg.
- NH3, eutrofización terrestre: 13.47 mol N-eq/kg.
- NH3, eutrofización marina: 0.092 kg N-eq/kg.
- NOx, eutrofización terrestre: 4.26 mol N-eq/kg.
- NOx, eutrofización marina: 0.389 kg N-eq/kg.
- NO3-, eutrofización marina: 0.226 kg N-eq/kg.
- CO2 fósil: 1 kg CO2-eq/kg.
- CH4 fósil: 29.8 kg CO2-eq/kg.

Las capturas `04` a `10`, incluida la captura complementaria `07b`, conservan la evidencia visual de los factores y de las identidades de flujo utilizadas. `07_factor_nh3_marino_0.092.png` muestra directamente el factor marino de NH3 (0.092); `07b_factor_nh3_terrestre_13.47.png` muestra directamente el factor terrestre (13.47); y `13_unitario_nh3_1kg_resultado.png` documenta el resultado unitario terrestre presentado por SimaPro como 13.5 debido al redondeo de pantalla.

## Casos unitarios ejecutados de extremo a extremo

Se ejecutaron cinco procesos unitarios de 1 kg en SimaPro:

- `QA_EF31_N2O_1kg`: cambio climático = 273 kg CO2-eq.
- `QA_EF31_CH4BIO_1kg`: cambio climático = 27 kg CO2-eq.
- `QA_EF31_NH3_1kg`: eutrofización marina = 0.092 kg N-eq; eutrofización terrestre se mostró como 13.5 mol N-eq por redondeo de pantalla frente al factor 13.47.
- `QA_EF31_NOX_1kg`: eutrofización marina = 0.389 kg N-eq; eutrofización terrestre = 4.26 mol N-eq.
- `QA_EF31_NO3_1kg`: eutrofización marina = 0.226 kg N-eq. Para el agua dulce canónica se utilizó el subcompartimento SimaPro `river`.

Las capturas `11` a `15` conservan los resultados unitarios. No se crearon procesos unitarios separados para CO2 fósil ni CH4 fósil; sus factores sí fueron inspeccionados directamente en la tabla del método.

## Comprobación agregada PROVISIONAL M1–M2

Se construyeron dos procesos agregados de QA/QC con las mismas cantidades elementales preparadas por Python, excluyendo electricidad IMN y procesos de fondo.

### Escenario A

Resultados SimaPro conservados en `18_resultados_escenario_A_provisional_m1_m2.pdf`:

- Cambio climático: 3167.9045 kg CO2-eq.
- Eutrofización marina: 15.648348 kg N-eq.
- Eutrofización terrestre: 617.05171 mol N-eq.

### Escenario B

Resultados SimaPro conservados en `19_resultados_escenario_B_provisional_m1_m2.pdf`:

- Cambio climático: 6252.0981 kg CO2-eq.
- Eutrofización marina: 35.622315 kg N-eq.
- Eutrofización terrestre: 961.26931 mol N-eq.

Las capturas `16` y `17` documentan los inventarios elementales introducidos para A y B.

## Archivos

Los nombres numerados preservan una selección deliberada de evidencia. Se excluyeron capturas de navegación, menús, pruebas de exportación y otras imágenes redundantes que no aportan trazabilidad científica adicional.

Esta carpeta es evidencia de QA/QC y no debe utilizarse como fuente de verdad numérica del ACV. Los resultados canónicos permanecen en los archivos generados por Python bajo `processed/` y `outputs/`.
