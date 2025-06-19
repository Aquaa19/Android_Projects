import math
import re
from fractions import Fraction

allowed_names = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "csc": lambda x: 1 / math.sin(x),
    "sec": lambda x: 1 / math.cos(x),
    "cot": lambda x: 1 / math.tan(x),
    "acsc": lambda x: math.asin(1 / x),
    "asec": lambda x: math.acos(1 / x),
    "acot": lambda x: math.atan(1 / x),
    "sqrt": math.sqrt,
    "pi": math.pi, "e": math.e
}

def fix_expression(expr: str) -> str:
    expr = expr.replace("^", "**")
    expr = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', expr)
    expr = re.sub(r'(\))([a-zA-Z(])', r'\1*\2', expr)
    expr = re.sub(r'(sin|cos|tan|asin|acos|atan|csc|sec|cot|acsc|asec|acot)\*\*(\d+)',
                  r'(\1(x))**\2', expr)
    return expr

def safe_eval(expr):
    expr = fix_expression(expr)
    try:
        return eval(expr, {"__builtins__": {}}, allowed_names)
    except ZeroDivisionError:
        raise ZeroDivisionError("Result: undefined (division by zero)")
    except Exception:
        raise ValueError("❌ Invalid mathematical expression")

def float_to_pi_fraction(x, tol=1e-6):
    if x == 0:
        return "0"
    coeff = x / math.pi
    sign = "-" if coeff < 0 else ""
    abs_coeff = abs(coeff)

    known = {
        1/6: "π/6", 1/4: "π/4", 1/3: "π/3", 1/2: "π/2",
        2/3: "2π/3", 3/4: "3π/4", 5/6: "5π/6", 1: "π",
        7/6: "7π/6", 5/4: "5π/4", 4/3: "4π/3", 3/2: "3π/2",
        5/3: "5π/3", 7/4: "7π/4", 11/6: "11π/6", 2: "2π"
    }

    for val, label in known.items():
        if abs(abs_coeff - val) < tol:
            return sign + label

    frac = Fraction(coeff).limit_denominator(12)
    return f"{sign}{abs(frac.numerator)}π/{frac.denominator}" if frac.denominator != 1 else f"{sign}{abs(frac.numerator)}π"

def float_to_sqrt_fraction(x, tol=1e-6):
    sqrt_vals = {
        math.sqrt(3): "√3", math.sqrt(2): "√2", math.sqrt(5): "√5",
        math.sqrt(6): "√6", math.sqrt(7): "√7",
        1 / math.sqrt(2): "1/√2", 1 / math.sqrt(3): "1/√3"
    }
    for val, sym in sqrt_vals.items():
        if abs(x - val) < tol:
            return sym
        if abs(x + val) < tol:
            return f"-{sym}"
    return None

def format_decimal_result(result, tol=1e-6):
    if abs(result) < tol:
        return "0"

    known_values = {
        math.sqrt(3)/2: "√3/2", math.sqrt(2)/2: "√2/2", 1/math.sqrt(3): "√3/3",
        1/2: "1/2", -math.sqrt(3)/2: "-√3/2", -1/2: "-1/2",
        0.5: "1/2", -0.5: "-1/2", 1: "1", -1: "-1"
    }
    for val, sym in known_values.items():
        if abs(result - val) < tol:
            return sym

    sqrt_sym = float_to_sqrt_fraction(result, tol)
    if sqrt_sym:
        return sqrt_sym

    return f"{result:.6f}"

def try_inverse_symbolic(expr: str, result: float):
    if any(fn in expr for fn in ("asin", "acos", "atan", "acsc", "asec", "acot")):
        return f"{float_to_pi_fraction(result)}"
    return None

def main(expression_string=None):
    from io import StringIO
    import sys

    if not expression_string:
        expression_string = "sin(4pi) + cos(pi/3)"

    expression_string = expression_string.strip()
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    print(f"\n📐 Evaluating: {expression_string}")

    try:
        result = safe_eval(expression_string)
        if isinstance(result, (int, float)):
            symbolic = try_inverse_symbolic(expression_string, result)
            if symbolic:
                print(f"Result: {symbolic}")
            else:
                print(f"Result: {format_decimal_result(result)}")
        else:
            print("❌ Error: Invalid result type")

    except ValueError as ve:
        print(ve)
    except ZeroDivisionError as zde:
        print(zde)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    sys.stdout = old_stdout
    return mystdout.getvalue()

if __name__ == "__main__":
    while True:
        expr = input("\nEnter trig expression (or 'exit'): ")
        if expr.lower() in ["exit", "quit"]:
            break
        print(main(expr))