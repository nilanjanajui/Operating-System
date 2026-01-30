# 16. Memory Allocation

import sys

def read_input():
    try:
        B = int(input("Enter number of blocks (B): ").strip())
        if B <= 0:
            print("ERROR: E_RANGE: B and P must be positive")
            sys.exit(1)

        block_sizes_str = input(f"Enter sizes of {B} blocks (space-separated): ").strip()
        block_sizes = list(map(int, block_sizes_str.split()))
        if len(block_sizes) != B:
            print("ERROR: E_INPUT: Number of blocks does not match B")
            sys.exit(1)
        if any(b <= 0 for b in block_sizes):
            print("ERROR: E_RANGE: Block sizes must be positive")
            sys.exit(1)

        P = int(input("Enter number of processes (P): ").strip())
        if P <= 0:
            print("ERROR: E_RANGE: B and P must be positive")

        process_sizes_str = input(f"Enter sizes of {P} processes (space-separated): ").strip()
        process_sizes = list(map(int, process_sizes_str.split()))
        if len(process_sizes) != P:
            print("ERROR: E_INPUT: Number of processes does not match P")
            sys.exit(1)
        if any(p <= 0 for p in process_sizes):
            print("ERROR: E_RANGE: Process sizes must be positive")
            sys.exit(1)

        return block_sizes, process_sizes

    except ValueError:
        print("ERROR: E_INPUT: All inputs must be integers")
        sys.exit(1)


def first_fit(blocks, processes):
    allocation = []
    blocks_copy = blocks.copy()
    allocated_count = 0
    for i, p_size in enumerate(processes):
        placed = False
        for j, b_size in enumerate(blocks_copy):
            if b_size >= p_size:
                allocation.append(f"PROC {i} SIZE {p_size} -> BLOCK {j}")
                blocks_copy[j] -= p_size
                allocated_count += 1
                placed = True
                break
        if not placed:
            allocation.append(f"PROC {i} SIZE {p_size} -> FAIL")
    return allocation, allocated_count


def best_fit(blocks, processes):
    allocation = []
    blocks_copy = blocks.copy()
    allocated_count = 0
    for i, p_size in enumerate(processes):
        best_index = -1
        best_size = None
        for j, b_size in enumerate(blocks_copy):
            if b_size >= p_size:
                if best_size is None or b_size < best_size:
                    best_size = b_size
                    best_index = j
        if best_index != -1:
            allocation.append(f"PROC {i} SIZE {p_size} -> BLOCK {best_index}")
            blocks_copy[best_index] -= p_size
            allocated_count += 1
        else:
            allocation.append(f"PROC {i} SIZE {p_size} -> FAIL")
    return allocation, allocated_count


def worst_fit(blocks, processes):
    allocation = []
    blocks_copy = blocks.copy()
    allocated_count = 0
    for i, p_size in enumerate(processes):
        worst_index = -1
        worst_size = None
        for j, b_size in enumerate(blocks_copy):
            if b_size >= p_size:
                if worst_size is None or b_size > worst_size:
                    worst_size = b_size
                    worst_index = j
        if worst_index != -1:
            allocation.append(f"PROC {i} SIZE {p_size} -> BLOCK {worst_index}")
            blocks_copy[worst_index] -= p_size
            allocated_count += 1
        else:
            allocation.append(f"PROC {i} SIZE {p_size} -> FAIL")
    return allocation, allocated_count


def run_all_algorithms(blocks, processes):
    algorithms = [
        ("FIRST_FIT", first_fit),
        ("BEST_FIT", best_fit),
        ("WORST_FIT", worst_fit)
    ]

    for name, func in algorithms:
        allocation, allocated_count = func(blocks, processes)
        print(f"\nALG {name}")
        for line in allocation:
            print(line)
        print(f"OK: ALLOCATED {allocated_count}/{len(processes)}")


if __name__ == "__main__":
    print("=== Contiguous Memory Allocation Simulator ===\n")
    blocks, processes = read_input()
    run_all_algorithms(blocks, processes)
