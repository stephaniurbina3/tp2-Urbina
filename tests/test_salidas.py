"""Pruebas de las salidas: formato en pantalla, exportacion y registro de rechazados."""

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))  # para poder importar los modulos de src

from error_consulta import ErrorConsulta  # noqa: E402
from pipeline import NO_DISPONIBLE, comparar_etiquetas, preparar_catalogo  # noqa: E402
from salidas import (  # noqa: E402
    COLUMNAS_RECHAZADOS,
    exportar_tabla,
    formatear_resumen,
    formatear_tabla,
    guardar_rechazados,
)


def tabla_ejemplo():
    return [
        {"codigo": "0012345678905", "nombre": "Cereal Avena Alfa",
         "energia (kcal)": 374.76, "grasas (g)": 10.0, "sodio (mg)": 150.0},
        {"codigo": "7792222222222", "nombre": "Yogur Natural Beta",
         "energia (kcal)": 60.0, "grasas (g)": NO_DISPONIBLE, "sodio (mg)": 45.5},
    ]


class PruebaConCarpeta(unittest.TestCase):
    """Base: da una carpeta temporal para guardar archivos de prueba."""

    def setUp(self):
        carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(carpeta.cleanup)  # se borra sola al terminar cada prueba
        self.carpeta = Path(carpeta.name)

    def leer_csv(self, ruta):
        with open(ruta, encoding="utf-8", newline="") as archivo:
            return list(csv.DictReader(archivo))


class PruebasFormatoDePantalla(unittest.TestCase):
    def test_columnas_alineadas_y_leyenda(self):
        texto = formatear_tabla(tabla_ejemplo())
        lineas = texto.split("\n")
        # encabezado, separador y dos filas tienen el mismo ancho
        self.assertEqual(len({len(linea) for linea in lineas[:4]}), 1)
        self.assertIn("Código", lineas[0])
        self.assertIn("100 g", texto)
        self.assertIn("N/D = no disponible", texto)

    def test_muestra_nd_sin_modificar_la_tabla(self):
        tabla = tabla_ejemplo()
        texto = formatear_tabla(tabla)
        fila_yogur = next(l for l in texto.split("\n") if "7792222222222" in l)
        self.assertIn("N/D", fila_yogur)
        self.assertEqual(tabla[1]["grasas (g)"], NO_DISPONIBLE)  # la tabla sigue igual

    def test_tabla_vacia(self):
        with self.assertRaises(ErrorConsulta):
            formatear_tabla([])


class PruebasExportacion(PruebaConCarpeta):
    def test_exporta_csv(self):
        ruta = exportar_tabla(tabla_ejemplo(), self.carpeta / "comparacion.csv")
        filas = self.leer_csv(ruta)
        self.assertEqual(len(filas), 2)
        self.assertEqual(list(filas[0]), list(tabla_ejemplo()[0]))  # mismas columnas, mismo orden
        self.assertEqual(filas[0]["codigo"], "0012345678905")       # conserva el cero inicial
        self.assertEqual(filas[0]["energia (kcal)"], "374.76")
        self.assertEqual(filas[1]["grasas (g)"], NO_DISPONIBLE)     # no disponible, no cero

    def test_exporta_json(self):
        ruta = exportar_tabla(tabla_ejemplo(), self.carpeta / "comparacion.json")
        with open(ruta, encoding="utf-8") as archivo:
            self.assertEqual(json.load(archivo), tabla_ejemplo())

    def test_crea_las_carpetas_que_faltan(self):
        ruta = self.carpeta / "una" / "otra" / "comparacion.json"
        exportar_tabla(tabla_ejemplo(), ruta)
        self.assertTrue(ruta.is_file())

    def test_formato_no_soportado(self):
        for nombre in ["comparacion.xlsx", "comparacion"]:
            with self.subTest(nombre=nombre):
                with self.assertRaises(ErrorConsulta):
                    exportar_tabla(tabla_ejemplo(), self.carpeta / nombre)

    def test_tabla_vacia(self):
        with self.assertRaises(ErrorConsulta):
            exportar_tabla([], self.carpeta / "comparacion.csv")

    def test_misma_entrada_misma_salida(self):
        entrada = RAIZ / "data" / "productos.csv"
        for extension in [".csv", ".json"]:
            with self.subTest(extension=extension):
                primera, _ = preparar_catalogo(entrada)
                segunda, _ = preparar_catalogo(entrada)
                a = exportar_tabla(comparar_etiquetas(primera), self.carpeta / ("a" + extension))
                b = exportar_tabla(comparar_etiquetas(segunda), self.carpeta / ("b" + extension))
                self.assertEqual(a.read_bytes(), b.read_bytes())

    def test_csv_y_json_de_entrada_exportan_lo_mismo(self):
        desde_csv, _ = preparar_catalogo(RAIZ / "data" / "productos.csv")
        desde_json, _ = preparar_catalogo(RAIZ / "data" / "productos.json")
        a = exportar_tabla(comparar_etiquetas(desde_csv), self.carpeta / "desde_csv.json")
        b = exportar_tabla(comparar_etiquetas(desde_json), self.carpeta / "desde_json.json")
        self.assertEqual(a.read_bytes(), b.read_bytes())


class PruebasRechazadosYResumen(PruebaConCarpeta):
    def test_guarda_rechazados_con_su_motivo(self):
        rechazados = [
            {"posicion": 4, "codigo": "123456", "nombre": "Uno",
             "tipo": "codigo_invalido", "motivo": "el código '123456' no tiene 8 ni 13 dígitos"},
            {"posicion": 9, "codigo": "0012345678905", "nombre": "Dos",
             "tipo": "valor_negativo", "motivo": "azucares: el valor -4 es negativo"},
        ]
        ruta = self.carpeta / "salidas" / "rechazados.csv"
        guardar_rechazados(rechazados, ruta)
        filas = self.leer_csv(ruta)
        self.assertEqual(list(filas[0]), COLUMNAS_RECHAZADOS)
        self.assertEqual(len(filas), 2)
        self.assertEqual(filas[1]["codigo"], "0012345678905")  # conserva el cero inicial
        self.assertEqual(filas[1]["tipo"], "valor_negativo")
        self.assertIn("azucares", filas[1]["motivo"])

    def test_sin_rechazados_guarda_solo_el_encabezado(self):
        ruta = self.carpeta / "rechazados.csv"
        guardar_rechazados([], ruta)
        self.assertEqual(ruta.read_text(encoding="utf-8").splitlines(),
                         [",".join(COLUMNAS_RECHAZADOS)])

    def test_resumen_de_lectura(self):
        rechazados = [{"tipo": "valor_negativo"}, {"tipo": "codigo_invalido"}]
        texto = formatear_resumen([1, 2, 3], rechazados)
        self.assertIn("Registros leídos: 5", texto)
        self.assertIn("Válidos: 3", texto)
        self.assertIn("Rechazados: 2 (codigo_invalido: 1, valor_negativo: 1)", texto)

    def test_resumen_sin_rechazados(self):
        texto = formatear_resumen([1, 2], [])
        self.assertIn("Rechazados: 0", texto)
        self.assertNotIn("(", texto)


if __name__ == "__main__":
    unittest.main()