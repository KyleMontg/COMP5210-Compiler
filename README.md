# **COMP5210-Compiler**
A compiler for a subsection of the C99 programming language by Kyle Montgomery.
Currently implemented parts: Lexer, Parser, Symbol Table

Hours Spent: 15

># Table of Contents
>[Requirements](#requirements)
>[Usage](#Usage)
>[Implementation](#implementation-overview)
>[Lexical Tokens](#Tokens)
>[Grammer Rules](#Grammer)
>[Sources](#sources)


## Requirements
>* Python 3.12 or later
>* For testing use test_runner.py

***

## Usage
##### Run code
>`python main.py "input_file"`
**flags**
> `-l` Contents of lexer will be printed to console
> `-a` Contents of Parser will be printed to console
> `-t` Contents of Symbol Table will be printed to console
> `-w "file_location/file_name"` When flagged, output file name and directory can be specified, defaults to output.txt in main directory
##### Run Tests
>`test_runner.py`
**flags**
> `-l` Test Lexer
> `-a` Test Parser
> `-t` Test Symbol Table
> * All tests ran and outcome of tests will be printed to the console


***

## Implementation Overview

### Lexical Specification
> * White space is skipped over
> * Comments are recognised as `//`, `/* */` and are skipped over
> * Valid numbers are one of the following:
> * decimal integers, decimal floats, hex
> * Identifiers follow `[A-Za-z_][A-Za-z0-9_]*`
> * Invalid tokens are caught via a LexerError
> * No support for arrays, pointers, structs, unions, enums, or typedef
> * Does not support ternary statement
> * Current Symbol Table does not support label or predefined variables being redefined

>##### Unsupported C punctuators
>|||||
>|-----|----|----|------|
>| ... | ## | <: | :>   |
>| <%  | %> | %: | %:%: |
>| #   | [  | ]  | ->   |
>| ?   |    |    |      |

### Parsing Strategy
> * Used a recursive decent parser and pratt parser
> * Pratt parsing for expressions uses a token precedence dictionary located in `tokens.py`
> * Chose pratt parsing because the ability to update and support more oerators in the future with ease

>##### Valid Prefix Operators
>|||||
>|----|----|----|----|
>| +  | -  | !  | ~  |
>| ++ | -- |    |    |


>##### Valid Postfix Operators
>|||||
>|----|----|----|----|
>| (  | .  | ++ | -- |


# To-Do
> * Add support for predefined veriables and functions\
> * Add label support


# Tokens

***
The tokens I chose to implement were a subsection of the C99 ISO Standard found [here](https://www.dii.uchile.cl/~daespino/files/Iso_C_1999_definition.pdf)

#### *Disclaimer: I accept more tokens than will possible be supported by the compiler at later stages of development*

### Type Specifier

| Symbol    | Token Name |
| --------- | ---------- |
| `float`   | FLOAT      |
| `int`     | INT        |
|`short`    | SHORT      |
|`long`     | LONG       |
|`double`   | DOUBLE     |
|`char`     | CHAR       |
|`void`     | VOID       |
|`_Bool`    | _BOOL      |

### Declaration Specifier

| Symbol     | Token Name |
| ---------- | ---------- |
|`const`     | CONST      |
|`static`    | STATIC     |
|`unsigned`  | UNSIGNED   |
|`signed`    | SIGNED     |

### Statement Keyword
| Symbol      | Token Name |
| ----------- | ---------- |
|`if`         | IF         |
|`else`       | ELSE       |
|`while`      | WHILE      |
|`do`         | DO         |
|`for`        | FOR        |
|`switch`     | SWITCH     |
|`case`       | CASE       |
|`default`    | DEFAULT    |
|`return`     | RETURN     |
|`goto`       | GOTO       |
|`break`      | BREAK      |
|`continue`   | CONTINUE   |

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
| `(`    | LPAREN     |
| `)`    | RPAREN     |
| `{`    | LBRACE     |
| `}`    | RBRACE     |
| `,`    | COMMA      |
| `:`    | COLON      |
| `;`    | SEMICOLON  |
| `.`    | DOT        |

### Other Tokens
| Token Name     | Description              |
| -------------- | ------------------------ |
| IDENTIFIER     | User-defined identifiers |
| NUMBER         | Numeric literals         |
| CHAR_LITERAL   | Character literals       |
| STRING_LITERAL | String Literals          |
| EOF            | End-of-file marker       |

# Grammer

***

`<Program> ::= <TranslationUnit>* EOF`
`<TranslationUnit> ::= <Function> | <DeclarationStatement>`
`<DeclarationStatement> ::= <TypeSpecifiers> <VarDeclarationList> ";"`
`<DeclarationTypes> ::= <DeclarationSpecifiers>* <TypeSpecifiers>`
`<DeclarationSpecifiers> ::= CONST | STATIC | UNSIGNED | SIGNED`
`<VarDeclarationList> ::= <VarDeclaration> ( "," <VarDeclaration> )*`
`<VarDeclaration> ::= IDENTIFIER ( "=" <Expression> )?`
`<Function> ::= <FunctionDefinition> | <FunctionDeclaration>`
`<FunctionDeclaration> ::= <FunctionInit> ";"`
`<FunctionDefinition> ::= <FunctionInit> <CompoundStatement>`
`<CompoundStatement> ::= "{" (<DeclarationStatement> | <Statements>)* "}"`
`<FunctionInit> ::= <DeclarationTypes> <FunctionDeclarator>`
`<FunctionDeclarator> ::= IDENTIFIER "(" <FunctionParamList>? ")"`
`<FunctionParamList> ::= <ParamDeclaration> ("," <ParamDeclaration> )*`
`<ParamDeclaration> ::= <DeclarationTypes> IDENTIFIER?`
`<TypeSpecifiers> ::= FLOAT | INT | SHORT | LONG | DOUBLE | CHAR | _BOOL | VOID`
`<Statements> ::= <IfStatement>`
`| <WhileStatement>`
`| <DoWhileStatement>`
`| <ForStatement>`
`| <SwitchStatement>`
`| <ReturnStatement>`
`| <GotoStatement>`
`| <BreakStatement>`
`| <ContinueStatement>`
`| <LabelStatement>`
`| <DeclarationStatement>`
`| <ExprStatement>`
`<ExprStatement> ::= <Expression>? ";"`
`<IfStatement> ::= "if" "(" <Expression> ")" <CompoundStatement> ("else" <CompoundStatement>)?`
`<WhileStatement> ::= "while" "(" <Expression> ")" <CompoundStatement>`
`<DoWhileStatement> ::= "do" <CompoundStatement> "while" "(" <Expression> ")" ";"`
`<ForStatement> ::= "for" "(" (<DeclarationStatement> | ";") <Expression>? ";" <Expression>? ")" <CompoundStatement>`
`<SwitchStatement> ::= "switch" "(" <Expression> ")" <SwitchBody>`
`<SwitchBody> ::= "{" <SwitchSection>* "}"`
`<SwitchSection> ::= <SwitchLabel> <Statements>*`
`<SwitchLabel> ::= "case" <Expression> ":" | "default" ":"`
`<ReturnStatement> ::= "return" <Expression>? ";"`
`<GotoStatement> ::= "goto" IDENTIFIER ";"`
`<BreakStatement> ::= "break" ";"`
`<ContinueStatement> ::= "continue" ";"`
`<LabelStatement> ::= IDENTIFIER ":" <Statements>`

***
##### For all the expression handling, a Pratt parsing technique was used.
##### The grammer below is not a 1 to 1 mapping of the parser
***

`<Expression> ::= <AssignmentExpression>`
`<AssignmentExpression> ::= <LogicalOrExpression>  | <UnaryExpression> <AssignmentOperator> <AssignmentExpression>`
`<AssignmentOperator> ::= "=" | "+=" | "-=" | "*=" | "/=" | "%=" | "<<=" | ">>=" | "&=" | "^=" | "|="`
`<LogicalOrExpression> ::= <LogicalAndExpression> ( "||" <LogicalAndExpression> )*`
`<LogicalAndExpression> ::= <BitwiseOrExpression> ( "&&" <BitwiseOrExpression> )*`
`<BitwiseOrExpression> ::= <BitwiseXorExpression> ( "|" <BitwiseXorExpression> )*`
`<BitwiseXorExpression> ::= <BitwiseAndExpression> ( "^" <BitwiseAndExpression> )*`
`<BitwiseAndExpression> ::= <EqualityExpression> ( "&" <EqualityExpression> )*`
`<EqualityExpression> ::= <RelationalExpression> ( ("==" | "!=") <RelationalExpression> )*`
`<RelationalExpression> ::= <ShiftExpression> ( ("<" | ">" | "<=" | ">=") <ShiftExpression> )*`
`<ShiftExpression> ::= <AdditiveExpression> ( ("<<" | ">>") <AdditiveExpression> )*`
`<AdditiveExpression> ::= <MultiplicativeExpression> ( ("+" | "-") <MultiplicativeExpression> )*`
`<MultiplicativeExpression> ::= <UnaryExpression> ( ("*" | "/" | "%") <UnaryExpression> )*`
`<UnaryExpression> ::= <PrefixOperator> <UnaryExpression> | <PostfixExpression>`
`<PrefixOperator> ::= "++" | "--" | "+" | "-" | "!" | "~"`
`<PostfixExpression> ::= <PrimaryExpression> <PostfixOp>*`
`<PostfixOp> ::= "++" | "--"`
`| "(" <ArgumentExpressionList>? ")"`
`| "." IDENTIFIER`
`<ArgumentExpressionList> ::= <Expression> ("," <Expression> )*`
`<PrimaryExpression> ::= IDENTIFIER | NUMBER | STRING_LITERAL | "(" <Expression> ")"`

# ToDo
    Fixes: Function Definition has a list for body but only contains compound statement, declaration statement has it as a list, remove all different types of assign

    Move Instruction() to get_block funciton




# Sources
* https://matklad.github.io/2020/04/13/simple-but-powerful-pratt-parsing.html - helped understand Pratt parsing
* https://github.com/ShivamSarodia/ShivyC/ - used for help formatting README
* https://www.dii.uchile.cl/~daespino/files/Iso_C_1999_definition.pdf - used for what tokens to implement

