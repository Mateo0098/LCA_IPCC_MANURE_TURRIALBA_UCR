"""Exporta entradas, emisiones y contribución eléctrica sin doble caracterización."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from compute_acv_impact_equivalents import load_functional_reference


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "processed"
OUTPUT = PROCESSED / "acv_foreground_intercambio.csv"

STAGES = {
    ("A", 1): "A1: Precomposteo", ("A", 2): "A2: Lombricompostaje",
    ("A", 3): "A3: Almacenamiento de aguas verdes",
    ("A", 4): "A4: Aplicación de aguas verdes en campos de pastoreo",
    ("B", 1): "B1: Almacenamiento de purines",
    ("B", 2): "B2: Aplicación de purines en campo de pastoreo",
}
EMISSIONS = {
    "CH4_ec1": ("Metano biogénico", "CH4", "air unspecified"),
    "N2O_ec14": ("Óxido nitroso", "N2O", "air unspecified"),
    "N2O_ec2": ("Óxido nitroso", "N2O", "air unspecified"),
    "N2O_ec5": ("Óxido nitroso", "N2O", "air unspecified"),
    "N2O_ec6": ("Óxido nitroso", "N2O", "air unspecified"),
    "N2O_ec16": ("Óxido nitroso", "N2O", "air unspecified"),
    "N2O_ec18": ("Óxido nitroso", "N2O", "air unspecified"),
    "NH3_ec12": ("Amoniaco", "NH3", "air unspecified"),
    "NH3_ec20": ("Amoniaco", "NH3", "air unspecified"),
    "NOx_as_NO2": ("Óxidos de nitrógeno como NO2", "NOx as NO2", "air unspecified"),
    "NO3_ec13": ("Nitrato", "NO3", "fresh water"),
    "NO3_ec21": ("Nitrato", "NO3", "fresh water"),
}


def main() -> None:
    emissions = pd.read_csv(PROCESSED / "ACV_resumen_emisiones.csv")
    reference = load_functional_reference(PROCESSED / "masa_total_escenario_etapa.csv")
    rows: list[dict[str, object]] = []
    for _, row in emissions.iterrows():
        scenario, stage = str(row["Escenario"]), int(row["Etapa"])
        for column, (flow, species, compartment) in EMISSIONS.items():
            value = pd.to_numeric(row.get(column), errors="coerce")
            if pd.isna(value) or float(value) == 0.0:
                continue
            rows.append({"escenario": scenario, "etapa": STAGES[(scenario, stage)], "nombre_flujo": flow,
                         "tipo_flujo": "emisión directa", "cantidad_anual": float(value), "unidad": "kg/año",
                         "cantidad_por_unidad_funcional": float(value) / reference, "especie_quimica": species,
                         "compartimento": compartment, "procedencia": column,
                         "condicion_caracterizacion": "Caracterizado en Python mediante EF 3.1",
                         "dataset_background_pendiente": "No",
                         "observaciones_doble_conteo": "Emisión del manejo ya caracterizada; verificación externa opcional, no sumar otro total."})
    resources = pd.read_csv(PROCESSED / "acv_inventario_recursos_operativos.csv")
    for row in resources.itertuples():
        note = ("El cañón usa la energía del tractor; no añadir energía ni combustión separada."
                if row.flujo == "Diésel" else
                "No añadir tratamiento municipal al agua pluvial; infraestructura existente fuera de frontera.")
        rows.append({"escenario": row.escenario, "etapa": STAGES[(row.escenario, int(row.etapa))],
                     "nombre_flujo": row.flujo, "tipo_flujo": "entrada tecnosférica",
                     "cantidad_anual": row.cantidad_anual, "unidad": row.unidad,
                     "cantidad_por_unidad_funcional": row.cantidad_por_unidad_funcional,
                     "especie_quimica": "", "compartimento": "tecnosfera",
                     "procedencia": row.procedencia, "condicion_caracterizacion": row.estado_lcia_actual,
                     "dataset_background_pendiente": "No", "observaciones_doble_conteo": note})
        if row.flujo == "Diésel":
            for column, flow, species in (
                ("co2_fosil_diesel_kg", "Dióxido de carbono fósil", "CO2"),
                ("ch4_fosil_diesel_kg", "Metano fósil", "CH4"),
                ("n2o_combustion_diesel_kg", "Óxido nitroso de combustión", "N2O"),
            ):
                value = float(getattr(row, column))
                rows.append({"escenario": row.escenario, "etapa": STAGES[(row.escenario, int(row.etapa))],
                             "nombre_flujo": flow, "tipo_flujo": "emisión directa", "cantidad_anual": value,
                             "unidad": "kg/año", "cantidad_por_unidad_funcional": value / reference,
                             "especie_quimica": species, "compartimento": "air unspecified",
                             "procedencia": column, "condicion_caracterizacion": "Emisión física IMN caracterizada con EF 3.1",
                             "dataset_background_pendiente": "No",
                             "observaciones_doble_conteo": "Combustión de diésel ya incluida; no sumar GWP IMN ni otra combustión del cañón."})
        else:
            value = float(row.clima_electricidad_imn_kg_co2eq)
            rows.append({"escenario": row.escenario, "etapa": STAGES[(row.escenario, int(row.etapa))],
                         "nombre_flujo": "Contribución climática de electricidad IMN", "tipo_flujo": "resultado agregado",
                         "cantidad_anual": value, "unidad": "kg CO2-eq/año",
                         "cantidad_por_unidad_funcional": value / reference,
                         "especie_quimica": "", "compartimento": "no aplica",
                         "procedencia": row.factores_imn, "condicion_caracterizacion": "Consumo 2025; proxy temporal de operación 2026",
                         "dataset_background_pendiente": "No",
                         "observaciones_doble_conteo": "No es CO2 elemental; no caracterizar de nuevo con EF ni añadir generación eléctrica separada."})
    for scenario, storage, application, liquid in (("A", 3, 4, "aguas verdes"), ("B", 1, 2, "purín")):
        rows.append({"escenario": scenario, "etapa": STAGES[(scenario, storage)],
                     "nombre_flujo": f"Transferencia de {liquid} hacia aplicación", "tipo_flujo": "transferencia",
                     "cantidad_anual": "", "unidad": "", "cantidad_por_unidad_funcional": "",
                     "especie_quimica": "", "compartimento": "foreground",
                     "procedencia": f"Balance vigente {STAGES[(scenario, storage)]}→{STAGES[(scenario, application)]}",
                     "condicion_caracterizacion": "No caracteriza; evita duplicar el agua y la masa transferidas",
                     "dataset_background_pendiente": "No",
                     "observaciones_doble_conteo": "No añadir nuevamente agua pluvial en la etapa de aplicación."})
    pd.DataFrame(rows).to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    print(f"Foreground neutral: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
