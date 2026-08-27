#!/usr/bin/env python3
"""Minimal MCP Server for testing - implements 3 tools"""
import asyncio
import json
from mcp.server import Server
from mcp import types

server = Server("test-echo-server")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="echo",
            description="Echo back the input message",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Message to echo"},
                },
                "required": ["message"],
            },
        ),
        types.Tool(
            name="add",
            description="Add two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                },
                "required": ["a", "b"],
            },
        ),
        types.Tool(
            name="status",
            description="Get server status",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "echo":
        msg = arguments.get("message", "")
        return [types.TextContent(type="text", text=f"Echo: {msg}")]
    elif name == "add":
        a = arguments.get("a", 0)
        b = arguments.get("b", 0)
        return [types.TextContent(type="text", text=str(a + b))]
    elif name == "status":
        return [types.TextContent(type="text", text=json.dumps({"status": "ok", "tools": 3}))]
    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    from mcp.server.stdio import stdio_server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
