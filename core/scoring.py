"""Scoring system - compute overall grade from test results"""
from dataclasses import dataclass


@dataclass
class Score:
    letter: str          # A+ / A / B / C / D
    overall: float       # 0-100
    functional: float
    performance: float
    security: float
    summary: str


def _pct(passed: int, total: int) -> float:
    return (passed / total * 100) if total > 0 else 0.0


def _perf_score(results: list) -> float:
    """Performance score: map P95 latency to 0-100 (<100ms = full, >5s = zero)"""
    p95_values = []
    for r in results:
        if r.get("category") != "performance" or r.get("status") != "passed":
            continue
        raw = r.get("detail_json") or r.get("detail")
        if not raw:
            continue
        try:
            import json
            detail = json.loads(raw) if isinstance(raw, str) else raw
            # Cases that store summary statistics directly
            if "p95_ms" in detail:
                p95_values.append(detail["p95_ms"])
            # Concurrency cases: take p95 across all concurrency levels
            for cr in detail.get("concurrency_results", []):
                if "p95_ms" in cr:
                    p95_values.append(cr["p95_ms"])
        except Exception:
            pass
    if not p95_values:
        return 50.0  # neutral score when no data
    p95 = max(p95_values)  # worst case
    # 100ms -> 100 points, 5000ms -> 0 points, linear interpolation
    if p95 <= 100:
        return 100.0
    if p95 >= 5000:
        return 0.0
    return 100.0 - (p95 - 100) / 4900 * 100


def compute_score(results: list[dict]) -> Score:
    """results: list of test_result rows (dicts with category/status/detail)"""
    cats = {"functional": [], "performance": [], "security": []}
    for r in results:
        cat = r.get("category", "")
        if cat in cats:
            cats[cat].append(r)

    func_cases = [r for r in cats["functional"] if r["status"] != "skipped"]
    sec_cases = [r for r in cats["security"] if r["status"] != "skipped"]

    func_pct = _pct(sum(1 for r in func_cases if r["status"] == "passed"), len(func_cases))
    sec_pct = _pct(sum(1 for r in sec_cases if r["status"] == "passed"), len(sec_cases))
    perf_pct = _perf_score(cats["performance"])

    # Weights: functional 40% + performance 30% + security 30%
    overall = func_pct * 0.4 + perf_pct * 0.3 + sec_pct * 0.3

    if overall >= 90:
        letter = "A+"
    elif overall >= 80:
        letter = "A"
    elif overall >= 70:
        letter = "B"
    elif overall >= 60:
        letter = "C"
    else:
        letter = "D"

    parts = []
    if func_pct >= 95:
        parts.append("complete protocol implementation")
    elif func_pct >= 70:
        parts.append("core functionality works, some cases failed")
    else:
        parts.append("functional defects present")
    if perf_pct >= 80:
        parts.append("fast responses")
    elif perf_pct >= 50:
        parts.append("moderate latency")
    else:
        parts.append("high latency")
    if sec_pct >= 95:
        parts.append("robust against adversarial inputs")
    else:
        parts.append("security cases crashed or errored")

    return Score(letter, overall, func_pct, perf_pct, sec_pct, "; ".join(parts))


def grade_color(letter: str) -> str:
    return {"A+": "green", "A": "green", "B": "blue", "C": "orange", "D": "red"}.get(letter, "gray")
