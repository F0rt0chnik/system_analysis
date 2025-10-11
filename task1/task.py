from typing import List, Tuple, Dict
from collections import defaultdict, deque

def main(s: str, e: str) -> Tuple[
    List[List[bool]],
    List[List[bool]],
    List[List[bool]],
    List[List[bool]],
    List[List[bool]]
]:

    edges = [line.split(",") for line in s.strip().splitlines()]
    edges = [(u.strip(), v.strip()) for u, v in edges]

    nodes = sorted(set([e] + [u for u, v in edges] + [v for u, v in edges]))
    index: Dict[str, int] = {node: i for i, node in enumerate(nodes)}
    n = len(nodes)

    adj = defaultdict(list)
    parent = {node: None for node in nodes}
    for u, v in edges:
        adj[u].append(v)
        parent[v] = u

    r1 = [[False] * n for _ in range(n)]   
    r2 = [[False] * n for _ in range(n)]   
    r3 = [[False] * n for _ in range(n)]   
    r4 = [[False] * n for _ in range(n)] 
    r5 = [[False] * n for _ in range(n)]   

    for u, v in edges:
        i, j = index[u], index[v]
        r1[i][j] = True
        r2[j][i] = True

    def dfs(start: str):
        visited = set()
        stack = [start]
        while stack:
            node = stack.pop()
            for nxt in adj[node]:
                if nxt not in visited:
                    visited.add(nxt)
                    stack.append(nxt)
        return visited

    for u in nodes:
        i = index[u]
        descendants = dfs(u)
        for v in descendants:
            j = index[v]
            if not r1[i][j]:
                r3[i][j] = True
                r4[j][i] = True
    for p in nodes:
        children = adj[p]
        for i in range(len(children)):
            for j in range(i + 1, len(children)):
                ci, cj = index[children[i]], index[children[j]]
                r5[ci][cj] = True
                r5[cj][ci] = True

    return r1, r2, r3, r4, r5
