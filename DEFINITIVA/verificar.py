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
