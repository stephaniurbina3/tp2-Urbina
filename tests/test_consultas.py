"""Pruebas de indice, busqueda, seleccion y comparacion."""

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))  # para poder importar los modulos de src

from conversiones import UNIDAD_DE_COMPARACION  # noqa: E402
from error_consulta import ErrorConsulta  # noqa: E402
from error_datos import ErrorDatos  # noqa: E402
from pipeline import (  # noqa: E402
    NO_DISPONIBLE,
    buscar_producto,
    comparar_etiquetas,
    indexar_productos,
    listar_categorias,
    nombre_de_columna,
    normalizar_ficha,
    preparar_catalogo,
    seleccionar_por_categoria,
    seleccionar_por_codigos,
)
from producto import ProductoNutricional  # noqa: E402

CEREAL = "7791111111111"
YOGUR = "7792222222222"
GALLETITAS = "0012345678905"  # con cero inicial


def crear_producto(codigo, nombre, categorias, **nutrientes):
    """Crea un ProductoNutricional con una ficha ya normalizada (valores por 100 g)."""
    return ProductoNutricional({
        "codigo": codigo,
        "nombre": nombre,
        "categorias": categorias,
        "nutrientes": nutrientes,
    })


def catalogo_chico():
    return [
        crear_producto(CEREAL, "Cereal Avena Alfa", ["Cereales", "Desayuno"],
                       energia=380.0, grasas=6.0),
        crear_producto(YOGUR, "Yogur Natural Beta", ["Yogures", "Lácteos"],
                       energia=60.0),
        crear_producto(GALLETITAS, "Galletitas Dulces Gamma",
                       ["Galletitas", "Desayuno", "Snacks"],
                       energia=480.0, grasas=18.0, sodio=400.0),
    ]


class PruebasIndiceYBusqueda(unittest.TestCase):
    def setUp(self):
        self.indice = indexar_productos(catalogo_chico())

    def test_indexa_por_codigo_como_texto(self):
        self.assertEqual(list(self.indice), [CEREAL, YOGUR, GALLETITAS])
        self.assertIn("0012345678905", self.indice)  # conserva el cero inicial

    def test_codigos_repetidos_no_se_pueden_indexar(self):
        repetidos = catalogo_chico() + [crear_producto(CEREAL, "Otro", ["Cereales"])]
        with self.assertRaises(ErrorDatos) as contexto:
            indexar_productos(repetidos)
        self.assertEqual(contexto.exception.tipo, "codigo_duplicado")

    def test_busca_un_producto_existente(self):
        self.assertEqual(buscar_producto(self.indice, YOGUR).nombre, "Yogur Natural Beta")
        self.assertEqual(buscar_producto(self.indice, GALLETITAS).nombre,
                         "Galletitas Dulces Gamma")

    def test_codigo_inexistente(self):
        with self.assertRaises(ErrorConsulta) as contexto:
            buscar_producto(self.indice, "7790000000000")
        self.assertIn("7790000000000", str(contexto.exception))

    def test_codigo_con_formato_invalido(self):
        for codigo in ["abc", "123", "", " 7791111111111", 7791111111111, None]:
            with self.subTest(codigo=codigo):
                with self.assertRaises(ErrorConsulta):
                    buscar_producto(self.indice, codigo)


class PruebasCategorias(unittest.TestCase):
    def setUp(self):
        self.productos = catalogo_chico()

    def test_lista_las_categorias_con_su_cantidad(self):
        esperado = [
            ("Cereales", 1), ("Desayuno", 2), ("Galletitas", 1),
            ("Lácteos", 1), ("Snacks", 1), ("Yogures", 1),
        ]
        self.assertEqual(listar_categorias(self.productos), esperado)

    def test_un_producto_pertenece_a_todas_sus_categorias(self):
        desayuno = seleccionar_por_categoria(self.productos, "Desayuno")
        self.assertEqual([p.codigo for p in desayuno], [CEREAL, GALLETITAS])  # orden original
        cereales = seleccionar_por_categoria(self.productos, "Cereales")
        self.assertEqual([p.codigo for p in cereales], [CEREAL])

    def test_la_categoria_se_compara_sin_mayusculas_ni_tildes(self):
        for texto in ["Lácteos", "lacteos", " LÁCTEOS "]:
            with self.subTest(texto=texto):
                elegidos = seleccionar_por_categoria(self.productos, texto)
                self.assertEqual([p.codigo for p in elegidos], [YOGUR])

    def test_categoria_sin_coincidencias(self):
        with self.assertRaises(ErrorConsulta) as contexto:
            seleccionar_por_categoria(self.productos, "Verduras")
        mensaje = str(contexto.exception)
        self.assertIn("Verduras", mensaje)
        self.assertIn("Cereales", mensaje)  # informa las categorias disponibles

    def test_categorias_que_solo_difieren_en_tildes_se_agrupan(self):
        productos = [
            crear_producto(CEREAL, "Uno", ["Lácteos"]),
            crear_producto(YOGUR, "Dos", ["lacteos"]),
        ]
        self.assertEqual(listar_categorias(productos), [("Lácteos", 2)])


class PruebasSeleccionPorCodigos(unittest.TestCase):
    def setUp(self):
        self.indice = indexar_productos(catalogo_chico())

    def test_selecciona_en_el_orden_pedido(self):
        elegidos = seleccionar_por_codigos(self.indice, [GALLETITAS, CEREAL])
        self.assertEqual([p.codigo for p in elegidos], [GALLETITAS, CEREAL])

    def test_ignora_codigos_repetidos_en_el_pedido(self):
        elegidos = seleccionar_por_codigos(self.indice, [CEREAL, CEREAL])
        self.assertEqual([p.codigo for p in elegidos], [CEREAL])

    def test_un_codigo_inexistente_detiene_la_seleccion(self):
        with self.assertRaises(ErrorConsulta) as contexto:
            seleccionar_por_codigos(self.indice, [CEREAL, "7790000000000"])
        self.assertIn("7790000000000", str(contexto.exception))

    def test_informa_todos_los_codigos_con_problemas(self):
        with self.assertRaises(ErrorConsulta) as contexto:
            seleccionar_por_codigos(self.indice, ["abc", "7790000000000"])
        mensaje = str(contexto.exception)
        self.assertIn("abc", mensaje)
        self.assertIn("7790000000000", mensaje)

    def test_sin_codigos(self):
        with self.assertRaises(ErrorConsulta):
            seleccionar_por_codigos(self.indice, [])


class PruebasCompararEtiquetas(unittest.TestCase):
    def test_una_fila_por_producto_con_las_mismas_columnas(self):
        tabla = comparar_etiquetas(catalogo_chico())
        self.assertEqual(len(tabla), 3)
        columnas = ["codigo", "nombre"] + [nombre_de_columna(n) for n in UNIDAD_DE_COMPARACION]
        for fila in tabla:
            self.assertEqual(list(fila), columnas)
        self.assertEqual(tabla[0]["codigo"], CEREAL)
        self.assertEqual(tabla[0][nombre_de_columna("energia")], 380.0)

    def test_nutrientes_faltantes_quedan_como_no_disponible(self):
        yogur = comparar_etiquetas(catalogo_chico())[1]
        self.assertEqual(yogur[nombre_de_columna("grasas")], NO_DISPONIBLE)
        self.assertNotEqual(yogur[nombre_de_columna("grasas")], 0)
        self.assertEqual(yogur[nombre_de_columna("energia")], 60.0)

    def test_cero_declarado_no_se_marca_como_no_disponible(self):
        tabla = comparar_etiquetas(
            [crear_producto(CEREAL, "Sin grasa", ["Cereales"], grasas=0.0)]
        )
        self.assertEqual(tabla[0][nombre_de_columna("grasas")], 0.0)

    def test_compara_productos_con_unidades_originales_distintas(self):
        producto_a = {
            "codigo": CEREAL, "nombre": "Producto A", "categorias": "Cereales",
            "base": "100g",
            "nutrientes": {
                "energia": {"valor": 400.0, "unidad": "kcal"},
                "sodio": {"valor": 0.2, "unidad": "g"},
            },
        }
        producto_b = {
            "codigo": YOGUR, "nombre": "Producto B", "categorias": "Cereales",
            "base": "porcion", "porcion_g": 50.0,
            "nutrientes": {
                "energia": {"valor": 836.8, "unidad": "kJ"},  # 200 kcal en 50 g
                "sodio": {"valor": 100.0, "unidad": "mg"},    # 100 mg en 50 g
            },
        }
        productos = [ProductoNutricional(normalizar_ficha(p)) for p in (producto_a, producto_b)]
        fila_a, fila_b = comparar_etiquetas(productos)
        # Los dos equivalen a 400 kcal y 200 mg cada 100 g
        for nutriente, esperado in [("energia", 400.0), ("sodio", 200.0)]:
            columna = nombre_de_columna(nutriente)
            self.assertAlmostEqual(fila_a[columna], esperado)
            self.assertAlmostEqual(fila_b[columna], esperado)

    def test_redondea_a_dos_decimales(self):
        tabla = comparar_etiquetas(
            [crear_producto(CEREAL, "Uno", ["Cereales"], energia=374.7611)]
        )
        self.assertEqual(tabla[0][nombre_de_columna("energia")], 374.76)

    def test_sin_productos(self):
        with self.assertRaises(ErrorConsulta):
            comparar_etiquetas([])


class PruebasConLaMuestra(unittest.TestCase):
    """Pruebas con los archivos de data/ (la muestra simulada del proyecto)."""

    def setUp(self):
        self.productos, _ = preparar_catalogo(RAIZ / "data" / "productos.csv")

    def test_las_categorias_principales_tienen_14_productos(self):
        # Cada categoria tenia 15 productos y perdio uno por los defectos deliberados
        cantidades = dict(listar_categorias(self.productos))
        for categoria in ["Cereales", "Yogures", "Jugos", "Galletitas"]:
            self.assertEqual(cantidades[categoria], 14)

    def test_csv_y_json_dan_la_misma_comparacion(self):
        desde_json, _ = preparar_catalogo(RAIZ / "data" / "productos.json")
        self.assertEqual(comparar_etiquetas(self.productos), comparar_etiquetas(desde_json))

    def test_busca_por_codigo_con_cero_inicial(self):
        indice = indexar_productos(self.productos)
        codigo = next(c for c in indice if c.startswith("0"))
        self.assertEqual(buscar_producto(indice, codigo).codigo, codigo)

    def test_faltantes_de_la_muestra_quedan_no_disponibles(self):
        tabla = comparar_etiquetas(self.productos)
        marcados = 0
        for producto, fila in zip(self.productos, tabla):
            for nutriente in UNIDAD_DE_COMPARACION:
                valor = fila[nombre_de_columna(nutriente)]
                if producto.obtener(nutriente) is None:
                    self.assertEqual(valor, NO_DISPONIBLE)
                    marcados += 1
                else:
                    self.assertNotEqual(valor, NO_DISPONIBLE)
        self.assertGreater(marcados, 0)


if __name__ == "__main__":
    unittest.main()