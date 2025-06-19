import re
import numpy as np

from z3 import Int, Solver, sat

known_values = {26: 111, 27: 117, 22: 105, 33: 97}


def parse_operations_log(filename):
    """
    Parse the operations log to extract linear constraints.
    Each constraint is of the form: sum(coefficient * variable) = expected_value
    """

    constraints = []
    current_coefficients = []
    current_variables = []
    in_constraint = False
    store_address = None

    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        with open('dna/' + filename, 'r') as file:
            lines = file.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Look for Load from memory pattern
        load_match = re.search(r'Load from memory\[(\d+)\]', line)
        if load_match:
            var_address = int(load_match.group(1))  # Fix: convert to int
            # Look ahead for the multiply operation
            if i + 2 < len(lines):
                next_line = lines[i + 1].strip()
                multiply_line = lines[i + 2].strip()

                if 'Push immediate' in next_line and 'Multiply' in multiply_line:
                    coeff_match = re.search(r'Push immediate (\d+)', next_line)
                    if coeff_match:
                        coefficient = int(coeff_match.group(1))
                        current_variables.append(var_address)  # Fix: use var_address
                        current_coefficients.append(coefficient)
                        in_constraint = True
                        i += 3
                        continue

        # Look for Store to memory pattern (end of constraint)
        store_match = re.search(r'Store to memory\[(\d+)\]', line)
        if store_match and in_constraint:
            store_address = int(store_match.group(1))

            # Create constraint
            constraint = {
                'variables': current_variables.copy(),
                'coefficients': current_coefficients.copy(),
                'result_address': store_address,
            }
            constraints.append(constraint)

            # Reset for next constraint
            current_variables = []
            current_coefficients = []
            in_constraint = False
            store_address = None

        # Look for Add operations (continue building current constraint)
        elif 'Add' in line and in_constraint:
            pass  # Just continue, we're still in the same constraint

        i += 1

    return constraints


def extract_expected_values(filename):
    """
    Extract the expected values from comparison operations
    """
    expected_values = {}

    with open(filename, 'r') as file:
        lines = file.readlines()

    # Look for comparison patterns at the end
    for i, line in enumerate(lines):
        line = line.strip()

        # Look for Load from memory followed by Push immediate and Compare equal
        load_match = re.search(r'Load from memory\[(\d+)\]', line)
        if load_match and i + 2 < len(lines):
            next_line = lines[i + 1].strip()
            compare_line = lines[i + 2].strip()

            if 'Push immediate' in next_line and 'Compare equal' in compare_line:
                address = int(load_match.group(1))
                value_match = re.search(r'Push immediate (\d+)', next_line)
                if value_match:
                    expected_values[address] = int(value_match.group(1))

    return expected_values


def create_z3_system(constraints, expected_values):
    """
    Create and solve the Z3 system progressively
    """
    print("Creating Z3 system...")

    # Find all unique variables
    all_vars = set()
    for constraint in constraints:
        all_vars.update(constraint['variables'])

    var_list = sorted(list(all_vars))
    print(f"Variables found: {len(var_list)} variables from memory[{min(var_list)}] to memory[{max(var_list)}]")

    # Create Z3 variables
    z3_vars = {}
    for var in var_list:
        z3_vars[var] = Int(f'mem_{var}')

    # Create solver
    solver = Solver()

    # Add constraints progressively
    print(f"\nAdding {len(constraints)} constraints...")
    for i, constraint in enumerate(constraints):
        # Build the linear equation
        terms = []
        for var, coeff in zip(constraint['variables'], constraint['coefficients']):
            terms.append(coeff * z3_vars[var])

        lhs = sum(terms)
        result_addr = constraint['result_address']

        if result_addr in expected_values:
            rhs = expected_values[result_addr]
            solver.add(lhs == rhs)
            print(f"Constraint {i+1}: Sum of {len(terms)} terms = {rhs} (memory[{result_addr}])")
        else:
            print(f"Warning: No expected value for constraint {i+1} (memory[{result_addr}])")

    # Add known values
    print(f"\nAdding {len(known_values)} known values...")
    for addr, value in known_values.items():
        if addr in z3_vars:
            solver.add(z3_vars[addr] == value)
            print(f"Known: memory[{addr}] = {value} ('{chr(value)}')")

    # Add ASCII constraints (printable characters)
    print(f"\nAdding ASCII constraints (32-126) for {len(var_list)} variables...")
    for var in var_list:
        solver.add(z3_vars[var] >= 32)
        solver.add(z3_vars[var] <= 126)

    print("\nSolving system...")
    if solver.check() == sat:
        model = solver.model()
        solution = {}
        for var in var_list:
            solution[var] = model.evaluate(z3_vars[var]).as_long()
        return solution, var_list
    else:
        print("No solution found!")
        return None, var_list


def print_solution(solution, var_list):
    """
    Print the solution in a readable format
    """
    if solution is None:
        print("No solution to display")
        return

    print("\nSOLUTION FOUND!")
    print("=" * 60)

    # Print as characters
    chars = []
    print("Memory values as characters:")
    for var in var_list:
        value = solution[var]
        char = chr(value) if 32 <= value <= 126 else '?'
        chars.append(char)
        print(f"memory[{var}] = {value} ('{char}')")

    print(f"\nComplete string: {''.join(chars)}")
    print(f"String length: {len(chars)}")


def main():
    filename = "operations.log"

    print("Parsing operations log...")
    constraints = parse_operations_log(filename)
    print(f"Found {len(constraints)} constraints")

    print("Extracting expected values...")
    expected_values = extract_expected_values(filename)
    print(f"Found {len(expected_values)} expected values")

    # Show some examples
    if constraints:
        print("\nExample constraint:")
        c = constraints[0]
        print(f"  Variables: {c['variables'][:5]}{'...' if len(c['variables']) > 5 else ''}")
        print(f"  Coefficients: {c['coefficients'][:5]}{'...' if len(c['coefficients']) > 5 else ''}")
        print(f"  Result stored at: memory[{c['result_address']}]")
        if c['result_address'] in expected_values:
            print(f"  Expected value: {expected_values[c['result_address']]}")

    # Create and solve Z3 system
    solution, var_list = create_z3_system(constraints, expected_values)

    # Print solution
    print_solution(solution, var_list)

    # Save solution to file
    if solution:
        with open("solution.txt", "w") as f:
            f.write("Memory Solution:\n")
            for var in var_list:
                value = solution[var]
                char = chr(value) if 32 <= value <= 126 else '?'
                f.write(f"memory[{var}] = {value} ('{char}')\n")

            f.write("\nComplete string: .;,;.{" + ''.join(chr(solution[var]) for var in var_list) + "}\n")

        print("\nSolution saved to 'solution.txt'")


if __name__ == "__main__":
    main()
