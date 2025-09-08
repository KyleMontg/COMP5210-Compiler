from tokens import *

#TODO add multiline comment handling
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
        comment = COMMENTS.get(char + next_char)
        if(comment is None):
            return False
        return True

    def _next_token(self) -> Token:
        char = self._clear_whitespace()
        token = None
        if(not char):
            return Token(EOF, None)
        if (self._is_comment()):
            return Token(EOF, None)
        for check in (self._is_identifier, self._is_number, self._is_symbol):
            token = check()
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
                if(token.type != EOF):
                    token_list.append(token)
                else:
                    break
        return token_list

    def set_new_file(self, file: list[str]|str):
        self.file = [file] if isinstance(file, str) else file