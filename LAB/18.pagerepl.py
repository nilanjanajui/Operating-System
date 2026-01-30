# 18
import sys
import argparse
from typing import List

def print_result(alg: str, faults: int, frames: List[int]) -> None:
    print(f"ALG {alg}")
    print(f"OK: FAULTS {faults}")
    print("OK: FINAL " + " ".join(str(f) if f != -1 else "-1" for f in frames))

def simulate_fifo(refs: List[int], F: int) -> tuple[int, List[int]]:
    """FIFO with circular pointer implementation."""
    frames = [-1] * F
    ptr = 0  # Pointer to next frame to replace
    faults = 0
    occupied = 0  # How many frames are actually occupied
    
    for page in refs:
        if page in frames:
            continue  # Hit
        
        faults += 1  # Miss
        
        if occupied < F:
            # Fill empty frame
            frames[occupied] = page
            occupied += 1
        else:
            # Replace at pointer
            frames[ptr] = page
            ptr = (ptr + 1) % F
    
    return faults, frames

def simulate_lru(refs: List[int], F: int) -> tuple[int, List[int]]:
    """LRU with timestamp tracking."""
    frames = [-1] * F
    last_used = {}  # page -> last access time
    time = 0
    faults = 0
    occupied = 0
    
    for page in refs:
        if page in frames:
            # Update last used time
            last_used[page] = time
        else:
            faults += 1
            
            if occupied < F:
                # Fill first empty frame
                frames[occupied] = page
                last_used[page] = time
                occupied += 1
            else:
                # Find LRU page in frames
                lru_page = frames[0]
                lru_time = last_used.get(lru_page, float('inf'))
                
                for i in range(1, F):
                    current_page = frames[i]
                    current_time = last_used.get(current_page, float('inf'))
                    if current_time < lru_time:
                        lru_page = current_page
                        lru_time = current_time
                
                # Replace LRU page
                idx = frames.index(lru_page)
                del last_used[lru_page]
                frames[idx] = page
                last_used[page] = time
        
        time += 1
    
    return faults, frames

def simulate_opt(refs: List[int], F: int) -> tuple[int, List[int]]:
    """Optimal page replacement."""
    frames = [-1] * F
    faults = 0
    occupied = 0
    
    for i, page in enumerate(refs):
        if page in frames:
            continue
        
        faults += 1
        
        if occupied < F:
            # Fill empty frame
            frames[occupied] = page
            occupied += 1
        else:
            # Find page to evict
            victim_idx = 0
            farthest_next = -1
            
            for idx, frame_page in enumerate(frames):
                # Find next use of this page
                next_use = len(refs) + 1  # Default: never used again
                for j in range(i + 1, len(refs)):
                    if refs[j] == frame_page:
                        next_use = j
                        break
                
                if next_use == len(refs) + 1:
                    # Never used again - evict this one immediately
                    victim_idx = idx
                    break
                elif next_use > farthest_next:
                    farthest_next = next_use
                    victim_idx = idx
                elif next_use == farthest_next and idx < victim_idx:
                    # Tie-break: smaller frame index
                    victim_idx = idx
            
            frames[victim_idx] = page
    
    return faults, frames

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--frames', type=int, required=True)
    args = parser.parse_args()
    
    if args.frames < 1 or args.frames > 64:
        print("ERROR: E_RANGE: frames must be 1..64", file=sys.stderr)
        return 1
    
    try:
        L_line = sys.stdin.readline()
        if not L_line:
            return 1
        L = int(L_line.strip())
        
        refs_line = sys.stdin.readline()
        if not refs_line:
            return 1
        refs = list(map(int, refs_line.strip().split()))
        
        if len(refs) != L:
            print("ERROR: E_INPUT: length mismatch", file=sys.stderr)
            return 1
        
        if any(x < 0 for x in refs):
            print("ERROR: E_RANGE: page numbers must be >= 0", file=sys.stderr)
            return 1
    except Exception:
        print("ERROR: E_INPUT: invalid input", file=sys.stderr)
        return 1
    
    # Run all algorithms
    f_faults, f_frames = simulate_fifo(refs, args.frames)
    print_result("FIFO", f_faults, f_frames)
    
    l_faults, l_frames = simulate_lru(refs, args.frames)
    print_result("LRU", l_faults, l_frames)
    
    o_faults, o_frames = simulate_opt(refs, args.frames)
    print_result("OPT", o_faults, o_frames)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())