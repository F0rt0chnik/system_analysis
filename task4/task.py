from __future__ import annotations
import json
from typing import Any, Dict, List, Tuple

Point = Tuple[float, float]


def _load_json_maybe(s: Any) -> Any:
    if isinstance(s, (dict, list)):
        return s
    return json.loads(s)


def _as_terms_map(var_obj: Any, expected_key: str | None = None) -> Dict[str, List[Point]]:
    if isinstance(var_obj, dict):
        if expected_key and expected_key in var_obj:
            terms = var_obj[expected_key]
        elif len(var_obj) == 1 and isinstance(next(iter(var_obj.values())), list):
            terms = next(iter(var_obj.values()))
        else:
            raise ValueError
    elif isinstance(var_obj, list):
        terms = var_obj
    else:
        raise TypeError

    out: Dict[str, List[Point]] = {}
    for term in terms:
        term_id = term["id"]
        pts = [(float(p[0]), float(p[1])) for p in term["points"]]
        pts.sort(key=lambda x: x[0])
        out[term_id] = pts
    return out


def _mu_piecewise_linear(x: float, points: List[Point]) -> float:
    if x <= points[0][0]:
        return points[0][1]
    if x >= points[-1][0]:
        return points[-1][1]
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= x <= x1:
            return y0 if x1 == x0 else y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return 0.0


def _build_universe(terms_map: Dict[str, List[Point]], step: float = 0.01) -> List[float]:
    xs = [p[0] for pts in terms_map.values() for p in pts]
    lo, hi = min(xs), max(xs)
    n = int(round((hi - lo) / step))
    S = [lo + i * step for i in range(n + 1)]
    S[-1] = hi
    return S


def main(
    temperature_json: str,
    heating_json: str,
    rules_json: str,
    current_temperature: float,
) -> float:
    temp_terms = _as_terms_map(_load_json_maybe(temperature_json), "температура")
    heat_terms = _as_terms_map(_load_json_maybe(heating_json), "уровень нагрева")
    rules = [(r[0], r[1]) for r in _load_json_maybe(rules_json)]

    S = _build_universe(heat_terms)

    mu_temp = {
        term: _mu_piecewise_linear(current_temperature, pts)
        for term, pts in temp_terms.items()
    }

    mu_agg = [0.0 for _ in S]

    for t_term, h_term in rules:
        act = mu_temp[t_term]
        if act <= 0:
            continue
        pts = heat_terms[h_term]
        for i, s in enumerate(S):
            mu_agg[i] = max(mu_agg[i], min(act, _mu_piecewise_linear(s, pts)))

    max_mu = max(mu_agg)
    if max_mu <= 0:
        return float(S[0])

    for s, mu in zip(S, mu_agg):
        if mu == max_mu:
            return float(s)

    return float(S[0])
