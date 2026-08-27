"""MCP客户端封装 - 支持stdio和SSE双transport"""
import asyncio
import json
import os
import sys
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Optional

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.sse import sse_client


@dataclass
class McpServerConfig:
    """MCP Server连接配置"""
    name: str
    transport: str  # "stdio" or "sse"
    # stdio
    command: str = ""
    args: list = field(default_factory=list)
    env: dict = field(default_factory=dict)
    # sse
    url: str = ""
    # misc
    description: str = ""
    tags: list = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "McpServerConfig":
        return cls(
            name=d["name"],
            transport=d.get("transport", "stdio"),
            command=d.get("command", ""),
            args=d.get("args", []),
            env=d.get("env", {}),
            url=d.get("url", ""),
            description=d.get("description", ""),
            tags=d.get("tags", []),
        )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "transport": self.transport,
            "command": self.command,
            "args": self.args,
            "env": self.env,
            "url": self.url,
            "description": self.description,
            "tags": self.tags,
        }


@dataclass
class ToolInfo:
    name: str
    description: str
    input_schema: dict


@dataclass
class CallResult:
    content: list
    is_error: bool
    raw: Any


class McpClient:
    """MCP客户端 - 封装连接、发现、调用"""

    def __init__(self, config: McpServerConfig):
        self.config = config
        self._session: Optional[ClientSession] = None
        self._tools: list[ToolInfo] = []
        self._server_info: dict = {}

    async def connect(self) -> dict:
        """连接MCP Server，返回server info"""
        try:
            if self.config.transport == "stdio":
                params = StdioServerParameters(
                    command=self.config.command,
                    args=self.config.args,
                    env={**os.environ, **self.config.env} if self.config.env else None,
                )
                self._ctx = stdio_client(params)
                read, write = await self._ctx.__aenter__()
            elif self.config.transport == "sse":
                self._ctx = sse_client(self.config.url)
                read, write = await self._ctx.__aenter__()
            else:
                return {"error": f"Unknown transport: {self.config.transport}"}

            self._session = ClientSession(read, write)
            await self._session.__aenter__()

            # Initialize
            result = await self._session.initialize()
            self._server_info = {
                "protocol_version": result.protocolVersion,
                "capabilities": result.capabilities.model_dump() if hasattr(result.capabilities, 'model_dump') else {},
                "server_name": result.serverInfo.name if result.serverInfo else "",
                "server_version": result.serverInfo.version if result.serverInfo else "",
            }
            return self._server_info
        except Exception as e:
            return {"error": str(e)}

    async def list_tools(self) -> list[ToolInfo]:
        """列出所有可用tools"""
        if not self._session:
            return []
        result = await self._session.list_tools()
        self._tools = [
            ToolInfo(
                name=t.name,
                description=t.description or "",
                input_schema=t.inputSchema.model_dump() if hasattr(t.inputSchema, 'model_dump') else dict(t.inputSchema),
            )
            for t in result.tools
        ]
        return self._tools

    async def call_tool(self, name: str, arguments: dict = None, timeout: float = 30) -> CallResult:
        """调用指定tool"""
        if not self._session:
            return CallResult(content=[], is_error=True, raw=None)
        try:
            result = await asyncio.wait_for(
                self._session.call_tool(name, arguments or {}),
                timeout=timeout,
            )
            content = []
            for c in (result.content or []):
                if hasattr(c, 'text'):
                    content.append({"type": "text", "text": c.text})
                else:
                    content.append({"type": str(type(c).__name__), "data": str(c)})
            return CallResult(
                content=content,
                is_error=result.isError if hasattr(result, 'isError') else False,
                raw=result,
            )
        except asyncio.TimeoutError:
            return CallResult(content=[{"type": "error", "text": "Timeout"}], is_error=True, raw=None)
        except Exception as e:
            return CallResult(content=[{"type": "error", "text": str(e)}], is_error=True, raw=None)

    async def list_resources(self):
        """列出resources（可选）"""
        if not self._session:
            return None
        try:
            result = await self._session.list_resources()
            return result.resources
        except Exception:
            return None

    async def list_prompts(self):
        """列出prompts（可选）"""
        if not self._session:
            return None
        try:
            result = await self._session.list_prompts()
            return result.prompts
        except Exception:
            return None

    async def close(self):
        """关闭连接"""
        try:
            if self._session:
                await self._session.__aexit__(None, None, None)
            if hasattr(self, '_ctx'):
                await self._ctx.__aexit__(None, None, None)
        except Exception:
            pass
        self._session = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args):
        await self.close()
