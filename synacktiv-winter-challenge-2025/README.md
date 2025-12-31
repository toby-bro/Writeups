# [Synacktiv winter challenge 2025](https://www.synacktiv.com/publications/2025-winter-challenge-quinindrome)

## Introduction

The challenge was to write the *smallest* possible [ELF](https://en.wikipedia.org/wiki/Executable_and_Linkable_Format) that is at the same time

- a byte-wise palindrome
- a quine
- and whose exit code is 0.

If any of the `headers` purpose is unclear to you the `man elf` should provide an answer.

### Teensy ELF

This was my first challenge writing ELFs so this writeup will mostly follow the progression I did.

The first thing I did was look up other people writing small ELFs and I found this [article on muppetlabs](https://www.muppetlabs.com/~breadbox/software/tiny/teensy.html) which created a 45 bytes ELF.

In this we learn that most of the ELF headers and program headers are not even checked by the linux kernel, when loading the ELF (for instance `e_version` is supposed to hold the version of the ELF but there is only one so what is the point of checking it, moreover headers that concern the sections).
So we can write nonesense in most of them and the ELF will all the same be accepted and loaded and executed.

Lastly we see that writing a 32bit ELF is much smaller than a 64bit ELF because addresses such as `e_entry`... are only 32 bits. So we will go to a 32bit ELF for the rest of the challenge.

### Quine

To print the program's code we need to have a way to access it. We will use the fact that we can load it in a `PT_LOAD` segment that will put all the bytes of the program in memory, from the first to the last.

So in our `Elf_Phdr` we need to put `p_offset=0x0`, `p_type=PT_LOAD` to load the ELF from the first byte of the file at the position `p_vaddr`.

Then we need to perform the syscall (in assembly `int 0x80`) write (`eax=0x4` to say which syscall we want to perform) with the following arguments `ebx=0x1` to write to stdout, `ecx` must be set to the same value as `p_vaddr` to ask it to print starting from the first byte of the file, and `edx` must be the number of bytes we want to print.

To get the exit code to 0. We will also perform a syscall (`int 0x80`) with `eax=0x1` to say that we exit and `ebx=0x0` to set the return code to 0.

This gives us the following code

```asm
mov eax, 0x4
xor ebx, ebx
inc ebx
mov ecx, $$ ; the address of the beginning of the program
mov edx, ?? ; the length of the program / the number of bytes we want to print
int 0x80
xor ebx, ebx
xor eax, eax
inc eax
int 0x80
```

My first quine (not a palindrome and not optimised for space), with all the ELF headers and program headers is visible in the file [quine.asm](./quine.asm).

To assemble it and check it was a quine.

```sh
nasm -f bin quine.asm -o quine && chmod +x quine && ./quine > quine2 && diff quine quine2
```

### Palindrome

To get a byte wise palindrome I just generated the ELF that was a quine, turned it around added it into my initial quine and adjusted the length of the program in edx to output the whole program.

```py
with open("quiny", "rb") as f:
    data = f.read()

# Create the full palindrome: Data + Reverse(Data[:-1])
# The axis of symmetry is the last byte of the program so I do not include it in the reversed version
# I did not think about it straight away but I am introducing it here nevertheless
palindrome = data + data[:-1][::-1]

with open("quinindrome", "wb") as f:
    f.write(palindrome)

print(f"Created quinindrome! Size: {len(palindrome)} bytes")
```

### First attempt

To make a real first submission I simply copied what was suggested by muppetlabs (link above) changed his code by mine.
The first submission was thus [quiny155.asm](./quiny155.asm)

```sh
nasm -f bin quiny155.asm -o quiny && chmod +x quiny && ./quiny > quiny2 && wc -c quiny && xxd quiny2 && python mirror.py && chmod +x quinindrome && ./quinindrome > quinindrome2 && xxd quinindrome2 && diff quinindrome2 quinindrome && ./test.sh quinindrome
00000000: 7f45 4c46 0100 0000 0000 0000 0000 0100  .ELF............
00000010: 0200 0300 3400 0100 3400 0100 0400 0000  ....4...4.......
00000020: 0000 0000 0000 0000 3400 2000 0100 0000  ........4. .....
00000030: 0000 0000 31db 43b9 0000 0100 ba9b 0000  ....1.C.........
00000040: 0031 c0b0 04cd 8031 db31 c040 cd80 0000  .1.....1.1.@....
00000050: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000060: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000070: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000080: 0000 0000 0000 0000 0000 0000 0000 0000  ................
00000090: 0000 0000 0000 0000 0000 00              ...........
Created quinindrome! Size: 155 bytes
00000000: 7f45 4c46 0100 0000 0000 0000 0000 0100  .ELF............
00000010: 0200 0300 3400 0100 3400 0100 0400 0000  ....4...4.......
00000020: 0000 0000 0000 0000 3400 2000 0100 0000  ........4. .....
00000030: 0000 0000 31db 43b9 0000 0100 ba9b 0000  ....1.C.........
00000040: 0031 c0b0 04cd 8031 db31 c040 cd80 cd40  .1.....1.1.@...@
00000050: c031 db31 80cd 04b0 c031 0000 009b ba00  .1.1.....1......
00000060: 0100 00b9 43db 3100 0000 0000 0000 0100  ....C.1.........
00000070: 2000 3400 0000 0000 0000 0000 0000 0400   .4.............
00000080: 0100 3400 0100 3400 0300 0200 0100 0000  ..4...4.........
00000090: 0000 0000 0000 0146 4c45 7f              .......FLE.
[+] First check passed: binary is a byte-wise palindrome.
[+] Second check passed: binary is a true quine, its output matches itself.
[+] Both checks passed: your binary is a very nice quinindrome!
[+] Your score: 155
```

## Getting started

The first things I did was to reread the muppetlabs article to try and figure out what were all the lines of the headers which were important and which were not.
For the next steps I

- put code into `e_shoff` and `e_flags` as these values are not checked
- kept the `e_phentsize` and `e_phnum` these values are critical
- put code into `e_shentsize`, `e_shnum` and `e_shstrndx` as these values are useless at the end of the ELF header
- realized that all the registers (except esp) are initalized to 0. So no need to clean them with `xor`
- reduce the size of the instructions
  - most of the values could be loaded into `al`, `dl` instead of `eax` `edx`... as these instructions are shorter as the value they expect is one byte instead of 4.
  - use `inc` and `dec` which are one byte wide to vary between 0 and 1.
- make the symmetry on the last byte.
- use a `jmp short` to skip over the `e_phentisize` and `e_phnum`

This is the first submission I sent synacktiv with a score of 109. The assembly file is [quiny109.asm](./quiny109.asm)

```sh
nasm -f bin quiny109.asm -o quiny && chmod +x quiny && ./quiny > quiny2 && wc -c quiny && python mirror.py && chmod +x quinindrome && ./quinindrome > quinindrome2 && xxd quinindrome2 && diff quinindrome2 quinindrome && ./test.sh quinindrome
55 quiny
Created quinindrome! Size: 109 bytes
00000000: 7f45 4c46 0100 0000 0000 0000 0000 0100  .ELF............
00000010: 0200 0300 2000 0100 2000 0100 0400 0000  .... ... .......
00000020: 43b9 0000 0100 b26d eb04 2000 0100 b004  C......m.. .....
00000030: cd80 4bb0 01cd 80cd 01b0 4b80 cd04 b000  ..K.......K.....
00000040: 0100 2004 eb6d b200 0100 00b9 4300 0000  .. ..m......C...
00000050: 0400 0100 2000 0100 2000 0300 0200 0100  .... ... .......
00000060: 0000 0000 0000 0000 0146 4c45 7f         .........FLE.
[+] First check passed: binary is a byte-wise palindrome.
[+] Second check passed: binary is a true quine, its output matches itself.
[+] Both checks passed: your binary is a very nice quinindrome!
[+] Your score: 109
```

## Playing with `org` and `p_vaddr`

### Using all the non necessary headers and reducing code

At this moment I saw that `e_version/p_filesz` could be used to put code into it, the only rule being that we need `p_memsz > p_filesz` otherwise we are telling the kernel loading the ELF that the file is larger than the space in memory in which we want to put it.
As `p_memsz` is also `e_entry` which is `p_vaddr + 0x14 = org + 0x14` then it means we need to make this adress bigger. (but not to big so as not to go into the kernel reserved space). We must thus keep org below `0xC0000000`.

Even more interesting as we must load this adress into `ecx` if it is an easy adress such as `0x10000000` then instead of using `mov ecx, 0x10000000` which becomes in assembly `B9 0000 0010` which takes 5 bytes, we can load the value using `inc ecx` and `shl ecx, 28` which becomes `41 C1 E1 1C` which is one byte less !

To skip the `e_entry` and `e_phoff` I used a jump short.
But to jump over the `e_phentsize` and `e_phnum` I used a `A9` as this will `test eax, imm32` so it will consume 4 bytes after it without changing the value of `eax` (only the sign flag, zero flag...) and this consumes one byte less than a jump short.

This gives us a new file of 101 bytes: [quiny101.asm](./quiny101.asm) assembled with the same command as always.

```sh
nasm -f bin quiny101.asm -o quiny && chmod +x quiny && ./quiny > quiny2 && wc -c quiny && python mirror.py && chmod +x quinindrome && ./quinindrome > quinindrome2 && xxd quinindrome2 && diff quinindrome2 quinindrome && ./test.sh quinindrome
51 quiny
Created quinindrome! Size: 101 bytes
00000000: 7f45 4c46 0100 0000 0000 0000 0000 0010  .ELF............
00000010: 0200 0300 4341 eb08 1400 0010 0400 0000  ....CA..........
00000020: c1e1 1cb2 65b0 04cd 80a9 2000 0100 4bb0  ....e..... ...K.
00000030: 01cd 80cd 01b0 4b00 0100 20a9 80cd 04b0  ......K... .....
00000040: 65b2 1ce1 c100 0000 0410 0000 1408 eb41  e..............A
00000050: 4300 0300 0210 0000 0000 0000 0000 0000  C...............
00000060: 0146 4c45 7f                             .FLE.
[+] First check passed: binary is a byte-wise palindrome.
[+] Second check passed: binary is a true quine, its output matches itself.
[+] Both checks passed: your binary is a very nice quinindrome!
[+] Your score: 101
```

### Using `xchg eax`

I then leart that instead of doing operations such as `mov al, 0x04` which take 2 bytes, all the `xchg eax, REG` are one byte. And remember to have the write be sent to `stdout` we had set `ebx=0x01` for the first syscall.

So once the first syscall is done instead of doing this three byte code `4B B0 01`

```asm
    dec     ebx                 ; [48] ebx = 0 (status)
    mov     al, 1               ; [49] eax = 1 (sys_exit)
```

I could use one of the registers initialized to 0 to get the zero into `eax` and then swap `eax` and `ebx` to get them to their desired values (resp 01 and 00).
We can thus reduce the second syscall related code to

```asm
    xchg    eax, esi
    xchg    eax, ebx
    int     0x80
```

This gives us [quiny99.asm](./quiny99.asm).

### Making the `org`/`p_vaddr` address valid code

At this moment when we look at the elf we can see that most of it is filled with zeroes, which are for the first the `p_type=PT_LOAD=0x00000001` followed by the `p_offset=0x00000000` and the `p_vaddr=0x01000000` (in little endian in the file). Moreover the `p_flags` is `0x0004` (READ) (it is sufficient as read implies execute) and we need to set `eax` to 4.
Why not make the `org` (the loading adress of the program) be valid code.

This took quite a lot of time to do as `p_vaddr % PAGE_SIZE` (page size is 4096) needs to be equal to `p_offset % 4096` and `org` is just an alias for `nasm` tool as the important thing is `p_vaddr`. So we need

- the 3 first characters of `org` to be 0 in little endian.
- `org < 0xC0000000` (to stay in user space authorized addresses)
- the whole `_start` adress must be valid code once reversed (little endian obliges)
- `_start` is `org + 0x14`
- `p_filesz <= p_memsz <=> e_version <= e_entry = org + 0x14`
  - especially for the MSB
- keep `p_vaddr = org` easy to load into ecx to try and use less than 5 bytes
- have the MSB of `org` be valid code to consume a 32 bit variable and put it into `eax`

The solution I found was to

- set the heighest bit to `0x0D` which is `or eax imm32` as eax is initialized to 0, which uses the `p_flags/e_phoff` value to set eax to `0x0004`.
- set the second LSB of `org` to `00` as `0x14` the LSB of `e_entry` is `adc al imm8` so we need the second LSB of `e_entry` to be `00`
- set the second MSB of `org` was set to `90` (nop)

This gives us `org = 0x0D900000`. Which can be loaded into `ecx` either with a `mov ecx, 0x0D900000` (5 bytes) or with two instructions `mov cl, D9` `shl ecx, 20` (also 5 bytes but can be split at different places).

In `e_version` to validate the constraint of `p_memsz >= p_filesz` I had to find an operation in MSB that was inoffensive and smaller than `OD` so in the 13 operations available I picked `06` which is `push es`.

This gives us [quiny95.asm](./quiny95.asm)

When I reached here I was content. I hope you agree with me that the code cannot be reduced more, all the fields of the header that are usefull have been kept all the others are used.

Moreover as the smallest ELF binary is 45 bytes (source muppetlabs), then the smallest quinindrome cannot be smaller than 92 bytes (to add the zero necessary for `e_phnum = 0x0001`).

I believed I could make it to the top 3 with this binary... *spoiler I did not*

## Automatizing the search for symmetries

The problem of my method was that I put the program header at offset 4 and I wanted to do the symmetry on the last byte of the program. Why not search for a symmetry in the middle of the program and put the program header at other places.

Moreover the rules I had fixed were those of muppetlabs and my own trial and error.
So I did not know irl what was enforced.

### Returning to the source

There are two files responsible of loading the binaries in the linux kernel [torvalds/linux/kernel/kexec_elf.c](github.com/torvalds/linux/blob/ccd1cdca5cd433c8a5dff78b69a79b31d9b77ee1/kernel/kexec_elf.c) and [torvalds/linux/fs/binfmt_elf.c](https://github.com/torvalds/linux/blob/ccd1cdca5cd433c8a5dff78b69a79b31d9b77ee1/fs/binfmt_elf.c).

Both do not enforce the same constraint one is for loading the ELFs in the kernelspace and the other is for loading as a userspace binary. Quite unsurprisingly the kernelspace code enforces more restrictions than the userspace file.

The rules that are effectively enforced are:

- for the Elf32_Ehdr
  - magic bytes of elf header must start with `7F454C46`
  - `e_type` must be `0200` (`ET_EXEC`) or `0300` (`ET_DYN`) (but this causes changes in the adresses so we will avoid it)
  - `e_machine` must be `0300` (`EM_386`) or `0600` (`EM_860`) for our 32 bit ELF
  - `e_entry` must be the address of the beginning of the code (when it is loaded by the Phdr)
  - `e_phoff` must be the offset in the file at which the program header starts
  - `e_phentisze` must be `0x0020`=32 (big endian)
  - `e_phnum` must be `0x0001`=1 (big endian)
- for the Elf32_Phdr
  - `p_type = 0x00000001 = PT_LOAD` for a loadable segment
  - `p_vaddr (mod 4096) === p_offset (mod 4096)`
  - `p_vaddr <= 0xC0000000`
  - `p_memsz >= p_filesz`
  - `p_flags` three first bits give the RWX permissions and we need at least R permissions
  - `p_offset <= p_filesz`
  - `p_offset` is the offset in the file of the data that needs to be loaded in memory

### Scripting the exploration

I then wrote a script [symmetries.py](./symmetries.py) to try all the possible:

- axis of symmetry
- offset of the phdr

and get the number of usable bytes, resolve the conflicts between the different undetermined values

This gave me a 83 bytes possibility with the `Phdr` at offset 44 from the beginning of the file.
All the `?` are dontcares we can put anything in them, the valid hexadecimal characters are fixed.
The `GHIJKLMNOPQRTUVWXYZ` are placeholders for values that need to be the same in hex at different places in the file.
In the following example we can choose the MSB of `e_entry` as it is `MN` but we must modify all subsequent occurences accordingly. Furthermore I fixed the LSB of `e_entry` to `04` but this needs to be changed depending on where we make the code start.

```txt
Symmetry found at axis 83: score 83
  - offset 44
  - elf: 7F454C46????????????????????????02000300????????04002CMN2C000000000000000000010020??2000010000000000000000002CMN2C0004????????00030002????????????????????????464C457F
  - Resolutions: {'G': '0', 'H': '0', 'I': '0', 'J': '0', 'K': '2', 'L': 'C'}
  - Reconstructed: {'e_entry': '04002CMN', 'p_offset': '00000000', 'p_vadd': '00002CMN'}
  - Usable bytes: 17
  - ELF header: 7F454C46????????????????????????02000300????????04002CMN2C000000000000000000010020??200001000000
  - PE header: 010000000000000000002CMN2C0004????????00030002??????????????????
```

A final code optimisation was found using `bswap` to make the load of the `ecx` a 4 byte ordeal. If I could have `ecx` be made of only zeroes except for one byte. I also used `68` to eat bytes by pushing to the stack rather than using a jump

With all this in mind it is possible to make the code fit in the second half of the header and gives us a 83 bytes palindrome quine as the complete payload is 15 bytes long.
There was no other solution shorter than 83 with sufficient bytes that could be used to inject code.

```sh
echo '7F454C4680CD939680CDC90F2CB504B0020003006853B2433B002C002C000000000000000000010020002000010000000000000000002C002C003B43B2536800030002B004B52C0FC9CD809693CD80464C457F' | xxd -r -p > quinpy83 && ./test.sh quinpy83
[+] First check passed: binary is a byte-wise palindrome.
[+] Second check passed: binary is a true quine, its output matches itself.
[+] Both checks passed: your binary is a very nice quinindrome!
[+] Your score: 83
```

### Debugging

Debugging this started to become painfull as I was writing the whole ELF by hand, so I wrote an [elf_parser.py](./elf_parser.py) to be able to follow what was happening and see where I made typos.

For the above file it gave the following output:

```sh
python elf_parser.py quinpy83

=== ELF HEADER ===

Magic Number:        ELF
EI_CLASS:            128 (Unknown)
EI_DATA:             205 (Unknown)
EI_VERSION:          147
EI_OSABI:            150 (Unknown)
EI_ABIVERSION:       128
e_type:              0x0002 (ET_EXEC)
e_machine:           0x0003 (EM_386)
e_version:           1135760232
e_entry:             0x2c003b

  Entry point calculation:
    Virtual address where execution starts: 0x2c003b
    This is in program header at vaddr 0x2c0000
    Note: Memory is page-aligned, so segment starts at 0x2c0000
    File offset = p_offset - page_offset + (e_entry - page_aligned_vaddr)
                = 0x0 - 0x0 + (0x2c003b - 0x2c0000)
                = 0x3b (byte 59 in file)
    Code at entry: 43B253680003

e_phoff:             44 (0x2c)
e_shoff:             0 (0x0)
e_flags:             0x00010000
e_ehsize:            32 bytes
e_phentsize:         32 bytes
e_phnum:             1
e_shentsize:         0 bytes
e_shnum:             0
e_shstrndx:          0

=== PROGRAM HEADERS ===

Program Header 0:
  p_type:      0x00000001 (PT_LOAD)
  p_offset:    0 (0x0)
  p_vaddr:     0x2c0000
  p_paddr:     0x433b002c
  p_filesz:    6837170 bytes (0x6853b2)
  p_memsz:     2952921091 bytes (0xb0020003)
  p_flags:     0x0f2cb504 (R--)
  p_align:     2525023689 bytes

  Memory mapping:
    File [0x0:0x6853b2] -> Memory [0x2c0000:0xb02e0003]
    File data preview: 7f 45 4c 46 80 cd 93 96 80 cd c9 0f 2c b5 04 b0 02 00 03 00 68 53 b2 43 3b 00 2c 00 2c 00 00 00 ...


=== DISASSEMBLY AT ENTRY POINT (0x2c003b) ===

  0x002c003b: 43                inc ebx
  0x002c003c: b2 53             mov dl, 0x53
  0x002c003e: 68 02000300      push 0x2000300
  0x002c0043: b0 04             mov al, 0x4
  0x002c0045: b5 2c             mov ch, 0x2c
  0x002c0047: 0F c9             bswap ecx
  0x002c0049: CD 80             int 0x80
  0x002c004b: 96                xchg eax, esi
  0x002c004c: 93                xchg eax, ebx
  0x002c004d: CD 80             int 0x80
  0x002c004f: 46                inc esi
  0x002c0050: 4c                dec esp
  0x002c0051: 45                inc ebp
  0x002c0052: 7f                <unknown>
```

Confident I would get on the podium I was astonished that I was only 4th ex aequo with the third, but first and second were still before me.

## `p_offset`

My train of thought was pretty much bloated at this point.

- I was confident that it was not possible to reduce the number of bytes to get the write syscall and the exit.
- I already checked the sources so the only values enforced in my mask are the minimal values enforced
- ~~I thought maybe I should put code into p_offset and instead of using this p_offset to load the program I would try and get the vestigial bytes when the kernel was parsing the file, so maybe I should debug podman's loading of the file...~~ I luckily didn't go that far...
- The only thing I enforced, that is not explicit in the `fs/libmt_elf.c` is the `p_offset` set to `00000000`

What happens ikl (in kernel life) is that the `p_offset` is used to determine in which memory page the data to load is present. Therefore as long as `p_offset` is smaller than 4096 then the first page of the loaded ELF will be loaded into memory. This means that even if I ask it to load data after the beginning of the file, it will load everything before it, as long as it is on the same memory page.

But I need to make sure that `p_offset % 4096 == p_vaddr % 4096`. (This can be translated into the 4 first hex characters in the little-endian hex representation of `p_vaddr` and `p_offset` must be equal)

I changed this in the constraints I enforced in my `symmetries.py` script, and got the following output (with more than 15 bytes available):

```txt
Symmetry found at axis 81: score 81
  - offset 44
  - elf: 7F454C46????????????????????????02000300????????040NKL0N2C0000002C000000010020??????2000010000002C0000002C0NKL0N04????????00030002????????????????????????464C457F
  - Resolutions: {'I': '0', 'G': '2', 'H': 'C', 'M': '0', 'J': 'N'}
  - Reconstructed: {'e_entry': '040NKL0N', 'p_offset': '2C000000', 'p_vadd': '2C0NKL0N'}
  - Usable bytes: 19
  - ELF header: 7F454C46????????????????????????02000300????????040NKL0N2C0000002C000000010020??????200001000000
  - PE header: 010000002C0000002C0NKL0N04????????00030002??????????????????????
```

To keep the `ecx` loading in 4 bytes I needed to have `p_vaddr - p_offset` have as many zeroes as possible.
So I set `N=0` and kept the same address as before `0x002C0000`. So `p_vaddr = 0x002C002C`, `p_offset=0x0000002C`, `e_entry=0x002C0004`.

This gave me this 81 bytes quinindrome

```sh
$ echo '7F454C46B25143B52C0FC9B004CD8068020003009693CD8004002c002C0000002C0000000100200000002000010000002C0000002C002c000480CD9396000300026880CD04B0C90F2CB54351B2464C457F' | xxd -r -p > quinpy81 && ./test.sh quinpy81
[+] First check passed: binary is a byte-wise palindrome.
[+] Second check passed: binary is a true quine, its output matches itself.
[+] Both checks passed: your binary is a very nice quinindrome!
[+] Your score: 81
$ python elf_parser.py quinpy81

=== ELF HEADER ===

Magic Number:        ELF
EI_CLASS:            178 (Unknown)
EI_DATA:             81 (Unknown)
EI_VERSION:          67
EI_OSABI:            181 (Unknown)
EI_ABIVERSION:       44
e_type:              0x0002 (ET_EXEC)
e_machine:           0x0003 (EM_386)
e_version:           2160956310
e_entry:             0x2c0004

  Entry point calculation:
    Virtual address where execution starts: 0x2c0004
    This is in program header at vaddr 0x2c002c
    Note: Memory is page-aligned, so segment starts at 0x2c0000
    File offset = p_offset - page_offset + (e_entry - page_aligned_vaddr)
                = 0x2c - 0x2c + (0x2c0004 - 0x2c0000)
                = 0x4 (byte 4 in file)
    Code at entry: B25143B52C0F

e_phoff:             44 (0x2c)
e_shoff:             44 (0x2c)
e_flags:             0x00200001
e_ehsize:            0 bytes
e_phentsize:         32 bytes
e_phnum:             1
e_shentsize:         0 bytes
e_shnum:             44
e_shstrndx:          0

=== PROGRAM HEADERS ===

Program Header 0:
  p_type:      0x00000001 (PT_LOAD)
  p_offset:    44 (0x2c)
  p_vaddr:     0x2c002c
  p_paddr:     0x93cd8004
  p_filesz:    196758 bytes (0x30096)
  p_memsz:     3447744514 bytes (0xcd806802)
  p_flags:     0x0fc9b004 (R--)
  p_align:     1363391788 bytes

  Memory mapping:
    File [0x2c:0x300c2] -> Memory [0x2c002c:0xcdac682e]
    File data preview: 01 00 00 00 2c 00 00 00 2c 00 2c 00 04 80 cd 93 96 00 03 00 02 68 80 cd 04 b0 c9 0f 2c b5 43 51 ...


=== DISASSEMBLY AT ENTRY POINT (0x2c0004) ===

  0x002c0004: b2 51             mov dl, 0x51
  0x002c0006: 43                inc ebx
  0x002c0007: b5 2c             mov ch, 0x2c
  0x002c0009: 0F c9             bswap ecx
  0x002c000b: b0 04             mov al, 0x4
  0x002c000d: CD 80             int 0x80
  0x002c000f: 68 00030002      push 0x30002
  0x002c0014: 96                xchg eax, esi
  0x002c0015: 93                xchg eax, ebx
  0x002c0016: CD 80             int 0x80
  ...
```
