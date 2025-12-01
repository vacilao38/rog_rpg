import json, os, re, random
DATA_DIR = os.path.join(os.getcwd(), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def save_json(name, data):
    path = os.path.join(DATA_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(name, default=None):
    path = os.path.join(DATA_DIR, f"{name}.json")
    if not os.path.exists(path):
        return default if default is not None else {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}

# simple dice parser: supports expressions like "2d6+3", "d20", "3d6-1"
dice_re = re.compile(r'(?P<count>\d*)d(?P<sides>\d+)(?P<mod>[+-]\d+)?', re.I)

def roll_dice(expr: str):
    """
    Parse a dice expression and roll it. Returns (total, breakdown)
    breakdown: list of tuples (desc, rolls-list-or-empty, subtotal)
    """
    expr = expr.strip().lower().replace(" ", "")
    # handle multiple terms separated by + or - not supported complex; we parse single term or prefixed integer
    m = dice_re.fullmatch(expr)
    if not m:
        # allow plain integer
        try:
            val = int(expr)
            return val, [("const", [], val)]
        except:
            raise ValueError("Invalid dice expression")
    count = int(m.group("count")) if m.group("count") else 1
    sides = int(m.group("sides"))
    mod = int(m.group("mod")) if m.group("mod") else 0
    rolls = [random.randint(1, sides) for _ in range(count)]
    subtotal = sum(rolls) + mod
    desc = f"{count}d{sides}{'+'+str(mod) if mod>0 else (str(mod) if mod<0 else '')}"
    return subtotal, [(desc, rolls, subtotal)]
