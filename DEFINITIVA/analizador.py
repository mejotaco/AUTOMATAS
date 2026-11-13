# -*- coding: utf-8 -*-
"""
analizador.py
Punto de entrada del ANALIZADOR SINTACTICO PREDICTIVO NO RECURSIVO.

Instrucciones analizadas: map, filter y reduce del lenguaje Python.

El analizador usa el metodo de la tabla LL(1): un analizador con pila
explicita que consulta en cada paso la tabla de analisis predictivo
M[No-Terminal, Terminal]. No utiliza recursividad (metodo no recursivo).

Uso:
  python analizador.py              (menu interactivo)
  python analizador.py archivo.txt  (analiza cada linea)
  python verificar.py               (pruebas automaticas)

Estructura modular:
  gramatica.py  definicion de la gramatica final (43 producciones)
  lexer.py      analizador lexico (tokens con linea y columna)
  conjuntos.py  conjuntos PRIMERO y SIGUIENTE (punto fijo)
  tabla.py      tabla M[A, a] con deteccion de conflictos
  parser.py     analizador sintactico no recursivo con traza
  reporter.py   impresion de traza, conjuntos, tabla y producciones
  runner.py     modos de ejecucion (archivo, teclado, menu)
"""

import sys

from conjuntos import calcular_primero, calcular_siguiente
from runner import analizar_archivo, menu
from tabla import construir_tabla


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass
    primero = calcular_primero()
    siguiente = calcular_siguiente(primero)
    tabla, conflictos = construir_tabla(primero, siguiente)
    if conflictos:
        print("ADVERTENCIA: la gramatica NO es LL(1). Conflictos:")
        for conflicto in conflictos:
            print("  " + conflicto)
        return
    if len(sys.argv) > 1:
        analizar_archivo(sys.argv[1], tabla)
        return
    menu(tabla, primero, siguiente)


if __name__ == "__main__":
    main()
