from src.tac import TAC, Instruction
from src.tokens import Token
from src.errors import TACError


def constant_fold(tac: TAC) -> TAC:
    """Preforms constant folding on a Three Adress Code"""
    instr_list = [
        instr
        for func_block in tac.functions
        for blocks in func_block.blocks
        for instr in blocks.instr_list
    ]
    for instr in instr_list:
        fold_instr(instr)
    return tac


def fold_instr(instr: Instruction):
    """Applies Constant Folding to an individual instruction"""
    if (instr.left is None
            or instr.right is None
            or instr.instr_type not in {'ASSIGN', 'DECL'}
            or instr.op is None
            or not isinstance(instr.left, Token)
            or not isinstance(instr.right, Token)
            or instr.left.type != 'NUMBER'
            or instr.right.type != 'NUMBER'
            ):
        return
    # Does not handle different number types
    if (instr.op.type == "PLUS"):
        instr.left = Token('NUMBER', str(
            int(instr.left.value) + int(instr.right.value)))
        instr.right = None
        instr.op = None
    elif (instr.op.type == "MINUS"):
        instr.left = Token('NUMBER', str(
            int(instr.left.value) - int(instr.right.value)))
        instr.right = None
        instr.op = None
    elif (instr.op.type == "MULTIPLY"):
        instr.left = Token('NUMBER', str(
            int(int(instr.left.value) * int(instr.right.value))))
        instr.right = None
        instr.op = None
    elif (instr.op.type == "DIVIDE"):
        if (int(instr.right.value) == 0):
            raise TACError(
                f"Division by zero detected during constant folding: "
                f"{instr.left.value} / 0",
                instr.op
            )
        instr.left = Token('NUMBER', str(
            int(int(instr.left.value) / int(instr.right.value))))
        instr.right = None
        instr.op = None
    elif (instr.op.type == "MODULUS"):
        if (int(instr.right.value) == 0):
            raise TACError(
                f"Modulo by zero detected during constant folding: "
                f"{instr.left.value} % 0",
                instr.op
            )
        instr.left = Token('NUMBER', str(
            int(int(instr.left.value) % int(instr.right.value))))
        instr.right = None
        instr.op = None
    elif (instr.op.type == "LESSTHAN"):
        if (int(instr.left.value) < int(instr.right.value)):
            instr.left = Token('NUMBER', '1')
        else:
            instr.left = Token('NUMBER', '0')
        instr.right = None
        instr.op = None
    elif (instr.op.type == "GREATERTHAN"):
        if (int(instr.left.value) > int(instr.right.value)):
            instr.left = Token('NUMBER', '1')
        else:
            instr.left = Token('NUMBER', '0')
        instr.right = None
        instr.op = None
    elif (instr.op.type == 'EQUAL'):
        if (int(instr.left.value) == int(instr.right.value)):
            instr.left = Token('NUMBER', '1')
        else:
            instr.left = Token('NUMBER', '0')
        instr.right = None
        instr.op = None
