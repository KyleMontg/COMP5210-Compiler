from dataclasses import dataclass, field
from typing import *
from src.ast_nodes import *
from src.errors import SymbolTableError

@dataclass
class Symbol:
    name: str
    data: dict[str, Any]
    scope_id: int


@dataclass
class Scope:
    id: int
    name: str
    parent: Optional['Scope']= field(default=None, repr=False)
    children: list['Scope'] = field(default_factory=list, repr=False)
    symbols: dict[str, Symbol] = field(default_factory=dict)
    labels: dict[str, Any] = field(default_factory=dict)    # goto labels

    def add(self, name, data):
        if name in self.symbols:
            raise SymbolTableError(f'Cant re-declare variable: {name}', None)
        self.symbols[name] = Symbol(name, data, self.id)

    def __repr__(self):
        s = f'\nID:       {self.id}\n'
        s += f'Name:     {self.name}\n'
        s += f'Symbols:  {self.symbols}\n'
        return s

class SymbolTable:
    def __init__(self):
        self.global_scope = Scope(0, 'global', None)
        self.head = self.global_scope
        self.current_scope = self.global_scope
        self.next_id = 1

    def __repr__(self):
        order = self.dump()
        s = ''
        for scope in order:
            s += str(scope)
        return s

    def _enter_scope(self, name):
        new_scope = Scope(self.next_id, name, self.current_scope)
        self.next_id += 1
        self.current_scope.children.append(new_scope)
        self.current_scope = new_scope

    def _exit_scope(self):
        if self.current_scope.parent is None:
            raise SymbolTableError('Can not back escape global scope', None)
        self.current_scope = self.current_scope.parent

    def _add_symbol(self, name, data):
        self.current_scope.add(name, data)

    # Loops through using dfs and returns an array or ordered scope
    def dump(self):
        visited = set()
        stack = [self.head]
        scope_order = []
        while stack:
            current_scope = stack.pop()
            if current_scope.id not in visited:
                visited.add(current_scope.id)
                scope_order.append(current_scope)
                for child in reversed(current_scope.children):
                    if child.id not in visited:
                        stack.append(child)
        return scope_order

    # Entry
    def build_symbol_table(self, program: Program):
        # loop through everything in global scope
        for unit in program.units:
            if isinstance(unit, FunctionDefinition):
                self._add_function(unit)
                self._enter_scope(unit.func_ident.value)
                self._add_param(unit.func_param)
                self._add_compound_stmt(unit.func_body)
                self._exit_scope()
            elif isinstance(unit, FunctionDeclaration):
                self._add_function(unit)
            elif isinstance(unit, DeclarationStatement):
                self._add_decl_stmt(unit, 'global')

    def _add_function(self, func):
        name = func.func_ident.value
        cur = self.current_scope
        existing = cur.symbols.get(name)
        if existing is not None:
            if existing.data.get('kind') == 'func':
                prev_type = existing.data.get('type')
                new_type = func.func_type.base.value
                if prev_type != new_type:
                    raise SymbolTableError(f"Function re-declared with different type: {name}", func.func_ident)
                existing.data['line'] = func.func_ident.line_num
                existing.data['char'] = func.func_ident.char_num
                return
            # Name exists but not as a function – real conflict
            raise SymbolTableError(f"Cant re-declare variable: {name}", func.func_ident)

        self._add_symbol(name,
                        {'kind': 'func',
                         'type': func.func_type.base.value,
                         'line': func.func_ident.line_num,
                         'char': func.func_ident.char_num})

    def _add_param(self, func_param):
        for param in func_param:
            if param.declarator is not None:
                self._add_symbol(param.declarator.value,
                                 {'kind': 'param',
                                  'type': param.decl_type.base.value,
                                  'line': param.declarator.line_num,
                                  'char': param.declarator.char_num})

    def _add_decl_stmt(self, unit, decl_type):
        for decl in unit.declarations:
            if decl:
                self._add_symbol(decl.declarator.value,
                                 {'kind': decl_type,
                                  'type': unit.decl_type.base.value,
                                  'line': decl.declarator.line_num,
                                  'char': decl.declarator.char_num})

    def _add_compound_stmt(self, block):
        self._enter_scope('block')
        for stmt in block.items:
            self._traverse_stmt(stmt)
        self._exit_scope()

    # used to find which statements need to be added to symbol table
    def _traverse_stmt(self, stmt):
        if isinstance(stmt, DeclarationStatement):
            self._add_decl_stmt(stmt, 'local')

        elif isinstance(stmt, CompoundStatement):
            self._add_compound_stmt(stmt)

        elif isinstance(stmt, IfStatement):
            self._traverse_stmt(stmt.then_branch)
            if stmt.else_branch:
                self._traverse_stmt(stmt.else_branch)

        elif isinstance(stmt, WhileStatement):
            self._traverse_stmt(stmt.body)

        elif isinstance(stmt, DoWhileStatement):
            self._traverse_stmt(stmt.body)

        elif isinstance(stmt, ForStatement):
            # enter scope before declaring conditional variables
            self._enter_scope('for_stmt')
            if isinstance(stmt.initializer, DeclarationStatement):
                self._add_decl_stmt(stmt.initializer, 'local')
            self._traverse_stmt(stmt.body)
            self._exit_scope()

        elif isinstance(stmt, SwitchStatement):
            for switch_stmt in stmt.body:
                for items in switch_stmt.items:
                    self._traverse_stmt(items)
