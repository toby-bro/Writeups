; quiny99.asm - 99 byte Quinindrome

BITS 32
    org     0x10000000

    ; --- ELF Header (Overlaps with Phdr) ---
    db      0x7F, "ELF"         ; e_ident[0..3]
    dd      1                   ; p_type (PT_LOAD) / e_ident[4..7]
    dd      0                   ; p_offset         / e_ident[8..11]
    dd      $$                  ; p_vaddr          / e_ident[12..15]
    dw      2                   ; e_type (ET_EXEC) / p_paddr[0..1]
    dw      3                   ; e_machine (386)  / p_paddr[2..3]
_start:     ; inc ebx, inc ecx, jmp +08
    db      0x43, 0x41, 0xEB, 0x08              ; e_version        / p_filesz (Huge size)
    dd      _start              ; e_entry          / p_memsz
    dd      4                   ; e_phoff          / p_flags

    ; --- Code Slot 1 (Offsets 32-40) ---
    ; Available space: 9 bytes
    shl     ecx, 28             ; [34] ecx = 0x10000000 (Buffer Start)
    mov     dl, 99              ; [37] edx = Total Size (99)
    mov     al, 4               ; [39] eax = 4 (sys_write)
    int     0x80                ; [40] syscall: write(1, 0x10000000, 99)

    ; --- The Bridge (Offset 41) ---
    ; We need to skip offsets 42-45 which MUST contain specific header values.
    ; Opcode 0xA9 is "TEST EAX, imm32". 
    ; It consumes 4 bytes of data and preserves EAX
    db      0xA9                ; [41] TEST EAX, ...

    ; --- Header Fields (Offsets 42-45) ---
    ; These act as the immediate operand for TEST
    dw      32                  ; [42] e_phentsize
    dw      1                   ; [44] e_phnum

    ; --- Code Slot 2 (Offsets 46-52) ---
_payload:
    xchg    eax, esi
    xchg    eax, ebx
    int     0x80                ; [48] syscall: exit(0)

    ; End of half file. 

