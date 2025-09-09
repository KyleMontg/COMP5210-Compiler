from tokens import *

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
            return f"({self.type},'{self.value}', Line: {self.line_num + 1} Char: {self.char_num})"
        return  f"({self.type},'{self.value}')"

    def __eq__(self, other) -> bool:
        return self.value == other.value and self.type == other.type
        

#TODO add option for not logging line numbers and char numbers
class Tokenizer:
    """Returns a List[Token] given List[str] or str

    Raises:
        Exception: Unknown Token
    """
    def __init__(self, file: list[str] | str):
        self.file = file.splitlines() if isinstance(file, str) else file
        self.index = 0
        self.line_num = 0
        self.line = ''
        self.in_mlc = False
    
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
    
    # If at EOF, return None
    def _clear_whitespace(self) -> str | None:
        if(self.index >= len(self.line)):
            return None
        char = self.line[self.index]
        while(not char.strip()):
            if(not self._peek()):
                return None
            char = self._advance()
        return char

    def _is_identifier(self) -> Token|None:
        char = self.line[self.index]
        if(not char.isalpha() and not char == '_'):
            return None
        ident = char
        while(True):
            next_char = self._peek()
            if(not next_char):
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
        if(SYMBOLS.get(char) is None):
            return None
        symbol = char
        while(True):
            next_char = self._peek()
            if(not next_char):
                break
            if(not SYMBOLS.get(symbol + next_char)):
                break
            char = self._advance()
            symbol += char
        self._advance()
        return Token(SYMBOLS.get(symbol), symbol, self.line_num, self.index)

    def _is_comment(self) -> bool:
        char = self.line[self.index]
        next_char = self._peek()
        if(not next_char):
            return False
        comment = char + next_char
        if(comment == '//'):
            return True
        return False

    def _build_literal(self, check_char: str) -> str:
        char = self.line[self.index]
        build_lit = char
        while(True):
            next_char = self._peek()
            if(not next_char):
                raise Exception('Incomplete Literal') #TODO Implement errors
            if(next_char != check_char):
                char = self._advance()
                build_lit += char
            else:
                char = self._advance()
                build_lit += char
                break
        self._advance()
        return(build_lit[1:-1])

    def _is_string_or_char(self) -> Token|None:
        char = self.line[self.index]
        if(not char):
            return None
        if(char == '"'):
            string_lit = self._build_literal('"')
            return Token(STRING_LITERAL, string_lit, self.line_num, self.index)
        elif(char == "'"):
            char_lit = self._build_literal("'")
            return Token(CHAR_LITERAL, char_lit, self.line_num, self.index)
        return None

    def _is_mlc(self) -> Token|None:
        char = self.line[self.index]
        next_char = self._peek()
        if(not char or not next_char):
            return None
        if(char + next_char != '/*'):
            return None
        mlc_end = self.line[self.index:].find('*/')
        if(mlc_end != -1):
            self.index = mlc_end + 2
            return None
        self.in_mlc = True
        return Token(EOF, None)


    def _next_token(self) -> Token:
        if(self.in_mlc):
            mlc_end = self.line.find('*/')
            if mlc_end == -1:
                return Token(EOF, None)
            self.in_mlc = False
            self.index = mlc_end + 2
        char = self._clear_whitespace()
        token = None
        if(not char):
            return Token(EOF, None)
        if (self._is_comment()):
            return Token(EOF, None)
        for check in (self._is_identifier, self._is_number, self._is_mlc, self._is_symbol, self._is_string_or_char):
            token = check()
            if token:
                return token
        unknown_token = f"Unknown Token: {char}, Line: {self.line_num + 1}, Char: {self.index + 1}"
        raise Exception(unknown_token) #TODO Implement Errors
    
    # Iterate through list[str] and returns list[Token]
    def tokenize(self) -> list[Token]:
        token_list = []
        for line_num, file_line in enumerate(self.file):
            self.line = file_line
            self.index = 0
            self.line_num = line_num
            while(True):
                token = self._next_token()
                if(token.type != EOF):
                    token_list.append(token)
                else:
                    break
        return token_list

    def set_new_file(self, file: list[str]|str):
        self.file = file.splitlines() if isinstance(file, str) else file