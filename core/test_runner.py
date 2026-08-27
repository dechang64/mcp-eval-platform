"""测试执行引擎 - 加载用例、执行、收集结果"""
import asyncio
import json
import os
import time
import statistics
from dataclasses import dataclass, field
from typing import Optional

from .mcp_client import McpClient, McpServerConfig, ToolInfo

SUITE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_cases", "test_suites.json")


def load_suites() -> dict:
    with open(SUITE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@dataclass
class CaseResult:
    case_id: str
    case_name: str
    category: str
    status: str  # passed/failed/skipped/error
    duration_ms: float
    detail: dict = field(default_factory=dict)
    error_msg: str = ""


def resolve_template(template: dict, tools: list[ToolInfo]) -> dict:
    """替换模板中的占位符"""
    if not template:
        return {}
    first_tool = tools[0].name if tools else "unknown"
    s = json.dumps(template)
    # Use json.dumps to properly escape replacement values
    s = s.replace("{first_tool}", json.dumps(first_tool)[1:-1])  # strip quotes
    s = s.replace("{long_string_10k}", json.dumps("A" * 10000)[1:-1])
    s = s.replace("{nested_100x}", json.dumps("[" * 100 + "]" * 100)[1:-1])
    s = s.replace("{special_chars}", json.dumps("\x00\x01\x02\n\r\t")[1:-1])
    return json.loads(s)


def pick_callable_tool(tools: list[ToolInfo]) -> tuple[str, dict]:
    """选一个可调用的tool（优先无必选参数的），返回(name, default_args)"""
    for t in tools:
        schema = t.input_schema or {}
        props = schema.get("properties", {})
        required = schema.get("required", [])
        if not required:
            return t.name, {}
    # All tools have required params - pick first and fill defaults
    if tools:
        t = tools[0]
        schema = t.input_schema or {}
        props = schema.get("properties", {})
        required = schema.get("required", [])
        args = {}
        for prop_name in required:
            p = props.get(prop_name, {})
            ptype = p.get("type", "string")
            if ptype == "string":
                args[prop_name] = "test"
            elif ptype == "number" or ptype == "integer":
                args[prop_name] = 1
            elif ptype == "boolean":
                args[prop_name] = True
            else:
                args[prop_name] = "test"
        return t.name, args
    return "unknown", {}


def check_expected(result, expected: dict, tool_name: str = "") -> tuple[bool, str]:
    """检查返回值是否符合预期"""
    if not expected:
        return True, ""

    # no_crash: 只要Server没断连就算通过
    if expected.get("no_crash") and result is not None:
        return True, ""

    if result is None:
        return False, "No response (server may have crashed)"

    # Check is_error
    if "is_error" in expected:
        expected_err = expected["is_error"]
        actual_err = getattr(result, "is_error", False)
        if actual_err != expected_err:
            return False, f"is_error mismatch: expected {expected_err}, got {actual_err}"

    # Check content exists
    if expected.get("content") == "exists":
        content = getattr(result, "content", None)
        if not content:
            return False, "No content in response"

    # Check tools is non-empty array
    if "tools" in expected:
        spec = expected["tools"]
        # This is for list_tools result, handled separately
        pass

    # Check protocol_version
    if "protocol_version" in expected and expected["protocol_version"] == "not_null":
        if not getattr(result, "protocolVersion", None):
            return False, "No protocol_version in response"

    # Check capabilities exists
    if "capabilities" in expected and expected["capabilities"] == "exists":
        if not getattr(result, "capabilities", None):
            return False, "No capabilities in response"

    # Check server_info exists
    if "server_info" in expected and expected["server_info"] == "exists":
        if not getattr(result, "serverInfo", None):
            return False, "No server_info in response"

    return True, ""


async def run_functional_case(client: McpClient, case: dict, tools: list[ToolInfo]) -> CaseResult:
    """执行单个功能测试用例"""
    cid = case["id"]
    name = case["name"]
    method = case.get("method", "")
    timeout = case.get("timeout", 30)
    optional = case.get("optional", False)

    start = time.time()
    try:
        if method == "initialize":
            # Already done during connect, just check info
            info = client._server_info
            if info.get("error"):
                return CaseResult(cid, name, "functional", "failed", (time.time()-start)*1000,
                                  {}, f"Connect error: {info['error']}")
            passed, msg = True, ""
            if "protocol_version" in case.get("expected", {}):
                if not info.get("protocol_version"):
                    passed, msg = False, "No protocol_version"
            return CaseResult(cid, name, "functional", "passed" if passed else "failed",
                              (time.time()-start)*1000, info, msg)

        elif method == "tools/list":
            tlist = await client.list_tools()
            detail = {"tool_count": len(tlist), "tools": [t.name for t in tlist]}
            if not tlist and not optional:
                return CaseResult(cid, name, "functional", "failed", (time.time()-start)*1000,
                                  detail, "No tools returned")
            return CaseResult(cid, name, "functional", "passed", (time.time()-start)*1000, detail)

        elif method == "tools/call":
            params = resolve_template(case.get("params_template") or case.get("params", {}), tools)
            tool_name = params.get("name", "")
            arguments = params.get("arguments", {})
            # If non-existent tool test, keep as is
            if "__nonexistent" in tool_name:
                tool_name = "__nonexistent_tool_xyz__"
                arguments = {}
            else:
                # Check if the tool has required params not satisfied by arguments
                tool_info = next((t for t in tools if t.name == tool_name), None)
                if tool_info:
                    required = (tool_info.input_schema or {}).get("required", [])
                    missing = [r for r in required if r not in arguments]
                    if missing:
                        # Use pick_callable_tool to find a better one
                        ct_name, ct_args = pick_callable_tool(tools)
                        if ct_name != "unknown":
                            tool_name, arguments = ct_name, ct_args
                elif not tool_name or tool_name == "unknown":
                    tool_name, arguments = pick_callable_tool(tools)
            result = await client.call_tool(tool_name, arguments, timeout=timeout)
            detail = {"tool": tool_name, "args": arguments, "result": result.content[:2]}
            expected = case.get("expected", {})
            passed, msg = check_expected(result, expected, tool_name)
            return CaseResult(cid, name, "functional", "passed" if passed else "failed",
                              (time.time()-start)*1000, detail, msg)

        elif method == "resources/list":
            resources = await client.list_resources()
            if resources is None:
                return CaseResult(cid, name, "functional", "skipped", (time.time()-start)*1000,
                                  {}, "Resources not supported")
            detail = {"resource_count": len(resources)}
            return CaseResult(cid, name, "functional", "passed", (time.time()-start)*1000, detail)

        elif method == "prompts/list":
            prompts = await client.list_prompts()
            if prompts is None:
                return CaseResult(cid, name, "functional", "skipped", (time.time()-start)*1000,
                                  {}, "Prompts not supported")
            detail = {"prompt_count": len(prompts)}
            return CaseResult(cid, name, "functional", "passed", (time.time()-start)*1000, detail)

        else:
            return CaseResult(cid, name, "functional", "skipped", (time.time()-start)*1000,
                              {}, f"Unknown method: {method}")

    except Exception as e:
        return CaseResult(cid, name, "functional", "error", (time.time()-start)*1000,
                          {}, str(e))


async def run_performance_case(client: McpClient, case: dict, tools: list[ToolInfo]) -> CaseResult:
    """执行性能测试用例"""
    cid = case["id"]
    name = case["name"]
    iterations = case.get("iterations", 20)
    params = resolve_template(case.get("params_template", {}), tools)
    tool_name = params.get("name", "")
    arguments = params.get("arguments", {})
    # Pick a callable tool if template or tool has missing required params
    if tool_name in ("{first_tool}", "unknown", ""):
        tool_name, arguments = pick_callable_tool(tools)
    else:
        tool_info = next((t for t in tools if t.name == tool_name), None)
        if tool_info:
            required = (tool_info.input_schema or {}).get("required", [])
            missing = [r for r in required if r not in arguments]
            if missing:
                ct_name, ct_args = pick_callable_tool(tools)
                if ct_name != "unknown":
                    tool_name, arguments = ct_name, ct_args
    timeout = case.get("timeout", 120)

    latencies = []
    errors = 0

    # Warmup
    try:
        await client.call_tool(tool_name, arguments, timeout=timeout)
    except Exception:
        pass

    start = time.time()
    for i in range(iterations):
        t0 = time.time()
        result = await client.call_tool(tool_name, arguments, timeout=timeout)
        t1 = time.time()
        latencies.append((t1 - t0) * 1000)
        if result.is_error:
            errors += 1

    total_time = time.time() - start

    if "concurrency_levels" in case:
        # Concurrency test
        detail = {"concurrency_results": []}
        for level in case["concurrency_levels"]:
            iter_per = case.get("iterations_per_level", 10)
            async def single_call():
                t0 = time.time()
                r = await client.call_tool(tool_name, arguments, timeout=timeout)
                return (time.time() - t0) * 1000, r.is_error

            tasks = [single_call() for _ in range(level * iter_per)]
            # Run in batches of `level`
            results_all = []
            for batch_start in range(0, len(tasks), level):
                batch = tasks[batch_start:batch_start + level]
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                results_all.extend(batch_results)

            lat = [r[0] for r in results_all if isinstance(r, tuple)]
            errs = sum(1 for r in results_all if isinstance(r, tuple) and r[1])
            rps = len(lat) / (sum(lat) / 1000) if sum(lat) > 0 else 0
            detail["concurrency_results"].append({
                "concurrency": level,
                "rps": round(rps, 1),
                "errors": errs,
                "p50_ms": round(statistics.median(lat), 1) if lat else 0,
                "p95_ms": round(sorted(lat)[int(len(lat) * 0.95)] if lat else 0, 1),
            })
        status = "passed" if all(r["errors"] == 0 for r in detail["concurrency_results"]) else "failed"
        return CaseResult(cid, name, "performance", status, (time.time()-start)*1000, detail)

    elif "trend_slope" in case.get("metrics", []):
        # Stability test
        detail = {
            "iterations": len(latencies),
            "mean_ms": round(statistics.mean(latencies), 1) if latencies else 0,
            "p50_ms": round(statistics.median(latencies), 1) if latencies else 0,
            "p95_ms": round(sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0, 1),
            "p99_ms": round(sorted(latencies)[int(len(latencies) * 0.99)] if latencies else 0, 1),
            "max_min_ratio": round(max(latencies) / min(latencies), 2) if latencies and min(latencies) > 0 else 0,
            "errors": errors,
        }
        # Simple trend: compare first half vs second half
        mid = len(latencies) // 2
        first_half = statistics.mean(latencies[:mid]) if mid > 0 else 0
        second_half = statistics.mean(latencies[mid:]) if mid > 0 else 0
        detail["trend"] = "degrading" if second_half > first_half * 1.5 else "stable"
        status = "passed" if errors == 0 and detail["max_min_ratio"] < 5 else "failed"
        return CaseResult(cid, name, "performance", status, (time.time()-start)*1000, detail)

    else:
        # Latency benchmark
        detail = {
            "iterations": len(latencies),
            "mean_ms": round(statistics.mean(latencies), 1) if latencies else 0,
            "p50_ms": round(statistics.median(latencies), 1) if latencies else 0,
            "p95_ms": round(sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0, 1),
            "p99_ms": round(sorted(latencies)[int(len(latencies) * 0.99)] if latencies else 0, 1),
            "min_ms": round(min(latencies), 1) if latencies else 0,
            "max_ms": round(max(latencies), 1) if latencies else 0,
            "errors": errors,
        }
        status = "passed" if errors == 0 else "failed"
        return CaseResult(cid, name, "performance", status, (time.time()-start)*1000, detail)


async def run_security_case(client: McpClient, case: dict, tools: list[ToolInfo]) -> CaseResult:
    """执行安全测试用例"""
    cid = case["id"]
    name = case["name"]
    params = resolve_template(case.get("params_template", {}), tools)
    tool_name = params.get("name", "")
    arguments = params.get("arguments", {})
    timeout = case.get("timeout", 15)

    start = time.time()
    try:
        result = await client.call_tool(tool_name, arguments, timeout=timeout)
        # Security cases: server didn't crash = passed
        if result is None:
            return CaseResult(cid, name, "security", "failed", (time.time()-start)*1000,
                              {}, "Server crashed or no response")
        # Server responded (even with error) = it survived
        detail = {"tool": tool_name, "args_keys": list(arguments.keys()),
                  "is_error": result.is_error,
                  "content_preview": str(result.content[0])[:200] if result.content else ""}
        # Check if server is still alive by listing tools
        try:
            await client.list_tools()
            still_alive = True
        except Exception:
            still_alive = False

        if still_alive:
            return CaseResult(cid, name, "security", "passed", (time.time()-start)*1000, detail)
        else:
            return CaseResult(cid, name, "security", "failed", (time.time()-start)*1000,
                              detail, "Server became unresponsive after test")
    except Exception as e:
        # If timeout but server still alive = pass (it handled the malicious input)
        try:
            await client.list_tools()
            return CaseResult(cid, name, "security", "passed", (time.time()-start)*1000,
                              {"timeout": True}, f"Handled gracefully (timeout): {e}")
        except Exception:
            return CaseResult(cid, name, "security", "failed", (time.time()-start)*1000,
                              {}, f"Server crashed: {e}")


async def run_suite(client: McpClient, suite_type: str = "all") -> list[CaseResult]:
    """执行完整测试套件"""
    suites = load_suites()
    tools = await client.list_tools()

    results = []
    categories = ["functional", "performance", "security"] if suite_type == "all" else [suite_type]

    for cat in categories:
        cases = suites.get(cat, [])
        for case in cases:
            if cat == "functional":
                r = await run_functional_case(client, case, tools)
            elif cat == "performance":
                r = await run_performance_case(client, case, tools)
            elif cat == "security":
                r = await run_security_case(client, case, tools)
            else:
                continue
            results.append(r)

    return results
