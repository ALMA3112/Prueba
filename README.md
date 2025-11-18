# Compilador con Tabla de Símbolos y Código de 3 Direcciones

## Descripción del Proyecto

Este proyecto implementa un **compilador completo** para un lenguaje de programación. El compilador incluye todas las fases de análisis y generación de código, desde el análisis léxico hasta la generación de código intermedio en tres direcciones.

### Características Principales

-  **Analizador Léxico (Lexer)**: Tokenización del código fuente
-  **Analizador Sintáctico (Parser)**: Construcción del AST mediante análisis descendente recursivo
-  **Tabla de Símbolos**: Gestión de declaraciones, tipos y alcances
-  **Generador de Código de 3 Direcciones**: Representación intermedia del código
-  **Análisis Semántico**: Verificación de tipos y declaraciones
-  **Visualizaciones**: Generación automática de imágenes del AST, tabla de símbolos, gramática, FIRST/FOLLOW y ETDs

## Requisitos de la Asignación

### Gramática Implementada
El proyecto implementa una gramática completa para un lenguaje imperativo con:
- Declaraciones de variables (int, float, bool)
- Asignaciones
- Estructuras de control (if/else, while)
- Expresiones aritméticas y relacionales
- Instrucción print

###  Tabla de Símbolos
Implementación completa de tabla de símbolos con:
- Gestión de múltiples ámbitos (scopes)
- Verificación de declaraciones
- Control de inicialización de variables
- Tipos de datos asociados

###  Código de 3 Direcciones
Generación de representación intermedia (AST_D) con:
- Asignaciones temporales
- Etiquetas para control de flujo
- Instrucciones condicionales
- Instrucciones de salto

##  Uso del Compilador

### Ejecución Básica

```bash
python prueba1.py
```

### Modificar el Programa de Entrada

Edita la variable `programa_prueba` en el código:

```python
programa_prueba = """
int x, y;
x = 2 + 3 * 4;
y = x - 5;
if ( y > 10 ) { 
    print(x); 
} else { 
    print(y); 
}
"""
```

### Salidas Generadas

El compilador genera automáticamente los siguientes archivos:

1. **P3_Conjuntos.png** - Conjuntos FIRST y FOLLOW
2. **P4_AST.png** - Árbol de Sintaxis Abstracta
3. **P5_Tabla.png** - Tabla de Símbolos
4. **P5_Codigo3D.png** - Código de 3 direcciones (imagen)
5. **codigo_3dir.txt** - Código de 3 direcciones (texto)
6. **P6_Gramatica.png** - Gramática del lenguaje
7. **P7_ETDS.png** - Esquemas de Traducción Dirigida por Sintaxis

##  Gramática del Lenguaje

### Producciones

```
P           → BLOQUE
BLOQUE      → STMT_LIST
STMT_LIST   → STMT STMT_LIST | ε
STMT        → DECLARACION ; 
            | ASIGNACION ; 
            | IF_STMT 
            | WHILE_STMT 
            | PRINT_STMT ; 
            | { BLOQUE }

DECLARACION → TIPO LIST_IDS
LIST_IDS    → id LIST_IDS_P
LIST_IDS_P  → , id LIST_IDS_P | ε
TIPO        → int | float | bool

ASIGNACION  → id = EXPR

IF_STMT     → if ( EXPR_REL ) STMT ELSE_PART
ELSE_PART   → else STMT | ε

WHILE_STMT  → while ( EXPR_REL ) STMT

PRINT_STMT  → print ( EXPR )

EXPR        → TERM EXPR_P
EXPR_P      → + TERM EXPR_P | - TERM EXPR_P | ε

TERM        → FACTOR TERM_P
TERM_P      → * FACTOR TERM_P | / FACTOR TERM_P | ε

FACTOR      → ( EXPR ) | num | id

EXPR_REL    → EXPR REL_OP EXPR | EXPR
REL_OP      → == | != | < | > | <= | >=
```


##  Tokens Reconocidos

### Palabras Reservadas
- `int`, `float`, `bool`
- `if`, `else`
- `while`
- `print`

### Operadores
- Aritméticos: `+`, `-`, `*`, `/`
- Relacionales: `==`, `!=`, `<`, `>`, `<=`, `>=`
- Asignación: `=`

### Delimitadores
- `(`, `)` - Paréntesis
- `{`, `}` - Llaves
- `;` - Punto y coma
- `,` - Coma

### Literales
- `num` - Números enteros y flotantes (ej: 42, 3.14)
- `id` - Identificadores (ej: x, count, myVar)

### Comentarios
- `//` - Comentarios de línea


## Arquitectura del Compilador

### 1. Analizador Léxico (`lex`)

**Función**: Convierte el texto fuente en una secuencia de tokens.

**Características**:
- Reconoce palabras reservadas
- Identifica operadores y delimitadores
- Procesa números enteros y flotantes
- Maneja comentarios de línea (`//`)
- Ignora espacios en blanco

**Ejemplo**:
```python
tokens = lex("int x = 5;")
# Resultado: [Token(int,int), Token(id,x), Token(ASIG,=), Token(num,5), Token(PTOCOMA,;), Token(EOF,EOF)]
```

### 2. Analizador Sintáctico (`Parser`)

**Función**: Construye el Árbol de Sintaxis Abstracta (AST).

**Método**: Análisis descendente recursivo (Recursive Descent Parser)

**Clases de Nodos AST**:
- `Programa` - Raíz del árbol
- `Bloque` - Bloque de sentencias
- `Declaracion` - Declaración de variables
- `Asignacion` - Asignación de valores
- `IfStmt` - Estructura if/else
- `WhileStmt` - Bucle while
- `PrintStmt` - Instrucción print
- `BinOp` - Operación binaria
- `Num` - Literal numérico
- `Id` - Identificador

### 3. Tabla de Símbolos (`TablaSimbolos`)

**Función**: Gestiona información sobre variables declaradas.

**Operaciones**:
- `insertar(nombre, tipo)` - Declara una nueva variable
- `buscar(nombre)` - Busca una variable en los ámbitos
- `asignar(nombre)` - Marca una variable como inicializada
- `entrar_ambito()` - Crea un nuevo ámbito
- `salir_ambito()` - Sale del ámbito actual

**Información almacenada**:
- Nombre de la variable
- Tipo de dato (int, float, bool)
- Estado de inicialización
- Nivel de anidamiento

### 4. Generador de Código 3D (`Generador3D`)

**Función**: Genera código intermedio en tres direcciones.

**Características**:
- Genera variables temporales (t1, t2, ...)
- Genera etiquetas (L1, L2, ...)
- Emite instrucciones de 3 direcciones
- Traduce estructuras de control a saltos

**Formato de Instrucciones**:
```
x = y op z          # Operación binaria
x = y               # Asignación
goto L              # Salto incondicional
ifFalse x goto L    # Salto condicional
L:                  # Etiqueta
print x             # Salida
```

**Ejemplo de Salida**:
```
t1 = 3
t2 = 4
t3 = t1 * t2
t4 = 2
t5 = t4 + t3
x = t5
t6 = 5
t7 = x - t6
y = t7
```


##  Ejemplo Completo

### Código Fuente

```c
int x, y;
x = 2 + 3 * 4;
y = x - 5;
if ( y > 10 ) { 
    print(x); 
} else { 
    print(y); 
}
```

### Tokens Generados

```
Token(int,int)
Token(id,x)
Token(COMA,,)
Token(id,y)
Token(PTOCOMA,;)
Token(id,x)
Token(ASIG,=)
...
```

### AST (Estructura)

```
Programa
└── Bloque
    ├── Declaracion:int
    │   ├── id:x
    │   └── id:y
    ├── Asignacion:x
    │   └── Op:+
    │       ├── Num:2
    │       └── Op:*
    │           ├── Num:3
    │           └── Num:4
    ├── Asignacion:y
    │   └── Op:-
    │       ├── Id:x
    │       └── Num:5
    └── If
        ├── Op:>
        │   ├── Id:y
        │   └── Num:10
        ├── Bloque
        │   └── Print
        │       └── Id:x
        └── Bloque
            └── Print
                └── Id:y
```

### Código de 3 Direcciones

```
t1 = 3
t2 = 4
t3 = t1 * t2
t4 = 2
t5 = t4 + t3
x = t5
t6 = 5
t7 = x - t6
y = t7
t8 = y
t9 = 10
t10 = t8 > t9
ifFalse t10 goto L2
t11 = x
print t11
goto L3
L2:
t12 = y
print t12
L3:
```
