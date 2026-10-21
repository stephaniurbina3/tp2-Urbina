# Datos

## Fuente y procedencia
- **Fuente:** datos **simulados**, generados con `scripts/generar_muestra.py`. Imitan etiquetas nutricionales de productos envasados (cereales, yogures, jugos y galletitas), pero **no son productos reales**.
- **Procedimiento de obtención:** `python scripts/generar_muestra.py`. Usa una semilla fija (2026), por lo que, con la misma versión de Python, produce siempre la misma muestra. Los archivos de esta carpeta son la referencia.
- **Responsable:** Stephani Urbina (autora del trabajo).
- **Licencia o condiciones de uso:** datos de elaboración propia, sin restricciones de uso.
- **Fecha de generación:** <21/10/2026>
- **Por qué simulados:** el plan original era usar un extracto de Open Food Facts, pero su API pública respondió con error 503 y restringe las consultas anónimas en momentos de alta demanda. Se optó por datos simulados, manteniendo la estructura de una etiqueta real (distintas unidades y bases de referencia).

## Archivos
| Archivo | Formato | Contenido |
|---|---|---|
| `productos.csv` | CSV (UTF-8) | 60 productos, 19 columnas planas |
| `productos.json` | JSON (UTF-8) | Los mismos 60 productos, con los nutrientes anidados en `nutrientes` |

Un nutriente no informado aparece como **celda vacía** en el CSV y como **clave ausente** en el JSON. Nunca se reemplaza por cero (un `0` significa que la etiqueta declara cero).

## Unidad de análisis
Cada fila del CSV (o cada elemento del JSON) es **un producto**, identificado por su código de barras.

## Variables
Los valores están **tal como se declaran en la "etiqueta"**: no están convertidos a una unidad común ni a 100 g.

| Columna CSV / clave JSON | Tipo | Unidad | Descripción | Puede faltar |
|---|---|---|---|---|
| `codigo` | texto | – | Código de barras ficticio (8 o 13 dígitos). Texto, para conservar ceros iniciales | No |
| `nombre` | texto | – | Nombre inventado: producto, variedad y marca ficticia | No |
| `categorias` | texto | – | Una o dos categorías separadas por coma | No |
| `base` | texto | – | Base de la declaración: `100g` o `porcion` | No |
| `porcion_g` | número | g | Tamaño de la porción; solo cuando `base` es `porcion` | Sí (vacío si es `100g`) |
| `energia_valor`, `energia_unidad` | número, texto | kcal o kJ | Energía declarada | Sí |
| `grasas`, `grasas_saturadas`, `carbohidratos`, `azucares`, `proteinas` (`_valor` y `_unidad`) | número, texto | g | Cantidad declarada | Sí |
| `sodio_valor`, `sodio_unidad` | número, texto | mg o g | Sodio declarado | Sí |

En el JSON, cada nutriente es un objeto, por ejemplo `"azucares": {"valor": 12.5, "unidad": "g"}`.

Tamaño: 60 observaciones y 12 variables (19 columnas en el CSV, porque cada nutriente tiene valor y unidad).

## Defectos deliberados
Para que el flujo de validación tenga algo que detectar, se introdujeron 4 errores a propósito. **No son fallas del script.**

| Defecto | Qué se espera del programa |
|---|---|
| Un código de 7 dígitos | Rechazarlo (no cumple el patrón de 8 o 13 dígitos) |
| Azúcares con valor negativo (-4,0 g) | Rechazarlo (valor fuera de rango) |
| Grasas con 140 g cada 100 g | Rechazarlo (imposible por 100 g) |
| Un código repetido | Conservar una ficha y registrar la otra como duplicada |

## Cómo reconstruir la muestra
1. `pip install -r requirements.txt`
2. `python scripts/generar_muestra.py`

## Limitaciones, sesgos y restricciones
- Los datos son inventados: no representan productos reales y los códigos de barras son ficticios. Pueden coincidir por azar con códigos reales, y no se calcula el dígito de control.
- Los valores salen de rangos plausibles definidos a mano para cuatro categorías; no reflejan la distribución real del mercado.
- Los nutrientes faltantes se eligen al azar, con probabilidades fijas; en datos reales los faltantes no son tan aleatorios.
- Los valores se redondean al declararlos (energía a enteros, gramos a un decimal), lo que introduce pequeñas diferencias al convertir.
- La muestra es chica (60 productos) y solo sirve para desarrollar y probar el programa, no para sacar conclusiones sobre alimentos.
- No contiene datos personales, credenciales ni claves.