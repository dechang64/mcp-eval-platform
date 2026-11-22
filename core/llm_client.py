"""Single LLM gateway for the whole platform: AMAX Token Router.

All model traffic in this repository goes through :func:`chat`. Nothing else
starts a CLI subprocess, reads a vendor key or builds a provider-specific
request. The router exposes an OpenAI-compatible Chat Completions endpoint, so
switching models is a configuration change, not a code change.

Configuration (environment variables or Streamlit Cloud Secrets):
    AMAX_API_KEY       required; router key (never logged, never committed)
    AMAX_BASE_URL      optional; default https://ai.amaxsmp.com/v1
    AMAX_MODEL         optional; default gpt-4o -- override with a model your
                       account can actually reach (GET {base}/models lists them)
    AMAX_TIMEOUT       optional; per-request timeout in seconds (default 120)
    AMAX_TEMPERATURE   optional; when unset the parameter is not sent at all,
                       which keeps reasoning-model endpoints compatible

Only the Python standard library is used, so requirements.txt needs no new
dependency and Streamlit Cloud can install the app unchanged.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import Optional

DEFAULT_BASE_URL = "https://ai.amaxsmp.com/v1"
DEFAULT_MODEL = "gpt-4o"
DEFAULT_TIMEOUT = 120.0


class LLMGatewayError(RuntimeError):
    """Raised when the router cannot be reached or returns an unusable reply."""


def _setting(name: str, default: str = "") -> str:
    value = os.environ.get(name, "").strip()
    if value:
        return value
    try:
        import streamlit as st
        value = str(st.secrets.get(name, "") or "").strip()
    except Exception:
        value = ""
    return value or default


def config() -> dict:
    return {
        "base_url": _setting("AMAX_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
        "api_key": _setting("AMAX_API_KEY"),
        "model": _setting("AMAX_MODEL", DEFAULT_MODEL),
        "timeout": float(_setting("AMAX_TIMEOUT", str(DEFAULT_TIMEOUT))),
        "temperature": _setting("AMAX_TEMPERATURE"),
    }


def is_configured() -> bool:
    return bool(config()["api_key"])


def status() -> dict:
    """UI-safe status: never returns the key or any part of it."""
    c = config()
    return {
        "configured": bool(c["api_key"]),
        "base_url": c["base_url"],
        "model": c["model"],
        "transport": "AMAX Token Router (OpenAI-compatible)",
    }


def _request(url: str, api_key: str, payload: Optional[dict],
             timeout: float, method: str = "POST") -> dict:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {
        "Authorization": "Bearer " + api_key,
        "Accept": "application/json",
        "User-Agent": "ISA104-mcp-eval/1.0",
    }
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def chat(prompt: str, system: str = "", retries: int = 3, *,
         model: str = "", timeout: float = 0) -> str:
    """Send one prompt to the router and return the plain-text reply."""
    c = config()
    if not c["api_key"]:
        raise LLMGatewayError(
            "AMAX_API_KEY is not set. Add it to Streamlit Cloud Secrets (or export "
            "it locally); see docs/AMAX_Router_Setup.md."
        )
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    body = {"model": model or c["model"], "messages": messages}
    if c["temperature"]:
        try:
            body["temperature"] = float(c["temperature"])
        except ValueError:
            pass
    url = c["base_url"] + "/chat/completions"
    tmo = timeout or c["timeout"]
    last = None
    for attempt in range(max(1, retries)):
        try:
            data = _request(url, c["api_key"], body, tmo)
            return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            last = LLMGatewayError("AMAX Router HTTP %d: %s" % (e.code, detail))
            if e.code == 429 or 500 <= e.code < 600:
                time.sleep(min(2 ** attempt * 2, 30))
                continue
            raise last
        except (urllib.error.URLError, TimeoutError, OSError,
                json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
            last = LLMGatewayError(
                "AMAX Router call failed (%s): %s" % (type(e).__name__, e))
            time.sleep(min(2 ** attempt, 15))
    raise last or LLMGatewayError("AMAX Router call failed")


def list_models() -> list:
    """List the model ids the current account can reach (GET /models)."""
    c = config()
    if not c["api_key"]:
        raise LLMGatewayError("AMAX_API_KEY is not set.")
    try:
        data = _request(c["base_url"] + "/models", c["api_key"], None,
                        c["timeout"], method="GET")
    except urllib.error.HTTPError as e:
        raise LLMGatewayError("AMAX Router /models -> HTTP %d" % e.code)
    return [str(x.get("id", "")) for x in data.get("data", []) if x.get("id")]
