# Unified LLM gateway — AMAX Token Router

Every model call in this application goes through
[`core/llm_client.py`](../core/llm_client.py). Before this change the code
shelled out to a locally installed `z-ai` CLI (`glm-4-plus`), which is not
available on Streamlit Cloud and forced four separate call sites
(`core/llm_compat.py` x2, `core/agent_loop.py`, `modules/llm_compat_page.py`)
to depend on a subprocess. The gateway uses an **OpenAI-compatible Chat
Completions endpoint** and the Python standard library only, so switching
models is a configuration change and `requirements.txt` needs no new package.

## Configuration

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `AMAX_API_KEY` | **yes** | — | Router key. Never logged, never displayed, never committed. |
| `AMAX_BASE_URL` | no | `https://ai.amaxsmp.com/v1` | Router endpoint. Override for a private gateway. |
| `AMAX_MODEL` | no | `gpt-4o` | Model id. **Must be one your account can reach** — check `GET {base}/models`. |
| `AMAX_TIMEOUT` | no | `120` | Per-request timeout in seconds. |
| `AMAX_TEMPERATURE` | no | unset | When unset the parameter is not sent, keeping reasoning-model endpoints compatible. |

Values are read first from environment variables, then from Streamlit Cloud
Secrets. Locally:

```bash
export AMAX_API_KEY="sk-..."
export AMAX_MODEL="gpt-4o"       # or any model listed by /models
streamlit run app.py
```

On **Streamlit Cloud** open *App settings -> Secrets* and paste (see
[`.streamlit/secrets.example.toml`](../.streamlit/secrets.example.toml)):

```toml
MCP_EVAL_DEMO_READONLY = "1"
AMAX_API_KEY = "sk-..."
AMAX_BASE_URL = "https://ai.amaxsmp.com/v1"
AMAX_MODEL = "gpt-4o"
```

`.streamlit/secrets.toml` is already in `.gitignore`. The example file contains
a placeholder only. **Never put a real key in this repository, in a commit
message, in a log or in a screenshot.**

## Hosted demo

`MCP_EVAL_DEMO_READONLY=1` hides Server Manager, Test Suites, Test Runs, LLM
Compatibility, Scenario Testing and Reports — every page that could register a
server, start a subprocess, call the router or write to the results database.
The four remaining pages and the ISA104 Course page are documentation/read-only.
Consequently **the router is not called at all on the public demo**; it is
configured for local teaching use and for any future authenticated deployment.

## Discovering models

```python
from core.llm_client import list_models
print(list_models())       # GET {AMAX_BASE_URL}/models
```

If a model id is wrong the router returns HTTP 400/404 and the page shows the
error text; the key is never included. This is also why `AMAX_MODEL` has no
hard-coded vendor list — router catalogues change with the account's plan.

## Failure behaviour

- 429 and 5xx: exponential backoff, up to `retries` attempts.
- Network/timeout/JSON errors: retried with a short backoff, then raised as
  `LLMGatewayError` with the exception type and a truncated upstream message.
- No key: fail fast with a message pointing at this file. Nothing is sent.
- `status()` returns only `configured`, `base_url`, `model` and `transport`.

## Migration note for the four call sites

`core/llm_compat.py` still exports `llm_call(prompt, system, retries)` with the
same signature, so `core/agent_loop.py` and `modules/llm_compat_page.py` were
not rewritten. They now resolve to the gateway automatically — one place to
rotate a key, one place to change a model, one place to add tracing later.
