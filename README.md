# **COMP5210-Compiler**
A compiler for a subsection of the C programming language by Kyle Montgomery.
***
##




## Usage


***



## Implementation Overview

### Testing
> For testing I opted to use Pytest. To use this just enter `pytest` in a terminal in the main directory of project

### Tokens
> The tokens I chose to implement were compiled for the lists shown at [Tokens in C](https://www.geeksforgeeks.org/c/tokens-in-c/)

***

# Tokens

#### *Disclaimer: I accept more tokens than will be supported by the compiler at later stages of development*

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

### Comments
| Symbol | Token Name  |
| ------ | ----------- |
| `//`   | SLC         |
| `/*`   | MLCSTART \* |
| `*/`   | MLCEND \*   |

### Other Tokens
| Token Name | Description              |
| ---------- | ------------------------ |
| IDENTIFIER | User-defined identifiers |
| NUMBER     | Numeric literals         |
| EOF        | End-of-file marker       |

\* Not Implemented




# Sources
* https://github.com/ShivamSarodia/ShivyC/ - used for help formatting README
* https://www.geeksforgeeks.org/c/tokens-in-c/ - used for what tokens to implement




