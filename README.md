# Comparador de etiquetas nutricionales

**Autor:** Stephani Urbina
**Materia:** Programación Orientada a Datos · UCA · Licenciatura en Ciencia de Datos · 2026
**Trabajo:** TP2 individual

## 1. Problema, usuario y solución propuesta

**Problema.** Comparar las etiquetas nutricionales de varios productos exige localizar cada ficha y homogeneizar unidades (g, mg, kcal, kJ) y bases de referencia (por 100 g o por porción). Además, cuando un nutriente falta en la ficha puede confundirse con cero, y eso produce comparaciones incorrectas: "no informado" no es lo mismo que "no contiene".

**Usuario.** Una persona que quiere comparar productos envasados (consumidor, estudiante de nutrición, analista) y necesita una tabla homogénea y confiable para decidir o analizar.

**Solución.** Un programa en Python con un catálogo consultable de productos, cargado desde archivos CSV o JSON equivalentes. Quien lo usa elige un código o una categoría y obtiene una comparación de nutrientes por cada 100 g, que puede exportar.

## 2. Funcionalidades y modo de uso

Operaciones previstas para la primera versión, a través de un menú interactivo en la terminal:

1. Listar las categorías disponibles y cuántos productos tiene cada una.
2. Buscar un producto por código de barras (EAN de 8 o 13 dígitos) y mostrar su ficha.
3. Comparar los productos de una categoría.
4. Comparar un grupo de productos indicando sus códigos.
5. Exportar la comparación en CSV o JSON.

**Resultado e interpretación.** La comparación es una tabla con una fila por producto y una columna por nutriente, todo expresado por 100 g y en una unidad común. Los valores **no disponibles** se marcan explícitamente y nunca se reemplazan por cero. Cada valor debe leerse como "lo declarado en la ficha, convertido a la unidad de comparación"; no se verifica contra el producto real.

_Instrucciones de uso con ejemplos: pendiente._

## 3. Alcance de la primera versión

**Incluye**
- Carga de productos desde archivos CSV y JSON equivalentes.
- Validación del código (patrón de 8 o 13 dígitos) y de los valores de la ficha.
- Conversión de unidades y de bases de referencia a 100 g.
- Búsqueda por código y selección por categoría, admitiendo varias categorías por producto.
- Registro de los productos rechazados y su motivo.
- Exportación de la comparación.
- Pruebas automatizadas y documentación.

**Queda fuera**
- Interfaz web o gráfica.
- Descarga automática desde la API de Open Food Facts.
- Verificación del dígito de control del EAN: solo se valida el patrón de dígitos.
- Puntajes de salubridad (por ejemplo, Nutri-Score) y recomendaciones.
- Aprendizaje automático.

## 4. Datos: fuente, licencia y unidad de análisis

- **Fuente de referencia:** [Open Food Facts](https://world.openfoodfacts.org/data). El volcado completo pesa varios GB y no se incluye en el repositorio.
- **Muestra incluida:** por problemas con la API de Open Food Facts, `data/productos.csv` y `data/productos.json` contienen una muestra de **datos ficticios** con el mismo formato que tendrían los datos reales. Se genera con `scripts/generar_muestra`. Procedencia, unidades y criterios de selección: ver `data/README.md`.
- **Licencia de los datos de referencia:** Open Database License (ODbL) para la base y Database Contents License para los contenidos; se cita la fuente.
- **Unidad de análisis:** un producto, identificado por su código de barras.

## 5. Instalación y ejecución

**Pruebas** (desde la raíz del repositorio):

```text
python -m unittest discover tests
```

También se pueden ejecutar desde VS Code, en el panel Testing.

_Pendiente: comandos para ejecutar la aplicación (se completarán cuando exista `main.py`)._

## 6. Organización del código

Estructura actual (se irá completando):

```text
tp2-apellido/
|-- README.md
|-- requirements.txt
|-- .gitignore
|-- src/        código de la aplicación: funciones y clases agrupadas por tema
|   |-- fuente_datos.py   clase abstracta FuenteDatos
|   |-- fuente_csv.py     clase FuenteCSV
|   |-- fuente_json.py    clase FuenteJSON
|   '-- fuentes.py        selección de la fuente según la extensión
|-- tests/
|   '-- test_fuentes.py   pruebas de lectura de CSV y JSON
|-- scripts/    utilidades para preparar los datos
|-- data/       muestra de datos y su procedencia
'-- outputs/    resultados generados (no se versionan)
```

`src/` no es un paquete (no tiene `__init__.py`): los módulos se importan por su nombre, por ejemplo `from fuentes import crear_fuente`. Cada clase está en su propio archivo.

Diseño previsto:

| Elemento | Responsabilidad | Estado |
|---|---|---|
| `FuenteDatos` | Clase abstracta con `cargar()`; la implementan `FuenteCSV` y `FuenteJSON` | Implementado |
| `FuenteCSV` / `FuenteJSON` | Leen el archivo y devuelven la misma estructura de productos | Implementado |
| `crear_fuente()` | Elige la fuente según la extensión del archivo | Implementado |
| `normalizar_ficha()` | Extrae los campos anidados de un registro y convierte las unidades | Pendiente |
| `indexar_productos()` | Construye el índice por código, conservando los códigos como texto | Pendiente |
| `buscar_producto()` | Devuelve la ficha de un código | Pendiente |
| `comparar_etiquetas()` | Construye la tabla homogénea con marcas de no disponible | Pendiente |
| `ProductoNutricional` | Clase que contiene la ficha y entrega cada nutriente en la unidad de comparación | Pendiente |

**Expresión regular prevista:** validar que el código tenga exactamente 8 o 13 dígitos. Esta validación **no comprueba el dígito de control** del EAN.

### 6.1 Decisiones de diseño: lectura de datos

- **Una clase por archivo.** `FuenteDatos`, `FuenteCSV` y `FuenteJSON` están en archivos separados. `fuentes.py` solo contiene funciones.
- **Clase abstracta.** `FuenteDatos` usa `abc.ABC` y declara el método abstracto `cargar()`. Cada formato lo implementa a su manera, y el resto del programa llama a `cargar()` sin saber si el archivo es CSV o JSON (polimorfismo).
- **Misma estructura de salida.** Las dos fuentes devuelven una lista de diccionarios, uno por producto, con `codigo`, `nombre`, `categorias`, `base`, `porcion_g` (si corresponde) y `nutrientes`. Por eso los dos formatos son intercambiables.
- **Código como texto.** El código de barras se lee siempre como `str` para conservar los ceros iniciales.
- **Nutrientes no informados.** Una celda vacía del CSV no se convierte en cero: el nutriente simplemente no aparece en el diccionario del producto.
- **Selección por extensión.** `crear_fuente(ruta)` elige `FuenteCSV` o `FuenteJSON` según la extensión (sin distinguir mayúsculas) y falla con un mensaje claro si el formato no es compatible.
- **Solo lectura.** Esta etapa no valida códigos, rangos ni duplicados, y no convierte unidades: eso se hace en una etapa posterior.
- **Errores claros.** Archivo inexistente, columnas faltantes, números inválidos (con el número de fila), JSON mal formado o con estructura incorrecta se informan con un mensaje que dice qué falló y dónde.
- **Biblioteca estándar.** Se usan `csv` y `json`, que alcanzan para este caso.
- **Pruebas.** `tests/test_fuentes.py` prueba cada fuente con archivos temporales, la selección de la fuente, que la clase abstracta no se pueda instanciar y la equivalencia entre `data/productos.csv` y `data/productos.json`.

### Reglas de validación (`src/validaciones.py`)

Cada regla levanta un `ErrorDatos` (definido en `src/error_datos.py`) con un **tipo** y un **detalle**. `validar_catalogo()` atrapa el error, aparta el producto y lo registra, sin detener el programa. `cargar_catalogo()` (en `src/pipeline.py`) integra la lectura con la validación y devuelve la lista de productos válidos y la de rechazados.

Si un producto incumple varias reglas, se registra la primera que falla, en este orden:

| Orden | Regla | Tipo de rechazo |
|---|---|---|
| 1 | El código es texto y tiene exactamente 8 o 13 dígitos | `codigo_invalido` |
| 2 | El nombre no está vacío | `nombre_faltante` |
| 3 | La base es `100g` o `porcion`; si es `porcion`, hay un `porcion_g` mayor que cero | `base_invalida` |
| 4 | Cada nutriente informado tiene un valor numérico y finito | `valor_invalido` |
| 5 | La unidad es una de las admitidas (energía: `kcal` o `kJ`; el resto: `g` o `mg`) | `unidad_desconocida` |
| 6 | El valor no es negativo | `valor_negativo` |
| 7 | El valor no supera el máximo posible (ver abajo) | `fuera_de_rango` |
| 8 | El código no se repite en el catálogo | `codigo_duplicado` |

**Decisiones:**
- **Expresión regular del código:** `[0-9]{8}|[0-9]{13}`, aplicada con `fullmatch`. Valida solo la forma (8 o 13 dígitos ASCII). No comprueba el dígito de control del EAN ni que el producto exista. Se usa `[0-9]` y no `\d` porque `\d` acepta dígitos de otros alfabetos.
- **Códigos como texto:** un código que no es texto se rechaza, para no perder silenciosamente los ceros iniciales.
- **Rangos:** ningún nutriente puede pesar más que el producto: 100 g (o 100000 mg) cada 100 g, o el tamaño de la porción si la base es `porcion`. La energía no puede superar 900 kcal (3766 kJ) cada 100 g, el equivalente a grasa pura.
- **Valores no informados:** un nutriente ausente es válido, y un cero declarado también.
- **Nutrientes no contemplados:** los que no están en la tabla de unidades no se validan.
- **Duplicados:** se conserva la primera aparición válida y se rechazan las siguientes. Si la primera fue rechazada por otra regla, una repetición válida posterior sí entra.
- **Registro de rechazados:** cada rechazo guarda la posición en el archivo, el código, el nombre, el tipo y el motivo. El programa continúa con los productos válidos.

## 7. Ejemplo de resultado

_Pendiente: se agregará una salida real cuando la aplicación funcione._

## 8. Decisiones de limpieza

Decisiones previstas (se confirmarán al implementar):

- Los códigos se leen y se guardan como texto para conservar los ceros iniciales.
- Un nutriente ausente se registra como _no disponible_; no se reemplaza por cero.
- Las unidades se convierten a una unidad común de comparación y todo se expresa por 100 g.
- Si un producto tiene varias categorías, se aplica una regla de selección explícita.
- Los registros inválidos se apartan y se registran con su motivo, sin detener el programa.

## 9. Interpretación y limitaciones

_Pendiente: se completará al finalizar. Limitaciones ya conocidas: no se verifica el dígito de control del EAN, se trabaja con una muestra y no con la base completa, y la calidad de la comparación depende de la calidad de las fichas de origen._
