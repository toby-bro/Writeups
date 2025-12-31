; quiny95.asm - 95 byte Quinindrome

BITS 32
    org     0x0D900000

    ; --- ELF Header (Overlaps with Phdr) ---
    db      0x7F, "ELF"         ; e_ident[0..3]
    dd      1                   ; p_type (PT_LOAD) / e_ident[4..7]
    dd      0                   ; p_offset         / e_ident[8..11]
    dd      $$                  ; p_vaddr          / e_ident[12..15]
    dw      2                   ; e_type (ET_EXEC) / p_paddr[0..1]
    dw      3                   ; e_machine (386)  / p_paddr[2..3]
_start:     ; mov edx, 95 | inc ebx | push es
    db      0xB2, 95, 0x43, 0x06              ; e_version        / p_filesz (Huge size)
    db      0x14, 0x00, 0x90, 0x0D ;_start ; adc al 0 | nop | or eax; e_entry / p_memsz
    dd      4                   ; e_phoff          / p_flags

    ; --- Code Slot 1 (Offsets 32-40) ---
    ; Available space: 9 bytes
    mov     cl, 0xD9            ; [32] ecx = 0x000000D9 
    shl     ecx, 20             ; [34] ecx = 0x0D900000 (Buffer Start)
    int     0x80                ; [37] syscall: write(1, 0x0D900000, 95)
    xchg    eax, esi            ; [38] eax = 0
    xchg    eax, ebx            ; [39] ebx = 0 (status) and eax = 1 (sys_exit)
    db      0xA9                ; [40] test eax, ...

    ; --- Header Fields (Offsets 42-45) ---
    ; These act as the immediate operand for TEST
    dw      32                  ; [42] e_phentsize
    dw      1                   ; [44] e_phnum

    int     0x80                ; [46] syscall: exit(0)

