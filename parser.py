"""
Gramática soportada:
    programa     → declaración*
    declaración  → varDecl | funDecl | sentencia
    varDecl      → "var" IDENTIFICADOR ("=" expresión)? ";"
    funDecl      → "def" IDENTIFICADOR "(" parámetros? ")" bloque
    sentencia    → ifStmt | whileStmt | forStmt | returnStmt | bloque | exprStmt
    ifStmt       → "if" "(" expresión ")" bloque ("else" bloque)?
    whileStmt    → "while" "(" expresión ")" bloque
    forStmt      → "for" "(" exprStmt expresión ";" expresión ")" bloque
    returnStmt   → "return" expresión? ";"
    bloque       → "{" declaración* "}"
    exprStmt     → expresión ";"
    expresión    → asignación
    asignación   → IDENT "=" asignación | comparación
    comparación  → término (("==" | "!=" | "<" | ">" | "<=" | ">=") término)*
    término      → factor (("+" | "-") factor)*
    factor       → primario (("*" | "/") primario)*
    primario     → NUMERO | CADENA | "true" | "false" | IDENT | "(" expresión ")"
"""
from lexer import Token, TipoToken, Lexer
class ErrorSintactico(Exception):
    pass
# ─── Clase Parser ─────────────────────────────────────────────────
class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.posicion = 0
        self.errores = []       
    def _token_actual(self) -> Token:
        return self.tokens[self.posicion]
    def _token_anterior(self) -> Token:
        return self.tokens[self.posicion - 1]
    def _fin_de_archivo(self) -> bool:
        """¿Ya llegamos al final?"""
        return self._token_actual().tipo == TipoToken.EOF
    def _avanzar(self) -> Token:
        token = self._token_actual()
        if not self._fin_de_archivo():
            self.posicion += 1
        return token
    def _verificar(self, tipo: TipoToken) -> bool:
        if self._fin_de_archivo():
            return False
        return self._token_actual().tipo == tipo
    def _coincidir(self, *tipos: TipoToken) -> bool:
        for tipo in tipos:
            if self._verificar(tipo):
                self._avanzar()
                return True
        return False
    def _consumir(self, tipo: TipoToken, mensaje_error: str) -> Token:
        if self._verificar(tipo):
            return self._avanzar()
        token = self._token_actual()
        error_msg = (
            f"Error [Línea {token.linea}, Col {token.columna}]: "
            f"{mensaje_error} "
            f"(se encontró '{token.valor}' [{token.tipo.name}])."
        )
        self.errores.append(error_msg)
        raise ErrorSintactico(error_msg)
    def _sincronizar(self):
        self._avanzar() 
        while not self._fin_de_archivo():
            if self._token_anterior().tipo == TipoToken.PUNTO_Y_COMA:
                return
            if self._token_actual().tipo in (
                TipoToken.VAR,
                TipoToken.DEF,
                TipoToken.IF,
                TipoToken.WHILE,
                TipoToken.FOR,
                TipoToken.RETURN,
            ):
                return
            if self._token_actual().tipo == TipoToken.LLAVE_DER:
                return

            self._avanzar()

    # ══════════════════════════════════════════════════════════════
    #  REGLAS GRAMATICALES - Descenso recursivo
    # ══════════════════════════════════════════════════════════════
    def parsear(self):
        while not self._fin_de_archivo():
            self._declaracion()

        return self.errores
    # ── Declaraciones ─────────────────────────────────────────────
    def _declaracion(self):
        try:
            if self._coincidir(TipoToken.VAR):
                self._var_decl()
            elif self._coincidir(TipoToken.DEF):
                self._fun_decl()
            else:
                self._sentencia()
        except ErrorSintactico:
            self._sincronizar()
    def _var_decl(self):
        self._consumir(TipoToken.IDENTIFICADOR, "Se esperaba un nombre de variable después de 'var'")
        if self._coincidir(TipoToken.ASIGNACION):
            self._expresion()
        self._consumir(TipoToken.PUNTO_Y_COMA, "Se esperaba ';' después de la declaración de variable")
    def _fun_decl(self):
        self._consumir(TipoToken.IDENTIFICADOR, "Se esperaba el nombre de la función después de 'def'")
        self._consumir(TipoToken.PAREN_IZQ, "Se esperaba '(' después del nombre de la función")
        if not self._verificar(TipoToken.PAREN_DER):
            self._consumir(TipoToken.IDENTIFICADOR, "Se esperaba nombre de parámetro")
            while self._coincidir(TipoToken.COMA):
                self._consumir(TipoToken.IDENTIFICADOR, "Se esperaba nombre de parámetro después de ','")
        self._consumir(TipoToken.PAREN_DER, "Se esperaba ')' después de los parámetros")
        self._bloque()
    # ── Sentencias ────────────────────────────────────────────────
    def _sentencia(self):
        if self._coincidir(TipoToken.IF):
            self._if_stmt()
        elif self._coincidir(TipoToken.WHILE):
            self._while_stmt()
        elif self._coincidir(TipoToken.FOR):
            self._for_stmt()
        elif self._coincidir(TipoToken.RETURN):
            self._return_stmt()
        elif self._verificar(TipoToken.LLAVE_IZQ):
            self._bloque()
        else:
            self._expr_stmt()
    def _if_stmt(self):
        self._consumir(TipoToken.PAREN_IZQ, "Se esperaba '(' después de 'if'")
        self._expresion()
        self._consumir(TipoToken.PAREN_DER, "Se esperaba ')' después de la condición del 'if'")
        self._bloque()

        if self._coincidir(TipoToken.ELSE):
            self._bloque()
    def _while_stmt(self):
        self._consumir(TipoToken.PAREN_IZQ, "Se esperaba '(' después de 'while'")
        self._expresion()
        self._consumir(TipoToken.PAREN_DER, "Se esperaba ')' después de la condición del 'while'")
        self._bloque()
    def _for_stmt(self):
        self._consumir(TipoToken.PAREN_IZQ, "Se esperaba '(' después de 'for'")
        self._expr_stmt()           
        self._expresion()          
        self._consumir(TipoToken.PUNTO_Y_COMA, "Se esperaba ';' después de la condición del 'for'")
        self._expresion()          
        self._consumir(TipoToken.PAREN_DER, "Se esperaba ')' después de la cláusula del 'for'")
        self._bloque()

    def _return_stmt(self):
        if not self._verificar(TipoToken.PUNTO_Y_COMA):
            self._expresion()
        self._consumir(TipoToken.PUNTO_Y_COMA, "Se esperaba ';' después de 'return'")

    def _bloque(self):
        
        self._consumir(TipoToken.LLAVE_IZQ, "Se esperaba '{' para iniciar el bloque")

        while not self._verificar(TipoToken.LLAVE_DER) and not self._fin_de_archivo():
            self._declaracion()

        self._consumir(TipoToken.LLAVE_DER, "Se esperaba '}' para cerrar el bloque")

    def _expr_stmt(self):
     
        self._expresion()
        self._consumir(TipoToken.PUNTO_Y_COMA, "Se esperaba ';' al final de la expresión")

    def _expresion(self):
        return self._asignacion()

    def _asignacion(self):
        expr = self._comparacion()

        if self._coincidir(TipoToken.ASIGNACION):
            self._asignacion()  

        return expr

    def _comparacion(self):
        self._termino()
        while self._coincidir(
            TipoToken.IGUAL_IGUAL,
            TipoToken.DIFERENTE,
            TipoToken.MENOR,
            TipoToken.MAYOR,
            TipoToken.MENOR_IGUAL,
            TipoToken.MAYOR_IGUAL,
        ):
            self._termino()
    def _termino(self):
        self._factor()

        while self._coincidir(TipoToken.SUMA, TipoToken.RESTA):
            self._factor()

    def _factor(self):
        self._primario()

        while self._coincidir(TipoToken.MULTIPLICACION, TipoToken.DIVISION):
            self._primario()

    def _primario(self):

        if self._coincidir(TipoToken.NUMERO, TipoToken.CADENA, TipoToken.TRUE, TipoToken.FALSE):
            return

        if self._coincidir(TipoToken.IDENTIFICADOR):
            return

        if self._coincidir(TipoToken.PAREN_IZQ):
            self._expresion()
            self._consumir(TipoToken.PAREN_DER, "Se esperaba ')' para cerrar la expresión")
            return

        token = self._token_actual()
        error_msg = (
            f"Error [Línea {token.linea}, Col {token.columna}]: "
            f"Se esperaba una expresión, se encontró '{token.valor}' [{token.tipo.name}]."
        )
        self.errores.append(error_msg)
        raise ErrorSintactico(error_msg)

if __name__ == "__main__":
    codigo_con_errores = """
var x = 10;
var y = 20

if (x > 5 {
    y = y + 1;
}

while x < 100) {
    x = x * 2;
}

var resultado = x + y;
"""
    print("═══ CÓDIGO FUENTE ═══")
    for i, linea in enumerate(codigo_con_errores.split('\n'), 1):
        print(f"  {i:3d} | {linea}")
    lexer = Lexer(codigo_con_errores)
    tokens = lexer.tokenizar()
    parser = Parser(tokens)
    errores = parser.parsear()
    todos_los_errores = lexer.errores + errores
    print("\n═══ LOG DE ERRORES ═══")
    if todos_los_errores:
        for i, error in enumerate(todos_los_errores, 1):
            print(f"  {i}. {error}")
        print(f"\n  Total: {len(todos_los_errores)} error(es) encontrado(s).")
    else:
        print("  Sin errores. El programa es sintácticamente correcto.")
