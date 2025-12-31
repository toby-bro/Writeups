# ELF_MASK = """\
# 7F454C46????????????????????????\
# 0200 0300????????XXXXXXXXXXXXXXXX\
# ????????????????????20000100????\
# """
# PE_MASK = """\
# 01000000XXXXXXXXXXXXXXXX????????\
# ????????????????040?????????????\
# """


def get_elf_mask(
    *,
    e_entry: str = '04IJKLMN',
    e_phoff: str = 'OPQRSTUV',
    e_type: str = '0200',
    e_machine: str = '0300',
) -> str:
    return f"""\
7F454C46????????????????????????\
{e_type}{e_machine}????????{e_entry}{e_phoff}\
????????????????????20000100????\
"""


def get_pe_mask(*, p_offset: str = '', p_vadd: str = '') -> str:
    if p_offset == '':
        p_offset = 'GHI00000'
    if p_vadd == '':
        p_vadd = 'GHIJKLMN'
    return f"""\
01000000{p_offset}{p_vadd}????????\
????????????????????????????????\
"""


def reconstruct_placeholders(resolutions: dict[str, str]) -> dict[str, str]:
    e_entry = '04IJKLMN'
    e_phoff = 'OPQRSTUV'
    p_vadd = 'GHIJKLMN'
    p_offset = 'GHI00000'
    for key, value in resolutions.items():
        if key in e_entry:
            e_entry = e_entry.replace(key, value)
        if key in e_phoff:
            e_phoff = e_phoff.replace(key, value)
        if key in p_offset:
            p_offset = p_offset.replace(key, value)
        if key in p_vadd:
            p_vadd = p_vadd.replace(key, value)
    return {
        'e_entry': e_entry,
        # "e_phoff": e_phoff,
        'p_offset': '00000000' if p_offset == '000WXYZ@' else p_offset,
        'p_vadd': p_vadd,
    }


def delete_placeholder_chars(s: str) -> str:
    for ch in 'GHIJKLMNOPQRSTUVWXYZ@':
        s = s.replace(ch, 'X')
    return s


def revert_byte_order(hex_str: str) -> str:
    """Reverse byte order: read bytes from end to start, like the shell script"""
    result = ''
    i = len(hex_str) - 2
    while i >= 0:
        result += hex_str[i : i + 2]
        i -= 2
    return result


def get_e_entry_from_org(org: int) -> int:
    return org + 0x14


def shift_endianness(hex_str: str) -> str:
    return ''.join(reversed([hex_str[i : i + 2] for i in range(0, len(hex_str), 2)]))


def int_to_hex_le(value: int, length: int) -> str:
    hex_str = f'{value:0{length * 2}X}'
    return shift_endianness(hex_str)


def valid_intersection(mask1: str, mask2: str, offset: int = 0) -> tuple[str, dict[str, str]]:  # noqa: C901
    resolutions: dict[str, str] = {}
    if mask1[offset : len(mask2) + offset] == mask2:
        return mask1, {}
    intersection = mask1[:offset]
    undetermined_char = False
    for i in range(len(mask2)):
        if mask1[i + offset] == ' ':
            continue
        if mask1[i + offset] == '?':
            undetermined_char = True
            intersection += mask2[i]
            continue
        if mask2[i] == '?':
            undetermined_char = True
            intersection += mask1[i + offset]
            continue
        if mask1[i + offset] == mask2[i]:
            intersection += mask1[i + offset]
            continue
        if mask1[i + offset] != mask2[i]:
            undetermined_char = True
            if not is_hex_string(mask1[i + offset]) or not is_hex_string(mask2[i]):
                # print(f"Non-hex character mismatch at offset {i + offset}: '{mask1[i + offset]}' != '{mask2[i]}'")
                if not is_hex_string(mask2[i]):
                    wrong_char = mask2[i]
                    goood_char = mask1[i + offset]
                    resolutions[wrong_char] = goood_char
                    intersection += wrong_char
                    intersection = intersection.replace(wrong_char, goood_char)
                    mask2 = mask2.replace(wrong_char, goood_char)
                    mask1 = mask1.replace(wrong_char, goood_char)
                    continue
                if not is_hex_string(mask1[i + offset]):
                    wrong_char = mask1[i + offset]
                    goood_char = mask2[i]
                    resolutions[wrong_char] = goood_char
                    intersection += wrong_char
                    intersection = intersection.replace(wrong_char, goood_char)
                    mask1 = mask1.replace(wrong_char, goood_char)
                    mask2 = mask2.replace(wrong_char, goood_char)
                    continue
            return '', {}
    if undetermined_char:
        sol, res = valid_intersection(intersection + mask1[len(mask2) + offset :], revert_byte_order(mask1), 0)
    else:
        sol = intersection
        res = {}
    if sol != '':
        if len(resolutions) != 0:
            # print(f"Resolutions applied: {resolutions}")
            pass
        res.update(resolutions)
        return sol, res
    return '', {}


def is_hex_string(s: str) -> bool:
    try:
        int(s, 16)
        return True
    except ValueError:
        return False


def get_palindrome(s: str, axis: int = -1) -> str:
    if axis == -1:
        axis = len(s) // 2 * 2
    r = s[: axis // 2 * 2]
    if axis % 2 != 0:
        r += s[axis - 1 : axis + 1]
    r += revert_byte_order(s[: axis // 2 * 2])
    return r


def check_symmetry(axis: int) -> dict[int, tuple[str, dict[str, str]]]:
    valid_p_shifts: dict[int, tuple[str, dict[str, str]]] = {}
    resulting = get_palindrome(get_elf_mask(), axis)
    _inter, res0 = valid_intersection(resulting, get_elf_mask())
    if _inter != '':
        for i in range(0, len(_inter) - len(get_pe_mask()) + 1, 2):
            elf_mask_with_offset = get_elf_mask(e_phoff=int_to_hex_le(i // 2, 4))
            new_mask0, res1 = valid_intersection(
                get_palindrome(elf_mask_with_offset, axis),
                elf_mask_with_offset,
            )
            res1.update(res0)
            if new_mask0 == '':
                continue
            new_mask1, res2 = valid_intersection(new_mask0, get_pe_mask(), i)
            if i % 10 == 0:
                pass
            res2.update(res1)
            if new_mask1 != '':
                valid_p_shifts[i] = (new_mask1, res2)
    return valid_p_shifts


def is_usable(s: str) -> int:
    count = 0
    for i in 'GHIKLMNOPQRSTUVWXYZ&~()*+-./,:;':  # J is excluded
        if i in s:
            count += 1
    for i in s[: len(s) // 2]:
        if i == '?':
            count += 1
    return count


for i in range(len(get_elf_mask()) // 2, len(get_elf_mask()) - 12):
    valid_p_shifts = check_symmetry(i)
    if valid_p_shifts:
        for offset, solutions in valid_p_shifts.items():
            elf, res = solutions
            reconstructed_placeholders = reconstruct_placeholders(res)
            if (
                # is_valid_placeholder_reconstruction(reconstructed_placeholders)
                (us := is_usable(elf))
                >= 20
                # and offset != 8
            ):
                print(
                    f'Symmetry found at axis {i}: score {len(elf)//2}\n'
                    f'  - offset {offset//2}\n'
                    f'  - elf: {elf}\n'
                    f'  - Resolutions: {res}\n'
                    f'  - Reconstructed: {reconstructed_placeholders}\n'
                    f'  - Usable bytes: {us//2}\n'
                    f'  - ELF header: {elf[:len(get_elf_mask())]}\n'
                    f'  - PE header: {elf[offset:offset+len(get_pe_mask())]}\n',
                )

if (1 - 1) != 0:
    print(check_symmetry(81))
#
# print(get_elf_mask())
# print(len(get_elf_mask()))
# print(len(get_pe_mask()))
# print(get_pe_mask())


elf01 = '7F454C46\
B259\
43\
B532\
0FC9\
B004\
CD80\
68\
02000300\
90\
96\
EB1E\
040032003200000000000000000001\
93CD80\
2000010020\
80CD93\
010000000000000000003200320004\
1EEB\
96\
90\
00030002\
68\
80CD\
04B0\
C90F\
32B5\
43\
59B2\
464C457F'

elf02 = """7F454C46\
80CD\
93\
96\
80CD\
C90F\
32B5\
04B0\
02000300\
68\
59\
B290\
2F0032003200000000000000000001\
0FEB43\
2000010020\
43EB0F\
01000000000000000000320032002F\
90B2\
59\
68\
00030002\
B004\
B532\
0FC9\
CD80\
96\
93\
CD80\
464C457F"""
elf04 = '7F454C4680CD939680CDC90F2CB504B0020003006853B2433B002C002C000000000000000000010020\
002000010000000000000000002C002C003B43B2536800030002B004B52C0FC9CD809693CD80464C457F'

elf81 = '7F454C46B25143B52C0FC9B004CD8068020003009693CD8004002c002C0000002C000000010020000\
0002000010000002C0000002C002c000480CD9396000300026880CD04B0C90F2CB54351B2464C457F'

# if valid_intersection(elf01, get_elf_mask(e_entry="04003200", e_phoff=int_to_hex_le(100 // 2, 4)))[0] != "":
#    print("Valid intersection elf01")
#
# if valid_intersection(elf01, get_palindrome(elf01, 89)) != ("", {}):
#    print("elf01 is symmetric at axis 89")
#
# if valid_intersection(elf02, get_elf_mask(e_entry="82003200", e_phoff=int_to_hex_le(100 // 2, 4)))[0] != "":
#    print("Valid intersection elf02")
#
# if valid_intersection(elf02, get_palindrome(elf02, 89)) != ("", {}):
#    print("elf02 is symmetric at axis 89")
#
# if valid_intersection(elf04, get_elf_mask(e_entry="3B002C00", e_phoff=int_to_hex_le(44 // 2, 4)))[0] != "":
#    print("Valid intersection elf04")
#
if valid_intersection(elf04, get_palindrome(elf04, 83)) != ('', {}):
    print('elf04 is symmetric at axis 83')
if valid_intersection(elf81, get_palindrome(elf81, 81)) != ('', {}):
    print('elf81 is symmetric at axis 81')

# print(elf01)
# print(elf02)
print(elf04)
print(elf81)
