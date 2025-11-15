
#Instruction Types: ASSIGN, PARAM, CALL, LABEL, IF, FOR, WHILE, DECL, RETURN, GOTO
from src.tac import *
def copy_propagation(tac: TAC, cfg: list):
    func_list = tac.functions
    for func_block in func_list:
        for blocks in func_block.blocks:
            for instr in list(blocks.instr_list):
                if(instr.instr_type == 'ASSIGN'):
                    if(not hasattr(instr.op,"type")):
                        continue
                    if(instr.op.type == "PLUS"):
                        if(can_fold(instr.left, instr.right)):
                            instr.left = Token('NUMBER', str(int(instr.left.value) + int(instr.right.value)))
                            instr.right = None
                            instr.op = None

                    elif(instr.op.type == "MINUS"):
                        if(can_fold(instr.left, instr.right)):
                            instr.left = Token('NUMBER', str(int(instr.left.value) - int(instr.right.value)))
                            instr.right = None
                            instr.op = None

                    # Add for all cases
    return tac

def can_fold(left, right):
    if(left is None):
        return False
    if(right is None):
        return False
    if(left.type != 'NUMBER'):
        return False
    if(right.type != 'NUMBER'):
        return False
    return True