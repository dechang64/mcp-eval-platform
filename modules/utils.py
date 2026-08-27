"""Shared utility functions"""
import json
import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def fmt_duration(ms: float) -> str:
    if ms < 1000:
        return f"{ms:.0f}ms"
    return f"{ms/1000:.1f}s"


def fmt_timestamp(ts: str) -> str:
    if not ts:
        return "-"
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%m-%d %H:%M")
    except Exception:
        return ts


def status_badge(status: str) -> str:
    icons = {"passed": "✅", "failed": "❌", "skipped": "⏭️", "error": "💥", "running": "🔄"}
    return f"{icons.get(status, '❓')} {status}"


def run_async(coro):
    """Run an async coroutine inside Streamlit"""
    try:
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(coro)
        loop.close()
        return result
    except Exception as e:
        raise e


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
