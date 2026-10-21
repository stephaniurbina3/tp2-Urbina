"""Contrato comun de las fuentes de datos.

Todas las fuentes devuelven la MISMA estructura: una lista de productos, donde
cada producto es un diccionario como este:

    {
        "codigo": "0012345678905",       # texto (conserva ceros iniciales)
        "nombre": "Cereal Avena Alfa",
        "categorias": "Cereales, Desayuno",
        "base": "porcion",               # "100g" o "porcion"
        "porcion_g": 30.0,               # solo si la base es porcion
        "nutrientes": {                  # solo los nutrientes informados
            "energia": {"valor": 120.0, "unidad": "kcal"},
            "sodio": {"valor": 0.05, "unidad": "g"},
        },
    }

Esta etapa solo LEE: no valida el contenido (codigos, rangos, duplicados) ni
convierte unidades. Si el archivo no existe, esta mal formado o no tiene la
estructura esperada, se detiene con un mensaje claro.
"""

from abc import ABC, abstractmethod
from pathlib import Path


class FuenteDatos(ABC):
    """Contrato comun de las fuentes: se crean con una ruta y devuelven productos."""

    def __init__(self, ruta):
        self.ruta = Path(ruta)

    @abstractmethod
    def cargar(self):
        """Lee el archivo y devuelve la lista de productos (ver estructura arriba)."""

    def _verificar_que_existe(self):
        if not self.ruta.is_file():
            raise FileNotFoundError(f"No se encontró el archivo de datos: {self.ruta}")