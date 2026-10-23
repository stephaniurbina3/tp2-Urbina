# Comparador de etiquetas nutricionales

**Autora:** Stephani Urbina
**Materia:** Programación Orientada a Datos · UCA · Licenciatura en Ciencia de Datos · 2026
**Trabajo:** TP2 individual

## 1. Problema, usuario y pregunta

**Problema.** Comparar las etiquetas nutricionales de varios productos exige homogeneizar unidades (g, mg, kcal, kJ) y bases de referencia (por 100 g o por porción). Además, un nutriente que falta en la ficha puede confundirse con cero y producir comparaciones incorrectas: "no informado" no es lo mismo que "no contiene".

**Usuario.** Una persona que quiere comparar productos envasados (consumidor, estudiante de nutrición, analista) y necesita una tabla homogénea y confiable para decidir o analizar.

**Pregunta que guía el análisis.** ¿Cómo se comparan, sobre una base común de 100 g, los nutrientes de distintos productos envasados o de una categoría, y qué datos no están informados?

**Solución.** Un programa en Python con un menú interactivo en la terminal. Carga un catálogo de productos desde archivos CSV o JSON equivalentes, valida cada ficha (las inválidas se apartan y se registran con su motivo), lleva todos los nutrientes a una unidad común por cada 100 g y permite buscar, comparar y exportar.

**Resultado e interpretación.** Una tabla con una fila por producto y una columna por nutriente, por cada 100 g y en una unidad común. Cada valor es lo declarado en la ficha, convertido; no se verifica contra el producto real. `N/D` (en pantalla) o `no disponible` (en los archivos) indica que la ficha no informa ese nutriente: no equivale a cero.

## 2. Modo de uso

Al iniciar, el programa pide la ruta del archivo de datos: Enter usa `data/productos.csv`; también se puede escribir la ruta de un `.csv` o `.json` (o `salir`). Después muestra cuántos registros leyó, cuántos son válidos y cuántos rechazó, guarda los rechazados en `outputs/rechazados.csv` y abre el menú:

| Opción | Qué hace |
|---|---|
| 1 | Lista las categorías con la cantidad de productos de cada una |
| 2 | Pide un código EAN y muestra la ficha del producto, por 100 g |
| 3 | Muestra las categorías, pide una (sin distinguir mayúsculas ni tildes) y compara todos sus productos |
| 4 | Pide uno o varios códigos EAN (separados por espacios o comas) y compara esos productos |
| 5 | Exporta la última comparación a `outputs/`, en CSV o JSON según la extensión del nombre |
| 0 | Sale del programa |

Después de cada operación se vuelve al menú. Los errores de entrada (código inexistente, categoría sin productos, archivo inexistente) se informan con un mensaje claro y el programa sigue.

## 3. Alcance de la primera versión

- **Incluye:** carga desde CSV y JSON equivalentes, validación del código (8 o 13 dígitos) y de los valores, conversión de unidades y de bases de referencia a 100 g, búsqueda por código y selección por categoría (un producto puede tener varias), registro de rechazados con su motivo, exportación a CSV o JSON, pruebas automatizadas y documentación.
- **Queda fuera:** interfaz web o gráfica, descarga automática desde la API de Open Food Facts, verificación del dígito de control del EAN, puntajes de salubridad (como Nutri-Score) y recomendaciones, y aprendizaje automático.

## 4. Datos: fuente, licencia y unidad de análisis

- **Fuente:** datos **simulados**, generados con `scripts/generar_muestra.py` (semilla fija). Imitan etiquetas de productos envasados, pero no son productos reales.
- **Por qué simulados:** se intentó usar un extracto de Open Food Facts, pero su API pública devolvió error 503 y restringe las consultas anónimas cuando hay mucha demanda.
- **Responsable y licencia:** datos propios, sin restricciones de uso.
- **Unidad de análisis:** un producto, identificado por su código de barras (ficticio).
- **Archivos:** `data/productos.csv` y `data/productos.json`, con los mismos 60 productos en ambos formatos (4 con defectos deliberados para probar la validación).
- **Variables, procedimiento y limitaciones:** ver [`data/README.md`](data/README.md). Para regenerar la muestra: `python scripts/generar_muestra.py`.

## 5. Instalación y ejecución

Desarrollado con Python 3.14. Los comandos se ejecutan desde la raíz del repositorio (por ejemplo, en la terminal de VS Code).

1. Instalar las dependencias: `pip install -r requirements.txt` (el proyecto usa solo la biblioteca estándar, así que no se instala nada adicional).
2. Ejecutar la aplicación: `python src/main.py`
3. Ejecutar las pruebas: `python -m unittest discover -s tests -v`

Si en Windows `python` no se reconoce como comando, probar con `py` (por ejemplo, `py src/main.py`).

## 6. Organización del código

```text
tp2-urbina/
|-- README.md
|-- requirements.txt
|-- .gitignore
|-- docs/       diseño en detalle (reglas, funciones y decisiones)
|-- src/        código de la aplicación
|-- tests/      pruebas automatizadas (unittest)
|-- scripts/    generación de la muestra de datos
|-- data/       muestra de datos (CSV y JSON) y su procedencia
'-- outputs/    resultados generados (no se versionan)
```

| Módulo (`src/`) | Responsabilidad |
|---|---|
| `main.py` | Menú interactivo (punto de entrada); solo conversa con quien usa el programa |
| `pipeline.py` | Flujo de datos: cargar, normalizar, indexar, buscar, seleccionar y comparar |
| `fuente_datos.py`, `fuente_csv.py`, `fuente_json.py`, `fuentes.py` | Lectura de CSV y JSON detrás de una interfaz común; `crear_fuente()` elige según la extensión |
| `validaciones.py` | Reglas de validación y registro de rechazados |
| `producto.py` | Clase de dominio `ProductoNutricional` |
| `conversiones.py` | Unidad de comparación, conversión de unidades y base de 100 g |
| `salidas.py` | Tabla para pantalla, exportación a CSV o JSON y archivo de rechazados |
| `error_datos.py`, `error_consulta.py` | Errores propios |

**Flujo:** leer (CSV o JSON) → inspeccionar y validar → limpiar y transformar (normalizar a 100 g) → analizar (buscar, seleccionar y comparar) → comunicar (tabla en pantalla, exportación y registro de rechazados).

**Decisiones de diseño principales** (detalle en [`docs/diseno.md`](docs/diseno.md)):

- **Fuentes de datos.** `FuenteDatos` es una clase abstracta con el método `cargar()`; `FuenteCSV` y `FuenteJSON` lo implementan y devuelven la misma estructura de productos. Así el resto del programa no depende del formato del archivo.
- **Etapas separadas.** Leer no valida; validar no convierte; normalizar solo recibe productos ya válidos; comparar usa fichas normalizadas; mostrar y guardar es otra capa. Cada etapa se prueba por separado y un cambio en una no obliga a tocar las demás.
- **Clase de dominio.** `ProductoNutricional` contiene la ficha normalizada. Su método `obtener(nutriente)` devuelve el valor por 100 g en su unidad de comparación, o `None` si no está disponible.
- **Conversión y base común.** Energía en kcal; grasas, saturadas, carbohidratos, azúcares y proteínas en g; sodio en mg; todo por cada 100 g. Equivalencias: 1 kcal = 4,184 kJ; 1 g = 1000 mg; un valor por porción se multiplica por 100 y se divide por el tamaño de la porción.
- **Categorías.** Un producto pertenece a todas las categorías de su lista, y se comparan sin distinguir mayúsculas, tildes ni espacios.
- **Errores.** `ErrorDatos` (datos que incumplen las reglas) y `ErrorConsulta` (consultas que no se pueden resolver) son distintos. El menú atrapa solo errores previstos y deja visibles los inesperados.

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
[...]
Elegí una opción: 5
Nombre del archivo (termina en .csv o .json, por ejemplo comparacion.csv): comparacion.csv
Comparación guardada en C:\Users\HP\Documents\GitHub\TP2-POD-Urbina\outputs\comparacion.csv

Presioná Enter para volver al menú...

=== Menú ===
[...]
Elegí una opción: 0
¡Hasta luego!
```

Cómo leerlo:

- Cada fila es un producto y cada columna un nutriente, siempre **por cada 100 g**, aunque la etiqueta original estuviera por porción o en otras unidades.
- `N/D` significa que la etiqueta no informa ese nutriente. No es lo mismo que cero.
- Los productos rechazados no entran a la comparación: quedan registrados con su motivo en `outputs/rechazados.csv`.

## 8. Decisiones de limpieza

Cada producto se valida antes de entrar al catálogo. Si incumple varias reglas, se registra la primera que falla, en este orden:

| Regla | Motivo de rechazo (`tipo`) |
|---|---|
| El código es texto y tiene exactamente 8 o 13 dígitos | `codigo_invalido` |
| El nombre no está vacío | `nombre_faltante` |
| La base es `100g` o `porcion` (con `porcion_g` mayor que cero) | `base_invalida` |
| Los valores nutricionales son números finitos | `valor_invalido` |
| La unidad es admitida (energía: kcal o kJ; resto: g o mg) | `unidad_desconocida` |
| El valor no es negativo | `valor_negativo` |
| El valor no supera el máximo posible (100 g cada 100 g, o la porción; 900 kcal cada 100 g) | `fuera_de_rango` |
| El código no se repite | `codigo_duplicado` |

- **Expresión regular del código:** `[0-9]{8}|[0-9]{13}` (con `fullmatch`). Valida solo la **forma**; no comprueba el dígito de control del EAN ni que el producto exista, por eso se complementa con las demás reglas.
- **Códigos como texto**, para conservar los ceros iniciales.
- **Duplicados:** se conserva la primera aparición válida y se rechazan las siguientes.
- **Valores no informados:** un nutriente ausente es válido, no se agrega a la ficha y nunca se reemplaza por cero; un cero declarado sí se conserva.
- **Registro de rechazados:** cada producto rechazado se guarda en `outputs/rechazados.csv` con su posición, código, nombre, tipo y motivo, sin detener el programa.

## 9. Interpretación y limitaciones

- Los datos son simulados: sirven para desarrollar y probar el programa, no para sacar conclusiones sobre alimentos reales. Los códigos son ficticios y los faltantes se eligen al azar.
- Cada valor es lo declarado en la ficha, convertido a 100 g y a la unidad común; no se verifica contra el producto real. Los valores se redondean a 2 decimales solo en la tabla.
- No se comprueba el dígito de control del EAN.
- Se contemplan siete nutrientes y solo las unidades kcal, kJ, g y mg; otros nutrientes o unidades no se procesan.
- Si un producto incumple varias reglas, se registra solo la primera.
- La selección por categoría compara nombres (sin mayúsculas ni tildes); no reconoce sinónimos ni nombres parecidos.
- Es una aplicación de terminal: no tiene interfaz gráfica ni descarga datos de internet.
- Mejoras posibles: verificar el dígito de control, registrar todos los motivos de rechazo de un producto y trabajar con datos reales (por ejemplo, un extracto de Open Food Facts).