#!/usr/bin/env python3
"""
Solve the CTF challenge by recovering the missing 12 bits from partial MT19937 outputs.
"""

import sys
from hashlib import sha256

import z3  # type: ignore[import-untyped]
from Crypto.Cipher import AES
from mt19937_z3 import Z3_MT19937
from out import given, hex_enc_flag
from python_mt19937 import PythonMT19937


def solve_ctf() -> bool:
    print("🎯 Starting Mersenne twister solver...")
    print(f"📊 Number of partial outputs: {len(given)}")
    print(f"🔒 Encrypted flag: {hex_enc_flag[:50]}...")

    # Create Z3 solver
    print("\n🔧 Setting up Z3 solver...")
    z3_mt = Z3_MT19937()

    # We don't know the seed, so we'll let Z3 find it
    # The initial state will be symbolic
    print("✅ Created symbolic MT19937 state")

    print(f"📝 Adding constraints for {len(given)} partial outputs...")

    for i, upper_20_bits in enumerate(given):
        z3_mt.add_constraint_partial_output(i, upper_20_bits, 20)
        if (i + 1) % 100 == 0:
            print(f"   ✓ Added constraint {i + 1}/{len(given)}")

    print("🔍 Solving constraints...")
    result = z3_mt.solve()

    if result == z3.sat:
        print("🎉 Solution found!")

        # Get the model... this can be veeeery long... there is a difference between knowing a problem is SAT and actually getting the model
        print("🔓 Retrieving model...")
        model = z3_mt.get_model()

        if model is None:
            print("❌ Could not retrieve model")
            return False

        # Recover the initial state from model
        print("🔓 Recovering initial state from model...")

        # Get the initial state values from the model
        initial_state = z3_mt.get_initial_state_values(model)
        if initial_state is None:
            print("❌ Could not extract initial state from model")
            return False

        print("✅ Initial state recovered!")

        # Reconstruct the MT19937 generator with the recovered state
        recovered_mt = PythonMT19937()
        recovered_mt.mt = initial_state[:]
        recovered_mt.mti = 624  # Start with index that triggers immediate twist (like Python)

        print("🔓 Generating full 32-bit outputs...")
        recovered_outputs = []

        for i in range(len(given)):
            full_output = recovered_mt.getrandbits(32)
            recovered_outputs.append(full_output)

            # Verify the upper 20 bits match
            recovered_upper = full_output >> 12
            if recovered_upper != given[i]:
                print(f"❌ Mismatch at output {i}: expected {given[i]}, got {recovered_upper}")
                print(f"   Full output: 0x{full_output:08x}")
                print(f"   Expected upper: {given[i]}, got: {recovered_upper}")
                return False

        print("✅ All outputs recovered and verified!")

        print("🔑 Reconstructing encryption key...")
        key_parts = []
        for output in recovered_outputs:
            lower_12_bits = output & 0xFFF  # 2^12 - 1
            key_parts.append(str(lower_12_bits))

        key_string = ''.join(key_parts)[:100]
        key = sha256(key_string.encode()).digest()

        print(f"🔐 Key string (first 50 chars): {key_string[:50]}...")
        print(f"🔐 SHA256 key: {key.hex()[:32]}...")

        print("🚩 Decrypting flag...")
        try:
            cipher = AES.new(key, AES.MODE_ECB)
            ciphertext = bytes.fromhex(hex_enc_flag)
            plaintext = cipher.decrypt(ciphertext)

            flag = plaintext.rstrip(b'\x00')

            print(f"🎉 FLAG: {flag.decode()}")
            return True

        except Exception as e:
            print(f"❌ Decryption failed: {e}")
            return False

    else:
        print("❌ No solution found - constraints are UNSAT")
        return False


def solve_ctf_incremental() -> bool:
    """Try solving with fewer constraints first to check if approach works."""
    print("🔬 Testing incremental approach...")

    # Start with just a few outputs
    test_sizes = [50, 226, 227, 624, 625, 700]

    for test_size in test_sizes:
        print(f"\n🧪 Testing with {test_size} outputs...")

        z3_mt = Z3_MT19937()

        for i in range(min(test_size, len(given))):
            z3_mt.add_constraint_partial_output(i, given[i], 20)

        print(f"🔍 Solving with {test_size} constraints...")
        result = z3_mt.solve()

        print(f"Result for {test_size} outputs: {result}")

        if result == z3.sat:
            print(f"✅ {test_size} outputs: SAT")
        else:
            print(f"❌ {test_size} outputs: UNSAT")
            return False

    return True


if __name__ == "__main__":
    print("🎮 Never Enough solver")
    print("=" * 50)

    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        success = solve_ctf_incremental()
        if not success:
            print("❌ Incremental test failed")
            sys.exit(1)

    success = solve_ctf()

    if success:
        print("\n🏆 CTF challenge solved successfully!")
    else:
        print("\n💥 CTF challenge failed")
        sys.exit(1)
