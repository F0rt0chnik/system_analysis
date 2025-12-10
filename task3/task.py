import json
import re
from functools import cmp_to_key


def _clean_json(s: str) -> str:
    """Убирает лишние запятые перед ] и }."""
    s = re.sub(r",\s*\]", "]", s)
    s = re.sub(r",\s*\}", "}", s)
    return s


def _flatten_ranking(ranking: list) -> list:
    """Плоский список элементов из кластерной ранжировки."""
    res = []
    for item in ranking:
        if isinstance(item, list):
            for x in item:
                res.append(x)
        else:
            res.append(item)
    return res


def _build_pos_map(ranking: list) -> dict:
    """Карта: элемент -> индекс кластера (0 слева)."""
    pos: dict = {}
    for idx, item in enumerate(ranking):
        if isinstance(item, list):
            for x in item:
                pos[x] = idx
        else:
            pos[item] = idx
    return pos


def _make_matrix(elements: list, pos_map: dict) -> list[list[int]]:
    """Матрица отношений Y, где y_ij = 1, если xi ≥ xj (справа или равен)."""
    n = len(elements)
    mat = [[0] * n for _ in range(n)]
    for i, xi in enumerate(elements):
        for j, xj in enumerate(elements):
            mat[i][j] = 1 if pos_map[xi] >= pos_map[xj] else 0
    return mat


def _and_matrix(A: list[list[int]], B: list[list[int]]) -> list[list[int]]:
    """Покомпонентное «И» двух матриц."""
    n = len(A)
    return [[1 if (A[i][j] and B[i][j]) else 0 for j in range(n)] for i in range(n)]


def _transpose_matrix(A: list[list[int]]) -> list[list[int]]:
    """Транспонирование матрицы."""
    n = len(A)
    return [[A[j][i] for j in range(n)] for i in range(n)]


def main(jsonA_str: str, jsonB_str: str) -> str:
    """Принимает две JSON-строки с кластерными ранжировками.
    Возвращает JSON-строку с:
      - variant1: ядро противоречий (список пар),
      - variant2: согласованная кластерная ранжировка.
    """
    # лёгкая очистка на случай лишних запятых
    sA = _clean_json(jsonA_str)
    sB = _clean_json(jsonB_str)
    A = json.loads(sA)
    B = json.loads(sB)

    # элементы в порядке первого появления
    flat = _flatten_ranking(A) + _flatten_ranking(B)
    elements: list = []
    seen: set = set()
    for x in flat:
        if x not in seen:
            elements.append(x)
            seen.add(x)

    # позиции в каждой ранжировке
    posA = _build_pos_map(A)
    posB = _build_pos_map(B)

    # матрицы отношений
    YA = _make_matrix(elements, posA)
    YB = _make_matrix(elements, posB)

    # поэлементное произведение
    YAB = _and_matrix(YA, YB)

    # транспонированные матрицы
    YAt = _transpose_matrix(YA)
    YBt = _transpose_matrix(YB)
    YtAB = _and_matrix(YAt, YBt)

    n = len(elements)

    # ядро противоречий: пары (i, j), где YAB[i][j] == 0 и YtAB[i][j] == 0
    core_pairs: list[list] = []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if YAB[i][j] == 0 and YtAB[i][j] == 0:
                core_pairs.append([elements[i], elements[j]])

    # объединяем элементы, связанные противоречиями (неориентированный граф)
    parent = {el: el for el in elements}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for a, b in core_pairs:
        union(a, b)

    comps: dict = {}
    for el in elements:
        r = find(el)
        comps.setdefault(r, []).append(el)

    clusters = list(comps.values())

    # сортируем элементы внутри кластера по порядку появления
    order_index = {el: i for i, el in enumerate(elements)}
    clusters = [sorted(cluster, key=lambda x: order_index[x]) for cluster in clusters]

    # сравнение двух кластеров по данным двух ранжировок
    def _cmp_clusters(c1, c2):
        rep1 = c1[0]
        rep2 = c2[0]
        i = order_index[rep1]
        j = order_index[rep2]

        score = 0

        # A: rep1 < rep2 / rep1 > rep2
        if YA[j][i] == 1 and YA[i][j] == 0:
            score -= 1
        elif YA[i][j] == 1 and YA[j][i] == 0:
            score += 1

        # B: rep1 < rep2 / rep1 > rep2
        if YB[j][i] == 1 and YB[i][j] == 0:
            score -= 1
        elif YB[i][j] == 1 and YB[j][i] == 0:
            score += 1

        if score < 0:
            return -1
        if score > 0:
            return 1

        # при равенстве — по порядку появления
        if order_index[rep1] < order_index[rep2]:
            return -1
        if order_index[rep1] > order_index[rep2]:
            return 1
        return 0

    # кластеры слева (хуже) направо (лучше)
    clusters_sorted = sorted(clusters, key=cmp_to_key(_cmp_clusters))

    # одиночки как элемент, группы как списки
    consensus = [cluster if len(cluster) > 1 else cluster[0] for cluster in clusters_sorted]

    result = {
        "variant1": core_pairs,
        "variant2": consensus,
    }
    return json.dumps(result, ensure_ascii=False)


if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 3:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            sA = f.read()
        with open(sys.argv[2], "r", encoding="utf-8") as f:
            sB = f.read()
        print(main(sA, sB))
    else:
        # простой пример
        sA = "[1,[2,3],4,[5,6,7],8,9,10]"
