from src.tac import *

class Offset_Map:
    def __init__(self, register: str):
        self.offset = 8
        self.var_map = {}
        self.register = register

    def lookup(self, var, add_if_not_found=False):
        location = self.var_map.get(var, None)
        if(location is None and add_if_not_found):
            self.set_loc(var)
            location = self.var_map.get(var)
        elif(location is None):
            raise Exception()
        return location

    def set_loc(self, var):
        self.var_map[var] = f"[{self.register}-{self.offset}]"
        self.offset += 8


def tac_to_asm(tac:TAC, num_regs: int):
    #regs = {}
    #for i in range(num_regs):
    #    regs[f"%r{i}"] = None
    #lru = []
    asm = []

    offset_map = Offset_Map("rbp")


    func_list = tac.functions
    for func_blocks in func_list:
        asm.append(f"{func_blocks.name.value}:")
        for blocks in func_blocks.blocks:
            for instr in blocks.instr_list:
                if(instr.instr_type == 'DECL'):
                    if(instr.left is not None):
                        asm.append(f"; {instr.res.value} = {instr.left.value}")
                        asm = decl_instr(instr, asm, offset_map)
                    # Add constant vs, variable

                elif(instr.instr_type == 'ASSIGN'):
                    if(instr.op is None):
                        asm.append(f"; {instr.res.value} = {instr.left.value}")
                        asm = decl_instr(instr, asm, offset_map)

                    elif(instr.op.type == "PLUS"):
                        asm.append(f"; {instr.res.value} = {instr.left.value} + {instr.right.value}")
                        asm = creat_instr(instr, "rax", add_instr, asm, offset_map)

                    elif(instr.op.type == "MINUS"):
                        asm.append(f"; {instr.res.value} = {instr.left.value} - {instr.right.value}")
                        asm = creat_instr(instr, "rax", sub_instr, asm, offset_map)

                    elif(instr.op.type == "MULTIPLY"):
                        asm.append(f"; {instr.res.value} = {instr.left.value} * {instr.right.value}")
                        asm = creat_instr(instr, "rax", mul_instr, asm, offset_map)

                    elif(instr.op.type == "DIVIDE"):
                        asm.append(f"; {instr.res.value} = {instr.left.value} / {instr.right.value}")
                        asm = div_instr(instr, asm, offset_map)

                    elif(instr.op.type == "MODULUS"):
                        asm.append(f"; {instr.res.value} = {instr.left.value} % {instr.right.value}")
                        asm = mod_instr(instr, asm, offset_map)

                    elif(instr.op.type == "GREATERTHAN"):
                        asm.append(f"; {instr.res.value} = {instr.left.value} > {instr.right.value}")
                        asm = g_than_instr(instr, asm, offset_map)

                    elif(instr.op.type == "LESSTHAN"):
                        asm.append(f"; {instr.res.value} = {instr.left.value} < {instr.right.value}")
                        asm = l_than_instr(instr, asm, offset_map)

                    elif(instr.op.type == "INCREMENT"):
                        asm.append(f"; {instr.res.value} = {instr.left.value}++")
                        store_loc = offset_map.lookup(instr.res.value, True)
                        asm.append(mov_instr("rax", store_loc))
                        asm.append(add_instr("rax", 1))
                        asm.append(mov_instr(store_loc, "rax"))

                    elif(instr.op.type == "DECREMENT"):
                        asm.append(f"; {instr.res.value} = {instr.left.value}--")
                        store_loc = offset_map.lookup(instr.res.value, True)
                        asm.append(mov_instr("rax", store_loc))
                        asm.append(sub_instr("rax", 1))
                        asm.append(mov_instr(store_loc, "rax"))

                    else:
                        raise NotImplementedError

                elif(instr.instr_type == 'GOTO'):
                    asm.append(f"jmp {instr.res}")

                elif(instr.instr_type == 'LABEL'):
                    asm.append(f"{instr.res}:")

                elif(instr.instr_type in {'IF', 'WHILE', 'FOR'}):
                    store_loc = offset_map.lookup(instr.res.value, True)
                    asm.append(cmp_instr(store_loc, 0))
                    asm.append(jne_instr(instr.left))
                    asm.append(jmp_instr(instr.right))

                elif(instr.instr_type == 'RETURN'):
                    asm.append(mov_instr("eax", instr.res.value))

                else:
                    raise NotImplementedError
    return asm



def mov_instr(r1, r2):
    return f"mov {r1}, {r2}"

def movzx_instr(r1, r2):
    return f"movzx {r1}, {r2}"

def add_instr(r1, r2):
    return f"add {r1}, {r2}"

def sub_instr(r1, r2):
    return f"sub {r1}, {r2}"

def mul_instr(r1, r2):
    return f"imul {r1}, {r2}"

def cmp_instr(r1, r2):
    return f"cmp {r1}, {r2}"

def set_instr(c, r2):
    return f"set{c} {r2}"

def cqo_instr():
    return f"cqo"

def idiv_instr(r):
    return f"idiv {r}"

def jmp_instr(l):
    return f"jmp {l}"

def jne_instr(l):
    return f"jne {l}"

def creat_instr(instr, r, func_instr, asm, offset_map):
    store_loc = offset_map.lookup(instr.res.value, True)
    if(instr.left.type == "NUMBER"):
        asm.append(mov_instr(r, instr.left.value))
    else:
        left_loc = offset_map.lookup(instr.left.value)
        asm.append(mov_instr(r, left_loc))

    if(instr.right.type == "NUMBER"):
        asm.append(func_instr(r, instr.right.value))
    else:
        right_loc = offset_map.lookup(instr.right.value)
        asm.append(func_instr(r, right_loc))
    asm.append(mov_instr(store_loc, r))
    return asm

def div_instr(instr, asm, offset_map): # Add custom register support
    store_loc = offset_map.lookup(instr.res.value, True)
    if(instr.left.type == "NUMBER"):
        asm.append(mov_instr("rax", instr.left.value))
    else:
        left_loc = offset_map.lookup(instr.left.value)
        asm.append(mov_instr("rax", left_loc))

    if(instr.right.type == "NUMBER"):
        asm.append(mov_instr("rbx", instr.right.value))
    else:
        right_loc =  offset_map.lookup(instr.right.value)
        asm.append(mov_instr("rbx", right_loc))
    asm.append(cqo_instr())
    asm.append(idiv_instr("rbx"))
    asm.append(mov_instr(store_loc, "rax"))
    return asm

def g_than_instr(instr, asm, offset_map):
    store_loc = offset_map.lookup(instr.res.value, True)
    if(instr.left.type == "NUMBER"):
        asm.append(mov_instr("rax", instr.left.value))
    else:
        left_loc = offset_map.lookup(instr.left.value)
        asm.append(mov_instr("rax", left_loc))
    if(instr.right.type == "NUMBER"):
        asm.append(cmp_instr("rax", instr.right.value))
    else:
        right_loc = offset_map.lookup(instr.right.value)
        asm.append(cmp_instr("rax", right_loc))
    asm.append(set_instr("g", "al"))
    asm.append(movzx_instr("rax", "al"))
    asm.append(mov_instr(store_loc, "rax"))
    return asm

def l_than_instr(instr, asm, offset_map):
    store_loc = offset_map.lookup(instr.res.value, True)
    if(instr.left.type == "NUMBER"):
        asm.append(mov_instr("rax", instr.left.value))
    else:
        left_loc = offset_map.lookup(instr.left.value)
        asm.append(mov_instr("rax", left_loc))

    if(instr.right.type == "NUMBER"):
        asm.append(cmp_instr("rax", instr.right.value))
    else:
        right_loc = offset_map.lookup(instr.right.value)
        asm.append(cmp_instr("rax", right_loc))
    asm.append(set_instr("l", "al"))
    asm.append(movzx_instr("rax", "al"))
    asm.append(mov_instr(store_loc, "rax"))
    return asm

def mod_instr(instr, asm, offset_map):
    store_loc = offset_map.lookup(instr.res.value, True)
    if(instr.left.type == "NUMBER"):
        asm.append(mov_instr("rax", instr.left.value))
    else:
        left_loc = offset_map.lookup(instr.left.value)
        asm.append(mov_instr("rax", left_loc))
    if(instr.right.type == "NUMBER"):
        asm.append(mov_instr("rbx", instr.right.value))
    else:
        right_loc = offset_map.lookup(instr.right.value)
        asm.append(mov_instr("rbx", right_loc))

    asm.append(cqo_instr())
    asm.append(idiv_instr("rbx"))
    asm.append(mov_instr(store_loc, "rdx"))
    return asm

def decl_instr(instr, asm, offset_map):
    store_loc = offset_map.lookup(instr.res.value, True)
    if(instr.left.type == "NUMBER"):
        asm.append(mov_instr("rax", instr.left.value))
    else:
        left_loc = offset_map.lookup(instr.left.value)
        asm.append(mov_instr("rax", left_loc))
    asm.append(mov_instr(store_loc, "rax"))
    return asm