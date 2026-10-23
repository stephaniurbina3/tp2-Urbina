"""Conversion de unidades y de bases de referencia.

La unidad de comparacion de cada nutriente es la unidad en la que se muestran
y comparan todos los productos, siempre por cada 100 g.
"""

# Unidad de comparacion de cada nutriente (valores por 100 g)
UNIDAD_DE_COMPARACION = {
    "energia": "kcal",
    "grasas": "g",
    "grasas_saturadas": "g",
    "carbohidratos": "g",
    "azucares": "g",
    "proteinas": "g",
    "sodio": "mg",
}

# Cuantas unidades de destino hay en 1 unidad de origen
FACTORES = {
    ("kcal", "kJ"): 4.184,      # 1 kcal = 4,184 kJ
    ("kJ", "kcal"): 1 / 4.184,
    ("g", "mg"): 1000,          # 1 g = 1000 mg
    ("mg", "g"): 1 / 1000,
}


def convertir(valor, desde, hacia):
    """Convierte un valor entre unidades (kcal y kJ, o g y mg).

    Levanta ValueError si las unidades no son compatibles.
    """
    if desde == hacia:
        return valor
    factor = FACTORES.get((desde, hacia))
    if factor is None:
        raise ValueError(f"No se puede convertir de '{desde}' a '{hacia}'")
    return valor * factor


def a_base_100g(valor, base, porcion_g=None):
    """Lleva un valor declarado a la base de 100 g.

    Si la base es '100g' el valor no cambia; si es 'porcion', se escala segun
    el tamaño de la porcion.
    """
    if base == "100g":
        return valor
    if base == "porcion":
        if porcion_g is None or porcion_g <= 0:
            raise ValueError("la base 'porcion' necesita un porcion_g mayor que cero")
        return valor * 100 / porcion_g
    raise ValueError(f"Base desconocida: '{base}'")