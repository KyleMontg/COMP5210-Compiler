# **COMP5210-Compiler**
A compiler for a subsection of the C99 programming language by Kyle Montgomery.


># Table of Contents
>[Requirements](#requirements)  
>[Usage](#Usage)  
>[Language Specification](#language-specifications)  
>[Optimization](#optimizations)  
>[Lexical Tokens](#Tokens)  
>[Grammer Rules](#Grammer)  
>[Compiler Stages](#Compiler-Stages)  
>[Sources](#sources)  


## Requirements
##### Python 3.12 or later

***

## Usage
##### Run code  
>`python main.py input.c -o1 -asm`  
**flags**  
> `-l` Contents of lexer will be printed to console  
> `-a` Contents of Parser will be printed to console  
> `-t` Contents of Symbol Table will be printed to console  
> `-w "file_location/file_name"` When flagged, output file name and directory can be specified, defaults to output.txt in main directory  
> `-o0` Create the Three Address Code with no optimizations and print to terminal  
> `-o1` Create the Three Address Code with all optimizations and print to terminal  
> `-asm` Generates X86 Assembly for 64-bit Windows  
##### Run Tests
>`python test_runner.py --all`
**flags**
> `-l` Test Lexer
> `-p` Test Parser
> `-s` Test Semantic Analysis
> `-t` Test Three Address Code
> `-o` Test Optimizations
> `-a` Test All


# Language Specifications
***


### Lexical Specification
#### Types
* int: (signed 64-bit integers only)
#### Operators
* Arithmetic: `+, -, *, /, %, ++, --`
* Comparison: `<, >, <=, >=, ==, !=`
* Bitwise: `&, |, ^, ~, <<, >>`
* Logical: `&&, ||, !`
* Assignment: `=, !=, -=, *=, /=, %=`
#### Control Flow
* if / else
* while loops
* do-while loops
* for loops
* return
* break / continue
* goto / labels
#### Functions
* Supports one function with parameters
#### Expressions
* Binary Expressions
* Unary Expressions
* Assignment Expressions
* Supports use of Parentheses
#### Comments
* Single Line: `//`
* Multi-line: `/* */`
#### Unsupported
* Strings
* Chars
* Floating point numbers
* Pointers
* Funciton Calls
* Type Qualifiers



### Implimentation Specifications


##### Three Address Code Instruction Structure
* I reuse the same Instruction Object having fields:
* res (result)
* left (left side of operation)
* right (right side of operation)
* op (operator)
* Below are the different ways an instructions is constructed

>**DECL**    res=<identifier token>, left=<initializer token/temp>, right=None, op=None`

>**ASSIGN**  res=<target>, left=<operand>, right=<operand or None>, op=<operator token>`

>**PARAM**   res=Token('PARAM','param'), left=<argument value>, right=None, op=None`

>**CALL**    res=<temp for return>, left=<callee name>, right=None, op=Token('CALL','call')`

>**LABEL**   res=<label name string>, left=None, right=None, op=Token('LABEL','label')`

>**GOTO**    res=<target label>, left=None, right=None, op=Token('GOTO','goto')`

>**IF**      res=<condition temp>, left=<true label>, right=<false label>, op=Token('IFSTMT','if')

>**FOR**     res=<condition temp>, left=<body label>, right=<exit label>, op=Token('FORSTMT','for')`

>**WHILE**   res=<condition temp>, left=<body label>, right=<exit label>, op=Token('WHILESTMT','while')`

>**RETURN**  res=<value temp/literal>, left=None, right=None, op=Token('RETURN','return')`

***

#### Assembly Specification
* Windows X86
* Below is how I reserve registers:
*The first 4 parameters are held at:
> 1) rcx
> 2) rdx
> 3) r8
> 4) r9
> 5) or more live on the stack

> rbp - used for frame pointer
> rax - return register / used in division
> rcx - used as a temp register when needed
> r10 - r15 - used as general use registers


***
### Optimizations
#### Copy and Constant Propigation
* Creates a control flow graph and iterates through each block
* Propigates constant variables and literals
#### Constant Folding
* Collapses Binary Operations
#### Dead Code Elimination
* Creates a control flow graph and iterates through each block
* Marks variables defined and used
* Iterates through blocks until no change in used and unkown variables
* Removes unused variables
* Redirects labels followed directly by gotos to the goto destination
#### Register Optimization
* Creates a control flow graph
* Gets the live in and out sets for each control block
* Uses the out of each control block to propigate out to individual instructions
* Creates a tnterference graph to represent edges
* Uses greedy coloring algorithm to assign registers to variables


# Tokens

***
The tokens I chose to implement were a subsection of the C99 ISO Standard found [here](https://www.dii.uchile.cl/~daespino/files/Iso_C_1999_definition.pdf)

#### *Disclaimer: I accept more tokens than will possible be supported by the compiler at later stages of development*

### Type Specifier

| Symbol    | Token Name |
| --------- | ---------- |
| `int`     | INT        |
|`void`     | VOID       |

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

# Compiler Stages
***
### 1. Lexer (`lexer.py`)
* Tokenizes source code
### 2. Parser (`parser.py`)
* Recurive decent parser / Pratt parsing for expressions
* Builds Abstract Syntax Tree
### 3. Symbol Table (`symbol_table.py`)
* Tracks variable declarations and scopes
### 4. Semantic Analysis (`semantic_analysis.py`)
* Type Checking
* Undefined / uninitialized variable tracking
### 5. TAC Generation (`tac.py`)
* Generates a Three Address Code representation
### 6. Optimizations
* Constant Folding(`constant_fold.py`)
* Copy Propagation(`copy_and_constant_propagation.py`)
* Constant Propagation(`copy_and_constant_propagation.py`)
* Dead Code Elimination(`dead_code_elimination.py`)
### 7. Register Allocation(`register_optimization.py`)
* Block Liveness Analysis
* Line Liveness Analysis
* Interference graph construction
* Greedy graph coloring register allocation
### 8. Assembly Generation(`asm.py`)
* Windows X86-64 calling convention
* Register allocation mapping

***

# Sources
#### Prat Parsing
* https://matklad.github.io/2020/04/13/simple-but-powerful-pratt-parsing.html
#### Format READMEs
* https://github.com/ShivamSarodia/ShivyC/
#### C Standard Specification
* https://www.dii.uchile.cl/~daespino/files/Iso_C_1999_definition.pdf
#### Liveness Analysis / Interference Graphs
* https://www.youtube.com/watch?v=eeXk_ec1n6g
#### Greedy Graph Coloring
* https://www.geeksforgeeks.org/dsa/graph-coloring-set-2-greedy-algorithm/
#### control Flow Graph
* https://www.geeksforgeeks.org/software-engineering/software-engineering-control-flow-graph-cfg/
