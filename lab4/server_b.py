"""Lab 4 - Server B: the defective twin (SSE transport, stdlib only).

Same tool surface and business logic as server_a.py, but five defects are
planted. Evaluate both with the mcp-eval-platform and compare the graded
reports - then find every defect from the failing cases alone.

Run:  python server_b.py [--port 8102]
Eval: register http://localhost:8102/sse in the platform (Transport: sse)

 DEFECT 1 (FN-008): declares a bogus protocol version
 DEFECT 2 (FN-004): unknown tool pretends success
 DEFECT 3 (FN-005): invalid arguments are silently accepted
 DEFECT 4 (SEC-002): path-traversal input kills the session (crash)
 DEFECT 5 (PF-001): artificial 3s delay on every tool call

Hint: diff server_a.py server_b.py to see exactly what changed.
"""
import argparse
import json
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

KNOWN_VERSIONS = ["2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25", "2026-03-26", "2026-07-28"]

TOOLS = [
    {
        "name": "add",
        "description": "Add two integers and return the sum",
        "inputSchema": {
            "type": "object",
            "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
            "required": ["a", "b"],
        },
    },
    {
        "name": "echo",
        "description": "Echo the given text back",
        "inputSchema": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    },
    {
        "name": "lookup_order",
        "description": "Look up a demo order by its id (e.g. 'A-1001')",
        "inputSchema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    },
]
TOOL_NAMES = {t["name"] for t in TOOLS}

ORDERS = {"A-1001": {"item": "robot gripper", "qty": 2, "status": "shipped"},
          "A-1002": {"item": "camera module", "qty": 1, "status": "pending"}}


def ok(text):
    return {"content": [{"type": "text", "text": text}], "isError": False}


def fail(text):
    return {"content": [{"type": "text", "text": text}], "isError": True}


def validate(name, arguments):
    schema = next(t for t in TOOLS if t["name"] == name)["inputSchema"]
    required = schema.get("required", [])
    for r in required:
        if r not in arguments:
            return f"missing required argument: {r}"
    for k in arguments:
        if k not in schema["properties"]:
            return f"unknown argument: {k}"
    return None


def execute(name, arguments):
    if name == "add":
        a, b = arguments["a"], arguments["b"]
        if not isinstance(a, int) or not isinstance(b, int):
            return fail("add expects integers")
        return ok(str(a + b))
    if name == "echo":
        text = str(arguments["text"])
        return ok(text[:200])
    if name == "lookup_order":
        oid = str(arguments["order_id"])[:64]
        order = ORDERS.get(oid)
        if order is None:
            return fail(f"order not found: {oid}")
        return ok(json.dumps(order))
    return fail(f"unknown tool: {name}")


class Session:
    def __init__(self, wfile):
        self.wfile = wfile
        self.lock = __import__("threading").Lock()
        self.alive = True

    def send_event(self, event, data):
        if not self.alive:
            return
        with self.lock:
            try:
                self.wfile.write(f"event: {event}\ndata: {json.dumps(data)}\n\n".encode())
                self.wfile.flush()
            except Exception:
                pass

    def kill(self):
        # DEFECT 4: abrupt disconnect - the client sees the server "crash"
        self.alive = False
        try:
            self.wfile.close()
        except Exception:
            pass


SESSIONS = {}


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        if urlparse(self.path).path != "/sse":
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        sid = uuid.uuid4().hex[:16]
        SESSIONS[sid] = Session(self.wfile)
        self.wfile.write(f"event: endpoint\ndata: /messages?session_id={sid}\n\n".encode())
        self.wfile.flush()
        try:
            while True:
                time.sleep(1)
                self.wfile.write(b": keepalive\n\n")
                self.wfile.flush()
        except Exception:
            SESSIONS.pop(sid, None)

    def do_POST(self):
        u = urlparse(self.path)
        if u.path != "/messages":
            self.send_error(404)
            return
        sid = parse_qs(u.query).get("session_id", [None])[0]
        session = SESSIONS.get(sid)
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        self.send_response(202)
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"ok")
        if session is None:
            return
        try:
            msg = json.loads(body)
        except Exception:
            return
        response = self.dispatch(msg, session)
        if response is not None:
            session.send_event("message", response)

    def dispatch(self, msg, session):
        method = msg.get("method")
        msg_id = msg.get("id")

        if method == "initialize":
            # DEFECT 1: version negotiation ignored - always claims a version
            # that exists in no spec release. The declaration is a contract.
            return {"jsonrpc": "2.0", "id": msg_id, "result": {
                "protocolVersion": "2027-13-99",
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "lab4-server-b", "version": "1.0.0"},
            }}
        if method == "notifications/initialized":
            return None
        if method == "ping":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {}}
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}}
        if method == "tools/call":
            params = msg.get("params", {})
            name = params.get("name", "")
            arguments = params.get("arguments", {}) or {}

            # DEFECT 5: artificial latency on every call - performance
            # regressions are defects too, and graders measure them
            time.sleep(3.0)

            # DEFECT 4: hostile input crashes the whole server process
            # (the classic pattern behind real CVEs: unvalidated input
            # reaches a fatal code path; the evaluator sees the connection
            # drop and every later case fails)
            if "../" in json.dumps(arguments):
                session.kill()
                import os
                os._exit(1)

            if name not in TOOL_NAMES:
                # DEFECT 2: pretends success for an unknown tool
                return {"jsonrpc": "2.0", "id": msg_id, "result": ok("done")}

            err = validate(name, arguments)
            if err:
                # DEFECT 3: invalid arguments silently accepted - validation
                # result computed, then ignored
                return {"jsonrpc": "2.0", "id": msg_id, "result": ok("done")}

            return {"jsonrpc": "2.0", "id": msg_id, "result": execute(name, arguments)}
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"method not found: {method}"}}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8102)
    args = ap.parse_args()
    print(f"Server B (defective) listening on http://0.0.0.0:{args.port}/sse")
    ThreadingHTTPServer(("0.0.0.0", args.port), Handler).serve_forever()
