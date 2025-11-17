
from src.tac import *
from src.optimizations.cfg import *

def dead_code_elimination(tac: TAC):

    func_list = tac.functions
    for func_block in func_list:
        for blocks in func_block.blocks:
            var_usage = {}
            for index, instr in enumerate(list(blocks.instr_list)):
                if(instr.instr_type == 'ASSIGN' or instr.instr_type == 'DECL'):
                    # is variable in dictionary
                    # if false Add variable to dictionary
                    # if true mark varibale as true
                    if(var_usage.get(instr.res.value) is not None):
                        var_usage[instr.res.value][0] = True
                    else:
                        var_usage[instr.res.value] = [False, index]

                # Within each block, track variables and if they are used. delete if not used
                # Later look at expressions and if they evaluate to false you can replace entire path
            offset = 0
            for item in var_usage.items():
                instr_info = item[1]
                is_used = instr_info[0]
                index = instr_info[1]
                if not is_used:
                    blocks.instr_list.pop(index - offset)
                    offset += 1

    return tac