"""LLM兼容性测试引擎

测试目标：LLM 能否根据 MCP Server 的工具描述
  1. 选对工具（工具选择准确率）
  2. 填对参数（参数 schema 合规率）

流程：连接被测Server拿工具列表 → LLM为每个工具生成自然语言任务
     → LLM（看到工具目录+任务）选择工具+填参数 → 规则校验
"""
import asyncio
import json
import re
import subprocess
import time
from dataclasses import dataclass, field
from typing import Optional


# ── z-ai CLI 封装 ──────────────────────────────────────────

def llm_call(prompt: str, system: str = "", retries: int = 3) -> str:
    """调用 z-ai CLI，返回纯文本回复。429自动退避重试。"""
    cmd = ["z-ai", "chat", "-p", prompt]
    if system:
        cmd += ["-s", system]
    for attempt in range(retries):
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            out = proc.stdout
            # 过滤🚀初始化行，取JSON
            lines = [l for l in out.splitlines() if not l.startswith("🚀")]
            data = json.loads("\n".join(lines))
            return data["choices"][0]["message"]["content"]
        except subprocess.TimeoutExpired:
            if attempt == retries - 1:
                raise RuntimeError("z-ai CLI timeout")
            time.sleep(5)
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            if attempt == retries - 1:
                raise RuntimeError(f"z-ai output parse failed: {e}: {out[:200]}")
            time.sleep(3)
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                time.sleep(8 * (attempt + 1))
            elif attempt == retries - 1:
                raise
            else:
                time.sleep(3)
    raise RuntimeError("unreachable")


def extract_json(text: str) -> Optional[dict]:
    """从LLM回复中提取JSON对象（容忍```json```包裹）"""
    # 尝试直接解析
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except Exception:
        pass
    # 找最外层 { }
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return None
    return None


# ── 工具目录构建 ──────────────────────────────────────────

def build_tool_catalog(tools: list) -> str:
    """精简的工具目录文本（喂给LLM）"""
    entries = []
    for t in tools:
        schema = t.input_schema or {}
        props = schema.get("properties", {})
        params = []
        for pname, pdef in props.items():
            ptype = pdef.get("type", "any")
            pdesc = (pdef.get("description") or "")[:60]
            required = "必填" if pname in schema.get("required", []) else "可选"
            params.append(f"{pname}({ptype},{required}): {pdesc}")
        entry = f"### {t.name}\n{(t.description or '')[:200]}"
        if params:
            entry += "\n参数:\n" + "\n".join(f"- {p}" for p in params)
        entries.append(entry)
    return "\n\n".join(entries)


# ── 测试数据结构 ──────────────────────────────────────────

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


# ── 阶段1：任务生成 ────────────────────────────────────────

TASK_GEN_SYSTEM = "你是MCP工具测试专家。只输出JSON，不要输出其他内容。"

def generate_tasks(tools: list, max_tools: int = 14) -> list[dict]:
    """让LLM为每个工具生成一个自然语言用户任务"""
    catalog = build_tool_catalog(tools[:max_tools])
    prompt = f"""以下是MCP Server提供的工具目录。请为每个工具设计一个自然语言用户任务（用户会对AI助手说这句话，助手应调用对应工具完成任务）。

任务要求：
- 像真实用户口吻，不直接提到工具名
- 任务应该明确需要调用该工具
- 参数值在任务中给出或可合理推断

工具目录：
{catalog}

输出JSON格式：
{{"tasks": [{{"tool": "工具名", "task": "用户任务"}}]}}"""
    reply = llm_call(prompt, TASK_GEN_SYSTEM)
    data = extract_json(reply)
    if not data or "tasks" not in data:
        raise RuntimeError(f"task generation failed: {reply[:200]}")
    # 只保留合法工具名的任务
    valid_names = {t.name for t in tools}
    return [t for t in data["tasks"] if t.get("tool") in valid_names]


# ── 阶段2：工具选择+参数填充 ──────────────────────────────

SELECT_SYSTEM = "你是AI助手，需要选择并调用MCP工具。只输出JSON，不要输出其他内容。"

def run_selection(tasks: list[dict], tools: list) -> list[CompatResult]:
    """对每个任务，让LLM选工具+填参数，然后规则校验"""
    catalog = build_tool_catalog(tools)
    tool_map = {t.name: t for t in tools}
    results = []
    for task_item in tasks:
        start = time.time()
        task = task_item["task"]
        expected_tool = task_item["tool"]
        prompt = f"""你可以调用以下MCP工具：

{catalog}

用户说："{task}"

你应该调用哪个工具？如何填参数？
只输出JSON：{{"tool": "工具名", "arguments": {{...}}}}"""
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
            args_error = f"LLM调用失败: {e}"
            results.append(CompatResult(expected_tool, task, llm_tool, False, llm_args, False, args_error, (time.time()-start)*1000))
            continue

        tool_correct = (llm_tool == expected_tool)

        # 参数校验
        args_error = ""
        args_valid = True
        if tool_correct:
            t = tool_map[expected_tool]
            schema = t.input_schema or {}
            required = schema.get("required", [])
            missing = [r for r in required if r not in llm_args]
            if missing:
                args_valid = False
                args_error = f"缺少必填参数: {missing}"
            # 类型粗查
            props = schema.get("properties", {})
            for k, v in llm_args.items():
                if k in props:
                    ptype = props[k].get("type")
                    if ptype and not _type_ok(v, ptype):
                        args_valid = False
                        args_error += f"参数{k}类型错误(期望{ptype}) "
        else:
            args_error = f"选错工具: 期望{expected_tool}, 实际{llm_tool}"

        results.append(CompatResult(expected_tool, task, llm_tool, tool_correct, llm_args, args_valid, args_error.strip(), (time.time()-start)*1000))
    return results


def _type_ok(value, ptype) -> bool:
    type_map = {"string": str, "number": (int, float), "integer": int, "boolean": bool, "array": list, "object": dict}
    # JSON Schema 允许 type 为数组（如 ["string", "null"]）
    if isinstance(ptype, list):
        return any(_type_ok(value, p) for p in ptype)
    py_type = type_map.get(ptype)
    if py_type is None:
        return True
    if ptype in ("integer", "number") and isinstance(value, bool):
        return False
    return isinstance(value, py_type)


# ── 汇总 ──────────────────────────────────────────────────

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
    # 工具选择60% + 参数合规40%
    overall = tool_acc * 0.6 + args_rate * 0.4
    return CompatSummary(total, tool_acc, args_rate, overall, results)
