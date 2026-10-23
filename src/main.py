"""Punto de entrada: menu interactivo del comparador de etiquetas nutricionales.

Uso (desde la raiz del repositorio):
    python src/main.py

El programa pide la ruta del archivo de datos (CSV o JSON); con Enter usa la
ruta predeterminada, data/productos.csv. Solo se atrapan los errores previstos
(archivo inexistente o mal formado, consultas que no se pueden resolver y
problemas al guardar archivos); cualquier otro error se muestra completo, sin
ocultarse.
"""

from pathlib import Path

from error_consulta import ErrorConsulta
from pipeline import (
    buscar_producto,
    cargar_catalogo,
    comparar_etiquetas,
    indexar_productos,
    listar_categorias,
    normalizar_catalogo,
    seleccionar_por_categoria,
    seleccionar_por_codigos,
)
from salidas import (
    CARPETA_SALIDAS,
    exportar_tabla,
    formatear_resumen,
    formatear_tabla,
    guardar_rechazados,
)

RAIZ = Path(__file__).resolve().parent.parent
RUTA_PREDETERMINADA = RAIZ / "data" / "productos.csv"

MENU = """
=== Menú ===
1. Listar las categorías
2. Buscar un producto por código EAN
3. Comparar los productos de una categoría
4. Comparar productos por códigos EAN
5. Exportar la última comparación (CSV o JSON)
0. Salir"""


# ---------- Carga de datos ----------

def pedir_ruta():
    """Pide la ruta del archivo. Enter usa la predeterminada; 'salir' cancela (None)."""
    texto = input(
        f"Ruta del archivo de datos (Enter para usar {RUTA_PREDETERMINADA.relative_to(RAIZ)}, "
        "'salir' para terminar): "
    ).strip().strip('"')
    if texto.lower() == "salir":
        return None
    return Path(texto) if texto else RUTA_PREDETERMINADA


def cargar_datos():
    """Pide la ruta hasta poder leer el archivo.

    Devuelve (productos, rechazados), o None si se cancela.
    """
    while True:
        ruta = pedir_ruta()
        if ruta is None:
            return None
        try:
            validos, rechazados = cargar_catalogo(ruta)
        except (FileNotFoundError, ValueError) as error:
            print(f"No se pudo leer el archivo: {error}")
            continue
        return normalizar_catalogo(validos), rechazados


def guardar_registro_de_rechazados(rechazados):
    ruta = CARPETA_SALIDAS / "rechazados.csv"
    try:
        guardar_rechazados(rechazados, ruta)
    except OSError as error:
        print(f"No se pudo guardar el registro de rechazados: {error}")
    else:
        print(f"Registro de rechazados guardado en {ruta}")


# ---------- Opciones del menu ----------

def mostrar_tabla(tabla):
    print()
    print(formatear_tabla(tabla))


def listar(productos):
    print("\nCategorías disponibles:")
    for nombre, cantidad in listar_categorias(productos):
        print(f"  {nombre}: {cantidad} producto(s)")


def buscar(indice):
    codigo = input("Código EAN: ").strip()
    producto = buscar_producto(indice, codigo)
    print(f"\n{producto.nombre} (categorías: {', '.join(producto.categorias)})")
    mostrar_tabla(comparar_etiquetas([producto]))


def comparar_categoria(productos):
    listar(productos)
    categoria = input("\nCategoría: ").strip()
    tabla = comparar_etiquetas(seleccionar_por_categoria(productos, categoria))
    mostrar_tabla(tabla)
    return tabla


def comparar_codigos(indice):
    texto = input("Códigos EAN separados por espacios o comas: ")
    codigos = texto.replace(",", " ").split()
    tabla = comparar_etiquetas(seleccionar_por_codigos(indice, codigos))
    mostrar_tabla(tabla)
    return tabla


def exportar(tabla):
    if tabla is None:
        print("Primero hacé una comparación (opción 3 o 4).")
        return
    nombre = input("Nombre del archivo (termina en .csv o .json, por ejemplo comparacion.csv): ").strip()
    # Path(...).name descarta carpetas: el archivo siempre queda dentro de outputs/
    ruta = exportar_tabla(tabla, CARPETA_SALIDAS / Path(nombre).name)
    print(f"Comparación guardada en {ruta}")


def ejecutar_menu(productos):
    indice = indexar_productos(productos)
    ultima_tabla = None  # ultima comparacion hecha, para poder exportarla
    while True:
        print(MENU)
        opcion = input("Elegí una opción: ").strip()
        if opcion == "0":
            print("¡Hasta luego!")
            return
        try:
            if opcion == "1":
                listar(productos)
            elif opcion == "2":
                buscar(indice)
            elif opcion == "3":
                ultima_tabla = comparar_categoria(productos)
            elif opcion == "4":
                ultima_tabla = comparar_codigos(indice)
            elif opcion == "5":
                exportar(ultima_tabla)
            else:
                print("Opción no válida. Elegí un número del menú.")
        except ErrorConsulta as error:
            print(f"No se pudo completar la operación: {error}")
        except OSError as error:
            print(f"No se pudo guardar el archivo: {error}")
        input("\nPresioná Enter para volver al menú...")


def main():
    print("Comparador de etiquetas nutricionales")
    try:
        datos = cargar_datos()
        if datos is None:
            print("Programa terminado.")
            return
        productos, rechazados = datos
        print()
        print(formatear_resumen(productos, rechazados))
        guardar_registro_de_rechazados(rechazados)
        if not productos:
            print("No hay productos válidos para consultar.")
            return
        ejecutar_menu(productos)
    except (KeyboardInterrupt, EOFError):
        print("\nPrograma interrumpido.")


if __name__ == "__main__":
    main()