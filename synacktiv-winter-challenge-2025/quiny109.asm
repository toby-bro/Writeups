  ; quiny109.asm
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
_start:
    inc ebx                ; ebx = 1 (stdout file descriptor)
    mov ecx, $$            ; ecx = 0x00010000 (Start of file in memory)
    mov dl, 0x6d           ; edx = filesize*2 bytes
    jmp short _skip

                dw      32                      ; e_phentsize 
                dw      1                       ; e_phnum 
                ;dw      0                       ; e_shentsize 
                ;dw      0                       ; e_shnum 
                ;dw      0                       ; e_shstrndx 
  
_skip:
    
    mov al,4               ; eax = 4 (sys_write)
    
    ; xor eax, eax
    int 0x80               ; Call Kernel

    ; syscall: exit(0)
    dec ebx                ; ebx = 0 (exit code)
    mov al,1               ; eax = 1 (sys_exit)
    int 0x80               ; Call Kernel

; End of the "Half" file. 
; The rest will be the mirrored bytes appended by Python.

