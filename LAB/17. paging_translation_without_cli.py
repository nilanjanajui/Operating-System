# 17. Paging address translation

# Hardcode pagesize and TLB size
pagesize = 256
tlb_size = 2

# --- Read input from stdin (simulated with input() here for simplicity) ---
print("Enter number of page table entries:")
n = int(input())
page_table = {}
for _ in range(n):
    vpn, pfn, valid = map(int, input().split())
    if valid not in (0, 1):
        print(f"ERROR: E_INPUT: valid must be 0 or 1")
        exit(1)
    page_table[vpn] = (pfn, valid)

print("Enter number of queries:")
Q = int(input())
queries = []
for _ in range(Q):
    v = int(input())
    if v < 0:
        print(f"ERROR: E_RANGE: virtual address cannot be negative")
        exit(1)
    queries.append(v)

# --- Initialize TLB ---
TLB = [None] * tlb_size if tlb_size > 0 else None
tlb_hits = 0
tlb_misses = 0

# --- Process queries ---
for va in queries:
    vpn = va // pagesize
    offset = va % pagesize

    if vpn not in page_table or page_table[vpn][1] == 0:
        print(f"OK: VA {va} -> PAGEFAULT")
        continue

    pfn = page_table[vpn][0]

    if tlb_size > 0:
        index = vpn % tlb_size
        entry = TLB[index]
        if entry is not None and entry[0] == vpn:
            tlb_hits += 1
            print(f"OK: VA {va} -> PA {pfn*pagesize + offset} (TLB HIT)")
        else:
            tlb_misses += 1
            TLB[index] = (vpn, pfn)
            print(f"OK: VA {va} -> PA {pfn*pagesize + offset} (TLB MISS)")
    else:
        print(f"OK: VA {va} -> PA {pfn*pagesize + offset}")

if tlb_size > 0:
    print(f"OK: TLB_HITS {tlb_hits} TLB_MISSES {tlb_misses}")
