"""Smoke test: one generate_content call to the model named in GEMINI_MODEL."""
import os
import sys

from dotenv import load_dotenv
from google import genai


def main():
    load_dotenv()
    key = os.environ.get("GEMINI_API_KEY")
    model = os.environ.get("GEMINI_MODEL")
    if not key:
        sys.exit("GEMINI_API_KEY is not set (expected in .env).")
    if not model:
        sys.exit("GEMINI_MODEL is not set (expected in .env).")
    try:
        client = genai.Client(api_key=key)
        response = client.models.generate_content(
            model=model, contents="Reply with the single word: ok"
        )
        print("model:", model)
        print("response:", response.text)
    except Exception as e:
        sys.exit(f"Smoke test failed: {type(e).__name__}: {str(e)[:200]}")


if __name__ == "__main__":
    main()
