# Trinetra AI

**Autonomous Detect -> Patch -> Verify shield for mission-critical software.**

Built for the **AI Kavach** track of Indian Army Terrier Cyber Quest 2026, by Team **Cyber Sentinels**.

## The problem

SQL injection remains a persistent OWASP Top-10 flaw across logistics, reporting, and command-support backends. Finding a flaw isn't the hard part -- safely fixing it, and proving the fix holds, is where most tools stop.

## What Trinetra does

Trinetra ("three eyes") is a closed-loop pipeline that:

1. **Detects** -- static analysis flags unsafe, unparameterized SQL queries
2. **Reasons** -- an LLM drafts a parameterized-query patch, with context
3. **Verifies** -- a regression harness replays known SQLi payloads and runs the existing test suite before the fix is ever trusted

If verification fails, the failure feeds back into the reasoning step instead of the pipeline giving up. A patch is never marked "verified" until it survives that gate.

## Architecture

```
Code Input -> Static Analysis -> AI Reasoning -> Sandbox Patch -> Regression Test -> Verified-Fix Report
                                       ^                                |
                                       +----------- retry on fail ------+
```

## Repo layout

| Folder | What lives here |
|---|---|
| `sandbox_app/` | Deliberately vulnerable demo app -- our detection & patch target |
| `src/detect/` | Static analysis / AST scanner |
| `src/reason/` | LLM-based patch generation |
| `src/patch/` | Applies the patch inside an isolated sandbox |
| `src/verify/` | Regression harness + SQLi payload replay |
| `src/pipeline.py` | Orchestrates the full detect -> reason -> patch -> verify loop |
| `tests/` | Unit tests for each stage |
| `reports/` | Sample Verified-Fix Report output |
| `docs/` | Architecture notes and design decisions |

## Status

Early build. Currently working on: `sandbox_app/` and `src/detect/`.

## Tech stack

- Python (core pipeline)
- Static analysis: AST parsing + Bandit/Semgrep-style rules
- Reasoning: LLM API (model-agnostic -- swappable for a local model)
- Verification: Pytest + a custom SQLi payload library
- Isolation: Docker sandbox for safe patch trial-and-apply

## Team

Cyber Sentinels -- Terrier Cyber Quest 2026, AI Kavach track.

## License

MIT -- see [LICENSE](LICENSE).
