"""Fuente de datos para archivos CSV."""

import csv

from fuente_datos import FuenteDatos

COLUMNAS_OBLIGATORIAS = ["codigo", "nombre", "categorias", "base"]


class FuenteCSV(FuenteDatos):
    """Lee productos desde un CSV con los nutrientes en columnas planas."""

    def cargar(self):
        self._verificar_que_existe()
        # utf-8-sig tambien lee archivos con marca BOM (por ejemplo, guardados desde Excel)
        with open(self.ruta, encoding="utf-8-sig", newline="") as archivo:
            lector = csv.DictReader(archivo)
            nutrientes = self._revisar_columnas(lector.fieldnames or [])
            return [
                self._armar_producto(fila, numero_fila, nutrientes)
                for numero_fila, fila in enumerate(lector, start=2)  # la fila 1 es el encabezado
            ]

    def _revisar_columnas(self, columnas):
        """Comprueba el esquema y devuelve los nombres de los nutrientes del archivo."""
        faltan = [c for c in COLUMNAS_OBLIGATORIAS if c not in columnas]
        if faltan:
            raise ValueError(f"{self.ruta.name}: faltan las columnas {', '.join(faltan)}")
        nutrientes = [c[: -len("_valor")] for c in columnas if c.endswith("_valor")]
        for nutriente in nutrientes:
            if nutriente + "_unidad" not in columnas:
                raise ValueError(f"{self.ruta.name}: falta la columna {nutriente}_unidad")
        return nutrientes

    def _a_numero(self, texto, numero_fila, columna):
        try:
            return float(texto)
        except ValueError:
            raise ValueError(
                f"{self.ruta.name}, fila {numero_fila}, columna '{columna}': "
                f"'{texto}' no es un número"
            ) from None

    def _armar_producto(self, fila, numero_fila, nutrientes):
        producto = {
            "codigo": fila["codigo"],
            "nombre": fila["nombre"],
            "categorias": fila["categorias"],
            "base": fila["base"],
        }
        if fila.get("porcion_g"):
            producto["porcion_g"] = self._a_numero(fila["porcion_g"], numero_fila, "porcion_g")
        producto["nutrientes"] = {}
        for nutriente in nutrientes:
            texto = fila[nutriente + "_valor"]
            if texto:  # celda vacia = nutriente no informado: no se agrega (nunca es cero)
                producto["nutrientes"][nutriente] = {
                    "valor": self._a_numero(texto, numero_fila, nutriente + "_valor"),
                    "unidad": fila[nutriente + "_unidad"],
                }
        return producto