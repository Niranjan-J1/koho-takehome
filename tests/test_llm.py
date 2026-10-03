import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from llm import LLMError, cache_key, classify  # noqa: E402


class FakeError(Exception):
    def __init__(self, code, status=None, message=None, details=None):
        self.code, self.status, self.message, self.details = code, status, message, details


class FakeClient:
    """Pops one scripted outcome per call: an exception to raise or a text to return."""
    def __init__(self, outcomes):
        self.outcomes, self.calls = list(outcomes), []
        self.models = SimpleNamespace(generate_content=self._gen)

    def _gen(self, model, contents, config):
        self.calls.append((model, contents, config))
        out = self.outcomes.pop(0)
        if isinstance(out, Exception):
            raise out
        return SimpleNamespace(text=out)


def no_sleep(_):
    pass


def test_cache_key_stable_and_sensitive():
    assert cache_key("m", "p") == cache_key("m", "p")
    assert cache_key("m", "p") != cache_key("m", "q") != cache_key("n", "p")


def test_miss_then_hit_calls_client_once(tmp_path):
    client, stats = FakeClient(['{"category": "Dining"}']), {}
    assert classify("p", "m", client, tmp_path, no_sleep, stats) == '{"category": "Dining"}'
    assert classify("p", "m", client, tmp_path, no_sleep, stats) == '{"category": "Dining"}'
    assert len(client.calls) == 1 and stats == {"calls": 1, "hits": 1}
    assert client.calls[0][2]["temperature"] == 0 and client.calls[0][2]["automatic_function_calling"] == {"disable": True}


def test_retries_rate_limit_then_succeeds(tmp_path):
    client, waits = FakeClient([FakeError(429), FakeError(503), "ok"]), []
    assert classify("p", "m", client, tmp_path, waits.append) == "ok"
    assert len(client.calls) == 3 and waits == [5, 10]


def test_persistent_failure_aborts_and_caches_no_response(tmp_path):
    client = FakeClient([FakeError(429)] * 5)
    with pytest.raises(LLMError):
        classify("p", "m", client, tmp_path, no_sleep)
    assert [p.name for p in tmp_path.iterdir()] == ["last_error.json"]


def test_error_body_saved_and_key_redacted(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "SECRET123")
    details = {"error": {"status": "RESOURCE_EXHAUSTED", "details": [{"quotaMetric": "per_day", "note": "SECRET123"}]}}
    client = FakeClient([FakeError(429, "RESOURCE_EXHAUSTED", "quota exceeded", details)] * 5)
    with pytest.raises(LLMError) as exc:
        classify("p", "m", client, tmp_path, no_sleep)
    saved = json.loads((tmp_path / "last_error.json").read_text(encoding="utf-8"))
    assert saved["status"] == "RESOURCE_EXHAUSTED" and saved["details"]["error"]["details"][0]["quotaMetric"] == "per_day"
    assert "SECRET123" not in (tmp_path / "last_error.json").read_text(encoding="utf-8")
    assert "RESOURCE_EXHAUSTED" in str(exc.value) and "quota exceeded" in str(exc.value)


def test_non_retryable_error_aborts_immediately(tmp_path):
    client = FakeClient([FakeError(400)])
    with pytest.raises(LLMError):
        classify("p", "m", client, tmp_path, no_sleep)
    assert len(client.calls) == 1


def test_empty_response_returned_as_empty_text(tmp_path):
    assert classify("p", "m", FakeClient([None]), tmp_path, no_sleep) == ""
