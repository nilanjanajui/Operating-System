import sys
import argparse

# --- Parse command-line arguments ---
parser = argparse.ArgumentParser()
parser.add_argument("--pagesize", type=int, required=True)
parser.add_argument("--tlb", type=int, required=True)
args = parser.parse_args()

pagesize = args.pagesize
tlb_size = args.tlb

# Validate pagesize (must be power of 2)
if pagesize < 256 or pagesize > 65536 or (pagesize & (pagesize - 1)) != 0:
    print(f"ERROR: E_RANGE: pagesize must be power of 2 between 256 and 65536")
    sys.exit(1)

if tlb_size < 0 or tlb_size > 64:
    print(f"ERROR: E_RANGE: TLB size must be 0..64")
    sys.exit(1)

# --- Read input from stdin ---
lines = [line.strip() for line in sys.stdin if line.strip()]
try:
    n = int(lines[0])
    page_table = {}
    for i in range(1, n+1):
        parts = lines[i].split()
        if len(parts) != 3:
            raise ValueError("Invalid page table entry")
        vpn, pfn, valid = map(int, parts)
        if valid not in (0, 1):
            print(f"ERROR: E_INPUT: valid must be 0 or 1")
            sys.exit(1)
        page_table[vpn] = (pfn, valid)
    q_index = n + 1
    Q = int(lines[q_index])
    queries = [int(v) for v in lines[q_index+1 : q_index+1+Q]]
    for v in queries:
        if v < 0:
            print(f"ERROR: E_RANGE: virtual address cannot be negative")
            sys.exit(1)
except Exception as e:
    print(f"ERROR: E_INPUT: {e}")
    sys.exit(1)

# --- Initialize TLB if needed ---
TLB = [None] * tlb_size if tlb_size > 0 else None
tlb_hits = 0
tlb_misses = 0

# --- Process each query ---
for va in queries:
    vpn = va // pagesize
    offset = va % pagesize

    # Check page table
    if vpn not in page_table or page_table[vpn][1] == 0:
        print(f"OK: VA {va} -> PAGEFAULT")
        continue

    pfn = page_table[vpn][0]

    # Handle TLB
    if tlb_size > 0:
        index = vpn % tlb_size
        entry = TLB[index]
        if entry is not None and entry[0] == vpn:
            # TLB hit
            tlb_hits += 1
            print(f"OK: VA {va} -> PA {pfn*pagesize + offset} (TLB HIT)")
        else:
            # TLB miss, update TLB
            tlb_misses += 1
            TLB[index] = (vpn, pfn)
            print(f"OK: VA {va} -> PA {pfn*pagesize + offset} (TLB MISS)")
    else:
        # No TLB
        print(f"OK: VA {va} -> PA {pfn*pagesize + offset}")

# --- Print TLB stats if used ---
if tlb_size > 0:
    print(f"OK: TLB_HITS {tlb_hits} TLB_MISSES {tlb_misses}")



# run in terminal:
# printf "3
# 0 5 1
# 1 6 1
# 2 9 0
# 4
# 0
# 300
# 700
# 0
# " | python "/home/nilanjana/5th Semester/Operating System/LAB/paging_translation.py" --pagesize 256 --tlb 2