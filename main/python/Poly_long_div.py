from sympy import symbols, Poly, div, lcm, LC, simplify, S, sympify
import re
import sys
from io import StringIO
import re

def convert_unicode_superscripts(expr: str) -> str:
    """
    Converts Unicode superscripts (⁰-⁹) to Python exponent notation (**).
    Handles x³, (x+1)⁴, etc.
    """
    superscript_map = {
        '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
        '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'
    }

    result = ''
    i = 0
    while i < len(expr):
        if expr[i] in superscript_map:
            # This should never happen standalone
            result += '**' + superscript_map[expr[i]]
            i += 1
        elif expr[i] not in superscript_map:
            result += expr[i]
            i += 1
            # Check for trailing superscripts
            if i < len(expr) and expr[i] in superscript_map:
                power = ''
                while i < len(expr) and expr[i] in superscript_map:
                    power += superscript_map[expr[i]]
                    i += 1
                result += '**' + power
        else:
            result += expr[i]
            i += 1

    return result

def to_superscript(expr_str: str) -> str:
    superscript_digits = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
    }

    def replace_exp(match):
        base = match.group(1)
        power = match.group(2)
        supers = ''.join(superscript_digits.get(ch, ch) for ch in power)
        return f"{base}{supers}"

    # Step 1: Convert '**n' to superscripts
    expr_str = re.sub(r'([a-zA-Z0-9_()]+)\*\*([0-9]+)', replace_exp, expr_str)

    # Step 2: Remove multiplication signs where appropriate
    expr_str = re.sub(r'(?<=[a-zA-Z0-9⁰¹²³⁴⁵⁶⁷⁸⁹)])\*(?=[a-zA-Z(])', '', expr_str)

    return expr_str

def fix_expression(expr: str) -> str:
    """
    Fixes expression by adding * between numbers and variables, and converting ^ to **.
    Example: '3x^2 - 2x + 1' → '3*x**2 - 2*x + 1'
    """
    expr=convert_unicode_superscripts(expr)
    expr = expr.replace('^', '**')  # Replace caret with Python exponent
    expr = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', expr)  # 3x → 3*x
    expr = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', expr)  # x2 → x*2 (edge cases)
    expr = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', expr)  # xy → x*y
    return expr

def scale_to_match_leading_coeff(f1, f2):
    lc1 = LC(f1)
    lc2 = LC(f2)
    if lc1 == 0 or lc2 == 0:
        return S.Zero
    return S(lcm(lc2, lc1)) // lc1

def clean_integer_division_chain(f1, f2, vars):
    quotient_total = Poly(0, *vars)
    steps = []
    current_f1 = f1

    if f2.is_zero:
        return Poly(0, *vars), Poly(0, *vars), []

    while current_f1.degree() >= f2.degree():
        multiplier = scale_to_match_leading_coeff(current_f1, f2)
        if multiplier == S.Zero:
            break

        scaled_f1 = Poly(simplify(multiplier * current_f1.as_expr()), *vars)
        quotient, remainder = div(scaled_f1, f2, domain='QQ')

        remainder_expr = remainder.as_expr()
        denominators = [
            term.q for term in remainder_expr.as_coefficients_dict().values() if term.is_Rational
        ]
        lcm_denoms = lcm(denominators) if denominators else 1
        clean_remainder = Poly(simplify(remainder_expr * lcm_denoms), *vars)

        steps.append({
            'multiplier': multiplier,
            'scaled_f1': scaled_f1,
            'quotient': quotient,
            'remainder': clean_remainder
        })
        quotient_total += quotient
        current_f1 = clean_remainder

        if current_f1.degree() < f2.degree() or current_f1.is_zero:
            break

    return quotient_total, current_f1, steps

def perform_polynomial_division(f1_input: str, f2_input: str) -> str:
    output = ""
    try:
        all_symbols = list(sympify(f1_input + '+' + f2_input).free_symbols)
        if not all_symbols:
            return "❌ Error: No variables found in expressions."

        vars = symbols([str(s) for s in all_symbols])
        f1 = Poly(sympify(f1_input), *vars)
        f2 = Poly(sympify(f2_input), *vars)

        output += f"\nPerforming polynomial long division:\n"
        output += f"Numerator: {f1.as_expr()}\n"
        output += f"Denominator: {f2.as_expr()}\n"

        final_quotient, final_remainder, division_steps = clean_integer_division_chain(f1, f2, vars)

        if not division_steps:
            output += "\n❗ No division steps to show (possibly due to zero divisor or invalid degrees).\n"
            return output

        output += "\n--- Division Steps ---\n"
        for i, step in enumerate(division_steps, 1):
            output += f"Step {i}:\n"
            output += f"  Multiplier used: {step['multiplier']}\n"
            output += f"  Scaled dividend: {step['scaled_f1'].as_expr()}\n"
            output += f"  Quotient at this step: {step['quotient'].as_expr()}\n"
            output += f"  Remainder: {step['remainder'].as_expr()}\n\n"

        output += "--- Final Result ---\n"
        output += f"  Scaled dividend: {to_superscript(str(step['scaled_f1'].as_expr()))}\n"
        output += f"  Quotient at this step: {to_superscript(str(step['quotient'].as_expr()))}\n"
        output += f"  Remainder: {to_superscript(str(step['remainder'].as_expr()))}\n\n"
    except Exception as e:
        output += f"\n❌ Error: {e}\n"

    return output

def main(user_input=None):
    """
    Accepts input string like: "x^3 - 6x^2 + 11x - 6, x - 1"
    Parses it and calls perform_polynomial_division().
    """
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()

    try:
        print("\n=== Polynomial Long Division ===")

        if not user_input or ',' not in user_input:
            print("❌ Invalid input format. Use: <numerator>, <denominator>")
            sys.stdout = old_stdout
            return mystdout.getvalue()

        # Split and sanitize input
        parts = [p.strip() for p in user_input.split(',', 1)]
        f1_str = fix_expression(parts[0])
        f2_str = fix_expression(parts[1])

        # Perform division
        result = perform_polynomial_division(f1_str, f2_str)
        print(result)

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        sys.stdout = old_stdout
        return mystdout.getvalue()
