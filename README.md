# **COMP5210-Compiler**
A compiler for a subsection of the C99 programming language by Kyle Montgomery.

***

## Requirements
>* Python 3.12 or later
>* For testing you need pytest

***

## Usage
##### Run code
>`python main.py "input_file"`
**flags**
> `-l` When flagged, output of lexer will be printed to console
> `-o "file_location/file_name"` When flagged, output file name and directory can be specified, defaults to output.txt in main directory
##### Run Tests
>`pytest`

***

## Implementation Overview

### Lexical Specification
> * Preprocessing are tokenized but never processed
> * Only Support base 10 unsigned integers
> * Allows for multi-char `""` and char-constants `''`
> * Char-constants accepts multiple chars but implementation is not decided yet
> * No Escape sequences
> * Supports single line and multiline comments
> * Every line has an EOL token and every file has a EOF token
>    ##### Unsupported punctuators
>|||||
>|---|---|---|---|
>| ... | ## | <: | :>   |
>| <%  | %> | %: | %:%: |

### Testing
> For testing I opted to use Pytest. To use this just enter `pytest` in a terminal in the main directory of project

### Tokens
> The tokens I chose to implement were a subsection of the C99 ISO Standard found [here](https://www.dii.uchile.cl/~daespino/files/Iso_C_1999_definition.pdf)

***

### To Do
* Implement custom error handling
* Allow for multiple number types
* Rewriting lexer for easier tokenization of complex tokens
# Tokens

***

#### *Disclaimer: I accept more tokens than will possible be supported by the compiler at later stages of development*

### Keywords
| Keyword    | Token Name |
| ---------- | ---------- |
| `auto`     | AUTO       |
| `break`    | BREAK      |
| `case`     | CASE       |
| `char`     | CHAR       |
| `const`    | CONST      |
| `continue` | CONTINUE   |
| `default`  | DEFAULT    |
| `do`       | DO         |
| `double`   | DOUBLE     |
| `else`     | ELSE       |
| `enum`     | ENUM       |
| `extern`   | EXTERN     |
| `float`    | FLOAT      |
| `for`      | FOR        |
| `goto`     | GOTO       |
| `if`       | IF         |
| `int`      | INT        |
| `long`     | LONG       |
| `register` | REGISTER   |
| `return`   | RETURN     |
| `short`    | SHORT      |
| `signed`   | SIGNED     |
| `sizeof`   | SIZEOF     |
| `static`   | STATIC     |
| `struct`   | STRUCT     |
| `switch`   | SWITCH     |
| `typedef`  | TYPEDEF    |
| `union`    | UNION      |
| `unsigned` | UNSIGNED   |
| `void`     | VOID       |
| `volatile` | VOLATILE   |
| `while`    | WHILE      |

### Arithmetic Operators
| Symbol | Token Name |
| ------ | ---------- |
| `+`    | PLUS       |
| `-`    | MINUS      |
| `*`    | MULTIPLY   |
| `/`    | DIVIDE     |
| `%`    | MODULUS    |
| `++`   | INCREMENT  |
| `--`   | DECREMENT  |

### Relational Operators
| Symbol | Token Name       |
| ------ | ---------------- |
| `<`    | LESSTHAN         |
| `>`    | GREATERTHAN      |
| `<=`   | LESSTHANEQUAL    |
| `>=`   | GREATERTHANEQUAL |
| `==`   | EQUAL            |
| `!=`   | NOTEQUAL         |

### Logical Operators
| Symbol | Token Name |
| ------ | ---------- |
| `&&`   | LOGAND     |
| `\|\|` | LOGOR      |
| `!`    | LOGNOT     |

### Bitwise Operators
| Symbol | Token Name |
| ------ | ---------- |
| `&`    | BITAND     |
| `\|`   | BITOR      |
| `^`    | BITXOR     |
| `~`    | BITNOT     |
| `<<`   | LEFTSHIFT  |
| `>>`   | RIGHTSHIFT |

### Assignment Operators
| Symbol | Token Name   |
| ------ | ------------ |
| `=`    | ASSIGN       |
| `+=`   | PLUSASSIGN   |
| `-=`   | MINUSASSIGN  |
| `*=`   | MULTASSIGN   |
| `/=`   | DIVASSIGN    |
| `%=`   | MODASSIGN    |
| `&=`   | ANDASSIGN    |
| `\|=`   | ORASSIGN    |
| `^=`   | XORASSIGN    |
| `<<=`  | LSHIFTASSIGN |
| `>>=`  | RSHIFTASSIGN |

### Punctuators
| Symbol | Token Name |
| ------ | ---------- |
| `[`    | LBRACK     |
| `]`    | RBRACK     |
| `(`    | LPAREN     |
| `)`    | RPAREN     |
| `{`    | LBRACE     |
| `}`    | RBRACE     |
| `,`    | COMMA      |
| `:`    | COLON      |
| `;`    | SEMICOLON  |
| `#`    | PREPROC    |
| `.`    | DOT        |
| `?`    | TERNARY    |

### Other Tokens
| Token Name     | Description              |
| -------------- | ------------------------ |
| IDENTIFIER     | User-defined identifiers |
| NUMBER         | Numeric literals         |
| EOF            | End-of-file marker       |
| CHAR_LITERAL   | Character literals       |
| STRING_LITERAL | String Literals          |

# Sources
* https://github.com/ShivamSarodia/ShivyC/ - used for help formatting README
* https://www.dii.uchile.cl/~daespino/files/Iso_C_1999_definition.pdf - used for what tokens to implement




