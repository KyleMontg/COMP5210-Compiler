from src.tac import *


class ASM:
    '''
    Stores list of ASM instructions
    '''
    def __init__(self):
        self.instr_list = []

class Offset_Map:
    '''
    Stores a map of variable names and their offset for thier memory location
    '''
    def __init__(self, register: str):
        self.offset = 8
        self.var_map = {}
        self.register = register

    def lookup(self, var):
        location = self.var_map.get(var, None)
        if(location is None):
            self.set_loc(var)
            location = self.var_map.get(var)
        return location

    def set_loc(self, var):
        self.var_map[var] = f"[{self.register}-{self.offset}]"
        self.offset += 8



class RegAllocator:
    '''
    Handles storing variables into memory and registers
    '''
    def __init__(self, num_regs, asm):
        self.lru = []
        self.asm = asm.instr_list
        self.offset_map = Offset_Map("%fp")
        self.reg_map = {}
        self.regs = {}
        for i in range(num_regs):
            self.regs[f"%r{i}"] = None
        self.free_reg = []
        for i in range(num_regs):
            self.free_reg.append(f"%r{i}")

    def _mark_used(self, reg):
        '''
        Updates the Register to the front of Least Recently Used List
        '''
        if reg in self.lru:
            self.lru.remove(reg)
        self.lru.append(reg)

    def _store_var(self, reg):
        '''
        Stores the variable in a register to a frame
        '''
        var = self.regs[reg]
        if var is not None:
            store_loc = self.offset_map.lookup(var)
            self.asm.append(mov_instr(store_loc, reg))
            self.reg_map.pop(var, None)
            self.regs[reg] = None

    def _alloc_reg(self):
        '''
        Gets a free register or releases a register to be used
        '''
        if self.free_reg:
            reg = self.free_reg.pop(0)
        else:
            reg = self.lru.pop(0)
            self._store_var(reg)
        self._mark_used(reg)
        return reg

    def get_reg(self, var):
        '''
        Returns a register that holds var
        '''
        # Assign frame offset if var does not have one
        frame_loc = self.offset_map.lookup(var)
        if var in self.reg_map:
            reg = self.reg_map[var]
            self._mark_used(reg)
            return reg
        reg = self._alloc_reg()
        self.asm.append(mov_instr(reg, frame_loc))
        self.regs[reg] = var
        self.reg_map[var] = reg
        self._mark_used(reg)
        return reg

    def assign_reg(self, var, reg):
        '''
        Assigns a specific register to a specific variable
        '''
        if(self.regs[reg] not in (None, var)):
            self._store_var(reg)
        old_reg = self.reg_map.get(var, None)
        if old_reg is not None and old_reg != reg:
            self.regs[old_reg] = None
            self.reg_map.pop(var, None)
            if old_reg not in self.free_reg:
                self.free_reg.append(old_reg)
        self.regs[reg]= var
        self.reg_map[var] = reg
        self._mark_used(reg)



def tac_to_asm(tac:TAC, num_regs = 12):
    '''
    Reads Three Address Code and Produces Assembly X64
    '''
    if(num_regs < 3):
        raise ASMError("ASM Generator requires at least 3 registers")
    asm_obj = ASM()
    asm = asm_obj.instr_list
    reg_all = RegAllocator(num_regs, asm_obj)

    func_list = tac.functions
    for func_blocks in func_list:
        asm.append(f"{func_blocks.name.value}:")
        for blocks in func_blocks.blocks:
            for instr in blocks.instr_list:
                if(instr.instr_type == 'DECL'):
                    if(instr.left is not None):
                        asm.append(f"; {instr.res.value} = {instr.left.value}")
                        decl_instr(instr, asm, reg_all)

                elif(instr.instr_type == 'ASSIGN'):
                    if(instr.op is None):
                        asm.append(f"; {instr.res.value} = {instr.left.value}")
                        decl_instr(instr, asm, reg_all)

                    elif(instr.op.type == "PLUS"):
                        asm.append(f"; {instr.res.value} = {instr.left.value} + {instr.right.value}")
                        creat_instr(instr, add_instr, asm, reg_all)

                    elif(instr.op.type == "MINUS"):
                        asm.append(f"; {instr.res.value} = {instr.left.value} - {instr.right.value}")
                        creat_instr(instr, sub_instr, asm, reg_all)

                    elif(instr.op.type == "MULTIPLY"):
                        asm.append(f"; {instr.res.value} = {instr.left.value} * {instr.right.value}")
                        creat_instr(instr, mul_instr, asm, reg_all)

                    elif(instr.op.type == "DIVIDE"):
                        asm.append(f"; {instr.res.value} = {instr.left.value} / {instr.right.value}")
                        div_instr(instr, asm, reg_all)

                    elif(instr.op.type == "MODULUS"):
                        asm.append(f"; {instr.res.value} = {instr.left.value} % {instr.right.value}")
                        mod_instr(instr, asm, reg_all)

                    elif(instr.op.type == "GREATERTHAN"):
                        asm.append(f"; {instr.res.value} = {instr.left.value} > {instr.right.value}")
                        lg_than_instr(instr, asm, 'g', reg_all)

                    elif(instr.op.type == "LESSTHAN"):
                        asm.append(f"; {instr.res.value} = {instr.left.value} < {instr.right.value}")
                        lg_than_instr(instr, asm, 'l', reg_all)

                    elif(instr.op.type == "INCREMENT"):
                        asm.append(f"; {instr.res.value} = {instr.left.value}++")
                        incr_instr(instr, asm, reg_all)

                    elif(instr.op.type == "DECREMENT"):
                        asm.append(f"; {instr.res.value} = {instr.left.value}--")
                        decr_instr(instr, asm, reg_all)

                    else:
                        raise NotImplementedError

                elif(instr.instr_type == 'GOTO'):
                    asm.append(f"jmp {instr.res}")

                elif(instr.instr_type == 'LABEL'):
                    asm.append(f"{instr.res}:")

                elif(instr.instr_type in {'IF', 'WHILE', 'FOR'}):
                    store_loc = reg_all._alloc_reg()
                    reg_all.assign_reg(instr.res.value, store_loc)
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

def incr_instr(instr, asm, reg_all):
    # Increments a registers value by 1
    store_loc = reg_all.get_reg(instr.res.value)
    asm.append(add_instr(store_loc, 1))

def decr_instr(instr, asm, reg_all):
    # Decrements a registers value by 1
    store_loc = reg_all.get_reg(instr.res.value)
    asm.append(sub_instr(store_loc, 1))

def creat_instr(instr, func_instr, asm: list, reg_all: RegAllocator):
    # Handles Addition, Subtraction, and Multiplication
    # Get a new register
    store_loc = reg_all._alloc_reg()
    if(instr.left.type == "NUMBER"):
        asm.append(mov_instr(store_loc, instr.left.value))
    else:
        left_reg = reg_all.get_reg(instr.left.value)
        asm.append(mov_instr(store_loc, left_reg))

    if(instr.right.type == "NUMBER"):
        asm.append(func_instr(store_loc, instr.right.value))
    else:
        right_reg = reg_all.get_reg(instr.right.value)
        asm.append(func_instr(store_loc, right_reg))
    reg_all.assign_reg(instr.res.value, store_loc)

def div_instr(instr, asm, reg_all: RegAllocator): # Add custom register support
    if(instr.left.type == "NUMBER"):
        left_reg = reg_all._alloc_reg()
        asm.append(mov_instr(left_reg, instr.left.value))
    else:
        left_reg = reg_all.get_reg(instr.left.value)

    if(instr.right.type == "NUMBER"):
        right_reg = reg_all._alloc_reg()
        asm.append(mov_instr(right_reg, instr.right.value))
    else:
        right_reg = reg_all.get_reg(instr.right.value)
    # Extend register
    asm.append(cqo_instr())
    # Divide by right value
    asm.append(idiv_instr(right_reg))
    # Store
    reg_all.assign_reg(instr.res.value, left_reg)


def lg_than_instr(instr, asm, l_or_g: str, reg_all: RegAllocator):
    store_loc = reg_all._alloc_reg()
    if(instr.left.type == "NUMBER"):
        left_reg = reg_all._alloc_reg()
        asm.append(mov_instr(left_reg, instr.left.value))
    else:
        left_reg = reg_all.get_reg(instr.left.value)

    if(instr.right.type == "NUMBER"):
        asm.append(cmp_instr(left_reg, instr.right.value))
    else:
        right_reg = reg_all.get_reg(instr.right.value)
        asm.append(cmp_instr(left_reg, right_reg))
    # Set compare flag
    asm.append(set_instr(l_or_g, "al"))
    # Move result into store location register
    asm.append(movzx_instr(store_loc, "al"))
    # Assign reister to variable
    reg_all.assign_reg(instr.res.value, store_loc)

def mod_instr(instr, asm, reg_all: RegAllocator):
    store_loc = reg_all.get_reg(instr.res.value)

    if(instr.left.type == "NUMBER"):
        left_reg = reg_all._alloc_reg()
        asm.append(mov_instr(left_reg, instr.left.value))
    else:
        left_reg = reg_all.get_reg(instr.left.value)

    if(instr.right.type == "NUMBER"):
        right_reg = reg_all._alloc_reg()
        asm.append(mov_instr(right_reg, instr.right.value))
    else:
        right_reg = reg_all.get_reg(instr.right.value)

    asm.append(cqo_instr())
    asm.append(idiv_instr(right_reg))
    remain_reg = reg_all._alloc_reg()
    asm.append(mov_instr(remain_reg, "rdx"))
    reg_all.assign_reg(instr.res.value, remain_reg)


def decl_instr(instr, asm, reg_all: RegAllocator):
    store_loc = reg_all._alloc_reg()
    reg_all.assign_reg(instr.res.value, store_loc)
    if(instr.left.type == "NUMBER"):
        asm.append(mov_instr(store_loc, instr.left.value))
    else:
        left_reg = reg_all.get_reg(instr.left.value)
        asm.append(mov_instr(store_loc, left_reg))
