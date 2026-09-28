#!/usr/bin/env python3
"""Check the clauses a page MUST state, and the clauses it must NEVER state.

WHY THIS EXISTS (PLAN section 8, T4.10's acceptance; G0.7 landed the checker
that compares docs EXAMPLES to the CLI's command tree, and this is the same CI
step's second half: it compares a page's CLAIMS to what the product does).

The retired-claim guard catches a sentence someone already retired. It cannot
catch a page that simply never says the thing it has to say, and it cannot tell
"we do not claim consistency" from "we forgot to mention it". Three clauses on
backup-restore.mdx are of that shape:

  1. the page MUST state that Velero's resource archives hold workload Secrets
     in plaintext (plan 7.8). A page about a bucket that omits it teaches an
     operator to hand out `s3:GetObject` to a whole team;
  2. the page MUST NOT claim consistency for an uncoordinated file copy, which
     gives none (plan 7.5);
  3. the page MUST NOT claim a recovery-time guarantee: T4.8 and T4.9 record
     wall-clock times with their conditions and assert no budget (plan section
     10, "Numbers carry their conditions").

WHAT THIS DOES NOT CHECK. That the surrounding prose is right, that the numbers
are the runs' numbers, or that a claim's word list is complete. These are three
enumerated clauses with enumerated wordings, and a reviewer adds one when a new
clause of this shape appears. Like the other guards here, it fails CLOSED: a
page that cannot be read is a failure, never a skip.

WHAT IT PROVES ABOUT ITSELF. scripts/selftest_page_claims.py runs it over a
corpus of deliberately wrong pages and over near-miss pages that must pass, so a
broken pattern cannot print "clean" forever.

Usage:
    check_page_claims.py                       # the page the registry names
    check_page_claims.py --page path/to.mdx    # one page
    check_page_claims.py --page tests/page-claims/must-trip   # a corpus
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
REGISTRY = HERE / "page-claims.json"

# One parser for one convention: a page's prose is reduced to sentences the same
# way the retired-claim guard reduces it, so "what a sentence says" does not
# depend on which guard is asking.
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from check_retired_claims import sentences, strip_markup  # noqa: E402


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def matches(patterns: list[str], sentence: str) -> str | None:
    for pattern in patterns:
        if re.search(pattern, sentence, flags=re.I):
            return pattern
    return None


def check_page(reg: dict, label: str, text: str) -> tuple[list[str], int]:
    """(failures, clauses checked) for one page."""
    prose = strip_markup(text)
    body = sentences(prose)
    failures: list[str] = []
    claims = reg["claims"]

    for claim in claims:
        if claim["kind"] == "must_state":
            hit = next((s for s in body if matches(claim["patterns"], s)), None)
            if hit is None:
                failures.append(
                    f"{label}: MISSING CLAIM [{claim['id']}]\n"
                    f"    The page must state this, in one of the wordings here:\n"
                    f"      - " + "\n      - ".join(claim["patterns"]) + "\n"
                    f"    Why: {claim['because']}"
                )
        elif claim["kind"] == "must_not_state":
            for s in body:
                hit = matches(claim["patterns"], s)
                if hit:
                    failures.append(
                        f"{label}: FORBIDDEN CLAIM [{claim['id']}]\n"
                        f"    sentence: {s[:240]}\n"
                        f"    matched:  {hit}\n"
                        f"    Why: {claim['because']}"
                    )
                    break
        else:
            raise ValueError(f"{REGISTRY}: claim {claim['id']} has kind {claim['kind']!r}, "
                             "which is neither must_state nor must_not_state")

    return failures, len(claims)


def sources(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(path.rglob("*.mdx"))
    return []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", type=Path,
                    help="one MDX file, or a directory of them (default: the page the "
                         "registry names), checked against every clause in the registry")
    args = ap.parse_args()

    reg = load_registry()
    target = args.page or REPO / reg["page"]

    files = sources(target)
    if not files:
        print("PAGE-CLAIM GUARD FAILED\n")
        print(f"  - {target}: cannot be read; the guard would check nothing and report clean. "
              "Pass the page (or corpus directory) of MDX to check.")
        return 1

    failures: list[str] = []
    checked = 0
    for path in files:
        found, clauses = check_page(reg, str(path), path.read_text(encoding="utf-8"))
        failures += found
        checked += clauses

    if failures:
        print("PAGE-CLAIM GUARD FAILED\n")
        for failure in failures:
            print(failure + "\n")
        print(f"{len(failures)} problem(s). See scripts/page-claims.json.")
        return 1

    print(f"page-claim guard: clean ({checked} clause(s) checked over {len(files)} file(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
