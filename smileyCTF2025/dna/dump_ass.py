# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: main.py
# Bytecode version: 3.10.0rc2 (3439)
# Source timestamp: 2025-06-06 03:24:45 UTC (1749180285)

flag_test = '.;,;.{' + ''.join(chr(i) for i in range(48, 48 + 49)) + '}'

key_list = [111, 117, 105, 97]
EXTRACT_STRINGS = False

import marshal
import sys

from unluckyfuncs import *

unlucky_functions = [unlucky_1, unlucky_2, unlucky_3, unlucky_4]

s = []
m = {}
nm = {'A': 0, 'T': 1, 'G': 2, 'C': 3}
unlucky = [
    b'\x8coooooooooooonooolooo,ooo\x9cSooo\x06o\x12o\x1bo\x0bnvo\x13o\x0bmSo\x1bo\x0blvo\x13o\x0bnSo\x1bo\x0bkvo\x13o\x0blSo\x1bo\x0bmvo\x13o\x0bkSo\x13o\x0eo\x0bo<oFj!\xb5n;\xb5n.\xb5n(\xb5n,\xc6n\xb5m\x01\x02\xc6n\xb5l\x1b\x02\x1f\xc6o\x1deooo\x95fS\x1a\x01\x03\x1a\x0c\x04\x16Q\xb5h\x1a\x01\x03\x1a\x0c\x04\x16booo\x9ccoookmcncncncngn',
    b'\x96uuuuuuuuuuuuruuu}uuu6uuu\x86\x11uuu\x11t\x08u\x11w\x08t\x11v\x08w\x11q\x11p\xf1u\tu1u\xf6t\x08v\tu\tt\tw\x13v1u(n\x08q\x01u\x01t\x01w\xd5v\xd4u\xf6t\xf6t1u(e)w\x08p\x08s\tv\tspulu\x01w\tq\tpluluMuvuIu\x04i\x04g\tv\x14w\x11u&u\\s;\xafq426!\xafq!642\xafq6!24\x16tuuuuuuuuuuuwuuusuuu&uuu\x86ouuu\x1cu\tu(|\x08t\tt\x01u\x01t\xd5w\xd4u\xf6t\xe6w\x04w&u\\u\xdcv\xafv\x06\x00\x18\xafw\x1b\x18\xafs\x03\x14\x19\x00\x10\x06\xdcw\xafw[E\xaft\x16\xdcu\x07xuuu\x8f|I\x00\x1b\x19\x00\x16\x1e\x0cK\xafr\x00\x1b\x19\x00\x16\x1e\x0cnuuu\x86wuuuou\x8fh\x00\x1b\x19\x00\x16\x1e\x0c*G[I\x19\x1a\x16\x14\x19\x06K[I\x11\x1c\x16\x01\x16\x1a\x18\x05K\xdcq\xaf|\x10\x1b\x00\x18\x10\x07\x14\x01\x10\xafs\x06\x1a\x07\x01\x10\x11\x07}uuu\xafq\x1e\x10\x0c\x06\xdcr\xafw\x06D\xafw\x06G\xafw\x06F\xafv\x01\x18\x05\xaft\x06\xaft\x1c\x07yuuu\x07xuuu\x07xuuu\x07{uuu\x07zuuucuuu\x86guuuqwqtqt{t{tmtotw\x8a}w',
    b"\x8aiiiiiiiiiiiihiiiniiijiii\x9a/iii\x1di\rh\xeah\xe0i\xe1i\xc9h\x1di\rk\xeah\xc9k\rj\rm\xedi\x1dj\xc9m\xc8i\xc8k\xc8hhi.i\xeei\x0fh\rl\ro\xeda\ro\x1dl\xeaj\x14i\x15i\x1dj\xeah\x08j\ri:i@n'\xb3o\x1b\x08\x07\r\x06\x04\xb3`\x0f\x1c\x07\n\x1d\x06\x06\x05\x1a\nkiiiiiiiiiiikiiikiii:iii\x9aaiii\x15i\x15h(i:i@h'\xc0i\xc0k\xb3h\x11\xb3h\x10\x1bliii\x1bliii\x93`U\x1c\x07\x05\x1c\n\x02\x10W\xb3n\x1c\x07\x05\x1c\n\x02\x10Miii\x9akiiiai\x93r\x1c\x07\x05\x1c\n\x02\x106ZGU\x05\x06\n\x08\x05\x1aWGU\x05\x08\x04\x0b\r\x08W\niiiiiiiiiiiiiiiijiiiiiii\x9aCiii\x0ci3h\ri3k\xeei\xeeh\x0fk\rh\rk\xeda3j\xeei\x0fh\rj\rm\xeda3m\xeeimi3l:i@l\x93s\x1c\x07\x05\x1c\n\x02\x106ZGU\x05\x06\n\x08\x05\x1aWG\x1c\x07\x05\x1c\n\x02\x10\nkiiiiiiiiiiimiiiliiiziii\x9a-iii\x1di\xeai\xc9h\x15h\xc8hhi\x1dk\rh\xeah\x14k\xe1h\xc9j\x15k\xc8hhi\x1dm\rk\xeah-i4e\x14j\x15h\x15k\x15jpipi\x15i\rh\x15jpiUi\x18z\ri:i@j'\xb3m(*.=\x80miii\xc0l\xb3l\x1a\x1c\x19\x0c\x1b\xb3a66\x00\x07\x00\x1d66\xb3m\x05\x00\x1a\x1d\xb3n\x1a\x01\x1c\x0f\x0f\x05\x0c\xb3l\x1b\x08\x07\x0e\x0c\xc0m\xb3m\x1a\x0c\x05\x0f\xb3n\x04\x08\x19\x19\x00\x07\x0e\xb3m\x02\x0c\x10\x1a\xb3h\x00\xc0k\xb3`66\n\x05\x08\x1a\x1a66\xb3h\x1b\x1bliii\x1b`iii\x1bciiiOiii\x9aeiiiehahcheh\x7fhm\x96\x93J\x1c\x07\x05\x1c\n\x02\x106ZGU\x05\x06\n\x08\x05\x1aWG\x1c\x07\x05\x1c\n\x02\x10G66\x00\x07\x00\x1d66\nkiiiiiiiiiiiliiiliiiziii\x9a;iii\x1di\rh\xeah\x14k\x1di\rk\xeah\x14j`i\x15k\xc9h\rm\xc8h\x14m\x1dk\xeei\x0fh\rl\ro\xeda\x15j\xc9j\x15m\xc8h\xc9m\xc8i\ri\rn\xeckpi-i\xeah\xeah\x1bA\x1dl\xeai\xc9o\xe1i\xc8h:i\x18`@a'\x1bkiii\xb3n\x01\x08\x1a\x01\x05\x00\x0b=\x80Iiii\nhiiiiiiiiiiikiiimiiiZiii\x9auiii\xe8i\x15i4`\x14h\x15h\x1di\xe1i\xeah\x02k?ihi\x18k\ri:i@h'\xc0h\xb3j\x06\x1b\r\xc0k\xb3kGY\x1bniii\xc0h\xb3j\x02\x0c\x10\x1bliii\x1b`iii\x1bciii[iii\x9amiiik\xe9si\x93P\x1c\x07\x05\x1c\n\x02\x106ZGU\x05\x06\n\x08\x05\x1aWG\x1c\x07\x05\x1c\n\x02\x10G66\x0e\x0c\x1d\x00\x1d\x0c\x0466GU\x05\x06\n\x08\x05\x1aWGU\x0e\x0c\x07\x0c\x11\x19\x1bW\x80hiii\xc0n\xb3c66\x00\x04\x19\x06\x1b\x1d66\xb3`\x1b\x08\x07\r\x0b\x10\x1d\x0c\x1a\xb3j\x08\x05\x05\xb3o\x1a\x01\x08[\\_\xb3o\r\x00\x0e\x0c\x1a\x1d\x1bziii\xb3b66\x0e\x0c\x1d\x00\x1d\x0c\x0466\xc0l\x1bpiii\x1bBiii\xb3m\x01\x05\x00\x0b\xb3m\x1b\x05\x00\x0b\xb3h\x0b\xc0h\x1bwiii\x1bCiii\x1b`iii\x1bciiiDiii\x9agiiiahahkhchAhehk\x94\x93O\x1c\x07\x05\x1c\n\x02\x106ZGU\x05\x06\n\x08\x05\x1aWG\x1c\x07\x05\x1c\n\x02\x10G66\x0e\x0c\x1d\x00\x1d\x0c\x0466\xc0o\xb3a66\x07\x08\x04\x0c66\xb3c66\x04\x06\r\x1c\x05\x0c66\xb3e66\x18\x1c\x08\x05\x07\x08\x04\x0c66\x1b}iii\x1b\\iii\xb3d66\n\x05\x08\x1a\x1a\n\x0c\x05\x0566\x1bliii\xc0h\x1bviii\x1bSiii\x1b`iii\x1bciiiLiii\x9aoiiiaigh}n\x1bciii\xc0o\x1bYiii\xb3m\x1a\x0c\x0c\r\xb3o\x1b\x0c\r\x1c\n\x0c\xb3k\x07\x04\xb3o\x1f\x08\x05\x1c\x0c\x1a\xb3m\r\x00\n\x1d\xc0h\x1bciii\x1bliii\x1b+iii\x1b`iii\x1bciiiHiii\x9aaiiiakwh}hey",
    b'\x82aaaaaaaaaaaacaaagaaa"aaa\x92]aaa&a\x05`\x05c\xe5a\x05c\x15a\xe2b\x1ca&a\x05b\x05e\xe5a\x05e\x15`\x1da\x05d\xece\x1c`\x15c\x05g\x15`\x15b\xe2`\xfaa\x05f\xfcb\xe2``a\x05a2aHi/\x02aaaaaaaaaaaaaaaabaaaaaaa\x92Iaaa\x04a;`\x05a;c\xe6a\x07`\x05`\x05c\xe5i;b\xe6a\x07`\x05b\x05e\xe5i;e\xe6aea;d2aHd\x9bt\x14\x0f\r\x14\x02\n\x18>UO]\r\x0e\x02\x00\r\x12_O,,\x02eaaaaaaaaaaaeaaagaaaraaa\x92saaa\x15a\xe2a\xc1`\x1da\x1d`\x1dc\x1db\xc0e2aH`/\xc8c\xbbd\x12\x14\x11\x04\x13\xbbf>>\x0f\x04\x16>>\xc8e\xbbb\x02\r\x12\xbbe\x0f\x00\x0c\x04\xbbd\x03\x00\x12\x04\x12\xbbb\x05\x02\x15\xc8`\xbbh>>\x02\r\x00\x12\x12>>\xc8a\x9bh]\x14\x0f\r\x14\x02\n\x18_\xbbf\x14\x0f\r\x14\x02\n\x18Zaaa\x92caaas`\x9b|\x14\x0f\r\x14\x02\n\x18>UO]\r\x0e\x02\x00\r\x12_O,,O>>\x0f\x04\x16>>\x02`aaaaaaaaaaafaaadaaa~aaa\x92\x05aaa\x15a\xe2a\x0b`\x1d`\x08a\x1dc\xc5`\xef`\x1cb\x15c\x1db\xc1b\xc0a\xe2`\x1ce\x1de\x05a\x05a\x05`\xe4bxa\x1de\x05c\x05a\x05`\xe4bxava\x1ce\x15e\x15d\x1db\xc1g\xc0a\xe2`\xe2`%a<k=c\x1cd\x1cg\x1de\x1ddxa\x1db\x1dg]a\x10D\x1db2aHb/\x88caaa\x88`aaa\xc8f\x13gaaa\xbbi>>\x02\x00\r\r>>\xbbe\r\x08\x12\x15\xbbg\x17\x00\r\x14\x04\x12\xbbh\x04\x0f\x14\x0c\x04\x13\x00\x15\x04\xbbg\x12\x0e\x13\x15\x04\x05\xbbe\n\x04\x18\x12\xc8f\x13haaa\xbbe\x00\x13\x06\x12\xbbg\n\x16\x00\x13\x06\x12\xbbi\x08\x0f\x12\x15\x00\x0f\x02\x04\xbbe\x17\x00\r\x12\xbb`\x08\xbb`\n\x13laaa\x13naaa\x13qaaa\x13paaa_aaa\x92maaas`m`}`y`o`e`\x9b\x7f\x14\x0f\r\x14\x02\n\x18>UO]\r\x0e\x02\x00\r\x12_O,,O>>\x02\x00\r\r>>\xc8g\xbbi>>\x0f\x00\x0c\x04>>\xbbk>>\x0c\x0e\x05\x14\r\x04>>\xbbm>>\x10\x14\x00\r\x0f\x00\x0c\x04>>\x13faaa\x13yaaa\xbbl>>\x02\r\x00\x12\x12\x02\x04\r\r>>\x13naaa\x13naaa\x13laaa\x13qaaa\x13paaa[aaa\x92gaaaiam`ub\xbbc,,\x02aaaaaaaaaaaaaaaa`aaa!aaa\x92maaa\x04a;`\x05a;c\x05`2aHc\x9bt\x14\x0f\r\x14\x02\n\x18>UO]\r\x0e\x02\x00\r\x12_O,%/\xc8b\x13Iaaa\x13Haaa\x13Kaaa\x13naaa\x13naaa\x13naaa\x13qaaa\x13paaa\'aaa\x92eaaaiae`\xbbc,%\xc8`\xbbh\x0c\x04\x15\x00\x02\r\x00\x12\x12\x9b@\x06\r\x0e\x03\x00\r\x12IH:F\x0f\x14\x02\r\x04\x0e\x15\x08\x05\x04>\x0c\x00\x11F<A\\A,%I\x9b`H\xc8e\xbbe\x15\x18\x11\x04\xbbe\x05\x08\x02\x15\xbbe\x04\x19\x04\x02\xbbc\x0f\x0c\xc8c\x13Laaa\x13Saaa\x13naaa\x13naaa\x13qaaa\x13paaaVaaa\x92gaaaqbumyb',
]
trans = lambda s: sum((nm[c] << 2 * i for i, c in enumerate(s)))

# Assembly dump setup
if len(sys.argv) != 2:
    print(f'Usage: {sys.argv[0]} <dna_file>')
    sys.exit(1)

code = open(sys.argv[1]).read()
asm_file = sys.argv[1].replace('.dna', '.asm')

# Calculate flag for assembly generation
flag = flag_test.encode()
if len(flag) != 56:
    exit('WRONG!')
if flag[:6] != b'.;,;.{':
    exit('WRONG!')
if flag[(-1)] != 125:
    exit('WRONG!')
flag_content = flag[6:(-1)]

# Open assembly file for writing
asm_f = open(asm_file, 'w')
asm_f.write(f"; Assembly dump of {sys.argv[1]}\n")
asm_f.write("; Generated by dump_ass.py\n")
asm_f.write("; DNA VM to x86-like assembly translation\n")
asm_f.write(";\n")
asm_f.write(f"; Code length: {len(code)} DNA bases\n")
asm_f.write("; Register mapping: A=0, T=1, G=2, C=3\n")
asm_f.write("; Memory layout: Flag at addresses 640-689 (50 bytes)\n")
asm_f.write(f"; Flag content: {flag_content.hex()}\n")
asm_f.write(";\n\n")

# Write data section first
asm_f.write("section .data\n")
asm_f.write("    mem: times 8192 db 0         ; VM memory space (1000 bytes)\n")
asm_f.write("    \n")
asm_f.write("    ; Flag initialization data\n")
asm_f.write("    flag_data: db ")
for i, byte_val in enumerate(flag_content):
    if i > 0:
        asm_f.write(", ")
    asm_f.write(f"{byte_val}")
asm_f.write(f"  ; {len(flag_content)} bytes\n")
asm_f.write("    flag_len: equ $ - flag_data\n")
asm_f.write("\n")

asm_f.write("section .bss\n")
asm_f.write("    stack: resb 1000             ; VM stack space\n")
asm_f.write("    stack_ptr: resd 1            ; Stack pointer\n")
asm_f.write("\n")

asm_f.write("section .text\n")
asm_f.write("global _start\n\n")
asm_f.write("_start:\n")
asm_f.write("    ; Initialize memory with flag data at offset 640\n")
asm_f.write("    mov esi, flag_data           ; source: flag data\n")
asm_f.write("    mov edi, mem + 640           ; destination: mem[640]\n")
asm_f.write("    mov ecx, flag_len            ; count: flag length\n")
asm_f.write("    rep movsb                    ; copy flag to memory\n")
asm_f.write("    \n")
asm_f.write("    ; Initialize stack pointer\n")
asm_f.write("    mov dword [stack_ptr], 0     ; stack starts empty\n")
asm_f.write("    \n")
asm_f.write("    ; Start VM execution\n")


def write_asm(pc: int, opcode: int, operand: int):
    """Write assembly instruction to file"""
    asm_f.write(f"addr_{pc:05d}:    ; PC={pc}, Opcode={opcode}\n")

    if opcode == 0:  # push immediate
        asm_f.write(f"    ; Push immediate {operand}\n")
        asm_f.write(f"    mov     eax, {operand}\n")
        asm_f.write("    call    vm_push\n")
    elif opcode == 1:  # pop
        asm_f.write("    ; Pop and discard \n")
        asm_f.write("    call    vm_pop\n")
    elif opcode == 2:  # load from memory
        asm_f.write(f"    ; Load from memory[{operand}]\n")
        asm_f.write(f"    mov     eax, [mem+{operand}]\n")
        asm_f.write("    call    vm_push\n")
    elif opcode == 3:  # store to memory
        asm_f.write(f"    ; Store to memory[{operand}]\n")
        asm_f.write("    call    vm_pop\n")
        asm_f.write(f"    mov     [mem+{operand}], eax\n")
    elif opcode == 4:  # add
        asm_f.write("    ; Add\n")
        asm_f.write("    call    vm_pop               ; get first operand\n")
        asm_f.write("    mov     ebx, eax\n")
        asm_f.write("    call    vm_pop               ; get second operand\n")
        asm_f.write("    add     eax, ebx\n")
        asm_f.write("    call    vm_push\n")
    elif opcode == 5:  # subtract
        asm_f.write("    ; Subtract \n")
        asm_f.write("    call    vm_pop               ; get first operand (top)\n")
        asm_f.write("    mov     ebx, eax\n")
        asm_f.write("    call    vm_pop               ; get second operand\n")
        asm_f.write("    sub     eax, ebx             ; second - first\n")
        asm_f.write("    call    vm_push\n")
    elif opcode == 6:  # multiply
        asm_f.write("    ; Multiply\n")
        asm_f.write("    call    vm_pop\n")
        asm_f.write("    mov     ebx, eax\n")
        asm_f.write("    call    vm_pop\n")
        asm_f.write("    imul    eax, ebx\n")
        asm_f.write("    call    vm_push\n")
    elif opcode == 7:  # modulo
        asm_f.write("    ; Modulo\n")
        asm_f.write("    call    vm_pop               ; get divisor\n")
        asm_f.write("    mov     ebx, eax\n")
        asm_f.write("    call    vm_pop               ; get dividend\n")
        asm_f.write("    xor     edx, edx             ; clear edx\n")
        asm_f.write("    div     ebx                  ; eax = eax / ebx, edx = eax % ebx\n")
        asm_f.write("    mov     eax, edx             ; result is remainder\n")
        asm_f.write("    call    vm_push\n")
    elif opcode == 8:  # equals
        asm_f.write("    ; Compare equal\n")
        asm_f.write("    call    vm_pop\n")
        asm_f.write("    mov     ebx, eax\n")
        asm_f.write("    call    vm_pop\n")
        asm_f.write("    cmp     eax, ebx\n")
        asm_f.write("    mov     eax, 0\n")
        asm_f.write("    sete    al                   ; set AL to 1 if equal\n")
        asm_f.write("    call    vm_push\n")
    elif opcode == 9:  # unconditional jump
        asm_f.write(f"    ; Jump to PC {operand}\n")
        asm_f.write(f"    jmp     addr_{operand:05d}\n")
    elif opcode == 10:  # jump-if-true
        asm_f.write(f"    ; Jump if true to PC {operand} \n")
        asm_f.write("    call    vm_pop\n")
        asm_f.write("    cmp     eax, 1\n")
        asm_f.write(f"    je      addr_{operand:05d}\n")
    elif opcode == 11:  # jump-if-false
        asm_f.write(f"    ; Jump if false to PC {operand}\n")
        asm_f.write("    call    vm_pop\n")
        asm_f.write("    cmp     eax, 1\n")
        asm_f.write(f"    jne     addr_{operand:05d}\n")
    elif opcode == 12:  # output char
        asm_f.write("    ; Output character \n")
        asm_f.write("    call    vm_pop\n")
        asm_f.write("    call    putchar\n")
    elif opcode == 13:  # dynamic code exec
        asm_f.write("    ; Dynamic code execution \n")
        asm_f.write("    call    vm_pop               ; discard key value\n")
        asm_f.write("    call    exec_unlucky_func\n")
    elif opcode == 14:  # swap named registers
        asm_f.write("    ; Swap named registers \n")
        asm_f.write("    call    vm_pop\n")
        asm_f.write("    mov     ebx, eax\n")
        asm_f.write("    call    vm_pop\n")
        asm_f.write("    call    swap_registers\n")
    elif opcode == 15:  # halt
        asm_f.write("    ; Halt \n")
        asm_f.write("    jmp     exit\n")
    else:
        asm_f.write(f"    ; ERROR: Unknown opcode {opcode} \n")

    asm_f.write("\n")


flag = flag_test.encode()
if len(flag) != 56:
    exit('WRONG!')
if flag[:6] != b'.;,;.{':
    exit('WRONG!')
if flag[(-1)] != 125:
    exit('WRONG!')
flag = flag[6:(-1)]
for i in range(len(flag)):
    m[640 + i] = flag[i]
pc = 0
cycles = 0


while pc < len(code):
    cycles += 1
    # decode opcode and operand
    pri = trans(code[pc : pc + 2])
    pro = trans(code[pc + 2 : pc + 12])

    write_asm(pc, pri, pro)

    match pri:
        case 0:
            # push immediate
            s.append(pro)
            pc += 12

        case 1:
            # pop
            if not s:
                raise Exception('Stack underflow')
            s.pop()
            pc += 2

        case 2:
            # load from memory
            if pro not in m:
                raise Exception(f'Uninitialized memory access at {pro}')
            s.append(m[pro])
            pc += 12

        case 3:
            # store to memory
            if not s:
                raise Exception('Stack underflow')
            m[pro] = s.pop()
            pc += 12

        case 4:
            # add
            if len(s) < 2:
                raise Exception('Stack underflow')
            a, b = s.pop(), s.pop()
            s.append(a + b)
            pc += 2

        case 5:
            # subtract
            if len(s) < 2:
                raise Exception('Stack underflow')
            a, b = s.pop(), s.pop()
            s.append(b - a)
            pc += 2

        case 6:
            # multiply
            if len(s) < 2:
                raise Exception('Stack underflow')
            a, b = s.pop(), s.pop()
            s.append(a * b)
            pc += 2

        case 7:
            # modulo
            if len(s) < 2:
                raise Exception('Stack underflow')
            a, b = s.pop(), s.pop()
            if a == 0:
                raise Exception('Division by zero')
            s.append(b % a)
            pc += 2

        case 8:
            # equals
            if len(s) < 2:
                raise Exception('Stack underflow')
            a, b = s.pop(), s.pop()
            s.append(1 if a == b else 0)
            pc += 2

        case 9:
            # unconditional jump
            pc = pro

        case 10:
            # jump-if-true
            if not s:
                raise Exception('Stack underflow')
            if s.pop() == 1:
                pc = pro
            else:
                pc += 12

        case 11:
            # jump-if-false
            if not s:
                raise Exception('Stack underflow')
            if s.pop() != 1:
                pc = pro
            else:
                pc += 12

        case 12:
            # output char
            # print(
            #    f'\nOutputting character at PC {pc} with pri {pri}, pro {pro} ',
            #    end='',
            # )
            # This is the final 'WRONG!' printing function
            if not s:
                raise Exception('Stack underflow')
            sys.stdout.write(chr(s.pop()))
            pc += 2

        case 13:
            # dynamic code exec
            # print(cycles, s)
            if not s:
                raise Exception('Stack underflow')
            key_doncare = s.pop()
            key = key_list.pop(0)

            def f():
                return

            bytecode = bytes(b ^ key for b in unlucky.pop(0))
            f.__code__ = marshal.loads(bytecode)
            f()
            print(f"[{len(unlucky_functions) - len(unlucky)}] Key used: {key}")
            # unlucky_functions.pop(0)()

            pc += 2

        case 14:
            # swap named registers
            if len(s) < 2:
                raise Exception('Stack underflow')
            a, b = s.pop(), s.pop()
            if a not in nm or b not in nm:
                raise Exception('Invalid register names')
            print(f'Swapping registers {a} and {b}')
            nm[a], nm[b] = nm[b], nm[a]
            pc += 2

        case 15:
            # halt
            break

        case _:
            raise Exception(f'Unknown opcode {pri} at position {pc}')

# Close assembly file with helper functions
asm_f.write("\n; Helper functions\n")
asm_f.write("vm_push:\n")
asm_f.write("    ; Push EAX onto VM stack\n")
asm_f.write("    mov     ebx, [stack_ptr]     ; get current stack pointer\n")
asm_f.write("    mov     [stack + ebx*4], eax ; store value\n")
asm_f.write("    inc     ebx                  ; increment stack pointer\n")
asm_f.write("    mov     [stack_ptr], ebx     ; save new stack pointer\n")
asm_f.write("    ret\n")
asm_f.write("\n")
asm_f.write("vm_pop:\n")
asm_f.write("    ; Pop from VM stack into EAX\n")
asm_f.write("    mov     ebx, [stack_ptr]     ; get current stack pointer\n")
asm_f.write("    dec     ebx                  ; decrement stack pointer\n")
asm_f.write("    mov     [stack_ptr], ebx     ; save new stack pointer\n")
asm_f.write("    mov     eax, [stack + ebx*4] ; load value\n")
asm_f.write("    ret\n")
asm_f.write("\n")
asm_f.write("putchar:\n")
asm_f.write("    ; Print character in EAX to stdout\n")
asm_f.write("    push    eax                  ; save character\n")
asm_f.write("    mov     eax, 4               ; sys_write\n")
asm_f.write("    mov     ebx, 1               ; stdout\n")
asm_f.write("    mov     ecx, esp             ; pointer to character on stack\n")
asm_f.write("    mov     edx, 1               ; length = 1\n")
asm_f.write("    int     0x80                 ; syscall\n")
asm_f.write("    pop     eax                  ; restore stack\n")
asm_f.write("    ret\n")
asm_f.write("\n")
asm_f.write("exec_unlucky_func:\n")
asm_f.write("    ; Execute dynamic code (placeholder)\n")
asm_f.write("    ret\n")
asm_f.write("\n")
asm_f.write("swap_registers:\n")
asm_f.write("    ; Swap DNA register mappings (placeholder)\n")
asm_f.write("    ret\n")
asm_f.write("\n")
asm_f.write("exit:\n")
asm_f.write("    ; Exit program\n")
asm_f.write("    mov     eax, 1               ; sys_exit\n")
asm_f.write("    mov     ebx, 0               ; exit status\n")
asm_f.write("    int     0x80                 ; syscall\n")
asm_f.close()

print(f"Assembly dump written to: {asm_file}")

if EXTRACT_STRINGS:
    # try to dump all the strings from the code
    string = ''
    for attempt in range(14):
        # for pc in range(69308 - 14 * 100, len(code), 14):
        for pc in range(0 + attempt, len(code), 14):
            pri = trans(code[pc : pc + 2])
            pro = trans(code[pc + 2 : pc + 12])
            if pro > 33 and pro < 125:
                string += chr(pro)
            elif pro == 0:
                string += ' '
            elif pro == 10:
                string += '\n'
            elif pro == 13:
                string += '\r'
            elif pro == 9:
                string += '\t'
            elif pro == 32:
                string += ' '
            elif len(string) > 2:
                print(f'attempt {attempt}, PC {pc} string : {string}')
                string = ''
            else:
                string = ''
        # sys.stdout.write(chr(pro))
