# Never Enough

This challenge is one of those most educational challenges, there is no weird obfuscation, no weird tricks, this is based on a real life python code issue. So let's understand why all these years we were told that vanilla `random` was not safe to use for cryptographic purposes.

## Analysis of the challenge source code

The source code of the challenge is very simple:

```py
from random import getrandbits
from Crypto.Cipher import AES
from hashlib import sha256
danger = 624*32 # i hear you need this much.
given = []
key = ""
for _ in range(danger//20 - 16): # should be fine if im only giving u this much :3
    x = getrandbits(32)
    # we share <3
    key += str(x % 2**12)
    given.append(x >> 12)

key = key[:100]
key = sha256(key.encode()).digest()
flag = open("flag.txt", "rb").read().strip()
cipher = AES.new(key, AES.MODE_ECB)
print(given)
print(cipher.encrypt(flag + b"\x00" * (16 - len(flag) % 16)).hex())
```

For each 12-bit number that is added to the key, we are given it's upper 32 bits. We will see later on why all these numbers.

The provided files are [`out.txt`](out.txt) which contains the 982 upper 20 bits of the outputs of the `getrandbits(32)` function, and [`chall.py`](chall.py) which is the source code of the challenge.

## Deep dive into documentation

First of all I went to the Python's standard library implementation of [`random`](https://github.com/python/cpython/blob/main/Lib/random.py#L901-L907) of which we can find an excerpt here (by following vscode's resolution of imports)

```py
# random.py
from os import urandom as _urandom
# [...] lot's of code
    def getrandbits(self, k):
        """getrandbits(k) -> x.  Generates an int with k random bits."""
        if k < 0:
            raise ValueError('number of bits must be non-negative')
        numbytes = (k + 7) // 8                       # bits / 8 and rounded up
        x = int.from_bytes(_urandom(numbytes), 'big')
        return x >> (numbytes * 8 - k)                # trim excess bits
```

Surprisingly nothing of much interest here except that there is this call to `os.urandom`, which really does all the job. This was very surprising as I was not expecting it to rely on an os based random generator which I would have thought secure, but I decided to overlook this and go to the python documentation of random's `getrandbits` function.

### How python implements it's random module

*This part was not delved into during the CTF, but when I was writing this writeup. As I knew that I had overlooked something important at the resolution time. I left purposefully my initial misconception in the writeup to show the thought process that led to the solution. If this is the only thing that interests you, you can skip to the next section, otherwise let's continue on how Python implements its `random` module.*

Going back to this `random.getrandbits` function, we see that it relies on `os.urandom` to generate random bytes, and then converts these bytes into an integer with the right number of bits.
At first glance this `urandom` function is not present in the `lib/os.py` file, which is where I expected it to be. Instead it is implemented in the C code of the Python interpreter.
If you were wondering why this function is not in the `lib/os.py` file you can check this [StackOverflow answer](https://stackoverflow.com/questions/54092441/where-can-i-find-the-source-code-of-os-urandom) which explains is much better than I could.
But from what I made out, `os.urandom` is a function that is implemented in the C code of the Python interpreter, and it is used to generate random bytes from the operating system's source of randomness.

And here is the [os.urandom](https://github.com/python/cpython/blob/0f56adb8d74e703974811620559d96c999334547/Modules/posixmodule.c#L11284-L11303) implementation, that we can find in the `posixmodule.c` file.

By consulting [Python's `os.urandom` documentation](https://docs.python.org/3/library/os.html#os.urandom) we learn that it is a function that returns random bytes suitable for cryptographic use, and that it uses the operating system's source of randomness.
Whoooah, this is not what we expected, we were hoping for a non-safe random number generator and finish with the opposite.

Going back to [Python's `random` documentation](https://docs.python.org/3/library/random.html) I saw what I had initially overlooked :

>The functions supplied by this module are actually bound methods of a hidden instance of the random.Random class. You can instantiate your own instances of Random to get generators that don’t share state.
>
> Class Random can also be subclassed if you want to use a different basic generator of your own devising: see the documentation on that class for more details.
>
> The random module also provides the SystemRandom class which uses the system function os.urandom() to generate random numbers from sources provided by the operating system.

So by default when calling the `random` module's functions, we are using an instance of the `random.Random` class, which uses the Mersenne Twister as the core generator, and not the `SystemRandom` class which uses `os.urandom`. But we can specify that we want our source of randomness to be the system's by using the `SystemRandom` subclass (I suppose that this is the default behaviour as some programmers might want to seed their random behaviour to ensure reproducibility of their code, and thus use the Mersenne Twister, but for all other cases I am surprised that the default is not to use the system's source of randomness).

After a little bit more exploration of the C python code base I found the [actual implementation of the `getrandbits` function](https://github.com/python/cpython/blob/main/Modules/_randommodule.c#L495-L550) and we can see that it is indeed based on [this function](https://github.com/python/cpython/blob/01c80b265060f016d3534eb74d540363808804e1/Modules/_randommodule.c#L124-L166) that implements the Mersenne Twister that we will learn about in two lines. Hurrah, we understood how the `random` module works in CPython.

### Analysis of `random.getrandbits`

Going to the [random documentation](https://docs.python.org/3/library/random.html) what I learned was much more aligned with what I was expecting of this challenge : a non-cryptographicaly secure pseudo-random number generator (PRNG).

Here is what we learn:

> This module implements pseudo-random number generators for various distributions.
>
> \[...\]
>
> Almost all module functions depend on the basic function random(), which generates a random float uniformly in the half-open range 0.0 <= X < 1.0. Python uses the Mersenne Twister as the core generator. It produces 53-bit precision floats and has a period of 2**19937-1. The underlying implementation in C is both fast and threadsafe. The Mersenne Twister is one of the most extensively tested random number generators in existence. However, being completely deterministic, it is not suitable for all purposes, and is completely unsuitable for cryptographic purposes.
>
> \[...\]
>
> random.getrandbits(k)
>
> Returns a non-negative Python integer with k random bits. This method is supplied with the Mersenne Twister generator and some other generators may also provide it as an optional part of the API. When available, getrandbits() enables randrange() to handle arbitrarily large ranges.

We now know how the `getrandbits` function works: it is based on the Mersenne Twister, furthermore that it is completely deterministic.

We now know what this challenge is going to be about.

I read a few ressources on internet, the most useful being:

- The [Wikipedia page on Mersenne Twister](https://en.wikipedia.org/wiki/Mersenne_Twister)
- [breaking python PRNG](https://stackered.com/blog/python-random-prediction/) which I completely forgot about when implmementing the solution which is a shame because it adressed quite a few of the issues I had to solve
- [Cryptopal's challenge](https://cryptopals.com/sets/3/challenges/23)
- And a person solving cryptopal's challenge on [cypher.codes](https://cypher.codes/writing/cryptopals-challenge-set-3)
- I also saw this [GitHub repository](https://github.com/icemonster/symbolic_mersenne_cracker) which would have probably also saved time but I forgot about it until I was done with the challenge.

From all of these ressources, we learn that

1. Mersenne Twister is a pseudorandom number generator (PRNG) that is *deterministic* and has a very long period.
2. It generates numbers based on an internal state of **624** integers, and if one knows 624 consecutive outputs, one can reconstruct the internal state of the generator.
3. The generation process involves an invertible tempering function, and a twist function that *twists* the internal state every 624 outputs.
4. Each time we ask the generator for a number it applies the tempering function to the next integer in its internal state, until it reaches the last integer, at which point it twists the internal state and starts over.

At that point we finally make some sense from the comment `danger = 624 * 32  # i hear you need this much.` This comment refers to the fact that the Mersenne Twister has an internal state of 624 integers, each 32 bits long, which gives a total of $624 \times 32 = 19,968$ bits of state information. However, we only have the upper 20 bits of each output, which means we have $982 \times 20 = 19,640$ bits of information. This is close to the theoretical limit, but we will hope that this is sufficient, given the mathematical constraints on the numbers that are generated, to be able to reconstruct the internal state of the generator.

## Implementation of the solution

### Z3 to the rescue

After having discovered in the `rev/DNA` challenge the power of the Z3 solver I told myself that this challenge was also probably easily solved by Z3 that by my trying to write the complete system of equations that would enable me to derive the internal state of the generator from the outputs.
This is only possible because SAT solvers and SMT solvers have been so optimized that "reducing" a problem to a SMT problem is often a quick and easy win, even if it is not the most intuitive way to do so. Furthermore, Z3 has a very intuitive Python API that makes it easy to write the constraints and solve them.

### Steps

What I did was the following:

1. Write a Mersenne Twister in python that mimics the exact behaviour of the python `random.getrandbits` function.
2. Write a `Z3` Mersene Twister that has exactly the same behaviour as the python one, but that can be used to solve the constraints.
3. Extensively test my two Mersenne twisters to ensure they behaves exactly like `getrandbits`. *(Ensuring that my Z3 Mersenne solver managed to solve the problem proved itself by far the toughest part of this challenge.)*
4. Convert all our outputs to Z3 constraints
5. Wait for the solver to perform its magic
6. Profit
7. Realize that the CTF finished 48 minutes ago
8. Go on discord and see that the above ressources that had been since then been long forgotten would have saved a lot of time

### Implementation

I used [kmyk's](https://github.com/kmyk/mersenne-twister-predictor/blob/master/mt19937predictor.py) implementation of the Mersenne Twister to write my reference implementation of the python's getrandbits. *I only went to the C documentation once the challenge was finished, I suppose I would have won time if I had done it from start.*

My python implementation of python's `getrandbits` can be found in [python_mt19937.py](python_mt19937.py).

Once this was done, I iterated on the Z3 implementation [mt19937_z3.py](mt19937_z3.py).

#### Implementing the constraints

Instead of performing - as is classically the case, to attack the Mersenne Twister - by untempering the outputs, I decided to just implement the Mersenne Twister in Z3. So for each output I would:

- Check if the internal state index was 624, if so I would twist the internal state.
- Apply the tempering function to the unknown initial internal state and "equal" it to the output.

Twisting the state was by far the part I took the most time to implement as I had initially overlooked a few important details. Here are the keys to understanding how the twist function works:

- The state is a list of 624 integers in an intial state
- The twist function iterates on this list and applies a transformation to each integer using the current values of the state matrix, once it modified a value it replaces it's old value with the new one in the state matrix.
- So for the first 226 elements all the values that are used are from the old state, but for the next 398 elements, the values used are from the new state. This basic fact that I initially overlooked took me waaaay too long to figure out.
- Lastly, in this problem they are two twists, one at 0 and one at 624 so I needed to make Z3 aware of three complete states.

Once this was done and the Z3 implementation managed to interface itself with the python implementation, and they managed to produce solutions that agreed with getrandbits, I finally wrote the last script that would solve the challenge : [solve_ctf.py](solve_ctf.py).

This script also enabled me to debug my Z3 implementation by checking that whatever the number of inputs from the `out.txt` I gave it, the problem stayed SAT(satisfiable).

### Solve

```txt
❯ python solve_ctf.py
🎮 Never Enough solver
==================================================
🎯 Starting CTF solver...
📊 Number of partial outputs: 982
🔒 Encrypted flag: c8a6c38be0ec97bc32df34e0df6e5d7b64a1dc238b0e5019a7...

🔧 Setting up Z3 solver...
✅ Created symbolic MT19937 state
📝 Adding constraints for 982 partial outputs...
   ✓ Added constraint 100/982
   ✓ Added constraint 200/982
   ✓ Added constraint 300/982
   ✓ Added constraint 400/982
   ✓ Added constraint 500/982
   ✓ Added constraint 600/982
   ✓ Added constraint 700/982
   ✓ Added constraint 800/982
   ✓ Added constraint 900/982
🔍 Solving constraints...
🎉 Solution found!
🔓 Recovering initial state from model...
✅ Initial state recovered!
🔓 Generating full 32-bit outputs...
✅ All outputs recovered and verified!
🔑 Reconstructing encryption key...
🔐 Key string (first 50 chars): 76312203420325621612292416387511692535693416368934...
🔐 SHA256 key: 1d18f995847000d3efedace354e44a68...
🚩 Decrypting flag...
🎉 FLAG: .;,;.{never_enough_but_you_gotta_just_make_more_or_something_idk_im_not_a_motivational_speaker_but_you_get_the_idea}

🏆 CTF challenge solved successfully!
```

The time to solve the problem was of 15 minutes and 26 seconds. I suppose there might have been more efficient ways to do it by untempering the first 624 outputs and getting guarantees on the initial state, but I did not implement this so I don't know how long it would have taken.
