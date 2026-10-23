"""Salidas del programa: formato de tablas para la pantalla y archivos en outputs/.

La carpeta de salidas se crea automaticamente cuando hace falta.
"""

import csv
import json
from pathlib import Path

from error_consulta import ErrorConsulta
from pipeline import NO_DISPONIBLE

CARPETA_SALIDAS = Path(__file__).resolve().parent.parent / "outputs"
COLUMNAS_RECHAZADOS = ["posicion", "codigo", "nombre", "tipo", "motivo"]

# Encabezados cortos para la pantalla (las unidades van en la leyenda).
# Los archivos exportados conservan los nombres completos de las columnas.
ENCABEZADOS_PANTALLA = {
    "codigo": "Código",
    "nombre": "Nombre",
    "energia (kcal)": "Energía",
    "grasas (g)": "Grasas",
    "grasas_saturadas (g)": "Satur.",
    "carbohidratos (g)": "Carbo.",
    "azucares (g)": "Azúcar",
    "proteinas (g)": "Prot.",
    "sodio (mg)": "Sodio",
}
LEYENDA = (
    "Valores por cada 100 g (energía en kcal, sodio en mg, el resto en g). "
    "N/D = no disponible."
)


def formatear_tabla(tabla):
    """Devuelve la tabla comparativa como texto con columnas alineadas.

    Solo cambia la presentacion: la marca NO_DISPONIBLE se muestra como 'N/D'
    y la tabla original no se modifica.
    """
    if not tabla:
        raise ErrorConsulta("No hay una tabla para mostrar")
    columnas = list(tabla[0])
    encabezados = [ENCABEZADOS_PANTALLA.get(c, c) for c in columnas]
    filas = [
        ["N/D" if fila[c] == NO_DISPONIBLE else str(fila[c]) for c in columnas]
        for fila in tabla
    ]
    anchos = [
        max(len(encabezados[i]), *(len(fila[i]) for fila in filas))
        for i in range(len(columnas))
    ]
    lineas = [
        "  ".join(texto.ljust(ancho) for texto, ancho in zip(encabezados, anchos)),
        "  ".join("-" * ancho for ancho in anchos),
    ]
    for fila in filas:
        lineas.append("  ".join(texto.ljust(ancho) for texto, ancho in zip(fila, anchos)))
    lineas.append("")
    lineas.append(LEYENDA)
    return "\n".join(lineas)


def formatear_resumen(productos, rechazados):
    """Resumen de la lectura: registros leidos, validos y rechazados (por tipo)."""
    por_tipo = {}
    for rechazo in rechazados:
        por_tipo[rechazo["tipo"]] = por_tipo.get(rechazo["tipo"], 0) + 1
    detalle = ", ".join(f"{tipo}: {cantidad}" for tipo, cantidad in sorted(por_tipo.items()))
    linea_rechazados = f"  Rechazados: {len(rechazados)}"
    if detalle:
        linea_rechazados += f" ({detalle})"
    return "\n".join([
        f"Registros leídos: {len(productos) + len(rechazados)}",
        f"  Válidos: {len(productos)}",
        linea_rechazados,
    ])


def _preparar_carpeta(ruta):
    Path(ruta).parent.mkdir(parents=True, exist_ok=True)


def guardar_tabla_csv(tabla, ruta):
    _preparar_carpeta(ruta)
    with open(ruta, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(tabla[0]))
        escritor.writeheader()
        escritor.writerows(tabla)


def guardar_tabla_json(tabla, ruta):
    _preparar_carpeta(ruta)
    with open(ruta, "w", encoding="utf-8") as archivo:
        json.dump(tabla, archivo, ensure_ascii=False, indent=2)


# Cada extension de archivo se asocia con la funcion que sabe escribirla
ESCRITORES = {".csv": guardar_tabla_csv, ".json": guardar_tabla_json}


def exportar_tabla(tabla, ruta):
    """Guarda la tabla comparativa en CSV o JSON segun la extension de la ruta.

    Crea las carpetas que falten y devuelve la ruta escrita.
    """
    if not tabla:
        raise ErrorConsulta("No hay una tabla para exportar")
    ruta = Path(ruta)
    escritor = ESCRITORES.get(ruta.suffix.lower())
    if escritor is None:
        raise ErrorConsulta(
            f"Formato no soportado: '{ruta.suffix}'. "
            "Use un nombre de archivo terminado en .csv o .json"
        )
    escritor(tabla, ruta)
    return ruta


def guardar_rechazados(rechazados, ruta):
    """Guarda el registro de productos rechazados, con su motivo, en un CSV.

    Si no hubo rechazados, el archivo queda solo con el encabezado.
    """
    _preparar_carpeta(ruta)
    with open(ruta, "w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=COLUMNAS_RECHAZADOS)
        escritor.writeheader()
        escritor.writerows(rechazados)