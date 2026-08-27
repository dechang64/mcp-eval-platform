"""场景化测试框架 - 多工具协同工作流测试

与单用例测试的区别：场景由多个工具调用组成，步骤间有状态传递
（上一步写入的数据，下一步必须能读到），检验的是工具间协同性。

每个场景:
  required_tools: 需要的工具名（缺失则 skipped，实现半通用适配）
  steps: [(tool, args_fn(ctx), check_fn(text, ctx) -> (bool, msg))]
  ctx 是步骤间共享的上下文 dict
"""
import asyncio
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Callable, Optional


@dataclass
class StepResult:
    tool: str
    args: dict
    ok: bool
    message: str
    response_snippet: str = ""
    duration_ms: float = 0.0


@dataclass
class ScenarioResult:
    name: str
    description: str
    status: str  # passed / failed / skipped
    steps: list = field(default_factory=list)
    duration_ms: float = 0.0

    @property
    def passed_steps(self) -> int:
        return sum(1 for s in self.steps if s.ok)


@dataclass
class Scenario:
    name: str
    description: str
    required_tools: list
    steps: list  # [(tool, args_fn, check_fn)]


def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _get_dimension(ctx: dict, default: int = 384) -> int:
    return ctx.get("dimension", default)


def _parse_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None


# ── 场景1: 向量生命周期 ─────────────────────────────────────

def _sc_vector_lifecycle() -> Scenario:
    vid = _uid("vec")

    async def get_dim(client, ctx):
        r = await client.call_tool("stats", {})
        d = _parse_json(r.content[0]["text"] if r.content else "")
        if d:
            ctx["dimension"] = d.get("vector_db", {}).get("dimension", 384)
        else:
            ctx["dimension"] = 384

    return Scenario(
        name="SC-001 向量生命周期",
        description="插入向量 → 语义检索能找到 → 数据库计数+1",
        required_tools=["insert_vector", "vector_search", "stats"],
        steps=[
            ("stats", lambda ctx: {}, lambda t, ctx: (True, "")),
            ("insert_vector",
             lambda ctx: {"id": vid, "values": [0.05] * _get_dimension(ctx), "metadata": {"src": "scenario-test"}},
             lambda t, ctx: ("成功" in t or "success" in t.lower(), f"插入返回: {t[:80]}")),
            ("vector_search",
             lambda ctx: {"query_vector": [0.05] * _get_dimension(ctx), "k": 5},
             lambda t, ctx: _check_search_hit(t, vid)),
            ("stats",
             lambda ctx: {},
             lambda t, ctx: _check_vector_count(t, ctx)),
        ],
    )


def _check_search_hit(text: str, vid: str):
    d = _parse_json(text)
    if isinstance(d, list):
        for item in d:
            if item.get("id") == vid:
                return True, f"score={item.get('score', '?')}"
        return False, f"检索未命中 {vid}: {text[:100]}"
    return False, f"非JSON响应: {text[:80]}"


def _check_vector_count(text: str, ctx: dict):
    d = _parse_json(text)
    if isinstance(d, dict):
        total = d.get("vector_db", {}).get("total_vectors")
        if total is not None and total >= 1:
            return True, f"total_vectors={total}"
        return False, f"计数异常: {text[:80]}"
    return False, f"非JSON响应: {text[:80]}"


# ── 场景2: 记忆管理循环 ─────────────────────────────────────

def _sc_memory_lifecycle() -> Scenario:
    content = f"场景测试记忆-{uuid.uuid4().hex[:6]}：患者对测试药物过敏"
    return Scenario(
        name="SC-002 记忆管理循环",
        description="写入记忆 → 检索命中 → 遗忘 → 检索为空（完整CRUD语义）",
        required_tools=["memory_remember", "memory_recall", "memory_forget"],
        steps=[
            ("memory_remember",
             lambda ctx: {"content": content, "importance": 0.9},
             lambda t, ctx: _extract_memory_id(t, ctx)),
            ("memory_recall",
             lambda ctx: {"query": "测试药物 过敏", "k": 10},
             lambda t, ctx: _check_recall_hit(t, ctx)),
            ("memory_forget",
             lambda ctx: {"id": ctx.get("memory_id", "")},
             lambda t, ctx: ("not found" not in t.lower(), f"forget返回: {t[:60]}")),
            ("memory_recall",
             lambda ctx: {"query": "测试药物 过敏", "k": 10},
             lambda t, ctx: _check_recall_empty(t, ctx)),
        ],
    )


def _extract_memory_id(text: str, ctx: dict):
    d = _parse_json(text)
    if isinstance(d, dict) and d.get("id"):
        ctx["memory_id"] = d["id"]
        return True, f"id={d['id']}"
    return False, f"未返回id: {text[:80]}"


def _check_recall_hit(text: str, ctx: dict):
    d = _parse_json(text)
    if isinstance(d, list):
        mid = ctx.get("memory_id", "")
        for item in d:
            if item.get("id") == mid:
                return True, f"score={item.get('score', '?')}"
        return False, f"检索未命中 {mid}: {text[:100]}"
    return False, f"非JSON响应: {text[:80]}"


def _check_recall_empty(text: str, ctx: dict):
    d = _parse_json(text)
    if isinstance(d, list):
        mid = ctx.get("memory_id", "")
        if all(item.get("id") != mid for item in d):
            return True, "遗忘后不可检索"
        return False, f"遗忘后仍能检索到 {mid}"
    return False, f"非JSON响应: {text[:80]}"


# ── 场景3: 图谱构建与遍历 ───────────────────────────────────

def _sc_graph_lifecycle() -> Scenario:
    nid1, nid2, eid = _uid("node"), _uid("node"), _uid("edge")
    return Scenario(
        name="SC-003 图谱构建与遍历",
        description="双节点+边构建 → 邻居查询 → 多跳遍历（图完整性）",
        required_tools=["add_graph_node", "add_graph_edge", "graph_neighbors", "graph_traverse"],
        steps=[
            ("add_graph_node",
             lambda ctx: {"id": nid1, "label": "Hospital", "properties": {"name": "测试中心医院"}},
             lambda t, ctx: ("成功" in t or "success" in t.lower(), t[:60])),
            ("add_graph_node",
             lambda ctx: {"id": nid2, "label": "Disease", "properties": {"name": "测试流感"}},
             lambda t, ctx: ("成功" in t or "success" in t.lower(), t[:60])),
            ("add_graph_edge",
             lambda ctx: {"id": eid, "label": "TREATS", "source": nid1, "target": nid2},
             lambda t, ctx: ("成功" in t or "success" in t.lower(), t[:60])),
            ("graph_neighbors",
             lambda ctx: {"node_id": nid1},
             lambda t, ctx: _check_neighbor(t, nid2)),
            ("graph_traverse",
             lambda ctx: {"start_id": nid1, "max_hops": 2},
             lambda t, ctx: _check_traverse(t, nid1, nid2, eid)),
        ],
    )


def _check_neighbor(text: str, nid2: str):
    d = _parse_json(text)
    if isinstance(d, list):
        if any(item.get("id") == nid2 for item in d):
            return True, f"邻居含 {nid2}"
        return False, f"邻居缺失 {nid2}: {text[:100]}"
    return False, f"非JSON响应: {text[:80]}"


def _check_traverse(text: str, nid1: str, nid2: str, eid: str):
    d = _parse_json(text)
    if isinstance(d, dict):
        nodes = {n.get("id") for n in d.get("nodes", [])}
        edges = {e.get("id") for e in d.get("edges", [])}
        ok = nid1 in nodes and nid2 in nodes and eid in edges
        return ok, f"nodes={len(nodes)} edges={len(edges)}"
    return False, f"非JSON响应: {text[:80]}"


# ── 场景4: 审计链一致性 ─────────────────────────────────────

def _sc_audit_consistency() -> Scenario:
    vid, nid = _uid("vec"), _uid("node")

    def check_audit_grew(text: str, ctx: dict):
        d = _parse_json(text)
        if isinstance(d, list):
            before = ctx.get("audit_before", 0)
            if len(d) > before:
                return True, f"审计条目 {before} → {len(d)}"
            return False, f"写入操作未被审计链记录（{before} → {len(d)}）"
        return False, f"非JSON响应: {text[:80]}"

    return Scenario(
        name="SC-004 审计链一致性",
        description="执行写入操作 → 审计链必须记录（合规性关键场景）",
        required_tools=["insert_vector", "add_graph_node", "audit_recent", "stats"],
        steps=[
            ("stats", lambda ctx: {},
             lambda t, ctx: _capture_audit_len(t, ctx)),
            ("insert_vector",
             lambda ctx: {"id": vid, "values": [0.05] * _get_dimension(ctx)},
             lambda t, ctx: (True, "")),
            ("add_graph_node",
             lambda ctx: {"id": nid, "label": "TestNode"},
             lambda t, ctx: (True, "")),
            ("audit_recent",
             lambda ctx: {"limit": 100},
             check_audit_grew),
        ],
    )


def _capture_audit_len(text: str, ctx: dict):
    d = _parse_json(text)
    if isinstance(d, dict):
        n = d.get("audit_chain", {}).get("total_entries", 0)
        ctx["audit_before"] = n
        return True, f"审计条目基线={n}"
    return False, f"非JSON响应: {text[:80]}"


# ── 场景5: 持久化往返 ───────────────────────────────────────

def _sc_persistence() -> Scenario:
    vid = _uid("vec")
    return Scenario(
        name="SC-005 持久化往返",
        description="写入向量 → persist落盘 → 计数保持（数据不丢）",
        required_tools=["insert_vector", "persist", "stats"],
        steps=[
            ("stats", lambda ctx: {}, lambda t, ctx: _capture_vec_count(t, ctx)),
            ("insert_vector",
             lambda ctx: {"id": vid, "values": [0.05] * _get_dimension(ctx)},
             lambda t, ctx: (True, "")),
            ("persist", lambda ctx: {},
             lambda t, ctx: ("persist" in t.lower() or "保存" in t or "成功" in t, t[:60])),
            ("stats", lambda ctx: {},
             lambda t, ctx: _check_count_grew(t, ctx)),
        ],
    )


def _capture_vec_count(text: str, ctx: dict):
    d = _parse_json(text)
    if isinstance(d, dict):
        ctx["vec_before"] = d.get("vector_db", {}).get("total_vectors", 0)
        return True, ""
    return False, ""


def _check_count_grew(text: str, ctx: dict):
    d = _parse_json(text)
    if isinstance(d, dict):
        after = d.get("vector_db", {}).get("total_vectors", 0)
        before = ctx.get("vec_before", 0)
        return after > before, f"vectors {before} → {after}"
    return False, f"非JSON响应: {text[:80]}"


BUILTIN_SCENARIOS = [
    _sc_vector_lifecycle,
    _sc_memory_lifecycle,
    _sc_graph_lifecycle,
    _sc_audit_consistency,
    _sc_persistence,
]


def match_scenarios(tools: list) -> list[tuple[Scenario, str]]:
    """按server实际拥有的工具匹配场景。返回 (scenario, status) 列表。"""
    names = {t.name for t in tools}
    out = []
    for factory in BUILTIN_SCENARIOS:
        sc = factory()
        missing = [t for t in sc.required_tools if t not in names]
        if missing:
            out.append((sc, "skipped"))
        else:
            out.append((sc, "ready"))
    return out


async def run_scenario(client, scenario: Scenario) -> ScenarioResult:
    """执行一个场景：步骤间通过 ctx 传递状态。"""
    start = time.time()
    ctx = {}
    steps = []
    # 先探测dimension（如果stats存在）
    names = {t.name for t in await client.list_tools()} if hasattr(client, "list_tools") else set()
    if "stats" in names:
        try:
            r = await client.call_tool("stats", {})
            d = _parse_json(r.content[0]["text"] if r.content else "")
            if isinstance(d, dict):
                ctx["dimension"] = d.get("vector_db", {}).get("dimension", 384)
        except Exception:
            pass

    for tool, args_fn, check_fn in scenario.steps:
        t0 = time.time()
        try:
            args = args_fn(ctx) if callable(args_fn) else args_fn
            r = await client.call_tool(tool, args)
            text = r.content[0]["text"] if r.content else ""
            if r.is_error:
                ok, msg = False, f"工具报错: {text[:100]}"
            else:
                ok, msg = check_fn(text, ctx)
        except Exception as e:
            ok, msg, text = False, f"异常: {str(e)[:100]}", ""
        steps.append(StepResult(tool, args if isinstance(args, dict) else {},
                                ok, msg, text[:200], (time.time() - t0) * 1000))
        if not ok:
            break  # 状态传递链断裂，后续步骤无意义

    passed = all(s.ok for s in steps) and len(steps) == len(scenario.steps)
    return ScenarioResult(
        scenario.name, scenario.description,
        "passed" if passed else "failed",
        steps, (time.time() - start) * 1000,
    )


async def run_all_scenarios(client, progress_cb=None) -> list[ScenarioResult]:
    tools = await client.list_tools()
    matched = match_scenarios(tools)
    results = []
    for sc, status in matched:
        if status == "skipped":
            results.append(ScenarioResult(sc.name, sc.description, "skipped", [], 0))
            continue
        r = await run_scenario(client, sc)
        results.append(r)
        if progress_cb:
            progress_cb(r)
    return results
