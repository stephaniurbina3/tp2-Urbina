"""Flujo de procesamiento del catalogo (se ira completando en commits siguientes)."""

from fuentes import crear_fuente
from validaciones import validar_catalogo

from conversiones import UNIDAD_DE_COMPARACION, a_base_100g, convertir
from producto import ProductoNutricional

def cargar_catalogo(ruta):
    """Lee el archivo (CSV o JSON) y separa los productos validos de los rechazados.

    Devuelve (validos, rechazados); ver validar_catalogo() para el formato.
    """
    productos = crear_fuente(ruta).cargar()
    return validar_catalogo(productos)

def separar_categorias(texto):
    """Convierte 'Cereales, Desayuno' en ['Cereales', 'Desayuno'] (sin espacios ni vacios)."""
    return [parte.strip() for parte in (texto or "").split(",") if parte.strip()]


def normalizar_ficha(producto):
    """Convierte un producto YA VALIDADO en una ficha homogenea.

    La ficha tiene codigo, nombre, categorias (lista) y nutrientes. Cada nutriente
    queda por cada 100 g y en su unidad de comparacion (ver conversiones.py).
    Un nutriente no disponible no se agrega: nunca se reemplaza por cero.
    No se redondea: los valores conservan su precision.
    """
    nutrientes = {}
    for nombre, unidad_destino in UNIDAD_DE_COMPARACION.items():
        dato = producto["nutrientes"].get(nombre)
        if dato is None:
            continue  # no disponible
        valor = convertir(dato["valor"], dato["unidad"], unidad_destino)
        nutrientes[nombre] = a_base_100g(valor, producto["base"], producto.get("porcion_g"))
    return {
        "codigo": producto["codigo"],
        "nombre": producto["nombre"],
        "categorias": separar_categorias(producto.get("categorias")),
        "nutrientes": nutrientes,
    }


def preparar_catalogo(ruta):
    """Lee, valida y normaliza el catalogo.

    Devuelve (productos, rechazados): productos es una lista de ProductoNutricional
    (solo los validos) y rechazados es el registro de productos apartados.
    """
    validos, rechazados = cargar_catalogo(ruta)
    productos = [ProductoNutricional(normalizar_ficha(p)) for p in validos]
    return productos, rechazados