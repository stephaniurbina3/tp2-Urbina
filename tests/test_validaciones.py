"""Pruebas de las validaciones del catalogo."""

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))  # para poder importar los modulos de src

from error_datos import ErrorDatos  # noqa: E402
from validaciones import validar_catalogo, validar_codigo, validar_producto  # noqa: E402


def producto_valido(codigo="7791234567890", nombre="Cereal Avena Alfa"):
    """Devuelve un producto valido NUEVO (cada prueba lo modifica a su gusto)."""
    return {
        "codigo": codigo,
        "nombre": nombre,
        "categorias": "Cereales",
        "base": "100g",
        "nutrientes": {
            "energia": {"valor": 380.0, "unidad": "kcal"},
            "grasas": {"valor": 6.5, "unidad": "g"},
            "sodio": {"valor": 120.0, "unidad": "mg"},
        },
    }


class PruebasCodigoEAN(unittest.TestCase):
    def test_codigos_validos(self):
        for codigo in ["7791234567890", "0012345678905", "12345678", "00000000"]:
            with self.subTest(codigo=codigo):
                validar_codigo(codigo)  # no debe levantar error

    def test_codigos_invalidos(self):
        invalidos = [
            "",                 # vacio
            "1234567",          # 7 digitos
            "123456789",        # 9 digitos
            "12345678901234",   # 14 digitos
            "77912345678AB",    # con letras
            "7791234567890.0",  # un numero leido como decimal
            " 7791234567890",   # con un espacio
            "7791234567890\n",  # con un salto de linea al final
            "\uff11\uff12\uff13\uff14\uff15\uff16\uff17\uff18",  # 8 digitos que no son ASCII
        ]
        for codigo in invalidos:
            with self.subTest(codigo=codigo):
                with self.assertRaises(ErrorDatos) as contexto:
                    validar_codigo(codigo)
                self.assertEqual(contexto.exception.tipo, "codigo_invalido")

    def test_codigo_que_no_es_texto(self):
        for codigo in [7791234567890, 12345678.0, None]:
            with self.subTest(codigo=codigo):
                with self.assertRaises(ErrorDatos) as contexto:
                    validar_codigo(codigo)
                self.assertEqual(contexto.exception.tipo, "codigo_invalido")


class PruebasReglasDeProducto(unittest.TestCase):
    def tipo_de_error(self, producto):
        """Devuelve el tipo de error del producto (la prueba falla si no hay ninguno)."""
        with self.assertRaises(ErrorDatos) as contexto:
            validar_producto(producto)
        return contexto.exception.tipo

    def test_producto_valido(self):
        validar_producto(producto_valido())  # no debe levantar error

    def test_nutriente_no_informado_y_cero_son_validos(self):
        producto = producto_valido()
        del producto["nutrientes"]["sodio"]                                # no informado
        producto["nutrientes"]["grasas"] = {"valor": 0.0, "unidad": "g"}  # cero declarado
        validar_producto(producto)

    def test_nombre_faltante(self):
        producto = producto_valido(nombre="   ")
        self.assertEqual(self.tipo_de_error(producto), "nombre_faltante")

    def test_base_invalida(self):
        casos = [
            {"base": "200g"},                        # base desconocida
            {"base": "porcion"},                     # porcion sin porcion_g
            {"base": "porcion", "porcion_g": 0},     # porcion_g no positivo
            {"base": "porcion", "porcion_g": "30"},  # porcion_g no es un numero
        ]
        for cambios in casos:
            with self.subTest(cambios=cambios):
                producto = producto_valido()
                producto.update(cambios)
                self.assertEqual(self.tipo_de_error(producto), "base_invalida")

    def test_valor_que_no_es_numero(self):
        for valor in ["abc", "12", None, float("nan"), float("inf"), True]:
            with self.subTest(valor=valor):
                producto = producto_valido()
                producto["nutrientes"]["grasas"]["valor"] = valor
                self.assertEqual(self.tipo_de_error(producto), "valor_invalido")

    def test_unidad_desconocida(self):
        casos = [
            ("sodio", "oz"),
            ("energia", "g"),      # la energia no se mide en gramos
            ("energia", "KJ"),     # solo se admite "kJ"
            ("grasas", "kcal"),
            ("grasas", None),
        ]
        for nutriente, unidad in casos:
            with self.subTest(nutriente=nutriente, unidad=unidad):
                producto = producto_valido()
                producto["nutrientes"][nutriente]["unidad"] = unidad
                self.assertEqual(self.tipo_de_error(producto), "unidad_desconocida")

    def test_valor_negativo(self):
        producto = producto_valido()
        producto["nutrientes"]["grasas"]["valor"] = -4.0
        self.assertEqual(self.tipo_de_error(producto), "valor_negativo")

    def test_grasas_no_pueden_superar_100_g_por_100_g(self):
        producto = producto_valido()
        producto["nutrientes"]["grasas"]["valor"] = 100.0
        validar_producto(producto)  # el limite exacto es valido
        producto["nutrientes"]["grasas"]["valor"] = 140.0
        self.assertEqual(self.tipo_de_error(producto), "fuera_de_rango")

    def test_rango_segun_porcion(self):
        producto = producto_valido()
        producto["base"] = "porcion"
        producto["porcion_g"] = 30
        producto["nutrientes"]["energia"]["valor"] = 100.0
        producto["nutrientes"]["grasas"]["valor"] = 30.0
        validar_producto(producto)  # no puede haber mas gramos que la porcion
        producto["nutrientes"]["grasas"]["valor"] = 31.0
        self.assertEqual(self.tipo_de_error(producto), "fuera_de_rango")

    def test_rango_en_miligramos(self):
        producto = producto_valido()
        producto["nutrientes"]["sodio"] = {"valor": 100000.0, "unidad": "mg"}
        validar_producto(producto)  # 100 g expresados en mg: limite exacto
        producto["nutrientes"]["sodio"]["valor"] = 150000.0
        self.assertEqual(self.tipo_de_error(producto), "fuera_de_rango")

    def test_energia_fuera_de_rango(self):
        producto = producto_valido()
        producto["nutrientes"]["energia"] = {"valor": 3766.0, "unidad": "kJ"}
        validar_producto(producto)  # limite exacto en kJ
        producto["nutrientes"]["energia"]["valor"] = 3800.0
        self.assertEqual(self.tipo_de_error(producto), "fuera_de_rango")
        producto["nutrientes"]["energia"] = {"valor": 950.0, "unidad": "kcal"}
        self.assertEqual(self.tipo_de_error(producto), "fuera_de_rango")


class PruebasValidarCatalogo(unittest.TestCase):
    def test_conserva_los_validos_aunque_haya_rechazados(self):
        bueno_1 = producto_valido("7791111111111", "Producto uno")
        malo = producto_valido("7792222222222", "Producto malo")
        malo["nutrientes"]["azucares"] = {"valor": -4.0, "unidad": "g"}
        bueno_2 = producto_valido("7793333333333", "Producto dos")

        validos, rechazados = validar_catalogo([bueno_1, malo, bueno_2])

        self.assertEqual(validos, [bueno_1, bueno_2])  # se conservan, en orden
        self.assertEqual(len(rechazados), 1)
        self.assertEqual(len(validos) + len(rechazados), 3)  # no se pierde ninguno

    def test_registra_posicion_codigo_y_motivo(self):
        malo = producto_valido("7792222222222", "Producto malo")
        malo["nutrientes"]["azucares"] = {"valor": -4.0, "unidad": "g"}

        _, rechazados = validar_catalogo([producto_valido(), malo])

        rechazo = rechazados[0]
        self.assertEqual(rechazo["posicion"], 2)
        self.assertEqual(rechazo["codigo"], "7792222222222")
        self.assertEqual(rechazo["nombre"], "Producto malo")
        self.assertEqual(rechazo["tipo"], "valor_negativo")
        self.assertIn("azucares", rechazo["motivo"])

    def test_duplicado_se_conserva_el_primero(self):
        primero = producto_valido("7791234567890", "Primero")
        segundo = producto_valido("7791234567890", "Segundo")

        validos, rechazados = validar_catalogo([primero, segundo])

        self.assertEqual(validos, [primero])
        self.assertEqual(rechazados[0]["tipo"], "codigo_duplicado")
        self.assertEqual(rechazados[0]["posicion"], 2)
        self.assertEqual(rechazados[0]["nombre"], "Segundo")

    def test_duplicado_de_un_producto_rechazado_no_cuenta(self):
        malo = producto_valido("7791234567890", "Malo")
        malo["nutrientes"]["grasas"]["valor"] = -1.0
        bueno = producto_valido("7791234567890", "Bueno")

        validos, rechazados = validar_catalogo([malo, bueno])

        self.assertEqual(validos, [bueno])
        self.assertEqual(rechazados[0]["tipo"], "valor_negativo")

    def test_catalogo_vacio(self):
        self.assertEqual(validar_catalogo([]), ([], []))


if __name__ == "__main__":
    unittest.main()