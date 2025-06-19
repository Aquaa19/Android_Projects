def gcd(a, m):
    if m == 0:
        return a, 1, 0

    gcd_val, p_prime, q_prime = gcd(m, a % m)
    p = q_prime
    q = p_prime - (a // m) * q_prime

    return gcd_val, p, q

def linear_congruence_solver(a, b, m):
    d, p, q = gcd(a, m)

    if b % d != 0:
        return None

    x0 = (b * p // d) % m
    return x0

def crt_solver(congruences):
    output = ""
    n = len(congruences)
    a_list = [a for a, m in congruences]
    m_list = [m for a, m in congruences]
    from math import gcd
    from itertools import combinations
    for (m1,m2) in combinations(m_list,2):
        if gcd(m1,m2)!=1:
            return "❌ Moduli are not pairwise co-prime. CRT may not be applicable"
    M = 1
    for m in m_list:
        M *= m
    output += f"\nM = m1 * m2 * ... * mn = {M}\n"

    M_list = [M // m_i for m_i in m_list]

    output += "\nSolving the required congruences:\n"
    for i in range(n):
        output += f"(M/m{i+1})*x ≡ 1 mod m{i+1}: {M_list[i]}*x ≡ 1 mod {m_list[i]}\n"

    solutions = []
    for i in range(n):
        b_i = linear_congruence_solver(M_list[i], 1, m_list[i])
        if b_i is None:
            output += f"No solution exists for {M_list[i]}*x ≡ 1 mod {m_list[i]}\n"
            return output
        output += f"Solution: x ≡ {b_i} mod {m_list[i]}\n"
        solutions.append(b_i)

    x0 = 0
    for i in range(n):
        x0 += a_list[i] * M_list[i] * solutions[i]

    x = x0 % M
    output += f"\nCalculating x0:\n"
    terms = []
    for i in range(n):
        terms.append(f"a{i+1}*(M/m{i+1})*b{i+1}")
    expression = " + ".join(terms)
    output += f"x0 = {expression}\n"

    output += f"x0 = {x0}\n"
    output += f"\nx ≡ {x0} mod {M}\n"
    output += f"\nFinal solution: x ≡ {x} mod {M}\n"
    return output + f"\nThe smallest positive solution is: {x}\n"

def main(arg=None):
    output = ""
    output+= "\nChinese Remainder Theorem Solver\n"
    output+="for the system: x ≡ a1 (mod m1), x ≡ a2 (mod m2), ..., x ≡ an (mod mn),\n\n"
    try:
        if arg is None:
            return "❌ No input provided. Format: a1 m1 a2 m2 ... an mn"

        parts = arg.strip().split()
        if len(parts) % 2 != 0:
            return "❌ Invalid input. Expected pairs of 'a m' values."

        congruences = []
        for i in range(0, len(parts), 2):
            a = int(parts[i])
            m = int(parts[i+1])
            if m == 0:
                return "❌ Modulus 'm' cannot be zero."
            congruences.append((a, m))

        for i,(a,m) in enumerate(congruences):
            output+=f"x ≡ {a} (mod {m})\n"

        result=crt_solver(congruences)
        output+= result if result else "\nNo solution found.\n"
    except Exception as e:
        output+=f"⚠️ Error: {e}\n"

    return output


