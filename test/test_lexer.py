from pathlib import Path
import sys
import glob
src_file = str(Path(Path.cwd(),'src'))
sys.path.append(src_file)
from lexer import Tokenizer, Token

KEYWORDS = {
    "auto": "AUTO",
    "break": "BREAK",
    "case": "CASE",
    "char": "CHAR",
    "const": "CONST",
    "continue": "CONTINUE",
    "default": "DEFAULT",
    "do": "DO",
    "double": "DOUBLE",
    "else": "ELSE",
    "enum": "ENUM",
    "extern": "EXTERN",
    "float": "FLOAT",
    "for": "FOR",
    "goto": "GOTO",
    "if": "IF",
    "int": "INT",
    "long": "LONG",
    "register": "REGISTER",
    "return": "RETURN",
    "short": "SHORT",
    "signed": "SIGNED",
    "sizeof": "SIZEOF",
    "static": "STATIC",
    "struct": "STRUCT",
    "switch": "SWITCH",
    "typedef": "TYPEDEF",
    "union": "UNION",
    "unsigned": "UNSIGNED",
    "void": "VOID",
    "volatile": "VOLATILE",
    "while": "WHILE",
}
SYMBOLS = {
    "+": "PLUS",
    "-": "MINUS",
    "*": "MULTIPLY",
    "/": "DIVIDE",
    "%": "MODULUS",
    "++": "INCREMENT",
    "--": "DECREMENT",
    "<": "LESSTHAN",
    ">": "GREATERTHAN",
    "<=": "LESSTHANEQUAL",
    ">=": "GREATERTHANEQUAL",
    "==": "EQUAL",
    "!=": "NOTEQUAL",
    "&&": "LOGAND",
    "||": "LOGOR",
    "!": "LOGNOT",
    "&": "BITAND",
    "|": "BITOR",
    "^": "BITXOR",
    "~": "BITNOT",
    "<<": "LEFTSHIFT",
    ">>": "RIGHTSHIFT",
    "=": "ASSIGN",
    "+=": "PLUSASSIGN",
    "-=": "MINUSASSIGN",
    "*=": "MULTASSIGN",
    "/=": "DIVASSIGN",
    "%=": "MODASSIGN",
    "&=": "ANDASSIGN",
    "|=": "ORASSIGN",
    "^=": "XORASSIGN",
    "<<=": "LSHIFTASSIGN",
    ">>=": "RSHIFTASSIGN",
    "[": "LBRACK",
    "]": "RBRACK",
    "(": "LPAREN",
    ")": "RPAREN",
    "{": "LBRACE",
    "}": "RBRACE",
    ",": "COMMA",
    ":": "COLON",
    ";": "SEMICOLON",
    "#": "PREPROC",
    ".": "DOT",
}

def test_keywords():
    tok = Tokenizer("")
    for case, token_type in KEYWORDS.items():
        tok.set_new_file(case)
        assert(tok.tokenize() == [Token(token_type, case)])


def test_symbols():
    tok = Tokenizer("")
    for case, token_type in SYMBOLS.items():
        tok.set_new_file(case)
        assert(tok.tokenize() == [Token(token_type, case)])


def test_other_tokens():
    tok = Tokenizer("cokezero")
    assert(tok.tokenize() == [Token("IDENTIFIER", "cokezero")])

    tok.set_new_file("123")
    assert(tok.tokenize() == [Token("NUMBER", "123")])

def test_edge_cases():
    tok = Tokenizer("")
    tok.set_new_file("")
    assert(tok.tokenize() == [])

def test_code():
    test_path = Path(src_file, '/test/test_code')
    for files in glob.iglob(str(Path(test_path, '*.c'))):
        with open(files) as f:
            tok = Tokenizer(f.read())
            token_list= tok.tokenize()


