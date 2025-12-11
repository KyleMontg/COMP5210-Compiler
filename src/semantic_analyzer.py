from src.ast_nodes import *
from src.symbol_table import SymbolTable, Scope
from src.errors import SemanticError
from src.tokens import Token
from typing import Set, Optional


class SemanticAnalyzer:
    """
    Performs comprehensive semantic analysis on the AST:
    1. Reject strings and char literals
    2. Reject non-int types (only allow signed 64-bit int)
    3. Reject function calls
    4. Reject member expressions (struct access)
    5. Check that all variables are defined before use
    6. Check that all variables are initialized before use
    """

    def __init__(self, ast: Program, symbol_table: SymbolTable):
        self.ast = ast
        self.symbol_table = symbol_table
        self.current_scope = symbol_table.global_scope

    def analyze(self):
        """Run all semantic analysis passes"""
        # Pass 1: Check type restrictions and forbidden constructs
        self.check_type_restrictions()

        # Pass 2: Check undefined variables
        self.check_undefined_variables()

        # Pass 3: Check uninitialized variables
        self.check_uninitialized_usage()

    # ==================== PASS 1: TYPE RESTRICTIONS ====================

    def check_type_restrictions(self):
        """
        Check for:
        - String literals
        - Char literals
        - Non-int types
        - Function calls
        - Member expressions
        """
        for unit in self.ast.units:
            if isinstance(unit, FunctionDefinition):
                # Check function return type
                self._check_type_is_int(unit.func_type)

                # Check parameter types
                for param in unit.func_param:
                    self._check_type_is_int(param.decl_type)

                # Enter function scope
                self._enter_scope_by_name(unit.func_ident.value)

                # Check function body
                self._check_statement_restrictions(unit.func_body)

                # Exit function scope
                self._exit_scope()

            elif isinstance(unit, FunctionDeclaration):
                # Check function declaration type
                self._check_type_is_int(unit.func_type)

                # Check parameter types
                for param in unit.func_param:
                    self._check_type_is_int(param.decl_type)

            elif isinstance(unit, DeclarationStatement):
                # Check global declaration type
                self._check_type_is_int(unit.decl_type)

                # Check initializers
                for decl in unit.declarations:
                    if decl and decl.initializer:
                        self._check_expression_restrictions(decl.initializer)

    def _check_type_is_int(self, decl_type):
        """Ensure type is 'int' (no char, void, _Bool, etc.)"""
        if not hasattr(decl_type, 'base'):
            return

        base_type = decl_type.base

        # Reject non-int types
        if base_type.type != 'INT':
            raise SemanticError(
                f"Type '{base_type.value}' is not supported. "
                "This compiler only supports 'int' (signed 64-bit integers).",
                base_type
            )

        # Reject unsigned, const, static specifiers
        if hasattr(decl_type, 'specifiers'):
            for spec in decl_type.specifiers:
                if spec.type in ('UNSIGNED', 'CONST', 'STATIC'):
                    raise SemanticError(
                        f"Type specifier '{spec.value}' is not supported. "
                        "This compiler only supports plain 'int' (signed 64-bit).",
                        spec
                    )

    def _check_statement_restrictions(self, stmt):
        """Check statement for restricted constructs"""

        if isinstance(stmt, DeclarationStatement):
            # Check type is int
            self._check_type_is_int(stmt.decl_type)

            # Check initializers
            for decl in stmt.declarations:
                if decl and decl.initializer:
                    self._check_expression_restrictions(decl.initializer)

        elif isinstance(stmt, ExpressionStatement):
            if stmt.expression:
                self._check_expression_restrictions(stmt.expression)

        elif isinstance(stmt, ReturnStatement):
            if stmt.expression:
                self._check_expression_restrictions(stmt.expression)

        elif isinstance(stmt, CompoundStatement):
            # Enter block scope
            self._enter_first_block_scope()
            for item in stmt.items:
                self._check_statement_restrictions(item)
            self._exit_scope()

        elif isinstance(stmt, IfStatement):
            self._check_expression_restrictions(stmt.condition)
            self._check_statement_restrictions(stmt.then_branch)
            if stmt.else_branch:
                self._check_statement_restrictions(stmt.else_branch)

        elif isinstance(stmt, WhileStatement):
            self._check_expression_restrictions(stmt.condition)
            self._check_statement_restrictions(stmt.body)

        elif isinstance(stmt, DoWhileStatement):
            self._check_statement_restrictions(stmt.body)
            self._check_expression_restrictions(stmt.condition)

        elif isinstance(stmt, ForStatement):
            # Enter for scope
            self._enter_scope_by_name('for_stmt')

            if stmt.initializer:
                if isinstance(stmt.initializer, DeclarationStatement):
                    self._check_type_is_int(stmt.initializer.decl_type)
                    for decl in stmt.initializer.declarations:
                        if decl and decl.initializer:
                            self._check_expression_restrictions(
                                decl.initializer)
                else:
                    self._check_expression_restrictions(stmt.initializer)

            if stmt.condition:
                self._check_expression_restrictions(stmt.condition)

            if stmt.increment:
                self._check_expression_restrictions(stmt.increment)

            self._check_statement_restrictions(stmt.body)

            self._exit_scope()

    def _check_expression_restrictions(self, expr):
        """Check expression for restricted constructs"""

        if isinstance(expr, Literal):
            # REJECT string literals
            if expr.token.type == 'STRING_LITERAL':
                raise SemanticError(
                    "String literals are not supported. "
                    "This compiler only supports signed 64-bit integers.",
                    expr.token
                )

            # REJECT char literals
            if expr.token.type == 'CHAR_LITERAL':
                raise SemanticError(
                    "Character literals are not supported. "
                    "This compiler only supports signed 64-bit integers.",
                    expr.token
                )

        elif isinstance(expr, CallExpression):
            # REJECT function calls
            if hasattr(expr.callee, 'token'):
                token = expr.callee.token
            else:
                token = None

            raise SemanticError(
                "Function calls are not supported in this compiler. "
                "Only variable declarations, assignments, and control flow are allowed.",
                token
            )

        elif isinstance(expr, MemberExpression):
            # REJECT member access (struct/union fields)
            if hasattr(expr.property, 'token'):
                token = expr.property.token
            else:
                token = None

            raise SemanticError(
                "Member access (struct/union fields) is not supported in this compiler. "
                "Only simple integer variables are allowed.",
                token
            )

        elif isinstance(expr, BinaryExpression):
            self._check_expression_restrictions(expr.left)
            self._check_expression_restrictions(expr.right)

        elif isinstance(expr, AssignmentExpression):
            self._check_expression_restrictions(expr.left)
            self._check_expression_restrictions(expr.right)

        elif isinstance(expr, PrefixExpression):
            self._check_expression_restrictions(expr.operand)

        elif isinstance(expr, PostfixExpression):
            self._check_expression_restrictions(expr.operand)

        elif isinstance(expr, Identifier):
            # Identifiers are fine (will be checked in other passes)
            pass

    # ==================== PASS 2: UNDEFINED VARIABLES ====================

    def check_undefined_variables(self):
        """Check that all used variables are defined in scope"""
        for unit in self.ast.units:
            if isinstance(unit, FunctionDefinition):
                # Enter function scope
                self._enter_scope_by_name(unit.func_ident.value)

                # Check function body
                self._check_statement_for_undefined(unit.func_body)

                # Exit function scope
                self._exit_scope()

            elif isinstance(unit, DeclarationStatement):
                # Check global declarations
                for decl in unit.declarations:
                    if decl and decl.initializer:
                        self._check_expression_for_undefined(decl.initializer)

    def _check_statement_for_undefined(self, stmt):
        """Recursively check statement for undefined variables"""

        if isinstance(stmt, DeclarationStatement):
            # Check initializers
            for decl in stmt.declarations:
                if decl and decl.initializer:
                    self._check_expression_for_undefined(decl.initializer)

        elif isinstance(stmt, ExpressionStatement):
            if stmt.expression:
                self._check_expression_for_undefined(stmt.expression)

        elif isinstance(stmt, ReturnStatement):
            if stmt.expression:
                self._check_expression_for_undefined(stmt.expression)

        elif isinstance(stmt, CompoundStatement):
            # Enter block scope
            self._enter_first_block_scope()
            for item in stmt.items:
                self._check_statement_for_undefined(item)
            self._exit_scope()

        elif isinstance(stmt, IfStatement):
            self._check_expression_for_undefined(stmt.condition)
            self._check_statement_for_undefined(stmt.then_branch)
            if stmt.else_branch:
                self._check_statement_for_undefined(stmt.else_branch)

        elif isinstance(stmt, WhileStatement):
            self._check_expression_for_undefined(stmt.condition)
            self._check_statement_for_undefined(stmt.body)

        elif isinstance(stmt, DoWhileStatement):
            self._check_statement_for_undefined(stmt.body)
            self._check_expression_for_undefined(stmt.condition)

        elif isinstance(stmt, ForStatement):
            # Enter for scope
            self._enter_scope_by_name('for_stmt')

            if stmt.initializer:
                if isinstance(stmt.initializer, DeclarationStatement):
                    for decl in stmt.initializer.declarations:
                        if decl and decl.initializer:
                            self._check_expression_for_undefined(
                                decl.initializer)
                else:
                    # initializer is ExpressionStatement
                    if isinstance(stmt.initializer, ExpressionStatement):
                        if stmt.initializer.expression:
                            self._check_expression_for_undefined(
                                stmt.initializer.expression)
                    else:
                        self._check_expression_for_undefined(stmt.initializer)

            if stmt.condition:
                self._check_expression_for_undefined(stmt.condition)

            if stmt.increment:
                self._check_expression_for_undefined(stmt.increment)

            self._check_statement_for_undefined(stmt.body)

            self._exit_scope()

    def _check_expression_for_undefined(self, expr):
        """Recursively check expression for undefined variables"""

        if isinstance(expr, Identifier):
            var_name = expr.token.value
            if not self._is_variable_defined(var_name):
                raise SemanticError(
                    f"Variable '{var_name}' is used before being declared.",
                    expr.token
                )

        elif isinstance(expr, BinaryExpression):
            self._check_expression_for_undefined(expr.left)
            self._check_expression_for_undefined(expr.right)

        elif isinstance(expr, AssignmentExpression):
            # Check right side first
            self._check_expression_for_undefined(expr.right)

            # Check left side (should be defined)
            if isinstance(expr.left, Identifier):
                var_name = expr.left.token.value
                if not self._is_variable_defined(var_name):
                    raise SemanticError(
                        f"Variable '{var_name}' is assigned before being declared.",
                        expr.left.token
                    )

        elif isinstance(expr, PrefixExpression):
            self._check_expression_for_undefined(expr.operand)

        elif isinstance(expr, PostfixExpression):
            self._check_expression_for_undefined(expr.operand)

        elif isinstance(expr, Literal):
            # Literals are always fine
            pass

    # ==================== PASS 3: UNINITIALIZED VARIABLES ====================

    def check_uninitialized_usage(self):
        """Check that variables aren't used before initialization"""
        for unit in self.ast.units:
            if isinstance(unit, FunctionDefinition):
                # Enter function scope
                self._enter_scope_by_name(unit.func_ident.value)

                # Parameters are initialized
                initialized: Set[str] = set()
                for param in unit.func_param:
                    if param.declarator:
                        initialized.add(param.declarator.value)

                # Check function body
                self._check_statement_for_initialization(
                    unit.func_body, initialized)

                # Exit function scope
                self._exit_scope()

    def _check_statement_for_initialization(self, stmt, initialized: Set[str]):
        """Track initialization and check usage"""

        if isinstance(stmt, DeclarationStatement):
            for decl in stmt.declarations:
                if decl:
                    if decl.initializer is not None:
                        # Check initializer first
                        self._check_expression_for_initialization(
                            decl.initializer, initialized)
                        # Then mark as initialized
                        initialized.add(decl.declarator.value)
                    # else: declared but NOT initialized - don't add to set

        elif isinstance(stmt, ExpressionStatement):
            if stmt.expression:
                if isinstance(stmt.expression, AssignmentExpression):
                    # Check right side first
                    self._check_expression_for_initialization(
                        stmt.expression.right, initialized)

                    # After assignment, left side is initialized
                    if isinstance(stmt.expression.left, Identifier):
                        initialized.add(stmt.expression.left.token.value)
                else:
                    self._check_expression_for_initialization(
                        stmt.expression, initialized)

        elif isinstance(stmt, ReturnStatement):
            if stmt.expression:
                self._check_expression_for_initialization(
                    stmt.expression, initialized)

        elif isinstance(stmt, CompoundStatement):
            # Create new set for block scope (copy parent's initialized vars)
            block_initialized = initialized.copy()

            # Enter block scope
            self._enter_first_block_scope()

            for item in stmt.items:
                self._check_statement_for_initialization(
                    item, block_initialized)

            # Exit block scope
            self._exit_scope()

            # Don't propagate block-local initializations to outer scope

        elif isinstance(stmt, IfStatement):
            # Check condition
            self._check_expression_for_initialization(
                stmt.condition, initialized)

            # Both branches see same initialization state
            then_init = initialized.copy()
            self._check_statement_for_initialization(
                stmt.then_branch, then_init)

            if stmt.else_branch:
                else_init = initialized.copy()
                self._check_statement_for_initialization(
                    stmt.else_branch, else_init)

            # Conservative: don't propagate any new initializations from branches

        elif isinstance(stmt, WhileStatement):
            self._check_expression_for_initialization(
                stmt.condition, initialized)

            # Body doesn't guarantee execution, so don't propagate initializations
            body_init = initialized.copy()
            self._check_statement_for_initialization(stmt.body, body_init)

        elif isinstance(stmt, DoWhileStatement):
            # Body executes at least once
            self._check_statement_for_initialization(stmt.body, initialized)
            self._check_expression_for_initialization(
                stmt.condition, initialized)

        elif isinstance(stmt, ForStatement):
            # Enter for scope
            self._enter_scope_by_name('for_stmt')

            # Create local initialization tracking
            for_init = initialized.copy()

            # Initializer
            if stmt.initializer:
                if isinstance(stmt.initializer, DeclarationStatement):
                    for decl in stmt.initializer.declarations:
                        if decl and decl.initializer:
                            self._check_expression_for_initialization(
                                decl.initializer, for_init)
                            for_init.add(decl.declarator.value)

                else:
                    # initializer is ExpressionStatement
                    if isinstance(stmt.initializer, ExpressionStatement):
                        expr = stmt.initializer.expression  # Get the actual expression!
                        if isinstance(expr, AssignmentExpression):
                            # Check right side
                            self._check_expression_for_initialization(
                                expr.right, for_init)
                            # Mark left side as initialized (for = operator only)
                            if expr.operator.type == 'ASSIGN':
                                if isinstance(expr.left, Identifier):
                                    var_name = expr.left.token.value
                                    for_init.add(expr.left.token.value)
                                    initialized.add(var_name)
                    else:
                        # Fallback
                        self._check_expression_for_initialization(
                            stmt.initializer, for_init)
            # Condition
            if stmt.condition:
                self._check_expression_for_initialization(
                    stmt.condition, for_init)

            # Body (doesn't guarantee execution)
            body_init = for_init.copy()
            self._check_statement_for_initialization(stmt.body, body_init)

            # Increment
            if stmt.increment:
                self._check_expression_for_initialization(
                    stmt.increment, for_init)

            # Exit for scope
            self._exit_scope()

    def _check_expression_for_initialization(self, expr, initialized: Set[str]):
        """Check if expression uses uninitialized variables"""

        if isinstance(expr, Identifier):
            var_name = expr.token.value

            # Check if initialized
            if var_name not in initialized:
                # It's declared (we checked in pass 2), but not initialized
                raise SemanticError(
                    f"Variable '{var_name}' is used before being initialized.",
                    expr.token
                )

        elif isinstance(expr, BinaryExpression):
            self._check_expression_for_initialization(expr.left, initialized)
            self._check_expression_for_initialization(expr.right, initialized)

        elif isinstance(expr, AssignmentExpression):
            # Right side must be initialized
            self._check_expression_for_initialization(expr.right, initialized)

            # Left side check depends on operator
            # For compound assignments (+=, etc.), left side must be initialized
            if expr.operator.type != 'ASSIGN':
                if isinstance(expr.left, Identifier):
                    var_name = expr.left.token.value
                    if var_name not in initialized:
                        raise SemanticError(
                            f"Variable '{var_name}' is used in compound assignment "
                            f"before being initialized.",
                            expr.left.token
                        )

        elif isinstance(expr, PrefixExpression):
            # ++x or --x requires x to be initialized
            if expr.prefix.type in ('INCREMENT', 'DECREMENT'):
                if isinstance(expr.operand, Identifier):
                    var_name = expr.operand.token.value
                    if var_name not in initialized:
                        raise SemanticError(
                            f"Variable '{var_name}' is used in increment/decrement "
                            f"before being initialized.",
                            expr.operand.token
                        )
            else:
                self._check_expression_for_initialization(
                    expr.operand, initialized)

        elif isinstance(expr, PostfixExpression):

            # x++ or x-- requires x to be initialized
            if hasattr(expr.postfix, 'type') and expr.postfix.type in ('INCREMENT', 'DECREMENT'):
                if isinstance(expr.operand, Identifier):
                    var_name = expr.operand.token.value
                    if var_name not in initialized:
                        raise SemanticError(
                            f"Variable '{var_name}' is used in increment/decrement "
                            f"before being initialized.",
                            expr.operand.token
                        )
            else:
                self._check_expression_for_initialization(
                    expr.operand, initialized)

        elif isinstance(expr, Literal):
            # Literals don't need initialization check
            pass

    # ==================== HELPER METHODS ====================

    def _is_variable_defined(self, var_name: str) -> bool:
        """Check if variable is defined in current or parent scopes"""
        scope = self.current_scope
        while scope is not None:
            if var_name in scope.symbols:
                return True
            scope = scope.parent
        return False

    def _enter_scope_by_name(self, name: str):
        """Enter child scope by name"""
        for child in self.current_scope.children:
            if child.name == name:
                self.current_scope = child
                return
        raise Exception(f"Internal error: Scope '{name}' not found")

    def _enter_first_block_scope(self):
        """Enter the first block scope (handles multiple block children)"""
        for child in self.current_scope.children:
            if child.name == 'block':
                self.current_scope = child
                return
        # If no block scope, stay in current scope

    def _exit_scope(self):
        """Return to parent scope"""
        if self.current_scope.parent:
            self.current_scope = self.current_scope.parent
