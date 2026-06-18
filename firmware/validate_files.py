#!/usr/bin/env python3
# ============================================================
# USS SPIDERBOT — Validador de Sintaxis de Archivos Python
# Solemne 3 — Taller de Programación I
# Python 3 — Ejecución Local
# ============================================================
# Escanea automáticamente todos los archivos .py en la carpeta
# USS_SpiderBot/ y verifica que compilen correctamente usando
# el módulo nativo ast. Genera un reporte en consola.
# ============================================================

import ast
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def validar_archivo(ruta):
    with open(ruta, "r", encoding="utf-8") as f:
        source = f.read()
    try:
        ast.parse(source, filename=ruta)
        return True, None
    except SyntaxError as e:
        return False, str(e)

def main():
    archivos_py = sorted([
        f for f in os.listdir(SCRIPT_DIR)
        if f.endswith(".py") and os.path.isfile(os.path.join(SCRIPT_DIR, f))
    ])

    if not archivos_py:
        print("No se encontraron archivos .py en el directorio.")
        sys.exit(0)

    print("=" * 60)
    print("  Validador de Sintaxis — USS SpiderBot")
    print("=" * 60)

    errores = 0

    for archivo in archivos_py:
        ruta = os.path.join(SCRIPT_DIR, archivo)
        ok, error_msg = validar_archivo(ruta)
        if ok:
            print(f"  [OK] {archivo}")
        else:
            print(f"  [ERROR] {archivo}: {error_msg}")
            errores += 1

    print("=" * 60)
    total = len(archivos_py)
    print(f"  Resumen: {total - errores}/{total} archivos OK", end="")
    if errores > 0:
        print(f", {errores} archivo(s) con error(es)")
    else:
        print()
    print("=" * 60)

    return 1 if errores > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
