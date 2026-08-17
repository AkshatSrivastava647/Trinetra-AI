"""
src/reason/generator.py

Uses Google's Gemini API to generate a safe, parameterized replacement
for a SQL injection vulnerability. Implements exponential backoff for
free‑tier rate limits.

Part of Trinetra AI's "Detect → Reason → Patch → Verify" pipeline.
"""

import os
import time
import json
import random
from typing import Dict, List, Optional

from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


class RateLimitExceeded(Exception):
    """Custom exception for rate‑limit errors after retries."""
    pass


def call_gemini_with_retry(
    prompt: str,
    model: str = "gemini-2.0-flash-lite",  # free tier, fast and cheap
    max_retries: int = 5,
    initial_delay: float = 1.0,
) -> str:
    """
    Send a prompt to Gemini with exponential backoff on rate‑limit errors.

    Args:
        prompt: The full prompt string.
        model: Gemini model name (flash‑lite is free & suitable).
        max_retries: Maximum number of retry attempts.
        initial_delay: Starting delay in seconds (doubles each retry).

    Returns:
        The text response from the model.

    Raises:
        RateLimitExceeded if all retries fail.
    """
    # Get API key from environment
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not set in environment or .env file."
        )

    # Initialize the client
    client = genai.Client(api_key=api_key)

    delay = initial_delay
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                # Optional: set temperature for more deterministic output
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=512,
                ),
            )
            # The response object has a 'text' attribute
            return response.text

        except Exception as e:
            # Check if the error is rate‑limit related (status 429 or similar)
            # The SDK may raise a specific error; we'll catch all and inspect.
            error_str = str(e).lower()
            if "rate" in error_str or "quota" in error_str or "429" in error_str:
                if attempt == max_retries - 1:
                    raise RateLimitExceeded(
                        f"Rate limit exceeded after {max_retries} retries."
                    ) from e
                # Exponential backoff with jitter
                sleep_time = delay * (2 ** attempt) + random.uniform(0, 0.5)
                print(f"Rate limit hit. Retrying in {sleep_time:.2f}s...")
                time.sleep(sleep_time)
            else:
                # Non‑rate‑limit error – re-raise immediately
                raise

    # Should never reach here, but fallback
    raise RateLimitExceeded("Unexpected failure in retry loop.")


def generate_fix(
    vulnerable_line: str,
    context_lines: Optional[List[str]] = None,
    filepath: Optional[str] = None,
) -> Dict[str, str]:
    """
    Given a vulnerable line and (optionally) surrounding context, ask Gemini
    to produce a safe parameterized replacement.

    Args:
        vulnerable_line: The exact line of code with the SQL injection flaw.
        context_lines: List of lines around the vulnerable line (including
                       function definition, other statements) for context.
        filepath: If provided, we could read more context – but it's optional.

    Returns:
        A dict with:
            - original_line: the input vulnerable line.
            - fixed_line: the suggested safe replacement line.
            - explanation: plain‑English description of the fix.
    """
    # Build a coherent prompt with clear instructions
    if context_lines:
        context = "\n".join(context_lines)
        context_block = f"Here is the surrounding context (the function where this line appears):\n```\n{context}\n```\n"
    else:
        context_block = ""

    prompt = f"""
You are a security expert tasked with fixing a SQL injection vulnerability.

{context_block}
The specific vulnerable line is: