from typing import List, Optional, Sequence
from src.errors import ParserError
from src.tokens import (
    Token,
    DECLARATION_SPECIFIERS,
    TYPE_SPECIFIERS,
    TOKEN_PREC,
    PREFIX_OPERATORS,
    POSTFIX_OPERATORS,
    ASSIGNMENT_TOKENS
)
from src.ast_nodes import (
    Program,
    DeclarationStatement,
    DeclarationTypes,
    VarDeclaration,
    FunctionDeclaration,
    FunctionDefinition,
    ParameterDeclaration,
    CompoundStatement,
    IfStatement,
    WhileStatement,
    DoWhileStatement,
    ForStatement,
    SwitchSection,
    SwitchStatement,
    DefaultLabel,
    CallExpression,
    MemberExpression,
    PostfixExpression,
    PrefixExpression,
    Literal,
    Identifier,
    CaseLabel,
    ExpressionStatement,
    ContinueStatement,
    BreakStatement,
    GotoStatement,
    AssignmentExpression,
    BinaryExpression,
    LabelStatement,
    ReturnStatement
)


# None returns used to propegate dead ends
# AST tree is generated using custom classes found in ast_nodes.py
# There is not a direct 1 to 1 on ast_node classes and grammer rules

class Parser:
    '''Takes in a list of lexime tokens and returns a list of ast nodes'''

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.last_error: Optional[Token] = None
# Helper functions

    def _cur(self) -> Token:
        if self.pos >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return self._cur()

    def _match(self, *types: str) -> bool:
        tok = self._cur()
        if tok.type in types:
            return True
        return False

    def _peek(self) -> Token:
        if self.pos + 1 >= len(self.tokens):
            return self.tokens[self.pos + 1]
        return self.tokens[self.pos + 1]

    def _expect(self, types: Sequence[str]) -> Optional[Token]:
        tok = self._cur()
        if tok.type not in types:
            self.last_error = tok
            return None
        self._advance()
        return tok
# Parse entry point

    def parse(self) -> Program:
        return self._program()

    # <Program> ::= <TranslationUnit>* EOF
    def _program(self) -> Program:
        translation_units = []
        while self._cur().type != 'EOF':
            unit = self._translation_unit()
            if unit is None:
                error_token = self.last_error if self.last_error else self._cur()
                raise ParserError(
                    f'There was an error parsing token {self.last_error} at pos {self.pos} cur {self._cur()}',
                    self.last_error
                )
            translation_units.append(unit)
        return Program(translation_units)

    # <TranslationUnit> ::= <Function> | <DeclarationStatement>
    def _translation_unit(self):
        start = self.pos
        func = self._function()
        if func is not None:
            return func
        self.pos = start
        decl = self._declaration_statement()
        if decl is not None:
            return decl
        return None

    # <DeclarationStatement> ::= <DeclarationTypes> <VarDeclarationList> ";"
    def _declaration_statement(self):
        decl_type = self._declaration_types()
        if (decl_type is None):
            return None
        decl_list = self._var_declaration_list()
        if (decl_list is None):
            return None
        if (self._expect('SEMICOLON') is None):
            return None
        return DeclarationStatement(decl_type, decl_list)

    # <DeclarationTypes> ::= <DeclarationSpecifiers>* <DeclarationType>
    def _declaration_types(self):
        specifier_list = []
        while self._cur().type in DECLARATION_SPECIFIERS:
            specifier = self._expect(list(DECLARATION_SPECIFIERS))
            specifier_list.append(specifier)
        decl_type = self._expect(list(TYPE_SPECIFIERS))
        if (decl_type is None):
            return None
        return DeclarationTypes(specifier_list, decl_type)

    # <VarDeclarationList> ::= <VarDeclaration> ( "," <VarDeclaration> )*
    def _var_declaration_list(self):
        delc_list: List[VarDeclaration] = []
        var_decl = self._var_declaration()
        if (var_decl is None):
            return None
        delc_list.append(var_decl)
        while self._match('COMMA'):
            self._expect('COMMA')
            var_decl = self._var_declaration()
            if (var_decl is None):
                return None
            delc_list.append(var_decl)
        return delc_list

    # <VarDeclaration> ::= IDENTIFIER ( "=" <Expression> )?
    def _var_declaration(self):
        decl = self._declarator()
        if (decl is None):
            return None
        init = None
        if self._match('ASSIGN'):
            self._expect('ASSIGN')
            expr = self._expression(TOKEN_PREC['COMMA'] + 1)
            if (expr is None):
                return None
            init = expr
        return VarDeclaration(decl, init)

    # <Function> ::= <FunctionDefinition> | <FunctionDeclaration>
    def _function(self):
        init = self._function_init()
        if (init is None):
            return None
        decl_type, identifier, parameters = init
        if (self._match('SEMICOLON')):
            self._expect('SEMICOLON')
            return FunctionDeclaration(decl_type, identifier, parameters)
        statements = self._compound_statement()
        if (statements is None):
            return None

        return FunctionDefinition(decl_type, identifier, parameters, statements)

    # <FunctionInit> ::= <DeclarationTypes> <FunctionDeclarator>
    def _function_init(self):
        decl_type = self._declaration_types()
        if (decl_type is None):
            return None
        func_decl = self._function_declarator()
        if (func_decl is None):
            return None
        identifier, parameters = func_decl
        return (decl_type, identifier, parameters)

    # <FunctionDeclarator> ::= IDENTIFIER "(" <FunctionParamList>? ")"
    def _function_declarator(self):
        parameters = []
        identifier = self._expect('IDENTIFIER')
        if (identifier is None):
            return None
        if (self._expect('LPAREN') is None):
            return None
        if not self._match('RPAREN'):
            parameters = self._function_param_list()
            if (parameters is None):
                return None
        self._expect('RPAREN')
        return (identifier, parameters)

    # <FunctionParamList> ::= <ParamDeclaration> ("," <ParamDeclaration> )*
    def _function_param_list(self):
        param_list = []
        param_decl = self._param_declaration()
        if (param_decl is None):
            return None
        param_list.append(param_decl)
        while (self._match('COMMA')):
            self._expect('COMMA')
            param_decl = self._param_declaration()
            if (param_decl is None):
                return None
            param_list.append(param_decl)
        return param_list

    # <ParamDeclaration> ::= <DeclarationTypes> IDENTIFIER?
    def _param_declaration(self):
        decl_types = self._declaration_types()
        if (decl_types is None):
            return None
        decl = None
        if self._match('IDENTIFIER'):
            decl = self._declarator()
        return ParameterDeclaration(decl_types, decl)

    # IDENTIFIER
    def _declarator(self):
        identifier = self._expect('IDENTIFIER')
        if (identifier is None):
            return None
        return identifier

    # <CompoundStatement> ::= "{" (<DeclarationStatement> | <Statements>)* "}"
    def _compound_statement(self):
        if self._expect('LBRACE') is None:
            return None
        statements = []
        while not self._match('RBRACE'):
            if self._match(*DECLARATION_SPECIFIERS) or self._match(*TYPE_SPECIFIERS):
                decl_stmt = self._declaration_statement()
                if decl_stmt is None:
                    return None
                statements.append(decl_stmt)
                continue
            stmt = self._statement()
            if stmt is None:
                return None
            statements.append(stmt)
        self._expect('RBRACE')
        return CompoundStatement(statements)

    # <Statements> ::= <IfStatement>
    # | <WhileStatement>
    # | <DoWhileStatement>
    # | <ForStatement>
    # | <SwitchStatement>
    # | <ReturnStatement>
    # | <GotoStatement>
    # | <BreakStatement>
    # | <ContinueStatement>
    # | <LabelStatement>
    # | <DeclarationStatement>
    def _statement(self):
        if self._match('IF'):
            return self._if_statement()
        if self._match('WHILE'):
            return self._while_statement()
        if self._match('DO'):
            return self._do_while_statement()
        if self._match('FOR'):
            return self._for_statement()
        if self._match('SWITCH'):
            return self._switch_statement()
        if self._match('RETURN'):
            return self._return_statement()
        if self._match('GOTO'):
            return self._goto_statement()
        if self._match('BREAK'):
            return self._break_statement()
        if self._match('CONTINUE'):
            return self._continue_statement()
        # label needs to be checked before compound statement and expression otherwise they consume IDENTIFIER
        if self._match('IDENTIFIER') and self._peek().type == 'COLON':
            return self._label_statement()
        if self._match('LBRACE'):
            return self._compound_statement()
        return self._expr_statement()

    # <IfStatement> ::= "if" "(" <Expression> ")" <CompoundStatement> ("else" <CompoundStatement>)?
    def _if_statement(self):
        if self._expect('IF') is None:
            return None
        if self._expect('LPAREN') is None:
            return None
        condition = self._expression()
        if condition is None:
            return None
        if self._expect('RPAREN') is None:
            return None
        then_branch = self._statement()
        if then_branch is None:
            return None
        else_branch = None
        if self._match('ELSE'):
            self._expect('ELSE')
            else_branch = self._statement()
            if else_branch is None:
                return None
        return IfStatement(condition, then_branch, else_branch)

    # <WhileStatement> ::= "while" "(" <Expression> ")" <CompoundStatement>
    def _while_statement(self):
        if self._expect('WHILE') is None:
            return None
        if self._expect('LPAREN') is None:
            return None
        condition = self._expression()
        if condition is None:
            return None
        if self._expect('RPAREN') is None:
            return None
        body = self._statement()
        if body is None:
            return None
        return WhileStatement(condition, body)

    # <DoWhileStatement> ::= "do" <CompoundStatement> "while" "(" <Expression> ")" ";"
    def _do_while_statement(self):
        if self._expect('DO') is None:
            return None
        body = self._statement()
        if body is None:
            return None
        if self._expect('WHILE') is None:
            return None
        if self._expect('LPAREN') is None:
            return None
        condition = self._expression()
        if condition is None:
            return None
        if self._expect('RPAREN') is None:
            return None
        if self._expect('SEMICOLON') is None:
            return None
        return DoWhileStatement(body, condition)

    # <ForStatement> ::= "for" "(" (<DeclarationStatement> | ";") <Expression>? ";" <Expression>? ")" <CompoundStatement>
    def _for_statement(self):
        if self._expect('FOR') is None:
            return None
        if self._expect('LPAREN') is None:
            return None
        initializer = None
        if self._cur().type != 'SEMICOLON':
            start_pos = self.pos
            initializer = self._declaration_statement()
            if initializer is None:
                self.pos = start_pos
                expr = self._expression()
                if expr is None:
                    return None
                if self._expect('SEMICOLON') is None:
                    return None
                initializer = ExpressionStatement(expr)
        else:
            if self._expect('SEMICOLON') is None:
                return None
        condition = None
        if self._cur().type != 'SEMICOLON':
            condition = self._expression()
            if condition is None:
                return None
        if self._expect('SEMICOLON') is None:
            return None
        increment = None
        if self._cur().type != 'RPAREN':
            increment = self._expression()
            if increment is None:
                return None
        if self._expect('RPAREN') is None:
            return None
        body = self._statement()
        if body is None:
            return None
        return ForStatement(initializer, condition, increment, body)

    # <SwitchStatement> ::= "switch" "(" <Expression> ")" <SwitchBody>
    def _switch_statement(self):
        if self._expect('SWITCH') is None:
            return None
        if self._expect('LPAREN') is None:
            return None
        expression = self._expression()
        if expression is None:
            return None
        if self._expect('RPAREN') is None:
            return None
        body = self._switch_body()
        if body is None:
            return None
        return SwitchStatement(expression, body)

    # <SwitchBody> ::= "{" <SwitchSection>* "}"
    def _switch_body(self):
        if self._expect('LBRACE') is None:
            return None
        sections = []
        while True:
            cur = self._cur()
            if cur.type == 'RBRACE':
                break
            section = self._switch_section()
            if section is None:
                return None
            sections.append(section)
        if self._expect('RBRACE') is None:
            return None
        return sections

    # <SwitchSection> ::= <SwitchLabel> <Statements>*
    def _switch_section(self):
        label = self._switch_label()
        if label is None:
            return None
        label_list = [label]
        while self._cur().type in {'CASE', 'DEFAULT'}:
            label = self._switch_label()
            if label is None:
                return None
            label_list.append(label)
        items = []
        while self._cur().type not in {'CASE', 'DEFAULT', 'RBRACE'}:
            stmt = self._statement()
            if stmt is None:
                return None
            items.append(stmt)
        return SwitchSection(label_list, items)

    # <SwitchLabel> ::= "case" <Expression> ":" | "default" ":"
    def _switch_label(self):
        cur = self._cur()
        if cur.type == 'CASE':
            case_tok = self._expect('CASE')
            if case_tok is None:
                return None
            expr = self._expression()
            if expr is None:
                return None
            if self._expect('COLON') is None:
                return None
            return CaseLabel(case_tok, expr)
        if cur.type == 'DEFAULT':
            default_tok = self._expect('DEFAULT')
            if default_tok is None:
                return None
            if self._expect('COLON') is None:
                return None
            return DefaultLabel(default_tok)
        return None

    # <ExprStatement> ::= <Expression>? ";"
    def _expr_statement(self):
        if self._match('SEMICOLON'):
            self._expect('SEMICOLON')
            return ExpressionStatement(None)
        expr = self._expression()
        if expr is None:
            return None
        if self._expect('SEMICOLON') is None:
            return None
        return ExpressionStatement(expr)

    # <ReturnStatement> ::= "return" <Expression>? ";"
    def _return_statement(self):
        if (self._expect('RETURN') is None):
            return None
        expression = None
        if not self._match('SEMICOLON'):
            expression = self._expression()
            if expression is None:
                return None
        self._expect('SEMICOLON')
        return ReturnStatement(expression)

    # <GotoStatement> ::= "goto" IDENTIFIER ";"
    def _goto_statement(self):
        if self._expect('GOTO') is None:
            return None
        identifier = self._expect('IDENTIFIER')
        if (identifier is None):
            return None
        if self._expect('SEMICOLON') is None:
            return None
        return GotoStatement(identifier)

    # <BreakStatement> ::= "break" ";"
    def _break_statement(self):
        if self._expect('BREAK') is None:
            return None
        if self._expect('SEMICOLON') is None:
            return None
        return BreakStatement()

    # <ContinueStatement> ::= "continue" ";"
    def _continue_statement(self):
        if self._expect('CONTINUE') is None:
            return None
        if self._expect('SEMICOLON') is None:
            return None
        return ContinueStatement()

    # <LabelStatement> ::= IDENTIFIER ":" <Statements>
    def _label_statement(self):
        identifier = self._expect('IDENTIFIER')
        if (identifier is None):
            return None
        if self._expect('COLON') is None:
            return None
        statement = self._statement()
        if statement is None:
            return None
        return LabelStatement(identifier, statement)

    # ------------------------------------------------------------------
    # Pratt parser For Expressions
    # ------------------------------------------------------------------

    # This part of the code does not correlate to the grammar one to one
    # This uses a precidence table to determine which side of the expression to collapse
    # The token precidence table can be found in tokens.py -> TOKEN_PREC
    def _expression(self, min_prec: int = 0):
        # first combine prefix
        node = self._parse_prefix()
        if node is None:
            return None
        while True:
            tok = self._cur()
            # post op increment / decrement and function calls
            if tok.type in POSTFIX_OPERATORS:
                node = self._apply_postfix(node)
                if node is None:
                    return None
                continue
            prec = TOKEN_PREC.get(tok.type, -1)
            # collapses expression to the right side if left side token has a lower precedence
            if prec < min_prec:
                break
            operator = tok
            self._advance()
            # if not an assignment token, + 1 to current precedence
            # this covers if both left and right are the same operation, guarantee left side collapse
            next_prec = prec if tok.type in ASSIGNMENT_TOKENS else prec + 1
            right = self._expression(next_prec)
            # if end of expression
            if right is None:
                return None
            if operator.type in ASSIGNMENT_TOKENS:
                node = AssignmentExpression(operator, node, right)
            else:
                node = BinaryExpression(operator, node, right)
        return node

    # Supported prefix operations:
    # 'PLUS', 'MINUS', 'LOGNOT', 'BITNOT', 'INCREMENT', 'DECREMENT'
    def _parse_prefix(self):
        if self._match(*PREFIX_OPERATORS):
            prefix = self._expect(list(PREFIX_OPERATORS))
            prefix_int = TOKEN_PREC.get('PREFIX')
            assert (isinstance(prefix_int, int))
            operand = self._expression(prefix_int)
            return PrefixExpression(prefix, operand)
        # If no prefix
        primary = self._parse_primary()
        if primary is None:
            return None
        return primary

    def _parse_primary(self):
        # Parentheses handling
        if self._match('LPAREN'):
            self._expect('LPAREN')
            expr = self._expression()
            if (expr is None):
                return None
            self._expect('RPAREN')
            return expr
        # If no parentheses
        if self._match('NUMBER', 'STRING_LITERAL', 'CHAR_LITERAL'):
            tok = self._expect(['NUMBER', 'STRING_LITERAL', 'CHAR_LITERAL'])
            return Literal(tok)
        if self._match('IDENTIFIER'):
            tok = self._expect('IDENTIFIER')
            return Identifier(tok)
        return None

    # Supported postfic operations:
    # 'LPAREN', 'DOT', 'INCREMENT', 'DECREMENT'
    def _apply_postfix(self, node):
        # Function Calls
        if self._match('LPAREN'):
            func_call = self._function_call(node)
            if (func_call is None):
                return None
            return func_call
        # Member Expressions
        if self._match('DOT'):
            self._advance()
            identifier = self._expect('IDENTIFIER')
            if identifier is None:
                return None
            return MemberExpression(node, identifier)
        # Postfix Operations
        if self._match('INCREMENT', 'DECREMENT'):
            postfix = self._expect(['INCREMENT', 'DECREMENT'])
            return PostfixExpression(node, postfix)
        return node

    # builds argument list for function calls
    def _function_call(self, node):
        self._advance()
        args = []
        if self._match('RPAREN'):
            if (self._expect('RPAREN') is None):
                return None
            return CallExpression(node, args)
        expr = self._expression(TOKEN_PREC['COMMA'] + 1)
        if expr is None:
            return None
        args.append(expr)
        while self._match('COMMA'):
            self._expect('COMMA')
            if self._match('RPAREN'):
                break
            args.append(self._expression(TOKEN_PREC['COMMA'] + 1))
        if self._expect('RPAREN') is None:
            return None
        return CallExpression(node, args)
