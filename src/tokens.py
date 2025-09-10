# This is a subset of keywords from the C language



# keyword
# identifier
# constant
# string-literal
# punctuator
KEYWORDS = {
    "auto"      : 'AUTO',
    "break"     : 'BREAK',
    "case"      : 'CASE',
    "char"      : 'CHAR',
    "const"     : 'CONST',
    "continue"  : 'CONTINUE',
    "default"   : 'DEFAULT',
    "do"        : 'DO',
    "double"    : 'DOUBLE',
    "else"      : 'ELSE',
    "enum"      : 'ENUM',
    "extern"    : 'EXTERN',
    "float"     : 'FLOAT',
    "for"       : 'FOR',
    "goto"      : 'GOTO',
    "if"        : 'IF',
    "inline"    : 'INLINE',
    "int"       : 'INT',
    "long"      : 'LONG',
    "register"  : 'REGISTER',
    "restrict"  : 'RESTRICT',
    "return"    : 'RETURN',
    "short"     : 'SHORT',
    "signed"    : 'SIGNED',
    "sizeof"    : 'SIZEOF',
    "static"    : 'STATIC',
    "struct"    : 'STRUCT',
    "switch"    : 'SWITCH',
    "typedef"   : 'TYPEDEF',
    "union"     : 'UNION',
    "unsigned"  : 'UNSIGNED',
    "void"      : 'VOID',
    "volatile"  : 'VOLATILE',
    "while"     : 'WHILE',
    "_Bool"     : '_BOOL',
    "_Complex"  : '_Complex',
    "_Imaginary": '_IMAGINARY'
}

SYMBOLS = {
#ARITHMETIC_OPERATORS
    "+"  : 'PLUS',
    "-"  : 'MINUS',
    "*"  : 'MULTIPLY',
    "/"  : 'DIVIDE',
    "%"  : 'MODULUS',
    "++" : 'INCREMENT',
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
    "[" : 'LBRACK',
    "]" : 'RBRACK',
    "(" : 'LPAREN',
    ")" : 'RPAREN',
    "{" : 'LBRACE',
    "}" : 'RBRACE',
    "," : 'COMMA',
    ":" : 'COLON',
    ";" : 'SEMICOLON',
    "#" : 'PREPROC',
    "." : 'DOT',
    "?" : 'TERNARY'

}

IDENTIFIER     = 'IDENTIFIER'
NUMBER         = 'NUMBER'
EOL            = 'EOL'
EOF            = 'EOF'
CHAR_LITERAL   = 'CHAR_LITERAL'
STRING_LITERAL = 'STRING_LITERAL'