# 15. Deadlock Detection WFG using DFS

import sys

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
            error("E_INPUT", f"invalid edge line: '{line}'")
        try:
            u, v = map(int, parts)
        except ValueError:
            error("E_INPUT", f"cannot parse edge line: '{line}'")
        if not (0 <= u < P) or not (0 <= v < P):
            error("E_RANGE", f"node {u if u<0 or u>=P else v} out of range 0..{P-1}")
        edges.append((u, v))

    return P, E, edges

def build_graph(P, edges):
    graph = [[] for _ in range(P)]
    for u, v in edges:
        graph[u].append(v)
    for adj in graph:
        adj.sort()
    return graph

def find_deadlock(P, graph):
    visited = [False] * P
    rec_stack = [False] * P
    canonical_cycle = None

    def dfs(node, path):
        nonlocal canonical_cycle
        visited[node] = True
        rec_stack[node] = True
        path.append(node)

        for neigh in graph[node]:
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

    for u in range(P):
        if not visited[u]:
            dfs(u, [])

    return canonical_cycle

def main():
    P, E, edges = read_input()
    graph = build_graph(P, edges)
    cycle = find_deadlock(P, graph)

    if cycle:
        print("OK: DEADLOCK YES")
        print("OK: CYCLE", ' '.join(map(str, cycle)))
    else:
        print("OK: DEADLOCK NO")

if __name__ == "__main__":
    main()
