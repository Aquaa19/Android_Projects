from sympy import symbols, lambdify, Poly
from sympy.core.backend import sympify
from sympy import div, lcm, LC, simplify, gcd
from io import StringIO
import sys, re

x = symbols('x')
EPSILON = 1e-9

# Mapping from unicode superscripts to regular digits
superscript_map = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")

# Mapping from normal digits to unicode superscripts
unicode_sup_map = {
    "0": "⁰", "1": "¹", "2": "²", "3": "³",
    "4": "⁴", "5": "⁵", "6": "⁶", "7": "⁷",
    "8": "⁸", "9": "⁹"
}

def to_unicode_superscript(expr):
    expr_str = str(expr)
    expr_str = re.sub(r'\*\*([0-9]+)', lambda m: ''.join(unicode_sup_map.get(ch, '') for ch in m.group(1)), expr_str)
    expr_str = expr_str.replace("*", "")  # Remove all explicit multiplications
    return expr_str

def preprocess_expression(expr):
    """
    Converts Unicode superscripts and implicit multiplication to valid sympy syntax.
    Example: x² -> x**2, 3x -> 3*x
    """
    superscript_map = {
        '⁰': '0', '¹': '1', '²': '2', '³': '3',
        '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'
    }

    # Replace superscripts with Python-style exponents
    def replace_superscripts(match):
        base = match.group(1)
        supers = match.group(2)
        power = ''.join(superscript_map.get(ch, '') for ch in supers)
        return f"{base}**{power}"

    expr = re.sub(r'(x)([⁰¹²³⁴⁵⁶⁷⁸⁹]+)', replace_superscripts, expr)

    # Replace implicit multiplication like 3x with 3*x
    expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)

    return expr

def parse_polynomial(expression_string):
    try:
        processed = preprocess_expression(expression_string.replace('^', '**'))
        expr = sympify(processed)
        return Poly(expr, x)
    except Exception as e:
        return None

def scale_to_match_leading_coeff(f1, f2):
    lc1, lc2 = LC(f1), LC(f2)
    if lc1 == 0 or lc2 == 0:
        return 1
    return lcm(abs(lc2), abs(lc1)) // abs(lc1)

def fraction_free_division(dividend, divisor):
    multiplier = scale_to_match_leading_coeff(dividend, divisor)
    scaled_dividend = Poly(simplify(multiplier * dividend.as_expr()), x)
    quotient, remainder = div(scaled_dividend, divisor, domain='QQ')
    remainder_expr = remainder.as_expr()
    denominators = [coeff.q for coeff in remainder_expr.as_coefficients_dict().values() if coeff.is_Rational]
    lcm_denoms = 1
    for d in denominators:
        lcm_denoms = (lcm_denoms * d) // gcd(lcm_denoms, d)
    clean_remainder = Poly(simplify(remainder_expr * lcm_denoms), x)
    return quotient, clean_remainder

def sturm_sequence_fraction_free(f, f1, show_steps=True):
    sequence = [f, f1]
    step = 1
    while True:
        dividend, divisor = sequence[-2], sequence[-1]
        if divisor.is_zero:
            break
        quotient, remainder = fraction_free_division(dividend, divisor)
        next_poly = -remainder
        if next_poly.is_zero:
            sequence.append(Poly(0, x))
            break
        sequence.append(next_poly)
        step += 1
    return sequence

def find_root_intervals(x_vals, sign_changes):
    root_intervals = []
    for i in range(len(sign_changes) - 1):
        delta = sign_changes[i] - sign_changes[i + 1]
        if delta != 0:
            root_intervals.append((x_vals[i], x_vals[i + 1], abs(delta)))
    return root_intervals

def count_sign_changes(signs):
    cleaned = [s for s in signs if s != "0" and s != "ERR"]
    return sum((a != b) for a, b in zip(cleaned, cleaned[1:])) if len(cleaned) >= 2 else 0

def main(user_input=None):
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    try:
        print("\n=== Sturm's Theorem Evaluation ===")

        if not user_input or not user_input.strip():
            print("No input provided. Expected format: polynomial, x1, x2, ...")
            sys.stdout = old_stdout
            return mystdout.getvalue()

        parts = [p.strip() for p in user_input.split(',') if p.strip()]
        if len(parts) < 1:
            print("Input too short.")
            sys.stdout = old_stdout
            return mystdout.getvalue()

        expression_string = parts[0]
        eval_points_strings = parts[1:]

        f = parse_polynomial(expression_string)
        if f is None:
            print("Failed to parse polynomial.")
            sys.stdout = old_stdout
            return mystdout.getvalue()

        f1 = f.diff(x)
        print(f"Parsed polynomial: f(x) = {to_unicode_superscript(f.as_expr())}")
        print(f"Derivative: f'(x) = {to_unicode_superscript(f1.as_expr())}")

        x_vals_to_use = [float(s) for s in eval_points_strings] if eval_points_strings else [-4, -3, -2, -1, 0, 1, 2, 3, 4]
        print("Using evaluation points:", x_vals_to_use)

        sequence = sturm_sequence_fraction_free(f, f1, show_steps=False)
        print("--- Final Sturm Sequence ---")
        for i, poly in enumerate(sequence):
            print(f"f{i}(x) = {to_unicode_superscript(poly.as_expr())}")

        sign_functions = [lambdify(x, poly.as_expr(), modules="math") for poly in sequence]
        sign_table = []

        for func in sign_functions:
            row = []
            for val_x in x_vals_to_use:
                try:
                    val_eval = func(val_x)
                    if abs(val_eval) < EPSILON:
                        sign_symbol = "0"
                    else:
                        sign_symbol = "+" if val_eval > 0 else "-"
                except Exception:
                    sign_symbol = "ERR"
                row.append(sign_symbol)
            sign_table.append(row)

        sign_changes_at_x = [count_sign_changes([sign_table[row][col] for row in range(len(sign_table))]) for col in range(len(x_vals_to_use))]

        col_width = max(max(len(str(xv)) for xv in x_vals_to_use), 3) + 2
        header = f"{'f⁰(x)':<7}| " + " ".join(f"{xv:^{col_width}} |" for xv in x_vals_to_use)
        print(header)
        print("-" * len(header))

        for i, row in enumerate(sign_table):
            line = f"f{i}(x) | " + " ".join(f"{s:^{col_width}} |" for s in row)
            print(line)
        print("-" * len(header))

        changes_line = f"V(x)  | " + " ".join(f"{c:^{col_width}} |" for c in sign_changes_at_x)
        print(changes_line)

        root_intervals = find_root_intervals(x_vals_to_use, sign_changes_at_x)
        print("\n=== Intervals Containing Roots ===")
        if root_intervals:
            for a, b, count in root_intervals:
                print(f" - {count} real root{'s' if count > 1 else ''} in interval ({a}, {b})")
        else:
            print(" - No real roots detected in the evaluated range.")

    except Exception as e:
        print(f"Error in Sturm's method: {e}")
    finally:
        sys.stdout = old_stdout
        return mystdout.getvalue()

if __name__ == "__main__":
    result_no_arg = main()
    print(result_no_arg)
