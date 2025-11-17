

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
from collections import defaultdict
from src.optimizations.cfg import *
import copy


def copy_propagation(tac): # type: ignore
    cfg = build_cfg(tac)
    for node_list in cfg:
        if(len(node_list) == 0):
            continue
        queue = [node_list[0]]
        known_map = defaultdict(dict)
        while queue:
            node = queue.pop(0)
            entry_known = common_keys(node.pred, known_map)
            exit_known = _scan_block(node.block, copy.deepcopy(entry_known))
            changed = known_map[node] != exit_known
            known_map[node] = exit_known
            if(changed):
                queue.extend(node.succ)
        for node in known_map.keys():
            entry = common_keys(node.pred, known_map)
            propagate_known(node.block, entry)

def common_keys(nodes: list[CFGNode], known_map):
        if(not nodes):
            return {}
        # List of pred known dicts
        known_list = [known_map[i] for i in nodes]
        # List for all agreed var values from pred on entry
        merged = copy.deepcopy(known_list[0])
        for dict_item in known_list[1:]:
            for key in list(merged.keys()):
                if key not in dict_item or merged[key] != dict_item[key]:
                    del merged[key]

        return merged

def _scan_block(block, entry):
    known = copy.copy(entry)
    for instr in block.instr_list:
        if(instr.instr_type in ('DECL', 'ASSIGN')):
            known.pop(instr.res.value, None)
            if(instr.left is None):
                continue
            if(instr.right is None and instr.left.type == 'NUMBER'):
                known[instr.res.value] = instr.left
            elif(instr.right is None and instr.left.type == 'IDENTIFIER'):
                if(instr.res.value == instr.left.value):
                    continue
                known[instr.res.value] = known.get(instr.left.value, instr.left)
    return known

def propagate_known(block, entry):
    known = dict(entry)
    for instr in block.instr_list:

        if(isinstance(instr.left, Token)):
            if instr.left is not None and instr.left.type == 'IDENTIFIER':
                known_tok = known.get(instr.left.value)
                if known_tok is not None:
                    instr.left = copy.deepcopy(known_tok)
        if(isinstance(instr.right, Token)):
            if instr.right is not None and instr.right.type == 'IDENTIFIER':
                known_tok = known.get(instr.right.value)
                if known_tok is not None:
                    instr.right = copy.deepcopy(known_tok)

        if instr.instr_type in ('IF', 'WHILE', 'RETURN') and instr.res is not None and getattr(instr.res, 'type', None) == 'IDENTIFIER':
            known_tok = known.get(instr.res.value)
            if known_tok is not None:
                instr.res = copy.deepcopy(known_tok)

        if instr.instr_type in ('DECL', 'ASSIGN'):
            res_name = instr.res.value
            known.pop(res_name, None)
            if instr.left is None:
                continue
            if instr.op is None and instr.right is None:
                if instr.left.type == 'NUMBER':
                    known[res_name] = instr.left
                elif instr.left.type == 'IDENTIFIER' and instr.left.value != res_name:
                    known[res_name] = known.get(instr.left.value, instr.left)
