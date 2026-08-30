"""Lab 4 - Server A: the reference MCP server (SSE transport, stdlib only).

A protocol-correct Model Context Protocol server you can evaluate with the
mcp-eval-platform. It should score A+ on the standard suite.

Run:  python server_a.py [--port 8101]
Eval: register http://localhost:8101/sse in the platform (Transport: sse)

Protocol implemented: HTTP+SSE transport (MCP 2024-11-05 style)
  GET  /sse                        -> event stream, first event "endpoint"
  POST /messages?session_id=...    -> JSON-RPC requests (202 Accepted)
                                      responses are pushed back on the SSE stream
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
    # Tool-level error: the call completed, the tool refused. Correct MCP behaviour.
    return {"content": [{"type": "text", "text": text}], "isError": True}


def validate(name, arguments):
    """Schema validation - rejects wrong/extra params before executing."""
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
    """Pure business logic. No I/O, no SQL, no filesystem - nothing to exploit."""
    time.sleep(0.02)  # simulated tool work: real tools take a few tens of ms
    if name == "add":
        a, b = arguments["a"], arguments["b"]
        if not isinstance(a, int) or not isinstance(b, int):
            return fail("add expects integers")
        return ok(str(a + b))
    if name == "echo":
        text = str(arguments["text"])
        # Defensive: even weird payloads just get echoed, never interpreted
        return ok(text[:200])
    if name == "lookup_order":
        oid = str(arguments["order_id"])[:64]
        order = ORDERS.get(oid)
        if order is None:
            return fail(f"order not found: {oid}")
        return ok(json.dumps(order))
    return fail(f"unknown tool: {name}")  # unreachable: dispatch checks first


class Session:
    def __init__(self, wfile):
        self.wfile = wfile
        self.lock = __import__("threading").Lock()

    def send_event(self, event, data):
        with self.lock:
            try:
                self.wfile.write(f"event: {event}\ndata: {json.dumps(data)}\n\n".encode())
                self.wfile.flush()
            except Exception:
                pass


SESSIONS = {}  # session_id -> Session


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass  # keep stdout clean: logs must never leak into the protocol channel

    # ---------- SSE channel ----------
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
        # First event: tell the client where to POST messages
        self.wfile.write(f"event: endpoint\ndata: /messages?session_id={sid}\n\n".encode())
        self.wfile.flush()
        # Hold the stream open; the platform's client closes it on disconnect
        try:
            while True:
                time.sleep(1)
                self.wfile.write(b": keepalive\n\n")
                self.wfile.flush()
        except Exception:
            SESSIONS.pop(sid, None)

    # ---------- message channel ----------
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
            return  # malformed JSON: drop silently, never crash
        response = self.dispatch(msg)
        if response is not None:
            session.send_event("message", response)

    # ---------- JSON-RPC dispatch ----------
    def dispatch(self, msg):
        method = msg.get("method")
        msg_id = msg.get("id")

        if method == "initialize":
            requested = msg.get("params", {}).get("protocolVersion", KNOWN_VERSIONS[0])
            # Correct negotiation: honour the client's version if we know it
            version = requested if requested in KNOWN_VERSIONS else KNOWN_VERSIONS[0]
            return {"jsonrpc": "2.0", "id": msg_id, "result": {
                "protocolVersion": version,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "lab4-server-a", "version": "1.0.0"},
            }}
        if method == "notifications/initialized":
            return None  # notifications carry no id and get no response
        if method == "ping":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {}}
        if method == "tools/list":
            return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": TOOLS}}
        if method == "tools/call":
            params = msg.get("params", {})
            name = params.get("name", "")
            arguments = params.get("arguments", {}) or {}
            if name not in TOOL_NAMES:
                # Unknown tool: refuse, do not crash, do not pretend success
                return {"jsonrpc": "2.0", "id": msg_id, "result": fail(f"unknown tool: {name}")}
            err = validate(name, arguments)
            if err:
                # Invalid arguments: explicit tool-level error with a reason
                return {"jsonrpc": "2.0", "id": msg_id, "result": fail(f"invalid arguments: {err}")}
            return {"jsonrpc": "2.0", "id": msg_id, "result": execute(name, arguments)}
        # Unknown method: protocol-level error, still a well-formed response
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": f"method not found: {method}"}}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8101)
    args = ap.parse_args()
    print(f"Server A (reference) listening on http://0.0.0.0:{args.port}/sse")
    ThreadingHTTPServer(("0.0.0.0", args.port), Handler).serve_forever()
