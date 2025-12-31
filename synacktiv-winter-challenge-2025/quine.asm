bits 32
org 0x08048000  ; Standard load address for 32-bit Linux binaries

; ==========================================================
; ELF HEADER (Elf32_Ehdr) - 52 bytes
; ==========================================================
elf_header:
    db 0x7F, 'E', 'L', 'F' ; Magic Number
    db 1                   ; Class (1 = 32-bit)
    db 1                   ; Data (1 = Little Endian)
    db 1                   ; Version
    db 0                   ; OS ABI (System V)
    db 0, 0, 0, 0, 0, 0, 0, 0 ; Padding (8 bytes unused)

    dw 2                   ; e_type (2 = Executable)
    dw 3                   ; e_machine (3 = x86)
    dd 1                   ; e_version
    dd _start              ; e_entry (Address of code start)
    dd program_header - $$ ; e_phoff (Offset of Program Header)
    dd 0                   ; e_shoff (Section header - unused)
    dd 0                   ; e_flags
    dw 52                  ; e_ehsize (Size of this ELF header)
    dw 32                  ; e_phentsize (Size of Program Header)
    dw 1                   ; e_phnum (Number of Program Headers)
    dw 0                   ; e_shentsize (Unused)
    dw 0                   ; e_shnum (Unused)
    dw 0                   ; e_shstrndx (Unused)

; ==========================================================
; PROGRAM HEADER (Elf32_Phdr) - 32 bytes
; ==========================================================
program_header:
    dd 1                   ; p_type (1 = LOAD)
    dd 0                   ; p_offset (File offset 0)
    dd $$                  ; p_vaddr (Virtual address in memory)
    dd $$                  ; p_paddr (Physical address - ignored)
    
    ; IMPORTANT: This is the Total File Size (Head + Tail)
    ; We estimate the half is ~90 bytes, so total is 180 (0xB4).
    ; We will verify this exact number in Step 4.
    dd 0xB4                ; p_filesz 
    dd 0xB4                ; p_memsz 
    
    dd 7                   ; p_flags (Read | Write | Execute)
    dd 0x1000              ; p_align (Alignment)

; ==========================================================
; THE CODE (The Payload)
; ==========================================================
_start:
    ; syscall: write(stdout, base_address, total_size)
    xor ebx, ebx           ; Clean ebx
    inc ebx                ; ebx = 1 (stdout file descriptor)
    
    mov ecx, $$            ; ecx = 0x08048000 (Start of file in memory)
    
    ; edx must match the total size in the header (0xB4)
    mov edx, 0x71          ; edx = 180 bytes
    
    mov eax, 4             ; eax = 4 (sys_write)
    int 0x80               ; Call Kernel

    ; syscall: exit(0)
    xor ebx, ebx           ; ebx = 0 (exit code)
    mov eax, 1             ; eax = 1 (sys_exit)
    int 0x80               ; Call Kernel

; End of the "Half" file. 
; The rest will be the mirrored bytes appended by Python.
