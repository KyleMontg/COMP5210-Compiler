#Dictionary for tokenizer
ADD = 'ADD'
SUB = 'SUB'
MUL = 'MUL'
DIV = 'DIV'
MOD = 'MOD'
POW = 'POW'
SET = 'SET'
NOT_EQ = 'NOT_EQ'
L_THAN_EQ = 'L_THAN_EQ'
G_THAN_EQ = 'G_THAN_EQ'
EQ = 'EQ'
LPAR = 'LPAR'
RPAR = 'RPAR'
L_BRACK = 'L_BRACK'
R_BRACK = 'R_BRACK'
SEMI = 'SEMI'
COMMA = 'COMMA'
G_THAN = 'G_THAN'
L_THAN = 'L_THAN'
DOT = 'DOT'
HASH = 'HASH'
LBRACE = 'LBRACE'
RBRACE = 'RBRACE'
EOF = 'EOF'
VAR = 'VAR'
NUM = 'NUM'
NOT = 'NOT'
KEYWORD = 'KEYWORD'

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
    '(' : LPAR,
    ')' : RPAR,
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
    def __init__(self, type: str, value:str):
        self.type = type
        self.value = value
        #self.line = line
    def __repr__(self):
        return f"({self.type},{self.value})"
        


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
    
    # Returns next token in line 
    def _next_token(self) -> Token:
        char = self.line[self.index]  # For readability
        
        if(char is None):
            return Token(EOF, None)

        # Clear Whitespace?
        while(not char.strip()):
            if(self._peek()is not None):
                char = self._advance()
            else:
                return Token(EOF,None)               
        
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
                return Token(keyword, var)
            return Token(VAR, var)
        
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
            return Token(NUM, num)
        
        # Is Symbol?
        elif(token := token_table.get(char)):
            symbol = Token(token, char)
            next_char = self._peek()
            if(next_char is not None and token_table.get(char + next_char) is not None):
                symbol = Token(token_table.get(char + next_char), char + next_char)
                self._advance()
            self._advance()
            return symbol
        
        else:
            raise Exception(f'Unknown Token: {char}')
    
    # Generates tokens in list of lists to track line numbers
    def tokenize(self) -> list[list[Token]]:
        file_token_list = []
        for raw_line in self.file:
            self.line = raw_line
            self.index = 0
            token_list = []
            while(True):
                token = self._next_token()
                if(token.type is not EOF):
                    token_list.append(token)
                else:
                    break
            file_token_list.append(token_list)
        return file_token_list