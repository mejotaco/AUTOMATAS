# Analizador Sintáctico Predictivo No Recursivo (LL(1)) — VERSIÓN DEFINITIVA

Proyecto modular extraído del documento `Analizador_LL1_revisado.docx` (sección 10,
Código fuente del programa). El original era un solo archivo (`analizador_predictivo.py`);
aquí está organizado en **módulos** con la misma lógica, misma numeración de producciones
(P1…P43) y los mismos resultados que las capturas del documento.

## Instrucciones reconocidas

Subconjunto de Python: instrucciones de **orden superior** `map`, `filter` y `reduce`,
con **expresiones lambda** (1 o más parámetros), **listas literales** (`[1,2,3]`, `[]`),
iterables (`identificador`, `numero`, `range(n,m)`) y expresiones aritméticas y de
comparación (`+ - * / < > <= >= == !=`).

## Estructura modular

| Archivo        | Responsabilidad |
|----------------|-----------------|
| `gramatica.py` | Gramática final sin recursividad por la izquierda: terminales, 43 producciones numeradas, `EPS` (cadena vacía λ/ε) y helpers. |
| `lexer.py`     | Analizador léxico: `Token`, `ErrorSintactico`, `tokenizar` (línea y columna). |
| `conjuntos.py` | Conjuntos **PRIMERO** y **SIGUIENTE** por punto fijo. |
| `tabla.py`     | Tabla predictiva `M[A, a]` con detección de conflictos LL(1). |
| `parser.py`    | Analizador sintáctico **no recursivo**: pila explícita + tabla, traza paso a paso. |
| `reporter.py`  | Impresión de traza, conjuntos, tabla y producciones. |
| `runner.py`    | Modos de ejecución: archivo, teclado y menú interactivo. |
| `analizador.py`| Punto de entrada (`main`). |
| `verificar.py` | Pruebas automáticas (lambda, eps, listas, orden superior). |
| `pruebas_ok.txt` / `pruebas_error.txt` | Archivos de entrada de ejemplo. |
| `Analizador_LL1_revisado.docx` | Documento fuente de referencia. |

## Uso

```bat
python analizador.py              :: menu interactivo (opciones 1 a 5)
python analizador.py pruebas_ok.txt
python analizador.py pruebas_error.txt
python verificar.py               :: 17 pruebas automaticas
```

## Verificación de requerimientos (`python verificar.py`)

- **lambda (expresiones)**: producción `FUNCION -> lambda PARAMETROS : EXPRESION` (P11);
  acepta `map(lambda x: x*2, [1,2,3])`, `reduce(lambda a,b: a+b, range(1,10))`, etc.
- **lambda (cadena vacía ε/λ)**: 6 producciones vacías — P10 (`MAS_ITERABLES`),
  P15 (`MAS_PARAMETROS`), P20 (`EXPRESION'`), P24 (`TERMINO'`), P34 (`ELEMENTOS_OPT`),
  P37 (`MAS_ELEMENTOS`); probadas con `map(lambda x: x, [])` entre otros casos.
- **operaciones con listas**: `LISTA -> [ ELEMENTOS_OPT ]` (P32) con
  `ELEMENTOS/MAS_ELEMENTOS`; listas `[1,2,3]`, vacía `[]`, y también como 2º/3º argumento.
- **operaciones de orden superior**: `MAP/FILTER/REDUCE -> map|filter|reduce ( ARGUMENTOS )`
  con `ARGUMENTOS -> FUNCION , ITERABLE MAS_ITERABLES`; la función puede ser un `lambda`
  (P11) o un `identificador` (P12), p. ej. `map(multiplicar, lista1, lista2)`.
- La tabla se construye **sin conflictos** ⇒ la gramática es LL(1).

Resultado: **17 de 17 pruebas correctas**, `4 de 4 ACEPTADAS` con `pruebas_ok.txt`
y `0 de 3 ACEPTADAS` con `pruebas_error.txt` (coincide con las capturas del documento).

## Gramática (producciones principales)

```
S               -> INSTRUCCION
INSTRUCCION     -> MAP | FILTER | REDUCE
MAP             -> map ( ARGUMENTOS )
FILTER          -> filter ( ARGUMENTOS )
REDUCE          -> reduce ( ARGUMENTOS )
ARGUMENTOS      -> FUNCION , ITERABLE MAS_ITERABLES
MAS_ITERABLES   -> , ITERABLE MAS_ITERABLES | eps
FUNCION         -> lambda PARAMETROS : EXPRESION | identificador
PARAMETROS      -> identificador MAS_PARAMETROS
MAS_PARAMETROS  -> , identificador MAS_PARAMETROS | eps
EXPRESION       -> TERMINO EXPRESION'
EXPRESION'      -> + TERMINO EXPRESION' | - TERMINO EXPRESION'
                 | RELACION TERMINO EXPRESION' | eps
TERMINO         -> FACTOR TERMINO'
TERMINO'        -> * FACTOR TERMINO' | / FACTOR TERMINO' | eps
FACTOR          -> identificador | numero | ( EXPRESION )
ITERABLE        -> LISTA | range ( numero , numero ) | identificador | numero
LISTA           -> [ ELEMENTOS_OPT ]
ELEMENTOS_OPT   -> ELEMENTOS | eps
ELEMENTOS       -> numero MAS_ELEMENTOS
MAS_ELEMENTOS   -> , numero MAS_ELEMENTOS | eps
RELACION        -> < | > | <= | >= | == | !=
```

## Referencias

Aho, Lam, Sethi y Ullman (2008). *Compiladores: principios, técnicas y herramientas* (2.ª ed.).
Hopcroft, Motwani y Ullman (2008). *Introducción a la teoría de autómatas, lenguajes y computación* (3.ª ed.).
Python Software Foundation. docs.python.org/3 — `map`, `filter`, `functools.reduce`.
