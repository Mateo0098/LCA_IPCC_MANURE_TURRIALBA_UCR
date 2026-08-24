"""Exporta A1 desde el ledger canónico de N/TAN."""
from acv_resumen_emisiones_csv import exportar_fila_absoluta
from reactive_n_ledger import emission_row

if __name__ == "__main__":
    exportar_fila_absoluta("A", 1, emission_row("A", 1))
