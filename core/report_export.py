"""报告导出 - Markdown格式"""
import json
from datetime import datetime


def export_run_markdown(run: dict, results: list, score=None) -> str:
    """导出单次测试运行为Markdown报告"""
    lines = []
    ts = run.get("started_at", "")
    try:
        dt = datetime.fromisoformat(ts)
        ts = dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        pass

    lines.append(f"# MCP Server 评测报告")
    lines.append("")
    lines.append(f"**Server**: {run['server_name']}")
    lines.append(f"**运行ID**: #{run['id']}")
    lines.append(f"**时间**: {ts}")
    lines.append(f"**套件**: {run['suite_type']}")
    lines.append(f"**状态**: {run['status']}")
    lines.append(f"**用例通过**: {run['passed']}/{run['total_cases']}")
    if run.get("duration_sec"):
        lines.append(f"**总耗时**: {run['duration_sec']:.1f}s")

    if score:
        lines.append("")
        lines.append("## 综合评级")
        lines.append("")
        lines.append(f"| 维度 | 得分 |")
        lines.append(f"|------|------|")
        lines.append(f"| **综合** | **{score.letter} ({score.overall:.0f}/100)** |")
        lines.append(f"| 功能 | {score.functional:.0f}% |")
        lines.append(f"| 性能 | {score.performance:.0f}% |")
        lines.append(f"| 安全 | {score.security:.0f}% |")
        lines.append("")
        lines.append(f"> {score.summary}")

    lines.append("")
    lines.append("## 详细结果")
    lines.append("")
    lines.append("| ID | 用例 | 类别 | 状态 | 耗时 | 备注 |")
    lines.append("|----|------|------|------|------|------|")
    icons = {"passed": "✅", "failed": "❌", "skipped": "⏭️", "error": "💥"}
    for r in results:
        icon = icons.get(r["status"], "❓")
        dur = f"{r['duration_ms']:.0f}ms"
        note = (r.get("error_msg") or "").replace("|", "\\|").replace("\n", " ")[:60]
        lines.append(f"| {r['case_id']} | {r['case_name']} | {r['category']} | {icon} {r['status']} | {dur} | {note} |")

    # 性能摘要
    perf = [r for r in results if r["category"] == "performance" and r["status"] == "passed"]
    if perf:
        lines.append("")
        lines.append("## 性能摘要")
        lines.append("")
        for r in perf:
            try:
                d = json.loads(r["detail_json"]) if r.get("detail_json") else {}
            except Exception:
                continue
            lines.append(f"**{r['case_id']} {r['case_name']}**")
            if "mean_ms" in d:
                lines.append(f"- mean: {d['mean_ms']}ms / p50: {d.get('p50_ms', '-')}ms / p95: {d.get('p95_ms', '-')}ms / p99: {d.get('p99_ms', '-')}ms")
                if "max_min_ratio" in d:
                    lines.append(f"- 稳定性: {d.get('trend', '-')} (max/min = {d['max_min_ratio']:.1f})")
            if "concurrency_results" in d:
                for cr in d["concurrency_results"]:
                    lines.append(f"- 并发{cr['concurrency']}: {cr['rps']:.1f} RPS / p50 {cr['p50_ms']}ms / errors {cr['errors']}")
            lines.append("")

    lines.append("")
    lines.append("---")
    lines.append(f"*由 MCP综合评测系统 生成于 {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    return "\n".join(lines)
