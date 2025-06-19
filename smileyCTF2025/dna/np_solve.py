import re

import numpy as np

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
            var_address = int(load_match.group(1))
            # Look ahead for the multiply operation
            if i + 2 < len(lines):
                next_line = lines[i + 1].strip()
                multiply_line = lines[i + 2].strip()

                if 'Push immediate' in next_line and 'Multiply' in multiply_line:
                    coeff_match = re.search(r'Push immediate (\d+)', next_line)
                    if coeff_match:
                        coefficient = int(coeff_match.group(1))
                        current_variables.append(var_address)
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


def solve_with_numpy(constraints, expected_values):
    """
    Build and solve the linear system using NumPy
    """
    print("Building NumPy linear system...")

    # Find all unique variables
    all_vars = set()
    for constraint in constraints:
        all_vars.update(constraint['variables'])

    var_list = sorted(list(all_vars))
    n_vars = len(var_list)
    var_to_index = {var: i for i, var in enumerate(var_list)}

    print(f"Variables: {n_vars} variables from memory[{min(var_list)}] to memory[{max(var_list)}]")

    # Build coefficient matrix A and result vector b
    valid_constraints = []
    for constraint in constraints:
        if constraint['result_address'] in expected_values:
            valid_constraints.append(constraint)

    n_constraints = len(valid_constraints)
    print(f"Valid constraints: {n_constraints}")

    # Add known values as constraints
    n_known = len(known_values)
    total_constraints = n_constraints + n_known

    A = np.zeros((total_constraints, n_vars))
    b = np.zeros(total_constraints)

    # Add regular constraints
    for i, constraint in enumerate(valid_constraints):
        for var, coeff in zip(constraint['variables'], constraint['coefficients']):
            if var in var_to_index:
                A[i, var_to_index[var]] = coeff
        b[i] = expected_values[constraint['result_address']]

    # Add known values as constraints
    for i, (var, value) in enumerate(known_values.items()):
        if var in var_to_index:
            constraint_idx = n_constraints + i
            A[constraint_idx, var_to_index[var]] = 1
            b[constraint_idx] = value

    print(f"System matrix A: {A.shape}")
    print(f"Result vector b: {b.shape}")
    print(f"Rank of A: {np.linalg.matrix_rank(A)}")

    # Try different numpy solvers
    solutions = {}

    # Method 1: Least squares (works for overdetermined systems)
    try:
        print("\nTrying least squares solution...")
        x_lstsq, residual, rank, s = np.linalg.lstsq(A, b, rcond=None)
        solutions['lstsq'] = x_lstsq
        print(f"Least squares - Residual: {residual}")
        print(f"Least squares - Rank: {rank}")
    except Exception as e:
        print(f"Least squares failed: {e}")

    # Method 2: Pseudo-inverse
    try:
        print("\nTrying pseudo-inverse solution...")
        A_pinv = np.linalg.pinv(A)
        x_pinv = A_pinv @ b
        solutions['pinv'] = x_pinv
        residual_pinv = np.linalg.norm(A @ x_pinv - b)
        print(f"Pseudo-inverse - Residual: {residual_pinv}")
    except Exception as e:
        print(f"Pseudo-inverse failed: {e}")

    # Method 3: Try direct solve if system is square
    try:
        print("\nTrying direct solve (square system)...")
        x_solve = np.linalg.solve(A[:49, :49], b[:49])
        solutions['solve'] = x_solve
        residual_solve = np.linalg.norm(A[:49, :49] @ x_solve - b[:49])
        print(f"Direct solve - Residual: {residual_solve}")
    except Exception as e:
        print(f"Direct solve failed: {e}")  # Choose best solution (lowest residual)
    if solutions:
        best_method = None
        best_residual = float('inf')
        best_solution = None

        print("\nComparing all solutions:")
        print("=" * 50)

        for method, sol in solutions.items():
            residual = np.linalg.norm(A @ sol - b)
            print(f"\n{method.upper()} METHOD:")
            print(f"Residual: {residual}")

            # Convert to integer and show string
            int_sol = {}
            chars = []
            for i, var in enumerate(var_list):
                value = sol[i]
                int_value = max(32, min(126, int(round(value))))
                int_sol[var] = int_value
                chars.append(chr(int_value))

            solution_string = ''.join(chars)
            print(f"String: {solution_string}")
            print(f"First 10 values: {[int_sol[var] for var in var_list[:10]]}")

            if residual < best_residual:
                best_residual = residual
                best_solution = sol
                best_method = method

        print(f"\nBest solution: {best_method} (residual: {best_residual})")

        # Convert to integer solution
        int_solution = {}
        for i, var in enumerate(var_list):
            value = best_solution[i]
            # Round to nearest integer and clamp to ASCII range
            int_value = max(32, min(126, int(round(value))))
            int_solution[var] = int_value

        return int_solution, var_list, best_residual

    return None, var_list, float('inf')


def print_solution(solution, var_list, residual=None):
    """
    Print the solution in a readable format
    """
    if solution is None:
        print("No solution to display")
        return None, None

    print("\nSOLUTION FOUND!")
    if residual is not None:
        print(f"Residual: {residual}")
    print("=" * 60)

    # Print as characters
    chars = []
    values = []
    print("Memory values as characters:")
    for var in var_list:
        value = solution[var]
        char = chr(value) if 32 <= value <= 126 else '?'
        chars.append(char)
        values.append(value)
        print(f"memory[{var}] = {value} ('{char}')")

    print(f"\nComplete string: {''.join(chars)}")
    print(f"String length: {len(chars)}")

    return np.array(values), chars


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

    # Solve with NumPy
    from time import time

    start_time = time()
    solution, var_list, residual = solve_with_numpy(constraints, expected_values)
    end_time = time()
    print(f"Solved in {end_time - start_time} seconds")
    if solution:
        np_array, chars = print_solution(solution, var_list, residual)

        # Save solution
        with open("solution.txt", "w") as f:
            f.write("NumPy Solution:\n")
            f.write(f"Residual: {residual}\n\n")
            for var in var_list:
                value = solution[var]
                char = chr(value) if 32 <= value <= 126 else '?'
                f.write(f"memory[{var}] = {value} ('{char}')\n")
            f.write(f"\nComplete string: {''.join(chars)}\n")

        print("\nSolution saved to 'solution.txt'")
    else:
        print("No solution found!")


if __name__ == "__main__":
    main()
