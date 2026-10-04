"""Cached Gemini call: the only module that talks to the API. eval.py sends every prompt through classify().

Reruns are reproducible because responses are cached, not because of temperature 0 or the seed:
those reduce variation between fresh calls but do not guarantee identical outputs, so a cleared
cache can give different results.
"""
import hashlib
import json
import os
import time
from pathlib import Path

CACHE = Path(__file__).resolve().parent.parent / "cache"
SEED = 2026
RETRIES = 5
RETRY_CODES = {429, 500, 502, 503, 504}
# JSON mode, but deliberately no enum/schema on the category: a constrained enum would hide
# invented categories, which we want to see and score as errors. AFC is off because no tools are used.
CONFIG = {"temperature": 0, "seed": SEED, "response_mime_type": "application/json",
          "automatic_function_calling": {"disable": True}}


class LLMError(RuntimeError):
    """Persistent API failure. The run aborts; it is never scored as a model error.

    An outage or quota error says nothing about classification quality. Scoring it as wrong would
    penalise whichever approach happened to be running, so we stop and resume from the cache instead.
    """


def cache_key(model, prompt, config=CONFIG):
    """The model is part of the key so responses from different models never collide. After the
    switch from gemini-3.8-flash, its cached calls stay separate and cannot leak into results."""
    blob = json.dumps({"model": model, "prompt": prompt, "config": config}, sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _redact(text):
    key = os.environ.get("GEMINI_API_KEY")
    return text.replace(key, "[REDACTED]") if key else text


def _save_error(e, cache_dir):
    """Keep the full error body (quota metric, retry delay) so a persistent failure is diagnosable."""
    body = {k: getattr(e, k, None) for k in ("code", "status", "message", "details")}
    body["type"] = type(e).__name__
    path = Path(cache_dir) / "last_error.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_redact(json.dumps(body, indent=2, default=str)), encoding="utf-8")


def make_client():
    from dotenv import load_dotenv
    from google import genai
    load_dotenv()
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise LLMError("GEMINI_API_KEY is not set (expected in .env).")
    return genai.Client(api_key=key)


def classify(prompt, model, client=None, cache_dir=CACHE, sleep=time.sleep, stats=None):
    """Return the raw response text for `prompt`, from cache if present. Only successful calls are cached."""
    path = Path(cache_dir) / f"{cache_key(model, prompt)}.json"
    if path.exists():
        if stats is not None:
            stats["hits"] = stats.get("hits", 0) + 1
        return json.loads(path.read_text(encoding="utf-8"))["text"]
    client = client or make_client()
    for attempt in range(RETRIES):
        try:
            resp = client.models.generate_content(model=model, contents=prompt, config=CONFIG)
            break
        except Exception as e:  # transport errors have no code; retry those too
            code = getattr(e, "code", None)
            if (code is not None and code not in RETRY_CODES) or attempt == RETRIES - 1:
                _save_error(e, cache_dir)
                status, msg = getattr(e, "status", None), getattr(e, "message", None)
                raise LLMError(_redact(f"API call failed: {type(e).__name__} (code={code}, status={status}): {msg}. "
                                       f"Full body in {Path(cache_dir) / 'last_error.json'}")) from None
            sleep(5 * 2 ** attempt)
    text = resp.text or ""  # empty or blocked response is a model output; parse() scores it invalid
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"model": model, "config": CONFIG, "prompt": prompt, "text": text}), encoding="utf-8")
    if stats is not None:
        stats["calls"] = stats.get("calls", 0) + 1
    return text
