# Auditoría de integración estadística provisional M1–M2

## Alcance y reglas aplicadas

La integración se construyó exclusivamente desde los promedios de jornada de `processed/muestreos_resumen_intrajornada.csv`. M1 y M2 reciben igual peso temporal; el número de muestras compuestas y de réplicas analíticas no modifica ese peso. La desviación estándar presentada es la desviación entre promedios de jornada y permanece separada de la variabilidad intrajornada.

No se aplicaron pruebas inferenciales ni se conectaron los resultados al modelo ACV. Toda integración M1–M2 es provisional.

## Variables comparables e integración provisional

| Material | Variable | Unidad | M1 | M2 | Promedio provisional | DE entre jornadas | M2 − M1 | Diferencia M2 vs M1 (%) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| estiércol fresco | N total | % masa | 0.3716666666666667 | 0.6644444444444445 | 0.5180555555555556 | 0.20702515204739477 | 0.2927777777777778 | 78.77428998505232 |
| estiércol fresco | humedad | % | 85.76982906572027 | 87.03025437216381 | 86.40004171894205 | 0.8912552813653571 | 1.260425306443537 | 1.46954391791751 |
| estiércol fresco | materia seca | % | 14.23017093427972 | 12.9697456278362 | 13.59995828105796 | 0.8912552813653446 | -1.2604253064435191 | -8.85741508141144 |
| estiércol fresco | cenizas | % | 14.123007600287302 | 16.45109457122497 | 15.287051085756136 | 1.6462060843420745 | 2.328086970937669 | 16.484356851088215 |
| estiércol fresco | sólidos volátiles | % | 85.87699239971269 | 83.54890542877503 | 84.71294891424387 | 1.6462060843420694 | -2.3280869709376617 | -2.7109554094554555 |
| estiércol precompostado | N total | % masa | 2.425 | 2.5833333333333335 | 2.5041666666666664 | 0.11195857368787025 | 0.15833333333333366 | 6.529209621993141 |
| estiércol precompostado | humedad | % | 77.59304506420413 | 81.07106783573836 | 79.33205644997125 | 2.4593334868730827 | 3.478022771534228 | 4.482389843904628 |
| estiércol precompostado | materia seca | % | 22.40695493579587 | 18.92893216426164 | 20.667943550028752 | 2.4593334868730854 | -3.4780227715342313 | -15.5220679539011 |
| estiércol precompostado | cenizas | % | 29.04135297366371 | 20.909649589034746 | 24.975501281349228 | 5.74998260586874 | -8.131703384628963 | -28.00042887810095 |
| estiércol precompostado | sólidos volátiles | % | 70.95864702633628 | 79.09035041096524 | 75.02449871865076 | 5.74998260586874 | 8.131703384628963 | 11.459777948712697 |

La diferencia porcentual es descriptiva y no constituye evidencia de diferencia estadísticamente significativa.

## Variables no comparables y pendientes de M3

- **aguas verdes — N total:** M1 corresponde a especiación y se excluye; M2 (M2=0.00925588888888889) es el único estimador Kjeldahl elegible. Estado: `pendiente_M3`.
- **purines — N total:** M1 corresponde a especiación y se excluye; M2 (M2=0.013937777777777768) es el único estimador Kjeldahl elegible. Estado: `pendiente_M3`.

Las fracciones de N amoniacal, nítrico y ureico de M1 permanecen en la fuente intrajornada únicamente como trazabilidad; no se suman ni se comparan con N total Kjeldahl.

## Variables de solo caracterización

- **aguas verdes — densidad:** M1=1.0;M2=1.0; no es un parámetro actual del modelo ACV.
- **purines — densidad:** M1=1.0;M2=1.0; no es un parámetro actual del modelo ACV.
- **estiércol precompostado — carbono:** M1=35.745;M2=36.86666666666667; no es un parámetro actual del modelo ACV.
- **estiércol precompostado — relación C/N:** M2=14.3; no es un parámetro actual del modelo ACV.

## Observaciones metodológicas y anomalías

- El N total precompostado se conserva sin alterar en la integración. La conversión aprobada a base húmeda se aplica posteriormente y solo en A2 mediante la materia seca gravimétrica del TFG.
- Carbono y relación C/N precompostados se mantienen como caracterización descriptiva.
- La relación C/N precompostada no está disponible como fila independiente en M1; por ello su resumen descriptivo actual contiene únicamente M2.
- No se detectaron duplicados de jornada por material y variable en la fuente.
- Con M3, las reglas incorporarán automáticamente M1+M2+M3 para sólidos y M2+M3 para N de líquidos, sujeto a compatibilidad metodológica.
