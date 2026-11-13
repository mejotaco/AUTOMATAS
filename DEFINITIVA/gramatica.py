# -*- coding: utf-8 -*-
"""
gramatica.py
Definition of the final grammar (without left recursion) of the
predictive syntactic analyzer for the instructions map, filter and
reduce of the Python language.

Module structure of the project:
    gramatica.py  -> this module (terminals, productions, helpers)
    lexer.py      -> lexical analyzer (tokenizing)
    conjuntos.py  -> PRIMEROS and SIGUIENTES sets (fixed point)
    tabla.py      -> predictive analysis table M[No-Terminal, Terminal]
    parser.py     -> NON-RECURSIVE predictive syntactic analyzer (stack + table)
    reporter.py   -> printing of traces, sets, table and productions
    runner.py     -> execution modes (keyboard, file, menu)
    analizador.py -> entry point (main)

Implemented grammar (after eliminating left recursion):

  S               -> INSTRUCCION
  INSTRUCCION     -> MAP | FILTER | REDUCE
  MAP             -> map ( ARGUMENTOS )
  FILTER          -> filter ( ARGUMENTOS )
  REDUCE          -> reduce ( ARGUMENTOS )
  ARGUMENTOS      -> FUNCION , ITERABLE MAS_ITERABLES
  MAS_ITERABLES   -> , ITERABLE MAS_ITERABLES | eps (lambda: empty string)
  FUNCION         -> lambda PARAMETROS : EXPRESION | identificador
  PARAMETROS      -> identificador MAS_PARAMETROS
  MAS_PARAMETROS  -> , identificador MAS_PARAMETROS | eps (lambda: empty string)
  EXPRESION       -> TERMINO EXPRESION'
  EXPRESION'      -> + TERMINO EXPRESION' | - TERMINO EXPRESION'
                   | RELACION TERMINO EXPRESION' | eps (lambda: empty string)
  TERMINO         -> FACTOR TERMINO'
  TERMINO'        -> * FACTOR TERMINO' | / FACTOR TERMINO' | eps (lambda: empty string)
  FACTOR          -> identificador | numero | ( EXPRESION )
  ITERABLE        -> LISTA | range ( numero , numero )
                   | identificador | numero
  LISTA           -> [ ELEMENTOS_OPT ]
  ELEMENTOS_OPT   -> ELEMENTOS | eps (lambda: empty string)
  ELEMENTOS       -> numero MAS_ELEMENTOS
  MAS_ELEMENTOS   -> , numero MAS_ELEMENTOS | eps (lambda: empty string)
  RELACION        -> < | > | <= | >= | == | !=

Original rules WITH left recursion (before the transformation):

  EXPRESION -> EXPRESION + TERMINO | EXPRESION - TERMINO
             | EXPRESION RELACION TERMINO | TERMINO
  TERMINO   -> TERMINO * FACTOR | TERMINO / FACTOR | FACTOR

Examples of accepted instructions:

  map(lambda x: x*2, [1,2,3])
  filter(lambda n: n>=5, numeros)
  reduce(lambda a,b: a+b, range(1,10))
  map(multiplicar, lista1, lista2)
"""

EPS = "eps"          # lambda (empty string)
FIN = "$"

TERMINALES = [
    "map", "filter", "reduce", "lambda", "range",
    "identificador", "numero",
    "(", ")", "[", "]", ",", ":", "+", "-", "*", "/",
    "<", ">", "<=", ">=", "==", "!=",
]

RESERVADAS = {"map", "filter", "reduce", "lambda", "range"}
SIMBOLOS_DOBLES = ("<=", ">=", "==", "!=")
SIMBOLOS_SIMPLES = set("()[]:,+-*/<>")

# High-order instructions recognized by the grammar (first element of
# the production is the reserved word of the instruction).
INSTRUCCIONES_ORDEN_SUPERIOR = ("map", "filter", "reduce")

# Productions of the final grammar, numbered from 1 (P1, P2, ...).
PRODUCCIONES = [
    ("S",              ("INSTRUCCION",)),                                     # P1
    ("INSTRUCCION",    ("MAP",)),                                             # P2
    ("INSTRUCCION",    ("FILTER",)),                                          # P3
    ("INSTRUCCION",    ("REDUCE",)),                                          # P4
    ("MAP",            ("map", "(", "ARGUMENTOS", ")")),                      # P5
    ("FILTER",          ("filter", "(", "ARGUMENTOS", ")")),                  # P6
    ("REDUCE",         ("reduce", "(", "ARGUMENTOS", ")")),                   # P7
    ("ARGUMENTOS",     ("FUNCION", ",", "ITERABLE", "MAS_ITERABLES")),        # P8
    ("MAS_ITERABLES",  (",", "ITERABLE", "MAS_ITERABLES")),                   # P9
    ("MAS_ITERABLES",  ()),                                                   # P10  (eps)
    ("FUNCION",        ("lambda", "PARAMETROS", ":", "EXPRESION")),           # P11
    ("FUNCION",        ("identificador",)),                                   # P12
    ("PARAMETROS",     ("identificador", "MAS_PARAMETROS")),                  # P13
    ("MAS_PARAMETROS", (",", "identificador", "MAS_PARAMETROS")),             # P14
    ("MAS_PARAMETROS", ()),                                                   # P15  (eps)
    ("EXPRESION",      ("TERMINO", "EXPRESION'")),                            # P16
    ("EXPRESION'",     ("+", "TERMINO", "EXPRESION'")),                       # P17
    ("EXPRESION'",     ("-", "TERMINO", "EXPRESION'")),                       # P18
    ("EXPRESION'",     ("RELACION", "TERMINO", "EXPRESION'")),                # P19
    ("EXPRESION'",     ()),                                                   # P20  (eps)
    ("TERMINO",        ("FACTOR", "TERMINO'")),                               # P21
    ("TERMINO'",       ("*", "FACTOR", "TERMINO'")),                          # P22
    ("TERMINO'",       ("/", "FACTOR", "TERMINO'")),                          # P23
    ("TERMINO'",       ()),                                                   # P24  (eps)
    ("FACTOR",         ("identificador",)),                                   # P25
    ("FACTOR",         ("numero",)),                                          # P26
    ("FACTOR",         ("(", "EXPRESION", ")")),                              # P27
    ("ITERABLE",       ("LISTA",)),                                           # P28
    ("ITERABLE",       ("range", "(", "numero", ",", "numero", ")")),         # P29
    ("ITERABLE",       ("identificador",)),                                   # P30
    ("ITERABLE",       ("numero",)),                                          # P31
    ("LISTA",          ("[", "ELEMENTOS_OPT", "]")),                          # P32
    ("ELEMENTOS_OPT",  ("ELEMENTOS",)),                                       # P33
    ("ELEMENTOS_OPT",  ()),                                                   # P34  (eps)
    ("ELEMENTOS",      ("numero", "MAS_ELEMENTOS")),                          # P35
    ("MAS_ELEMENTOS",  (",", "numero", "MAS_ELEMENTOS")),                     # P36
    ("MAS_ELEMENTOS",  ()),                                                   # P37  (eps)
    ("RELACION",       ("<",)),                                               # P38
    ("RELACION",       (">",)),                                               # P39
    ("RELACION",       ("<=",)),                                              # P40
    ("RELACION",       (">=",)),                                              # P41
    ("RELACION",       ("==",)),                                              # P42
    ("RELACION",       ("!=",)),                                              # P43
]

NO_TERMINALES = []
for _izq, _ in PRODUCCIONES:
    if _izq not in NO_TERMINALES:
        NO_TERMINALES.append(_izq)

ORDEN_TOTAL = TERMINALES + [FIN, EPS]


def es_terminal(x):
    """Devuelve True si el simbolo x es un terminal de la gramatica."""
    return x in TERMINALES


def ordenar_conjunto(conjunto):
    """Ordena un conjunto de simbolos segun el orden canonico de la gramatica."""
    presentes = [s for s in ORDEN_TOTAL if s in conjunto]
    resto = sorted(s for s in conjunto if s not in ORDEN_TOTAL)
    return presentes + resto


def producciones_eps():
    """Devuelve los numeros (1-based) de las producciones vacias (lambda/eps)."""
    return [i + 1 for i, (_izq, cuerpo) in enumerate(PRODUCCIONES) if not cuerpo]


def cuerpo_eps(izq):
    """Devuelve True si el no terminal izq tiene alguna produccion vacia."""
    return any(n == izq and not cuerpo for n, cuerpo in PRODUCCIONES)
