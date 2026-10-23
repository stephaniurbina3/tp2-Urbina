"""Pruebas de la clase ProductoNutricional."""

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from producto import ProductoNutricional  # noqa: E402


def ficha_ejemplo():
    """Ficha ya normalizada: valores por 100 g en la unidad de comparacion."""
    return {
        "codigo": "0012345678905",
        "nombre": "Cereal Avena Alfa",
        "categorias": ["Cereales", "Desayuno"],
        "nutrientes": {"energia": 375.0, "grasas": 0.0, "sodio": 150.0},
    }


class PruebasProductoNutricional(unittest.TestCase):
    def setUp(self):
        self.producto = ProductoNutricional(ficha_ejemplo())

    def test_guarda_los_datos_de_la_ficha(self):
        self.assertEqual(self.producto.codigo, "0012345678905")
        self.assertEqual(self.producto.nombre, "Cereal Avena Alfa")
        self.assertEqual(self.producto.categorias, ["Cereales", "Desayuno"])

    def test_obtiene_un_nutriente_disponible(self):
        self.assertEqual(self.producto.obtener("energia"), 375.0)
        self.assertEqual(self.producto.obtener("sodio"), 150.0)

    def test_nutriente_no_disponible_es_none_y_no_cero(self):
        valor = self.producto.obtener("azucares")
        self.assertIsNone(valor)
        self.assertNotEqual(valor, 0)

    def test_cero_informado_se_conserva(self):
        valor = self.producto.obtener("grasas")
        self.assertIsNotNone(valor)
        self.assertEqual(valor, 0.0)

    def test_nutriente_desconocido_levanta_error(self):
        with self.assertRaises(ValueError):
            self.producto.obtener("colesterol")


if __name__ == "__main__":
    unittest.main()