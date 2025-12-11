"""
Utilities to snapshot and compare TAC structures to detect unintended changes
introduced by optimization passes.

Primary API:
- snapshot_tac(tac, include_meta=True) -> dict
- diff_tac(a, b, include_meta=True, max_diffs=50) -> list[str]
- tac_equals(a, b, include_meta=True) -> bool
- compare_tac_structures(a, b, include_meta=True, max_diffs=50) -> tuple[bool, list[str]]

Usage:
    from src.tac_diff import diff_tac, tac_equals
    # Take a snapshot before optimization
    before = snapshot_tac(tac)
    # ... run optimization that may mutate tac in-place ...
    after = snapshot_tac(tac)
    diffs = diff_tac(before, after)  # or diff_tac(tac_before, tac_after)
    if diffs:
        print('\n'.join(diffs))
"""

from __future__ import annotations

from typing import Any, Iterable

try:
    # Optional imports; functions gracefully degrade if not available
    from src.tac import TAC, Instruction, BasicBlock, FunctionBlock  # type: ignore
    from src.tokens import Token  # type: ignore
except Exception:  # pragma: no cover - allow use just for structural dicts
    TAC = Instruction = BasicBlock = FunctionBlock = Token = object  # type: ignore


# -----------------------
# Normalization utilities
# -----------------------

def _norm_token(x: Any) -> Any:
    """Normalize a Token-like object to simple primitives.

    Returns a tuple (type, value) for Tokens; leaves primitives unchanged.
    """
    try:
        if isinstance(x, Token):  # type: ignore[misc]
            return (getattr(x, 'type', None), getattr(x, 'value', None))
    except Exception:
        pass
    return x


def _norm_operand(x: Any) -> Any:
    """Normalize instruction operands to primitives.

    - Token -> (type, value)
    - dataclass nodes with `.token` -> normalized token
    - primitives (str, int, None) -> as-is
    """
    if x is None:
        return None
    # Try to unwrap dataclass nodes that hold a token
    try:
        # Lazy import to avoid heavy deps when unused
        import dataclasses
        if dataclasses.is_dataclass(x) and hasattr(x, 'token'):
            return _norm_token(getattr(x, 'token'))
    except Exception:
        pass
    return _norm_token(x)


def _norm_op(x: Any) -> Any:
    """Normalize the op field to a stable primitive.

    For Tokens, prefer the token type (e.g., 'PLUS', 'LABEL'). Otherwise str(x).
    """
    if x is None:
        return None
    try:
        if isinstance(x, Token):  # type: ignore[misc]
            return getattr(x, 'type', None)
    except Exception:
        pass
    # Avoid converting numbers to strings unnecessarily
    if isinstance(x, (int, float)):
        return x
    return str(x)


def _norm_instruction(instr: Any) -> dict[str, Any]:
    return {
        'type': getattr(instr, 'instr_type', None),
        'res': _norm_operand(getattr(instr, 'res', None)),
        'left': _norm_operand(getattr(instr, 'left', None)),
        'right': _norm_operand(getattr(instr, 'right', None)),
        'op': _norm_op(getattr(instr, 'op', None)),
    }


def _norm_block(block: Any) -> list[dict[str, Any]]:
    instrs = getattr(block, 'instr_list', None)
    if instrs is None and hasattr(block, 'code'):
        instrs = getattr(block, 'code')  # alternate naming
    if instrs is None:
        return []
    return [_norm_instruction(i) for i in instrs]


def _norm_function(func: Any) -> dict[str, Any]:
    blocks = getattr(func, 'blocks', []) or []
    return {
        'name': getattr(func, 'name', None),
        'blocks': [_norm_block(b) for b in blocks],
    }


def _norm_globals(tac: Any) -> list[dict[str, Any]]:
    globs = getattr(tac, 'globals', []) or []
    return [_norm_instruction(i) for i in globs]


def snapshot_tac(tac_or_snapshot: Any, include_meta: bool = True) -> dict[str, Any] | Any:
    """Snapshot a TAC object (or return already-snapshotted dict unchanged).

    If input already looks like a snapshot (i.e., plain dict), it is returned
    as-is. This lets you call `diff_tac` with either TACs or snapshots.
    """
    if isinstance(tac_or_snapshot, dict):
        return tac_or_snapshot

    # If the object has `.functions`, treat it like TAC
    if hasattr(tac_or_snapshot, 'functions'):
        funcs = getattr(tac_or_snapshot, 'functions', []) or []
        snapshot = {
            'functions': [_norm_function(f) for f in funcs],
            'globals': _norm_globals(tac_or_snapshot),
        }
        if include_meta:
            snapshot.update({
                'temp_var_count': getattr(tac_or_snapshot, 'temp_var_count', None),
                'label_count': getattr(tac_or_snapshot, 'label_count', None),
                'ctrl_stack_len': len(getattr(tac_or_snapshot, 'ctrl_stack', []) or []),
            })
        return snapshot

    # If a list of FunctionBlocks was passed
    if isinstance(tac_or_snapshot, list):
        return {'functions': [_norm_function(f) for f in tac_or_snapshot]}

    # Fallback: try to normalize as a single function or block/instruction
    if hasattr(tac_or_snapshot, 'blocks'):
        return _norm_function(tac_or_snapshot)
    if hasattr(tac_or_snapshot, 'instr_list'):
        return _norm_block(tac_or_snapshot)
    if hasattr(tac_or_snapshot, 'instr_type'):
        return _norm_instruction(tac_or_snapshot)

    # Unknown type; return as-is
    return tac_or_snapshot


# -------------
# Deep diffing
# -------------

def _diff(a: Any, b: Any, path: str, out: list[str], max_diffs: int) -> None:
    if len(out) >= max_diffs:
        return

    # Exact type match for primitives
    if isinstance(a, (str, int, float, type(None))) and isinstance(b, (str, int, float, type(None))):
        if a != b:
            out.append(f"{path}: {a!r} != {b!r}")
        return

    # Dict comparison
    if isinstance(a, dict) and isinstance(b, dict):
        a_keys = set(a.keys())
        b_keys = set(b.keys())
        for k in sorted(a_keys - b_keys):
            if len(out) >= max_diffs:
                return
            out.append(f"{path}.{k}: key missing in right")
        for k in sorted(b_keys - a_keys):
            if len(out) >= max_diffs:
                return
            out.append(f"{path}.{k}: key missing in left")
        for k in sorted(a_keys & b_keys):
            _diff(a[k], b[k], f"{path}.{k}", out, max_diffs)
            if len(out) >= max_diffs:
                return
        return

    # List comparison
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: length {len(a)} != {len(b)}")
            if len(out) >= max_diffs:
                return
        # Compare up to overlapping length, then note extras
        for i, (ai, bi) in enumerate(zip(a, b)):
            _diff(ai, bi, f"{path}[{i}]", out, max_diffs)
            if len(out) >= max_diffs:
                return
        if len(a) > len(b):
            for i in range(len(b), len(a)):
                if len(out) >= max_diffs:
                    return
                out.append(f"{path}[{i}]: extra in left -> {a[i]!r}")
        elif len(b) > len(a):
            for i in range(len(a), len(b)):
                if len(out) >= max_diffs:
                    return
                out.append(f"{path}[{i}]: extra in right -> {b[i]!r}")
        return

    # Fallback: compare stringified values to avoid exceptions
    if a != b:
        out.append(f"{path}: {a!r} != {b!r}")


def diff_tac(a: Any, b: Any, include_meta: bool = True, max_diffs: int = 50) -> list[str]:
    """Return a list of human-readable differences between two TAC structures.

    `a` and `b` can be TAC objects or snapshots from `snapshot_tac`.
    """
    sa = snapshot_tac(a, include_meta=include_meta)
    sb = snapshot_tac(b, include_meta=include_meta)
    diffs: list[str] = []
    _diff(sa, sb, path='tac', out=diffs, max_diffs=max_diffs)
    if len(diffs) >= max_diffs:
        diffs.append(f"… truncated after {max_diffs} differences …")
    return diffs


def tac_equals(a: Any, b: Any, include_meta: bool = True) -> bool:
    """Shorthand boolean equality check for TAC structures."""
    return len(diff_tac(a, b, include_meta=include_meta, max_diffs=1)) == 0


def compare_tac_structures(
    a: Any,
    b: Any,
    include_meta: bool = True,
    max_diffs: int = 50,
) -> tuple[bool, list[str]]:
    """Return (are_equal, diffs) for two TACs or snapshots."""
    diffs = diff_tac(a, b, include_meta=include_meta, max_diffs=max_diffs)
    return (len(diffs) == 0, diffs)


__all__ = [
    'snapshot_tac',
    'diff_tac',
    'tac_equals',
    'compare_tac_structures',
]
