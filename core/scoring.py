"""评分体系 - 根据测试结果计算综合评级"""
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
    """性能分：P95延迟映射到0-100（<100ms=满分，>5s=0分）"""
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
            # 直接存统计摘要的用例
            if "p95_ms" in detail:
                p95_values.append(detail["p95_ms"])
            # 并发用例取最大concurrency的p95
            for cr in detail.get("concurrency_results", []):
                if "p95_ms" in cr:
                    p95_values.append(cr["p95_ms"])
        except Exception:
            pass
    if not p95_values:
        return 50.0  # 无数据给中性分
    p95 = max(p95_values)  # 取最差情况
    # 100ms -> 100分, 5000ms -> 0分, 线性插值
    if p95 <= 100:
        return 100.0
    if p95 >= 5000:
        return 0.0
    return 100.0 - (p95 - 100) / 4900 * 100


def compute_score(results: list[dict]) -> Score:
    """results: test_results 行列表（dict含 category/status/detail）"""
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

    # 权重: 功能40% + 性能30% + 安全30%
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
        parts.append("协议实现完整")
    elif func_pct >= 70:
        parts.append("基本功能可用，个别用例未通过")
    else:
        parts.append("存在功能缺陷")
    if perf_pct >= 80:
        parts.append("响应迅速")
    elif perf_pct >= 50:
        parts.append("性能中等")
    else:
        parts.append("延迟偏高")
    if sec_pct >= 95:
        parts.append("安全健壮")
    else:
        parts.append("安全用例有崩溃/异常")

    return Score(letter, overall, func_pct, perf_pct, sec_pct, "；".join(parts))


def grade_color(letter: str) -> str:
    return {"A+": "green", "A": "green", "B": "blue", "C": "orange", "D": "red"}.get(letter, "gray")
