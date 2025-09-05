#Dictionary for 
# TODO: implement ' and "
# TODO: implement new punctuators/keywords/exc..    

# PUNCTUATORS
LBRACK      = "["
RBRACK      = "]"
LPAREN      = "("
RPAREN      = ")"
LBRACE      = "{"
RBRACE      = "}"
COMMA       = ","
COLON       = ":"
SEMICOLON   = ";"
ASTERISK    = "*"
PREPROC     = "#"
DOT         = "."
TILDE       = "~"

# KEYWORDS
AUTO        = "auto"
BREAK       = "break"
CASE        = "case"
CHAR        = "char"
CONST       = "const"
CONTINUE    = "continue"
DEFAULT     = "default"
DO          = "do"
DOUBLE      = "double"
ELSE        = "else"
ENUM        = "enum"
EXTERN      = "extern"
FLOAT       = "float"
FOR         = "for"
GOTO        = "goto"
IF          = "if"
INT         = "int"
LONG        = "long"
REGISTER    = "register"
RETURN      = "return"
SHORT       = "short"
SIGNED      = "signed"
SIZEOF      = "sizeof"
STATIC      = "static"
STRUCT      = "struct"
SWITCH      = "switch"
TYPEDEF     = "typedef"
UNION       = "union"
UNSIGNED    = "unsigned"
VOID        = "void"
VOLATILE    = "volatile"
WHILE       = "while"

# ARITHMETIC OPERATORS
PLUS        = "+"
MINUS       = "-"
MULTIPLY    = "*"
DIVIDE      = "/"
MODULUS     = "%"
UNARYPLUS   = "+"
UNARYMINUS  = "-"
INCREMENT   = "++"
DECREMENT   = "--"

# RELATIONAL OPERATORS
LESSTHAN        = "<"
GREATERTHAN     = ">"
LESSTHANEQUAL   = "<="
GREATERTHANEQUAL= ">="
EQUAL           = "=="
NOTEQUAL        = "!="

# LOGICAL OPERATORS
LOGAND      = "&&"
LOGOR       = "||"
LOGNOT      = "!"

# BITWISE OPERATORS
BITAND      = "&"
BITOR       = "|"
BITXOR      = "^"
BITNOT      = "~"
LEFTSHIFT   = "<<"
RIGHTSHIFT  = ">>"

# ASSIGNMENT OPERATORS
ASSIGN      = "="
PLUSASSIGN  = "+="
MINUSASSIGN = "-="
MULTASSIGN  = "*="
DIVASSIGN   = "/="
MODASSIGN   = "%="
ANDASSIGN   = "&="
ORASSIGN    = "|="
XORASSIGN   = "^="
LSHIFTASSIGN= "<<="
RSHIFTASSIGN= ">>="

# INDENTATION (if you plan to treat it as a token)
INDENT      = "INDENT"
token_table = {
    '+' : ADD,
    '-' : SUB,
    '*' : MUL,
    '/' : DIV,
    '%' : MOD,
    '^' : POW,
    '=' : SET,
    '!=': NOT_EQ,
    '<=': L_THAN_EQ,
    '>=': G_THAN_EQ,
    '==': EQ,
    '!' : NOT,
    '(' : LPAREN,
    ')' : RPAREN,
    '[' : L_BRACK,
    ']' : R_BRACK,
    ';' : SEMI,
    ',' : COMMA,
    '>' : G_THAN,
    '<' : L_THAN,
    '.' : DOT,
    '#' : HASH,
    '{' : LBRACE,
    '}' : RBRACE
}

keyword_table = {
    'int'     : KEYWORD,
    'bool'    : KEYWORD,
    'double'  : KEYWORD,
    'float'   : KEYWORD,
    'long'    : KEYWORD,
    'short'   : KEYWORD,
    'char'    : KEYWORD,
    'const'   : KEYWORD,
    'continue': KEYWORD,
    'break'   : KEYWORD,
    'true'    : KEYWORD,
    'false'   : KEYWORD,
    'struct'  : KEYWORD,
    'if'      : KEYWORD,
    'else'    : KEYWORD,
    'for'     : KEYWORD,
    'while'   : KEYWORD,
    'return'  : KEYWORD,
    'static'  : KEYWORD,
    'void'    : KEYWORD
}


class Token:
    def __init__(self, token_type: str, value:str, loc:int, char_num: int):
        self.type = token_type
        self.value = value
        self.line_num = loc + 1
        self.char_num = char_num + 1
    def __repr__(self):
        return f"({self.type},'{self.value}', Line: {self.line_num} Char: {self.char_num})"
        


class Tokenizer:
    """Turns a list of strings into a list of lists of tokens

    Raises:
        Exception: Unknown Token

    Returns:
        list[list[Token]]: List of lists containing tokens, each index is a new line of tokens
    """
    def __init__(self, file: list[str]):
        self.file = file
        self.index = 0
        self.line = ''
        self.line_num = 0
    
    # Increments index of source by one
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
    
    def _return_token(self, token_type, content):
        return(Token(token_type, content, f'Line: {self.line_num}, Char: {self.index}'))
    
    # Returns next token in line
    def _next_token(self) -> Token:
        char = self.line[self.index]  # For readability
        
        if(char is None):
            return Token(EOF, None, self.line_num, self.index)

        # Clear Whitespace?
        while(not char.strip()):
            if(self._peek() is not None):
                char = self._advance()
            else:
                return Token(EOF, None, self.line_num, self.index)
        
        # Is letter?
        if(char.isalpha()):
            var = char
            while(True):
                next_char = self._peek()
                if(next_char is None):
                    break
                elif(next_char.isalpha() or next_char.isdigit()):
                    char = self._advance()
                    var += char
                else:
                    break
            self._advance()
            if(keyword := keyword_table.get(var)):
                return Token(keyword, var, self.line_num, self.index)
            return Token(VAR, var, self.line_num, self.index)
        
        # Is number?
        elif(char.isdigit()):
            num = char
            while(True):
                next_char = self._peek()
                if(next_char is None):
                    break
                if(next_char.isdigit()):
                    char = self._advance()
                    num += char
                else:
                    break
            self._advance()
            return Token(NUM, num, self.line_num, self.index)
        
        # Is Symbol?
        elif(token := token_table.get(char)):
            symbol = Token(token, char, self.line_num, self.index)
            next_char = self._peek()
            possible_token = token_table.get(char + next_char)
            if(next_char is not None and possible_token is not None):
                symbol = Token(possible_token, char + next_char, self.line_num, self.index)
                self._advance()
            self._advance()
            return symbol
        
        else:
            message = f"Unknown Token: {char}, Line: {self.line_num + 1}, Char: {self.index + 1}"
            raise Exception(message)
    
    # Generates tokens in list of lists to track line numbers
    def tokenize(self) -> list[list[Token]]:
        token_list = []
        for index, raw_line in enumerate(self.file):
            self.line = raw_line
            self.index = 0
            self.line_num = index
            while(True):
                token = self._next_token()
                if(token.type is not EOF):
                    token_list.append(token)
                else:
                    break
        return token_list