"""Pruebas del menu interactivo, con respuestas simuladas."""

import csv
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))  # para poder importar los modulos de src

import main  # noqa: E402


class PruebasMenu(unittest.TestCase):
    def setUp(self):
        carpeta = tempfile.TemporaryDirectory()
        self.addCleanup(carpeta.cleanup)
        self.salidas = Path(carpeta.name)  # las pruebas no escriben en outputs/ real

    def ejecutar(self, respuestas):
        """Ejecuta el programa con esas respuestas y devuelve lo que imprimio."""
        salida = io.StringIO()
        with patch("main.CARPETA_SALIDAS", self.salidas), \
                patch("builtins.input", side_effect=respuestas), \
                redirect_stdout(salida):
            main.main()
        return salida.getvalue()

    def test_muestra_el_resumen_de_lectura(self):
        # Respuestas: ruta (Enter = predeterminada), salir
        texto = self.ejecutar(["", "0"])
        self.assertIn("Registros leídos: 60", texto)
        self.assertIn("Válidos: 56", texto)
        self.assertIn("Rechazados: 4", texto)

    def test_lee_tambien_un_archivo_json(self):
        ruta_json = str(RAIZ / "data" / "productos.json")
        texto = self.ejecutar([ruta_json, "0"])
        self.assertIn("Válidos: 56", texto)

    def test_guarda_el_registro_de_rechazados(self):
        self.ejecutar(["", "0"])
        with open(self.salidas / "rechazados.csv", encoding="utf-8", newline="") as archivo:
            filas = list(csv.DictReader(archivo))
        self.assertEqual(len(filas), 4)
        tipos = sorted(fila["tipo"] for fila in filas)
        self.assertEqual(
            tipos, ["codigo_duplicado", "codigo_invalido", "fuera_de_rango", "valor_negativo"]
        )
        self.assertTrue(all(fila["motivo"] for fila in filas))

    def test_lista_las_categorias(self):
        # Respuestas: ruta, opcion 1, Enter para volver al menu, salir
        texto = self.ejecutar(["", "1", "", "0"])
        self.assertIn("Categorías disponibles", texto)
        self.assertIn("Cereales: 14 producto(s)", texto)

    def test_archivo_inexistente_vuelve_a_pedir_la_ruta(self):
        texto = self.ejecutar(["no_existe.csv", "salir"])
        self.assertIn("No se pudo leer el archivo", texto)
        self.assertIn("Programa terminado", texto)
        self.assertNotIn("=== Menú ===", texto)

    def test_codigo_inexistente_no_cierra_el_programa(self):
        # Respuestas: ruta, opcion 2, codigo, Enter, salir
        texto = self.ejecutar(["", "2", "7790000000000", "", "0"])
        self.assertIn("No hay ningún producto con el código 7790000000000", texto)
        self.assertIn("¡Hasta luego!", texto)  # el programa siguio y salio bien

    def test_opcion_invalida(self):
        texto = self.ejecutar(["", "9", "", "0"])
        self.assertIn("Opción no válida", texto)

    def test_compara_una_categoria_y_exporta_a_json(self):
        # Respuestas: ruta, opcion 3, categoria, Enter, opcion 5, nombre, Enter, salir
        texto = self.ejecutar(["", "3", "yogures", "", "5", "comparacion.json", "", "0"])
        self.assertIn("Yogur", texto)
        with open(self.salidas / "comparacion.json", encoding="utf-8") as archivo:
            filas = json.load(archivo)
        self.assertEqual(len(filas), 14)
        self.assertIn("energia (kcal)", filas[0])

    def test_exportar_sin_comparar_antes(self):
        texto = self.ejecutar(["", "5", "", "0"])
        self.assertIn("Primero hacé una comparación", texto)

    def test_un_error_inesperado_no_se_oculta(self):
        # Si algo falla por un error de programacion, el programa no lo tapa
        with patch("main.listar", side_effect=RuntimeError("falla de prueba")):
            with self.assertRaises(RuntimeError):
                self.ejecutar(["", "1"])


if __name__ == "__main__":
    unittest.main()