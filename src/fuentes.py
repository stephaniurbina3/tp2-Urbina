"""Seleccion de la fuente de datos segun el formato del archivo."""

from pathlib import Path

from fuente_csv import FuenteCSV
from fuente_json import FuenteJSON

# Cada extension de archivo se asocia con la clase que sabe leerla
FUENTES = {".csv": FuenteCSV, ".json": FuenteJSON}


def crear_fuente(ruta):
    """Elige la fuente adecuada segun la extension del archivo."""
    extension = Path(ruta).suffix.lower()
    clase = FUENTES.get(extension)
    if clase is None:
        raise ValueError(
            f"Formato no soportado: '{extension}'. Use un archivo .csv o .json"
        )
    return clase(ruta)