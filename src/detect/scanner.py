import re

SQL_KEYWORDS = r"(SELECT|INSERT|UPDATE|DELETE)\b"

# Flags f-strings or concatenation containing SQL keywords —
# the exact pattern in sandbox_app/app.py's vulnerable query.
UNSAFE_PATTERN = re.compile(
    rf"""f['"].*{SQL_KEYWORDS}.*\{{.*\}}.*['"]""",
    re.IGNORECASE,
)


def scan_file(filepath: str) -> list[dict]:
    """Return a list of {line_number, line_text} for each unsafe query found."""
    findings = []
    with open(filepath, "r") as f:
        for i, line in enumerate(f, start=1):
            if UNSAFE_PATTERN.search(line):
                findings.append({"line_number": i, "line_text": line.strip()})
    return findings


if __name__ == "__main__":
    import os

    # Walk up from this file's location to the repo root,
    # so this works no matter which folder you run it from.
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    target = os.path.join(repo_root, "sandbox_app", "app.py")

    results = scan_file(target)
    for r in results:
        print(f"[VULNERABLE] Line {r['line_number']}: {r['line_text']}")