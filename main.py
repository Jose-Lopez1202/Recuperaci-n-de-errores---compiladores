
import sys
from datetime import datetime
from lexer import Lexer
from parser import Parser

def leer_archivo(ruta: str) -> str:
    """Lee el contenido de un archivo fuente."""
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta}'.")
        sys.exit(1)
def mostrar_codigo_fuente(codigo: str):
    print("╔══════════════════════════════════════════════════════╗")
    print("║              CÓDIGO FUENTE ANALIZADO                 ║")
    print("╚══════════════════════════════════════════════════════╝")
    lineas = codigo.split('\n')
    for i, linea in enumerate(lineas, 1):
        print(f"  {i:4d} │ {linea}")
    print()
def generar_reporte(archivo_fuente: str, errores_lexicos: list, errores_sintacticos: list):
    todos = errores_lexicos + errores_sintacticos
    total_lex = len(errores_lexicos)
    total_sin = len(errores_sintacticos)
    total = len(todos)
    print("╔══════════════════════════════════════════════════════╗")
    print("║                 REPORTE DE ERRORES                   ║")
    print("╚══════════════════════════════════════════════════════╝")
    if total == 0:
        print("  ✓ El programa es sintácticamente correcto.")
        print("    No se encontraron errores.")
    else:
        if total_lex > 0:
            print(f"\n  ── Errores Léxicos ({total_lex}) ──")
            for i, err in enumerate(errores_lexicos, 1):
                print(f"    {i}. {err}")

        if total_sin > 0:
            print(f"\n  ── Errores Sintácticos ({total_sin}) ──")
            for i, err in enumerate(errores_sintacticos, 1):
                print(f"    {i}. {err}")

        print(f"\n  ── Resumen ──")
        print(f"    Errores léxicos:     {total_lex}")
        print(f"    Errores sintácticos: {total_sin}")
        print(f"    Total:               {total}")
    nombre_log = "errores.log"
    with open(nombre_log, 'w', encoding='utf-8') as f:
        f.write(f"Reporte de Errores - Compilador con Modo Pánico\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Archivo analizado: {archivo_fuente}\n")
        f.write(f"{'=' * 55}\n\n")
        if total == 0:
            f.write("El programa es sintácticamente correcto.\n")
        else:
            if total_lex > 0:
                f.write(f"Errores Léxicos ({total_lex}):\n")
                for i, err in enumerate(errores_lexicos, 1):
                    f.write(f"  {i}. {err}\n")
                f.write("\n")

            if total_sin > 0:
                f.write(f"Errores Sintácticos ({total_sin}):\n")
                for i, err in enumerate(errores_sintacticos, 1):
                    f.write(f"  {i}. {err}\n")
                f.write("\n")
            f.write(f"{'=' * 55}\n")
            f.write(f"Total de errores: {total}\n")

    print(f"\n  Log guardado en: {nombre_log}")
def main():
    if len(sys.argv) > 1:
        archivo = sys.argv[1]
    else:
        archivo = "casos_prueba.txt"
    codigo = leer_archivo(archivo)
    mostrar_codigo_fuente(codigo)
    print("╔══════════════════════════════════════════════════════╗")
    print("║              FASE 1: ANÁLISIS LÉXICO                 ║")
    print("╚══════════════════════════════════════════════════════╝")
    lexer = Lexer(codigo)
    tokens = lexer.tokenizar()
    print(f"  Tokens generados: {len(tokens)}")
    if lexer.errores:
        print(f"  Errores léxicos encontrados: {len(lexer.errores)}")
    else:
        print(f"  Sin errores léxicos.")
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║     FASE 2: ANÁLISIS SINTÁCTICO (MODO PÁNICO)       ║")
    print("╚══════════════════════════════════════════════════════╝")
    parser = Parser(tokens)
    errores_sintacticos = parser.parsear()
    print(f"  Errores sintácticos encontrados: {len(errores_sintacticos)}")
    print()
    generar_reporte(archivo, lexer.errores, errores_sintacticos)
if __name__ == "__main__":
    main()
