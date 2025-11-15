
#Instruction Types: ASSIGN, PARAM, CALL, LABEL, IF, FOR, WHILE, DECL, RETURN


"""
block ?:
    DECL    res=<identifier token>, left=<initializer token/temp>, right=None, op=None
    ASSIGN  res=<target>, left=<operand>, right=<operand or None>, op=<operator token>
    PARAM   res=Token('PARAM','param'), left=<argument value>, right=None, op=None
    CALL    res=<temp for return>, left=<callee name>, right=None, op=Token('CALL','call')
    LABEL   res=<label name string>, left=None, right=None, op=Token('LABEL','label')
    GOTO    res=<target label>, left=None, right=None, op=Token('GOTO','goto')
    IF      res=<condition temp>, left=<true label>, right=<false label>, op=Token('IFSTMT','if')
    FOR     res=<condition temp>, left=<body label>, right=<exit label>, op=Token('FORSTMT','for')
    WHILE   res=<condition temp>, left=<body label>, right=<exit label>, op=Token('WHILESTMT','while')
    RETURN  res=<value temp/literal>, left=None, right=None, op=Token('RETURN','return')
"""

from src.tac import *

def constant_fold(cfg): # type: ignore
    for node_list in cfg:
        head = node_list[0]
        if head is None:
            continue
        entry = {}
        exit = {}
        cur_block = head.block

        # for every variable in a node, look for what its defined by and what it depends on
            # if its defined in that block and a constant add to substitution list
                # substitute varable in that node with the constant
            # if constant numbers, use a fold
            # if its not but


def _traverse_block(block, known):
    # track variable assingments in block
    for instr in block.instr_list:

        if(instr.instr_type == 'DECL'):
            if(instr.left is None):
                continue
            if(instr.left.type == 'NUMBER'):
                # add constant to now known
                known[instr.res.value] = Token(instr.left.type, instr.left.value)
            elif(instr.left.type == 'IDENTIFIER'):
                # check to see if identifier has a constant
                value = known.get(instr.left.value)
                if value == 'unknown':
                    # if identifier known and not a constant
                    known[instr.res.value] = 'unknown'
                elif(value is not None):
                    # replace value with constant
                    # update known with now known constant
                    instr.left = Token(value.token_type, value.value)
                    known[instr.res.value] = Token(value.token_type, value.value)
                else:
                    known[instr.res.value] = 'unknown'

        if(instr.instr_type == 'ASSIGN'):
            if(instr.left is not None):
                # handle if no operator and single number
                if(instr.left.type == 'NUMBER' and instr.right is None):
                    # add constant to now known
                    known[instr.res.value] = Token(instr.left.type, instr.left.value)
                elif(instr.left.type == 'IDENTIFIER'):
                    # check to see if identifier has a constant
                    value = known.get(instr.left.value)
                    if value == 'unknown':
                        # if identifier known and not a constant
                        known[instr.res.value] = 'unknown'
                    elif(value is not None):
                        # replace value with constant
                        # update known with now known constant
                        instr.left = Token(value.token_type, value.value)
                    else:
                        known[instr.res.value] = 'unknown'

            if(instr.right is not None):
                if(instr.right.type == 'IDENTIFIER'):
                    value = known.get(instr.right.value)
                    if value == 'unknown':
                        # if identifier known and not a constant
                        known[instr.res.value] = 'unknown'
                    elif(value is not None):
                        # replace value with constant
                        # update known with now known constant
                        instr.right = Token(value.token_type, value.value)
                    else:
                        known[instr.res.value] = 'unknown'


        if(instr.instr_type == 'PARAM'):
            ...

        if(instr.instr_type == 'CALL'):
            pass

        if(instr.instr_type == 'LABEL'):
            pass

        if(instr.instr_type == 'IF'):
            ...

        if(instr.instr_type == 'FOR'):
            ...

        if(instr.instr_type == 'WHILE'):
            ...

        if(instr.instr_type == 'GOTO'):
            ...

        if(instr.instr_type == 'RETURN'):
            ...

    return known
























































'''


class FoldLookup:
    def __init__(self, instr: Instruction, index: int, is_used: bool, is_redefined: bool):
        self.instr = instr
        self.index = index
        self.is_used = is_used
        self.is_redefined = is_redefined
















def constant_fold(tac: TAC, cfg: list):
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
'''