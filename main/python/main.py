import importlib

def execute_module(name):
    output = ""
    try:
        module = importlib.import_module(name)
        if hasattr(module, 'main'):
            result = module.main()
            if result is not None:
                output += result
        elif hasattr(module, 'evaluate_custom_expression_manual_steps'):
            result = module.evaluate_custom_expression_manual_steps()
            if result is not None:
                output += result
        else:
            output += f"No suitable entry point (main or evaluate function) in '{name}.py'\n"
    except Exception as e:
        output += f"❌ Error loading {name}.py: {e}\n"
    return output

def main():
    output = ""
    menu = {
        "1": "congruence",
        "2": "CRT",
        "3": "cubic",
        "4": "multiplier",
        "5": "sturm_final",
        "6": "trig_calc",
        "7": "proj",
        "8": "Poly_long_div",
        "9": "Quad",
        "0": "exit"
    }

    choice = "1"  # Example: Selecting 'congruence' module

    module_name = menu.get(choice)

    if module_name == "exit":
        output += "Exiting program.\n"
        return output

    if not module_name:
        output += "Invalid hardcoded choice. Please check the 'choice' variable.\n"
        return output

    output += execute_module(module_name)
    return output

if __name__ == "__main__":
    result = main()
    print(result)
