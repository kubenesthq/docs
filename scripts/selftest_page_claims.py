#!/usr/bin/env python3
"""Prove the page-claim guard fires on its fixtures, and does not over-fire.

WHY THIS EXISTS, the same reason as the other self-tests here: the guard's
failure mode is entirely in its GREEN path. A broken regex, a renamed registry
key, a claim whose kind is misspelled so nothing is checked -- any of these
makes it print "page-claim guard: clean" and exit 0 forever, and nothing
downstream notices, because a red result gets investigated and a green one does
not.

WHAT THIS ASSERTS
  1. EVERY clause in the registry has a `must-trip` fixture named after it, and
     the guard names that clause when it runs over the corpus, so the registry
     cannot grow past its own evidence.
  2. The `must-pass` fixtures -- a page that states what it must and states none
     of the forbidden claims -- do NOT trip it. Over-firing blocks a publish and
     trains people to ignore the gate.
  3. Every fixture maps to a real clause, so a fixture for a clause that was
     removed does not linger and quietly pass.
  4. THE REAL PAGE passes, with a non-zero number of clauses checked, so the
     guard is not vacuous on the page that ships.
  5. A MISSING page fails rather than printing clean: "cannot read the page" must
     never read as "no problems found".

WHAT THIS DOES NOT PROVE. That the word lists behind these three clauses are
complete, or that the page's prose is accurate. Both are review obligations;
this proves only that the guard can fail.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
GUARD = HERE / "check_page_claims.py"
REGISTRY = HERE / "page-claims.json"
FIXTURES = REPO / "tests" / "page-claims"


def run(target: pathlib.Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(GUARD), "--page", str(target)],
        capture_output=True, text=True,
    )


def main() -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    ids = {claim["id"] for claim in registry["claims"]}
    trip_dir = FIXTURES / "must-trip"
    pass_dir = FIXTURES / "must-pass"
    problems: list[str] = []

    fixture_ids = {p.stem for p in trip_dir.glob("*.mdx")}
    for missing in sorted(ids - fixture_ids):
        problems.append(
            f"NO FIXTURE for clause [{missing}]. Add tests/page-claims/must-trip/"
            f"{missing}.mdx -- a page that violates exactly that clause -- so the "
            "guard is proven to catch it."
        )
    for stale in sorted(fixture_ids - ids):
        problems.append(
            f"FIXTURE FOR AN UNKNOWN CLAUSE [{stale}]: no registry entry has that id. "
            "Either the clause was removed and the fixture goes with it, or the id was "
            "renamed."
        )

    # 1: the guard must fail on the corpus and name every clause.
    tripped = run(trip_dir)
    if tripped.returncode == 0:
        problems.append(
            "THE GUARD DID NOT FAIL on tests/page-claims/must-trip. Every page there "
            "violates a clause, so a clean result means the guard has stopped working."
        )
    named = set(re.findall(r"\[([a-z0-9-]+)\]", tripped.stdout))
    for unnamed in sorted(ids - named):
        problems.append(
            f"the guard did not report clause [{unnamed}] over the must-trip corpus: "
            "either its fixture is missing or its pattern no longer matches prose that "
            "violates the clause."
        )

    # 2: and it must not fire on the near-miss corpus.
    passed = run(pass_dir)
    if passed.returncode != 0:
        problems.append(
            "THE GUARD FIRED on tests/page-claims/must-pass, which states the required "
            "clauses and none of the forbidden ones:\n" + passed.stdout.strip()
        )

    # 4: the page that ships, with something actually checked.
    real_page = REPO / registry["page"]
    real = run(real_page)
    if real.returncode != 0:
        problems.append(
            f"THE GUARD FIRED on {registry['page']}, the page this registry is about:\n"
            + real.stdout.strip()
        )
    elif (count := re.search(r"\((\d+) clause\(s\) checked", real.stdout)) is None:
        problems.append(
            f"the guard checked no clause on {registry['page']}, so it is vacuous on the "
            "page that ships:\n" + real.stdout.strip()
        )
    elif int(count.group(1)) != len(ids):
        problems.append(
            f"the guard checked {count.group(1)} clause(s) on {registry['page']}, want "
            f"{len(ids)}: the registry and the run disagree about what is being checked."
        )

    # 5: unreadable fails closed.
    absent = run(REPO / "content" / "does-not-exist.mdx")
    if absent.returncode == 0 or "cannot be read" not in absent.stdout:
        problems.append(
            "a page path that does not exist did not fail the guard with the reason, so a "
            "missing page is being read as \"no problems found\":\n" + absent.stdout.strip()
        )

    if problems:
        print("PAGE-CLAIM GUARD SELF-TEST FAILED\n")
        for problem in problems:
            print(f"  - {problem}\n")
        return 1

    print(f"page-claim guard self-test: clean ({len(ids)} clause(s) proven to fire, "
          "near-misses pass, the real page checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
