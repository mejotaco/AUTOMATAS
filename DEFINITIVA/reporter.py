# -*- coding: utf-8 -*-
"""
reporter.py
Impresion de resultados auxiliares: traza de la pila, conjuntos
PRIMERO y SIGUIENTE, tabla de analisis predictivo y producciones.
"""

from gramatica import (
    EPS,
    FIN,
    NO_TERMINALES,
    PRODUCCIONES,
    TERMINALES,
    ordenar_conjunto,
)


def imprimir_traza(pasos):
    """Imprime la traza PASO | PILA | ENTRADA | ACCION de un analisis."""
    print()
    print("%-5s %-44s %-44s %s" % ("PASO", "PILA (cima a la derecha)",
                                   "ENTRADA", "ACCION"))
    print("-" * 118)
    for paso, pila_txt, entrada, accion in pasos:
        print("%-5d %-44s %-44s %s" % (paso, pila_txt, entrada, accion))
    print("-" * 118)


def imprimir_conjuntos(primero, siguiente):
    """Imprime los conjuntos PRIMERO y SIGUIENTE de todos los no terminales."""
    print("CONJUNTOS PRIMERO")
    for nt in NO_TERMINALES:
        print("  PRIMERO(%s) = { %s }" % (nt, ", ".join(ordenar_conjunto(primero[nt]))))
    print()
    print("CONJUNTOS SIGUIENTE")
    for nt in NO_TERMINALES:
        print("  SIGUIENTE(%s) = { %s }" % (nt, ", ".join(ordenar_conjunto(siguiente[nt]))))
    print()


def imprimir_tabla(tabla):
    """Imprime la tabla de analisis predictivo M[No-Terminal, Terminal]."""
    print("TABLA DE ANALISIS PREDICTIVO M[No-Terminal, Terminal]")
    print("(cada Pn corresponde a una produccion; vea el listado de producciones)\n")
    for nt in NO_TERMINALES:
        entradas = [(t, tabla[(nt, t)]) for t in TERMINALES + [FIN] if (nt, t) in tabla]
        linea = "%-16s:" % nt
        for terminal, indice in entradas:
            linea += " '%s'->P%d" % (terminal, indice + 1)
        print(linea)
    print()


def imprimir_producciones():
    """Imprime el listado numerado de producciones de la gramatica."""
    print("PRODUCCIONES DE LA GRAMATICA (Pn)")
    for indice, (izq, cuerpo) in enumerate(PRODUCCIONES, 1):
        cuerpo_txt = " ".join(cuerpo) if cuerpo else EPS
        print("  P%-3d %s -> %s" % (indice, izq, cuerpo_txt))
    print()
