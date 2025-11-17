from src.tokens import Token

class ParserError(Exception):
    def __init__(self, message: str, token):
        self.message = message
        self.token = token
        super().__init__(message)

class LexerError(Exception):
    def __init__(self, message: str, token):
        self.message = message
        self.token = token
        super().__init__(self.__str__())

class SymbolTableError(Exception):
    def __init__(self, message: str, token):
        self.message = message
        self.token = token
        super().__init__(self.__str__())

class TACError(Exception):
    def __init__(self, message:str, token):
        self.message = message
        self.token = token
        super().__init__(self.__str__())

class ASMError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.__str__())