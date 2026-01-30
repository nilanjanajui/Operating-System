# 15. Deadlock Detection WFG using Kahn Style Method

import sys
from collections import deque, defaultdict

def error(code, message):
    print(f"ERROR: {code}: {message}")
    sys.exit(1)

def read_input():
    try:
        first_line = input("Enter P E (process count and edge count): ").strip()
        if not first_line:
            error("E_INPUT", "missing first line")
        parts = first_line.split()
        if len(parts) != 2:
            error("E_INPUT", f"first line must have 2 integers, got {len(parts)}")
        P, E = map(int, parts)
        if P < 0 or E < 0:
            error("E_RANGE", "negative process or edge count")
    except ValueError:
        error("E_INPUT", "cannot parse first line")

    edges = []
    for i in range(E):
        line = input(f"Enter edge {i+1} (u v): ").strip()
        parts = line.split()
        if len(parts) != 2:
            error("E_INPUT", f"invalid edge line: '{line.strip()}'")
        try:
            u, v = map(int, parts)
        except ValueError:
            error("E_INPUT", f"cannot parse edge line: '{line.strip()}'")
        if not (0 <= u < P) or not (0 <= v < P):
            error("E_RANGE", f"node {u if u<0 or u>=P else v} out of range 0..{P-1}")
        edges.append((u, v))

    return P, E, edges

def build_graph(P, edges):
    graph = [[] for _ in range(P)]
    indegree = [0] * P
    for u, v in edges:
        graph[u].append(v)
        indegree[v] += 1
    return graph, indegree

def kahn_deadlock(P, graph, indegree):
    # Queue of nodes with zero indegree
    q = deque([i for i in range(P) if indegree[i] == 0])
    processed = 0

    indegree_copy = indegree.copy()
    while q:
        node = q.popleft()
        processed += 1
        for neigh in graph[node]:
            indegree_copy[neigh] -= 1
            if indegree_copy[neigh] == 0:
                q.append(neigh)

    # If all nodes processed, no deadlock
    if processed == P:
        return None

    # Nodes remaining with indegree > 0 are part of a cycle
    remaining = [i for i in range(P) if indegree_copy[i] > 0]

    # Now we need to find **canonical cycle** among remaining nodes
    # Use DFS limited to remaining nodes
    visited = [False] * P
    rec_stack = [False] * P
    canonical_cycle = None

    def dfs(node, path):
        nonlocal canonical_cycle
        visited[node] = True
        rec_stack[node] = True
        path.append(node)

        for neigh in sorted(graph[node]):
            if neigh not in remaining:
                continue
            if rec_stack[neigh]:
                idx = path.index(neigh)
                cycle = path[idx:] + [neigh]
                if canonical_cycle is None:
                    canonical_cycle = cycle
                else:
                    old_start = min(canonical_cycle[:-1])
                    new_start = min(cycle[:-1])
                    if new_start < old_start:
                        canonical_cycle = cycle
                    elif new_start == old_start and cycle < canonical_cycle:
                        canonical_cycle = cycle
            elif not visited[neigh]:
                dfs(neigh, path.copy())

        rec_stack[node] = False

    for u in sorted(remaining):
        if not visited[u]:
            dfs(u, [])

    return canonical_cycle

def main():
    P, E, edges = read_input()
    graph, indegree = build_graph(P, edges)
    cycle = kahn_deadlock(P, graph, indegree)

    if cycle:
        print("OK: DEADLOCK YES")
        print("OK: CYCLE", ' '.join(map(str, cycle)))
    else:
        print("OK: DEADLOCK NO")

if __name__ == "__main__":
    main()
