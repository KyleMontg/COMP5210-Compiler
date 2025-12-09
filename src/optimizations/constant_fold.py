#Instruction Types: ASSIGN, PARAM, CALL, LABEL, IF, FOR, WHILE, DECL, RETURN, GOTO
from src.tac import *
def constant_fold(tac: TAC):
    func_list = tac.functions
    for func_block in func_list:
        for blocks in func_block.blocks:
                for instr in list(blocks.instr_list):
                    fold_instr(instr)
    return tac

def fold_instr(instr):
    if(instr.left is None or instr.right is None):
        return
    if(instr.instr_type not in {'ASSIGN', 'DECL'}):
        return
    if(instr.op is None):
        return
    if(instr.left.type != 'NUMBER' or instr.right.type != 'NUMBER'):
        return
    # Does not handle different number types
    if(instr.op.type == "PLUS"):
            instr.left = Token('NUMBER', str(int(instr.left.value) + int(instr.right.value)))
            instr.right = None
            instr.op = None
    elif(instr.op.type == "MINUS"):
            instr.left = Token('NUMBER', str(int(instr.left.value) - int(instr.right.value)))
            instr.right = None
            instr.op = None
    elif(instr.op.type == "MULTIPLY"):
            instr.left = Token('NUMBER', str(int(int(instr.left.value) * int(instr.right.value))))
            instr.right = None
            instr.op = None
    elif(instr.op.type == "DIVIDE"):
            if(int(instr.right.value) == 0):
                ...
                #TODO Raise zero division error
            instr.left = Token('NUMBER', str(int(int(instr.left.value) / int(instr.right.value))))
            instr.right = None
            instr.op = None
    elif(instr.op.type == "MODULUS"):
            if(int(instr.right.value) == 0):
                ...
                #TODO Raise zero division error
            instr.left = Token('NUMBER', str(int(int(instr.left.value) % int(instr.right.value))))
            instr.right = None
            instr.op = None
    elif(instr.op.type == "LESSTHAN"):
        if(int(instr.left.value) < int(instr.right.value)):
            instr.left = Token('NUMBER', '1')
        else:
            instr.left = Token('NUMBER', '0')
        instr.right = None
        instr.op = None
        
    elif(instr.op.type == "GREATERTHAN"):
        if(int(instr.left.value) > int(instr.right.value)):
            instr.left = Token('NUMBER', '1')
        else:
            instr.left = Token('NUMBER', '0')
        instr.right = None
        instr.op = None

