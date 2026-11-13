# Códigos fuente — DEFINITIVA

Archivos Python incluidos:

- [analizador.py](#analizador)
- [conjuntos.py](#conjuntos)
- [gramatica.py](#gramatica)
- [lexer.py](#lexer)
- [parser.py](#parser)
- [reporter.py](#reporter)
- [runner.py](#runner)
- [tabla.py](#tabla)
- [verificar.py](#verificar)

<a id="analizador"></a>

## analizador.py

```python
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
```

<a id="conjuntos"></a>

## conjuntos.py

```python
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
```

<a id="gramatica"></a>

## gramatica.py

```python
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
```

<a id="lexer"></a>

## lexer.py

```python
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
```

<a id="parser"></a>

## parser.py

```python
# -*- coding: utf-8 -*-
"""
parser.py
Analizador sintactico predictivo NO RECURSIVO (pila explicita + tabla LL(1)).

Algoritmo:
  1. Colocar '$' al final de la entrada y '$ S' en la pila (S arriba).
  2. Apuntar al primer token de la entrada.
  3. Mientras la pila no este vacia:
       X <- cima de la pila ; a <- token actual
       si X es terminal:  si X == a, desapilar y avanzar; si no, ERROR
       si X == '$':       si a == '$' ACEPTAR; si no, ERROR
       si X es no terminal:
           si M[X, a] == X -> Y1 ... Yk: desapilar X y apilar Yk..Y1
           en caso contrario (celda vacia): ERROR

Cada paso queda registrado en una traza (paso, pila, entrada, accion).
"""

from gramatica import EPS, FIN, PRODUCCIONES, es_terminal
from lexer import ErrorSintactico, Token, tokenizar
from tabla import esperados
from reporter import imprimir_traza


def analizar_tokens(tokens, tabla):
    """Analiza la lista de tokens (terminada en $) con pila y tabla.

    Devuelve (aceptada, pasos, mensaje_error):
      aceptada      True si la cadena pertenece al lenguaje.
      pasos         traza [(paso, pila, entrada, accion), ...].
      mensaje_error descripcion del primer error, o None.
    """
    pila = [FIN, "S"]
    i = 0
    pasos = []
    while True:
        if len(pasos) >= 3000:
            return False, pasos, "Error: numero de pasos excedido (posible ciclo)."
        paso = len(pasos) + 1
        cima = pila[-1]
        tok = tokens[i]
        entrada = " ".join(t.valor for t in tokens[i:])
        pila_txt = " ".join(pila)
        if cima == FIN:
            if tok.tipo == FIN:
                pasos.append((paso, pila_txt, entrada, "ACEPTAR"))
                return True, pasos, None
            pasos.append((paso, pila_txt, entrada, "ERROR"))
            return False, pasos, (
                "Error sintactico en linea %d, columna %d: se encontro '%s' "
                "pero la instruccion ya estaba completa."
                % (tok.linea, tok.columna, tok.valor))
        if es_terminal(cima):
            if cima == tok.tipo:
                pasos.append((paso, pila_txt, entrada, "coincide '%s'" % cima))
                pila.pop()
                i += 1
                continue
            pasos.append((paso, pila_txt, entrada, "ERROR"))
            return False, pasos, (
                "Error sintactico en linea %d, columna %d: se esperaba '%s' "
                "pero se encontro '%s'."
                % (tok.linea, tok.columna, cima, tok.valor))
        produccion = tabla.get((cima, tok.tipo))
        if produccion is None:
            pasos.append((paso, pila_txt, entrada, "ERROR"))
            return False, pasos, (
                "Error sintactico en linea %d, columna %d: token '%s' inesperado; "
                "se esperaba uno de: %s"
                % (tok.linea, tok.columna, tok.valor, esperados(tabla, cima)))
        _izq, cuerpo = PRODUCCIONES[produccion]
        cuerpo_txt = " ".join(cuerpo) if cuerpo else EPS
        pasos.append((paso, pila_txt, entrada,
                      "P%d: %s -> %s" % (produccion + 1, cima, cuerpo_txt)))
        pila.pop()
        for simbolo in reversed(cuerpo):
            pila.append(simbolo)


def analizar_y_mostrar(texto, tabla, linea=1, mostrar_traza=True):
    """Tokeniza, analiza y muestra el resultado completo de una instruccion.

    Devuelve True si la instruccion fue aceptada.
    """
    texto_limpio = texto.strip()
    print("Instruccion (%d): %s" % (linea, texto_limpio))
    try:
        tokens = tokenizar(texto, linea)
    except ErrorSintactico as error:
        print(str(error))
        print(">>> RESULTADO: instruccion RECHAZADA (error lexico)\n")
        return False
    tokens.append(Token(FIN, FIN, linea, len(texto) + 1))
    aceptada, pasos, mensaje_error = analizar_tokens(tokens, tabla)
    if mostrar_traza:
        imprimir_traza(pasos)
    if aceptada:
        print(">>> RESULTADO: instruccion ACEPTADA. "
              "La cadena SI pertenece al lenguaje generado por la gramatica.\n")
    else:
        print(">>> %s" % mensaje_error)
        print(">>> RESULTADO: instruccion RECHAZADA. "
              "La cadena NO pertenece al lenguaje generado por la gramatica.\n")
    return aceptada
```

<a id="reporter"></a>

## reporter.py

```python
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
```

<a id="runner"></a>

## runner.py

```python
# -*- coding: utf-8 -*-
"""
runner.py
Modos de ejecucion del analizador: analisis desde un archivo de texto,
analisis desde el teclado y menu interactivo.
"""

from parser import analizar_y_mostrar
from reporter import (
    imprimir_conjuntos,
    imprimir_producciones,
    imprimir_tabla,
)


def analizar_archivo(ruta, tabla):
    """Analiza cada linea no vacia y sin comentario '#' del archivo ruta."""
    try:
        with open(ruta, "r", encoding="utf-8-sig") as archivo:
            lineas = archivo.read().splitlines()
    except OSError as error:
        print("No se pudo abrir el archivo: %s" % error)
        return
    aceptadas = 0
    total = 0
    for numero, linea in enumerate(lineas, 1):
        texto = linea.strip()
        if not texto or texto.startswith("#"):
            continue
        total += 1
        if analizar_y_mostrar(texto, tabla, numero):
            aceptadas += 1
    print("=" * 60)
    print("RESUMEN: %d de %d instrucciones ACEPTADAS." % (aceptadas, total))
    print("=" * 60)


def modo_teclado(tabla):
    """Modo interactivo: lee instrucciones del teclado hasta linea vacia."""
    print("Escriba una instruccion y presione ENTER (linea vacia para terminar):\n")
    while True:
        try:
            texto = input("instruccion> ")
        except EOFError:
            break
        if not texto.strip():
            break
        analizar_y_mostrar(texto, tabla, 1)


def menu(tabla, primero, siguiente):
    """Menu principal del analizador."""
    while True:
        print("==============================================================")
        print("   ANALIZADOR SINTACTICO PREDICTIVO NO RECURSIVO")
        print("   Instrucciones: map, filter y reduce (Python)")
        print("==============================================================")
        print("  1) Analizar una instruccion desde el teclado")
        print("  2) Analizar instrucciones desde un archivo de texto")
        print("  3) Mostrar conjuntos PRIMERO y SIGUIENTE")
        print("  4) Mostrar tabla de analisis predictivo")
        print("  5) Mostrar producciones de la gramatica")
        print("  0) Salir")
        try:
            opcion = input("Opcion: ").strip()
        except EOFError:
            break
        print()
        if opcion == "1":
            modo_teclado(tabla)
        elif opcion == "2":
            try:
                ruta = input("Ruta del archivo: ").strip()
            except EOFError:
                ruta = ""
            if ruta:
                print()
                analizar_archivo(ruta, tabla)
        elif opcion == "3":
            imprimir_conjuntos(primero, siguiente)
        elif opcion == "4":
            imprimir_tabla(tabla)
            imprimir_producciones()
        elif opcion == "5":
            imprimir_producciones()
        elif opcion == "0":
            break
        else:
            print("Opcion no valida.\n")
```

<a id="tabla"></a>

## tabla.py

```python
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
```

<a id="verificar"></a>

## verificar.py

```python
# -*- coding: utf-8 -*-
"""
verificar.py
Pruebas automaticas del analizador (modular).

Verifica que la gramatica y el analizador cuenten con:
  1. lambda: expresiones lambda de Python (1 y 2 parametros) en FUNCION.
  2. lambda (cadena vacia): producciones vacias eps de MAS_ITERABLES,
     MAS_PARAMETROS, EXPRESION', TERMINO', ELEMENTOS_OPT y MAS_ELEMENTOS.
  3. operaciones con listas: literales [1,2,3], lista vacia [] y la
     produccion LISTA con ELEMENTOS/MAS_ELEMENTOS.
  4. operaciones de orden superior: map, filter y reduce recibiendo
     como argumento una funcion (lambda o identificador).

Ejecutar:  python verificar.py
"""

from conjuntos import calcular_primero, calcular_siguiente
from lexer import ErrorSintactico, Token, tokenizar
from gramatica import FIN, PRODUCCIONES, producciones_eps
from parser import analizar_tokens
from tabla import construir_tabla

CASOS = [
    # (instruccion, se_espera_aceptada, caracteristica_que_cubre)
    ("map(lambda x: x*2, [1,2,3])",              True,  "lambda + listas + orden superior (map)"),
    ("filter(lambda n: n>=5, numeros)",          True,  "lambda + orden superior (filter)"),
    ("reduce(lambda a,b: a+b, range(1,10))",     True,  "lambda de 2 parametros + orden superior (reduce)"),
    ("reduce(lambda a,b: a+b, [1,2,3,4], 100)",  True,  "lambda de 2 parametros + valor inicial (3er arg)"),
    ("map(multiplicar, lista1, lista2)",         True,  "orden superior: funcion por nombre en map"),
    ("reduce(sumar, [1,2,3,4], 100)",            True,  "orden superior: funcion por nombre en reduce"),
    ("filter(lambda n: n>=5, [3,7,4,9])",        True,  "lambda con comparacion + lista literal"),
    ("map(lambda x: x, [])",                     True,  "produccion vacia eps (lista vacia)"),
    ("map(lambda x, y: x+y, a, b)",              True,  "lambda con 2 parametros (MAS_PARAMETROS)"),
    ("map(lambda x: x*(1+2), [1,2,3])",          True,  "expresion entre parentesis (FACTOR)"),
    ("map(lambda x: x/2-1, [1,2,3])",            True,  "expresion con division y resta"),
    ("map(lambda x: x+1, [1,2,3], [4,5,6])",     True,  "map con 2 iterables (MAS_ITERABLES)"),
    ("filter(lambda n: n<=9, range(1,10))",      True,  "iterable range"),
    ("map(lambda x: x*2 [1,2,3])",               False, "error: falta la coma entre argumentos"),
    ("filter(lambda n: n>=5, [3,7,4,9]",         False, "error: falta el parentesis de cierre"),
    ("reduce(lambda a b: a+b, range(1,10))",     False, "error: falta la coma entre parametros"),
    ("map(2, [1,2,3])",                          False, "error: el primer argumento no es funcion"),
]


def construir():
    primero = calcular_primero()
    siguiente = calcular_siguiente(primero)
    tabla, conflictos = construir_tabla(primero, siguiente)
    return tabla, conflictos


def analizar_silencioso(texto, tabla):
    try:
        tokens = tokenizar(texto, 1)
    except ErrorSintactico:
        return False
    tokens.append(Token(FIN, FIN, 1, len(texto) + 1))
    aceptada, _pasos, _error = analizar_tokens(tokens, tabla)
    return aceptada


def verificar_estructura():
    """Verifica que la gramatica tenga lambda, eps, listas y orden superior."""
    print("VERIFICACION DE LA ESTRUCTURA DE LA GRAMATICA")
    print("-" * 70)
    eps_nums = producciones_eps()
    nombres_eps = sorted({izq for i, (izq, cuerpo) in enumerate(PRODUCCIONES)
                          if not cuerpo})
    print("Producciones vacias (lambda/eps): P%s (%s)"
          % (", P".join(str(n) for n in eps_nums), ", ".join(nombres_eps)))
    tiene_lambda = any(cuerpo and cuerpo[0] == "lambda" for _i, cuerpo in PRODUCCIONES)
    tiene_lista = any(izq == "LISTA" for izq, _c in PRODUCCIONES)
    tiene_orden = any(izq in ("MAP", "FILTER", "REDUCE")
                      for izq, _c in PRODUCCIONES)
    print("Produccion FUNCION -> lambda PARAMETROS : EXPRESION: %s"
          % ("SI" if tiene_lambda else "NO"))
    print("Produccion LISTA -> [ ELEMENTOS_OPT ]  : %s"
          % ("SI" if tiene_lista else "NO"))
    print("Instrucciones de orden superior (map, filter, reduce): %s"
          % ("SI" if tiene_orden else "NO"))
    print()
    return tiene_lambda and tiene_lista and tiene_orden and len(eps_nums) == 6


def main():
    tabla, conflictos = construir()
    print("=" * 70)
    print("VERIFICACION DEL ANALIZADOR PREDICTIVO NO RECURSIVO (MODULAR)")
    print("=" * 70)
    print()
    if conflictos:
        print("La gramatica NO es LL(1). Conflictos:")
        for c in conflictos:
            print("  " + c)
        return
    print("Tabla M[A, a] construida sin conflictos: la gramatica ES LL(1).")
    print()

    estructura_ok = verificar_estructura()

    print("PRUEBAS DE ACEPTACION / RECHAZO")
    print("-" * 70)
    print("%-3s %-45s %-9s %s" % ("#", "INSTRUCCION", "ESPERADO", "RESULTADO"))
    print("-" * 70)
    fallidos = 0
    for numero, (texto, esperado, cobertura) in enumerate(CASOS, 1):
        aceptada = analizar_silencioso(texto, tabla)
        correcto = (aceptada == esperado)
        if not correcto:
            fallidos += 1
        print("%-3d %-45s %-9s %s  [%s]"
              % (numero, texto, "ACEPTAR" if esperado else "RECHAZAR",
                 "OK" if correcto else "FALLO", cobertura))
    print("-" * 70)
    total = len(CASOS)
    print("RESUMEN: %d de %d pruebas correctas." % (total - fallidos, total))
    print("Estructura (lambda, eps, listas, orden superior): %s"
          % ("OK" if estructura_ok else "INCOMPLETA"))
    print("=" * 70)
    if fallidos or not estructura_ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
```
