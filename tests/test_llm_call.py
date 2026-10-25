"""Signature-compatibility and retry-semantics tests for core.llm_compat.llm_call.

Mocks the openai client — no network, no real keys. Env vars below are
dummy values used only to exercise the configuration paths.
"""
import os
import unittest
from unittest import mock

os.environ["AMAX_API_KEY"] = "dummy-test-key"
os.environ["AMAX_BASE_URL"] = "https://example.invalid/v1"
os.environ["AMAX_MODEL"] = "test-model"

from core import llm_compat  # noqa: E402


class _Msg:
    content = "hello world"


class _Choice:
    message = _Msg()


class _Resp:
    choices = [_Choice()]


class LlmCallTest(unittest.TestCase):
    def test_signature_and_success(self):
        with mock.patch("openai.OpenAI") as m:
            inst = m.return_value
            inst.chat.completions.create.return_value = _Resp()
            # historical signature: llm_call(prompt, system="", retries=3)
            out = llm_compat.llm_call("do something", system="be nice", retries=3)
            self.assertEqual(out, "hello world")
            kwargs = inst.chat.completions.create.call_args.kwargs
            self.assertEqual(kwargs["model"], "test-model")
            roles = [msg["role"] for msg in kwargs["messages"]]
            self.assertEqual(roles, ["system", "user"])

    def test_defaults(self):
        with mock.patch("openai.OpenAI") as m:
            inst = m.return_value
            inst.chat.completions.create.return_value = _Resp()
            out = llm_compat.llm_call("p")
            self.assertEqual(out, "hello world")
            # no system prompt → single user message
            roles = [msg["role"] for msg in inst.chat.completions.create.call_args.kwargs["messages"]]
            self.assertEqual(roles, ["user"])

    def test_generic_error_retries_then_succeeds(self):
        with mock.patch("openai.OpenAI") as m:
            inst = m.return_value
            inst.chat.completions.create.side_effect = [ValueError("boom"), _Resp()]
            with mock.patch("time.sleep") as s:
                out = llm_compat.llm_call("p", retries=3)
            self.assertEqual(out, "hello world")
            s.assert_called_once_with(3)

    def test_rate_limit_backoff_and_final_raise(self):
        class FakeRateLimit(Exception):
            status_code = 429

        with mock.patch("openai.OpenAI") as m:
            inst = m.return_value
            inst.chat.completions.create.side_effect = FakeRateLimit("429 too many requests")
            with mock.patch("time.sleep") as s:
                with self.assertRaises(RuntimeError) as ctx:
                    llm_compat.llm_call("p", retries=3)
            self.assertIn("429", str(ctx.exception))
            # sleeps 8*(0+1) and 8*(1+1); final attempt raises immediately
            self.assertEqual(s.call_count, 2)
            s.assert_any_call(8)
            s.assert_any_call(16)

    def test_missing_key_raises_clear_error(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch("openai.OpenAI"):
                with self.assertRaises(RuntimeError) as ctx:
                    llm_compat.llm_call("p")
        self.assertIn("AMAX_API_KEY", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
