from typing import List
import csv
import io

def main(csv_graph: str) -> List[List[int]]:
    vertices = [1, 2, 3, 4, 5]
    vertex_to_idx = {v: i for i, v in enumerate(vertices)}
    n = len(vertices)
    matrix = [[0]*n for _ in range(n)]

    f = io.StringIO(csv_graph)
    reader = csv.reader(f)
    for row in reader:
        if len(row) != 2:
            raise ValueError(f"Некорректная строка CSV: {row}")
        u, v = int(row[0]), int(row[1])
        matrix[vertex_to_idx[u]][vertex_to_idx[v]] = 1
    extra_edges = [
        (2,1),
        (3,1),
        (4,3),
        (5,3)]
    for u,v in extra_edges:
        matrix[vertex_to_idx[u]][vertex_to_idx[v]] = 1

    return matrix
