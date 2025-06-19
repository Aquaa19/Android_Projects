def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def main(arg=None):
    output = ""

    if arg is None:
        return "❌ No input provided.\n"

    try:
        parts = arg.strip().split()
        if len(parts) != 2:
            return "❌ Please provide two numbers separated by space.\n"

        num1, num2 = map(int, parts)

        output += f"Finding smallest multiplier so that {num1} × multiplier is divisible by {num2}:\n"

        if num2 == 0:
            return "❌ Cannot divide by zero.\n"

        if num1 % num2 == 0:
            output += f"✅ {num1} is already divisible by {num2}.\n"
            output += f"No multiplier needed. {num1} / {num2} = {num1 // num2}\n"
            return output

        common = gcd(num1, num2)
        c = num2 // common
        d = num1 * c

        output += f"✅ Multiply {num1} by {c} to make it divisible by {num2}\n"
        output += f"{num1} × {c} = {d}\n"
        output += f"{d} / {num2} = {d // num2}\n"

        return output

    except ValueError:
        return "❌ Invalid input. Please enter two integers separated by space.\n"
