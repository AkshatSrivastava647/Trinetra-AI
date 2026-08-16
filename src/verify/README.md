# verify

Regression verification harness. Replays known SQLi payloads against the patched
code and runs the existing functional test suite.

A patch is only marked "verified" if it survives this gate. If it fails, the
failure is fed back into `reason/` for another attempt.

Status: not yet built.
