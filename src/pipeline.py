"""Flujo de procesamiento del catalogo (se ira completando en commits siguientes)."""

from fuentes import crear_fuente
from validaciones import validar_catalogo


def cargar_catalogo(ruta):
    """Lee el archivo (CSV o JSON) y separa los productos validos de los rechazados.

    Devuelve (validos, rechazados); ver validar_catalogo() para el formato.
    """
    productos = crear_fuente(ruta).cargar()
    return validar_catalogo(productos)