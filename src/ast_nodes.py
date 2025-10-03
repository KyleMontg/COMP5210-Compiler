from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass(slots=True)
class Program:
    units: List[Any] = field(default_factory=list)


# Functions


@dataclass(slots=True)
class FunctionDefinition:
    func_type: Any
    func_ident: Any
    func_param: List[Any] = field(default_factory=list)
    func_body: List[Any] = field(default_factory=list)


@dataclass(slots=True)
class FunctionDeclaration:
    func_type: Any
    func_ident: Any
    func_param: List[Any] = field(default_factory=list)


# Declarations

@dataclass(slots=True)
class DeclarationStatement:
    decl_type: Any
    declarations: List[Any] = field(default_factory=list)


@dataclass(slots=True)
class DeclarationTypes:
    specifiers: List[Any]
    base: Any


@dataclass(slots=True)
class VarDeclaration:
    declarator: Any
    initializer: Optional[Any]


@dataclass(slots=True)
class ParameterDeclaration:
    decl_type: Any
    declarator: Optional[Any]


# Statements


@dataclass(slots=True)
class CompoundStatement:
    items: List[Any] = field(default_factory=list)


@dataclass(slots=True)
class IfStatement:
    condition: Any
    then_branch: Any
    else_branch: Optional[Any]


@dataclass(slots=True)
class WhileStatement:
    condition: Any
    body: Any


@dataclass(slots=True)
class DoWhileStatement:
    body: Any
    condition: Any


@dataclass(slots=True)
class ForStatement:
    initializer: Optional[Any]
    condition: Optional[Any]
    increment: Optional[Any]
    body: Any


@dataclass(slots=True)
class SwitchStatement:
    expression: Any
    body: Any



@dataclass(slots=True)
class SwitchSection:
    labels: List[Any] = field(default_factory=list)
    items: List[Any] = field(default_factory=list)


@dataclass(slots=True)
class CaseLabel:
    token: Any
    expression: Any


@dataclass(slots=True)
class DefaultLabel:
    token: Any


@dataclass(slots=True)
class ReturnStatement:
    expression: Optional[Any]


@dataclass(slots=True)
class GotoStatement:
    identifier: Any


@dataclass(slots=True)
class BreakStatement:
    pass


@dataclass(slots=True)
class ContinueStatement:
    pass


@dataclass(slots=True)
class LabelStatement:
    identifier: Any
    statement: Any


@dataclass(slots=True)
class ExpressionStatement:
    expression: Optional[Any]


# Expressions


@dataclass(slots=True)
class AssignmentExpression:
    operator: Any
    left: Any
    right: Any


@dataclass(slots=True)
class BinaryExpression:
    operator: Any
    left: Any
    right: Any


@dataclass(slots=True)
class PrefixExpression:
    prefix: Any
    operand: Any


@dataclass(slots=True)
class CallExpression:
    callee: Any
    arguments: List[Any] = field(default_factory=list)


@dataclass(slots=True)
class MemberExpression:
    object: Any
    property: Any



@dataclass(slots=True)
class PostfixExpression:
    postfix: Any
    operand: Any


@dataclass(slots=True)
class Identifier:
    token: Any


@dataclass(slots=True)
class Literal:
    token: Any

