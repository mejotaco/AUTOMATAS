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
