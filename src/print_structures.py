from dataclasses import is_dataclass, asdict, fields
# AI Generated Formatting Code
def ast_to_json(ast):
    if ast is None:
        return None
    if is_dataclass(ast):
        return {key: ast_to_json(value) for key, value in asdict(ast).items()}
    return ast
# AI Generated AST Print Function
def pretty_ast(ast) -> str:
    """Return a tree-style string of the AST using ASCII connectors."""
    def format_atom(v):
        if v is None:
            return "None"
        if isinstance(v, list):
            return "[]"
        # Prefer concise Token rendering
        try:
            from src.tokens import Token  # lazy import for isinstance check
        except Exception:
            Token = None
        if Token is not None and isinstance(v, Token):
            return f"{v.type}({repr(v.value)})"
        return repr(v) if isinstance(v, str) else str(v)

    def render(node, indent: str = "", is_last: bool = True) -> str:
        lines = []
        connector = "└──" if is_last else "├──"
        if is_dataclass(node):
            name = node.__class__.__name__
            if indent == "":
                lines.append(f"{name}")
            else:
                lines.append(f"{indent}{connector} {name}")
            child_indent = indent + ("    " if is_last else "│   ")
            flds = list(fields(node))
            for idx, f in enumerate(flds):
                val = getattr(node, f.name)
                last_field = idx == len(flds) - 1
                branch = "└──" if last_field else "├──"
                sub_indent = child_indent + ("    " if last_field else "│   ")
                if is_dataclass(val):
                    lines.append(f"{child_indent}{branch} {f.name}")
                    lines.extend(render(val, sub_indent, True).splitlines())
                elif isinstance(val, list):
                    if len(val) == 0:
                        lines.append(f"{child_indent}{branch} {f.name}: []")
                    else:
                        lines.append(f"{child_indent}{branch} {f.name}")
                        for j, item in enumerate(val):
                            item_last = j == len(val) - 1
                            lines.extend(render(item, sub_indent, item_last).splitlines())
                else:
                    lines.append(f"{child_indent}{branch} {f.name}: {format_atom(val)}")
            return "\n".join(lines)
        elif isinstance(node, list):
            label = f"list[{len(node)}]"
            if indent == "":
                lines.append(label)
            else:
                lines.append(f"{indent}{connector} {label}")
            child_indent = indent + ("    " if is_last else "│   ")
            for j, item in enumerate(node):
                lines.extend(render(item, child_indent, j == len(node) - 1).splitlines())
            return "\n".join(lines)
        else:
            text = format_atom(node)
            if indent == "":
                lines.append(text)
            else:
                lines.append(f"{indent}{connector} {text}")
            return "\n".join(lines)

    return render(ast)

def pretty_tac(instructions) -> str:
    """Format TAC into readable text.

    Accepts any of:
    - List[Instruction]
    - List[BasicBlock] (with attribute `code`)
    - List[FunctionIR] (with attribute `blocks` and `name`)
    - A single FunctionIR or BasicBlock
    - A single Instruction

    Matches current Instruction(res, left, right=None, op=None) usage in src/tac.py,
    including postfix temp+update and special unary encodings for BITNOT/LOGNOT.
    """
    OP_SYMBOL = {
        'PLUS': '+', 'MINUS': '-', 'MULTIPLY': '*', 'DIVIDE': '/', 'MODULUS': '%',
        'LESSTHAN': '<', 'GREATERTHAN': '>', 'LESSTHANEQUAL': '<=', 'GREATERTHANEQUAL': '>=',
        'EQUAL': '==', 'NOTEQUAL': '!=',
        'LOGAND': '&&', 'LOGOR': '||', 'LOGNOT': '!',
        'BITAND': '&', 'BITOR': '|', 'BITXOR': '^', 'BITNOT': '~',
        'LEFTSHIFT': '<<', 'RIGHTSHIFT': '>>',
        'INCREMENT': '+', 'DECREMENT': '-',
    }

    def operand_str(x):
        try:
            from src.tokens import Token
            from dataclasses import is_dataclass
            import src.ast_nodes as astn
        except Exception:
            Token = None
            astn = None
            is_dataclass = lambda v: False
        if x is None:
            return ''
        # Unwrap AST wrapper nodes like Identifier/Literal to their token
        if astn is not None and is_dataclass(x) and hasattr(x, 'token'):
            x = getattr(x, 'token')
        if Token is not None and isinstance(x, Token):
            if x.type == 'IDENTIFIER':
                return str(x.value)
            if x.type == 'NUMBER':
                return str(x.value)
            if x.type == 'CHAR_LITERAL':
                return repr(x.value)
            if x.type == 'STRING_LITERAL':
                return repr(x.value)
            if x.type == 'BOOL':
                return repr(x.value)
            return f"{x.type}({repr(x.value)})"
        return str(x)

    def op_info(op_token):
        try:
            from src.tokens import Token
        except Exception:
            Token = None
        if op_token is None:
            return None, None
        if Token is not None and isinstance(op_token, Token):
            return OP_SYMBOL.get(op_token.type, str(op_token.value)), op_token.type
        s = str(op_token)
        return s, s

    def format_instruction(ins, index):
        op_print, op_type = op_info(getattr(ins, 'op', None))
        dst = operand_str(getattr(ins, 'res', None))
        left_raw = getattr(ins, 'left', None)
        left = operand_str(left_raw)
        right_raw = getattr(ins, 'right', None)
        right = operand_str(right_raw)

        # RETURN encoding support:
        # - Old: res=None, left=value
        # - Current: res=value, left=None
        if op_type == 'RETURN':
            ret_val = None
            if left_raw is not None:
                ret_val = left
            else:
                # Fall back to dst (res) when left is None
                dst_str = dst.strip() if isinstance(dst, str) else dst
                if dst_str not in (None, ""):
                    ret_val = dst
            return f"{index:04}: return" if ret_val is None else f"{index:04}: return {ret_val}"

        # GOTO encoding: op=GOTO, target label in res (fallback to left)
        if op_type == 'GOTO':
            label_name = operand_str(getattr(ins, 'res', None)) or operand_str(getattr(ins, 'left', None))
            return f"{index:04}: goto {label_name}"

        # LABEL encoding: op=LABEL, label name may be in res or left
        if op_type == 'LABEL':
            label_name = operand_str(getattr(ins, 'res', None)) or operand_str(getattr(ins, 'left', None))
            return f"{index:04}: label {label_name}:"

        # CALL encoding: op=CALL, res=temp, left=function name
        if op_type == 'CALL':
            func_name = operand_str(getattr(ins, 'left', None))
            dst_name = operand_str(getattr(ins, 'res', None))
            if dst_name:
                return f"{index:04}: {dst_name} = call {func_name}"
            return f"{index:04}: call {func_name}"

        # Conditional statements encoding per your layout:
        # res = condition place, left = true target, right = false target
        if op_type in {'IFSTMT', 'WHILESTMT', 'FORSTMT'}:
            cond = operand_str(getattr(ins, 'res', None))
            tlabel = operand_str(getattr(ins, 'left', None)) if getattr(ins, 'left', None) is not None else None
            flabel = operand_str(getattr(ins, 'right', None)) if getattr(ins, 'right', None) is not None else None
            # Unified rendering as IF-style conditional with true/else labels
            if tlabel and flabel:
                return f"{index:04}: if {cond} goto {tlabel} else {flabel}"
            if tlabel:
                return f"{index:04}: if {cond} goto {tlabel}"
            if flabel:
                return f"{index:04}: if not {cond} goto {flabel}"
            return f"{index:04}: if {cond}"

        if op_print is None:
            # Treat special assignment-like encodings
            # PARAM encoding seen as: res=Token('PARAM','param'), left=arg
            try:
                from src.tokens import Token as _Tkn
            except Exception:
                _Tkn = None
            res_raw = getattr(ins, 'res', None)
            if _Tkn is not None and isinstance(res_raw, _Tkn) and getattr(res_raw, 'type', None) == 'PARAM':
                return f"{index:04}: param {left}"
            return f"{index:04}: {dst} = {left}"

        if left_raw is None and right_raw is not None and op_type in {'BITNOT', 'LOGNOT'}:
            return f"{index:04}: {dst} = {op_print} {dst}"

        if right_raw is None:
            return f"{index:04}: {dst} = {op_print} {left}"
        return f"{index:04}: {dst} = {left} {op_print} {right}"

    def flatten_to_functions(obj):
        """Return list of tuples (func_name, list_of_blocks), where list_of_blocks is a list of lists of instructions."""
        funcs = []
        if obj is None:
            return funcs
        # Single FunctionIR
        if hasattr(obj, 'blocks') and hasattr(obj, 'name'):
            blocks = []
            for b in getattr(obj, 'blocks', []) or []:
                code = getattr(b, 'code', None)
                if code is None:
                    code = getattr(b, 'instr_list', []) or []
                blocks.append(list(code))
            funcs.append((getattr(obj, 'name', '<anon>'), blocks))
            return funcs
        # List of something
        if isinstance(obj, list):
            if len(obj) == 0:
                return []
            first = obj[0]
            # List[FunctionIR]
            if hasattr(first, 'blocks') and hasattr(first, 'name'):
                for f in obj:
                    funcs.extend(flatten_to_functions(f))
                return funcs
            # List[BasicBlock]
            if hasattr(first, 'code') or hasattr(first, 'instr_list'):
                blocks = []
                for b in obj:
                    code = getattr(b, 'code', None)
                    if code is None:
                        code = getattr(b, 'instr_list', []) or []
                    blocks.append(list(code))
                funcs.append((None, blocks))
                return funcs
            # List[Instruction]
            funcs.append((None, [list(obj)]))
            return funcs
        # Single BasicBlock
        if hasattr(obj, 'code') or hasattr(obj, 'instr_list'):
            code = getattr(obj, 'code', None)
            if code is None:
                code = getattr(obj, 'instr_list', []) or []
            funcs.append((None, [list(code)]))
            return funcs
        # Single Instruction
        if hasattr(obj, 'op') and hasattr(obj, 'res'):
            funcs.append((None, [[obj]]))
            return funcs
        # Fallback: nothing
        return funcs

    lines = []
    # Allow passing the whole TAC object; print globals then functions
    prelude_lines = []
    obj = instructions
    if hasattr(obj, 'functions'):
        # Print globals first if present
        globals_list = getattr(obj, 'globals', None)
        if globals_list:
            prelude_lines.append("globals:")
            gidx = 0
            for ins in globals_list:
                line = format_instruction(ins, gidx)
                prelude_lines.append("  " + line)
                gidx += 1
            prelude_lines.append("")
        # Then render functions from the TAC object
        obj = getattr(obj, 'functions')

    functions = flatten_to_functions(obj)
    block_counter = 0  # global block numbering across all functions
    for fname, blocks in functions:
        idx = 0
        if fname is not None:
            # Unwrap token/Identifier names to string
            disp_name = operand_str(fname)
            lines.append(f"function {disp_name}:")
        for code in blocks:
            if fname is not None:
                lines.append(f"  block {block_counter}:")
                block_counter += 1
            for ins in code:
                line = format_instruction(ins, idx)
                if fname is not None:
                    lines.append("    " + line)
                else:
                    lines.append(line)
                idx += 1
        if fname is not None and blocks:
            lines.append("")

    full = []
    if prelude_lines:
        full.extend(prelude_lines)
    full.extend(lines)
    return "\n".join(full).rstrip()
