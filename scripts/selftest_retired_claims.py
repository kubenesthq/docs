#!/usr/bin/env python3
"""Prove the retired-claim guard CAN FAIL, and that it does not over-fire.

WHY THIS EXISTS. check_retired_claims.py protects the publish: if a retired
security claim reappears in any wording, the deploy stops. Its failure mode is
therefore entirely in the GREEN path. A broken regex, a renamed registry key, an
exclusion that swallows everything -- any of these makes it print
"retired-claim guard: clean" and exit 0 forever, and nothing downstream notices,
because A RED RESULT GETS INVESTIGATED AND A GREEN ONE DOES NOT.

That is not hypothetical. The published-bundle workload gate had two defects in
one day and BOTH were in its green path: a PASS branch that had never executed
(kn-nlz8) and an experiment arm that changed nothing (kn-i965). Neither was
visible to review; both were visible only to use. This guard has the same shape
and is mine, so it gets the same treatment.

WHAT THIS ASSERTS
  1. EVERY retired claim in the registry has a fixture that trips it, and the
     guard names that claim's id when it does. A new registry entry with no
     fixture FAILS here -- so the registry cannot grow past its own evidence.
  2. The must-pass fixtures, which sit deliberately close to the retired claims
     without making them, do NOT trip it. Over-firing costs a publish and trains
     people to ignore the guard, which is its own way of going quiet.
  3. Every fixture maps to a real registry id, so a fixture for a claim that was
     un-retired does not linger and quietly pass.

The fixtures under tests/retired-claims/ are DELIBERATELY WRONG PROSE. They are
not part of the site and are never published; content/ is what ships.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
GUARD = HERE / "check_retired_claims.py"
REGISTRY = HERE / "retired-claims.json"
FIXTURES = REPO / "tests" / "retired-claims"


def run_guard(content_dir: pathlib.Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(GUARD), "--content", str(content_dir)],
        capture_output=True, text=True,
    )


def main() -> int:
    registry = json.loads(REGISTRY.read_text())
    retired_ids = {entry["id"] for entry in registry["retired"]}

    trip_dir = FIXTURES / "must-trip"
    pass_dir = FIXTURES / "must-pass"
    problems: list[str] = []

    fixture_ids = {p.stem for p in trip_dir.glob("*.mdx")}
    for missing in sorted(retired_ids - fixture_ids):
        problems.append(
            f"NO FIXTURE for retired claim [{missing}]. Add "
            f"tests/retired-claims/must-trip/{missing}.mdx containing prose that "
            "makes the claim, so the guard is proven to catch it."
        )
    for stale in sorted(fixture_ids - retired_ids):
        problems.append(
            f"FIXTURE FOR AN UNKNOWN CLAIM [{stale}]: no registry entry has that "
            "id. Either the claim was un-retired and the fixture should go, or "
            "the id was renamed."
        )

    # 1 + 3: the guard must FAIL on the must-trip corpus and name every id.
    tripped = run_guard(trip_dir)
    if tripped.returncode == 0:
        problems.append(
            "THE GUARD DID NOT FAIL on tests/retired-claims/must-trip. Every page "
            "there makes a retired claim, so a clean result means the guard has "
            "stopped working -- which is exactly the failure it cannot report "
            "about itself."
        )
    named = set(re.findall(r"RETIRED CLAIM REAPPEARED \[([^\]]+)\]", tripped.stdout))
    for unnamed in sorted(retired_ids - named):
        problems.append(
            f"the guard did not catch [{unnamed}] on its own fixture. Its patterns "
            "no longer match prose that makes the claim."
        )

    # 2: and it must NOT fire on the near-miss corpus.
    passed = run_guard(pass_dir)
    if passed.returncode != 0:
        problems.append(
            "THE GUARD FIRED on tests/retired-claims/must-pass, which is prose that "
            "does not make any retired claim:\n" + passed.stdout.strip()
        )

    if problems:
        print("RETIRED-CLAIM GUARD SELF-TEST FAILED\n")
        for p in problems:
            print(f"  - {p}\n")
        return 1

    print(
        f"retired-claim guard self-test: clean "
        f"({len(retired_ids)} retired claim(s) proven to trip, near-misses pass)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
