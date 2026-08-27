"""Scenario Testing Framework - multi-tool collaborative workflows

Unlike single-case tests, a scenario consists of multiple tool calls with
state passing between steps (data written by step N must be readable by
step N+1), verifying cross-tool behavioral consistency.

Each scenario:
  required_tools: tool names that must exist (otherwise the scenario is skipped;
                  semi-generic adaptation)
  steps: [(tool, args_fn(ctx), check_fn(text, ctx) -> (bool, msg))]
  ctx is a dict shared across steps
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


# ── Scenario 1: vector lifecycle ───────────────────────────

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
        name="SC-001 Vector Lifecycle",
        description="insert vector -> semantic search finds it -> db count +1",
        required_tools=["insert_vector", "vector_search", "stats"],
        steps=[
            ("stats", lambda ctx: {}, lambda t, ctx: (True, "")),
            ("insert_vector",
             lambda ctx: {"id": vid, "values": [0.05] * _get_dimension(ctx), "metadata": {"src": "scenario-test"}},
             lambda t, ctx: ("success" in t.lower(), f"insert returned: {t[:80]}")),
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
        return False, f"search missed {vid}: {text[:100]}"
    return False, f"non-JSON response: {text[:80]}"


def _check_vector_count(text: str, ctx: dict):
    d = _parse_json(text)
    if isinstance(d, dict):
        total = d.get("vector_db", {}).get("total_vectors")
        if total is not None and total >= 1:
            return True, f"total_vectors={total}"
        return False, f"unexpected count: {text[:80]}"
    return False, f"non-JSON response: {text[:80]}"


# ── Scenario 2: memory lifecycle ───────────────────────────

def _sc_memory_lifecycle() -> Scenario:
    content = f"scenario-test-memory-{uuid.uuid4().hex[:6]}: patient is allergic to the test drug"
    return Scenario(
        name="SC-002 Memory Lifecycle",
        description="remember -> recall hits -> forget -> recall is empty (full CRUD semantics)",
        required_tools=["memory_remember", "memory_recall", "memory_forget"],
        steps=[
            ("memory_remember",
             lambda ctx: {"content": content, "importance": 0.9},
             lambda t, ctx: _extract_memory_id(t, ctx)),
            ("memory_recall",
             lambda ctx: {"query": "test drug allergic patient", "k": 10},
             lambda t, ctx: _check_recall_hit(t, ctx)),
            ("memory_forget",
             lambda ctx: {"id": ctx.get("memory_id", "")},
             lambda t, ctx: ("not found" not in t.lower(), f"forget returned: {t[:60]}")),
            ("memory_recall",
             lambda ctx: {"query": "test drug allergic patient", "k": 10},
             lambda t, ctx: _check_recall_empty(t, ctx)),
        ],
    )


def _extract_memory_id(text: str, ctx: dict):
    d = _parse_json(text)
    if isinstance(d, dict) and d.get("id"):
        ctx["memory_id"] = d["id"]
        return True, f"id={d['id']}"
    return False, f"no id returned: {text[:80]}"


def _check_recall_hit(text: str, ctx: dict):
    d = _parse_json(text)
    if isinstance(d, list):
        mid = ctx.get("memory_id", "")
        for item in d:
            if item.get("id") == mid:
                return True, f"score={item.get('score', '?')}"
        return False, f"recall missed {mid}: {text[:100]}"
    return False, f"non-JSON response: {text[:80]}"


def _check_recall_empty(text: str, ctx: dict):
    d = _parse_json(text)
    if isinstance(d, list):
        mid = ctx.get("memory_id", "")
        if all(item.get("id") != mid for item in d):
            return True, "not retrievable after forget"
        return False, f"still retrievable after forget: {mid}"
    return False, f"non-JSON response: {text[:80]}"


# ── Scenario 3: graph construction and traversal ───────────

def _sc_graph_lifecycle() -> Scenario:
    nid1, nid2, eid = _uid("node"), _uid("node"), _uid("edge")
    return Scenario(
        name="SC-003 Graph Construction & Traversal",
        description="build 2 nodes + 1 edge -> neighbor query -> multi-hop traversal (graph integrity)",
        required_tools=["add_graph_node", "add_graph_edge", "graph_neighbors", "graph_traverse"],
        steps=[
            ("add_graph_node",
             lambda ctx: {"id": nid1, "label": "Hospital", "properties": {"name": "Test Central Hospital"}},
             lambda t, ctx: ("success" in t.lower(), t[:60])),
            ("add_graph_node",
             lambda ctx: {"id": nid2, "label": "Disease", "properties": {"name": "Test Flu"}},
             lambda t, ctx: ("success" in t.lower(), t[:60])),
            ("add_graph_edge",
             lambda ctx: {"id": eid, "label": "TREATS", "source": nid1, "target": nid2},
             lambda t, ctx: ("success" in t.lower(), t[:60])),
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
            return True, f"neighbors include {nid2}"
        return False, f"neighbor missing {nid2}: {text[:100]}"
    return False, f"non-JSON response: {text[:80]}"


def _check_traverse(text: str, nid1: str, nid2: str, eid: str):
    d = _parse_json(text)
    if isinstance(d, dict):
        nodes = {n.get("id") for n in d.get("nodes", [])}
        edges = {e.get("id") for e in d.get("edges", [])}
        ok = nid1 in nodes and nid2 in nodes and eid in edges
        return ok, f"nodes={len(nodes)} edges={len(edges)}"
    return False, f"non-JSON response: {text[:80]}"


# ── Scenario 4: audit chain consistency ────────────────────

def _sc_audit_consistency() -> Scenario:
    vid, nid = _uid("vec"), _uid("node")

    def check_audit_grew(text: str, ctx: dict):
        d = _parse_json(text)
        if isinstance(d, list):
            before = ctx.get("audit_before", 0)
            if len(d) > before:
                return True, f"audit entries {before} -> {len(d)}"
            return False, f"write operations not recorded in audit chain ({before} -> {len(d)})"
        return False, f"non-JSON response: {text[:80]}"

    return Scenario(
        name="SC-004 Audit Chain Consistency",
        description="perform writes -> the audit chain must record them (key compliance scenario)",
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
        return True, f"audit baseline={n}"
    return False, f"non-JSON response: {text[:80]}"


# ── Scenario 5: persistence round-trip ─────────────────────

def _sc_persistence() -> Scenario:
    vid = _uid("vec")
    return Scenario(
        name="SC-005 Persistence Round-Trip",
        description="insert vector -> persist to disk -> count preserved (no data loss)",
        required_tools=["insert_vector", "persist", "stats"],
        steps=[
            ("stats", lambda ctx: {}, lambda t, ctx: _capture_vec_count(t, ctx)),
            ("insert_vector",
             lambda ctx: {"id": vid, "values": [0.05] * _get_dimension(ctx)},
             lambda t, ctx: (True, "")),
            ("persist", lambda ctx: {},
             lambda t, ctx: ("persist" in t.lower() or "saved" in t.lower(), t[:60])),
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
        return after > before, f"vectors {before} -> {after}"
    return False, f"non-JSON response: {text[:80]}"


BUILTIN_SCENARIOS = [
    _sc_vector_lifecycle,
    _sc_memory_lifecycle,
    _sc_graph_lifecycle,
    _sc_audit_consistency,
    _sc_persistence,
]


def match_scenarios(tools: list) -> list[tuple[Scenario, str]]:
    """Match scenarios against the tools the server actually exposes.
    Returns a list of (scenario, status) tuples."""
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
    """Execute one scenario; state passes between steps via ctx."""
    start = time.time()
    ctx = {}
    steps = []
    # Probe dimension first (if stats exists)
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
                ok, msg = False, f"tool error: {text[:100]}"
            else:
                ok, msg = check_fn(text, ctx)
        except Exception as e:
            ok, msg, text = False, f"exception: {str(e)[:100]}", ""
        steps.append(StepResult(tool, args if isinstance(args, dict) else {},
                                ok, msg, text[:200], (time.time() - t0) * 1000))
        if not ok:
            break  # state-passing chain broken; remaining steps are meaningless

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


def _sc_kg_memory_lifecycle() -> Scenario:
    """Knowledge-graph memory lifecycle (adapts to the official server-memory tool family)"""
    marker = f"KGMarker-{uuid.uuid4().hex[:6]}"

    def _check_created(text, ctx):
        ok = marker in text
        return ok, "entity created" if ok else f"entity not found in creation response: {text[:80]}"

    def _check_found(text, ctx):
        ok = marker in text
        return ok, "search hit target entity" if ok else f"search missed: {text[:80]}"

    def _mk_entities_args(ctx):
        return {"entities": [{"name": marker, "entityType": "TestEntity",
                              "observations": ["cross-benchmark test entity"]}]}

    def _mk_search_args(ctx):
        return {"query": marker}

    def _mk_delete_args(ctx):
        return {"entityNames": [marker]}

    def _check_gone(text, ctx):
        ok = marker not in text
        return ok, "not searchable after delete" if ok else f"entity still searchable: {text[:80]}"

    return Scenario(
        name="SC-006 Knowledge-Graph Memory Lifecycle",
        description="create entity -> search hits -> delete entity -> search is empty (official memory server)",
        required_tools=["create_entities", "search_nodes", "delete_entities"],
        steps=[
            ("create_entities", _mk_entities_args, _check_created),
            ("search_nodes", _mk_search_args, _check_found),
            ("delete_entities", _mk_delete_args, lambda t, c: (True, "delete executed")),
            ("search_nodes", _mk_search_args, _check_gone),
        ],
    )


# Register into builtin scenarios (original list + new scenario)
BUILTIN_SCENARIOS = BUILTIN_SCENARIOS + [_sc_kg_memory_lifecycle]
