"""
Trinetra AI -- pipeline orchestrator.

Wires together: detect -> reason -> patch -> verify, with a retry loop
that feeds a failed verification back into the reasoning step.

This is a skeleton only -- fill in each stage as you build it out.
"""

# from src.detect import scan_for_vulnerabilities
# from src.reason import generate_patch
# from src.patch import apply_patch
# from src.verify import run_regression_suite


def run_pipeline(target_path: str, max_retries: int = 2):
    """
    Run the full detect -> reason -> patch -> verify loop on `target_path`.

    TODO:
      1. vulnerabilities = scan_for_vulnerabilities(target_path)
      2. for each vulnerability:
           patch = generate_patch(vulnerability)
           apply_patch(patch)
           result = run_regression_suite()
           if not result.passed and retries_left:
               # feed result.failure_reason back into generate_patch()
               retry
    """
    raise NotImplementedError("Build me step by step -- see README.md for the plan.")


if __name__ == "__main__":
    run_pipeline(target_path="sandbox_app/")
