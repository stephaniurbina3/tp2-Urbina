"""Clase de dominio: un producto con su ficha nutricional ya normalizada."""

from conversiones import UNIDAD_DE_COMPARACION


class ProductoNutricional:
    """Un producto del catalogo.

    Contiene su ficha normalizada (ver normalizar_ficha en pipeline.py): codigo,
    nombre, categorias (lista) y nutrientes por cada 100 g, en la unidad de
    comparacion de cada uno.
    """

    def __init__(self, ficha):
        self.ficha = ficha
        self.codigo = ficha["codigo"]
        self.nombre = ficha["nombre"]
        self.categorias = ficha["categorias"]

    def obtener(self, nutriente):
        """Devuelve el nutriente por 100 g, en su unidad de comparacion.

        Devuelve None si el nutriente no esta disponible en la ficha: no es lo
        mismo que cero. Si el nombre no es un nutriente conocido, levanta
        ValueError (asi un error de tipeo no se confunde con un dato no disponible).
        """
        if nutriente not in UNIDAD_DE_COMPARACION:
            raise ValueError(f"Nutriente desconocido: '{nutriente}'")
        return self.ficha["nutrientes"].get(nutriente)

    def __repr__(self):
        return f"ProductoNutricional({self.codigo!r}, {self.nombre!r})"