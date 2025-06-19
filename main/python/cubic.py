from sympy import symbols, sympify, simplify, solve, expand
import re

x = symbols('x')

def preprocess(expr):
    expr = expr.replace("^", "**")
    expr = re.sub(r'(\d)(x)', r'\1*\2', expr)
    expr = re.sub(r'(x)(\d)', r'\1**\2', expr)
    return expr

def find_roots_from_expr(expr_str):
    output = ""
    try:
        expr_str = preprocess(expr_str)
        expr = sympify(expr_str)
        expr = simplify(expr)
        expr = expand(expr)

        degree = expr.as_poly(x).degree()
        if degree != 3:
            return f"❌ The equation is degree {degree}, not a cubic.\n"

        output += f"📘 Parsed Expression: {expr}\n"

        roots = solve(expr, x)
        if not roots:
            output += "❌ No roots found.\n"
            return output

        output += "\n✅ Roots of the equation:\n"
        for i, r in enumerate(roots, 1):
            r_simplified = simplify(r)
            approx = r_simplified.evalf()
            output += f"Root {i}: {r_simplified} ≈ {approx:.6f}\n"

        return output

    except Exception as e:
        return f"⚠️ Error parsing or solving the expression: {e}\n"

# Accept an optional argument
def main(expr_str=None):
    if expr_str is None:
        print("🔍 Cubic Equation Root Finder")
        print("Enter a cubic polynomial like: x^3 - 6x^2 + 11x - 6\n")
        expr_str = input("Enter the expression: ")

    result = find_roots_from_expr(expr_str)
    print(result)
    return result  # Return for programmatic use

# CLI entry
if __name__ == "__main__":
    main()
