from src.tac import *

# https://www.geeksforgeeks.org/software-engineering/software-engineering-control-flow-graph-cfg/
class CFGNode:
    def __init__(self, block):
        self.block = block
        self.succ = []
        self.pred = []
        self.label = block.instr_list[0] if block.instr_list else None
        if(self.label and self.label.instr_type != 'LABEL'):
            self.label = None
        self.last_instr = block.instr_list[-1] if block.instr_list else None

    def add_succ(self, other):
        if other not in self.succ:
            self.succ.append(other)
            other.pred.append(self)


def build_cfg(tac: TAC):
    func_list = tac.functions
    node_list = []
    for func_block in func_list:
        node_list.append(_cfg_builder(func_block))
    return node_list


def _cfg_builder(func):
    nodes = [CFGNode(block) for block in func.blocks]
    label_to_node = {}
    for node in nodes:
        if node.label:
            label_to_node[node.label.res] = node

    for i, node in enumerate(nodes):
        term = node.last_instr
        if term is None:
            if i + 1 < len(nodes):
                node.add_succ(nodes[i + 1])
        elif term.instr_type == 'GOTO':
            node.add_succ(label_to_node[term.res])
        elif term.instr_type in {'IF', 'FOR', 'WHILE'}:
            node.add_succ(label_to_node[term.left])
            node.add_succ(label_to_node[term.right])
        elif term.instr_type not in {'RETURN'} and i + 1 < len(nodes):
            node.add_succ(nodes[i + 1])
    return nodes