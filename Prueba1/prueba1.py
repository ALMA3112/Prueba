import matplotlib.pyplot as plt

class Token:
    def __init__(self,tipo,lexema):
        self.tipo=tipo
        self.lexema=lexema
    def __repr__(self):
        return "Token("+self.tipo+","+self.lexema+")"

def es_letra(c):
    return ('a'<=c<='z') or ('A'<=c<='Z') or c=='_'

def es_digito(c):
    return '0'<=c<='9'

def lex(texto):
    i=0
    n=len(texto)
    tokens=[]
    while i<n:
        c=texto[i]
        if c==' ' or c=='\t' or c=='\r' or c=='\n':
            i+=1
            continue
        if c=='/' and i+1<n and texto[i+1]=='/':
            i+=2
            while i<n and texto[i] != '\n':
                i+=1
            continue
        if es_letra(c):
            start=i
            while i<n and (es_letra(texto[i]) or es_digito(texto[i])):
                i+=1
            lexema=texto[start:i]
            if lexema in ('int','float','bool','if','else','while','print'):
                tokens.append(Token(lexema,lexema))
            else:
                tokens.append(Token('id',lexema))
            continue
        if es_digito(c):
            start=i
            while i<n and es_digito(texto[i]):
                i+=1
            if i<n and texto[i]=='.':
                i+=1
                if i<n and es_digito(texto[i]):
                    while i<n and es_digito(texto[i]):
                        i+=1
                else:
                    raise Exception("Error lexico: punto sin decimales")
            lexema=texto[start:i]
            tokens.append(Token('num',lexema))
            continue
        if c=='=':
            if i+1<n and texto[i+1]=='=':
                tokens.append(Token('EQ','=='))
                i+=2
            else:
                tokens.append(Token('ASIG','='))
                i+=1
            continue
        if c=='!':
            if i+1<n and texto[i+1]=='=':
                tokens.append(Token('NE','!='))
                i+=2
            else:
                raise Exception("Error lexico: '!' no soportado solo")
            continue
        if c=='<':
            if i+1<n and texto[i+1]=='=':
                tokens.append(Token('LE','<='))
                i+=2
            else:
                tokens.append(Token('LT','<'))
                i+=1
            continue
        if c=='>':
            if i+1<n and texto[i+1]=='=':
                tokens.append(Token('GE','>='))
                i+=2
            else:
                tokens.append(Token('GT','>'))
                i+=1
            continue
        if c==';':
            tokens.append(Token('PTOCOMA',';')); i+=1; continue
        if c==',':
            tokens.append(Token('COMA',',')); i+=1; continue
        if c=='{':
            tokens.append(Token('LLAVE_A','{')); i+=1; continue
        if c=='}':
            tokens.append(Token('LLAVE_C','}')); i+=1; continue
        if c=='(':
            tokens.append(Token('PAR_A','(')); i+=1; continue
        if c==')':
            tokens.append(Token('PAR_C',')')); i+=1; continue
        if c=='+':
            tokens.append(Token('MAS','+')); i+=1; continue
        if c=='-':
            tokens.append(Token('MENOS','-')); i+=1; continue
        if c=='*':
            tokens.append(Token('MULT','*')); i+=1; continue
        if c=='/':
            tokens.append(Token('DIV','/')); i+=1; continue
        raise Exception("Error lexico caracter invalido '"+c+"' en posicion "+str(i))
    tokens.append(Token('EOF','EOF'))
    return tokens

class Nodo:
    pass

class Programa(Nodo):
    def __init__(self,bloque):
        self.bloque=bloque

class Bloque(Nodo):
    def __init__(self,stmts):
        self.stmts=stmts

class Declaracion(Nodo):
    def __init__(self,tipo,ids):
        self.tipo=tipo
        self.ids=ids

class Asignacion(Nodo):
    def __init__(self,ident,expr):
        self.ident=ident
        self.expr=expr

class IfStmt(Nodo):
    def __init__(self,cond,thenp,elsep):
        self.cond=cond
        self.thenp=thenp
        self.elsep=elsep

class WhileStmt(Nodo):
    def __init__(self,cond,body):
        self.cond=cond
        self.body=body

class PrintStmt(Nodo):
    def __init__(self,expr):
        self.expr=expr

class BinOp(Nodo):
    def __init__(self,op,left,right):
        self.op=op
        self.left=left
        self.right=right
        self.type=None
        self.addr=None

class Num(Nodo):
    def __init__(self,valor):
        self.valor=valor
        self.type='int' if '.' not in valor else 'float'
        self.addr=None

class Id(Nodo):
    def __init__(self,nombre):
        self.nombre=nombre
        self.type=None
        self.addr=None

class Parser:
    def __init__(self,tokens):
        self.tokens=tokens
        self.pos=0
        self.actual=self.tokens[self.pos]
    def consumir(self,tipo=None):
        if tipo and self.actual.tipo!=tipo:
            raise Exception("Error sintactico: se esperaba "+str(tipo)+" y vino "+str(self.actual.tipo))
        val=self.actual
        self.pos+=1
        if self.pos<len(self.tokens):
            self.actual=self.tokens[self.pos]
        return val
    def parse(self):
        bloque=self.parse_BLOQUE()
        if self.actual.tipo!='EOF':
            raise Exception("Error: tokens sobrantes")
        return Programa(bloque)
    def parse_BLOQUE(self):
        stmts=self.parse_STMT_LIST()
        return Bloque(stmts)
    def parse_STMT_LIST(self):
        stmts=[]
        while self.actual.tipo not in ('EOF','LLAVE_C'):
            if self.actual.tipo=='PTOCOMA':
                self.consumir('PTOCOMA')
                continue
            stmts.append(self.parse_STMT())
        return stmts
    def parse_STMT(self):
        if self.actual.tipo in ('int','float','bool'):
            decl=self.parse_DECLARACION()
            self.consumir('PTOCOMA')
            return decl
        if self.actual.tipo=='id' and self.pos+1<len(self.tokens) and self.tokens[self.pos+1].tipo=='ASIG':
            asign=self.parse_ASIGNACION()
            self.consumir('PTOCOMA')
            return asign
        if self.actual.tipo=='if':
            return self.parse_IF()
        if self.actual.tipo=='while':
            return self.parse_WHILE()
        if self.actual.tipo=='print':
            pr=self.parse_PRINT()
            self.consumir('PTOCOMA')
            return pr
        if self.actual.tipo=='LLAVE_A':
            self.consumir('LLAVE_A')
            bloque=self.parse_BLOQUE()
            self.consumir('LLAVE_C')
            return bloque
        raise Exception("Error sintactico inicio de sentencia: "+str(self.actual))
    def parse_DECLARACION(self):
        tipo=self.consumir().lexema
        ids=[self.consumir('id').lexema]
        while self.actual.tipo=='COMA':
            self.consumir('COMA')
            ids.append(self.consumir('id').lexema)
        return Declaracion(tipo,ids)
    def parse_ASIGNACION(self):
        idt=self.consumir('id').lexema
        self.consumir('ASIG')
        expr=self.parse_EXPR_REL()
        return Asignacion(idt,expr)
    def parse_IF(self):
        self.consumir('if')
        self.consumir('PAR_A')
        cond=self.parse_EXPR_REL()
        self.consumir('PAR_C')
        thenp=self.parse_STMT()
        elsep=None
        if self.actual.tipo=='else':
            self.consumir('else')
            elsep=self.parse_STMT()
        return IfStmt(cond,thenp,elsep)
    def parse_WHILE(self):
        self.consumir('while')
        self.consumir('PAR_A')
        cond=self.parse_EXPR_REL()
        self.consumir('PAR_C')
        body=self.parse_STMT()
        return WhileStmt(cond,body)
    def parse_PRINT(self):
        self.consumir('print')
        self.consumir('PAR_A')
        expr=self.parse_EXPR()
        self.consumir('PAR_C')
        return PrintStmt(expr)
    def parse_EXPR_REL(self):
        left=self.parse_EXPR()
        if self.actual.tipo in ('EQ','NE','LT','GT','LE','GE'):
            op=self.consumir().lexema
            right=self.parse_EXPR()
            return BinOp(op,left,right)
        return left
    def parse_EXPR(self):
        node=self.parse_TERM()
        while self.actual.tipo in ('MAS','MENOS'):
            op=self.consumir().lexema
            right=self.parse_TERM()
            node=BinOp(op,node,right)
        return node
    def parse_TERM(self):
        node=self.parse_FACTOR()
        while self.actual.tipo in ('MULT','DIV'):
            op=self.consumir().lexema
            right=self.parse_FACTOR()
            node=BinOp(op,node,right)
        return node
    def parse_FACTOR(self):
        if self.actual.tipo=='PAR_A':
            self.consumir('PAR_A')
            nodo=self.parse_EXPR()
            self.consumir('PAR_C')
            return nodo
        if self.actual.tipo=='num':
            val=self.consumir('num').lexema
            return Num(val)
        if self.actual.tipo=='id':
            nombre=self.consumir('id').lexema
            return Id(nombre)
        raise Exception("Error sintactico factor: "+str(self.actual))

class TablaSimbolos:
    def __init__(self):
        self.pila=[{}]
    def entrar_ambito(self):
        self.pila.append({})
    def salir_ambito(self):
        if len(self.pila)>1:
            self.pila.pop()
        else:
            raise Exception("Error: salir_ambito en nivel 0")
    def insertar(self,nombre,tipo):
        if nombre in self.pila[-1]:
            raise Exception("Error semantico: redeclaracion de "+nombre)
        self.pila[-1][nombre]={'tipo':tipo,'inicializado':False}
    def asignar(self,nombre):
        for scope in reversed(self.pila):
            if nombre in scope:
                scope[nombre]['inicializado']=True
                return scope[nombre]
        raise Exception("Error semantico: variable no declarada "+nombre)
    def buscar(self,nombre):
        for scope in reversed(self.pila):
            if nombre in scope:
                return scope[nombre]
        return None
    def todas(self):
        res=[]
        nivel=0
        for scope in self.pila:
            for k,v in scope.items():
                res.append((k,v['tipo'],v['inicializado'],nivel))
            nivel+=1
        return res

class Generador3D:
    def __init__(self):
        self.temporal=0
        self.etiqueta=0
        self.codigo=[]
    def nuevo_temp(self):
        self.temporal+=1
        return "t"+str(self.temporal)
    def nueva_etiqueta(self):
        self.etiqueta+=1
        return "L"+str(self.etiqueta)
    def emit(self,instr):
        self.codigo.append(instr)
    def generar(self,nodo,ts):
        if isinstance(nodo,Programa):
            self.generar(nodo.bloque,ts)
        elif isinstance(nodo,Bloque):
            for s in nodo.stmts:
                self.generar(s, ts)
        elif isinstance(nodo,Declaracion):
            for idn in nodo.ids:
                ts.insertar(idn,nodo.tipo)
        elif isinstance(nodo,Asignacion):
            info=ts.buscar(nodo.ident)
            if not info:
                raise Exception("Error semantico: "+nodo.ident+" no declarado")
            dir_expr=self.generar(nodo.expr,ts)
            self.emit(nodo.ident+" = "+dir_expr)
            ts.asignar(nodo.ident)
        elif isinstance(nodo,IfStmt):
            cond=self.generar(nodo.cond,ts)
            Lf=self.nueva_etiqueta()
            Ls=self.nueva_etiqueta()
            self.emit("ifFalse "+cond+" goto "+Lf)
            self.generar(nodo.thenp,ts)
            self.emit("goto "+Ls)
            self.emit(Lf+":")
            if nodo.elsep:
                self.generar(nodo.elsep,ts)
            self.emit(Ls+":")
        elif isinstance(nodo,WhileStmt):
            Li=self.nueva_etiqueta()
            Lf=self.nueva_etiqueta()
            self.emit(Li+":")
            cond=self.generar(nodo.cond,ts)
            self.emit("ifFalse "+cond+" goto "+Lf)
            self.generar(nodo.body,ts)
            self.emit("goto "+Li)
            self.emit(Lf+":")
        elif isinstance(nodo,PrintStmt):
            dirr=self.generar(nodo.expr,ts)
            self.emit("print "+dirr)
        elif isinstance(nodo,BinOp):
            l=self.generar(nodo.left,ts)
            r=self.generar(nodo.right,ts)
            t=self.nuevo_temp()
            self.emit(t+" = "+l+" "+nodo.op+" "+r)
            return t
        elif isinstance(nodo,Num):
            t=self.nuevo_temp()
            self.emit(t+" = "+nodo.valor)
            return t
        elif isinstance(nodo,Id):
            info=ts.buscar(nodo.nombre)
            if not info:
                raise Exception("Error semantico: "+nodo.nombre+" no declarado")
            return nodo.nombre

class NodoAST:
    def __init__(self, texto):
        self.texto = texto
        self.hijos = []

    def agregar_hijo(self, n):
        self.hijos.append(n)

def convertir_ast_a_formato_grafico(nodo):
    if isinstance(nodo, Programa):
        raiz = NodoAST("Programa")
        raiz.agregar_hijo(convertir_ast_a_formato_grafico(nodo.bloque))
        return raiz
    if isinstance(nodo, Bloque):
        n = NodoAST("Bloque")
        for s in nodo.stmts:
            n.agregar_hijo(convertir_ast_a_formato_grafico(s))
        return n
    if isinstance(nodo, Declaracion):
        n = NodoAST("Declaracion:"+nodo.tipo)
        for idn in nodo.ids:
            n.agregar_hijo(NodoAST("id:"+idn))
        return n
    if isinstance(nodo, Asignacion):
        n = NodoAST("Asignacion:"+nodo.ident)
        n.agregar_hijo(convertir_ast_a_formato_grafico(nodo.expr))
        return n
    if isinstance(nodo, IfStmt):
        n = NodoAST("If")
        n.agregar_hijo(convertir_ast_a_formato_grafico(nodo.cond))
        then_n = convertir_ast_a_formato_grafico(nodo.thenp)
        n.agregar_hijo(then_n)
        if nodo.elsep:
            else_n = convertir_ast_a_formato_grafico(nodo.elsep)
            n.agregar_hijo(else_n)
        return n
    if isinstance(nodo, WhileStmt):
        n = NodoAST("While")
        n.agregar_hijo(convertir_ast_a_formato_grafico(nodo.cond))
        n.agregar_hijo(convertir_ast_a_formato_grafico(nodo.body))
        return n
    if isinstance(nodo, PrintStmt):
        n = NodoAST("Print")
        n.agregar_hijo(convertir_ast_a_formato_grafico(nodo.expr))
        return n
    if isinstance(nodo, BinOp):
        n = NodoAST("Op:"+nodo.op)
        n.agregar_hijo(convertir_ast_a_formato_grafico(nodo.left))
        n.agregar_hijo(convertir_ast_a_formato_grafico(nodo.right))
        return n
    if isinstance(nodo, Num):
        return NodoAST("Num:"+nodo.valor)
    if isinstance(nodo, Id):
        return NodoAST("Id:"+nodo.nombre)
    return NodoAST(str(type(nodo).__name__))

def dibujar_ast_en_arbol(nodo, archivo):
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.axis("off")

    # Calcula el ancho del subárbol
    def ancho(n):
        if not n.hijos:
            return 1
        return sum(ancho(h) for h in n.hijos)

    # Asigna posiciones
    def asignar_pos(n, x, y):
        w = ancho(n)
        cx = x + w / 2
        coords[n] = (cx, y)

        offset = x
        for h in n.hijos:
            wh = ancho(h)
            asignar_pos(h, offset, y - 2)
            offset += wh

    coords = {}
    asignar_pos(nodo, 0, 0)

    # Dibujar líneas
    for padre in coords:
        x1, y1 = coords[padre]
        for hijo in padre.hijos:
            x2, y2 = coords[hijo]
            ax.plot([x1, x2], [y1, y2], color="black")

    # Dibujar nodos
    for node, (x, y) in coords.items():
        texto = node.texto if hasattr(node, "texto") else str(node)
        ax.text(
            x, y, texto,
            ha="center", va="center",
            fontsize=12,
            family="monospace",
            bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="black")
        )

    plt.savefig(archivo, dpi=200, bbox_inches="tight")
    plt.close()

def dibujar_texto_en_imagen(texto, archivo, anchura=12, altura=16, tamano=18):
    max_caracteres = 100
    lineas = texto.split("\n")
    nuevas_lineas = []
    for linea in lineas:
        while len(linea) > max_caracteres:
            nuevas_lineas.append(linea[:max_caracteres])
            linea = linea[max_caracteres:]
        nuevas_lineas.append(linea)
    texto_final = "\n".join(nuevas_lineas)
    fig = plt.figure(figsize=(anchura, altura))
    plt.axis('off')
    fig.text(
        0.02,
        0.98,
        texto_final,
        ha='left',
        va='top',
        family='monospace',
        fontsize=tamano
    )
    plt.savefig(archivo, bbox_inches='tight', dpi=200)
    plt.close(fig)

def dibujar_tabla_sim(ts,archivo):
    datos=ts.todas()
    if len(datos)==0:
        fig=plt.figure(figsize=(6,2))
        fig.text(0.01,0.99,"Tabla de simbolos vacia",ha='left',va='top',family='monospace',size=12)
        plt.axis('off')
        plt.savefig(archivo,bbox_inches='tight')
        plt.close(fig)
        return
    columnas=["Nombre","Tipo","Inicializado","Nivel"]
    filas=[]
    for e in datos:
        filas.append([str(e[0]),str(e[1]),str(e[2]),str(e[3])])
    nrows=len(filas)
    fig=plt.figure(figsize=(6, max(2,nrows*0.5)))
    ax=fig.add_subplot(111)
    ax.axis('off')
    tabla=ax.table(cellText=filas, colLabels=columnas, loc='center')
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(10)
    tabla.scale(1,1.2)
    plt.savefig(archivo,bbox_inches='tight')
    plt.close(fig)

def calcular_first_follow(gram):
    first={}
    follow={}
    for A in gram:
        first[A]=set()
        follow[A]=set()
    def es_terminal(x):
        return x not in gram
    changed=True
    while changed:
        changed=False
        for A,prods in gram.items():
            for prod in prods:
                if len(prod)==0:
                    if '' not in first[A]:
                        first[A].add('')
                        changed=True
                    continue
                i=0
                while True:
                    X=prod[i]
                    if es_terminal(X):
                        if X not in first[A]:
                            first[A].add(X)
                            changed=True
                        break
                    else:
                        antes=len(first[A])
                        for x in first[X]:
                            if x!='':
                                first[A].add(x)
                        if '' in first[X]:
                            i+=1
                            if i>=len(prod):
                                if '' not in first[A]:
                                    first[A].add('')
                                    changed=True
                                break
                            continue
                        if len(first[A])!=antes:
                            changed=True
                        break
    primera_lista=list(gram.keys())[0]
    follow[primera_lista].add('EOF')
    changed=True
    while changed:
        changed=False
        for A,prods in gram.items():
            for prod in prods:
                for i,B in enumerate(prod):
                    if B in gram:
                        j=i+1
                        while True:
                            if j>=len(prod):
                                antes=len(follow[B])
                                for x in follow[A]:
                                    follow[B].add(x)
                                if len(follow[B])!=antes:
                                    changed=True
                                break
                            beta=prod[j]
                            if beta in gram:
                                antes=len(follow[B])
                                for x in first[beta]:
                                    if x!='':
                                        follow[B].add(x)
                                if '' in first[beta]:
                                    j+=1
                                    continue
                                if len(follow[B])!=antes:
                                    changed=True
                                break
                            else:
                                antes=len(follow[B])
                                follow[B].add(beta)
                                if len(follow[B])!=antes:
                                    changed=True
                                break
    return first,follow

def dibujar_first_follow(gram, archivo):
    first, follow = calcular_first_follow(gram)

    lineas = []
    lineas.append("FIRST:")
    for nt in gram:
        lineas.append(f"{nt} : {{ {', '.join(sorted(first[nt]))} }}")

    lineas.append("\nFOLLOW:")
    for nt in gram:
        lineas.append(f"{nt} : {{ {', '.join(sorted(follow[nt]))} }}")

    texto = "\n".join(lineas)

    dibujar_texto_en_imagen(
        texto,
        archivo,
        anchura=10,
        altura=12,
        tamano=12
    )


def dict_gramatica():
    G={}
    G['P']=[['BLOQUE']]
    G['BLOQUE']=[['STMT_LIST']]
    G['STMT_LIST']=[['STMT','STMT_LIST'],[]]
    G['STMT']=[['DECLARACION',';'],['ASIGNACION',';'],['IF_STMT'],['WHILE_STMT'],['PRINT_STMT',';'],['{','BLOQUE','}']]
    G['DECLARACION']=[['TIPO','LIST_IDS']]
    G['LIST_IDS']=[['id','LIST_IDS_P']]
    G['LIST_IDS_P']=[[',','id','LIST_IDS_P'],[]]
    G['TIPO']=[['int'],['float'],['bool']]
    G['ASIGNACION']=[['id','=','EXPR']]
    G['IF_STMT']=[['if','(','EXPR_REL',')','STMT','ELSE_PART']]
    G['ELSE_PART']=[['else','STMT'],[]]
    G['WHILE_STMT']=[['while','(','EXPR_REL',')','STMT']]
    G['PRINT_STMT']=[['print','(','EXPR',')']]
    G['EXPR']=[['TERM','EXPR_P']]
    G['EXPR_P']=[['+','TERM','EXPR_P'],['-','TERM','EXPR_P'],[]]
    G['TERM']=[['FACTOR','TERM_P']]
    G['TERM_P']=[['*','FACTOR','TERM_P'],['/','FACTOR','TERM_P'],[]]
    G['FACTOR']=[['(','EXPR',')'],['num'],['id']]
    G['EXPR_REL']=[['EXPR','REL_OP','EXPR'],['EXPR']]
    G['REL_OP']=[['=='],['!='],['<'],['>'],['<='],['>=']]
    return G

def texto_gramatica():
    lines=[]
    lines.append("P -> BLOQUE")
    lines.append("BLOQUE -> STMT_LIST")
    lines.append("STMT_LIST -> STMT STMT_LIST | epsilon")
    lines.append("STMT -> DECLARACION ; | ASIGNACION ; | IF_STMT | WHILE_STMT | PRINT_STMT ; | { BLOQUE }")
    lines.append("DECLARACION -> TIPO LIST_IDS")
    lines.append("LIST_IDS -> id LIST_IDS_P")
    lines.append("LIST_IDS_P -> , id LIST_IDS_P | epsilon")
    lines.append("TIPO -> int | float | bool")
    lines.append("ASIGNACION -> id = EXPR")
    lines.append("IF_STMT -> if ( EXPR_REL ) STMT ELSE_PART")
    lines.append("ELSE_PART -> else STMT | epsilon")
    lines.append("WHILE_STMT -> while ( EXPR_REL ) STMT")
    lines.append("PRINT_STMT -> print ( EXPR )")
    lines.append("EXPR -> TERM EXPR_P")
    lines.append("EXPR_P -> + TERM EXPR_P | - TERM EXPR_P | epsilon")
    lines.append("TERM -> FACTOR TERM_P")
    lines.append("TERM_P -> * FACTOR TERM_P | / FACTOR TERM_P | epsilon")
    lines.append("FACTOR -> ( EXPR ) | num | id")
    lines.append("EXPR_REL -> EXPR REL_OP EXPR | EXPR")
    lines.append("REL_OP -> == | != | < | > | <= | >=")
    return "\n".join(lines)

def texto_etds():
    lines=[]
    lines.append("DECLARACION -> TIPO LIST_IDS { insertar cada id en tabla con TIPO }")
    lines.append("ASIGNACION -> id = EXPR { comprobar id declarado; emit(id = EXPR.addr) }")
    lines.append("IF_STMT -> if ( EXPR_REL ) STMT ELSE_PART { etiquetas y saltos }")
    lines.append("WHILE_STMT -> while ( EXPR_REL ) STMT { etiquetas y saltos }")
    lines.append("PRINT -> print ( EXPR ) { emit(print addr) }")
    return "\n".join(lines)

def guardar_codigo_txt(codigo,archivo):
    f=open(archivo,"w")
    for l in codigo:
        f.write(l+"\n")
    f.close()

programa_prueba="""
int x, y;
x = 2 + 3 * 4;
y = x - 5;
if ( y > 10 ) { print(x); } else { print(y); }
"""

if __name__ == '__main__':
    
    # Programa de prueba
    programa_prueba = """
    int x, y;
    x = 2 + 3 * 4;
    y = x - 5;
    if ( y > 10 ) { print(x); } else { print(y); }
    """

    # 1. LÉXICO
    tokens = lex(programa_prueba)

    # 2. PARSER
    parser = Parser(tokens)
    ast = parser.parse()

    # 3. TABLA DE SÍMBOLOS REAL (LA ÚNICA QUE USAMOS)
    ts = TablaSimbolos()

    # 4. GENERACIÓN DE CÓDIGO 3D
    gen = Generador3D()
    gen.generar(ast, ts)

    # 5. AST GRÁFICO
    arbol = convertir_ast_a_formato_grafico(ast)
    dibujar_ast_en_arbol(arbol, "P4_AST.png")

    # 6. DIBUJAR TABLA DE SÍMBOLOS FINAL (ts CORRECTA)
    dibujar_tabla_sim(ts, "P5_Tabla.png")

    # 7. GUARDAR CÓDIGO 3D
    guardar_codigo_txt(gen.codigo, "codigo_3dir.txt")
    dibujar_texto_en_imagen("\n".join(gen.codigo), "P5_Codigo3D.png", anchura=6, altura=8, tamano=10)

    # 8. GRAMÁTICA
    dibujar_texto_en_imagen(texto_gramatica(), "P6_Gramatica.png", anchura=8, altura=10, tamano=9)

    # 9. FIRST / FOLLOW
    G = dict_gramatica()
    dibujar_first_follow(G, "P3_Conjuntos.png")

    # 10. ETDS
    dibujar_texto_en_imagen(texto_etds(), "P7_ETDS.png", anchura=8, altura=10, tamano=9)

    print("Generado: P3_Conjuntos.png, P4_AST.png, P5_Tabla.png, codigo_3dir.txt, P5_Codigo3D.png, P6_Gramatica.png, P7_ETDS.png")
