import re
import math
from fractions import Fraction

def parse_quadratic(equation_str):
    eq = equation_str.replace('−', '-').replace('–', '-').replace(' ', '')
    var_match = re.search(r'[a-zA-Z]', eq)
    var = var_match.group(0) if var_match else 'x'

    a = b = c = 0

    pattern_a = re.compile(rf'([+-]?\d*\.?\d*){var}²')
    pattern_b = re.compile(rf'([+-]?\d*\.?\d*){var}(?![^\d]*²)')
    pattern_c = re.compile(rf'([+-]?\d+)(?![^\d{var}])')

    match_a = pattern_a.search(eq)
    if match_a:
        a_str = match_a.group(1)
        a = float(a_str) if a_str not in ('', '+', '-') else float(f"{a_str}1")

    match_b = pattern_b.search(eq)
    if match_b:
        b_str = match_b.group(1)
        b = float(b_str) if b_str not in ('', '+', '-') else float(f"{b_str}1")

    eq_removed = re.sub(pattern_a, '', eq)
    eq_removed = re.sub(pattern_b, '', eq_removed)
    match_c = re.findall(r'[+-]?\d+(?![a-zA-Z])', eq_removed)
    if match_c:
        c = sum([float(val) for val in match_c])

    return int(a), int(b), int(c), var

def simplify_sqrt(n):
    if n == 0:
        return (0, 1)
    if n < 0:
        return 1, abs(n)
    m = int(math.floor(math.sqrt(n)))
    for i in range(m, 0, -1):
        if n % (i * i) == 0:
            outside = i
            inside = n // (i * i)
            return outside, inside
    return 1, n

def format_root(b, sqrt_coeff, sqrt_inner, a, sign='+'):
    b_val = -b
    if sqrt_coeff == 0 or sqrt_inner == 0:
        num = b_val
        denom = 2 * a
        common = math.gcd(int(num), int(denom))
        if int(denom // common) == 1:
            return str(int(num // common))
        return f"{int(num // common)} / {int(denom // common)}"

    term_to_add_subtract = sqrt_coeff
    if sign == '-':
        term_to_add_subtract = -sqrt_coeff

    numerator_val = b_val + term_to_add_subtract

    denom_val = 2 * a

    common_divisor = math.gcd(int(numerator_val), int(denom_val))

    num_s = int(numerator_val // common_divisor)
    denom_s = int(denom_val // common_divisor)

    if sqrt_inner == 1:
        if denom_s == 1:
            return str(num_s)
        return f"{num_s} / {denom_s}"
    else:
        common_gcd_all = math.gcd(math.gcd(abs(int(b_val)), abs(int(sqrt_coeff))), abs(int(2 * a)))

        b_simplified = int(b_val // common_gcd_all)
        sc_simplified = int(sqrt_coeff // common_gcd_all)
        denom_simplified = int((2 * a) // common_gcd_all)

        root_display_part = ""
        if sc_simplified == 1:
            root_display_part = f"\u221a{sqrt_inner}"
        elif sc_simplified == -1:
            root_display_part = f"-\u221a{sqrt_inner}"
        elif sc_simplified != 0 :
            root_display_part = f"{sc_simplified}\u221a{sqrt_inner}"

        if not root_display_part:
            num_str = f"{b_simplified}"
        else:
            signed_root_part = f"{sign} {root_display_part}" if b_simplified != 0 or sign == '-' else root_display_part
            if b_simplified == 0 and sign == '+':
                num_str = root_display_part
            elif b_simplified == 0 and sign == '-':
                num_str = f"-{root_display_part}"
            else:
                num_str = f"{b_simplified} {signed_root_part}"

        if denom_simplified == 1:
            return num_str.strip()
        return f"({num_str.strip()}) / {denom_simplified}"

def solve_quadratic_verbose_return(a, b, c, var):
    output = []
    output.append(f"\nGiven quadratic equation: {a}{var}² + ({b}){var} + ({c}) = 0")
    output.append("\nUsing Sridharacharya's formula:")
    output.append(f"{var} = (-b ± √(b² - 4ac)) / 2a")

    discriminant = b ** 2 - 4 * a * c
    output.append(f"\nStep 1: Discriminant D = ({b})² - 4×({a})×({c}) = {discriminant}")

    if discriminant < 0:
        abs_d = abs(int(discriminant))
        coeff, inner = simplify_sqrt(abs_d)
        output.append(f"Step 2: √D = √({discriminant}) = {coeff}√{inner}i (simplified)")

        def format_complex_root(b, sqrt_coeff, sqrt_inner, a, sign='+'):
            b_val = -b
            denom = 2 * a
            common = math.gcd(math.gcd(abs(int(b_val)), abs(int(sqrt_coeff))), abs(int(denom)))
            b_part = int(b_val // common)
            sc_part = int(sqrt_coeff // common)
            denom_part = int(denom // common)
            return f"({b_part} {sign} {sc_part}√{sqrt_inner}i) / {denom_part}"

        root1_str = format_complex_root(b, coeff, inner, a, '+')
        root2_str = format_complex_root(b, coeff, inner, a, '-')

        output.append("\nRoots in simplified radical form (complex):")
        output.append(f"{var} = {root1_str}")
        output.append(f"{var} = {root2_str}")
        return "\n".join(output)

    elif discriminant == 0:
        root_val = -b / (2 * a)
        if root_val.is_integer():
            root_val = int(root_val)
        else:
            root_val = str(Fraction(-b, 2 * a).limit_denominator())

        output.append(f"Step 2: √D = √{discriminant} = 0")
        output.append("\nOnly one root:")
        output.append(f"{var} = {root_val}")
        return "\n".join(output)

    else:
        sqrt_val_perfect_square = math.isqrt(int(discriminant))
        if sqrt_val_perfect_square * sqrt_val_perfect_square == discriminant:
            sqrt_d_simplified_coeff = int(sqrt_val_perfect_square)
            sqrt_d_simplified_inner = 1
            output.append(f"Step 2: √D = √{discriminant} = {sqrt_d_simplified_coeff}")
        else:
            sqrt_d_simplified_coeff, sqrt_d_simplified_inner = simplify_sqrt(int(discriminant))
            output.append(f"Step 2: √D = √{discriminant} = {sqrt_d_simplified_coeff}√{sqrt_d_simplified_inner} (simplified)")

        root1_str = format_root(b, sqrt_d_simplified_coeff, sqrt_d_simplified_inner, a, '+')
        root2_str = format_root(b, sqrt_d_simplified_coeff, sqrt_d_simplified_inner, a, '-')

        output.append("\nRoots in simplified radical form:")
        output.append(f"{var} = {root1_str}")
        output.append(f"{var} = {root2_str}")

        try:
            val1 = (-b + math.sqrt(discriminant)) / (2 * a)
            val2 = (-b - math.sqrt(discriminant)) / (2 * a)
            output.append("\nApproximate decimal values (rounded to 4 decimal places):")
            output.append(f"{var} ≈ {val1:.4f}")
            output.append(f"{var} ≈ {val2:.4f}")
        except:
            pass

        return "\n".join(output)

def main(equation_str):
    try:
        a, b, c, var = parse_quadratic(equation_str)
        if a == 0:
            return "❌ Not a quadratic equation. Coefficient 'a' must not be zero."
        return solve_quadratic_verbose_return(a, b, c, var)
    except Exception as e:
        return f"❌ Invalid input. Could not parse the equation: {str(e)}"
