SIZE = 1024


def int_to_bool_list(num: int, length: int) -> list[bool]:
    binary_str = bin(num)[2:].zfill(length)
    if len(binary_str) > length:
        raise ValueError(f"Number {num} requires more than {length} bits")
    return [bit == '1' for bit in binary_str]


def bool_list_to_int(bool_list: list[bool]) -> int:
    return int(''.join('1' if b else '0' for b in bool_list), 2)


def reverse_bits(bool_list: list[bool]) -> list[bool]:
    return bool_list[::-1]


def xor_bool_lists(a: list[bool], b: list[bool]) -> list[bool]:
    assert len(a) == len(b), f"Lists must be same length: {len(a)} != {len(b)}"
    return [x ^ y for x, y in zip(a, b)]


def multiply_bool_lists(a: list[bool], b: list[bool]) -> list[bool]:
    """
    Multiply two SIZE-bit numbers represented as boolean lists.
    Returns a 2*SIZE-bit result.
    """
    assert len(a) == SIZE, f"First operand must be SIZE bits, got {len(a)}"
    assert len(b) == SIZE, f"Second operand must be SIZE bits, got {len(b)}"

    int_a = bool_list_to_int(a)
    int_b = bool_list_to_int(b)
    result = int_a * int_b

    return int_to_bool_list(result, 2 * SIZE)


def check_constraints(p: list[bool], q: list[bool], n: list[bool], veil_xor: list[bool], mask_size: int) -> bool:
    assert len(p) == SIZE, f"p must be SIZE bits, got {len(p)}"
    assert len(q) == SIZE, f"q must be SIZE bits, got {len(q)}"
    assert len(n) == 2 * SIZE, f"n must be 2*SIZE bits, got {len(n)}"
    assert len(veil_xor) == SIZE, f"veil_xor must be SIZE bits, got {len(veil_xor)}"

    p_masked = [False] * SIZE
    q_masked = [False] * SIZE

    for i in range(mask_size):
        p_masked[i] = p[i]
        q_masked[i] = q[i]

    for i in range(mask_size):
        p_masked[SIZE - mask_size + i] = p[SIZE - mask_size + i]
        q_masked[SIZE - mask_size + i] = q[SIZE - mask_size + i]

    product = multiply_bool_lists(p_masked, q_masked)

    # Check MSB bits of product
    top_n = bool_list_to_int(n[: mask_size + 1])
    top_product = bool_list_to_int(product[: mask_size + 1])
    if top_n - top_product > mask_size + 1:
        return False
    if top_product > top_n:
        return False

    # Check LSB bits of product
    for i in range(mask_size):
        if product[2 * SIZE - mask_size + i] != n[2 * SIZE - mask_size + i]:
            return False

    # Check veil XOR constraint for the masked bits
    q_reversed = reverse_bits(q_masked)
    p_xor_q_rev = xor_bool_lists(p_masked, q_reversed)

    # Check MSB bits of XOR
    for i in range(mask_size):
        if p_xor_q_rev[i] != veil_xor[i]:
            return False

    # Check LSB bits of XOR
    for i in range(mask_size):
        if p_xor_q_rev[SIZE - mask_size + i] != veil_xor[SIZE - mask_size + i]:
            return False

    return True


def generate_candidates(
    p_template: list[bool], q_template: list[bool], mask_size: int
) -> list[tuple[list[bool], list[bool]]]:
    """
    Generate new candidates by setting the next MSB and LSB bits.
    """
    assert len(p_template) == SIZE, f"p_template must be SIZE bits, got {len(p_template)}"
    assert len(q_template) == SIZE, f"q_template must be SIZE bits, got {len(q_template)}"

    candidates = []

    # Try all combinations of the new MSB and LSB bits for both p and q
    for p_msb in [False, True]:
        for p_lsb in [False, True]:
            for q_msb in [False, True]:
                for q_lsb in [False, True]:
                    new_p = p_template.copy()
                    new_q = q_template.copy()

                    # Set the new MSB bit
                    new_p[mask_size - 1] = p_msb
                    new_q[mask_size - 1] = q_msb

                    # Set the new LSB bit
                    new_p[SIZE - mask_size] = p_lsb
                    new_q[SIZE - mask_size] = q_lsb

                    candidates.append((new_p, new_q))

    return candidates


def progressive_factorization(n: int, veil_xor: int) -> tuple[int, int]:
    n_bits = int_to_bool_list(n, 2 * SIZE)
    veil_xor_bits = int_to_bool_list(veil_xor, SIZE)

    print(f"n has {len(n_bits)} bits")
    print(f"veil_xor has {len(veil_xor_bits)} bits")

    valid_candidates = []

    for i1 in [False, True]:
        for i2 in [False, True]:
            for i3 in [False, True]:
                for i4 in [False, True]:
                    # Create SIZE-bit templates with only the first and last bits set
                    p_template = [False] * SIZE
                    q_template = [False] * SIZE

                    p_template[0] = i1
                    p_template[-1] = i2
                    q_template[0] = i3
                    q_template[-1] = i4

                    if check_constraints(p_template, q_template, n_bits, veil_xor_bits, 1):
                        valid_candidates.append((p_template, q_template))

    print(f"Starting with {len(valid_candidates)} valid 1-bit candidates")

    # Progressive extension
    for mask_size in range(2, SIZE // 2 + 1):  # Up to 512 bits from each end
        new_candidates = []

        for p_template, q_template in valid_candidates:
            candidates = generate_candidates(p_template, q_template, mask_size)

            for new_p, new_q in candidates:
                if check_constraints(new_p, new_q, n_bits, veil_xor_bits, mask_size):
                    new_candidates.append((new_p, new_q))

        valid_candidates = new_candidates
        print(f"After {mask_size} bits: {len(valid_candidates)} valid candidates")

        if len(valid_candidates) == 0:
            print("No more valid candidates found")
            break

    if len(valid_candidates) == 0:
        raise ValueError("No valid factors found")

    # Return the first valid solution
    p_final, q_final = valid_candidates[0]

    # Verify lengths one more time
    assert len(p_final) == SIZE, f"Final p must be SIZE bits, got {len(p_final)}"
    assert len(q_final) == SIZE, f"Final q must be SIZE bits, got {len(q_final)}"

    p_int = bool_list_to_int(p_final)
    q_int = bool_list_to_int(q_final)

    return p_int, q_int


def solve_challenge(n: int, c: int, veil_xor: int) -> bytes:
    print("Starting progressive factorization...")
    p, q = progressive_factorization(n, veil_xor)

    print("Found factors:")
    print(f"p = {p}")
    print(f"q = {q}")

    # Verify the solution
    assert p * q == n, f"Invalid factorization: {p} * {q} != {n}"

    # Verify veil XOR constraint
    q_reversed_int = int(bin(q)[2:][::-1], 2)
    assert p ^ q_reversed_int == veil_xor, f"Invalid veil XOR: {p} ^ {q_reversed_int} != {veil_xor}"

    print("Factorization verified!")

    # Compute private exponent
    phi = (p - 1) * (q - 1)
    e = 65537
    d = pow(e, -1, phi)

    # Decrypt
    m = pow(c, d, n)

    # Convert to bytes
    flag = m.to_bytes((m.bit_length() + 7) // 8, 'big')

    return flag


if __name__ == "__main__":
    n = 25650993834245004720946189793874326497984795849338302417110946799293291648040249066481025511053012034073848003478136002015789778483853455736405270138192685004206122168607287667373629714589814547144217162436740164024414206705483947822707673759856022882063396271521077034396144039740088690783163935477234001508676877728359035563304374705319120303835098697559771353065115371216095633826663393222290375210498159025443467666369652776698531368926392564476840557482790175694984871271075976052162527476586777386578254654222259777299785563550342986250558793337690540798983389913689337683350216697595855274995968459458553148267
    c = 7874419222145223100478995004906732383469089972173454594282476506666095078687712494332749473566534625352139353593310707008146533254390514332880136585545606758108380402050369451711762195058199249765633645224407166178729834108159734540770902813439688437621416030538050164358987313607945402928893945400086827254622507315341530235984071126104731692679123171962413857123065243252313290356908958113679070546907527095194888688858140118665219670816655147095649132221436351529029926610142793850463533766705147562234382644751744682744799743855986811769162311342911946128543115444104102909314075691320520722623778914052878038508
    veiled_xor = 26845073698882094013214557201710791833291706601384082712658811014034994099681783926930272036664572532136049856667171349310624166258134687815795133386046337514685147643316723034719743474088423205525505355817639924602251866472741277968741560579392242642848932606998045419509860412262320853772858267058490738386
    
    flag = solve_challenge(n, c, veiled_xor)
    print("Decrypted flag:", flag.decode('utf-8', errors='ignore'))
