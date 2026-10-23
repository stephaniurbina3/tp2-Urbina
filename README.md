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

**Instrucciones de uso.**
1. Ejecutar `python src/main.py` desde la raíz del repositorio (ver sección 5).
2. Indicar la ruta del archivo de datos (CSV o JSON) o apretar Enter para usar la predeterminada, `data/productos.csv`. El programa muestra cuántos registros leyó, cuántos son válidos y cuántos rechazó (por tipo), y guarda los rechazados con su motivo en `outputs/rechazados.csv`.
3. Elegir una opción del menú: listar categorías, buscar un producto por código EAN, comparar una categoría, comparar productos por códigos EAN, o exportar la última comparación a `outputs/` en CSV o JSON.
4. Después de cada operación se vuelve al menú; la opción `0` cierra el programa.

Los valores no disponibles se muestran como `N/D` en pantalla y como `no disponible` en los archivos exportados. Un ejemplo completo está en la sección 7.

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

Desarrollado con Python 3.14. Los comandos se ejecutan desde la raíz del repositorio (por ejemplo, en la terminal de VS Code).

1. Instalar las dependencias: `pip install -r requirements.txt`
2. Ejecutar la aplicación: `python src/main.py`
3. Ejecutar las pruebas: `python -m unittest discover -s tests -v`

Si en Windows `python` no se reconoce como comando, probar con `py` (por ejemplo, `py src/main.py`).

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

### Dominio y conversión de unidades (`src/producto.py`, `src/conversiones.py`, `src/pipeline.py`)

- **`ProductoNutricional`** (`producto.py`) contiene la ficha normalizada de un producto: código, nombre, categorías (lista) y nutrientes por cada 100 g. Su método `obtener(nutriente)` devuelve el valor en la unidad de comparación, o `None` si el nutriente no está disponible. Si el nombre no corresponde a un nutriente conocido, levanta un error, para que un error de tipeo no se confunda con un dato no disponible.
- **`normalizar_ficha()`** (`pipeline.py`) transforma un producto ya validado en una ficha homogénea: convierte cada nutriente a su unidad de comparación y lo lleva a una base de 100 g. No redondea; los valores conservan su precisión.
- **`preparar_catalogo()`** (`pipeline.py`) integra el flujo: lee el archivo, valida, normaliza los productos válidos y devuelve también el registro de rechazados. Los productos rechazados no se normalizan.

**Unidad de comparación (siempre por cada 100 g):**

| Nutriente | Unidad |
|---|---|
| Energía | kcal |
| Grasas, grasas saturadas, carbohidratos, azúcares, proteínas | g |
| Sodio | mg |

**Conversiones** (`conversiones.py`):
- 1 kcal = 4,184 kJ.
- 1 g = 1000 mg.
- Base `porcion`: valor × 100 / `porcion_g`. Si la base ya es `100g`, el valor no cambia.
- Las unidades incompatibles (por ejemplo, de g a kcal) levantan un error.

**Tratamiento de faltantes:**
- Un nutriente no disponible no aparece en la ficha normalizada y `obtener()` devuelve `None`. Nunca se convierte en cero.
- Un cero declarado en la etiqueta sí se conserva como `0.0`.
- Las categorías se guardan como lista; la regla para seleccionar productos por categoría se documentará al implementarla.

## 7. Ejemplo de resultado

Sesión real con la muestra incluida (`data/productos.csv`): se elige la categoría Yogures y se exporta la comparación.

```text
Comparador de etiquetas nutricionales
Ruta del archivo de datos (Enter para usar data\productos.csv, 'salir' para terminar): 

Registros leídos: 60
  Válidos: 56
  Rechazados: 4 (codigo_duplicado: 1, codigo_invalido: 1, fuera_de_rango: 1, valor_negativo: 1)
Registro de rechazados guardado en C:\Users\HP\Documents\GitHub\TP2-POD-Urbina\outputs\rechazados.csv

=== Menú ===
1. Listar las categorías
2. Buscar un producto por código EAN
3. Comparar los productos de una categoría
4. Comparar productos por códigos EAN
5. Exportar la última comparación (CSV o JSON)
0. Salir
Elegí una opción: 3

Categorías disponibles:
  Bebidas: 2 producto(s)
  Cereales: 14 producto(s)
  Desayuno: 4 producto(s)
  Galletitas: 14 producto(s)
  Integrales: 1 producto(s)
  Jugos: 14 producto(s)
  Lácteos: 2 producto(s)
  Postres: 4 producto(s)
  Sin conservantes: 1 producto(s)
  Snacks: 1 producto(s)
  Yogures: 14 producto(s)

Categoría: yogures

Código         Nombre                Energía  Grasas  Satur.  Carbo.  Azúcar  Prot.  Sodio
-------------  --------------------  -------  ------  ------  ------  ------  -----  -----
0363856073927  Yogur Frutilla Sigma  44.69    0.5     0.3     6.2     6.2     3.8    89.0 
0675347897133  Yogur Vainilla Beta   105.16   3.4     2.1     15.6    7.9     3.1    65.0 
0805780370412  Yogur Natural Sigma   87.2     0.48    0.32    17.84   8.8     3.04   49.6 
7790125373924  Yogur Durazno Beta    106.0    3.3     2.4     16.1    9.8     3.0    78.0 
7790668179223  Yogur Frutilla Gamma  85.0     1.1     0.0     N/D     4.5     5.8    44.0 
7795154742843  Yogur Natural Alfa    92.0     3.6     2.0     11.4    7.8     3.6    63.0 
7796252807001  Yogur Griego Delta    72.0     0.72    0.72    12.0    8.24    4.4    N/D  
7796550620484  Yogur Natural Delta   58.8     0.6     0.6     8.5     8.5     4.9    60.0 
7797207547354  Yogur Bebible Beta    89.6     2.88    2.08    12.24   5.28    3.84   60.8 
7797443256885  Yogur Frutilla Alfa   95.0     1.9     1.9     14.4    8.6     4.9    72.0 
7797457212835  Yogur Natural Gamma   83.0     1.4     1.4     13.9    5.4     3.6    62.0 
7797916979780  Yogur Griego Alfa     106.0    2.4     1.8     17.1    12.0    N/D    53.0 
7798195391827  Yogur Frutilla Beta   89.41    2.35    1.76    11.29   4.18    5.82   59.41
7799822290044  Yogur Bebible Alfa    90.0     3.94    0.06    8.12    8.12    5.59   46.47

Valores por cada 100 g (energía en kcal, sodio en mg, el resto en g). N/D = no disponible.

Presioná Enter para volver al menú...

=== Menú ===
1. Listar las categorías
2. Buscar un producto por código EAN
3. Comparar los productos de una categoría
4. Comparar productos por códigos EAN
5. Exportar la última comparación (CSV o JSON)
0. Salir
Elegí una opción: 5
Nombre del archivo (termina en .csv o .json, por ejemplo comparacion.csv): comparacion.csv
Comparación guardada en C:\Users\HP\Documents\GitHub\TP2-POD-Urbina\outputs\comparacion.csv

Presioná Enter para volver al menú...

=== Menú ===
1. Listar las categorías
2. Buscar un producto por código EAN
3. Comparar los productos de una categoría
4. Comparar productos por códigos EAN
5. Exportar la última comparación (CSV o JSON)
0. Salir
Elegí una opción: 0
¡Hasta luego!
```

Cómo leerlo:
- Cada fila es un producto y cada columna un nutriente, siempre **por cada 100 g**, aunque la etiqueta original estuviera por porción o en otras unidades.
- `N/D` significa que la etiqueta no informa ese nutriente. No es lo mismo que cero.
- Los productos rechazados no entran a la comparación: quedan registrados con su motivo en `outputs/rechazados.csv`.

## 8. Decisiones de limpieza

Decisiones previstas (se confirmarán al implementar):

- Los códigos se leen y se guardan como texto para conservar los ceros iniciales.
- Un nutriente ausente se registra como _no disponible_; no se reemplaza por cero.
- Las unidades se convierten a una unidad común de comparación y todo se expresa por 100 g.
- Si un producto tiene varias categorías, se aplica una regla de selección explícita.
- Los registros inválidos se apartan y se registran con su motivo, sin detener el programa.

## 9. Interpretación y limitaciones

_Pendiente: se completará al finalizar. Limitaciones ya conocidas: no se verifica el dígito de control del EAN, se trabaja con una muestra y no con la base completa, y la calidad de la comparación depende de la calidad de las fichas de origen._
