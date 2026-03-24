# Compilador con Recuperación de Errores (Modo Pánico)

Implementación de un analizador léxico y sintáctico con recuperación de errores mediante la técnica de **Modo Pánico** (Panic Mode Recovery). El compilador es capaz de detectar múltiples errores sintácticos en una sola ejecución sin detenerse ante el primero.

## Descripción

El proyecto implementa un compilador para un mini-lenguaje con soporte para:
- Declaración de variables (`var`)
- Estructuras de control (`if`, `else`, `while`, `for`)
- Definición de funciones (`def`)
- Expresiones aritméticas y de comparación
- Comentarios de línea (`//`)

Cuando el parser encuentra un error sintáctico, entra en **modo pánico**: registra el error con línea y columna, descarta tokens hasta un punto de sincronización seguro (`;`, `if`, `while`, `def`, `}`, etc.) y continúa el análisis.

## Estructura del Proyecto

```
compilador/
├── lexer.py              # Analizador léxico (tokenizador)
├── parser.py             # Analizador sintáctico con modo pánico
├── main.py               # Punto de entrada del programa
├── casos_prueba.txt      # Archivo con errores sintácticos intencionales
├── prueba_correcta.txt   # Archivo sin errores para validación
└── README.md
```
