# Diseño en detalle

Este documento amplía las secciones 6 y 8 del [README](../README.md).

## 1. Flujo del programa

| Etapa | Qué hace | Dónde |
|---|---|---|
| Leer | Convierte un CSV o un JSON en una lista de productos con una estructura común | `fuente_datos.py`, `fuente_csv.py`, `fuente_json.py`, `fuentes.py` |
| Inspeccionar y validar | Revisa el esquema del archivo y aplica las reglas a cada producto | `fuentes` (esquema), `validaciones.py` |
| Limpiar y transformar | Lleva cada nutriente a su unidad de comparación y a 100 g; los faltantes no se convierten en cero | `pipeline.py`, `conversiones.py` |
| Analizar | Indexa, busca, selecciona y compara | `pipeline.py` |
| Comunicar | Muestra la tabla, exporta resultados y guarda los rechazados | `main.py`, `salidas.py` |

## 2. Estructura de los datos

**Producto tal como se lee** (igual desde CSV o JSON; los valores están como se declaran en la etiqueta):

```json
{
  "codigo": "0012345678905",
  "nombre": "Cereal Avena Alfa",
  "categorias": "Cereales, Desayuno",
  "base": "porcion",
  "porcion_g": 40.0,
  "nutrientes": {
    "energia": {"valor": 627.6, "unidad": "kJ"},
    "sodio": {"valor": 0.06, "unidad": "g"}
  }
}
```

**Ficha normalizada** (por 100 g y en la unidad de comparación de cada nutriente):

```json
{
  "codigo": "0012345678905",
  "nombre": "Cereal Avena Alfa",
  "categorias": ["Cereales", "Desayuno"],
  "nutrientes": {"energia": 375.0, "sodio": 150.0}
}
```

## 3. Lectura de datos

- `FuenteDatos` (clase abstracta, `abc.ABC`) define el contrato: se crea con una ruta y `cargar()` devuelve la lista de productos. `FuenteCSV` y `FuenteJSON` lo implementan.
- El lector de CSV reconstruye la estructura anidada a partir de las columnas planas `<nutriente>_valor` y `<nutriente>_unidad`. Una celda vacía significa "no informado" y el nutriente no se agrega.
- Los códigos se leen como texto, para conservar los ceros iniciales.
- Los números se unifican como decimales, así un CSV y su JSON equivalente producen resultados idénticos.
- `crear_fuente(ruta)` elige la clase según la extensión (`.csv` o `.json`) y falla con un mensaje claro si el formato no es soportado.
- La lectura no valida el contenido, pero se detiene con un mensaje claro si el archivo no existe, está mal formado, le faltan columnas obligatorias o tiene un valor ilegible como número.

## 4. Reglas de validación

Cada regla levanta un `ErrorDatos` (`error_datos.py`) con un **tipo** y un **detalle**. `validar_catalogo()` atrapa el error, aparta el producto y lo registra, sin detener el programa. Si un producto incumple varias reglas, se registra la primera que falla, en este orden:

| Orden | Regla | Tipo de rechazo |
|---|---|---|
| 1 | El código es texto y tiene exactamente 8 o 13 dígitos | `codigo_invalido` |
| 2 | El nombre no está vacío | `nombre_faltante` |
| 3 | La base es `100g` o `porcion`; si es `porcion`, hay un `porcion_g` mayor que cero | `base_invalida` |
| 4 | Cada nutriente informado tiene un valor numérico y finito | `valor_invalido` |
| 5 | La unidad es admitida (energía: `kcal` o `kJ`; el resto: `g` o `mg`) | `unidad_desconocida` |
| 6 | El valor no es negativo | `valor_negativo` |
| 7 | El valor no supera el máximo posible | `fuera_de_rango` |
| 8 | El código no se repite en el catálogo | `codigo_duplicado` |

Decisiones:

- **Expresión regular:** `[0-9]{8}|[0-9]{13}`, aplicada con `fullmatch`. Valida solo la forma. Se usa `[0-9]` y no `\d` porque `\d` acepta dígitos de otros alfabetos.
- **Máximo posible:** ningún nutriente puede pesar más que el producto (100 g o 100000 mg cada 100 g, o el tamaño de la porción si la base es `porcion`), y la energía no puede superar 900 kcal (3766 kJ) cada 100 g, el equivalente a grasa pura.
- **Duplicados:** se conserva la primera aparición válida y se rechazan las siguientes. Si la primera fue rechazada por otra regla, una repetición válida posterior sí entra.
- **Nutrientes no contemplados** (que no están en la tabla de unidades) no se validan.
- **Registro de rechazados:** posición en el archivo, código, nombre, tipo y motivo.

## 5. Dominio y conversiones

- **`ProductoNutricional`** (`producto.py`) contiene la ficha normalizada. Su método `obtener(nutriente)` devuelve el valor por 100 g en la unidad de comparación, o `None` si no está disponible. Si el nombre no corresponde a un nutriente conocido, levanta un error, para que un error de tipeo no se confunda con un dato no disponible.
- **`normalizar_ficha()`** (`pipeline.py`) transforma un producto ya validado en una ficha homogénea. No redondea.
- **`preparar_catalogo()`** (`pipeline.py`) lee, valida y normaliza; devuelve los productos válidos y el registro de rechazados.

| Nutriente | Unidad de comparación (por 100 g) |
|---|---|
| Energía | kcal |
| Grasas, grasas saturadas, carbohidratos, azúcares, proteínas | g |
| Sodio | mg |

Conversiones (`conversiones.py`): 1 kcal = 4,184 kJ; 1 g = 1000 mg; base `porcion`: valor × 100 / `porcion_g`. Las unidades incompatibles (por ejemplo, de g a kcal) levantan un error.

## 6. Consulta y comparación

| Función (`pipeline.py`) | Qué hace |
|---|---|
| `indexar_productos(productos)` | Arma un índice `{código: ProductoNutricional}`; levanta `ErrorDatos` si hay códigos repetidos |
| `buscar_producto(indice, codigo)` | Devuelve el producto con ese EAN; error claro si el código no es válido o no existe |
| `listar_categorias(productos)` | Devuelve las categorías con su cantidad de productos, ordenadas por nombre |
| `seleccionar_por_categoria(productos, categoria)` | Devuelve los productos de una categoría; error claro, con las categorías disponibles, si no hay coincidencias |
| `seleccionar_por_codigos(indice, codigos)` | Devuelve los productos de esos EAN, en el orden pedido y sin repetidos; es todo o nada e informa todos los problemas juntos |
| `comparar_etiquetas(productos)` | Construye la tabla comparativa por 100 g: una fila por producto y una columna por nutriente |

**Regla de categorías:** un producto pertenece a **todas** las categorías de su lista (no hay una principal). Se comparan sin distinguir mayúsculas, tildes ni espacios sobrantes: `Lácteos`, `lacteos` y ` LÁCTEOS ` son la misma. Un producto cuenta una sola vez por categoría.

**Errores:** `ErrorConsulta` (`error_consulta.py`) se usa para las consultas que no se pueden resolver (código inválido o inexistente, categoría sin productos, nada para comparar). Se distingue de `ErrorDatos`, que corresponde a datos del catálogo que incumplen las reglas.

**Tabla comparativa:** cada fila es un diccionario con `codigo`, `nombre` y una columna por nutriente con su unidad (por ejemplo `energia (kcal)` o `sodio (mg)`). Los nutrientes sin dato se marcan con `no disponible`, nunca con cero; un cero declarado se muestra como `0.0`. Los valores se redondean a 2 decimales solo en la tabla.

## 7. Salidas y menú

- `salidas.py` arma la tabla para la pantalla (encabezados cortos, leyenda de unidades y `N/D` para los datos no disponibles), exporta a CSV o JSON dentro de `outputs/` (crea la carpeta si falta) y guarda `outputs/rechazados.csv`.
- `main.py` solo conversa con quien usa el programa: pide datos, llama a `pipeline.py` y muestra el resultado.
- Se atrapan únicamente los errores previstos: al leer el archivo (`FileNotFoundError`, `ValueError`), en las consultas (`ErrorConsulta`) y al guardar archivos (`OSError`). Cualquier otro error se muestra completo, sin ocultarse.
- Al exportar, el archivo siempre queda dentro de `outputs/`, aunque se escriba una ruta.

## 8. Pruebas

Se usa `unittest`, de la biblioteca estándar. Comando: `python -m unittest discover -s tests -v`.

| Archivo (`tests/`) | Qué cubre |
|---|---|
| `test_fuentes.py` | Lectura de CSV y JSON, estructura común, selección de la fuente y errores de archivo |
| `test_validaciones.py` | Códigos EAN válidos e inválidos, cada regla de rechazo, duplicados y conservación de los válidos |
| `test_conversiones.py` | Conversiones con resultado conocido, ida y vuelta, base de 100 g |
| `test_producto.py` | `ProductoNutricional` y el tratamiento de nutrientes no disponibles |
| `test_normalizacion.py` | Fichas normalizadas, faltantes y equivalencia entre CSV y JSON |
| `test_consultas.py` | Índice, búsqueda, categorías, selección por códigos y comparación |
| `test_salidas.py` | Formato en pantalla, exportación, mismos resultados con la misma entrada y rechazados |
| `test_main.py` | Flujo del menú con respuestas simuladas, incluidos los errores |
| `test_pipeline.py` | Flujo completo con la muestra de `data/` |