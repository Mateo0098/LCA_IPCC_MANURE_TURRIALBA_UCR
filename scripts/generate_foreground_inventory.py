"""Exporta el foreground neutral para la futura integración con SimaPro."""

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
                         "observaciones_doble_conteo": "No duplicar si SimaPro incluye esta emisión elemental."})
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
                     "procedencia": row.procedencia, "condicion_caracterizacion": "Pendiente de proceso de fondo en SimaPro",
                     "dataset_background_pendiente": "Sí", "observaciones_doble_conteo": note})
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
