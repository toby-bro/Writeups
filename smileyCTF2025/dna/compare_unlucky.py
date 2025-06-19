import dis
import marshal
import sys
from io import StringIO

# Load your reversed functions
exec(open('unluckyfuncs.py').read())

# Original disassembly keys from your analysis
original_keys = [111, 117, 105, 97]
functions = [unlucky_1, unlucky_2, unlucky_3, unlucky_4]


def get_disassembly_string(code_obj):
    """Capture disassembly output as string"""
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    dis.dis(code_obj)
    output = sys.stdout.getvalue()
    sys.stdout = old_stdout
    return output


print("Comparing reversed functions with original bytecode...\n")

for i, (func, key) in enumerate(zip(functions, original_keys)):
    print(f"=== Function [{i}] (Key {key}) ===")

    # Get reversed function bytecode
    reversed_bytecode = get_disassembly_string(func.__code__)

    # Load original bytecode from unlucky data
    from unlu import unlucky

    try:
        original_bytecode_raw = bytes(b ^ key for b in unlucky[i])
        original_code_obj = marshal.loads(original_bytecode_raw)
        original_bytecode = get_disassembly_string(original_code_obj)

        def print_bytecode():
            print("REVERSED FUNCTION:")
            print(reversed_bytecode)
            print("\nORIGINAL FUNCTION:")
            print(original_bytecode)

        # Simple comparison (note: line numbers and some details may differ)
        if len(reversed_bytecode.split('\n')) == len(original_bytecode.split('\n')):
            print("✓ Bytecode length matches")
        else:
            print("✗ Bytecode length differs")

        # Check if main opcodes are similar
        reversed_opcodes = [
            line.strip().split()[1]
            for line in reversed_bytecode.split('\n')
            if line.strip() and len(line.strip().split()) > 1 and not line.strip().split()[0].startswith('--')
        ]
        original_opcodes = [
            line.strip().split()[1]
            for line in original_bytecode.split('\n')
            if line.strip() and len(line.strip().split()) > 1 and not line.strip().split()[0].startswith('--')
        ]

        if reversed_opcodes == original_opcodes:
            print("✓ Opcodes match perfectly")
        else:
            print("✗ Opcodes differ")
            print(f"Reversed opcodes: {len(reversed_opcodes)} vs Original opcodes: {len(original_opcodes)}")
            print_bytecode()

    except Exception as e:
        print(f"Error loading original bytecode: {e}")

    print("-" * 80)
