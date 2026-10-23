"""Validaciones del catalogo: deciden que productos entran y cuales se rechazan.

Cada regla levanta un ErrorDatos con el tipo y el detalle del problema.
validar_catalogo() captura ese error, aparta el producto y lo registra, sin
detener el programa. Si un producto incumple varias reglas, se registra la
primera que falla (en el orden de validar_producto).
"""

import math
import re
from error_datos import ErrorDatos

PATRON_EAN = re.compile(r"[0-9]{8}|[0-9]{13}")
BASES_ADMITIDAS = ("100g", "porcion")
UNIDADES_ADMITIDAS = {
    "energia": ("kcal", "kJ"),
    "grasas": ("g", "mg"),
    "grasas_saturadas": ("g", "mg"),
    "carbohidratos": ("g", "mg"),
    "azucares": ("g", "mg"),
    "proteinas": ("g", "mg"),
    "sodio": ("g", "mg"),
}

# Maximo posible cada 100 g de producto, en cada unidad.
# Ningun nutriente puede pesar mas que el producto; y la grasa pura aporta
# unas 9 kcal por gramo, de ahi el tope de 900 kcal (3766 kJ) por 100 g.
LIMITE_POR_100G = {"g": 100, "mg": 100000, "kcal": 900, "kJ": 3766}


def _es_numero(valor):
    """True si es un numero (int o float, no bool) y no es NaN ni infinito."""
    return (
        isinstance(valor, (int, float))
        and not isinstance(valor, bool)
        and math.isfinite(valor)
    )


def validar_codigo(codigo):
    if not isinstance(codigo, str):
        raise ErrorDatos(
            "codigo_invalido",
            f"el código debe ser texto y es de tipo {type(codigo).__name__}",
        )
    if not PATRON_EAN.fullmatch(codigo):
        raise ErrorDatos(
            "codigo_invalido",
            f"el código '{codigo}' no está formado por exactamente 8 o 13 dígitos",
        )


def validar_nombre(nombre):
    if not isinstance(nombre, str) or not nombre.strip():
        raise ErrorDatos("nombre_faltante", "el producto no tiene nombre")


def validar_base(producto):
    """Valida la base de referencia y devuelve a cuantos gramos se refieren los valores."""
    base = producto.get("base")
    if base not in BASES_ADMITIDAS:
        raise ErrorDatos("base_invalida", f"la base '{base}' no es '100g' ni 'porcion'")
    if base == "100g":
        return 100
    porcion = producto.get("porcion_g")
    if not _es_numero(porcion) or porcion <= 0:
        raise ErrorDatos(
            "base_invalida",
            "la base es 'porcion' pero falta un porcion_g numérico mayor que cero",
        )
    return porcion


def validar_nutrientes(producto, referencia_g):
    nutrientes = producto.get("nutrientes")
    if not isinstance(nutrientes, dict):
        raise ErrorDatos("valor_invalido", "los nutrientes no tienen el formato esperado")

    for nombre, unidades in UNIDADES_ADMITIDAS.items():
        dato = nutrientes.get(nombre)
        if dato is None:
            continue  # no informado: es valido (y no es lo mismo que cero)

        valor = dato.get("valor") if isinstance(dato, dict) else None
        if not _es_numero(valor):
            raise ErrorDatos("valor_invalido", f"{nombre}: el valor '{valor}' no es un número")

        unidad = dato.get("unidad")
        if unidad not in unidades:
            raise ErrorDatos(
                "unidad_desconocida",
                f"{nombre}: la unidad '{unidad}' no está admitida (se admite: {', '.join(unidades)})",
            )

        if valor < 0:
            raise ErrorDatos("valor_negativo", f"{nombre}: el valor {valor:g} es negativo")

        limite = LIMITE_POR_100G[unidad] * referencia_g / 100
        if valor > limite:
            raise ErrorDatos(
                "fuera_de_rango",
                f"{nombre}: {valor:g} {unidad} supera el máximo posible ({limite:g} {unidad})",
            )


def validar_producto(producto):
    """Aplica las reglas de un producto; levanta ErrorDatos con la primera que falle."""
    validar_codigo(producto.get("codigo"))
    validar_nombre(producto.get("nombre"))
    referencia_g = validar_base(producto)
    validar_nutrientes(producto, referencia_g)


def validar_catalogo(productos):
    """Separa los productos validos de los rechazados.

    Devuelve (validos, rechazados). Cada rechazado es un diccionario con la
    posicion del producto en el archivo (empieza en 1), su codigo, su nombre,
    el tipo de error y el motivo.

    Si un codigo se repite, se conserva la primera aparicion valida y se
    rechazan las siguientes.
    """
    validos = []
    rechazados = []
    codigos_vistos = set()

    for posicion, producto in enumerate(productos, start=1):
        try:
            validar_producto(producto)
            codigo = producto["codigo"]
            if codigo in codigos_vistos:
                raise ErrorDatos("codigo_duplicado", f"el código {codigo} ya apareció antes")
        except ErrorDatos as error:
            rechazados.append({
                "posicion": posicion,
                "codigo": producto.get("codigo"),
                "nombre": producto.get("nombre"),
                "tipo": error.tipo,
                "motivo": error.detalle,
            })
        else:
            codigos_vistos.add(codigo)
            validos.append(producto)

    return validos, rechazados