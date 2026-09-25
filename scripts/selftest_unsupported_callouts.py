#!/usr/bin/env python3
"""Prove the unsupported-command guard fires on its fixtures, and does not over-fire.

WHY THIS EXISTS, and it is the same reason as scripts/selftest_retired_claims.py:
the guard's failure mode is entirely in its GREEN path. If it stops matching, or
the list rots into naming pages and commands that are no longer there, it prints
"clean" and exits 0 forever, and nothing downstream notices -- a red result gets
investigated and a green one does not.

WHAT THIS ASSERTS
  1. THE LIST IS NOT STALE. Every pair points at a page that exists under the
     repository AND still shows that command. A page that quietly loses the
     command the list names is how the list starts checking nothing, so it fails
     here rather than in a green guard run.
  2. EVERY LISTED PAIR HAS ITS OWN must-trip FIXTURE, named from the pair, and
     the guard names each one when run over that corpus -- so the registry cannot
     grow past its own evidence.
  3. THE GUARD DOES NOT FIRE on must-pass: a listed command inside a proper
     callout, and commands outside the list with no callout at all. Over-firing
     blocks a publish and teaches people to bypass the gate.
  4. THE FIXTURES ARE A CLOSED SET. A must-trip fixture whose pair left the list
     is an orphan and fails, so the corpus cannot drift from the registry.

WHAT THIS DOES NOT PROVE. That the list is COMPLETE. It is a hand-written
enumeration; a command missing from both the CLI and the list passes here.
G0.7's CLI metadata is the check that closes that hole.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
GUARD = HERE / "check_unsupported_callouts.py"
LIST = HERE / "unsupported-commands.json"
FIXTURES = REPO / "tests" / "unsupported-callouts"


def fixture_stem(page: str, command: str) -> str:
    """The fixture name a pair must have: day-2.mdx + kubenest health -> day-2--kubenest-health."""
    slug = re.sub(r"[^a-z0-9]+", "-", command.lower()).strip("-")
    return f"{pathlib.Path(page).stem}--{slug}"


def run_guard(content_dir: pathlib.Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(GUARD), "--content", str(content_dir)],
        capture_output=True, text=True,
    )


def main() -> int:
    entries = json.loads(LIST.read_text(encoding="utf-8"))["unsupported"]
    trip_dir = FIXTURES / "must-trip"
    pass_dir = FIXTURES / "must-pass"
    problems: list[str] = []

    # 1: the pair still describes the repository it names.
    for entry in entries:
        page = REPO / entry["page"]
        if not page.exists():
            problems.append(
                f"LIST IS STALE: {entry['page']} does not exist. Either the page moved "
                f"and the list needs its new path, or it was deleted and the pair goes."
            )
            continue
        if entry["command"] not in page.read_text(encoding="utf-8"):
            problems.append(
                f"LIST IS STALE: {entry['page']} no longer shows `{entry['command']}`, so its "
                "pair checks nothing. If the command was corrected to a real one, the pair is "
                "done and comes out; if it moved to another page, the pair follows it."
            )

    # 2 + 4: one fixture per pair, and no fixture without a pair.
    stems = {fixture_stem(e["page"], e["command"]) for e in entries}
    for stem in sorted(stems):
        if not (trip_dir / f"{stem}.mdx").exists():
            problems.append(
                f"NO FIXTURE for pair [{stem}]. Add tests/unsupported-callouts/must-trip/"
                f"{stem}.mdx showing that command OUTSIDE a callout, so the guard is proven "
                "to catch it."
            )
    for path in sorted(trip_dir.glob("*.mdx")):
        if path.stem not in stems:
            problems.append(
                f"FIXTURE FOR AN UNKNOWN PAIR [{path.name}]: no list entry maps to that name. "
                "Either the pair was removed and the fixture goes with it, or it was renamed."
            )

    # 3a: the guard must fail on must-trip, and name every fixture it failed on.
    tripped = run_guard(trip_dir)
    if tripped.returncode == 0:
        problems.append(
            "THE GUARD DID NOT FAIL on tests/unsupported-callouts/must-trip. Every page there "
            "shows a listed command outside a callout, so a clean result means the guard has "
            "stopped working -- which is the failure it cannot report about itself."
        )
    for stem in sorted(stems):
        if f"{stem}.mdx" not in tripped.stdout:
            problems.append(
                f"the guard did not report {stem}.mdx while scanning must-trip, so either its "
                "fixture is missing or its patterns no longer match that command."
            )

    # 3b: and it must not fire on must-pass, which is where a real page lives.
    passed = run_guard(pass_dir)
    if passed.returncode != 0:
        problems.append(
            "THE GUARD FIRED on tests/unsupported-callouts/must-pass, which is a listed command "
            "inside a proper callout plus commands outside the list:\n" + passed.stdout.strip()
        )

    if problems:
        print("UNSUPPORTED-CALLOUT GUARD SELF-TEST FAILED\n")
        for p in problems:
            print(f"  - {p}\n")
        return 1

    print(f"unsupported-callout guard self-test: clean ({len(entries)} pair(s) proven to trip, "
          "near-misses pass)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
