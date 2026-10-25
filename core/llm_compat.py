"""LLM Compatibility Test Engine

Goal: measure whether an LLM can, given only the MCP server's tool descriptions:
  1. Pick the right tool (tool selection accuracy)
  2. Fill valid arguments (argument schema compliance)

Flow: connect to the server under test and fetch its tool list →
      the LLM generates one natural-language task per tool →
      the LLM (seeing the tool catalog + task) picks a tool and fills args →
      a rule engine validates both.

LLM backend: AMAX (OpenAI-compatible chat completions). Configuration is
read lazily at call time — env vars first, then Streamlit secrets:
  AMAX_API_KEY   (required)  secret key
  AMAX_BASE_URL  (optional)  default https://ai.amaxsmp.com/v1
  AMAX_MODEL     (optional)  default see DEFAULT_MODEL below
"""
import asyncio
import json
import os
import re
import time
from dataclasses import dataclass, field
from typing import Optional

DEFAULT_MODEL = "qwen3.5-flash-nothinking"
DEFAULT_BASE_URL = "https://ai.amaxsmp.com/v1"


def get_llm_model() -> str:
    """Resolve the model name: AMAX_MODEL env / secrets, else the default."""
    model = os.environ.get("AMAX_MODEL", "")
    if not model:
        try:
            import streamlit as st
            model = st.secrets.get("AMAX_MODEL", "")
        except Exception:
            model = ""
    return model or DEFAULT_MODEL


# ── AMAX backend (OpenAI-compatible) ─────────────────────

def llm_call(prompt: str, system: str = "", retries: int = 3) -> str:
    """Call the AMAX OpenAI-compatible API and return the plain-text reply.

    Retry semantics (preserved from the previous z-ai CLI implementation):
      - 429 / rate-limit → exponential backoff 8 * (attempt + 1) seconds
      - any other error  → 3s backoff
    Both give up after `retries` attempts and raise. The last 429 now
    surfaces a real error instead of falling through to "unreachable".
    Client-side timeout: 60s per call.
    """
    import openai

    api_key = os.environ.get("AMAX_API_KEY", "")
    base_url = os.environ.get("AMAX_BASE_URL", "")
    model = os.environ.get("AMAX_MODEL", "")
    try:
        import streamlit as st
        api_key = api_key or st.secrets.get("AMAX_API_KEY", "")
        base_url = base_url or st.secrets.get("AMAX_BASE_URL", "")
        model = model or st.secrets.get("AMAX_MODEL", "")
    except Exception:
        pass  # outside Streamlit runtime (tests, scripts) — env only
    if not api_key:
        raise RuntimeError("AMAX_API_KEY not configured (Streamlit secret or env var)")
    base_url = base_url or DEFAULT_BASE_URL
    model = model or DEFAULT_MODEL

    client = openai.OpenAI(base_url=base_url, api_key=api_key, timeout=60)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(model=model, messages=messages)
            content = resp.choices[0].message.content
            if isinstance(content, str):
                return content
            # Multimodal replies: concatenate text blocks
            return "".join(getattr(b, "text", "") for b in content)
        except Exception as e:
            is_rate_limit = (
                getattr(e, "status_code", None) == 429
                or "429" in str(e)
                or "rate" in str(e).lower()
            )
            if is_rate_limit:
                if attempt < retries - 1:
                    time.sleep(8 * (attempt + 1))
                    continue
                raise RuntimeError(
                    f"AMAX rate limit (429) persists after {retries} attempts: {e}"
                ) from e
            if attempt < retries - 1:
                time.sleep(3)
                continue
            raise
    raise RuntimeError("unreachable")


def extract_json(text: str) -> Optional[dict]:
    """Extract a JSON object from an LLM reply (tolerates ```json fences)"""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except Exception:
        pass
    # Find the outermost { }
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return None
    return None


# ── Tool catalog builder ───────────────────────────────────

def build_tool_catalog(tools: list) -> str:
    """Compact tool catalog text (fed to the LLM)"""
    entries = []
    for t in tools:
        schema = t.input_schema or {}
        props = schema.get("properties", {})
        params = []
        for pname, pdef in props.items():
            ptype = pdef.get("type", "any")
            pdesc = (pdef.get("description") or "")[:60]
            required = "required" if pname in schema.get("required", []) else "optional"
            params.append(f"{pname}({ptype},{required}): {pdesc}")
        entry = f"### {t.name}\n{(t.description or '')[:200]}"
        if params:
            entry += "\nParameters:\n" + "\n".join(f"- {p}" for p in params)
        entries.append(entry)
    return "\n\n".join(entries)


# ── Test data structures ───────────────────────────────────

@dataclass
class CompatResult:
    tool_name: str
    task: str
    llm_tool: str
    tool_correct: bool
    llm_args: dict
    args_valid: bool
    args_error: str = ""
    duration_ms: float = 0.0


# ── Phase 1: task generation ───────────────────────────────

TASK_GEN_SYSTEM = "You are an MCP tool testing expert. Output JSON only, nothing else."

def generate_tasks(tools: list, max_tools: int = 14) -> list[dict]:
    """Have the LLM generate one natural-language user task per tool"""
    catalog = build_tool_catalog(tools[:max_tools])
    prompt = f"""Below is the tool catalog of an MCP Server. For each tool, design one natural-language user task (something a user would say to an AI assistant, which should result in calling that tool).

Task requirements:
- Sound like a real user; do NOT mention the tool name directly
- The task must clearly require calling that tool
- Argument values should be given in the task or reasonably inferable

Tool catalog:
{catalog}

Output JSON format:
{{"tasks": [{{"tool": "tool_name", "task": "user task"}}]}}"""
    reply = llm_call(prompt, TASK_GEN_SYSTEM)
    data = extract_json(reply)
    if not data or "tasks" not in data:
        raise RuntimeError(f"task generation failed: {reply[:200]}")
    # Keep only tasks with valid tool names
    valid_names = {t.name for t in tools}
    return [t for t in data["tasks"] if t.get("tool") in valid_names]


# ── Phase 2: tool selection + argument filling ─────────────

SELECT_SYSTEM = "You are an AI assistant that selects and calls MCP tools. Output JSON only, nothing else."

def run_selection(tasks: list[dict], tools: list) -> list[CompatResult]:
    """For each task: LLM picks a tool + fills args, then rules validate both"""
    catalog = build_tool_catalog(tools)
    tool_map = {t.name: t for t in tools}
    results = []
    for task_item in tasks:
        start = time.time()
        task = task_item["task"]
        expected_tool = task_item["tool"]
        prompt = f"""You can call the following MCP tools:

{catalog}

The user says: "{task}"

Which tool should you call, and with what arguments?
Output JSON only: {{"tool": "tool_name", "arguments": {{...}}}}"""
        try:
            reply = llm_call(prompt, SELECT_SYSTEM)
            data = extract_json(reply) or {}
            llm_tool = data.get("tool", "")
            llm_args = data.get("arguments", {})
            if not isinstance(llm_args, dict):
                llm_args = {}
        except Exception as e:
            llm_tool = ""
            llm_args = {}
            args_error = f"LLM call failed: {e}"
            results.append(CompatResult(expected_tool, task, llm_tool, False, llm_args, False, args_error, (time.time()-start)*1000))
            continue

        tool_correct = (llm_tool == expected_tool)

        # Argument validation
        args_error = ""
        args_valid = True
        if tool_correct:
            t = tool_map[expected_tool]
            schema = t.input_schema or {}
            required = schema.get("required", [])
            missing = [r for r in required if r not in llm_args]
            if missing:
                args_valid = False
                args_error = f"missing required arguments: {missing}"
            # Rough type check
            props = schema.get("properties", {})
            for k, v in llm_args.items():
                if k in props:
                    ptype = props[k].get("type")
                    if ptype and not _type_ok(v, ptype):
                        args_valid = False
                        args_error += f"argument {k} has wrong type (expected {ptype}) "
        else:
            args_error = f"wrong tool: expected {expected_tool}, got {llm_tool}"

        results.append(CompatResult(expected_tool, task, llm_tool, tool_correct, llm_args, args_valid, args_error.strip(), (time.time()-start)*1000))
    return results


def _type_ok(value, ptype) -> bool:
    type_map = {"string": str, "number": (int, float), "integer": int, "boolean": bool, "array": list, "object": dict}
    # JSON Schema allows type to be an array (e.g. ["string", "null"])
    if isinstance(ptype, list):
        return any(_type_ok(value, p) for p in ptype)
    py_type = type_map.get(ptype)
    if py_type is None:
        return True
    if ptype in ("integer", "number") and isinstance(value, bool):
        return False
    return isinstance(value, py_type)


# ── Summary ────────────────────────────────────────────────

@dataclass
class CompatSummary:
    total: int
    tool_accuracy: float
    args_valid_rate: float
    overall: float
    results: list = field(default_factory=list)

    @property
    def grade(self) -> str:
        if self.overall >= 90:
            return "A+"
        if self.overall >= 80:
            return "A"
        if self.overall >= 70:
            return "B"
        if self.overall >= 60:
            return "C"
        return "D"


def summarize(results: list[CompatResult]) -> CompatSummary:
    total = len(results)
    if total == 0:
        return CompatSummary(0, 0.0, 0.0, 0.0)
    tool_ok = sum(1 for r in results if r.tool_correct)
    args_ok = sum(1 for r in results if r.tool_correct and r.args_valid)
    tool_acc = tool_ok / total * 100
    args_rate = args_ok / total * 100
    # Tool selection 60% + argument compliance 40%
    overall = tool_acc * 0.6 + args_rate * 0.4
    return CompatSummary(total, tool_acc, args_rate, overall, results)
