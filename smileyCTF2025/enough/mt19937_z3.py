#!/usr/bin/env python3

from typing import TYPE_CHECKING

import z3  # type: ignore[import-untyped]

N = 624
M = 397
MATRIX_A = 0x9908B0DF
UPPER_MASK = 0x80000000
LOWER_MASK = 0x7FFFFFFF

# Tempering constants
TEMPERING_MASK_B = 0x9D2C5680
TEMPERING_MASK_C = 0xEFC60000
TEMPERING_SHIFT_U = 11
TEMPERING_SHIFT_S = 7
TEMPERING_SHIFT_T = 15
TEMPERING_SHIFT_L = 18


def z3_int32(value: z3.BitVecRef) -> z3.BitVecRef:
    return value & 0xFFFFFFFF


def z3_temper(value: z3.BitVecRef) -> z3.BitVecRef:
    value = value ^ z3.LShR(value, TEMPERING_SHIFT_U)
    value = value ^ ((value << TEMPERING_SHIFT_S) & TEMPERING_MASK_B)
    value = value ^ ((value << TEMPERING_SHIFT_T) & TEMPERING_MASK_C)
    value = value ^ z3.LShR(value, TEMPERING_SHIFT_L)
    return z3_int32(value)


def z3_untemper(value: z3.BitVecRef) -> z3.BitVecRef:
    value = z3_unshift_right_xor(value, TEMPERING_SHIFT_L)
    value = z3_unshift_left_mask_xor(value, TEMPERING_SHIFT_T, TEMPERING_MASK_C)
    value = z3_unshift_left_mask_xor(value, TEMPERING_SHIFT_S, TEMPERING_MASK_B)
    value = z3_unshift_right_xor(value, TEMPERING_SHIFT_U)
    return z3_int32(value)


def z3_unshift_right_xor(value: z3.BitVecRef, shift: int) -> z3.BitVecRef:
    """
    Reverse a right shift XOR operation using Z3.
    Implements: result = result ^ (result >> shift)
    """
    result = z3.BitVecVal(0, 32)
    for i in range(32 // shift + 1):
        result ^= z3.LShR(value, shift * i)
    return z3_int32(result)


def z3_unshift_left_mask_xor(value: z3.BitVecRef, shift: int, mask: int) -> z3.BitVecRef:
    """
    Reverse a left shift mask XOR operation using Z3.
    Implements: result = result ^ ((result << shift) & mask)
    """
    result = z3.BitVecVal(0, 32)
    for i in range(0, 32 // shift + 1):
        part_mask = ((0xFFFFFFFF >> (32 - shift)) << (shift * i)) & 0xFFFFFFFF
        part = value & part_mask
        value ^= (part << shift) & mask
        result |= part
    return z3_int32(result)


def z3_add_twist_constraints(
    solver: z3.Solver, mt_before: list[z3.BitVecRef], mt_after: list[z3.BitVecRef], twist_id: str = ""
) -> None:
    mt_after_first_loop = [z3.BitVec(f"after_first_{twist_id}_{i}", 32) for i in range(N)]

    # First loop: modifies elements 0-226
    twist_first_loop(solver, mt_before, mt_after_first_loop)

    # Elements 227-623 remain unchanged after first loop
    for i in range(N - M, N):
        solver.add(mt_after_first_loop[i] == mt_before[i])

    # Now for the second loop, we need to model the in-place modification correctly
    # We'll create intermediate states for each step of the second loop
    current_state = mt_after_first_loop

    # Second loop: modifies elements 227-622, one by one
    current_state = twist_second_loop(solver, twist_id, current_state)

    # Special case for element 623
    kk = N - 1  # 623
    final_state = [z3.BitVec(f"final_{twist_id}_{i}", 32) for i in range(N)]

    y = z3_int32((current_state[kk] & UPPER_MASK) | (current_state[0] & LOWER_MASK))
    new_value = current_state[M - 1] ^ z3.LShR(y, 1)  # M - 1 is equal to 396
    new_value = z3.If((y & 1) == 1, new_value ^ MATRIX_A, new_value)
    if TYPE_CHECKING:
        assert isinstance(new_value, z3.BitVecRef), "Expected new_value to be a BitVecRef"

    # Set the constraints for the final step
    for i in range(N):
        if i == kk:
            solver.add(final_state[i] == z3_int32(new_value))
        else:
            solver.add(final_state[i] == current_state[i])

    # Final result: mt_after equals the final state
    for i in range(N):
        solver.add(mt_after[i] == final_state[i])


def twist_first_loop(solver: z3.Solver, mt_before: list[z3.BitVecRef], mt_after_first_loop: list[z3.BitVecRef]) -> None:
    for kk in range(N - M):
        y = z3_int32((mt_before[kk] & UPPER_MASK) | (mt_before[kk + 1] & LOWER_MASK))
        new_value = mt_before[kk + M] ^ z3.LShR(y, 1)
        new_value = z3.If((y & 1) == 1, new_value ^ MATRIX_A, new_value)
        if TYPE_CHECKING:
            assert isinstance(new_value, z3.BitVecRef), "Expected new_value to be a BitVecRef"
        solver.add(mt_after_first_loop[kk] == z3_int32(new_value))


def twist_second_loop(solver: z3.Solver, twist_id: str, current_state: list[z3.BitVecRef]) -> list[z3.BitVecRef]:
    for kk in range(N - M, N - 1):
        # Create new state after modifying element kk
        next_state = [z3.BitVec(f"step2_{twist_id}_{kk}_{i}", 32) for i in range(N)]

        # Calculate the new value for position kk
        y = z3_int32((current_state[kk] & UPPER_MASK) | (current_state[kk + 1] & LOWER_MASK))
        offset = kk + (M - N)  # kk - 227, gives 0 to 395
        new_value = current_state[offset] ^ z3.LShR(y, 1)
        new_value = z3.If((y & 1) == 1, new_value ^ MATRIX_A, new_value)
        if TYPE_CHECKING:
            assert isinstance(new_value, z3.BitVecRef), "Expected new_value to be a BitVecRef"

        # Set the constraints: only position kk changes, others stay the same
        for i in range(N):
            if i == kk:
                solver.add(next_state[i] == z3_int32(new_value))
            else:
                solver.add(next_state[i] == current_state[i])

        current_state = next_state
    return current_state


def z3_extract_number(mt_array: list[z3.BitVecRef], index: int) -> z3.BitVecRef:
    """
    Extract a tempered number from the MT19937 state array using Z3.
    This is equivalent to calling extract_number() in the reference implementation.
    """
    # Get the raw value from the state
    y = mt_array[index]

    # Apply tempering
    tempered = z3_temper(y)

    return z3_int32(tempered)


class Z3_MT19937:
    def __init__(self, solver: z3.Solver | None = None) -> None:
        self.solver = solver if solver else z3.Solver()
        self.N = 624
        self.M = 397
        self.MATRIX_A = 0x9908B0DF
        self.UPPER_MASK = 0x80000000
        self.LOWER_MASK = 0x7FFFFFFF

        # Create symbolic state array for the initial state
        self.mt_initial = [z3.BitVec(f"mt_init_{i}", 32) for i in range(self.N)]

        # Track states after each twist operation
        self.states = [self.mt_initial]  # states[0] is initial, states[1] after first twist, etc.

        # Initial index (Python starts with 624, triggering immediate twist)
        self.initial_index = z3.BitVec("initial_index", 32)

    def ensure_state_exists(self, twist_count: int) -> None:
        """
        Ensure that we have symbolic variables for the state after twist_count twists.
        """
        while len(self.states) <= twist_count:
            # Create new state after one more twist
            prev_state = self.states[-1]
            twist_id = len(self.states)  # Use twist number as unique ID
            new_state = [z3.BitVec(f"mt_twist_{twist_id}_{i}", 32) for i in range(self.N)]

            # Add constraints that new_state is prev_state after twisting
            z3_add_twist_constraints(self.solver, prev_state, new_state, str(twist_id))

            self.states.append(new_state)

    def add_constraint_output(self, output_index: int, expected_value: int) -> None:
        """
        Add a constraint that the output at the given index equals the expected value.
        This properly handles the initial index and twisting for Python's getrandbits().

        Python's behavior:
        - Starts with index = 624 (triggers immediate twist)
        - Output 0 comes from states[1] at index 0 (after first twist)
        - Output i comes from states[1 + i//624] at index i%624
        """
        # Calculate which twist state and index
        twist_count = 1 + (output_index // self.N)
        state_index = output_index % self.N

        # Ensure we have the required state
        self.ensure_state_exists(twist_count)
        current_state = self.states[twist_count]

        # Extract and constrain the output
        output = z3_extract_number(current_state, state_index)
        self.solver.add(output == expected_value)

    def add_constraint_partial_output(self, output_index: int, upper_bits: int, num_upper_bits: int) -> None:
        """
        Add a constraint for partial output (only upper bits known).
        Uses the same logic as add_constraint_output.
        """
        # Calculate which twist state and index
        twist_count = 1 + (output_index // self.N)
        state_index = output_index % self.N

        # Ensure we have the required state
        self.ensure_state_exists(twist_count)
        current_state = self.states[twist_count]

        # Extract the output
        output = z3_extract_number(current_state, state_index)

        # Constrain only the upper bits
        upper_mask = (0xFFFFFFFF << (32 - num_upper_bits)) & 0xFFFFFFFF
        self.solver.add((output & upper_mask) == (upper_bits << (32 - num_upper_bits)))

    def solve(self) -> z3.CheckSatResult:
        return self.solver.check()

    def get_model(self) -> z3.ModelRef | None:
        """Get the model (solution) if SAT."""
        if self.solver.check() == z3.sat:
            return self.solver.model()
        return None

    def get_initial_state_values(self, model: z3.ModelRef) -> list[int] | None:
        """Extract the concrete initial state values from a model."""
        if model is None:
            return None

        state = []
        for i in range(self.N):
            val = model[self.mt_initial[i]]
            if val is None:
                return None
            state.append(val.as_long())

        return state
