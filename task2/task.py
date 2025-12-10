from task1.task import main as main_task1
import math as m


def entropy(matrix_list: list[list[bool]]) -> float:
    out_counts = []

    for matrix in matrix_list:
        out_counts.append([sum(row) for row in matrix])

    h_list = []
    for counts in out_counts:
        h = 0
        for c in counts:
            if c > 0:
                p = c / 6
                h += -p * m.log2(p)
        h_list.append(h)

    return sum(h_list)


def get_norm_complexity(h: float) -> float:
    c = 1 / (m.e * m.log(2))
    return h / (5 * 7 * c)


def main(s: str, e: str) -> tuple[float, float]:
    matrices = main_task1(s, e)

    h_m_r = entropy(matrices)
    norm = get_norm_complexity(h_m_r)

    result = (round(h_m_r, 1), round(norm, 1))
    print(result)
    return result


# пример вызова
main("1,2\n1,3\n3,4\n3,5\n5,6\n6,7", "1")
