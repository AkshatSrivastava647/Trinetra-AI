# Architecture

See the flow diagram in the main [README](../README.md).

Design notes:
- CPU-only, single-container target -- no GPU dependency
- Reasoning layer is model-agnostic (hosted API or local model)
- Verification is a hard gate: nothing is called "fixed" until the original
  exploit fails and the test suite passes
