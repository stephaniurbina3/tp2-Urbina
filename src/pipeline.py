"""Flujo de procesamiento del catalogo (se ira completando en commits siguientes)."""

import unicodedata

from fuentes import crear_fuente
from validaciones import PATRON_EAN, validar_catalogo

from conversiones import UNIDAD_DE_COMPARACION, a_base_100g, convertir
from producto import ProductoNutricional

from error_consulta import ErrorConsulta
from error_datos import ErrorDatos

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
        valor_100g = a_base_100g(valor, producto["base"], producto.get("porcion_g"))
        # float(): el valor queda siempre decimal, venga de un CSV (texto) o de un
        # JSON (que puede traer enteros), asi ambos formatos dan fichas identicas
        nutrientes[nombre] = float(valor_100g)
    return {
        "codigo": producto["codigo"],
        "nombre": producto["nombre"],
        "categorias": separar_categorias(producto.get("categorias")),
        "nutrientes": nutrientes,
    }


def normalizar_catalogo(validos):
    """Normaliza los productos validos y los devuelve como ProductoNutricional."""
    return [ProductoNutricional(normalizar_ficha(p)) for p in validos]


def preparar_catalogo(ruta):
    """Lee, valida y normaliza el catalogo.

    Devuelve (productos, rechazados): productos es una lista de ProductoNutricional
    (solo los validos) y rechazados es el registro de productos apartados.
    """
    validos, rechazados = cargar_catalogo(ruta)
    return normalizar_catalogo(validos), rechazados

# Indice, busqueda y seleccion 

NO_DISPONIBLE = "no disponible"  # marca explicita de un nutriente sin dato (nunca se usa cero)


def indexar_productos(productos):
    """Arma un indice {codigo: ProductoNutricional} para buscar por codigo (texto).

    Levanta ErrorDatos si hay codigos repetidos: el indice no puede tener dos
    productos con el mismo codigo.
    """
    indice = {}
    for producto in productos:
        if producto.codigo in indice:
            raise ErrorDatos("codigo_duplicado", f"el código {producto.codigo} está repetido")
        indice[producto.codigo] = producto
    return indice


def buscar_producto(indice, codigo):
    """Devuelve el producto con ese codigo EAN; levanta ErrorConsulta si no se puede."""
    if not isinstance(codigo, str) or not PATRON_EAN.fullmatch(codigo):
        raise ErrorConsulta(f"'{codigo}' no es un código EAN válido (8 o 13 dígitos)")
    if codigo not in indice:
        raise ErrorConsulta(f"No hay ningún producto con el código {codigo}")
    return indice[codigo]


def seleccionar_por_codigos(indice, codigos):
    """Devuelve los productos de esos codigos, en el orden pedido y sin repetidos.

    Es todo o nada: si algun codigo no es valido o no existe, levanta ErrorConsulta
    indicando todos los problemas encontrados.
    """
    if not codigos:
        raise ErrorConsulta("No se indicó ningún código")
    elegidos = []
    problemas = []
    vistos = set()
    for codigo in codigos:
        try:
            producto = buscar_producto(indice, codigo)
        except ErrorConsulta as error:
            problemas.append(str(error))
            continue
        if codigo not in vistos:
            vistos.add(codigo)
            elegidos.append(producto)
    if problemas:
        raise ErrorConsulta("; ".join(problemas))
    return elegidos


#  Categorias 
# Regla de categorias:
#  - Un producto pertenece a TODAS las categorias de su lista (no hay una principal).
#  - Las categorias se comparan sin distinguir mayusculas, tildes ni espacios
#    sobrantes: "Lácteos", "lacteos" y " LÁCTEOS " son la misma categoria.


def _clave_categoria(texto):
    """Forma de comparar categorias: sin tildes, sin mayusculas y sin espacios sobrantes."""
    # NFD separa cada letra de su tilde (á -> a + tilde); luego se descartan las tildes
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn"
    )
    return sin_tildes.strip().casefold()


def listar_categorias(productos):
    """Devuelve [(categoria, cantidad_de_productos), ...] ordenado por nombre.

    Un producto cuenta una sola vez en cada una de sus categorias. Las categorias
    que solo difieren en mayusculas, tildes o espacios se agrupan; se muestra la
    primera forma encontrada.
    """
    nombres = {}      # clave -> nombre a mostrar
    cantidades = {}   # clave -> cantidad de productos
    for producto in productos:
        claves_del_producto = set()
        for categoria in producto.categorias:
            clave = _clave_categoria(categoria)
            nombres.setdefault(clave, categoria)
            claves_del_producto.add(clave)
        for clave in claves_del_producto:
            cantidades[clave] = cantidades.get(clave, 0) + 1
    return [(nombres[clave], cantidades[clave]) for clave in sorted(nombres)]


def seleccionar_por_categoria(productos, categoria):
    """Devuelve los productos que pertenecen a la categoria, en su orden original.

    Levanta ErrorConsulta, informando las categorias disponibles, si no hay coincidencias.
    """
    clave = _clave_categoria(categoria)
    elegidos = [
        p for p in productos
        if clave in {_clave_categoria(c) for c in p.categorias}
    ]
    if not elegidos:
        disponibles = ", ".join(nombre for nombre, _ in listar_categorias(productos))
        raise ErrorConsulta(
            f"No hay productos en la categoría '{categoria}'. "
            f"Categorías disponibles: {disponibles}"
        )
    return elegidos


# Comparacion


def nombre_de_columna(nutriente):
    """Nombre de la columna de un nutriente en la tabla, con su unidad: 'sodio (mg)'."""
    return f"{nutriente} ({UNIDAD_DE_COMPARACION[nutriente]})"


def comparar_etiquetas(productos, decimales=2):
    """Construye la tabla comparativa de nutrientes por cada 100 g.

    Devuelve una lista de filas (diccionarios), una por producto, con codigo, nombre
    y una columna por nutriente en su unidad de comparacion. Un nutriente sin dato
    queda marcado con NO_DISPONIBLE; nunca se reemplaza por cero.
    Los valores se redondean a 'decimales' solo en la tabla: los productos no se modifican.
    """
    if not productos:
        raise ErrorConsulta("No hay productos para comparar")
    tabla = []
    for producto in productos:
        fila = {"codigo": producto.codigo, "nombre": producto.nombre}
        for nutriente in UNIDAD_DE_COMPARACION:
            valor = producto.obtener(nutriente)
            if valor is None:
                fila[nombre_de_columna(nutriente)] = NO_DISPONIBLE
            else:
                fila[nombre_de_columna(nutriente)] = round(valor, decimales)
        tabla.append(fila)
    return tabla