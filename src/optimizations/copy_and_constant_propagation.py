from src.tokens import Token
from src.tac import TAC, BasicBlock
from src.optimizations.cfg import CFGNode, build_cfg
import copy


def copy_and_constant_propagation(tac: TAC) -> None:
    """Preforms copy and constant propigation on a TAC"""
    cfg = build_cfg(tac)
    for node_list in cfg:
        if (len(node_list) == 0):
            continue
        queue: list[CFGNode] = [node_list[0]]
        # default dict to return empty dict if node not in known_map
        known_map: dict[CFGNode, dict[str, Token]] = dict()
        while queue:
            node = queue.pop(0)
            entry_known = common_keys(node.pred, known_map)
            exit_known = _scan_block(node.block, copy.deepcopy(entry_known))
            prev_known = known_map.get(node)
            changed = (prev_known is None) or (known_map[node] != exit_known)
            known_map[node] = exit_known
            if (changed):
                queue.extend(node.succ)
        for node in known_map:
            entry = common_keys(node.pred, known_map)
            propagate_known(node.block, entry)


def common_keys(nodes: list[CFGNode],
                known_map: dict[CFGNode, dict[str, Token]]
                ) -> dict[str, Token]:
    """Creates a common dict between a block and its predicessors"""
    merged = None
    for pred in nodes:
        pred_known = known_map.get(pred)
        if pred_known is None:
            continue
        if merged is None:
            merged = copy.deepcopy(pred_known)
            continue
        for k in list(merged.keys()):
            if k not in pred_known or merged[k] != pred_known[k]:
                del merged[k]
    return merged if merged is not None else {}


def _scan_block(block: BasicBlock, entry: dict[str, Token]) -> dict[str, Token]:
    """Scans a block to find known constants"""
    known: dict[str, Token] = copy.copy(entry)
    for instr in block.instr_list:
        if (instr.instr_type in ('DECL', 'ASSIGN')):
            assert (isinstance(instr.res, Token))
            known.pop(instr.res.value, None)
            if (instr.left is None):
                continue
            assert (isinstance(instr.left, Token))
            if (instr.right is None and instr.left.type == 'NUMBER'):
                known[instr.res.value] = instr.left
            elif (instr.right is None and instr.left.type == 'IDENTIFIER'):
                if (instr.res.value == instr.left.value):
                    continue
                known[instr.res.value] = known.get(
                    instr.left.value, instr.left)
    return known


def propagate_known(block: BasicBlock, entry) -> None:
    """Replaces known constants in instruction"""
    known = dict(entry)
    for instr in block.instr_list:
        if (isinstance(instr.left, Token) and instr.left.type == 'IDENTIFIER'):
            known_tok = known.get(instr.left.value)
            if known_tok is not None:
                instr.left = copy.deepcopy(known_tok)
        if (isinstance(instr.right, Token) and instr.right.type == 'IDENTIFIER'):
            known_tok = known.get(instr.right.value)
            if known_tok is not None:
                instr.right = copy.deepcopy(known_tok)

        if instr.instr_type in ('IF', 'WHILE', 'FOR', 'RETURN'):
            if (isinstance(instr.res, Token) and instr.res.type == 'IDENTIFIER'):
                known_tok = known.get(instr.res.value)
                if known_tok is not None:
                    instr.res = copy.deepcopy(known_tok)
        if instr.instr_type in ('DECL', 'ASSIGN'):
            assert (isinstance(instr.res, Token))
            res_name = instr.res.value
            known.pop(res_name, None)
            if instr.left is None:
                continue
            if instr.op is None and instr.right is None:
                assert (isinstance(instr.left, Token))
                if instr.left.type == 'NUMBER':
                    known[res_name] = instr.left
                elif instr.left.type == 'IDENTIFIER' and instr.left.value != res_name:
                    known[res_name] = known.get(
                        instr.left.value, instr.left)
