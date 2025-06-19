import dis
import marshal

from unlu import unlucky

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
