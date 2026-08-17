"""
Trinetra AI -- Reason module.

Takes a vulnerable code line (from src/detect/scanner.py) + surrounding
context, asks Gemini to generate a safe, parameterized-query replacement,
and returns a structured result: original_line, fixed_line, explanation.
"""

import os
import json
import time
import random

from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"  # swap here if this model ever gets deprecated
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


def call_gemini_with_retry(prompt: str, max_retries: int = 5) -> str:
    """Call Gemini, retrying ONLY on rate-limit (429) errors, with exponential backoff."""
    wait_seconds = 1
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
            return response.text
        except Exception as e:
            is_rate_limit = "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)
            if is_rate_limit and attempt < max_retries - 1:
                time.sleep(wait_seconds + random.uniform(0, 0.5))
                wait_seconds *= 2
                continue
            raise
    raise RuntimeError("Exceeded max retries calling Gemini API.")


def generate_fix(vulnerable_line: str, context_lines: str) -> dict:
    """Ask Gemini to rewrite a vulnerable SQL line as a safe, parameterized query."""
    prompt = f"""You are a security engineer fixing a SQL injection vulnerability
in a Python Flask + sqlite3 application.

Here is the surrounding code for context: This line builds a SQL query using an f-string, which allows SQL injection
(e.g. an attacker passing ' OR '1'='1 as input). Rewrite ONLY this line to
use a parameterized query instead (sqlite3 style: use "?" placeholders in
the query string, and pass the actual values as a separate tuple argument
to cur.execute()).

Respond with ONLY valid JSON, no markdown formatting, no code fences,
in exactly this shape:

{{
  "original_line": "the exact original line, unchanged",
  "fixed_line": "the new, safe line(s) as a single string, using \\n for line breaks if more than one line is needed",
  "explanation": "one or two plain-English sentences on what was wrong and how the fix addresses it"
}}

Example of the expected format (a different, similar case):

Input vulnerable line:
query = f"SELECT * FROM users WHERE username = '{{username}}'"

Expected JSON output:
{{
  "original_line": "query = f\\"SELECT * FROM users WHERE username = '{{username}}'\\"",
  "fixed_line": "query = \\"SELECT * FROM users WHERE username = ?\\"\\ncur.execute(query, (username,))",
  "explanation": "The original line inserted user input directly into the SQL string, letting an attacker change the query's logic. The fix uses a '?' placeholder and passes the value separately, so the database treats it as pure data, never as SQL code."
}}

Now produce the JSON for the actual vulnerable line given above."""

    raw = call_gemini_with_retry(prompt).strip()

    # Gemini sometimes wraps JSON in ```json fences even when told not to --
    # strip that defensively before parsing.
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    return json.loads(raw)


if __name__ == "__main__":
    vulnerable_line = 'query = f"SELECT id, name, location, status FROM units WHERE name = \'{name}\'"'
    context = '''@app.route("/unit/search")
def search():
    name = request.args.get("name", "")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    query = f"SELECT id, name, location, status FROM units WHERE name = '{name}'"
    cur.execute(query)'''

    result = generate_fix(vulnerable_line, context)
    print("Original:", result["original_line"])
    print("Fixed:   ", result["fixed_line"])
    print("Why:     ", result["explanation"])