# -*- coding: utf-8 -*-
"""
tabla.py
Construccion de la tabla de analisis sintactico predictivo M[A, a].

Regla de llenado: para cada produccion A -> alfa,
  (1) para cada terminal a en PRIMERO(alfa) \\ {eps} se coloca A -> alfa
      en M[A, a];
  (2) si eps (lambda) esta en PRIMERO(alfa), para cada terminal b en
      SIGUIENTE(A) se coloca A -> alfa en M[A, b].
Las celdas vacias son entradas de error. Si una celda recibiera dos
producciones habria conflicto y la gramatica no seria LL(1).
"""

from gramatica import EPS, FIN, PRODUCCIONES, TERMINALES
from conjuntos import primero_secuencia


def construir_tabla(primero, siguiente):
    """Construye la tabla M[(no_terminal, terminal)] -> indice de produccion.

    Devuelve (tabla, conflictos); conflictos es una lista de mensajes con
    las celdas que recibieron mas de una produccion (de estar vacia, la
    gramatica es LL(1)).
    """
    tabla = {}
    conflictos = []
    for indice, (izq, cuerpo) in enumerate(PRODUCCIONES):
        pr = primero_secuencia(cuerpo, primero)
        destinos = pr - {EPS}
        if EPS in pr:
            destinos = destinos | siguiente[izq]
        for a in destinos:
            clave = (izq, a)
            if clave in tabla and tabla[clave] != indice:
                conflictos.append(
                    "M[%s, %s]: P%d y P%d" % (izq, a, tabla[clave] + 1, indice + 1))
            tabla[clave] = indice
    return tabla, conflictos


def esperados(tabla, no_terminal):
    """Terminales que admiten el no terminal (para mensajes de error)."""
    columnas = [t for t in TERMINALES + [FIN] if (no_terminal, t) in tabla]
    return ", ".join("'%s'" % c for c in columnas)
