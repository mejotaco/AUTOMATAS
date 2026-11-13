# -*- coding: utf-8 -*-
"""
lexer.py
Analizador lexico del analizador sintactico predictivo no recursivo.

Convierte la cadena de entrada en una lista de tokens con tipo, valor,
linea y columna. Las palabras reservadas map, filter, reduce, lambda y
range se reconocen por su nombre; el resto de secuencias de letras,
digitos y guion bajo son identificadores; los numeros aceptan parte
decimal opcional; los simbolos dobles (<=, >=, ==, !=) se reconocen
antes que los simples.
"""

from gramatica import (
    RESERVADAS,
    SIMBOLOS_DOBLES,
    SIMBOLOS_SIMPLES,
)


class Token(object):
    """Componente lexico con tipo, valor, linea y columna."""

    def __init__(self, tipo, valor, linea, columna):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna

    def __repr__(self):
        return "Token(%s, %r, %d, %d)" % (self.tipo, self.valor,
                                          self.linea, self.columna)


class ErrorSintactico(Exception):
    """Error lexico o sintactico con informacion de linea y columna."""
    pass


def tokenizar(texto, linea=1):
    """Convierte texto en una lista de tokens.

    Lanza ErrorSintactico si encuentra un caracter no valido.
    """
    tokens = []
    i, col, n = 0, 1, len(texto)
    while i < n:
        c = texto[i]
        if c in " \t\r":
            i += 1
            col += 1
            continue
        if c == "\n":
            linea += 1
            col = 1
            i += 1
            continue
        if c == "#":
            while i < n and texto[i] != "\n":
                i += 1
            continue
        par = texto[i:i + 2]
        if par in SIMBOLOS_DOBLES:
            tokens.append(Token(par, par, linea, col))
            i += 2
            col += 2
            continue
        if c in SIMBOLOS_SIMPLES:
            tokens.append(Token(c, c, linea, col))
            i += 1
            col += 1
            continue
        if c.isdigit():
            j = i
            while j < n and texto[j].isdigit():
                j += 1
            if j < n - 1 and texto[j] == "." and texto[j + 1].isdigit():
                j += 1
                while j < n and texto[j].isdigit():
                    j += 1
            tokens.append(Token("numero", texto[i:j], linea, col))
            col += (j - i)
            i = j
            continue
        if c.isalpha() or c == "_":
            j = i
            while j < n and (texto[j].isalnum() or texto[j] == "_"):
                j += 1
            palabra = texto[i:j]
            tipo = palabra if palabra in RESERVADAS else "identificador"
            tokens.append(Token(tipo, palabra, linea, col))
            col += (j - i)
            i = j
            continue
        raise ErrorSintactico(
            "Error lexico en linea %d, columna %d: caracter no valido '%s'."
            % (linea, col, c))
    return tokens
