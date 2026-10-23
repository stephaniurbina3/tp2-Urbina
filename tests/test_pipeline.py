"""Pruebas del flujo de lectura y validacion con la muestra real de data/."""

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from pipeline import cargar_catalogo  # noqa: E402
from validaciones import validar_producto  # noqa: E402

# Los 4 defectos deliberados de la muestra (ver data/README.md)
TIPOS_DE_LOS_DEFECTOS = [
    "codigo_duplicado",
    "codigo_invalido",
    "fuera_de_rango",
    "valor_negativo",
]


class PruebasCatalogoReal(unittest.TestCase):
    def test_muestra_csv_separa_validos_y_rechazados(self):
        validos, rechazados = cargar_catalogo(RAIZ / "data" / "productos.csv")
        self.assertEqual(len(validos), 56)
        self.assertEqual(len(rechazados), 4)
        self.assertEqual(sorted(r["tipo"] for r in rechazados), TIPOS_DE_LOS_DEFECTOS)

    def test_csv_y_json_dan_el_mismo_resultado(self):
        desde_csv = cargar_catalogo(RAIZ / "data" / "productos.csv")
        desde_json = cargar_catalogo(RAIZ / "data" / "productos.json")
        self.assertEqual(desde_csv, desde_json)

    def test_los_validos_cumplen_las_reglas(self):
        validos, _ = cargar_catalogo(RAIZ / "data" / "productos.csv")
        codigos = [producto["codigo"] for producto in validos]
        self.assertEqual(len(codigos), len(set(codigos)))  # sin codigos repetidos
        for producto in validos:
            validar_producto(producto)  # ninguno levanta error
        # los codigos con cero inicial se conservan (como texto)
        self.assertTrue([c for c in codigos if c.startswith("0")])


if __name__ == "__main__":
    unittest.main()