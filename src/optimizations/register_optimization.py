from src.tac import *
from collections import defaultdict
from src.optimizations.cfg import *
import copy

# https://www.youtube.com/watch?v=eeXk_ec1n6g

def register_opimization(tac: TAC) -> list[tuple[list[CFGNode], dict[CFGNode, list[set[str]]]]]:
    cfg = build_cfg(tac)
    func_liveness = []
    for node_list in cfg:
        if(len(node_list) == 0):
            continue
        rev_node_list = copy.copy(node_list)
        rev_node_list.reverse()
        node_map_prev: dict[CFGNode, list[set[str]]] = dict()
        node_map: dict[CFGNode, list[set[str]]] = dict()
        while True:
            for node in rev_node_list:
                defined, used = track_variables(node.block)
                succ_list = node.succ
                out_set: set[str] = set()
                for succ in succ_list:
                    succ_out = node_map.get(succ)
                    if succ_out:
                        out_set = out_set.union(succ_out[0])
                in_set: set[str] = used.union(out_set - defined)
                node_map[node] = [in_set, out_set]
            if(node_map == node_map_prev):
                break
            node_map_prev = copy.copy(node_map)
        func_liveness.append((node_list, node_map))
    return func_liveness

def track_variables(block: BasicBlock) -> tuple[set[str], set[str]]:
    defined: set[str] = set()
    used: set[str] = set()
    for instr in block.instr_list:
        if(instr.instr_type in ('DECL', 'ASSIGN')):
            if(not_in_dic(instr.left, defined)):
                used.add(instr.left.value)  # type: ignore
            if(not_in_dic(instr.right, defined)):
                used.add(instr.right.value) # type: ignore
            defined.add(instr.res.value) # type: ignore

        if(instr.instr_type == 'RETURN'):
            if(not_in_dic(instr.res, defined)):
                used.add(instr.res.value) # type: ignore
    return defined, used

def not_in_dic(instr: Token | str | None,
               defined: set[str]
               ) -> bool:
    if(instr is None):
        return False
    if(not isinstance(instr, Token)):
        return False
    if(instr.type != 'IDENTIFIER'):
        return False
    if(not hasattr(instr, 'value')):
        return False
    if(instr.value in defined):
        return False
    return True