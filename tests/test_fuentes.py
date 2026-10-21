"""Pruebas de lectura: FuenteCSV, FuenteJSON y seleccion de la fuente."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from fuente_csv import FuenteCSV
from fuente_datos import FuenteDatos
from fuente_json import FuenteJSON
from fuentes import crear_fuente

CSV_MINIMO = (
    "codigo,nombre,categorias,base,porcion_g,energia_valor,energia_unidad,sodio_valor,sodio_unidad\n"
    '0012345678905,Cereal Avena Alfa,"Cereales, Desayuno",porcion,30,120,kcal,0.05,g\n'
    "7790000000017,Galletitas Beta,Galletitas,100g,,480,kcal,,g\n"
)

JSON_MINIMO = [
    {
        "codigo": "0012345678905",
        "nombre": "Cereal Avena Alfa",
        "categorias": "Cereales, Desayuno",
        "base": "porcion",
        "porcion_g": 30.0,
        "nutrientes": {
            "energia": {"valor": 120.0, "unidad": "kcal"},
            "sodio": {"valor": 0.05, "unidad": "g"},
        },
    },
    {
        "codigo": "7790000000017",
        "nombre": "Galletitas Beta",
        "categorias": "Galletitas",
        "base": "100g",
        "nutrientes": {"energia": {"valor": 480.0, "unidad": "kcal"}},
    },
]


class PruebasFuentes(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.carpeta = Path(self.temporal.name)

    def tearDown(self):
        self.temporal.cleanup()

    def escribir(self, nombre, contenido):
        ruta = self.carpeta / nombre
        ruta.write_text(contenido, encoding="utf-8")
        return ruta

    # ---------- CSV ----------

    def test_csv_lee_productos(self):
        ruta = self.escribir("productos.csv", CSV_MINIMO)
        productos = FuenteCSV(ruta).cargar()
        self.assertEqual(len(productos), 2)
        primero = productos[0]
        self.assertEqual(primero["codigo"], "0012345678905")  # conserva los ceros iniciales
        self.assertEqual(primero["porcion_g"], 30.0)
        self.assertEqual(primero["nutrientes"]["energia"], {"valor": 120.0, "unidad": "kcal"})

    def test_csv_nutriente_vacio_no_se_agrega(self):
        ruta = self.escribir("productos.csv", CSV_MINIMO)
        segundo = FuenteCSV(ruta).cargar()[1]
        self.assertNotIn("sodio", segundo["nutrientes"])
        self.assertNotIn("porcion_g", segundo)

    def test_csv_faltan_columnas(self):
        ruta = self.escribir("malo.csv", "codigo,nombre\n1,x\n")
        with self.assertRaisesRegex(ValueError, "faltan las columnas"):
            FuenteCSV(ruta).cargar()

    def test_csv_falta_columna_de_unidad(self):
        ruta = self.escribir("malo.csv", "codigo,nombre,categorias,base,sodio_valor\n1,x,y,100g,0.5\n")
        with self.assertRaisesRegex(ValueError, "falta la columna sodio_unidad"):
            FuenteCSV(ruta).cargar()

    def test_csv_numero_invalido(self):
        ruta = self.escribir("malo.csv", CSV_MINIMO.replace(",120,", ",abc,"))
        with self.assertRaisesRegex(ValueError, "fila 2"):
            FuenteCSV(ruta).cargar()

    def test_csv_archivo_inexistente(self):
        with self.assertRaisesRegex(FileNotFoundError, "No se encontró el archivo"):
            FuenteCSV(self.carpeta / "no_existe.csv").cargar()

    # ---------- JSON ----------

    def test_json_lee_productos(self):
        ruta = self.escribir("productos.json", json.dumps(JSON_MINIMO))
        productos = FuenteJSON(ruta).cargar()
        self.assertEqual(productos, JSON_MINIMO)
        self.assertEqual(productos[0]["codigo"], "0012345678905")

    def test_json_mal_formado(self):
        ruta = self.escribir("malo.json", "[{no es json")
        with self.assertRaisesRegex(ValueError, "mal formado"):
            FuenteJSON(ruta).cargar()

    def test_json_estructura_incorrecta(self):
        ruta = self.escribir("malo.json", '{"productos": []}')
        with self.assertRaisesRegex(ValueError, "lista de productos"):
            FuenteJSON(ruta).cargar()

    # ---------- Equivalencia entre formatos ----------

    def test_csv_y_json_equivalentes_con_los_mismos_datos(self):
        ruta_csv = self.escribir("productos.csv", CSV_MINIMO)
        ruta_json = self.escribir("productos.json", json.dumps(JSON_MINIMO))
        self.assertEqual(FuenteCSV(ruta_csv).cargar(), FuenteJSON(ruta_json).cargar())

    def test_archivos_reales_de_data_son_equivalentes(self):
        productos_csv = crear_fuente(RAIZ / "data" / "productos.csv").cargar()
        productos_json = crear_fuente(RAIZ / "data" / "productos.json").cargar()
        self.assertEqual(productos_csv, productos_json)

    # ---------- Seleccion de la fuente ----------

    def test_crear_fuente_csv(self):
        self.assertIsInstance(crear_fuente("datos/productos.csv"), FuenteCSV)

    def test_crear_fuente_json(self):
        self.assertIsInstance(crear_fuente("datos/productos.json"), FuenteJSON)

    def test_crear_fuente_ignora_mayusculas_en_la_extension(self):
        self.assertIsInstance(crear_fuente("datos/PRODUCTOS.CSV"), FuenteCSV)

    def test_crear_fuente_formato_no_soportado(self):
        with self.assertRaisesRegex(ValueError, "Formato no soportado"):
            crear_fuente("datos/productos.txt")

    # ---------- Clase abstracta ----------

    def test_fuente_datos_no_se_puede_instanciar(self):
        with self.assertRaises(TypeError):
            FuenteDatos("cualquier.csv")


if __name__ == "__main__":
    unittest.main()