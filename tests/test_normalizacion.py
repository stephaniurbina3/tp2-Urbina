"""Pruebas de la normalizacion de fichas y del catalogo preparado."""

import copy
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from conversiones import UNIDAD_DE_COMPARACION  # noqa: E402
from pipeline import normalizar_ficha, preparar_catalogo, separar_categorias  # noqa: E402
from producto import ProductoNutricional  # noqa: E402
from validaciones import LIMITE_POR_100G  # noqa: E402


def producto_crudo():
    """Producto ya validado, tal como se declara en la etiqueta (por porcion y con kJ)."""
    return {
        "codigo": "0012345678905",
        "nombre": "Cereal Avena Alfa",
        "categorias": "Cereales, Desayuno",
        "base": "porcion",
        "porcion_g": 40.0,
        "nutrientes": {
            "energia": {"valor": 627.6, "unidad": "kJ"},  # 150 kcal en 40 g
            "grasas": {"valor": 4.0, "unidad": "g"},
            "sodio": {"valor": 0.06, "unidad": "g"},      # 60 mg en 40 g
        },
    }


class PruebasNormalizarFicha(unittest.TestCase):
    def test_conserva_codigo_nombre_y_categorias(self):
        ficha = normalizar_ficha(producto_crudo())
        self.assertEqual(ficha["codigo"], "0012345678905")
        self.assertEqual(ficha["nombre"], "Cereal Avena Alfa")
        self.assertEqual(ficha["categorias"], ["Cereales", "Desayuno"])

    def test_convierte_a_unidad_de_comparacion_y_a_100g(self):
        nutrientes = normalizar_ficha(producto_crudo())["nutrientes"]
        self.assertAlmostEqual(nutrientes["energia"], 375.0)  # 150 kcal en 40 g -> 375 kcal cada 100 g
        self.assertAlmostEqual(nutrientes["grasas"], 10.0)    # 4 g en 40 g -> 10 g cada 100 g
        self.assertAlmostEqual(nutrientes["sodio"], 150.0)    # 60 mg en 40 g -> 150 mg cada 100 g

    def test_producto_por_100g_solo_cambia_de_unidad(self):
        producto = producto_crudo()
        producto["base"] = "100g"
        del producto["porcion_g"]
        producto["nutrientes"]["energia"] = {"valor": 1568.0, "unidad": "kJ"}
        nutrientes = normalizar_ficha(producto)["nutrientes"]
        self.assertAlmostEqual(nutrientes["energia"], 1568.0 / 4.184)
        self.assertAlmostEqual(nutrientes["grasas"], 4.0)

    def test_nutriente_no_disponible_no_aparece_ni_se_vuelve_cero(self):
        nutrientes = normalizar_ficha(producto_crudo())["nutrientes"]
        self.assertNotIn("azucares", nutrientes)
        self.assertNotIn("proteinas", nutrientes)

    def test_cero_declarado_se_conserva(self):
        producto = producto_crudo()
        producto["nutrientes"]["grasas"] = {"valor": 0.0, "unidad": "g"}
        nutrientes = normalizar_ficha(producto)["nutrientes"]
        self.assertEqual(nutrientes["grasas"], 0.0)

    def test_los_valores_son_siempre_decimales(self):
        # Un JSON puede traer enteros y un CSV siempre da decimales: la ficha unifica el tipo
        producto = producto_crudo()
        producto["base"] = "100g"
        del producto["porcion_g"]
        producto["nutrientes"]["energia"] = {"valor": 513, "unidad": "kcal"}  # entero
        nutrientes = normalizar_ficha(producto)["nutrientes"]
        self.assertIsInstance(nutrientes["energia"], float)

    def test_no_modifica_el_producto_original(self):
        producto = producto_crudo()
        copia = copy.deepcopy(producto)
        normalizar_ficha(producto)
        self.assertEqual(producto, copia)

    def test_separar_categorias(self):
        self.assertEqual(separar_categorias("Cereales, Desayuno"), ["Cereales", "Desayuno"])
        self.assertEqual(separar_categorias("  Yogures ,, "), ["Yogures"])
        self.assertEqual(separar_categorias(""), [])


class PruebasCatalogoPreparado(unittest.TestCase):
    """Pruebas con los archivos de data/ (la muestra simulada del proyecto)."""

    def setUp(self):
        self.productos, self.rechazados = preparar_catalogo(RAIZ / "data" / "productos.csv")

    def test_devuelve_productos_nutricionales_y_rechazados(self):
        self.assertEqual(len(self.productos), 56)
        self.assertEqual(len(self.rechazados), 4)
        for producto in self.productos:
            self.assertIsInstance(producto, ProductoNutricional)

    def test_csv_y_json_dan_las_mismas_fichas(self):
        desde_json, _ = preparar_catalogo(RAIZ / "data" / "productos.json")
        self.assertEqual([p.ficha for p in self.productos], [p.ficha for p in desde_json])

    def test_los_valores_normalizados_respetan_los_limites_por_100g(self):
        for producto in self.productos:
            for nutriente, unidad in UNIDAD_DE_COMPARACION.items():
                valor = producto.obtener(nutriente)
                if valor is not None:
                    self.assertGreaterEqual(valor, 0)
                    self.assertLessEqual(valor, LIMITE_POR_100G[unidad] + 1e-9)

    def test_los_faltantes_siguen_sin_estar_disponibles(self):
        self.assertTrue(any(p.obtener("grasas_saturadas") is None for p in self.productos))


if __name__ == "__main__":
    unittest.main()