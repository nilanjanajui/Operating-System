# 14. Deadlock banker's algorithm

def bankers_algorithm(allocation, max_need, available):
    n = len(allocation)        # number of processes
    m = len(available)         # number of resources

    # Calculate Need matrix
    need = [[max_need[i][j] - allocation[i][j] for j in range(m)] for i in range(n)]

    finish = [False] * n
    safe_sequence = []
    work = available[:]

    while len(safe_sequence) < n:
        found = False
        for i in range(n):
            if not finish[i] and all(need[i][j] <= work[j] for j in range(m)):
                for j in range(m):
                    work[j] += allocation[i][j]
                finish[i] = True
                safe_sequence.append(i)
                found = True
        if not found:
            print("OK: UNSAFE")
            return

    print("OK: SAFE")
    print("OK: SEQ", *safe_sequence)


# ----------------- USER INPUT -----------------
try:
    P, R = map(int, input("Enter number of processes and resources: ").split())
    print("Enter Allocation matrix row by row (space-separated):")
    allocation = [list(map(int, input().split())) for _ in range(P)]
    print("Enter Max matrix row by row (space-separated):")
    max_need = [list(map(int, input().split())) for _ in range(P)]
    print("Enter Available vector (space-separated):")
    available = list(map(int, input().split()))

    # Basic validation
    for i in range(P):
        for j in range(R):
            if allocation[i][j] > max_need[i][j]:
                raise ValueError(f"Allocation cannot exceed Max for process {i}, resource {j}")
            if allocation[i][j] < 0 or max_need[i][j] < 0 or available[j] < 0:
                raise ValueError("Resource values must be non-negative")
    if len(available) != R:
        raise ValueError("Available vector size must match number of resources")

    bankers_algorithm(allocation, max_need, available)

except Exception as e:
    print(f"ERROR: {e}")
