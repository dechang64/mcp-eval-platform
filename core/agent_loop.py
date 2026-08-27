"""LLM Agent Loop Testing - autonomous planning for composite tasks

Unlike single-step tool selection (llm_compat): here the LLM receives a
composite task that requires multiple tool calls to complete and must
plan the execution sequence autonomously, working like a real agent.

Evaluation dimensions:
  1. End-state correctness (end-state validation, hard metric)
  2. Planning quality (whether the fewest necessary steps were used)
  3. Loop safety (convergence within the round limit)
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
    completed: bool          # end-state validation passed
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
        return f"{n} steps"

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
    "You are an AI assistant that completes composite tasks by calling MCP tools. "
    "Each round, output exactly one JSON: {\"tool\": \"tool_name\", \"args\": {...}}. "
    "When the task is complete, output: {\"done\": true, \"summary\": \"one-line summary\"}. "
    "Do not output anything other than JSON."
)


def _history_text(steps: list, responses: list) -> str:
    if not steps:
        return "(no steps executed yet)"
    lines = []
    for i, (s, resp) in enumerate(zip(steps, responses), 1):
        args_str = json.dumps(s, ensure_ascii=False)[:120]
        lines.append(f"[{i}] {s['tool']}({args_str}) -> {resp[:100]}")
    return "\n".join(lines)


async def run_agent_loop(client, task: str, end_probes: list,
                         max_rounds: int = 8) -> AgentRunResult:
    """Run the agent loop.

    end_probes: [(tool, args_fn, check_fn(text)->(bool,msg))]
    The run counts as completed only if all end-state probes pass.
    """
    start = time.time()
    tools = await client.list_tools()
    catalog = build_tool_catalog(tools)
    steps_log, responses_log = [], []
    result = AgentRunResult(task=task, completed=False, max_rounds=max_rounds)
    done_reason = "max_rounds"

    for round_no in range(1, max_rounds + 1):
        prompt = (
            f"Available tools:\n{catalog}\n\n"
            f"Task: {task}\n\n"
            f"Steps already executed:\n{_history_text(steps_log, responses_log)}\n\n"
            f"Output the JSON for the next step:"
        )
        reply = llm_call(prompt, system=LOOP_SYSTEM)
        decision = extract_json(reply) if reply else None
        if not isinstance(decision, dict):
            continue  # parse failure, retry next round

        if decision.get("done"):
            done_reason = "llm_done"
            result.rounds_used = round_no - 1
            break

        tool = decision.get("tool", "")
        args = decision.get("args", {})
        tool_names = {t.name for t in tools}
        if tool not in tool_names:
            responses_log.append(f"tool does not exist: {tool}")
            steps_log.append({"tool": tool, "args": args})
            result.steps.append(AgentStep(round_no, tool, args, False, "tool does not exist"))
            continue

        try:
            r = await client.call_tool(tool, args)
            text = r.content[0]["text"] if r.content else ""
            snippet = text[:150]
            ok = not r.is_error
        except Exception as e:
            snippet, ok = f"exception: {str(e)[:80]}", False

        steps_log.append({"tool": tool, "args": args})
        responses_log.append(snippet)
        result.steps.append(AgentStep(round_no, tool, args, ok, snippet))
        result.rounds_used = round_no

    # End-state validation
    all_ok = True
    msgs = []
    for tool, args_fn, check_fn in end_probes:
        try:
            args = args_fn() if callable(args_fn) else args_fn
            r = await client.call_tool(tool, args)
            text = r.content[0]["text"] if r.content else ""
            ok, msg = check_fn(text)
        except Exception as e:
            ok, msg = False, f"probe exception: {str(e)[:60]}"
        all_ok = all_ok and ok
        msgs.append(msg)
    result.completed = all_ok
    result.end_check_msg = "; ".join(msgs)
    result.done_reason = done_reason
    result.duration_ms = (time.time() - start) * 1000
    return result


# ── Builtin composite tasks ────────────────────────────────

def builtin_agent_tasks() -> list[dict]:
    """Builtin composite tasks (for servers exposing memory_* tools)"""
    marker = f"RX-{int(time.time())}"
    content = f"{marker}: combining aspirin with warfarin increases bleeding risk; INR must be monitored"

    task1 = {
        "name": "AT-001 Medical Memory Management Composite Task",
        "task": (
            f"Complete the following memory management workflow: "
            f"1) Remember this medical fact: '{content}' (importance 0.9); "
            f"2) Verify via recall that this memory can be found; "
            f"3) Delete this memory; "
            f"4) Recall again and verify it no longer exists."
        ),
        "end_probes": [
            ("memory_recall", {"query": marker, "k": 10},
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
                return False, "memory not deleted (end-state error)"
            return True, "end-state verified: memory deleted"
    except Exception:
        pass
    return False, f"probe response error: {text[:60]}"
