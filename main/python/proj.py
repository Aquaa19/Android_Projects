from sympy import expand, simplify, factor, sympify, symbols
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
import re

# Unicode superscript conversion maps
unicode_sup_map = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
superscript_map = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
    '-': '⁻'
}

def unicode_to_normal_expr(expr):
    def replace(match):
        base = match.group(1)
        supers = match.group(2).translate(unicode_sup_map)
        return f"{base}^{supers}"
    return re.sub(r'([a-zA-Z0-9)])([⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+)', replace, expr)

def normal_to_unicode_expr(expr):
    def replace(match):
        power = match.group(1)
        return ''.join(superscript_map.get(ch, ch) for ch in power)
    expr = re.sub(r'\*\*([\-]?\d+)', lambda m: replace(m), expr)
    expr = expr.replace('*', '')  # Remove all multiplication signs
    return expr

def insert_implicit_multiplication_rules(expr_str):
    expr_str = re.sub(r'(\d)([a-zA-Z(])', r'\1*\2', expr_str)
    expr_str = re.sub(r'([a-zA-Z])([a-zA-Z])', r'\1*\2', expr_str)
    expr_str = re.sub(r'(\))([a-zA-Z0-9(])', r'\1*\2', expr_str)
    expr_str = re.sub(r'([a-zA-Z0-9])(\()', r'\1*\2', expr_str)
    return expr_str

def _parse_expression_string(expression_string):
    expr_str = expression_string.strip()
    if not expr_str:
        return None, "❌ Error: Expression cannot be empty."
    expr_str = unicode_to_normal_expr(expr_str)
    expr_processed = expr_str.replace('^', '**')
    expr_processed = insert_implicit_multiplication_rules(expr_processed)
    try:
        transformations = standard_transformations + (implicit_multiplication_application, convert_xor)
        parsed_expr = parse_expr(expr_processed, transformations=transformations, evaluate=False)
        return parsed_expr, None
    except Exception as e:
        return None, f"❌ Error parsing expression: {e}"

def expand_expr(expression_string):
    parsed_expr, error = _parse_expression_string(expression_string)
    if error:
        return error
    try:
        expanded = expand(parsed_expr)
        return normal_to_unicode_expr(str(expanded))
    except Exception as e:
        return f"❌ Error during expansion: {e}"

def simplify_expr(expression_string):
    parsed_expr, error = _parse_expression_string(expression_string)
    if error:
        return error
    try:
        simplified = simplify(parsed_expr)
        try:
            factored_after_simplify = factor(simplified)
            return normal_to_unicode_expr(str(factored_after_simplify))
        except Exception:
            return normal_to_unicode_expr(str(simplified))
    except Exception as e:
        return f"❌ Error during simplification: {e}"

def factor_expr(expression_string):
    parsed_expr, error = _parse_expression_string(expression_string)
    if error:
        return error
    try:
        factored = factor(parsed_expr)
        return normal_to_unicode_expr(str(factored))
    except Exception as e:
        return f"❌ Error during factorization: {e}. Not all expressions can be factored."

def substitute_expr(full_input_string):
    parts = full_input_string.split(';', 1)
    expression_string = parts[0].strip()
    if not expression_string:
        return "❌ Error: Expression part cannot be empty for substitution."
    parsed_expr, error = _parse_expression_string(expression_string)
    if error:
        return error
    substitutions = {}
    if len(parts) > 1 and parts[1].strip():
        var_assignments_str = parts[1].strip()
        try:
            expr_symbols = parsed_expr.free_symbols
            assignments = var_assignments_str.split(',')
            for assignment in assignments:
                assignment = assignment.strip()
                if not assignment:
                    continue
                var_val = assignment.split('=', 1)
                if len(var_val) != 2:
                    return f"❌ Error: Invalid variable assignment format: '{assignment}'. Expected 'var=value'."
                var_name = var_val[0].strip()
                val_str = var_val[1].strip()
                if not var_name:
                    return f"❌ Error: Variable name cannot be empty in '{assignment}'."
                if not val_str:
                    return f"❌ Error: Value cannot be empty for variable '{var_name}'."
                try:
                    val = sympify(val_str)
                except Exception as e_val:
                    return f"❌ Error: Could not parse value '{val_str}' for variable '{var_name}': {e_val}"
                substitutions[symbols(var_name)] = val
        except Exception as e_parse_subs:
            return f"❌ Error parsing variable assignments: {e_parse_subs}"
    else:
        if parsed_expr.free_symbols:
            return "❌ Error: Expression has variables but no values provided for substitution. Format: expr; var1=val1, var2=val2"
    try:
        substituted_expr = parsed_expr.subs(substitutions)
        if not substituted_expr.free_symbols:
            evaluated_result = substituted_expr.evalf()
            return str(evaluated_result)
        else:
            return normal_to_unicode_expr(str(substituted_expr))
    except Exception as e:
        return f"❌ Error during substitution/evaluation: {e}"

def main(argument_string, mode="expand"):
    mode = mode.lower()
    if mode == "expand":
        return expand_expr(argument_string)
    elif mode == "simplify":
        return simplify_expr(argument_string)
    elif mode == "factor":
        return factor_expr(argument_string)
    elif mode == "substitute":
        return substitute_expr(argument_string)
    else:
        return f"❌ Error: Unknown mode '{mode}'. Valid modes: expand, simplify, factor, substitute."
