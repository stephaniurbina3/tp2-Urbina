"""Pruebas de conversion de unidades y de bases de referencia."""

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))  # para poder importar los modulos de src

from conversiones import a_base_100g, convertir  # noqa: E402


class PruebasConvertir(unittest.TestCase):
    def test_kj_a_kcal(self):
        # 1 kcal = 4,184 kJ, asi que 418,4 kJ son 100 kcal
        self.assertAlmostEqual(convertir(418.4, "kJ", "kcal"), 100.0)

    def test_kcal_a_kj(self):
        self.assertAlmostEqual(convertir(100, "kcal", "kJ"), 418.4)

    def test_g_a_mg_y_mg_a_g(self):
        self.assertAlmostEqual(convertir(1.5, "g", "mg"), 1500.0)
        self.assertAlmostEqual(convertir(250, "mg", "g"), 0.25)

    def test_misma_unidad_no_cambia_el_valor(self):
        self.assertEqual(convertir(12.5, "g", "g"), 12.5)

    def test_ida_y_vuelta_conserva_el_valor(self):
        for valor in [0, 0.05, 1, 37.5, 1580]:
            for una, otra in [("kcal", "kJ"), ("g", "mg")]:
                with self.subTest(valor=valor, unidades=(una, otra)):
                    ida_y_vuelta = convertir(convertir(valor, una, otra), otra, una)
                    self.assertAlmostEqual(ida_y_vuelta, valor)

    def test_unidades_incompatibles(self):
        for desde, hacia in [("g", "kcal"), ("kJ", "mg"), ("oz", "g")]:
            with self.subTest(desde=desde, hacia=hacia):
                with self.assertRaises(ValueError):
                    convertir(1, desde, hacia)


class PruebasBase100g(unittest.TestCase):
    def test_base_100g_no_cambia_el_valor(self):
        self.assertEqual(a_base_100g(12.5, "100g"), 12.5)

    def test_base_porcion_se_lleva_a_100g(self):
        # 6 g en una porcion de 30 g equivalen a 20 g cada 100 g
        self.assertAlmostEqual(a_base_100g(6, "porcion", 30), 20.0)
        # 120 kcal en una porcion de 40 g equivalen a 300 kcal cada 100 g
        self.assertAlmostEqual(a_base_100g(120, "porcion", 40), 300.0)

    def test_base_invalida(self):
        for base, porcion in [("200g", None), ("porcion", None), ("porcion", 0)]:
            with self.subTest(base=base, porcion=porcion):
                with self.assertRaises(ValueError):
                    a_base_100g(10, base, porcion)


if __name__ == "__main__":
    unittest.main()