from src.tokens import Token

class ParserError(Exception):
    def __init__(self, message: str, token: Token = None):
        self.message = message
        self.token = token
        super().__init__(message)

class LexerError(Exception):
    def __init__(self, message: str, token: Token = None):
        self.message = message
        self.token = token
        super().__init__(self.__str__())

class SymbolTableError(Exception):
    def __init__(self, message: str, token: Token = None):
        self.message = message
        self.token = token
        super().__init__(self.__str__())
