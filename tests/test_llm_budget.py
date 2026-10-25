"""Unit tests for the LLM daily budget counter in core.results_store."""
import os
import tempfile
import unittest

# Point the DB at a throwaway file BEFORE importing results_store.
_tmpdir = tempfile.mkdtemp(prefix="mcp_eval_budget_test_")
os.environ["MCP_EVAL_DB"] = os.path.join(_tmpdir, "test.db")

from core import results_store  # noqa: E402


class LlmDailyBudgetTest(unittest.TestCase):
    def setUp(self):
        conn = results_store.get_db()
        conn.execute("DELETE FROM llm_daily_usage")
        conn.commit()
        conn.close()

    def test_counter_starts_at_zero(self):
        self.assertEqual(results_store.count_llm_runs_today(), 0)

    def test_increment_accumulates(self):
        results_store.increment_llm_runs_today()
        results_store.increment_llm_runs_today()
        self.assertEqual(results_store.count_llm_runs_today(), 2)

    def test_budget_default_is_200(self):
        os.environ.pop("LLM_DAILY_BUDGET_RUNS", None)
        self.assertEqual(results_store.get_llm_daily_budget(), 200)

    def test_budget_env_override(self):
        os.environ["LLM_DAILY_BUDGET_RUNS"] = "3"
        try:
            self.assertEqual(results_store.get_llm_daily_budget(), 3)
            # 0 runs used < 3 budget → not exceeded; after 3 runs → exceeded
            self.assertFalse(results_store.count_llm_runs_today() >= results_store.get_llm_daily_budget())
            for _ in range(3):
                results_store.increment_llm_runs_today()
            self.assertTrue(results_store.count_llm_runs_today() >= results_store.get_llm_daily_budget())
        finally:
            os.environ.pop("LLM_DAILY_BUDGET_RUNS", None)


if __name__ == "__main__":
    unittest.main()
