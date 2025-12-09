from src.tac import *
from collections import defaultdict
from src.optimizations.cfg import *
import copy

# https://www.youtube.com/watch?v=eeXk_ec1n6g

# Do analysis of basic blocks
# find basic block in and out. 

# check for variables used.
# if variable not definied in block, add to variable in and variable out of predecessors


# Store liveness as such
# in_dict  { block : [vars]}
# out_dict { block : [vars]}
#

# for all blocks, create a dictionary mapping blocks to empty dicts
# loop through block list backwards until no changes occur:
    # explore every block once.
    # for each block, compute in and out sets
        # live out = union of live in of successors
        # live in = used U (live out - defined)
    # if any in or out set changed, continue loop


def copy_propagation(tac): # type: ignore
    cfg = build_cfg(tac)
    for node_list in cfg:
        if(len(node_list) == 0):
            continue
        queue = [node_list[0]]
        # default dict to return empty dict if node not in known_map
        live_map = defaultdict(dict)
        while queue:
            node = queue.pop(0)
            entry_known = common_keys(node.pred, known_map)
            exit_known = _scan_block(node.block, copy.deepcopy(entry_known))
            changed = known_map[node] != exit_known
            known_map[node] = exit_known
            if(changed):
                queue.extend(node.succ)
        for node in known_map:
            entry = common_keys(node.pred, known_map)
            propagate_known(node.block, entry)

def common_keys(nodes: list[CFGNode], known_map):
        if(not nodes):
            return {}
        # List of pred known dicts
        known_list = [known_map.get(i, {}) for i in nodes]
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
        if(isinstance(instr.left, Token) and instr.left.type == 'IDENTIFIER'):
            known_tok = known.get(instr.left.value)
            if known_tok is not None:
                instr.left = copy.deepcopy(known_tok)
        if(isinstance(instr.right, Token) and instr.right.type == 'IDENTIFIER'):
            known_tok = known.get(instr.right.value)
            if known_tok is not None:
                instr.right = copy.deepcopy(known_tok)

        if instr.instr_type in ('IF', 'WHILE', 'FOR', 'RETURN'):
            if(isinstance(instr.res, Token) and instr.res.type == 'IDENTIFIER'):
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
