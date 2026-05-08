#!/usr/bin/env python3
"""Runs mutmut and fails if the mutation score is below THRESHOLD.

Current threshold: 50% — raise to 65% once T-06 (build_wa_url unit tests) lands,
since the surviving mutants are mostly static-file config lines not exercised by
the current BDD integration tests.
"""

import subprocess
import sys
import xml.etree.ElementTree as ET

THRESHOLD = 50


def main() -> None:
    subprocess.run(["mutmut", "run"], check=False)

    result = subprocess.run(
        ["mutmut", "junitxml"],
        capture_output=True,
        text=True,
        check=True,
    )

    root = ET.fromstring(result.stdout)
    total = int(root.get("tests", 0))
    survived = int(root.get("failures", 0))
    killed = total - survived
    score = (killed / total * 100) if total > 0 else 0.0

    print(f"Mutation score: {killed}/{total} ({score:.1f}%)")

    if score < THRESHOLD:
        print(f"FAIL: {score:.1f}% is below the {THRESHOLD}% threshold")
        sys.exit(1)

    print(f"PASS: {score:.1f}% meets the {THRESHOLD}% threshold")


if __name__ == "__main__":
    main()
