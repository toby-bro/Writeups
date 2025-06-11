# Veiled XOR - RSA with Bit-Reversed XOR Constraint

## Challenge Overview

This challenge involves a RSA based encryption scheme in which we are given $n = p \times q$ and $p \oplus q[::-1]$. Where $q[::-1]$ is the bit-reversed version of $q$. The goal is to recover $p$ and $q$ to be able to calulate the private key and decrypt the given ciphertext $c$.

## Approach

We are going to perform a bit by bit recovery of $p$ and $q$.

The idea is simple, at each iteration we will

1. Branch on the MSB and LSB of $p$ and $q$.
2. Compute the corresponding $p \times q$ and $p \oplus q[::-1]$.
3. Check if the computed values are compatible with the given values.

## 5-bit width example

Let's consider a simple problem where $p$ and $q$ are 5 bits long. Let's suppose we have

| Variable | binary value | base 10 value |
|----------|--------------|--------------|
| $p$      | 11011        | 27          |
| $q$      | 10011        | 19         |
| $q[::-1]$ | 11010        | 25        |
| $p \times q$ | 01000000001 | 513 |
| $p \oplus q[::-1]$ | 00010        | 2 |

The only information we know are the two last lines.

We will start by supposing that p and q have the following values:

| Variable | binary value |
|----------|--------------|
| $p$      | a???i        |
| $q$      | b???j        |
| $q[::-1]$ | j???b        |
| $p \oplus q[::-1] $ | $a\oplus j$ ??? $i\oplus b$ |
| $p\times q$ | $(a \times b)$ ??????? $(i \times j \pmod 2)$        |

The easy conditions to figure out and to understand are those of the XOR and the LSB of $n = p \times q$. And we know that $a \times b$ cannot be bigger than the two most significant bits of $n$. We have

$$\left \lbrace \begin{align*}
i \oplus b & = 0 \\
a \oplus j & = 0 \\
i \times j & \equiv 1  \pmod 2 \\
a \times b & \leq n[:2] \\
\end{align*} \right.$$

The tricky part is figuring out the condition on the MSB of $n = p \times q$, as the result depends of the carry bit of mulitplication. To try and figure out a condition I wanted to maximise the distance between the MSB of $p \times q$ and the MSB of $n$.

For instance the largest value we can get for the two last bits of $n$ is $11$ which can be obtained if all the bits of $p$ and $q$ are set to 1, thanks to the carry propagation. But this is not obtainable when we only have information on the MSB of $p$ and $q$. And so the largest value we can get for these two last bits is $01$. (We suppose that the unknown bits are set to $0$ in the implementation). In that case we have a difference of $2$.

If we now consider that we are at our $k$-th iteration, in a similar manner I considered that at each step the maximal distance that can is acceptable between the $k$ most significant bits of $n$ and the $k+1$ most significant bits of $p \times q$ is $k + 1$.

## Proof of the carry propagation property

In order to prove this property let's the multiplication with the highest carry on each column, this is obtained when $p$ and $q$ two $l$ length numbers consisting of $l$ $1$'s. In that case the carry is incremented by $1$ for the first $l+2$ bits. and then decreases for the last $l-1$ bits. This can be proven by recursion.

> Thus when considering the $k$-th most significant bit of $p \times q$ we have at most a carry of $k$.

If you want to see what it looks like in an example, let's consider the following with 5 bits. Now let's calculate $p \times q$ as if we were back in elementary school.
```txt
p =         11111
q =         11111
-----------------
=           11111
+          111110
+         1111100
+        11111000
+       111110000
-----------------
sum     123454321 in base 10
carry  1234432100 in base 10
-----------------
result 1111000001 in base 2
```

## Generalisation to the $k$-th step

Let's suppose the $k$ most significant and least significant bits of $p$ and $q$. Let's call these hypothetic solutions $p'$ and $q'$.
Let's call $m$ the mask which is $1...10...01...1$ with $k$ bits set to 1 at the beginning and at the end, and $1024 - 2k$ bits set to 0 in the middle.
Let's call $x$ the reversed xor of $p$ and $q$, i.e. $x = p \oplus q[::-1]$.
Let's call $n$ the product of $p$ and $q$, i.e. $n = p \times q$.
Let's call $(A)_{\to i}$ the number that is constituted of the $i$ most significant bit of any given $A$ (It's a right shift of $2048-i$ for a 2048 bit integer).

The conditions they must satisfy are:

$$\left \lbrace \begin{align*}
p' \oplus q'[::-1] \land m &= x \\
p' \times q' &\equiv n \pmod {2^{k}} \\
(p' \times q')\_{\to k+1} &\leq n\_{\to k+1} \\
n_{\to k +1} - (p' \times q')\_{\to k +1} & \leq k+1 \\
\end{align*} \right.$$

Now to solve the problem we have a stack of coupes $(p, q)$ that are possible. we unpile them, add 4 cases to the stack (one for each couple of bits we are adding to the most significant and least significant) and check if they satisfy the conditions. We stop when a couple $(p, q)$ satisfies the conditions and we can compute the private key.

Once this couple is found, decryption is straightforward RSA decryption, the private key is computed as follows:
$$d = e^{-1} \mod \phi(n)$$

where $e$ is the public exponent and $\phi(n) = (p-1)(q-1)$.

Then we can decrypt the ciphertext $c$ using the formula:
$$m = c^{d} \mod n$$

where $c$ is the ciphertext and $d$ is the private key.

## Implementation in python

Python is a really bad language when it comes to manipulating bits, but I wanted to draft a quick program to try the idea and see if the complexity was good enough. To represent the bits I used an array of booleans :sweat_smile:.

[boolean_solve.py](boolean_solve.py)

## Implementation in C with GMP and multi-threading

Once I was convinced it was going to work and realised that the complete execution would take about an hour, I decided to rewrite it in C, using `gmp` to handle the big integers. The resolution took about 15 minutes on my computer. But told myself I could accelerate this even more by multi-threading the elimination of the branches. This is the final implementation which took 2 minutes to solve the challenge.

[solve.c](solve.c)
