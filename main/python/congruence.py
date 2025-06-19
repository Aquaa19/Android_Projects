def gcd(a, m):
    if m == 0:
        return a, 1, 0
    gcd_val, p_prime, q_prime = gcd(m, a % m)
    p = q_prime
    q = p_prime - (a // m) * q_prime
    return gcd_val, p, q

def main(arg=None):
    output = ""
    try:
        if arg is None:
            return "❌ No input provided. Format: a b m"

        parts = arg.strip().split()
        if len(parts) != 3:
            return "❌ Invalid input. Please enter: a b m"

        a, b, m = map(int, parts)
        if m == 0:
            return "❌ Modulus 'm' cannot be zero."

        output += f"Solving linear congruence: {a}x ≡ {b} (mod {m})\n"

        d, p, q = gcd(a, m)
        output += f"GCD({a}, {m}) = {d}\n"
        output += f"Coefficients: p = {p}, q = {q}\n"
        output += f"Verification: {a} * {p} + {m} * {q} = {a*p + m*q}\n"

        if b % d != 0:
            output += "❌ No solution exists since b is not divisible by GCD(a, m)\n"
        else:
            x0 = (b * p // d) % m
            output += f"x(0) = {x0}\n"
            output += "✅ All solutions:\n"
            for j in range(d):
                xj = (x0 + (m * j) // d) % m
                output += f"x({j}) = {xj} (mod {m})\n"

    except Exception as e:
        output += f"⚠️ Error: {e}"

    return output
