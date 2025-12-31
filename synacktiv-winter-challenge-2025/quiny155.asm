  ; quiny155.asm
  ; taken from https://www.muppetlabs.com/~breadbox/software/tiny/teensy.html
  
  BITS 32
  
                org     0x00010000
  
                db      0x7F, "ELF"             ; e_ident
                dd      1                                       ; p_type
                dd      0                                       ; p_offset
                dd      $$                                      ; p_vaddr 
                dw      2                       ; e_type        ; p_paddr
                dw      3                       ; e_machine
                dd      _start                  ; e_version     ; p_filesz
                dd      _start                  ; e_entry       ; p_memsz
                dd      4                       ; e_phoff       ; p_flags
                dd      0                       ; e_shoff       ; p_align 
                dd      0                       ; e_flags
                dw      52                      ; e_ehsize 
                dw      32                      ; e_phentsize 
                dw      1                       ; e_phnum 
                dw      0                       ; e_shentsize 
                dw      0                       ; e_shnum 
                dw      0                       ; e_shstrndx 
  
; ==========================================================
; THE CODE (The Payload)
; ==========================================================
_start:
    ; syscall: write(stdout, base_address, total_size)
    xor ebx, ebx           ; Clean ebx
    inc ebx                ; ebx = 1 (stdout file descriptor)
    
    mov ecx, $$            ; ecx = 0x00010000 (Start of file in memory)
    
    ; edx must match the total size in the header (0xB4)
    mov edx, 0x9b          ; edx = filesize*2 bytes
    
    xor eax, eax
    mov al,4               ; eax = 4 (sys_write)
    int 0x80               ; Call Kernel

    ; syscall: exit(0)
    xor ebx, ebx           ; ebx = 0 (exit code)
    xor eax, eax           ; eax = 1 (sys_exit)
    inc eax
    int 0x80               ; Call Kernel

; End of the "Half" file. 
; The rest will be the mirrored bytes appended by Python.
