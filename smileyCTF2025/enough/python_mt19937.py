#!/usr/bin/env python3
"""
Python-compatible MT19937 implementation.
This implements the exact same initialization that Python's random module uses.
"""


def _int32(x: int) -> int:
    """Get the 32 least significant bits."""
    return int(0xFFFFFFFF & x)


class PythonMT19937:
    def __init__(self, seed: int | None = None) -> None:
        self.N = 624
        self.M = 397
        self.MATRIX_A = 0x9908B0DF
        self.UPPER_MASK = 0x80000000
        self.LOWER_MASK = 0x7FFFFFFF

        self.mt = [0] * self.N
        self.mti = self.N + 1  # Uninitialized state

        if seed is not None:
            self.init_by_seed(seed)

    def init_genrand(self, s: int) -> None:
        """Initialize with a single 32-bit seed (from original C code)."""
        self.mt[0] = _int32(s)
        for self.mti in range(1, self.N):
            self.mt[self.mti] = _int32(1812433253 * (self.mt[self.mti - 1] ^ (self.mt[self.mti - 1] >> 30)) + self.mti)
        self.mti = self.N

    def init_by_array(self, init_key: list[int]) -> None:
        """Initialize by array (from original C code)."""
        key_length = len(init_key)
        self.init_genrand(19650218)

        i = 1
        j = 0
        k = max(self.N, key_length)

        for _ in range(k):
            self.mt[i] = _int32((self.mt[i] ^ ((self.mt[i - 1] ^ (self.mt[i - 1] >> 30)) * 1664525)) + init_key[j] + j)
            i += 1
            j += 1
            if i >= self.N:
                self.mt[0] = self.mt[self.N - 1]
                i = 1
            if j >= key_length:
                j = 0

        for _ in range(self.N - 1):
            self.mt[i] = _int32((self.mt[i] ^ ((self.mt[i - 1] ^ (self.mt[i - 1] >> 30)) * 1566083941)) - i)
            i += 1
            if i >= self.N:
                self.mt[0] = self.mt[self.N - 1]
                i = 1

        self.mt[0] = 0x80000000  # MSB is 1; assuring non-zero initial array
        self.mti = self.N

    def init_by_seed(self, seed: int) -> None:
        """Initialize using Python's seed conversion method."""
        if isinstance(seed, int):
            if seed == 0:
                key = [0]
            else:
                key = []
                if seed < 0:
                    seed = -seed
                while seed:
                    key.append(seed & 0xFFFFFFFF)
                    seed >>= 32
            self.init_by_array(key)
        else:
            self.init_genrand(seed if seed is not None else 0)

    def genrand_int32(self) -> int:
        """Generate a 32-bit integer."""
        if self.mti >= self.N:
            if self.mti == self.N + 1:
                self.init_genrand(5489)  # Default seed
            self.twist()

        y = self.mt[self.mti]
        self.mti += 1

        # Tempering
        y ^= y >> 11
        y ^= (y << 7) & 0x9D2C5680
        y ^= (y << 15) & 0xEFC60000
        y ^= y >> 18

        return _int32(y)

    def twist(self) -> None:
        """Twist the state (generate N words at one time)."""
        mag01 = [0x0, self.MATRIX_A]

        for kk in range(self.N - self.M):
            y = (self.mt[kk] & self.UPPER_MASK) | (self.mt[kk + 1] & self.LOWER_MASK)
            self.mt[kk] = self.mt[kk + self.M] ^ (y >> 1) ^ mag01[y & 0x1]

        for kk in range(self.N - self.M, self.N - 1):
            y = (self.mt[kk] & self.UPPER_MASK) | (self.mt[kk + 1] & self.LOWER_MASK)
            self.mt[kk] = self.mt[kk + (self.M - self.N)] ^ (y >> 1) ^ mag01[y & 0x1]

        y = (self.mt[self.N - 1] & self.UPPER_MASK) | (self.mt[0] & self.LOWER_MASK)
        self.mt[self.N - 1] = self.mt[self.M - 1] ^ (y >> 1) ^ mag01[y & 0x1]

        self.mti = 0

    def getrandbits(self, bits: int) -> int:
        """Get random bits (compatible with Python's interface)."""
        if bits <= 32:
            return self.genrand_int32() >> (32 - bits)
        else:
            # For > 32 bits, combine multiple 32-bit values
            result = 0
            remaining = bits
            while remaining > 0:
                chunk = min(32, remaining)
                result = (result << chunk) | (self.genrand_int32() >> (32 - chunk))
                remaining -= chunk
            return result

    def getstate(self) -> tuple[int, tuple[int, ...], None]:
        """Get the internal state (Python-compatible format)."""
        return (3, tuple(self.mt + [self.mti]), None)


def test_python_compatibility() -> None:
    """Test that our implementation matches Python's random module."""
    import random

    # Test with same seed
    seed = 12345

    # Python's random
    py_rand = random.Random(seed)
    py_outputs = [py_rand.getrandbits(32) for _ in range(900)]

    # Our implementation
    our_rand = PythonMT19937(seed)
    our_outputs = [our_rand.getrandbits(32) for _ in range(900)]

    print("Python outputs:", py_outputs)
    print("Our outputs:   ", our_outputs)
    print("Match:", py_outputs == our_outputs)

    # Test state compatibility
    py_rand2 = random.Random(seed)
    py_state = py_rand2.getstate()
    print(f"\nPython state: version={py_state[0]}, len={len(py_state[1])}, index={py_state[1][624]}")

    our_rand2 = PythonMT19937(seed)
    our_state = our_rand2.getstate()
    print(f"Our state: version={our_state[0]}, len={len(our_state[1])}, index={our_state[1][624]}")

    # Test if states are the same
    print("States match:", py_state[1] == our_state[1])


if __name__ == "__main__":
    test_python_compatibility()
