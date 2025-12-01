
import os, json, random, re
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

def save_json(name, obj):
    p = DATA_DIR / f"{name}.json"
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)

def load_json(name, default):
    p = DATA_DIR / f"{name}.json"
    if not p.exists():
        return default
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

dice_expr_re = re.compile(r'(\d*)d(\d+)', re.I)

def roll_dice(expr):
    """
    Parse expressions like '2d6+3-1d4' and return total and breakdown
    """
    expr = expr.replace(" ", "")
    # replace d with standardized form
    parts = re.split(r'(?=[+-])', expr)
    total = 0
    breakdown = []
    for part in parts:
        if part == "":
            continue
        sign = 1
        if part[0] == '+':
            part = part[1:]
        elif part[0] == '-':
            sign = -1
            part = part[1:]
        m = dice_expr_re.fullmatch(part)
        if m:
            n = int(m.group(1)) if m.group(1) else 1
            s = int(m.group(2))
            rolls = [random.randint(1,s) for _ in range(n)]
            subtotal = sum(rolls)
            total += sign*subtotal
            breakdown.append((f"{'-' if sign<0 else ''}{n}d{s}", rolls, sign*subtotal))
        else:
            # flat number
            try:
                val = int(part)
                total += sign*val
                breakdown.append((f"{'-' if sign<0 else ''}{val}", [], sign*val))
            except:
                raise ValueError(f"Can't parse part: {part}")
    return total, breakdown
