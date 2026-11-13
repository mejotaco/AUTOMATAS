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
