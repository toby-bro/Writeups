
all: 
	nasm -f elf32 vm.asm -o vm.o
	ld -m elf_i386 vm.o -o vm_executable

clean:
	rm -f vm.o vm_executable
.PHONY: all clean