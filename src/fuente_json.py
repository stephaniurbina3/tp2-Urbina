"""Fuente de datos para archivos JSON."""

import json

from fuente_datos import FuenteDatos


class FuenteJSON(FuenteDatos):
    """Lee productos desde un JSON: una lista de objetos con los nutrientes anidados."""

    def cargar(self):
        self._verificar_que_existe()
        with open(self.ruta, encoding="utf-8-sig") as archivo:
            try:
                productos = json.load(archivo)
            except json.JSONDecodeError as error:
                raise ValueError(f"{self.ruta.name}: JSON mal formado ({error})") from error
        if not isinstance(productos, list) or not all(isinstance(p, dict) for p in productos):
            raise ValueError(f"{self.ruta.name}: se esperaba una lista de productos (objetos)")
        return productos