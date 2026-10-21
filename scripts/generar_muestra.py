"""Genera la muestra SIMULADA de productos que usa el proyecto.

Uso :
    python scripts/generar_muestra.py

Los datos son inventados: no son productos reales. Con la misma semilla se
obtiene siempre la misma muestra. Se guarda en dos formatos equivalentes:
  - data/productos.json (nutrientes anidados dentro de "nutrientes")
  - data/productos.csv  (nutrientes en columnas planas)

Cada ficha imita una etiqueta: los valores estan "como se declaran" (con
distintas unidades y bases de referencia), no normalizados. Un nutriente no
informado queda ausente en el JSON y como celda vacia en el CSV; nunca se
reemplaza por cero.
"""

import csv
import json
import random
from pathlib import Path

#Configuracion 
SEMILLA = 2026
POR_CATEGORIA = 15  # 4 categorias x 15 = 60 productos
CARPETA_DATA = Path(__file__).resolve().parent.parent / "data"
MARCAS = ["Alfa", "Beta", "Gamma", "Delta", "Sigma"]  # marcas ficticias
NUTRIENTES = [
    "energia", "grasas", "grasas_saturadas", "carbohidratos",
    "azucares", "proteinas", "sodio",
]

# Probabilidades que simulan como se declaran las etiquetas
PROB_PORCION = 0.30           # declarado por porcion en vez de por 100 g
PROB_KJ = 0.40                # energia en kJ en vez de kcal
PROB_SODIO_EN_G = 0.20        # sodio en g en vez de mg
PROB_CATEGORIA_EXTRA = 0.30   # producto con una segunda categoria
PROB_FALTANTE = {             # probabilidad de que el nutriente no este informado
    "energia": 0.05, "grasas": 0.08, "grasas_saturadas": 0.20,
    "carbohidratos": 0.08, "azucares": 0.15, "proteinas": 0.08, "sodio": 0.15,
}

# Rangos por 100 g (grasas, saturadas, carbohidratos, azucares y proteinas en g;
# sodio en mg) y porciones habituales en g
PERFILES = {
    "Cereales": {
        "producto": "Cereal",
        "tipos": ["Copos de maíz", "Avena", "Granola", "Aros", "Trigo inflado", "Muesli"],
        "extras": ["Desayuno", "Integrales"],
        "porciones": [30, 40],
        "grasas": (1, 9), "saturadas": (0.3, 4), "carbohidratos": (55, 75),
        "azucares": (3, 30), "proteinas": (5, 11), "sodio_mg": (50, 500),
    },
    "Yogures": {
        "producto": "Yogur",
        "tipos": ["Natural", "Frutilla", "Vainilla", "Durazno", "Bebible", "Griego"],
        "extras": ["Lácteos", "Postres"],
        "porciones": [125, 170],
        "grasas": (0, 4), "saturadas": (0, 3), "carbohidratos": (5, 18),
        "azucares": (4, 16), "proteinas": (3, 6), "sodio_mg": (40, 90),
    },
    "Jugos": {
        "producto": "Jugo",
        "tipos": ["Naranja", "Manzana", "Multifruta", "Pomelo", "Durazno", "Ananá"],
        "extras": ["Bebidas", "Sin conservantes"],
        "porciones": [200, 250],
        "grasas": (0, 0.5), "saturadas": (0, 0.2), "carbohidratos": (8, 13),
        "azucares": (7, 12), "proteinas": (0, 1), "sodio_mg": (0, 30),
    },
    "Galletitas": {
        "producto": "Galletitas",
        "tipos": ["Dulces", "De agua", "Rellenas", "Integrales", "De limón", "Con chips"],
        "extras": ["Snacks", "Desayuno"],
        "porciones": [30, 40],
        "grasas": (12, 22), "saturadas": (4, 12), "carbohidratos": (55, 65),
        "azucares": (5, 30), "proteinas": (5, 9), "sodio_mg": (200, 700),
    },
}


def digitos_al_azar(rng, cantidad):
    return "".join(rng.choice("0123456789") for _ in range(cantidad))


def generar_codigo(rng, usados):
    """Inventa un codigo de 13 u 8 digitos, distinto de los ya usados.

    Se guarda como texto para conservar los ceros iniciales. No se calcula el
    digito de control: los codigos son ficticios.
    """
    while True:
        tipo = rng.choices(["ean13", "ean13_cero", "ean8"], weights=[70, 20, 10])[0]
        if tipo == "ean13":
            codigo = "779" + digitos_al_azar(rng, 10)
        elif tipo == "ean13_cero":
            codigo = "0" + digitos_al_azar(rng, 12)
        else:
            codigo = digitos_al_azar(rng, 8)
        if codigo not in usados:
            usados.add(codigo)
            return codigo


def valores_por_100g(rng, perfil):
    """Valores 'verdaderos' por 100 g (energia en kcal, sodio en mg, resto en g)."""
    grasas = rng.uniform(*perfil["grasas"])
    saturadas = min(rng.uniform(*perfil["saturadas"]), grasas)
    carbohidratos = rng.uniform(*perfil["carbohidratos"])
    azucares = min(rng.uniform(*perfil["azucares"]), carbohidratos)
    proteinas = rng.uniform(*perfil["proteinas"])
    sodio_mg = rng.uniform(*perfil["sodio_mg"])
    energia_kcal = 4 * carbohidratos + 4 * proteinas + 9 * grasas
    return {
        "energia": energia_kcal, "grasas": grasas, "grasas_saturadas": saturadas,
        "carbohidratos": carbohidratos, "azucares": azucares,
        "proteinas": proteinas, "sodio": sodio_mg,
    }


def declarar(rng, perfil, valores):
    """Pasa los valores a la forma en que los declararia una etiqueta.

    Devuelve (base, porcion_g, nutrientes). Aca se decide la unidad y la base de
    cada producto; despues habra que volver a llevar todo a 100 g.
    """
    if rng.random() < PROB_PORCION:
        base = "porcion"
        porcion_g = rng.choice(perfil["porciones"])
        factor = porcion_g / 100
    else:
        base, porcion_g, factor = "100g", None, 1

    nutrientes = {}

    # Energia: en kJ o en kcal
    if rng.random() < PROB_KJ:
        nutrientes["energia"] = {"valor": round(valores["energia"] * 4.184 * factor), "unidad": "kJ"}
    else:
        nutrientes["energia"] = {"valor": round(valores["energia"] * factor), "unidad": "kcal"}

    # Nutrientes en gramos
    for nombre in ["grasas", "grasas_saturadas", "carbohidratos", "azucares", "proteinas"]:
        nutrientes[nombre] = {"valor": round(valores[nombre] * factor, 1), "unidad": "g"}

    # Sodio: en mg o en g
    sodio_mg = valores["sodio"] * factor
    if rng.random() < PROB_SODIO_EN_G:
        nutrientes["sodio"] = {"valor": round(sodio_mg / 1000, 3), "unidad": "g"}
    else:
        nutrientes["sodio"] = {"valor": round(sodio_mg), "unidad": "mg"}

    # Nutrientes no informados: se quitan (no se ponen en cero)
    for nombre in NUTRIENTES:
        if rng.random() < PROB_FALTANTE[nombre]:
            del nutrientes[nombre]

    return base, porcion_g, nutrientes


def generar_productos(rng):
    productos = []
    usados = set()
    for categoria, perfil in PERFILES.items():
        combinaciones = [(tipo, marca) for tipo in perfil["tipos"] for marca in MARCAS]
        for tipo, marca in rng.sample(combinaciones, POR_CATEGORIA):
            categorias = categoria
            if rng.random() < PROB_CATEGORIA_EXTRA:
                categorias += ", " + rng.choice(perfil["extras"])
            valores = valores_por_100g(rng, perfil)
            base, porcion_g, nutrientes = declarar(rng, perfil, valores)
            ficha = {
                "codigo": generar_codigo(rng, usados),
                "nombre": f"{perfil['producto']} {tipo} {marca}",
                "categorias": categorias,
                "base": base,
            }
            if porcion_g is not None:
                ficha["porcion_g"] = porcion_g
            ficha["nutrientes"] = nutrientes
            productos.append(ficha)
    return productos


def agregar_defectos(productos):
    """Introduce 4 errores A PROPOSITO, para que el flujo de validacion los detecte.

    Las posiciones suponen POR_CATEGORIA = 15 (60 productos).
    """
    # 1) codigo con 7 digitos (no es EAN-8 ni EAN-13)
    productos[3]["codigo"] = productos[3]["codigo"][:7]
    # 2) valor negativo
    productos[20]["nutrientes"]["azucares"] = {"valor": -4.0, "unidad": "g"}
    # 3) valor imposible: 140 g de grasa cada 100 g
    productos[37]["base"] = "100g"
    productos[37].pop("porcion_g", None)
    productos[37]["nutrientes"]["grasas"] = {"valor": 140.0, "unidad": "g"}
    # 4) codigo duplicado
    productos[50]["codigo"] = productos[51]["codigo"]


def guardar_json(productos, ruta):
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(productos, archivo, ensure_ascii=False, indent=2)


def guardar_csv(productos, ruta):
    columnas = ["codigo", "nombre", "categorias", "base", "porcion_g"]
    for nutriente in NUTRIENTES:
        columnas += [nutriente + "_valor", nutriente + "_unidad"]
    with open(ruta, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        for ficha in productos:
            fila = {
                "codigo": ficha["codigo"],
                "nombre": ficha["nombre"],
                "categorias": ficha["categorias"],
                "base": ficha["base"],
                "porcion_g": ficha.get("porcion_g", ""),
            }
            for nutriente, dato in ficha["nutrientes"].items():
                fila[nutriente + "_valor"] = dato["valor"]
                fila[nutriente + "_unidad"] = dato["unidad"]
            escritor.writerow(fila)  # lo que falta queda como celda vacia


def mostrar_resumen(productos):
    total = len(productos)
    print(f"Total: {total} productos")
    print(f"  codigos distintos: {len({p['codigo'] for p in productos})}")
    por_porcion = sum(1 for p in productos if p["base"] == "porcion")
    print(f"  declarados por porcion: {por_porcion}; por 100 g: {total - por_porcion}")
    for nutriente in NUTRIENTES:
        informados = sum(1 for p in productos if nutriente in p["nutrientes"])
        print(f"  {nutriente}: informado en {informados} de {total}")


def main():
    rng = random.Random(SEMILLA)
    productos = generar_productos(rng)
    agregar_defectos(productos)
    productos.sort(key=lambda ficha: ficha["codigo"])  # orden fijo por codigo
    mostrar_resumen(productos)
    CARPETA_DATA.mkdir(exist_ok=True)
    guardar_json(productos, CARPETA_DATA / "productos.json")
    guardar_csv(productos, CARPETA_DATA / "productos.csv")
    print("Archivos guardados en", CARPETA_DATA)


if __name__ == "__main__":
    main()