"""List the models the GEMINI_API_KEY can access, with supported methods. Read-only.

Setup helper for choosing GEMINI_MODEL, so no model string is ever guessed or hardcoded.
"""
import os
import sys

from dotenv import load_dotenv
from google import genai


def main():
    load_dotenv()
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("GEMINI_API_KEY is not set (expected in .env).")
    try:
        client = genai.Client(api_key=key)
        for model in client.models.list():
            print(model.name, "|", ", ".join(model.supported_actions or []))
    except Exception as e:
        sys.exit(f"Listing models failed: {type(e).__name__}")


if __name__ == "__main__":
    main()
