from src.optimizations.cfg import build_cfg
from src.tokens import Token
from src.tac import TAC, BasicBlock

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

def dead_code_elimination(tac: TAC):
    cfg = build_cfg(tac)
    for node_list in cfg:
        if(len(node_list) == 0):
            continue
        
        queue = [node_list[0]]
        visited = set()
        var_tracker = {}
        # key: variable name (str)
        # value: 0: declared not used, 1: used
        label_redirects = {}
        # key: label name
        # value: list(redirect_label: str / None)
        
        # loop through cfg nodes to mark used variables
        # eliminate dead code based on var_tracker
        while queue:
            node = queue.pop(0)
            visited.add(node)
            for succ in node.succ:
                if succ not in visited and succ not in queue:
                    queue.append(succ)
            get_variables(node.block, var_tracker, label_redirects)
        
        # remove unused nodes
        remove_unused(tac, var_tracker, label_redirects)
        # remove unreached blocks
        cfg = build_cfg(tac)
        for node_list in cfg:
            unreachable_blocks = set(node_list)
            if(len(node_list) == 0):
                continue
            queue = [node_list[0]]
            visited = set()
            while queue:
                node = queue.pop(0)
                visited.add(node)
                unreachable_blocks.discard(node)
                for succ in node.succ:
                    if succ not in visited and succ not in queue:
                        queue.append(succ)
            for block in unreachable_blocks:
                tac.functions[0].blocks.remove(block.block)
    return tac


def get_variables(block: BasicBlock, var_tracker: dict, label_redirects: dict):
    # prechek if label followed by goto
    goto_redirect(block, label_redirects)
    for instr in block.instr_list:
        if(instr.instr_type in ('DECL', 'ASSIGN')):
            # Get result and mark as declared
            res = var_tracker.get(instr.res.value)
            if(res is None):
                var_tracker[instr.res.value] = 0
            # If left is identifier, mark as used
            if(is_ident(instr.left)):
                left_val = var_tracker.get(instr.left.value)
                if(left_val is not None):
                    var_tracker[instr.left.value] = 1
            # If right is identifier, mark as used
            if(is_ident(instr)):
                right_val = var_tracker.get(instr.right.value)
                if(right_val is not None):
                    var_tracker[instr.right.value] = 1
            
        if(instr.instr_type == "IF"):
            # is the condition constant?
            if(instr.res.type == "NUMBER"):
                # remove if and replace with goto
                if(instr.res.value != '0'):
                    # true, goto left
                    instr.instr_type = "GOTO"
                    instr.res = instr.left
                    instr.left = None
                    instr.right = None
                    instr.op = Token('GOTO','goto')
                else:
                    # false, goto right
                    instr.instr_type = "GOTO"
                    instr.res = instr.right
                    instr.left = None
                    instr.right = None
                    instr.op = Token('GOTO','goto')
                    
        if(instr.instr_type in ('IF', 'FOR', 'WHILE')):
            # If condition is identifier, mark identifier as used
            if(is_ident(instr.res)):
                cond_val = var_tracker.get(instr.res.value)
                if(cond_val is not None):
                    var_tracker[instr.res.value] = 1
                    
        if(instr.instr_type == 'RETURN'):
            # If return value is identifier, mark identifier as used
            if(is_ident(instr.res)):
                ret_val = var_tracker.get(instr.res.value)
                if(ret_val is not None):
                    var_tracker[instr.res.value] = 1
                
    return var_tracker, label_redirects
    
def is_ident(instr: Token | str | None):
    if(instr is None):
        return False
    return isinstance(instr, Token) and instr.type == 'IDENTIFIER'

def goto_redirect(block, label_redirects: dict):
    '''
    check if a label is immediately followed by a goto
    if so, mark all instances of the label to the goto target
    '''
    instr_list = block.instr_list
    if(len(instr_list) != 2):
        return
    if(instr_list[0].instr_type == "LABEL" and instr_list[1].instr_type == "GOTO"):
        label_name = instr_list[0].res
        goto_target = instr_list[1].res
        label_redirects[label_name] = goto_target
    
    
def remove_unused(tac, var_tracker: dict, label_redirects: dict):
    for func in tac.functions:
        for block in func.blocks:
            goto_seen = False
            for instr in block.instr_list:
                if(goto_seen):
                    # after goto, remove all instructions
                    block.instr_list.remove(instr)
                    continue
                # remove unused decl/assign
                if(instr.instr_type in ('DECL', 'ASSIGN')):
                    res = var_tracker.get(instr.res.value)
                    if(res == 0):
                        block.instr_list.remove(instr)
                # update goto targets
                if(instr.instr_type == 'GOTO'):
                    goto_seen = True
                    label_name = instr.res
                    redirect = label_redirects.get(label_name)
                    if(redirect):
                        instr.res = redirect
                
                if(instr.instr_type == 'IF'):
                    # update true label
                    label_name_left = instr.left
                    redirect_left = label_redirects.get(label_name_left)
                    if(redirect_left):
                        instr.left = redirect_left
                    # update false label
                    label_name_right = instr.right
                    redirect_right = label_redirects.get(label_name_right)
                    if(redirect_right):
                        instr.right = redirect_right