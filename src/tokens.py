# This is a subset of keywords from the C language

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


KEYWORDS = {
# <TypeSpecifiers>
    "float"     : 'FLOAT',
    "int"       : 'INT',
    "short"     : 'SHORT',
    "long"      : 'LONG',
    "double"    : 'DOUBLE',
    "char"      : 'CHAR',
    "void"      : 'VOID',
    "_Bool"     : '_BOOL',
# <DeclarationSpecifiers>
    "const"     : 'CONST',
    "static"    : 'STATIC',
    "unsigned"  : 'UNSIGNED',
    "signed"    : 'SIGNED',
# <Statements>
    "if"        : 'IF',
    "else"      : 'ELSE',
    "while"     : 'WHILE',
    "do"        : 'DO',
    "for"       : 'FOR',
    "switch"    : 'SWITCH',
    "case"      : 'CASE',
    "default"   : 'DEFAULT',
    "return"    : 'RETURN',
    "goto"      : 'GOTO',
    "break"     : 'BREAK',
    "continue"  : 'CONTINUE',
}

SYMBOLS = {
#ARITHMETIC_OPERATORS
    "+"  : 'PLUS',
    "-"  : 'MINUS',
    "*"  : 'MULTIPLY',
    "/"  : 'DIVIDE',
    "%"  : 'MODULUS',
    "++" : 'INCREMENT', # No post increment
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
    "(" : 'LPAREN',
    ")" : 'RPAREN',
    "{" : 'LBRACE',
    "}" : 'RBRACE',
    "," : 'COMMA',
    ":" : 'COLON',
    ";" : 'SEMICOLON',
    "." : 'DOT',
}

# Higher precedence value = happens first
TOKEN_PREC = {
    'LPAREN':        100,
    'DOT':           100,
    'PREFIX':         90,
# Math Operators
    'MULTIPLY'        : 11,
    'DIVIDE'          : 11,
    'MODULUS'         : 11,
    'PLUS'            : 10,
    'MINUS'           : 10,
# Shifts
    'LEFTSHIFT'       : 9,
    'RIGHTSHIFT'      : 9,
# Relational
    'LESSTHAN'        : 8,
    'LESSTHANEQUAL'   : 8,
    'GREATERTHAN'     : 8,
    'GREATERTHANEQUAL': 8,
# Equality
    'EQUAL'           : 7,
    'NOTEQUAL'        : 7,
# Bitwise
    'BITAND'          : 6,
    'BITXOR'          : 5,
    'BITOR'           : 4,
# Logs
    'LOGAND'          : 3,
    'LOGOR'           : 2,
# Assignments
    'ASSIGN'          : 1,
    'PLUSASSIGN'      : 1,
    'MINUSASSIGN'     : 1,
    'MULTASSIGN'      : 1,
    'DIVASSIGN'       : 1,
    'MODASSIGN'       : 1,
    'ANDASSIGN'       : 1,
    'ORASSIGN'        : 1,
    'XORASSIGN'       : 1,
    'LSHIFTASSIGN'    : 1,
    'RSHIFTASSIGN'    : 1,
# Other
    'COMMA'           : 0
}

DECLARATION_SPECIFIERS = {
    'CONST',
    'STATIC',
    'UNSIGNED',
    'SIGNED'
}

TYPE_SPECIFIERS = {
    'FLOAT',
    'INT',
    'SHORT',
    'LONG',
    'DOUBLE',
    'CHAR',
    '_BOOL',
    'VOID'
}

ASSIGNMENT_TOKENS = {
    'ASSIGN',
    'PLUSASSIGN',
    'MINUSASSIGN',
    'MULTASSIGN',
    'DIVASSIGN',
    'MODASSIGN',
    'ANDASSIGN',
    'ORASSIGN',
    'XORASSIGN',
    'LSHIFTASSIGN',
    'RSHIFTASSIGN',
}

PREFIX_OPERATORS = {
    'PLUS',
    'MINUS',
    'LOGNOT',
    'BITNOT',
    'INCREMENT',
    'DECREMENT'
}

POSTFIX_OPERATORS = {
    'LPAREN',
    'DOT',
    'INCREMENT',
    'DECREMENT',
}

IDENTIFIER     = 'IDENTIFIER'
NUMBER         = 'NUMBER'
CHAR_LITERAL   = 'CHAR_LITERAL'
STRING_LITERAL = 'STRING_LITERAL'
EOF            = 'EOF'