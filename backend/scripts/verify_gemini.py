"""
Standalone verification utility for live Google Gemini API connectivity.
Validates header-based authentication, model reachability, and response parsing
without modifying application data or exposing secret keys.
"""

import asyncio
import os
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ai.gemini_provider import GeminiProvider
from app.core.config import get_settings


async def run_smoke_test() -> int:
    settings = get_settings()

    api_key = settings.gemini_api_key
    if not api_key or not api_key.strip():
        print("=================================================================")
        print("  Google Gemini Provider Live Verification: BLOCKED")
        print("=================================================================")
        print("Reason: GEMINI_API_KEY is not configured in backend/.env or environment.")
        print()
        print("To verify live Gemini integration once you have an API key:")
        print("  1. Add GEMINI_API_KEY=AIzaSy... to backend/.env")
        print("  2. Run: python scripts/verify_gemini.py")
        print("=================================================================")
        return 2

    model_name = settings.gemini_model or "gemini-flash-latest"
    print(f"Connecting to Google Gemini API (model={model_name})...")

    provider = GeminiProvider(
        api_key=api_key,
        model_name=model_name,
        timeout=30.0,
        max_retries=2,
    )

    try:
        response = await provider.generate_text(
            prompt="Respond strictly with the single word: CONNECTIVITY_OK",
            temperature=0.0,
            max_tokens=300,
        )
        print("=================================================================")
        print("  Google Gemini Provider Live Verification: SUCCESS")
        print("=================================================================")
        print(f"Model: {model_name}")
        print(f"Response: {response.strip()}")
        print("Header-based authentication (x-goog-api-key): Verified")
        print("=================================================================")
        return 0
    except Exception as exc:
        sanitized_msg = str(exc)
        # Ensure API key is never printed in output
        if api_key in sanitized_msg:
            sanitized_msg = sanitized_msg.replace(api_key, "[REDACTED_API_KEY]")

        print("=================================================================")
        print("  Google Gemini Provider Live Verification: FAILED")
        print("=================================================================")
        print(f"Model: {model_name}")
        print(f"Error category: {type(exc).__name__}")
        print(f"Details: {sanitized_msg}")
        print("=================================================================")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_smoke_test())
    sys.exit(exit_code)
