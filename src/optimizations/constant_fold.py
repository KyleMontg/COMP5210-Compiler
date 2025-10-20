
#Instruction Types: ASSIGN, PARAM, CALL, LABEL, IF, FOR, WHILE, DECL, RETURN
from src.tac import *
def constant_fold(tac: TAC):
    func_list = tac.functions
    for func_block in func_list:
        fold_lookup = {}
        for blocks in func_block.blocks:
            offset = 0
            for index, instr in enumerate(list(blocks.instr_list)): # Create a copy so iteration does skip
                blocks.instr_list[index - offset] = _attempt_fold(fold_lookup, instr)
                if(_decl_is_num(instr)):
                    fold_lookup[instr.res.value] = instr.left
                    blocks.instr_list.pop(index - offset)
                    offset += 1

    return tac
def _attempt_fold(fold_lookup: dict, instr: Instruction):

    if(instr.instr_type == 'ASSIGN'):
        # can left side be folded
        if(instr.left is None):
            pass
        elif(fold_lookup.get(instr.left.value) is not None):
            instr.left = fold_lookup[instr.left.value]
        # can right side be folded
        if(instr.right is None):
            pass
        elif(fold_lookup.get(instr.right.value) is not None):
            instr.right = fold_lookup[instr.right.value]
        # is a folded variable redefined
        if(fold_lookup.get(instr.res.value) is not None):
            del fold_lookup[instr.res.value]
        return instr
    if(instr.instr_type == 'PARAM'):
        return instr
    if(instr.instr_type == 'CALL'):
        return instr
    if(instr.instr_type == 'LABEL'):
        return instr
    if(instr.instr_type == 'IF'):
        return instr
    if(instr.instr_type == 'FOR'):
        return instr
    if(instr.instr_type == 'WHILE'):
        return instr
    if(instr.instr_type == 'DECL'):
        if(fold_lookup.get(instr.left.value) is not None):
            instr.left = fold_lookup[instr.left.value]
        if(fold_lookup.get(instr.res.value) is not None):
            del fold_lookup[instr.res.value]
        return instr
    if(instr.instr_type == 'RETURN'):
        return instr

def _decl_is_num(instr: Instruction):
    if instr.instr_type == 'DECL':
        if(instr.left.type == 'NUMBER'):
            return True
    return False

def _match_assign(instr: Instruction):
    if instr.instr_type == 'ASSIGN':
        return True
    return False

# find decl that is a number
# look for assignments and decl that use end
# stop if that variable it redefined