#!/usr/bin/env python3
import struct
import sys
from enum import Enum


class ElfClass(Enum):
    ELFCLASS32 = 1
    ELFCLASS64 = 2


class ElfData(Enum):
    ELFDATA2LSB = 1  # Little-endian
    ELFDATA2MSB = 2  # Big-endian


class ElfOSABI(Enum):
    UNIX_SYSTEM_V = 0
    HP_UX = 1
    NETBSD = 2
    LINUX = 3
    GNU_HURD = 4
    SOLARIS = 6
    IBM_AIX = 7
    SGI_IRIX = 8
    FREEBSD = 9
    OPENBSD = 12
    OPENVMS = 13


class ElfType(Enum):
    ET_NONE = 0
    ET_REL = 1
    ET_EXEC = 2
    ET_DYN = 3
    ET_CORE = 4


class ElfMachine(Enum):
    EM_386 = 3
    EM_S390 = 22
    EM_ARM = 40
    EM_X86_64 = 62
    EM_AARCH64 = 183


class PhType(Enum):
    PT_NULL = 0
    PT_LOAD = 1
    PT_DYNAMIC = 2
    PT_INTERP = 3
    PT_NOTE = 4
    PT_SHLIB = 5
    PT_PHDR = 6
    PT_TLS = 7
    PT_GNU_EH_FRAME = 0x6474E550
    PT_GNU_STACK = 0x6474E551
    PT_GNU_RELRO = 0x6474E552


class ElfParser:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.data = b''
        self.ehdr: dict[str, int] = {}
        self.phdrs: list[dict[str, int]] = []
        self.endianness = '<'  # Default to little-endian

    def parse(self) -> bool:
        with open(self.filename, 'rb') as f:
            self.data = f.read()

        # Check magic number
        if len(self.data) < 4 or self.data[0:4] != b'\x7fELF':
            print('Error: Not a valid ELF file (magic number mismatch)')
            return False

        # Parse ELF header
        self.parse_ehdr()

        # Parse program headers
        self.parse_phdrs()

        return True

    def parse_ehdr(self) -> None:
        """Parse the ELF header"""
        # Pad with zeros if file is too small
        min_size = 52  # Minimum size for 32-bit ELF header
        if len(self.data) < min_size:
            self.data = self.data + b'\x00' * (min_size - len(self.data))

        # EI_CLASS (1 byte at offset 4)
        ei_class = self.data[4]
        self.ehdr['ei_class'] = ei_class
        is_64bit = ei_class == 2

        # EI_DATA (1 byte at offset 5) - endianness
        ei_data = self.data[5]
        self.ehdr['ei_data'] = ei_data
        # Treat 0 or 1 as little-endian (default), 2 as big-endian
        is_little_endian = ei_data != 2

        # Set endianness for struct
        endian = '<' if is_little_endian else '>'

        if is_64bit:
            # 64-bit ELF header
            # Pad more if needed for 64-bit
            min_size_64 = 64
            if len(self.data) < min_size_64:
                self.data = self.data + b'\x00' * (min_size_64 - len(self.data))

            fmt = endian + 'HHIQQQIHHHHHH'
            offset = 16
            unpacked = struct.unpack_from(fmt, self.data, offset)

            self.ehdr['e_type'] = unpacked[0]
            self.ehdr['e_machine'] = unpacked[1]
            self.ehdr['e_version'] = unpacked[2]
            self.ehdr['e_entry'] = unpacked[3]
            self.ehdr['e_phoff'] = unpacked[4]
            self.ehdr['e_shoff'] = unpacked[5]
            self.ehdr['e_flags'] = unpacked[6]
            self.ehdr['e_ehsize'] = unpacked[7]
            self.ehdr['e_phentsize'] = unpacked[8]
            self.ehdr['e_phnum'] = unpacked[9]
            self.ehdr['e_shentsize'] = unpacked[10]
            self.ehdr['e_shnum'] = unpacked[11]
            self.ehdr['e_shstrndx'] = unpacked[12]
        else:
            # 32-bit ELF header
            fmt = endian + 'HHIIIIIHHHHHH'
            offset = 16
            unpacked = struct.unpack_from(fmt, self.data, offset)

            self.ehdr['e_type'] = unpacked[0]
            self.ehdr['e_machine'] = unpacked[1]
            self.ehdr['e_version'] = unpacked[2]
            self.ehdr['e_entry'] = unpacked[3]
            self.ehdr['e_phoff'] = unpacked[4]
            self.ehdr['e_shoff'] = unpacked[5]
            self.ehdr['e_flags'] = unpacked[6]
            self.ehdr['e_ehsize'] = unpacked[7]
            self.ehdr['e_phentsize'] = unpacked[8]
            self.ehdr['e_phnum'] = unpacked[9]
            self.ehdr['e_shentsize'] = unpacked[10]
            self.ehdr['e_shnum'] = unpacked[11]
            self.ehdr['e_shstrndx'] = unpacked[12]

        # Store ELF info for use in parsing program headers
        self.ehdr['is_64bit'] = is_64bit
        self.ehdr['is_little_endian'] = is_little_endian
        self.endianness = endian

    def parse_phdrs(self) -> None:
        """Parse program headers"""
        phoff = self.ehdr['e_phoff']
        phentsize = self.ehdr['e_phentsize']
        phnum = self.ehdr['e_phnum']
        is_64bit = self.ehdr['is_64bit']
        endian = self.endianness

        file_size = len(self.data)

        # Check if we can read any data at the specified offset
        if phoff >= file_size:
            print(f'\nNote: Program header offset (0x{phoff:x}) is at or beyond file size ({file_size} bytes)')
            print('No program header data available to parse\n')
            return

        # Calculate how many bytes are available from phoff
        available_bytes = file_size - phoff

        if available_bytes < phnum * phentsize:
            print('\nNote: Limited data available at program header offset')
            print(f'  Offset: 0x{phoff:x}')
            print(f'  Available: {available_bytes} bytes')
            print(f'  Required for {phnum} headers: {phnum * phentsize} bytes')
            print(f'Will read whatever data exists at offset 0x{phoff:x}\n')

        # Parse as many program headers as we can with available data
        for i in range(phnum):
            offset = phoff + i * phentsize

            # Check if we have enough bytes for this header
            if offset >= file_size:
                break

            bytes_available = file_size - offset
            bytes_needed = phentsize if is_64bit else 32  # Actual struct size

            if bytes_available < bytes_needed:
                print(f'Program header {i} incomplete: only {bytes_available} of {bytes_needed} bytes available\n')
                break

            phdr = {}

            if is_64bit:
                # 64-bit program header (56 bytes)
                if bytes_available < 56:
                    break

                fmt = endian + 'IIQQQQQQ'
                unpacked = struct.unpack_from(fmt, self.data, offset)

                phdr['p_type'] = unpacked[0]
                phdr['p_flags'] = unpacked[1]
                phdr['p_offset'] = unpacked[2]
                phdr['p_vaddr'] = unpacked[3]
                phdr['p_paddr'] = unpacked[4]
                phdr['p_filesz'] = unpacked[5]
                phdr['p_memsz'] = unpacked[6]
                phdr['p_align'] = unpacked[7]
            else:
                # 32-bit program header (32 bytes)
                if bytes_available < 32:
                    break

                fmt = endian + 'IIIIIIII'
                unpacked = struct.unpack_from(fmt, self.data, offset)

                phdr['p_type'] = unpacked[0]
                phdr['p_offset'] = unpacked[1]
                phdr['p_vaddr'] = unpacked[2]
                phdr['p_paddr'] = unpacked[3]
                phdr['p_filesz'] = unpacked[4]
                phdr['p_memsz'] = unpacked[5]
                phdr['p_flags'] = unpacked[6]
                phdr['p_align'] = unpacked[7]

            self.phdrs.append(phdr)

    def print_ehdr(self) -> None:
        """Print ELF header information"""
        print('\n=== ELF HEADER ===\n')
        print(f'Magic Number:        {self.data[0:4].decode("ascii")}')

        ei_class = self.ehdr['ei_class']
        class_name = '64-bit' if ei_class == 2 else '32-bit' if ei_class == 1 else 'Unknown'
        print(f'EI_CLASS:            {ei_class} ({class_name})')

        ei_data = self.ehdr['ei_data']
        endian_name = 'Little-endian' if ei_data == 1 else 'Big-endian' if ei_data == 2 else 'Unknown'
        print(f'EI_DATA:             {ei_data} ({endian_name})')

        ei_version = self.data[6]
        print(f'EI_VERSION:          {ei_version}')

        ei_osabi = self.data[7]
        osabi_name = ElfOSABI(ei_osabi).name if ei_osabi in [e.value for e in ElfOSABI] else 'Unknown'
        print(f'EI_OSABI:            {ei_osabi} ({osabi_name})')

        ei_abiversion = self.data[8]
        print(f'EI_ABIVERSION:       {ei_abiversion}')

        e_type = self.ehdr['e_type']
        type_name = ElfType(e_type).name if e_type in [e.value for e in ElfType] else 'Unknown'
        print(f'e_type:              0x{e_type:04x} ({type_name})')

        e_machine = self.ehdr['e_machine']
        machine_name = ElfMachine(e_machine).name if e_machine in [e.value for e in ElfMachine] else 'Unknown'
        print(f'e_machine:           0x{e_machine:04x} ({machine_name})')

        print(f"e_version:           {self.ehdr['e_version']}")
        print(f"e_entry:             0x{self.ehdr['e_entry']:x}")

        # Explain entry point calculation
        print('\n  Entry point calculation:')
        print(f"    Virtual address where execution starts: 0x{self.ehdr['e_entry']:x}")
        for phdr in self.phdrs:
            vaddr = phdr['p_vaddr']
            memsz = phdr['p_memsz']
            offset = phdr['p_offset']

            # Page-align addresses (OS loads in 4096-byte pages)
            page_aligned_vaddr = (vaddr // 4096) * 4096
            page_offset = vaddr - page_aligned_vaddr

            if page_aligned_vaddr <= self.ehdr['e_entry'] < vaddr + memsz:
                # Calculate file offset accounting for page alignment
                file_offset = offset - page_offset + (self.ehdr['e_entry'] - page_aligned_vaddr)
                print(f'    This is in program header at vaddr 0x{vaddr:x}')
                print(f'    Note: Memory is page-aligned, so segment starts at 0x{page_aligned_vaddr:x}')
                print('    File offset = p_offset - page_offset + (e_entry - page_aligned_vaddr)')
                print(
                    f"                = 0x{offset:x} - 0x{page_offset:x} + (0x{self.ehdr['e_entry']:x} - 0x{page_aligned_vaddr:x})",  # noqa: E501
                )
                print(f'                = 0x{file_offset:x} (byte {file_offset} in file)')
                if 0 <= file_offset < len(self.data):
                    code_bytes = self.data[file_offset : min(file_offset + 6, len(self.data))]
                    hex_code = ''.join(f'{b:02X}' for b in code_bytes)
                    print(f'    Code at entry: {hex_code}')
                elif file_offset < 0:
                    print('    Warning: Entry point is before file start (calculated offset is negative)')
                break
        print()

        print(f"e_phoff:             {self.ehdr['e_phoff']} (0x{self.ehdr['e_phoff']:x})")
        print(f"e_shoff:             {self.ehdr['e_shoff']} (0x{self.ehdr['e_shoff']:x})")
        print(f"e_flags:             0x{self.ehdr['e_flags']:08x}")
        print(f"e_ehsize:            {self.ehdr['e_ehsize']} bytes")
        print(f"e_phentsize:         {self.ehdr['e_phentsize']} bytes")
        print(f"e_phnum:             {self.ehdr['e_phnum']}")
        print(f"e_shentsize:         {self.ehdr['e_shentsize']} bytes")
        print(f"e_shnum:             {self.ehdr['e_shnum']}")
        print(f"e_shstrndx:          {self.ehdr['e_shstrndx']}")

    def print_phdrs(self) -> None:
        """Print program header information"""
        print('\n=== PROGRAM HEADERS ===\n')
        if not self.phdrs:
            print('No program headers parsed (file may be malformed)\n')
            return

        for i, phdr in enumerate(self.phdrs):
            print(f'Program Header {i}:')

            p_type = phdr['p_type']
            type_name = PhType(p_type).name if p_type in [e.value for e in PhType] else f'Unknown(0x{p_type:x})'
            print(f'  p_type:      0x{p_type:08x} ({type_name})')

            print(f"  p_offset:    {phdr['p_offset']} (0x{phdr['p_offset']:x})")
            print(f"  p_vaddr:     0x{phdr['p_vaddr']:x}")
            print(f"  p_paddr:     0x{phdr['p_paddr']:x}")
            print(f"  p_filesz:    {phdr['p_filesz']} bytes (0x{phdr['p_filesz']:x})")
            print(f"  p_memsz:     {phdr['p_memsz']} bytes (0x{phdr['p_memsz']:x})")

            p_flags = phdr['p_flags']
            flags_str = ''
            flags_str += 'R' if p_flags & 4 else '-'
            flags_str += 'W' if p_flags & 2 else '-'
            flags_str += 'X' if p_flags & 1 else '-'
            print(f'  p_flags:     0x{p_flags:08x} ({flags_str})')

            print(f"  p_align:     {phdr['p_align']} bytes")

            # Show what gets loaded into memory
            print('\n  Memory mapping:')
            print(
                f"    File [0x{phdr['p_offset']:x}:0x{phdr['p_offset'] + phdr['p_filesz']:x}] -> Memory [0x{phdr['p_vaddr']:x}:0x{phdr['p_vaddr'] + phdr['p_memsz']:x}]",  # noqa: E501
            )

            # Show what's actually in the file at this offset
            if phdr['p_offset'] < len(self.data) and phdr['p_filesz'] > 0:
                available = min(phdr['p_filesz'], len(self.data) - phdr['p_offset'], 32)
                data_preview = self.data[phdr['p_offset'] : phdr['p_offset'] + available]
                hex_str = ' '.join(f'{b:02x}' for b in data_preview)
                if available < phdr['p_filesz']:
                    hex_str += ' ...'
                print(f'    File data preview: {hex_str}')

            print()

    def disassemble_at_entry(self, max_instructions: int = 20) -> None:  # noqa: C901
        """Simple x86 disassembler starting at entry point"""
        entry = self.ehdr['e_entry']

        # Find which program header contains the entry point
        code_data = None
        code_offset = None
        base_vaddr = None
        base_offset = None

        for phdr in self.phdrs:
            vaddr = phdr['p_vaddr']
            memsz = phdr['p_memsz']
            offset = phdr['p_offset']
            filesz = phdr['p_filesz']

            # Page-align addresses (OS loads in 4096-byte pages)
            page_aligned_vaddr = (vaddr // 4096) * 4096
            page_offset = vaddr - page_aligned_vaddr

            # The segment actually starts at the page boundary in memory
            # So addresses from page_aligned_vaddr to vaddr+memsz are valid
            if page_aligned_vaddr <= entry < vaddr + memsz:
                # Calculate file offset relative to the segment start
                # But need to account for page alignment
                code_offset = offset - page_offset + (entry - page_aligned_vaddr)

                # Make sure we're not going before file start
                if code_offset < 0:
                    continue

                base_vaddr = page_aligned_vaddr
                base_offset = offset - page_offset

                # Load data accounting for page alignment
                # Start from where the page-aligned segment begins in the file
                actual_start = max(0, offset - page_offset)
                end_offset = min(offset + filesz, len(self.data))

                if actual_start < len(self.data):
                    code_data = self.data[actual_start:end_offset]
                    break

        if code_data is None or code_offset is None or base_vaddr is None or base_offset is None:
            print(f'\nCannot disassemble: entry point 0x{entry:x} not found in file\n')
            return

        print(f'\n=== DISASSEMBLY AT ENTRY POINT (0x{entry:x}) ===\n')

        reg_names = ['eax', 'ecx', 'edx', 'ebx', 'esp', 'ebp', 'esi', 'edi']
        reg8_names = ['al', 'cl', 'dl', 'bl', 'ah', 'ch', 'dh', 'bh']

        # Start at entry point
        pc = code_offset - base_offset
        instruction_count = 0
        visited = set()  # Track visited addresses to avoid infinite loops

        def vaddr_to_offset(vaddr: int) -> int | None:
            """Convert virtual address to offset in code_data"""
            if base_vaddr <= vaddr < base_vaddr + len(code_data):
                return vaddr - base_vaddr
            return None

        while pc < len(code_data) and instruction_count < max_instructions:
            addr = base_vaddr + pc

            # Avoid infinite loops
            if addr in visited:
                print('  (loop detected, stopping)')
                break
            visited.add(addr)

            opcode = code_data[pc]

            # MOV reg32, imm32 (0xB8 + reg)
            if 0xB8 <= opcode <= 0xBF:
                if pc + 4 < len(code_data):
                    reg = opcode - 0xB8
                    imm = struct.unpack('<I', code_data[pc + 1 : pc + 5])[0]
                    print(f'  0x{addr:08x}: B8+{reg:x} {imm:08x}      mov {reg_names[reg]}, 0x{imm:x}')
                    pc += 5
                else:
                    break

            # XCHG eax, reg32 (0x90-0x97)
            elif 0x90 <= opcode <= 0x97:
                if opcode == 0x90:
                    print(f'  0x{addr:08x}: 90                nop')
                else:
                    reg = opcode - 0x90
                    print(f'  0x{addr:08x}: {opcode:02x}                xchg eax, {reg_names[reg]}')
                pc += 1

            # INT imm8 (0xCD)
            elif opcode == 0xCD:
                if pc + 1 < len(code_data):
                    int_num = code_data[pc + 1]
                    print(f'  0x{addr:08x}: CD {int_num:02x}             int 0x{int_num:x}')
                    pc += 2
                else:
                    break

            # JMP short (0xEB)
            elif opcode == 0xEB:
                if pc + 1 < len(code_data):
                    offset = struct.unpack('b', bytes([code_data[pc + 1]]))[0]
                    target = addr + 2 + offset
                    print(f'  0x{addr:08x}: EB {code_data[pc+1]:02x}             jmp short 0x{target:x} ({offset:+d})')
                    # Follow the jump
                    new_pc = vaddr_to_offset(target)
                    if new_pc is not None and 0 <= new_pc < len(code_data):
                        pc = new_pc
                    else:
                        print(f'  (jump target 0x{target:x} out of bounds)')
                        break
                else:
                    break

            # MOV r/m8, r8 (0x88)
            elif opcode == 0x88:
                if pc + 1 < len(code_data):
                    modrm = code_data[pc + 1]
                    mod = (modrm >> 6) & 3
                    reg = (modrm >> 3) & 7
                    rm = modrm & 7
                    if mod == 3:  # Register to register
                        print(f'  0x{addr:08x}: 88 {modrm:02x}             mov {reg8_names[rm]}, {reg8_names[reg]}')
                        pc += 2
                    else:
                        print(f'  0x{addr:08x}: 88 {modrm:02x}             mov [?], {reg8_names[reg]}')
                        pc += 2
                else:
                    break

            # MOV r/m32, r32 (0x89)
            elif opcode == 0x89:
                if pc + 1 < len(code_data):
                    modrm = code_data[pc + 1]
                    mod = (modrm >> 6) & 3
                    reg = (modrm >> 3) & 7
                    rm = modrm & 7
                    if mod == 3:  # Register to register
                        print(f'  0x{addr:08x}: 89 {modrm:02x}             mov {reg_names[rm]}, {reg_names[reg]}')
                        pc += 2
                    else:
                        print(f'  0x{addr:08x}: 89 {modrm:02x}             mov [?], {reg_names[reg]}')
                        pc += 2
                else:
                    break

            # MOV r32, r/m32 (0x8B)
            elif opcode == 0x8B:
                if pc + 1 < len(code_data):
                    modrm = code_data[pc + 1]
                    mod = (modrm >> 6) & 3
                    reg = (modrm >> 3) & 7
                    rm = modrm & 7
                    if mod == 3:  # Register to register
                        print(f'  0x{addr:08x}: 8B {modrm:02x}             mov {reg_names[reg]}, {reg_names[rm]}')
                        pc += 2
                    else:
                        print(f'  0x{addr:08x}: 8B {modrm:02x}             mov {reg_names[reg]}, [?]')
                        pc += 2
                else:
                    break

            # XCHG r/m32, r32 (0x87)
            elif opcode == 0x87:
                if pc + 1 < len(code_data):
                    modrm = code_data[pc + 1]
                    mod = (modrm >> 6) & 3
                    reg = (modrm >> 3) & 7
                    rm = modrm & 7
                    if mod == 3:  # Register to register
                        print(f'  0x{addr:08x}: 87 {modrm:02x}             xchg {reg_names[rm]}, {reg_names[reg]}')
                        pc += 2
                    else:
                        print(f'  0x{addr:08x}: 87 {modrm:02x}             xchg [?], {reg_names[reg]}')
                        pc += 2
                else:
                    break

            # INC reg32 (0x40-0x47)
            elif 0x40 <= opcode <= 0x47:
                reg = opcode - 0x40
                print(f'  0x{addr:08x}: {opcode:02x}                inc {reg_names[reg]}')
                pc += 1

            # DEC reg32 (0x48-0x4F)
            elif 0x48 <= opcode <= 0x4F:
                reg = opcode - 0x48
                print(f'  0x{addr:08x}: {opcode:02x}                dec {reg_names[reg]}')
                pc += 1

            # PUSH imm32 (0x68)
            elif opcode == 0x68:
                if pc + 4 < len(code_data):
                    imm = struct.unpack('<I', code_data[pc + 1 : pc + 5])[0]
                    print(f'  0x{addr:08x}: 68 {imm:08x}      push 0x{imm:x}')
                    pc += 5
                else:
                    break

            # MOV reg8, imm8 (0xB0-0xB7)
            elif 0xB0 <= opcode <= 0xB7:
                if pc + 1 < len(code_data):
                    reg = opcode - 0xB0
                    imm = code_data[pc + 1]
                    print(f'  0x{addr:08x}: {opcode:02x} {imm:02x}             mov {reg8_names[reg]}, 0x{imm:x}')
                    pc += 2
                else:
                    break

            # PUSH ES (0x06)
            elif opcode == 0x06:
                print(f'  0x{addr:08x}: 06                push es')
                pc += 1

            # ADC AL, imm8 (0x14)
            elif opcode == 0x14:
                if pc + 1 < len(code_data):
                    imm = code_data[pc + 1]
                    print(f'  0x{addr:08x}: 14 {imm:02x}             adc al, 0x{imm:x}')
                    pc += 2
                else:
                    break

            # LEAVE (0xC9)
            elif opcode == 0xC9:
                print(f'  0x{addr:08x}: C9                leave')
                pc += 1

            # Shift/Rotate r/m32, imm8 (0xC1)
            elif opcode == 0xC1:
                if pc + 2 < len(code_data):
                    modrm = code_data[pc + 1]
                    mod = (modrm >> 6) & 3
                    reg = (modrm >> 3) & 7
                    rm = modrm & 7
                    imm = code_data[pc + 2]

                    shift_ops = ['rol', 'ror', 'rcl', 'rcr', 'shl', 'shr', '?', 'sar']
                    op = shift_ops[reg]

                    if mod == 3:  # Register
                        print(f'  0x{addr:08x}: C1 {modrm:02x} {imm:02x}          {op} {reg_names[rm]}, {imm}')
                        pc += 3
                    else:
                        print(f'  0x{addr:08x}: C1 {modrm:02x} {imm:02x}          {op} [?], {imm}')
                        pc += 3
                else:
                    break

            # LOOPZ/LOOPE rel8 (0xE1)
            elif opcode == 0xE1:
                if pc + 1 < len(code_data):
                    offset = struct.unpack('b', bytes([code_data[pc + 1]]))[0]
                    target = addr + 2 + offset
                    print(f'  0x{addr:08x}: E1 {code_data[pc+1]:02x}             loopz 0x{target:x} ({offset:+d})')
                    pc += 2
                else:
                    break

            # OR EAX, imm32 (0x0D)
            elif opcode == 0x0D:
                if pc + 4 < len(code_data):
                    imm = struct.unpack('<I', code_data[pc + 1 : pc + 5])[0]
                    print(f'  0x{addr:08x}: 0D {imm:08x}      or eax, 0x{imm:x}')
                    pc += 5
                else:
                    break

            # TEST EAX, imm32 (0xA9)
            elif opcode == 0xA9:
                if pc + 4 < len(code_data):
                    imm = struct.unpack('<I', code_data[pc + 1 : pc + 5])[0]
                    print(f'  0x{addr:08x}: A9 {imm:08x}      test eax, 0x{imm:x}')
                    pc += 5
                else:
                    break

            # Two-byte instructions (0x0F prefix)
            elif opcode == 0x0F:
                if pc + 1 < len(code_data):
                    opcode2 = code_data[pc + 1]

                    # BSWAP reg32 (0x0F C8-CF)
                    if 0xC8 <= opcode2 <= 0xCF:
                        reg = opcode2 - 0xC8
                        print(f'  0x{addr:08x}: 0F {opcode2:02x}             bswap {reg_names[reg]}')
                        pc += 2

                    # MOVZX r32, r/m8 (0x0F B6)
                    elif opcode2 == 0xB6:
                        if pc + 2 < len(code_data):
                            modrm = code_data[pc + 2]
                            mod = (modrm >> 6) & 3
                            reg = (modrm >> 3) & 7
                            rm = modrm & 7
                            if mod == 3:
                                print(
                                    f'  0x{addr:08x}: 0F B6 {modrm:02x}          movzx {reg_names[reg]}, {reg8_names[rm]}',  # noqa: E501
                                )
                            else:
                                print(f'  0x{addr:08x}: 0F B6 {modrm:02x}          movzx {reg_names[reg]}, [?]')
                            pc += 3
                        else:
                            break

                    # MOVSX r32, r/m8 (0x0F BE)
                    elif opcode2 == 0xBE:
                        if pc + 2 < len(code_data):
                            modrm = code_data[pc + 2]
                            mod = (modrm >> 6) & 3
                            reg = (modrm >> 3) & 7
                            rm = modrm & 7
                            if mod == 3:
                                print(
                                    f'  0x{addr:08x}: 0F BE {modrm:02x}          movsx {reg_names[reg]}, {reg8_names[rm]}',  # noqa: E501
                                )
                            else:
                                print(f'  0x{addr:08x}: 0F BE {modrm:02x}          movsx {reg_names[reg]}, [?]')
                            pc += 3
                        else:
                            break

                    # IMUL r32, r/m32 (0x0F AF)
                    elif opcode2 == 0xAF:
                        if pc + 2 < len(code_data):
                            modrm = code_data[pc + 2]
                            mod = (modrm >> 6) & 3
                            reg = (modrm >> 3) & 7
                            rm = modrm & 7
                            if mod == 3:
                                print(
                                    f'  0x{addr:08x}: 0F AF {modrm:02x}          imul {reg_names[reg]}, {reg_names[rm]}',  # noqa: E501
                                )
                            else:
                                print(f'  0x{addr:08x}: 0F AF {modrm:02x}          imul {reg_names[reg]}, [?]')
                            pc += 3
                        else:
                            break

                    else:
                        print(f'  0x{addr:08x}: 0F {opcode2:02x}             <unknown 0F opcode>')
                        pc += 2
                else:
                    break

            # Unknown instruction
            else:
                print(f'  0x{addr:08x}: {opcode:02x}                <unknown>')
                pc += 1

            instruction_count += 1

        print()


def main() -> None:
    if len(sys.argv) == 1:
        sys.argv.append('quinpy81')

    if len(sys.argv) != 2:
        print('Usage: python3 elf_parser.py <elf_file>')
        sys.exit(1)

    filename = sys.argv[1]

    parser = ElfParser(filename)

    if not parser.parse():
        sys.exit(1)

    parser.print_ehdr()
    parser.print_phdrs()
    parser.disassemble_at_entry()


if __name__ == '__main__':
    main()
