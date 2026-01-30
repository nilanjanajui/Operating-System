# 19
import sys
from typing import List, Tuple, Optional, Set

def error_exit(code: str, message: str) -> None:
    """Print error message and exit with non-zero status."""
    print(f"ERROR: {code}: {message}", file=sys.stderr)
    sys.exit(1)

def read_input() -> Tuple[int, Set[int], List[Tuple[str, int]]]:
    """Read and validate input from stdin."""
    try:
        # Read total blocks
        line = sys.stdin.readline()
        if not line:
            error_exit("E_INPUT", "empty input")
        N = int(line.strip())
        if not (1 <= N <= 10000):
            error_exit("E_RANGE", "total blocks must be 1..10000")
        
        # Read number of free blocks
        line = sys.stdin.readline()
        if not line:
            error_exit("E_INPUT", "missing free blocks count")
        F = int(line.strip())
        
        # Read free block IDs
        line = sys.stdin.readline()
        if not line:
            error_exit("E_INPUT", "missing free block list")
        free_blocks = list(map(int, line.strip().split()))
        
        if len(free_blocks) != F:
            error_exit("E_INPUT", f"free block count mismatch: expected {F}, got {len(free_blocks)}")
        
        # Validate free blocks
        seen = set()
        for block in free_blocks:
            if not (0 <= block < N):
                error_exit("E_RANGE", f"block ID {block} out of range 0..{N-1}")
            if block in seen:
                error_exit("E_DUPBLOCK", "free block list must contain unique IDs")
            seen.add(block)
        
        # Read number of files
        line = sys.stdin.readline()
        if not line:
            error_exit("E_INPUT", "missing file count")
        M = int(line.strip())
        
        # Read file requests
        files = []
        for _ in range(M):
            line = sys.stdin.readline()
            if not line:
                error_exit("E_INPUT", "incomplete file list")
            parts = line.strip().split()
            if len(parts) != 2:
                error_exit("E_INPUT", "invalid file line format")
            
            name = parts[0]
            try:
                size = int(parts[1])
            except ValueError:
                error_exit("E_INPUT", f"invalid file size for {name}")
            
            if not (1 <= size <= N):
                error_exit("E_RANGE", f"file size for {name} must be 1..{N}")
            
            files.append((name, size))
        
        return N, set(free_blocks), files
    
    except ValueError:
        error_exit("E_INPUT", "invalid number format")

def simulate_contiguous(N: int, free_blocks: Set[int], files: List[Tuple[str, int]]) -> List[Tuple[str, str]]:
    """Simulate contiguous allocation strategy."""
    results = []
    # Create a sorted list of free blocks for easier contiguous search
    sorted_free = sorted(free_blocks)
    
    for name, size in files:
        allocated = False
        
        # Find smallest starting block with enough consecutive free blocks
        for i in range(len(sorted_free) - size + 1):
            start = sorted_free[i]
            # Check if blocks start..start+size-1 are all free
            consecutive = True
            for j in range(1, size):
                if sorted_free[i + j] != start + j:
                    consecutive = False
                    break
            
            if consecutive:
                # Allocation successful
                results.append((name, f"START {start} LEN {size}"))
                
                # Remove allocated blocks from free list
                for j in range(size):
                    sorted_free.remove(start + j)
                
                allocated = True
                break
        
        if not allocated:
            results.append((name, "FAIL"))
    
    return results

def simulate_linked(N: int, free_blocks: Set[int], files: List[Tuple[str, int]]) -> List[Tuple[str, str]]:
    """Simulate linked allocation strategy."""
    results = []
    # Use sorted list for deterministic smallest block selection
    available_blocks = sorted(free_blocks)
    
    for name, size in files:
        if len(available_blocks) >= size:
            # Allocate smallest 'size' blocks
            allocated = available_blocks[:size]
            
            # Create chain string
            chain = "->".join(str(b) for b in allocated)
            results.append((name, f"CHAIN {chain}"))
            
            # Remove allocated blocks
            available_blocks = available_blocks[size:]
        else:
            results.append((name, "FAIL"))
    
    return results

def simulate_indexed(N: int, free_blocks: Set[int], files: List[Tuple[str, int]]) -> List[Tuple[str, str]]:
    """Simulate indexed allocation strategy."""
    results = []
    # Use sorted list for deterministic smallest block selection
    available_blocks = sorted(free_blocks)
    
    for name, size in files:
        # Indexed allocation needs: 1 index block + size data blocks
        total_needed = size + 1
        
        if len(available_blocks) >= total_needed:
            # Allocate blocks: first block is index, next 'size' blocks are data
            index_block = available_blocks[0]
            data_blocks = available_blocks[1:size+1]
            
            # Create data blocks string
            data_str = ",".join(str(b) for b in data_blocks)
            results.append((name, f"INDEX {index_block} DATA {data_str}"))
            
            # Remove allocated blocks
            available_blocks = available_blocks[total_needed:]
        else:
            results.append((name, "FAIL"))
    
    return results

def main() -> None:
    """Main function implementing filealloc tool."""
    # Read and validate input
    N, free_blocks, files = read_input()
    
    # Simulate each strategy independently
    print("ALG CONTIGUOUS")
    contiguous_results = simulate_contiguous(N, free_blocks.copy(), files)
    for name, result in contiguous_results:
        print(f"FILE {name} -> {result}")
    
    print("\nALG LINKED")
    linked_results = simulate_linked(N, free_blocks.copy(), files)
    for name, result in linked_results:
        print(f"FILE {name} -> {result}")
    
    print("\nALG INDEXED")
    indexed_results = simulate_indexed(N, free_blocks.copy(), files)
    for name, result in indexed_results:
        print(f"FILE {name} -> {result}")

if __name__ == "__main__":
    main()