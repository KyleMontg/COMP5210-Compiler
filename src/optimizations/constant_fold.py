
#Instruction Types: ASSIGN, PARAM, CALL, LABEL, IF, FOR, WHILE, DECL, RETURN


"""
To Fix code i need to track if a change is made and if made then remove origonal instruction after block execution
"""
from src.tac import *

class FoldLookup:
    def __init__(self, instr: Instruction, index: int, is_used: bool, is_redefined: bool):
        self.instr = instr
        self.index = index
        self.is_used = is_used
        self.is_redefined = is_redefined

def constant_fold(tac: TAC):
    func_list = tac.functions
    for func_block in func_list:
        for blocks in func_block.blocks:
            # Dictionary to track instruction lookups
            fold_lookup = {}
            for index, instr in enumerate(list(blocks.instr_list)): # Create a copy so iteration does skip

                blocks.instr_list[index] = _attempt_fold(fold_lookup, instr)

                if(_decl_is_num(instr) or _assign_is_num(instr)):
                    # Adds instruction, index of instruciton in block, and a bool to track if used
                    fold_lookup[instr.res.value] = FoldLookup(instr.left, index, False, False)
                    # Remove instruction from the block

            offset = 0
            for item in fold_lookup.items():
                fold_instr = item[1]
                # Offset used to keep correct index when removing instructions
                if fold_instr.is_used:
                    blocks.instr_list.pop(fold_instr.index - offset)
                    offset += 1
    return tac

def _attempt_fold(fold_lookup: dict, instr: Instruction):

    if(instr.instr_type == 'ASSIGN'):
        # can left side be folded
        if(instr.left is None):
            pass

        elif(fold_lookup.get(instr.left.value) is not None):
            fold_instr = fold_lookup[instr.left.value]
            if(not fold_instr.is_redefined):
                instr.left = fold_instr.instr
                fold_instr.is_used = True

        # can right side be folded
        if(instr.right is None):
            pass

        elif(fold_lookup.get(instr.right.value) is not None):
            fold_instr = fold_lookup[instr.right.value]
            if(not fold_instr.is_redefined):
                instr.right = fold_instr.instr
                fold_instr.is_used = True

        # is a folded variable redefined
        if(fold_lookup.get(instr.res.value) is not None):
            fold_instr = fold_lookup[instr.res.value]
            fold_instr.is_redefined = True

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

    if(instr.instr_type == 'GOTO'):
        return instr

    if(instr.instr_type == 'DECL'):

        if(fold_lookup.get(instr.left.value) is not None):
            fold_instr = fold_lookup[instr.left.value]
            if(not fold_instr.is_redefined):
                instr.left = fold_instr.instr
                fold_instr.is_used = True

        if(fold_lookup.get(instr.res.value) is not None):
            fold_instr = fold_lookup[instr.res.value]
            fold_instr.is_redefined = True

        return instr

    if(instr.instr_type == 'RETURN'):

        if(fold_lookup.get(instr.res.value) is not None):
            fold_instr = fold_lookup[instr.res.value]
            if(not fold_instr.is_redefined):
                instr.res = fold_instr.instr
                fold_instr.is_used = True

        return instr

def _decl_is_num(instr: Instruction):
    if instr.instr_type == 'DECL':
        if(instr.left.type == 'NUMBER'):
            return True
    return False

def _assign_is_num(instr: Instruction):
    if instr.instr_type == 'ASSIGN':
        if(instr.left.type == 'NUMBER' and instr.right is None):
            return True
    return False

# find decl that is a number
# look for assignments and decl that use end
# stop if that variable it redefined