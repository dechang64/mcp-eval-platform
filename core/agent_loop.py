"""LLM Agent循环测试 - 复合任务自主规划

区别于单步工具选择（llm_compat）：这里LLM拿到一个需要多步工具调用
才能完成的复合任务，必须自主规划执行序列，像真实Agent一样工作。

评估维度:
  1. 终态正确性（end-state validation，硬指标）
  2. 规划质量（是否用了最少的必要步骤）
  3. 循环安全性（是否在步数上限内收敛）
"""
import json
import time
from dataclasses import dataclass, field
from typing import Optional

from core.llm_compat import llm_call, extract_json, build_tool_catalog


@dataclass
class AgentStep:
    round_no: int
    tool: str
    args: dict
    ok: bool
    response_snippet: str


@dataclass
class AgentRunResult:
    task: str
    completed: bool          # 终态校验通过
    steps: list = field(default_factory=list)
    rounds_used: int = 0
    max_rounds: int = 8
    end_check_msg: str = ""
    done_reason: str = ""    # llm_done / max_rounds / error
    duration_ms: float = 0.0

    @property
    def efficiency(self) -> str:
        if not self.steps:
            return "-"
        n = len(self.steps)
        return f"{n}步"

    @property
    def grade(self) -> str:
        if self.completed and len(self.steps) <= 6:
            return "A+"
        if self.completed and len(self.steps) <= 8:
            return "A"
        if self.completed:
            return "B"
        if self.done_reason == "max_rounds":
            return "D"
        return "C"


LOOP_SYSTEM = (
    "你是AI助手，需要通过调用MCP工具完成复合任务。"
    "每轮只输出一个JSON：{\"tool\": \"工具名\", \"args\": {...参数...}}。"
    "任务完成时输出：{\"done\": true, \"summary\": \"一句话总结\"}。"
    "不要输出JSON以外的任何内容。"
)


def _history_text(steps: list, responses: list) -> str:
    if not steps:
        return "（尚未执行任何步骤）"
    lines = []
    for i, (s, resp) in enumerate(zip(steps, responses), 1):
        args_str = json.dumps(s, ensure_ascii=False)[:120]
        lines.append(f"[{i}] {s['tool']}({args_str}) → {resp[:100]}")
    return "\n".join(lines)


async def run_agent_loop(client, task: str, end_probes: list,
                         max_rounds: int = 8) -> AgentRunResult:
    """运行Agent循环。

    end_probes: [(tool, args_fn, check_fn(text)->(bool,msg))]
    终态校验全部通过才算 completed。
    """
    start = time.time()
    tools = await client.list_tools()
    catalog = build_tool_catalog(tools)
    steps_log, responses_log = [], []
    result = AgentRunResult(task=task, completed=False, max_rounds=max_rounds)
    done_reason = "max_rounds"

    for round_no in range(1, max_rounds + 1):
        prompt = (
            f"可用工具:\n{catalog}\n\n"
            f"任务: {task}\n\n"
            f"已执行步骤:\n{_history_text(steps_log, responses_log)}\n\n"
            f"输出下一步的JSON:"
        )
        reply = llm_call(prompt, system=LOOP_SYSTEM)
        decision = extract_json(reply) if reply else None
        if not isinstance(decision, dict):
            continue  # 解析失败，重试下一轮

        if decision.get("done"):
            done_reason = "llm_done"
            result.rounds_used = round_no - 1
            break

        tool = decision.get("tool", "")
        args = decision.get("args", {})
        tool_names = {t.name for t in tools}
        if tool not in tool_names:
            responses_log.append(f"工具不存在: {tool}")
            steps_log.append({"tool": tool, "args": args})
            result.steps.append(AgentStep(round_no, tool, args, False, f"工具不存在"))
            continue

        try:
            r = await client.call_tool(tool, args)
            text = r.content[0]["text"] if r.content else ""
            snippet = text[:150]
            ok = not r.is_error
        except Exception as e:
            snippet, ok = f"异常: {str(e)[:80]}", False

        steps_log.append({"tool": tool, "args": args})
        responses_log.append(snippet)
        result.steps.append(AgentStep(round_no, tool, args, ok, snippet))
        result.rounds_used = round_no

    # 终态校验
    all_ok = True
    msgs = []
    for tool, args_fn, check_fn in end_probes:
        try:
            args = args_fn() if callable(args_fn) else args_fn
            r = await client.call_tool(tool, args)
            text = r.content[0]["text"] if r.content else ""
            ok, msg = check_fn(text)
        except Exception as e:
            ok, msg = False, f"探测异常: {str(e)[:60]}"
        all_ok = all_ok and ok
        msgs.append(msg)
    result.completed = all_ok
    result.end_check_msg = "; ".join(msgs)
    result.done_reason = done_reason
    result.duration_ms = (time.time() - start) * 1000
    return result


# ── 内置复合任务 ────────────────────────────────────────────

def builtin_agent_tasks() -> list[dict]:
    """内置复合任务（适用于带memory_*工具的server）"""
    marker = f"RX-{int(time.time())}"
    content = f"{marker}：阿司匹林与华法林联用会增加出血风险，需监测INR"

    task1 = {
        "name": "AT-001 医疗记忆管理复合任务",
        "task": (
            f"请完成以下记忆管理流程："
            f"1) 记住这条医疗事实：'{content}'（重要性0.9）；"
            f"2) 通过检索验证这条记忆已可被找到；"
            f"3) 删除这条记忆；"
            f"4) 再次检索验证它已不存在。"
        ),
        "end_probes": [
            ("memory_recall", {"query": marker[:20], "k": 10},
             lambda t: _check_absent(t, marker)),
        ],
        "marker": marker,
    }
    return [task1]


def _check_absent(text: str, marker: str):
    try:
        d = json.loads(text)
        if isinstance(d, list):
            if any(marker in str(item.get("content", "")) for item in d):
                return False, "记忆未被删除（终态错误）"
            return True, "终态验证：记忆已删除"
    except Exception:
        pass
    return False, f"探测响应异常: {text[:60]}"
