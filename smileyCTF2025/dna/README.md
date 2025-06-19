# DNA

The description of the challenge is as follows:

>rev/DNA
>
>deoxy ribo nucleic acid deoxy meaning without oxygen ribo meaning the 5-carbon sugar backbone nucleic meaning of the nucleus acid meaning proton donor

And we are given an archive in which we find two files:

```sh
$ tar --list -f dna.tar.gz
dna/
dna/main.cpython-310.pyc
dna/vm.dna
```

`vm.dna` is exactly how I remembered my biology classes, an endless stream of ATGC bases. And on the other hand we learn that

```sh
$ file main.cpython-310.pyc
main.cpython-310.pyc: Byte-compiled Python module for CPython 3.10, timestamp-based, .py timestamp: Fri Jun  6 03:24:45 2025 UTC, .py size: 9623 bytes
```

The version of python is quite crucial to abide by as the bytecode the python interpreter produces changes with the versions of python, and this will prove itself crucial later on.

After having looked for different tools, the one that I used was [pylingual](https://pylingual.io). Even though the code that it suggested was not perfectly syntactically correct, a few simple changes were enough to get a working code [main.rev0.py](main.rev0.py).

This code takes as input a file, we will give it the `vm.dna` file, and then uses it to know what instructions to run. This works sort of like a simple chip which executes one instruction per cycle and can perform arithmetic operations and memory read and write.

The program also takes as input a user input that must be validated by matching the flag pattern of the smileyCTF and must be 49 characters long (without the `.;,;.{}` mask). So the objective is to find the right input and it will be the flag.

## First attempt at running the program

Not knowing how the characters are used, I decided to use as many printable characters as possible and validate the basic mask.

```python
flag_test_array = [chr(i) for i in range(48, 48 + 49)]

flag_test = '.;,;.{' + ''.join(flag_test_array) + '}'
# .;,;.{0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`}
```

After running the program with this very promising flag we get the following output:

```txt
Traceback (most recent call last):
  File "I/love/writeups/smileyCTF2025/dna/main.rev.py", line 196, in <module>
    f.__code__ = marshal.loads(bytecode)
TypeError: __code__ must be set to a code object
```

Not surprisingly this failed. Let's get back to analysing the de-bytecoded script. First of all we see that there are three parts that interact together the stack `s`, the code `vm.dna` and the memory `m`. We also see that the unlucky are popped when having the instruction coded 13, so they are only called once, and then loaded by `marshal` after being xored with a value on top of the stack. To be convinced that this was the place where the code was crashing I put a breakpoint just before the `marshal.loads`, it is reached and the execution fails on the next line.

After a little bit of debugging, trying to follow the instructions until I reached this point, I decided to put a cycles counter in the code to see how many cycles had to be run before reaching this point, and case 13 is triggered for the first time at cycle n°2158... or so to say I am not going to watch my stack for as many cycles to understand where the value that is xored to the `marshal.loads` comes from.

A few interesting facts we see when reading through this program:

- Our flag is stored into the memory of the program at the beginning of the execution, between memory indices 640 and 688.
- `pc` `pri` and `pro` seem to be respectively
  - the program counter (aka the pointer to the instruction to execute)
  - the instruction the program counter was pointing to
  - and a storage register, which holds the value of interest when the `pc` points to code that wants to push a value to the stack for instance, or jump somewhere...
- At each step `pc` is used to read the DNA at a certain address that gives us what instruction to execute `pri` and what to store in `pro`.
- And the most interesting fact is that `pc` (and consequently `pri` and `pro`) do not depend on the flag or the unlucky, only on the `vm.dna` instructions, and that  `pc` only ever increases by 2 if `pro` was not used and by 12 if `pro` was consumed.

This means that `vm.dna` is just a linear mix of instruction and data.

## Does anyone feel lucky

First of all not being familiar with `marshal` I checked the [python documentation](https://docs.python.org/3.10/library/marshal.html) (for python 3.10 (not that I think it changes but just in case)).

> This module contains functions that can read and write Python values in a binary format. The format is specific to Python, but independent of machine architecture issues (e.g., you can write a Python value to a file on a PC, transport the file to a Sun, and read it back there). Details of the format are undocumented on purpose; it may change between Python versions (although it rarely does).
>
> This is not a general “persistence” module. For general persistence and transfer of Python objects through RPC calls, see the modules pickle and shelve. The marshal module exists mainly to support reading and writing the “pseudo-compiled” code for Python modules of .pyc files. Therefore, the Python maintainers reserve the right to modify the marshal format in backward incompatible ways should the need arise. If you’re serializing and de-serializing Python objects, use the pickle module instead – the performance is comparable, version independence is guaranteed, and pickle supports a substantially wider range of objects than marshal.

_I saw a lot of messages on the discord concerning `marshal` and `unlucky` once the challenge was finished, I think the problem most of the people had was that they were not running all these programs with python 3.10 but another version, which led to incorrect decoding / unpickling of the unlucky bytecode_

As I wanted to reach the end of the program to know what was happening before trying to figure out how our flag was used, and because we had no idea what the `unlucky` code did, and it could very well modify the stack, the memory or the dna... We now needed to tackle the `unlucky` step.

The first step in understanding unlucky is decoding it. Luckily as it is xoring byte per byte with one and only key, we know that there are only 256 different possible values for the key, and to know if we have the right solution we have an oracle : `marshal.loads`. If it loads then it is probably the right key, if it fails then we can try another.

This is the code that I used to recover the four keys [find_unlucky_key.py](./find_unlucky_key.py)

```python
import dis
import marshal

for i_unl in range(len(unlucky)):
    for key in range(256):
        try:

            def f():
                return

            bytecode = bytes(b ^ key for b in unlucky[i_unl])
            code_obj = marshal.loads(bytecode)
            f.__code__ = code_obj
            print(f"[{i_unl}] Key found: {key}")
            print("Disassembled bytecode:")
            dis.dis(code_obj)
            print("-" * 50)

            # Dump the code object to a .pyc file
            with open(f"decoded_{i_unl}_{key}.pyc", "wb") as pyc_file:
                marshal.dump(code_obj, pyc_file)
        except (TypeError, ValueError, EOFError):
            continue
```

The output is that there is only one possible value for each key, which is reassuring.
At the same time I dumped the [disassembled bytecode](./unlucky.disass) and found out that the bytecode is close to human readable and that it only just shuffles the values of ATGC around, so the vm.dna code is not tampered with but it's meaning changes after an unlucky round.

### Useless side quest - writing unlucky back to python

Seeing how understandable the unlucky code was I asked copilot to reverse it and vibe python code that would generate this bytecode. Comparing the bytecode it generated to the original bytecode was surprisingly accurate. If you want to check out a close to exact original unlucky implementation check out [`unluckyfuncs.py`](./unluckyfuncs.py). The only thing he did not manage to render correctly was the `[::-1]` pattern for a reason that I did not understand. You can check this out in [`compare_unlucky.py`](./compare_unlucky.py)

## Reaching the end of the execution

With that said I modified the case 13 to use the newly found key values to use them instead of the stack provided value, which enabled us to reach the end of the program !... and get the output `WRONG!`.

Interestingly there is no more occurrence of this chain of characters in the python code so this must be encoded into the `vm.dna`.
After toying with breakpoints I finally understood that there was an equality test that was performed and depending on this output the pointer would either jump to the pc `69170` where it would print `WRONG!` or to the pc `69308` where it would print `CORRECT!`.
Seeing how the strings were printed by performing these 14 _nucleotides_ iterations I ran a "string extractor" program that tried all the different offsets between 0 and 13 and tried to see if there were any other strings to extract... there were none.

Now we know that our program

- takes in input the flag
- performs a series of operations that can't be tracked manually
- then checks an equality
- and finally decides if we inputted the right flag initially

## Dumping `vm.dna` to assembly

Knowing that the machine was using a fairly limited set of instructions I decided to print out what the whole program was doing into assembly (which would also enable me not to worry about the vm.dna or the unlucky anymore).

To do so I just added on each case a `print` with the equivalent line in assembly the program that did it is [`dump_ass.py`](./dump_ass.py). The result is [`vm.asm`](./vm.asm). I wrote a [`Makefile`](./Makefile) to compile it and the result once executed is indeed the same as the python version. _If you read attentively the assembly you'll notice I changed the code at the `pri=13` cases so as to mimic the early failures of a wrong output_.

At that point as the compiled version of the program was so efficient to run I hesitated to try brute-forcing the flag but after a quick check all the values that we provided were used at least once before the first breaking test of the `marshal` loading so I told myself it was still impractical.

Nevertheless by adding comments to the assembly we finally understand what the program is doing.

First of all we see that all the values that are stored in the memory are only accessed once, they are all compared to a hardcoded value, each time the result is correct we store a 1 in memory, if the result is false a 0. After having done 49 such comparisons we sum all the results and if we have an output of 49 then we get the `CORRECT` string.

We also see that for each value that the program is storing it accesses each character of the flag exactly once in an increasing order from the first character to the last.

And here is an excerpt of what is being done. I took all the first round of operations until a store in memory

```sh
cat vm.asm | head -n 1305 | grep addr -A 1 | grep -E '^\s+;'
    ; Load from memory[640]
    ; Push immediate 106
    ; Multiply
    ; Load from memory[641]
    ; Push immediate 27
    ; Multiply
    ; Load from memory[642]
    ; Push immediate 140
    ; Multiply
    ; Load from memory[643]
    ; Push immediate 138
    ; Multiply
    ; Load from memory[644]
    ; Push immediate 108
    ; Multiply
    ; Load from memory[645]
    ; Push immediate 91
    ; Multiply
    ; Load from memory[646]
    ; Push immediate 131
    ; Multiply
    ; Load from memory[647]
    ; Push immediate 138
    ; Multiply
    ; Load from memory[648]
    ; Push immediate 106
    ; Multiply
    ; Load from memory[649]
    ; Push immediate 127
    ; Multiply
    ; Load from memory[650]
    ; Push immediate 161
    ; Multiply
    ; Load from memory[651]
    ; Push immediate 115
    ; Multiply
    ; Load from memory[652]
    ; Push immediate 177
    ; Multiply
    ; Load from memory[653]
    ; Push immediate 152
    ; Multiply
    ; Load from memory[654]
    ; Push immediate 15
    ; Multiply
    ; Load from memory[655]
    ; Push immediate 55
    ; Multiply
    ; Load from memory[656]
    ; Push immediate 230
    ; Multiply
    ; Load from memory[657]
    ; Push immediate 131
    ; Multiply
    ; Load from memory[658]
    ; Push immediate 147
    ; Multiply
    ; Load from memory[659]
    ; Push immediate 183
    ; Multiply
    ; Load from memory[660]
    ; Push immediate 235
    ; Multiply
    ; Load from memory[661]
    ; Push immediate 197
    ; Multiply
    ; Load from memory[662]
    ; Push immediate 200
    ; Multiply
    ; Load from memory[663]
    ; Push immediate 104
    ; Multiply
    ; Load from memory[664]
    ; Push immediate 188
    ; Multiply
    ; Load from memory[665]
    ; Push immediate 196
    ; Multiply
    ; Load from memory[666]
    ; Push immediate 118
    ; Multiply
    ; Load from memory[667]
    ; Push immediate 28
    ; Multiply
    ; Load from memory[668]
    ; Push immediate 21
    ; Multiply
    ; Load from memory[669]
    ; Push immediate 97
    ; Multiply
    ; Load from memory[670]
    ; Push immediate 151
    ; Multiply
    ; Load from memory[671]
    ; Push immediate 217
    ; Multiply
    ; Load from memory[672]
    ; Push immediate 118
    ; Multiply
    ; Load from memory[673]
    ; Push immediate 22
    ; Multiply
    ; Load from memory[674]
    ; Push immediate 212
    ; Multiply
    ; Load from memory[675]
    ; Push immediate 31
    ; Multiply
    ; Load from memory[676]
    ; Push immediate 101
    ; Multiply
    ; Load from memory[677]
    ; Push immediate 227
    ; Multiply
    ; Load from memory[678]
    ; Push immediate 155
    ; Multiply
    ; Load from memory[679]
    ; Push immediate 237
    ; Multiply
    ; Load from memory[680]
    ; Push immediate 146
    ; Multiply
    ; Load from memory[681]
    ; Push immediate 68
    ; Multiply
    ; Load from memory[682]
    ; Push immediate 75
    ; Multiply
    ; Load from memory[683]
    ; Push immediate 71
    ; Multiply
    ; Load from memory[684]
    ; Push immediate 218
    ; Multiply
    ; Load from memory[685]
    ; Push immediate 173
    ; Multiply
    ; Load from memory[686]
    ; Push immediate 41
    ; Multiply
    ; Load from memory[687]
    ; Push immediate 220
    ; Multiply
    ; Load from memory[688]
    ; Push immediate 161
    ; Multiply
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Add
    ; Store to memory[4096]
```

What the program is doing is a sort of reverse polish notation maths in which :

- we read a char from the flag
- multiply it with a fixed value (hardcoded into `vm.dna`)
- repeat for all the other values of the flag
- sum all these multiplications
- store the result in a variable
- repeat 49 times
- compare these 49 sums of multiplications with hardcoded values

The program is thus verifying that our flag is the solution to a linear system of equations.

Last of all we also see that the values that are keys to the unlucky decryption are just values from our string at offsets 26,27,22,33. So we already know four variables from our system, only 45 more to go

## Resolving the system

_During the CTF I don't know why but I did not manage to solve this with numpy, but whilst writing this writeup I managed without any problem so I guess what I am presenting now is overkill._ The final version of main I was working with is [`main.rev.py`](./main.rev.py) I did not clean it up as it is not crucial in this writeup but if you wanted to see the result of this effort here it is. You can also see the failed attempt to solve the system, I still don't know why it failed.

### Original Z3 implementation

tl;dr I finally used Z3 which is an SMT solver. For those of you not familiar with formal computing, SMT stands for _satisfiability modulo theories_ and is used in "determining whether a mathematical formula is satisfiable", and once it knows a formula is SAT then it can even provide a value that will make it SAT which is close to amazing. _This can be used to prove theorems / and other logic properties by checking that problems are UNSAT, which guarantees us that no solution exists to our input_

Furthermore Z3 has a very intuitive python api so it is very easy to write the linear system into it.

I finally only worked with the comments :sweat_smile: I had put in the assembly code to get [`operations.log`](./operations.log). That I obtained with the following command.

```sh
cat vm.asm | grep addr -A 1 | grep -E '^\s+;' > operations.log
```

So I finally wrote a script [`extract_constraint.py`](./extract_constraint.py) which did just that.
The system is finally solved in 3 minutes 49 seconds by Z3.

### Writeup version with numpy

I was a little surprised when doing the CTF that numpy did not manage to solve a system with 49 equations and 49 solutions...
I convinced myself that as it did not store the numbers as rationals, then it was losing precision at each step and that the errors would propagate until the system was completely wrong... but I was not convinced, numpy should manage to solve such a system trivially. So _I_ vibe coded [`np_solve.py`](./np_solve.py) which did just that and solved the problem without any issues whatsoever in 0.062 seconds which is 3700 times faster than Z3.

Nevertheless it wasn't as uninteresting as I intended as copilot suggested three different methods to solve it (two of them were new to me):

- [`numpy.linalg.lstsq`](https://numpy.org/doc/stable/reference/generated/numpy.linalg.lstsq.html) Good for over determined or under determined systems, which is our case as we have 53 equations for 49 variables (49 equations plus the 4 values we know to decipher the `unlucky`)
- [`numpy.linalg.pinv`](https://numpy.org/doc/stable/reference/generated/numpy.linalg.pinv.html) Which computes a pseudo inverse with minimal norm, which is also useful when the matrix is not invertible.
- [`numpy.linalg.solve`](https://numpy.org/doc/stable/reference/generated/numpy.linalg.solve.html) The everlasting classic.

And after having tried all three of these methods, they all give the correct output. I guess `numpy` still is the best way of solving linear systems.

## Wrap up

This CTF took me ages to do, not so much because of the complexity of each step but because there were quite a few that had to be done before reaching the solution, and a failure in each of them would signify no flag. I had never used Z3 so I had fun learning about it, but once again, it only manages to solve the problem 3700 times more slowly than numpy :sweat_smile:, so for future problems I would only use it when I do not know the maths to solve the problem by hand (for instance `crypto/never_enough`). It was fun to learn about python bytecode also. Lastly I am curious to see the program that was used to generate the DNA it must have been even more painful than solving the challenge I guess.
Thanks to the smiley team for the chall.

If this writeup is not clear feel free to reach out to me for further details.
