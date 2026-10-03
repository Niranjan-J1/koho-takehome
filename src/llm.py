"""Cached Gemini call. Reruns are reproducible because responses are cached, not because of temperature 0 or the seed."""
import hashlib
import json
import os
import time
from pathlib import Path

CACHE = Path(__file__).resolve().parent.parent / "cache"
SEED = 2026
RETRIES = 5
RETRY_CODES = {429, 500, 502, 503, 504}
CONFIG = {"temperature": 0, "seed": SEED, "response_mime_type": "application/json",
          "automatic_function_calling": {"disable": True}}


class LLMError(RuntimeError):
    """Persistent API failure. The run aborts; it is never scored as a model error."""


def cache_key(model, prompt, config=CONFIG):
    blob = json.dumps({"model": model, "prompt": prompt, "config": config}, sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


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
                raise LLMError(f"API call failed: {type(e).__name__} (code={code})") from None
            sleep(5 * 2 ** attempt)
    text = resp.text or ""  # empty or blocked response is a model output; parse() scores it invalid
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"model": model, "config": CONFIG, "prompt": prompt, "text": text}), encoding="utf-8")
    if stats is not None:
        stats["calls"] = stats.get("calls", 0) + 1
    return text
