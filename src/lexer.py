KEYWORDS = {
    "auto"     : 'AUTO',
    "break"    : 'BREAK',
    "case"     : 'CASE',
    "char"     : 'CHAR',
    "const"    : 'CONST',
    "continue" : 'CONTINUE',
    "default"  : 'DEFAULT',
    "do"       : 'DO',
    "double"   : 'DOUBLE',
    "else"     : 'ELSE',
    "enum"     : 'ENUM',
    "extern"   : 'EXTERN',
    "float"    : 'FLOAT',
    "for"      : 'FOR',
    "goto"     : 'GOTO',
    "if"       : 'IF',
    "int"      : 'INT',
    "long"     : 'LONG',
    "register" : 'REGISTER',
    "return"   : 'RETURN',
    "short"    : 'SHORT',
    "signed"   : 'SIGNED',
    "sizeof"   : 'SIZEOF',
    "static"   : 'STATIC',
    "struct"   : 'STRUCT',
    "switch"   : 'SWITCH',
    "typedef"  : 'TYPEDEF',
    "union"    : 'UNION',
    "unsigned" : 'UNSIGNED',
    "void"     : 'VOID',
    "volatile" : 'VOLATILE',
    "while"    : 'WHILE'
}

OPERATORS = {
#ARITHMETIC_OPERATORS
    "+"  : 'PLUS',
    "-"  : 'MINUS',
    "*"  : 'MULTIPLY',
    "/"  : 'DIVIDE',
    "%"  : 'MODULUS',
    "+"  : 'UNARYPLUS',
    "-"  : 'UNARYMINUS',
    "++" : 'INCREMENT',
    "--" : 'DECREMENT',

#RELATIONAL_OPERATORS
    "<"  : 'LESSTHAN',
    ">"  : 'GREATERTHAN',
    "<=" : 'LESSTHANEQUAL',
    ">=" : 'GREATERTHANEQUAL',
    "==" : 'EQUAL',
    "!=" : 'NOTEQUAL',

#LOGICAL_OPERATORS
    "&&" : 'LOGAND',
    "||" : 'LOGOR',
    "!"  : 'LOGNOT',

#BITWISE_OPERATORS
    "&"  : 'BITAND',
    "|"  : 'BITOR',
    "^"  : 'BITXOR',
    "~"  : 'BITNOT',
    "<<" : 'LEFTSHIFT',
    ">>" : 'RIGHTSHIFT',

#ASSIGNMENT_OPERATORS
    "="   : 'ASSIGN',
    "+="  : 'PLUSASSIGN',
    "-="  : 'MINUSASSIGN',
    "*="  : 'MULTASSIGN',
    "/="  : 'DIVASSIGN',
    "%="  : 'MODASSIGN',
    "&="  : 'ANDASSIGN',
    "|="  : 'ORASSIGN',
    "^="  : 'XORASSIGN',
    "<<=" : 'LSHIFTASSIGN',
    ">>=" : 'RSHIFTASSIGN',

#PUNCTUATORS
    "[" : 'LBRACK',
    "]" : 'RBRACK',
    "(" : 'LPAREN',
    ")" : 'RPAREN',
    "{" : 'LBRACE',
    "}" : 'RBRACE',
    "," : 'COMMA',
    ":" : 'COLON',
    ";" : 'SEMICOLON',
    "*" : 'ASTERISK',
    "#" : 'PREPROC',
    "." : 'DOT',
    "~" : 'TILDE'
}

IDENTIFIER = 'IDENTIFIER'
NUMBER   = 'NUMBER'
EOF      = 'EOF'

#TODO Revise Token desc
class Token:
    """Representaition of C Language Tokens
    """
    def __init__(self, token_type: str, value:str, line_num:int = -1, char_num: int = -1):
        self.type = token_type
        self.value = value
        self.line_num = line_num
        self.char_num = char_num

    def __repr__(self) -> str:
        if(self.line_num > -1):
            return f"({self.type},'{self.value}', Line: {self.line_num + 1} Char: {self.char_num + 1})"
        return  f"({self.type},'{self.value}'"
        

#TODO Implement string or file input, add option for not logging line numbers and char numbers
class Tokenizer:
    """Returns a List[Token] given List[str] or str

    Raises:
        Exception: Unknown Token
    """
    def __init__(self, file: list[str] | str):
        self.file = [file] if isinstance(file, str) else file
        self.index = 0
        self.line_num = 0
        self.line = ''
    
    # Increments index of file by one
    def _advance(self) -> str|None:
        self.index += 1
        if(self.index >= len(self.line)):
            return None
        return self.line[self.index]

    # Returns the character at next index
    def _peek(self) -> str|None:
        if(self.index + 1 >= len(self.line)):
            return None
        return self.line[self.index + 1]
    
    def _clear_whitespace(self) -> str:
        char = self.line[self.index]
        while(not char.strip()):
            if(self._peek() is not None):
                char = self._advance()
            else:
                break
        return char

    def _is_identifier(self) -> Token|None:
        char = self.line[self.index]
        if(not char.isalpha()):
            return None
        ident = char
        while(True):
            next_char = self._peek()
            if(next_char is None):
                break
            elif(next_char.isalnum() or next_char == '_'):
                char = self._advance()
                ident += char
            else:
                break
        self._advance()
        if(keyword := KEYWORDS.get(ident)):
            return Token(keyword, ident, self.line_num, self.index)
        return Token(IDENTIFIER, ident, self.line_num, self.index)

    def _is_number(self) -> Token|None:
        char = self.line[self.index]
        if(not char.isdigit()):
            return None
        num = char
        while(True):
            next_char = self._peek()
            if(not next_char):
                break
            elif(next_char.isdigit()):
                char = self._advance()
                num += char
            else:
                break
        self._advance()
        return Token(NUMBER, num, self.line_num, self.index)
        
    def _is_symbol(self) -> Token|None:
        char  = self.line[self.index]
        if(OPERATORS.get(char) is None):
            return None
        symbol = char
        while(True):
            next_char = self._peek()
            if(not next_char):
                break
            if(not OPERATORS.get(symbol + next_char)):
                break
            char = self._advance()
            symbol += char
        self._advance()
        return Token(OPERATORS.get(symbol), symbol, self.line_num, self.index)

    def _next_token(self) -> Token:
        char = self._clear_whitespace()
        token = None
        if(char is None or char.strip() == ''):
            return Token(EOF, None)
        for check in (self._is_identifier, self._is_number, self._is_symbol):
            token = check()
            char = self.line[self.index]
            if token:
                return token
        unknown_token = f"Unknown Token: {char}, Line: {self.line_num + 1}, Char: {self.index + 1}"
        raise Exception(unknown_token)
    
    # Iterate through list[str] and returns list[Token]
    def tokenize(self) -> list[Token]:
        token_list = []
        for line_num, file_line in enumerate(self.file):
            self.line = file_line
            self.index = 0
            self.line_num = line_num
            while(True):
                token = self._next_token()
                if(token.type is not EOF):
                    token_list.append(token)
                else:
                    break
        return token_list