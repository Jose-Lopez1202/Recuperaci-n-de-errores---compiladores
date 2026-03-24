from enum import Enum, auto
# ─── Tipos de Token ───────────────────────────────────────────────

class TipoToken(Enum):
    NUMERO          = auto()
    IDENTIFICADOR   = auto()
    CADENA          = auto()
    VAR             = auto()
    IF              = auto()
    ELSE            = auto()
    WHILE           = auto()
    FOR             = auto()
    DEF             = auto()
    RETURN          = auto()
    TRUE            = auto()
    FALSE           = auto()
    SUMA            = auto()  
    RESTA           = auto()   
    MULTIPLICACION  = auto()   
    DIVISION        = auto()   
    ASIGNACION      = auto()   
    IGUAL_IGUAL     = auto()   
    DIFERENTE       = auto()   
    MENOR           = auto()   
    MAYOR           = auto()   
    MENOR_IGUAL     = auto()   
    MAYOR_IGUAL     = auto()   
    PAREN_IZQ       = auto()   
    PAREN_DER       = auto()   
    LLAVE_IZQ       = auto()   
    LLAVE_DER       = auto()  
    PUNTO_Y_COMA    = auto()   
    COMA            = auto()   
    EOF             = auto()  
# ─── Mapa de palabras reservadas ──────────────────────────────────
PALABRAS_RESERVADAS = {
    "var":    TipoToken.VAR,
    "if":     TipoToken.IF,
    "else":   TipoToken.ELSE,
    "while":  TipoToken.WHILE,
    "for":    TipoToken.FOR,
    "def":    TipoToken.DEF,
    "return": TipoToken.RETURN,
    "true":   TipoToken.TRUE,
    "false":  TipoToken.FALSE,
}
# ─── Clase Token ──────────────────────────────────────────────────
class Token:
    def __init__(self, tipo: TipoToken, valor: str, linea: int, columna: int):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna

    def __repr__(self):
        return f"Token({self.tipo.name}, '{self.valor}', lin={self.linea}, col={self.columna})"
# ─── Clase Lexer ──────────────────────────────────────────────────
class Lexer:
    def __init__(self, codigo_fuente: str):
        self.fuente = codigo_fuente
        self.posicion = 0        
        self.linea = 1       
        self.columna = 1         
        self.tokens = []      
        self.errores = []          
 # ── Helpers ───────────────────────────────────────────────────
    def _caracter_actual(self) -> str:
        """Retorna el carácter actual sin avanzar."""
        if self.posicion >= len(self.fuente):
            return '\0'  # Indica fin del archivo
        return self.fuente[self.posicion]
    def _ver_siguiente(self) -> str:
        """(lookahead)."""
        siguiente = self.posicion + 1
        if siguiente >= len(self.fuente):
            return '\0'
        return self.fuente[siguiente]
    def _avanzar(self) -> str:
        caracter = self._caracter_actual()
        self.posicion += 1
        if caracter == '\n':
            self.linea += 1
            self.columna = 1
        else:
            self.columna += 1
        return caracter
    def _agregar_token(self, tipo: TipoToken, valor: str, linea: int, columna: int):
        """Crea un token y lo agrega a la lista."""
        self.tokens.append(Token(tipo, valor, linea, columna))
    # ── Scanner ────────────────────────────────────────
    def _saltar_espacios_y_comentarios(self):
        while self.posicion < len(self.fuente):
            c = self._caracter_actual()
            if c in (' ', '\t', '\r', '\n'):
                self._avanzar()
            elif c == '/' and self._ver_siguiente() == '/':
                while self._caracter_actual() != '\n' and self._caracter_actual() != '\0':
                    self._avanzar()
            else:
                break
    def _leer_numero(self):
        inicio_col = self.columna
        inicio_lin = self.linea
        numero = ''
        while self._caracter_actual().isdigit():
            numero += self._avanzar()
        if self._caracter_actual() == '.' and self._ver_siguiente().isdigit():
            numero += self._avanzar()  # consume el '.'
            while self._caracter_actual().isdigit():
                numero += self._avanzar()
        self._agregar_token(TipoToken.NUMERO, numero, inicio_lin, inicio_col)
    def _leer_identificador(self):
        inicio_col = self.columna
        inicio_lin = self.linea
        texto = ''
        while self._caracter_actual().isalnum() or self._caracter_actual() == '_':
            texto += self._avanzar()
        tipo = PALABRAS_RESERVADAS.get(texto, TipoToken.IDENTIFICADOR)
        self._agregar_token(tipo, texto, inicio_lin, inicio_col)
    def _leer_cadena(self):
        inicio_col = self.columna
        inicio_lin = self.linea
        self._avanzar() 
        contenido = ''
        while self._caracter_actual() != '"' and self._caracter_actual() != '\0':
            if self._caracter_actual() == '\n':
                self.errores.append(
                    f"Error léxico [Línea {inicio_lin}, Col {inicio_col}]: "
                    f"Cadena no terminada."
                )
                return
            contenido += self._avanzar()
        if self._caracter_actual() == '\0':
            self.errores.append(
                f"Error léxico [Línea {inicio_lin}, Col {inicio_col}]: "
                f"Cadena no terminada (se alcanzó fin de archivo)."
            )
            return
        self._avanzar() 
        self._agregar_token(TipoToken.CADENA, contenido, inicio_lin, inicio_col)
    # ── Método principal ──────────────────────────────────────────
    def tokenizar(self) -> list[Token]:
        while self.posicion < len(self.fuente):
            self._saltar_espacios_y_comentarios()
            if self.posicion >= len(self.fuente):
                break
            c = self._caracter_actual()
            col = self.columna
            lin = self.linea
            # ── Números ──
            if c.isdigit():
                self._leer_numero()
            # ── Identificadores / palabras reservadas ──
            elif c.isalpha() or c == '_':
                self._leer_identificador()
            # ── Cadenas ──
            elif c == '"':
                self._leer_cadena()
            # ── Operadores de dos caracteres ──
            elif c == '=' and self._ver_siguiente() == '=':
                self._avanzar(); self._avanzar()
                self._agregar_token(TipoToken.IGUAL_IGUAL, '==', lin, col)
            elif c == '!' and self._ver_siguiente() == '=':
                self._avanzar(); self._avanzar()
                self._agregar_token(TipoToken.DIFERENTE, '!=', lin, col)
            elif c == '<' and self._ver_siguiente() == '=':
                self._avanzar(); self._avanzar()
                self._agregar_token(TipoToken.MENOR_IGUAL, '<=', lin, col)
            elif c == '>' and self._ver_siguiente() == '=':
                self._avanzar(); self._avanzar()
                self._agregar_token(TipoToken.MAYOR_IGUAL, '>=', lin, col)
            # ── Operadores y delimitadores de un carácter ──
            elif c == '+':
                self._avanzar()
                self._agregar_token(TipoToken.SUMA, '+', lin, col)
            elif c == '-':
                self._avanzar()
                self._agregar_token(TipoToken.RESTA, '-', lin, col)
            elif c == '*':
                self._avanzar()
                self._agregar_token(TipoToken.MULTIPLICACION, '*', lin, col)
            elif c == '/':
                self._avanzar()
                self._agregar_token(TipoToken.DIVISION, '/', lin, col)
            elif c == '=':
                self._avanzar()
                self._agregar_token(TipoToken.ASIGNACION, '=', lin, col)
            elif c == '<':
                self._avanzar()
                self._agregar_token(TipoToken.MENOR, '<', lin, col)
            elif c == '>':
                self._avanzar()
                self._agregar_token(TipoToken.MAYOR, '>', lin, col)
            elif c == '(':
                self._avanzar()
                self._agregar_token(TipoToken.PAREN_IZQ, '(', lin, col)
            elif c == ')':
                self._avanzar()
                self._agregar_token(TipoToken.PAREN_DER, ')', lin, col)
            elif c == '{':
                self._avanzar()
                self._agregar_token(TipoToken.LLAVE_IZQ, '{', lin, col)
            elif c == '}':
                self._avanzar()
                self._agregar_token(TipoToken.LLAVE_DER, '}', lin, col)
            elif c == ';':
                self._avanzar()
                self._agregar_token(TipoToken.PUNTO_Y_COMA, ';', lin, col)
            elif c == ',':
                self._avanzar()
                self._agregar_token(TipoToken.COMA, ',', lin, col)
            # ── Carácter no reconocido ──
            else:
                self.errores.append(
                    f"Error léxico [Línea {lin}, Col {col}]: "
                    f"Carácter inesperado '{c}'."
                )
                self._avanzar()
        # Siempre terminar con EOF
        self._agregar_token(TipoToken.EOF, '', self.linea, self.columna)
        return self.tokens
if __name__ == "__main__":
    codigo = """
var x = 10;
var nombre = "hola";
if (x >= 5) {
    x = x + 1;
}
// esto es un comentario
while (x < 20) {
    x = x * 2;
}
"""
    lexer = Lexer(codigo)
    tokens = lexer.tokenizar()
    print("═══ TOKENS GENERADOS ═══")
    for t in tokens:
        print(f"  {t}")
    if lexer.errores:
        print("\n═══ ERRORES LÉXICOS ═══")
        for e in lexer.errores:
            print(f"  {e}")
    else:
        print("\nSin errores léxicos.")
