from src.tokens import Token
from typing import Optional


class CompilerError(Exception):
    """Base class for all compiler errors"""

    def __init__(self, message: str, token: Optional[Token] = None, source_lines: Optional[list[str]] = None):
        self.message = message
        self.token = token
        self.source_lines = source_lines
        super().__init__(self.__str__())

    def __str__(self) -> str:
        if self.token is None or not hasattr(self.token, 'line_num'):
            return f"{self.__class__.__name__}: {self.message}"

        line = self.token.line_num + 1  # Convert to 1-indexed
        col = self.token.char_num

        error_msg = f"{self.__class__.__name__} at line {line}, column {col}:\n"
        error_msg += f"  {self.message}\n"

        # Show the source line if available
        if self.source_lines and 0 <= self.token.line_num < len(self.source_lines):
            source_line = self.source_lines[self.token.line_num]
            error_msg += f"\n  {line} | {source_line}\n"
            error_msg += f"      | {' ' * col}^\n"

        return error_msg


class LexerError(CompilerError):
    """Raised during lexical analysis"""
    pass


class ParserError(CompilerError):
    """Raised during parsing"""
    pass


class SymbolTableError(CompilerError):
    """Raised during symbol table construction"""
    pass


class TACError(CompilerError):
    """Raised during TAC generation"""
    pass


class ASMError(CompilerError):
    """Raised during assembly generation"""
    pass


class SemanticError(CompilerError):
    """Raised for semantic errors (type checking, undefined variables, etc.)"""
    pass
