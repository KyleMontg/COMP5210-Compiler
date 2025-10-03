import re
from src.errors import LexerError
from src.tokens import *

_SYMBOL_PATTERN = "|".join(re.escape(sym) for sym in sorted(SYMBOLS.keys(), key=len, reverse=True))

_NUMBER_PATTERN = r"""
    (?:0[xX][0-9A-Fa-f]+(?:\.[0-9A-Fa-f]*)?(?:[pP][+-]?\d+)?)
  | (?:\d+\.\d*(?:[eE][+-]?\d+)?[fFlL]?)
  | (?:\.\d+(?:[eE][+-]?\d+)?[fFlL]?)
  | (?:\d+(?:[eE][+-]?\d+)?[fFlL]?)
"""

_TOKEN_REGEX = re.compile(
    r"(?P<WHITESPACE>[ \t]+)"
    r"|(?P<NEWLINE>\r?\n)"
    r"|(?P<COMMENT>//[^\n]*)"
    r"|(?P<ML_COMMENT>/\*(?:.|\n)*?\*/)"
    r"|(?P<STRING>\"(?:\\.|[^\"\\])*\")"
    r"|(?P<CHAR>'(?:\\.|[^'\\])')"
    r"|(?P<NUMBER>" + _NUMBER_PATTERN + r")"
    r"|(?P<IDENTIFIER>[A-Za-z_]\w*)"
    r"|(?P<SYMBOL>" + _SYMBOL_PATTERN + r")"
    r"|(?P<MISMATCH>.)",
    re.VERBOSE,
)


class Tokenizer:
    """Regex based tokenizer for the C subset."""

    def __init__(self, src: str):
        self.src = src
        self.length = len(src)
        self.lines = self.src.splitlines()

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        line = 0
        col = 0
        i = 0

        while i < self.length:
            tok_match = _TOKEN_REGEX.match(self.src, i)
            if not tok_match:
                raise LexerError(
                    f"unexpected character '{self.src[i]}'",
                    self.src[i]
                )

            tok_typ = tok_match.lastgroup
            lexeme = tok_match.group()
            start_line = line
            start_col = col
            i = tok_match.end()

            if tok_typ in {"WHITESPACE", "COMMENT"}:
                col += len(lexeme)
                continue

            if tok_typ == "ML_COMMENT":
                newline_count = lexeme.count("\n")
                if newline_count:
                    line += newline_count
                    col = len(lexeme.rsplit("\n", 1)[-1])
                else:
                    col += len(lexeme)
                continue

            if tok_typ == "NEWLINE":
                line += 1
                col = 0
                continue

            if tok_typ == "STRING":
                tokens.append(Token(STRING_LITERAL, lexeme[1:-1], start_line, start_col))
            elif tok_typ == "CHAR":
                tokens.append(Token(CHAR_LITERAL, lexeme[1:-1], start_line, start_col))
            elif tok_typ == "NUMBER":
                tokens.append(Token(NUMBER, lexeme, start_line, start_col))
            elif tok_typ == "IDENTIFIER":
                token_type = KEYWORDS.get(lexeme, IDENTIFIER)
                tokens.append(Token(token_type, lexeme, start_line, start_col))
            elif tok_typ == "SYMBOL":
                tokens.append(Token(SYMBOLS[lexeme], lexeme, start_line, start_col))
            elif tok_typ == "MISMATCH":
                raise LexerError(
                    f"unexpected token '{lexeme}'",
                    self.src[i]
                )

            newline_count = lexeme.count("\n")
            if newline_count:
                line += newline_count
                col = len(lexeme.rsplit("\n", 1)[-1])
            else:
                col += len(lexeme)

        tokens.append(Token(EOF, '', line, col))
        return tokens
