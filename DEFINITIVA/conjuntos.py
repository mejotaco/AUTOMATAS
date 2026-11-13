# -*- coding: utf-8 -*-
"""
conjuntos.py
Calculo de los conjuntos PRIMERO y SIGUIENTE por el metodo de punto fijo.

Reglas de PRIMERO(X):
  * Si X es terminal, PRIMERO(X) = { X }.
  * Si X -> eps esta en P, entonces eps (lambda) pertenece a PRIMERO(X).
  * Si X -> Y1 Y2 ... Yn, se agrega PRIMERO(Y1) \\ {eps}; si eps esta en
    PRIMERO(Y1) se agrega ademas PRIMERO(Y2) \\ {eps}, y asi sucesivamente;
    si eps esta en PRIMERO(Yi) para todo i, entonces eps pertenece a PRIMERO(X).

Reglas de SIGUIENTE(A):
  * $ pertenece a SIGUIENTE(S), siendo S el simbolo inicial.
  * Si B -> alfa A beta, entonces PRIMERO(beta) \\ {eps} incluido en SIGUIENTE(A).
  * Si B -> alfa A, o bien B -> alfa A beta con eps en PRIMERO(beta),
    entonces SIGUIENTE(B) incluido en SIGUIENTE(A).
"""

from gramatica import (
    EPS,
    FIN,
    NO_TERMINALES,
    PRODUCCIONES,
    es_terminal,
)


def primero_secuencia(secuencia, primero):
    """PRIMERO de la secuencia Y1 Y2 ... Yk de simbolos de la gramatica.

    Devuelve el conjunto incluyendo EPS cuando la secuencia puede derivar
    en la cadena vacia (lambda).
    """
    resultado = set()
    for simbolo in secuencia:
        if es_terminal(simbolo):
            resultado.add(simbolo)
            return resultado
        f = primero[simbolo]
        resultado |= (f - {EPS})
        if EPS not in f:
            return resultado
    resultado.add(EPS)
    return resultado


def calcular_primero():
    """Calcula los conjuntos PRIMERO de todos los no terminales (punto fijo)."""
    primero = {nt: set() for nt in NO_TERMINALES}
    cambio = True
    while cambio:
        cambio = False
        for izq, cuerpo in PRODUCCIONES:
            p = primero_secuencia(cuerpo, primero)
            if not p <= primero[izq]:
                primero[izq] |= p
                cambio = True
    return primero


def calcular_siguiente(primero):
    """Calcula los conjuntos SIGUIENTE de todos los no terminales (punto fijo)."""
    siguiente = {nt: set() for nt in NO_TERMINALES}
    siguiente["S"].add(FIN)
    cambio = True
    while cambio:
        cambio = False
        for izq, cuerpo in PRODUCCIONES:
            for i, simbolo in enumerate(cuerpo):
                if es_terminal(simbolo):
                    continue
                resto = cuerpo[i + 1:]
                pr = primero_secuencia(resto, primero)
                antes = len(siguiente[simbolo])
                siguiente[simbolo] |= (pr - {EPS})
                if EPS in pr:
                    siguiente[simbolo] |= siguiente[izq]
                if len(siguiente[simbolo]) != antes:
                    cambio = True
    return siguiente
