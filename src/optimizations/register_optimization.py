from src.tac import TAC, Instruction, Token, BasicBlock
from src.optimizations.cfg import CFGNode, build_cfg
import copy

# https://www.youtube.com/watch?v=eeXk_ec1n6g
# https://www.geeksforgeeks.org/dsa/graph-coloring-set-2-greedy-algorithm/

"""Generates an InterferenceGraph and tracks variable liveness"""


class InterferenceGraph:
    """Holds edges and nodes for variable interference"""

    def __init__(self):
        self.edges: set[tuple[str, str]] = set()
        self.nodes: set[str] = set()

    def add_node(self, var: str) -> None:
        self.nodes.add(var)

    def add_edge(self, var1: str, var2: str) -> None:
        if (var1 == var2):
            return
        if (var2, var1) in self.edges:
            return
        self.edges.add((var1, var2))
        self.nodes.add(var1)
        self.nodes.add(var2)


def register_optimization(tac: TAC) -> dict[str, int]:
    """Takes in a Three Adress Code and finds close to optimal register allocation"""
    funcs_live_list = liveness_analysis(tac)
    func_list = tac.functions
    graph = InterferenceGraph()
    # building interference graph
    for func_block, live_list in zip(func_list, funcs_live_list):
        instr_list = [instr
                      for block in func_block.blocks
                      for instr in block.instr_list]
        for instr, liveness in zip(instr_list, live_list):
            out_set = liveness[1]
            defined_var = def_var(instr)
            if (defined_var is None):
                continue
            # Filter out paramaters
            if (defined_var.startswith('%param')):
                continue
            graph.add_node(defined_var)
            for out_var in out_set:
                if (out_var.startswith('%param')):
                    continue
                if (out_var != defined_var):
                    graph.add_edge(defined_var, out_var)
    return greedy_reg_alloc(graph)


def greedy_reg_alloc(graph:  InterferenceGraph) -> dict[str, int]:
    """Finds greedy solution to graph coloring problem"""
    # helper funciton to sort edges
    def get_edges(node: str):
        return num_edges[node]
    edges: dict[str, set[str]] = dict()
    # make sure isolated nodes have a set
    for node in graph.nodes:
        edges[node] = set()
    for left, right in graph.edges:
        edges[left].add(right)
        edges[right].add(left)
    # Calculate and sort variables by number of edges
    num_edges = {}
    for node in graph.nodes:
        num_edges[node] = len(edges[node])
    num_edges_sorted = sorted(graph.nodes, key=get_edges, reverse=True)
    registers: dict[str, int] = dict()
    # Allocated registers and "color graph"
    for node in num_edges_sorted:
        reserved = {registers[reg_id]
                    for reg_id in edges[node]
                    if reg_id in registers}
        reg_id = 0
        while reg_id in reserved:
            reg_id += 1
        registers[node] = reg_id
    return registers


def def_var(instr: Instruction) -> str | None:
    if (instr.instr_type in ("ASSIGN", "DECL", "CALL")
        and hasattr(instr.res, "value")
            and isinstance(instr.res, Token)):
        return instr.res.value
    else:
        return None


# Return is too jumbled for useful information from type hints
def liveness_analysis(tac: TAC) -> list[list]:
    """Finds liveness of blocks then individual instructions"""
    cfg = build_cfg(tac)
    funcs_live_list = []
    # loop over every function's basic blocks
    for node_list in cfg:
        if (len(node_list) == 0):
            continue
        # reverse list to do bottom up liveness for basic blocks
        rev_node_list = copy.copy(node_list)
        rev_node_list.reverse()
        # dicts to hold CFGNode to liveness mappings
        block_liveness_prev: dict[CFGNode, list[set[str]]] = dict()
        block_liveness: dict[CFGNode, list[set[str]]] = dict()
        while True:
            # for ever basic block
            for node in rev_node_list:
                defined, used = track_variables_block(node.block)
                # list of successors of current block
                succ_list: list[CFGNode] = node.succ
                out_set: set[str] = set()
                # get all successors in variables
                for succ in succ_list:
                    succ_in = block_liveness.get(succ)
                    if succ_in:
                        out_set = out_set.union(succ_in[0])
                # get all in variables for this block
                in_set: set[str] = used.union(out_set - defined)
                block_liveness[node] = [in_set, out_set]
            if (block_liveness == block_liveness_prev):
                break
            block_liveness_prev = copy.copy(block_liveness)
        # Get liveness for each line inside each block
        line_liveness: list[tuple[set[str], set[str]]] = []
        # Travel every instruction once
        for node in node_list:
            # Get instruction list and traverse it bottom up
            instr_list = copy.copy(node.block.instr_list)
            instr_list.reverse()
            instr_liveness = []
            # Set out for last instruction as out for block
            out_set = block_liveness[node][1]
            for instr in instr_list:
                defined, used = track_variables_line(instr)
                in_set: set[str] = used.union(out_set - defined)
                instr_liveness.append((in_set, out_set))
                out_set = copy.copy(in_set)
            instr_liveness.reverse()
            # Track line liveness by index of line_liveness
            line_liveness += instr_liveness
        funcs_live_list.append(line_liveness)
    return funcs_live_list


def track_variables_line(instr: Instruction) -> tuple[set[str], set[str]]:
    """Track used and defined for a single instruction"""
    defined: set[str] = set()
    used: set[str] = set()
    if (instr.instr_type in ('DECL', 'ASSIGN')):
        if (not_in_dic(instr.left, defined)):
            assert (isinstance(instr.left, Token))
            used.add(instr.left.value)
        if (not_in_dic(instr.right, defined)):
            assert (isinstance(instr.right, Token))
            used.add(instr.right.value)
        assert (isinstance(instr.res, Token))
        defined.add(instr.res.value)
    if instr.instr_type in ('IF', 'FOR', 'WHILE'):
        if not_in_dic(instr.res, defined):
            assert (isinstance(instr.res, Token))
            used.add(instr.res.value)
    if (instr.instr_type == 'RETURN'):
        if (not_in_dic(instr.res, defined)):
            assert (isinstance(instr.res, Token))
            used.add(instr.res.value)
    return defined, used


def track_variables_block(block: BasicBlock) -> tuple[set[str], set[str]]:
    """Track used and defined for entire block"""
    defined: set[str] = set()
    used: set[str] = set()
    for instr in block.instr_list:
        if (instr.instr_type in ('DECL', 'ASSIGN')):
            if (not_in_dic(instr.left, defined)):
                assert (isinstance(instr.left, Token))
                used.add(instr.left.value)
            if (not_in_dic(instr.right, defined)):
                assert (isinstance(instr.right, Token))
                used.add(instr.right.value)
            assert (isinstance(instr.res, Token))
            defined.add(instr.res.value)
        if instr.instr_type in ('IF', 'FOR', 'WHILE'):
            if not_in_dic(instr.res, defined):
                assert (isinstance(instr.res, Token))
                used.add(instr.res.value)
        if (instr.instr_type == 'RETURN'):
            if (not_in_dic(instr.res, defined)):
                assert (isinstance(instr.res, Token))
                used.add(instr.res.value)
    return defined, used


def not_in_dic(instr: Token | str | None,
               defined: set[str]
               ) -> bool:
    if (instr is None
       or not isinstance(instr, Token)
       or instr.type != 'IDENTIFIER'
       or not hasattr(instr, 'value')
       or instr.value in defined):
        return False
    return True
