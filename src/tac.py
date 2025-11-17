from src.ast_nodes import *
from src.tokens import *
from src.errors import *

'''
Instruction has general format of:
    res = left op right
For loop statements, labels, and gotos Instruction is used differently
'''
#Instruction Types: ASSIGN, PARAM, CALL, LABEL, IF, FOR, WHILE, RETURN, DECL
class Instruction:
    def __init__(self, instr_type: str, res, left, right = None, op = None):
        # Formated such that res = left op right
        self.op = op
        self.left = left
        self.right = right
        self.res = res
        self.instr_type = instr_type


# Control flow blocks
class BasicBlock:
    def __init__(self):
        self.instr_list = []


class FunctionBlock:
    def __init__(self, name: str, blocks: list, symbol_table):
        self.name = name
        self.blocks = blocks
        self.symbol_table = symbol_table


class TAC:
    def __init__(self):
        self.symbol_table = None
        self.temp_var_count = 0
        self.label_count = 0
        self.functions = []
        self.cur_func = None
        self.cur_block = None
        # Control-flow stack to track break/continue
        self.ctrl_stack = []
        self.globals = []

    def _push_to_block(self, instr: Instruction):
        # if global
        if(self.cur_func == None):

            self.globals.append(instr)
        else:
        # If theres a label create a new instruction block
            if(isinstance(instr.op, Token) and instr.op.type == 'LABEL'):
                new_block = BasicBlock()
                self.cur_func.blocks.append(new_block)
                self.cur_block = new_block
            self.cur_block.instr_list.append(instr)  # type: ignore

    def _get_temp_var(self):
        temp_name = f'%t{self.temp_var_count}'
        self.temp_var_count += 1
        tok = Token(IDENTIFIER, temp_name)
        return tok

    def _get_label(self):
        label_name = f"%L{self.label_count}"
        self.label_count += 1
        return label_name

    def _push_ctrl(self, break_label: str, continue_label = None):
        if(continue_label is not None):
            self.ctrl_stack.append({'break': break_label, 'continue': continue_label})
        else:
            self.ctrl_stack.append({'break': break_label})

    def _pop_ctrl(self):
        if self.ctrl_stack:
            self.ctrl_stack.pop()

    def _current_break(self):
        if self.ctrl_stack is None or 'break' not in self.ctrl_stack[-1]:
            raise TACError('break used invalid', None)
        return self.ctrl_stack[-1]['break']

    def _current_continue(self):
        if self.ctrl_stack is None or 'continue' not in self.ctrl_stack[-1]:
            raise TACError('continue used invalid', None)
        return self.ctrl_stack[-1]['continue']

    # -----
    # Entry
    # -----

    def generate_tac(self, head: Program, symbol_table):
        self.symbol_table = symbol_table
        self._program(head)
        return self.functions

    def _program(self, program: Program):
        for unit in program.units:
            if(isinstance(unit, FunctionDefinition)):
                self._func_def(unit)
            elif(isinstance(unit, DeclarationStatement)):
                self._decl_stmt(unit)
            else:
                raise TACError('Invalid Program Structure', unit)

    def _func_def(self, func_def: FunctionDefinition):
        # Setup blocks and function blocks
        func_name = func_def.func_ident
        func = FunctionBlock(func_name, [], self.symbol_table)
        self.functions.append(func)
        entry = BasicBlock()
        func.blocks.append(entry)
        self.cur_block = entry
        self.cur_func = func
        # Data class takes func_body as Any list but any object in that list hast attribute .items
        stmt_list = func_def.func_body.items # type: ignore
        for stmt in stmt_list:
            if(isinstance(stmt, DeclarationStatement)):
                self._decl_stmt(stmt)
            elif(isinstance(stmt, ExpressionStatement)):
                self._expr_stmt(stmt)
            elif(isinstance(stmt, BreakStatement)):
                self._break_stmt()
            elif(isinstance(stmt, ContinueStatement)):
                self._continue_stmt()
            elif(isinstance(stmt, ReturnStatement)):
                self._return_stmt(stmt)
            elif(isinstance(stmt, LabelStatement)):
                self._label_stmt(stmt.identifier.value)
            elif(isinstance(stmt, GotoStatement)):
                self._goto_stmt(stmt.identifier.value)
            elif(isinstance(stmt, SwitchStatement)):
                self._switch_stmt(stmt)
            elif(isinstance(stmt, ForStatement)):
                self._for_stmt(stmt)
            elif(isinstance(stmt, WhileStatement)):
                self._while_stmt(stmt)
            elif(isinstance(stmt, DoWhileStatement)):
                self._do_while_stmt(stmt)
            elif(isinstance(stmt, IfStatement)):
                self._if_stmt(stmt)
            else:
                raise TACError('Invalid Function Defenition Structure', stmt)

    def _decl_stmt(self, decl: DeclarationStatement):
        for decl_obj in decl.declarations:
            if(isinstance(decl_obj, VarDeclaration)):
                if(decl_obj.initializer is None):
                    break
                self._var_decl(decl_obj)
            else:
                raise TACError('Invalid Declaration Statement Structure', decl_obj)

    def _expr_stmt(self, expr_stmt: ExpressionStatement):
        expr =  expr_stmt.expression
        if expr is None:
            return
        if(isinstance(expr, AssignmentExpression)):
            self._assign_expr(expr)
        else:
            self._get_expression(expr)


    def _assign_expr(self, expr: AssignmentExpression):
        operator = expr.operator # has to be a token
        left = expr.left.token # has to be an identifier
        right = self._get_expression(expr.right)
        # For operator assigns, do operation with temp var, then assign
        if(operator.type == 'ASSIGN'):
            self._push_to_block(Instruction('ASSIGN', left, right))
        elif(operator.type == 'PLUSASSIGN'):
            temp_add = self._get_temp_var()
            self._push_to_block(Instruction('ASSIGN', temp_add, left, right, Token('PLUS', '+')))
            self._push_to_block(Instruction('ASSIGN', left, temp_add))
        elif(operator.type == 'MINUSASSIGN'):
            temp_add = self._get_temp_var()
            self._push_to_block(Instruction('ASSIGN', temp_add, left, right, Token('MINUS', '-')))
            self._push_to_block(Instruction('ASSIGN', left, temp_add))
        elif(operator.type == 'MULTASSIGN'):
            temp_add = self._get_temp_var()
            self._push_to_block(Instruction('ASSIGN', temp_add, left, right, Token('MULTIPLY', '*')))
            self._push_to_block(Instruction('ASSIGN', left, temp_add))
        elif(operator.type == 'DIVASSIGN'):
            temp_add = self._get_temp_var()
            self._push_to_block(Instruction('ASSIGN', temp_add, left, right, Token('DIVIDE', '/')))
            self._push_to_block(Instruction('ASSIGN', left, temp_add))
        elif(operator.type == 'MODASSIGN'):
            temp_add = self._get_temp_var()
            self._push_to_block(Instruction('ASSIGN', temp_add, left, right, Token('MODULUS', '%')))
            self._push_to_block(Instruction('ASSIGN', left, temp_add))
        elif(operator.type == 'ANDASSIGN'):
            temp_add = self._get_temp_var()
            self._push_to_block(Instruction('ASSIGN', temp_add, left, right, Token('BITAND', '&')))
            self._push_to_block(Instruction('ASSIGN', left, temp_add))
        elif(operator.type == 'ORASSIGN'):
            temp_add = self._get_temp_var()
            self._push_to_block(Instruction('ASSIGN', temp_add, left, right, Token('BITOR', '|')))
            self._push_to_block(Instruction('ASSIGN', left, temp_add))
        elif(operator.type == 'XORASSIGN'):
            temp_add = self._get_temp_var()
            self._push_to_block(Instruction('ASSIGN', temp_add, left, right, Token('BITXOR', '^')))
            self._push_to_block(Instruction('ASSIGN', left, temp_add))
        elif(operator.type == 'LSHIFTASSIGN'):
            temp_add = self._get_temp_var()
            self._push_to_block(Instruction('ASSIGN', temp_add, left, right, Token('LEFTSHIFT', '<<')))
            self._push_to_block(Instruction('ASSIGN', left, temp_add))
        elif(operator.type == 'RSHIFTASSIGN'):
            temp_add = self._get_temp_var()
            self._push_to_block(Instruction('ASSIGN', temp_add, left, right, Token('RIGHTSHIFT', '>>')))
            self._push_to_block(Instruction('ASSIGN', left, temp_add))
        else:
            raise TACError("Invlaid Assignment", operator)

    def _bi_expr(self, bi_expr: BinaryExpression):
        # Creates a temparary variable for left and right of expression and returns it
        op = bi_expr.operator
        left = self._get_expression(bi_expr.left)
        right = self._get_expression(bi_expr.right)
        temp_store = self._get_temp_var()
        self._push_to_block(Instruction('ASSIGN', temp_store, left, right, op))
        return temp_store

    def _post_expr(self, post_expr: PostfixExpression):
        # set temp_var = identifier then preform postfix
        # returns the temp_var
        operand = post_expr.operand
        postfix = post_expr.postfix
        ident = None
        pre_incement = self._get_temp_var()
        if(isinstance(postfix, Identifier)):
            ident = self._identifier(postfix)
        else:
            raise TACError('Invalid Postfix Structure', postfix)
        if(operand.type == 'INCREMENT' or operand.type == 'DECREMENT'):
            self._push_to_block(Instruction('ASSIGN', ident, ident, Token(NUMBER, '1'), operand ))
        else:
            raise TACError('Invalid Postfix Structure', operand.type)
        return pre_incement

    def _pre_expr(self, pre_expr: PrefixExpression):
        # sets
        operand = pre_expr.operand
        prefix = pre_expr.prefix
        ident = None
        if(isinstance(operand, Identifier)):
            ident = self._identifier(operand)
        else:
            raise TACError('Invalid Prefix Structure', operand)

        if(prefix.type == 'INCREMENT' or prefix.type == 'DECREMENT'):
            self._push_to_block(Instruction('ASSIGN', ident, ident, Token(NUMBER, '1'), prefix ))
        elif(prefix.type == 'BITNOT'):
            self._push_to_block(Instruction('ASSIGN', ident, None, Token('BITNOT', '~'), prefix ))
        elif(prefix.type == 'LOGNOT'):
            self._push_to_block(Instruction('ASSIGN', ident, None, Token('LOGNOT', '!'), prefix ))
        elif(prefix.type == 'PLUS' or prefix.type == 'MINUS'):
            #Unary plus and Unary minus do not need an instruction block
            pass
        else:
            raise TACError('Invalid Prefix Structure', prefix.type)
        return ident

    def _function_call(self, call: CallExpression):
        for arg in call.arguments:
            param = Token('PARAM', 'param')
            expr = self._get_expression(arg)
            self._push_to_block(Instruction('PARAM', param, expr))
        temp_var = self._get_temp_var()
        tok_name = call.callee.token.value  # name of funciton
        # when CALL token is found the arguments are used as follows:
        # 1. where call is assigned to after call is made
        # 2. name of function
        # 3. N/A
        # 4. Token type Call
        self._push_to_block(Instruction('CALL', temp_var, tok_name, None, Token('CALL', 'call')))
        return temp_var

    def _switch_stmt(self, stmt: SwitchStatement):
        label_tok = Token('LABEL', 'label')
        case_tok = Token('CASE', 'case')
        label_end = Instruction('LABEL', self._get_label(), None, None, label_tok)
        self._push_ctrl(label_end.res)
        for cases in stmt.body:
            # Creates a an if statement with control flow for true and false
            case_cond = self._get_expression(cases.labels[0].expression)
            label_true = Instruction('LABEL', self._get_label(), None, None, label_tok)
            label_false = Instruction('LABEL', self._get_label(), None, None, label_tok)
            self._push_to_block(Instruction('IF', case_cond, label_true.res, label_false.res, Token('IFSTMT', 'if')))
            self._push_to_block(label_true)
            self._loop_stmts(case_tok, cases)
            self._push_to_block(label_false)
        self._push_to_block(label_end)
        self._pop_ctrl()

    def _for_stmt(self, stmt: ForStatement):
        label_tok = Token('LABEL', 'label')
        for_tok = Token('FORSTMT', 'for')
        label_start = Instruction('LABEL', self._get_label(), None, None, label_tok)
        label_stmts = Instruction('LABEL', self._get_label(), None, None, label_tok)
        label_incr = Instruction('LABEL', self._get_label(), None, None, label_tok)
        label_end = Instruction('LABEL', self._get_label(), None, None, label_tok)

        # initializer
        if stmt.initializer is not None:
            self._decl_stmt(stmt.initializer) # type: ignore
        self._push_to_block(label_start)
        condition = self._get_expression(stmt.condition)
        # check condition
        self._push_to_block(Instruction('FOR', condition, label_stmts.res, label_end.res, for_tok))
        # for loop body
        self._push_to_block(label_stmts)
        self._push_ctrl(label_end.res, label_incr.res)
        self._loop_stmts(for_tok, stmt.body)
        self._pop_ctrl()
        # increment
        self._push_to_block(label_incr)
        if stmt.increment is not None:
            self._get_expression(stmt.increment)
        # goto start
        self._goto_stmt(label_start.res)
        self._push_to_block(label_end)

    def _while_stmt(self, stmt: WhileStatement):
        label_tok =  Token('LABEL', 'label')
        while_tok = Token('WHILESTMT', 'while')
        label_start = Instruction('LABEL', self._get_label(), None, None, label_tok)
        label_stmts = Instruction('LABEL', self._get_label(), None, None, label_tok)
        label_end = Instruction('LABEL', self._get_label(), None, None, label_tok)
        self._push_to_block(label_start)
        condition = self._get_expression(stmt.condition)
        # check condition
        # while instructions are formatted:
        # 1. condition
        # 2. if true goto
        # 3. if false goto
        # 4. while tok
        self._push_to_block(Instruction('WHILE', condition, label_stmts.res, label_end.res, while_tok))
        # while body
        self._push_to_block(label_stmts)
        self._push_ctrl(label_end.res, label_start.res)
        self._loop_stmts(while_tok, stmt.body)
        self._pop_ctrl()
        # goto start
        self._goto_stmt(label_start.res)
        self._push_to_block(label_end)

    def _do_while_stmt(self, stmt: DoWhileStatement):
        label_tok = Token('LABEL', 'label')
        while_tok = Token('WHILESTMT', 'while')
        label_start = Instruction('LABEL', self._get_label(), None, None, label_tok)
        label_end = Instruction('LABEL', self._get_label(), None, None, label_tok)
        # while body
        self._push_to_block(label_start)
        self._push_ctrl(label_end.res)
        self._loop_stmts(while_tok, stmt.body)
        self._pop_ctrl()
        # check condition
        condition = self._get_expression(stmt.condition)
        # while instructions are formatted:
        # 1. condition
        # 2. if true goto
        # 3. if false goto
        # 4. while tok
        self._push_to_block(Instruction('WHILE', condition, label_start.res, label_end.res, Token('WHILESTMT', 'while')))
        self._push_to_block(label_end)

    def _if_stmt(self, stmt: IfStatement):
        if_tok = Token('IFSTMT', 'if')
        label_tok = Token('LABEL', 'label')
        # check condition
        condition = self._get_expression(stmt.condition)
        label_true = Instruction('LABEL', self._get_label(), None, None, label_tok)
        label_false = Instruction('LABEL', self._get_label(), None, None, label_tok)
        label_end = Instruction('LABEL', self._get_label(), None, None, label_tok)
        # if instructions are formatted:
        # 1. condition
        # 2. if true goto
        # 3. if false goto
        # 4. if tok
        self._push_to_block(Instruction('IF',condition, label_true.res, label_false.res, if_tok))
        # if true
        self._push_to_block(label_true)
        self._loop_stmts(if_tok, stmt.then_branch)
        self._goto_stmt(label_end.res)
        # if false
        self._push_to_block(label_false)
        if(stmt.else_branch is not None):
            self._loop_stmts(if_tok, stmt.else_branch)
        self._goto_stmt(label_end.res)
        self._push_to_block(label_end)

    def _loop_stmts(self, tok, stmts):
        stmt_list = stmts.items
        for stmt in stmt_list:
            if(isinstance(stmt, DeclarationStatement)):
                self._decl_stmt(stmt)
            elif(isinstance(stmt, ExpressionStatement)):
                self._expr_stmt(stmt)
            elif(isinstance(stmt, BreakStatement)):
                self._break_stmt()
            elif(isinstance(stmt, ContinueStatement)):
                self._continue_stmt()
            elif(isinstance(stmt, ReturnStatement)):
                self._return_stmt(stmt)
            elif(isinstance(stmt, LabelStatement)):
                self._label_stmt(stmt.identifier.value)
            elif(isinstance(stmt, GotoStatement)):
                self._goto_stmt(stmt.identifier.value)
            elif(isinstance(stmt, SwitchStatement)):
                self._switch_stmt(stmt)
            elif(isinstance(stmt, ForStatement)):
                self._for_stmt(stmt)
            elif(isinstance(stmt, WhileStatement)):
                self._while_stmt(stmt)
            elif(isinstance(stmt, DoWhileStatement)):
                self._do_while_stmt(stmt)
            elif(isinstance(stmt, IfStatement)):
                self._if_stmt(stmt)
            else:
                raise TACError('Invalid Function Defenition Structure', stmt)

    def _get_expression(self, expr):
        result = None
        if(isinstance(expr, Literal)):
            result = self._literal(expr)
        elif(isinstance(expr, Identifier)):
            result = self._identifier(expr)
        elif(isinstance(expr, BinaryExpression)):
            result = self._bi_expr(expr)
        elif(isinstance(expr, PrefixExpression)):
            result = self._pre_expr(expr)
        elif(isinstance(expr, PostfixExpression)):
            result = self._post_expr(expr)
        elif(isinstance(expr, CallExpression)):
            result = self._function_call(expr)
        elif(isinstance(expr, MemberExpression)):
            raise NotImplementedError
        elif(isinstance(expr, Token)):
            result = expr
        else:
            raise TACError('Invalid Statement Structure', expr)
        return result

    def _var_decl(self, decl_obj: VarDeclaration):
        expr_obj = decl_obj.initializer
        var_ident = decl_obj.declarator
        value = self._get_expression(expr_obj)
        self._push_to_block(Instruction('DECL', var_ident, value))

    def _return_stmt(self, stmt: ReturnStatement):
        value = self._get_expression(stmt.expression)
        self._push_to_block(Instruction('RETURN' ,value, None, None, Token('RETURN', 'return')))
        self._push_to_block(Instruction('LABEL', self._get_label(), None, None, Token('LABEL', 'label')))

    def _label_stmt(self, name = None):
        if name is None:
            name = self._get_label()
        self._push_to_block(Instruction('LABEL', name, None, None, Token('LABEL', 'label')))

    def _goto_stmt(self, name: Instruction):
        self._push_to_block(Instruction('GOTO', name, None, None, Token('GOTO', 'goto')))

    def _break_stmt(self):
        target = self._current_break()
        self._goto_stmt(target)

    def _continue_stmt(self):
        target = self._current_continue()
        self._goto_stmt(target)

    def _literal(self, lit: Literal):
        return lit.token

    def _identifier(self, ident: Identifier):
        return ident.token