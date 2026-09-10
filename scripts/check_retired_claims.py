#!/usr/bin/env python3
"""Fail when a RETIRED claim reappears in the docs, in any wording.

WHY THIS EXISTS (kn-mxxu). On 2026-08-22 a pre-publication truth pass retired the
claim "a compromised backend cannot issue arbitrary kubectl commands" from the
homepage and wrote a warning saying so. The identical claim, worded "cannot issue
arbitrary Kubernetes API calls", sat in that same commit's own diff as untouched
context on the architecture page. It stayed live for three more months and was
found by accident.

The fix hunted a PHRASE. The claim had a SYNONYM. So this guard matches claims by
their semantic parts -- a subject that is us, a negation, and a capability noun --
rather than by remembered sentences. A literal-string check would reproduce the
exact bug it is meant to prevent.

TWO WAYS A REGISTRY LIKE THIS GOES STALE, and what is done about each:

  1. NEW PROSE THAT NOBODY CLASSIFIES. This is what killed the 2026-08-22 fix.
     Handled by failing CLOSED: any sentence matching the tripwire that is not
     accounted for in the registry fails the build. The list cannot silently miss
     new wording, because new wording that trips the tripwire stops the publish
     until a human classifies it.

  2. AN ALLOWED CLAIM WHOSE CODE JUSTIFICATION STOPS BEING TRUE. A sentence that
     was accurate when written stays in the registry marked fine forever.
     Handled by `evidence`: each allowed claim names a symbol that must be ABSENT
     or PRESENT in a sibling repo. Those run in ci.yml (see --evidence-root),
     never in the deploy workflow, because publishing must not depend on another
     repository -- that lesson is already written into deploy.yml.

Usage:
    check_retired_claims.py --content content/            # pre-publish, in-repo only
    check_retired_claims.py --served https://docs...      # post-publish, served HTML
    check_retired_claims.py --content content/ --evidence-root ../kubenest-backend
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REGISTRY = HERE / "retired-claims.json"


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def sentences(text: str) -> list[str]:
    """Split loosely. Over-splitting is safe here; under-splitting is not, because
    a claim spanning two sentences would evade a per-sentence match."""
    text = re.sub(r"\s+", " ", text)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def strip_markup(text: str) -> str:
    """Rendered HTML and MDX both reduce to prose for matching purposes."""
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)          # fenced code
    # Navigation is not page prose. Left in, a sidebar's headings concatenate into
    # one pseudo-sentence and match across items that are nowhere near each other.
    text = re.sub(r"<nav.*?</nav>", " ", text, flags=re.S | re.I)
    # Block boundaries become sentence boundaries, for the same reason: without
    # this, two adjacent headings read as one sentence to the splitter.
    text = re.sub(r"</(h[1-6]|p|li|nav|div|section|td|th|tr|blockquote)>", ". ",
                  text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)                        # remaining tags
    text = text.replace("&#x27;", "'").replace("&amp;", "&")
    text = text.replace("’", "'").replace("—", "--")
    return text


def matches(patterns: list[str], sentence: str) -> str | None:
    for p in patterns:
        if re.search(p, sentence, flags=re.I):
            return p
    return None


def tripwire_hit(reg: dict, sentence: str) -> bool:
    """A sentence is a candidate security claim when it carries all three parts:
    a subject that is us, a negation, and a capability noun. Claims about the
    CUSTOMER's obligations, or about other products, are not ours to police.

    out_of_family is consulted HERE ONLY. Retired claims are matched before this
    function is ever called, so an exclusion can quieten the tripwire but can
    never suppress a claim already known to be false."""
    for ex in reg.get("out_of_family", {}).get("patterns", []):
        if re.search(ex["pattern"], sentence, flags=re.I):
            return False
    t = reg["tripwire"]
    return (
        re.search(t["subject"], sentence, flags=re.I) is not None
        and re.search(t["negation"], sentence, flags=re.I) is not None
        and re.search(t["capability"], sentence, flags=re.I) is not None
    )


def check_text(reg: dict, label: str, text: str) -> list[str]:
    failures: list[str] = []
    prose = strip_markup(text)
    for s in sentences(prose):
        for claim in reg["retired"]:
            hit = matches(claim["patterns"], s)
            if hit:
                failures.append(
                    f"{label}: RETIRED CLAIM REAPPEARED [{claim['id']}]\n"
                    f"    sentence: {s[:240]}\n"
                    f"    matched:  {hit}\n"
                    f"    retired:  {claim['retired_by']} -- {claim['because']}"
                )
                break
        else:
            if tripwire_hit(reg, s):
                if not any(matches(a["patterns"], s) for a in reg["allowed"]):
                    failures.append(
                        f"{label}: UNCLASSIFIED SECURITY CLAIM\n"
                        f"    sentence: {s[:240]}\n"
                        f"    This asserts something about what KubeNest does NOT do with your\n"
                        f"    cluster or its credentials. Add it to scripts/retired-claims.json\n"
                        f"    as `allowed` (with `evidence` naming the code that makes it true)\n"
                        f"    or as `retired` (if it is false and must never come back)."
                    )
    return failures


def check_evidence(reg: dict, root: Path) -> list[str]:
    """Each allowed claim names code that must (not) exist for it to stay true."""
    failures: list[str] = []
    for a in reg["allowed"]:
        for ev in a.get("evidence", []):
            target = root / ev["file"] if ev.get("file") else root
            if ev.get("file") and not target.exists():
                failures.append(f"EVIDENCE PATH MISSING for [{a['id']}]: {target}")
                continue
            hay = ""
            if target.is_dir():
                for p in target.rglob("*.py"):
                    hay += p.read_text(encoding="utf-8", errors="ignore")
            else:
                hay = target.read_text(encoding="utf-8", errors="ignore")
            present = re.search(ev["symbol"], hay) is not None
            if ev["must"] == "absent" and present:
                failures.append(
                    f"EVIDENCE BROKEN for [{a['id']}]: {ev['symbol']} is PRESENT in {target}\n"
                    f"    The docs say: {a['says']}\n"
                    f"    That claim is no longer supported by the code. Fix one or the other."
                )
            if ev["must"] == "present" and not present:
                failures.append(
                    f"EVIDENCE BROKEN for [{a['id']}]: {ev['symbol']} is ABSENT from {target}\n"
                    f"    The docs say: {a['says']}"
                )
    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--content", type=Path, help="docs content directory (MDX)")
    ap.add_argument("--served", nargs="*", default=[], help="published URLs to fetch and check")
    ap.add_argument("--evidence-root", type=Path, help="sibling repo root for evidence checks")
    args = ap.parse_args()

    reg = load_registry()
    failures: list[str] = []

    if args.content:
        for p in sorted(args.content.rglob("*.mdx")):
            failures += check_text(reg, str(p), p.read_text(encoding="utf-8"))

    for url in args.served:
        import urllib.request

        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                body = r.read().decode("utf-8", errors="ignore")
        except Exception as e:                                    # noqa: BLE001
            failures.append(f"{url}: COULD NOT FETCH ({e}). Published is not merged; "
                            f"a check that cannot run must say so rather than pass.")
            continue
        failures += check_text(reg, url, body)

    if args.evidence_root:
        failures += check_evidence(reg, args.evidence_root)

    if failures:
        print("RETIRED-CLAIM GUARD FAILED\n")
        for f in failures:
            print(f + "\n")
        print(f"{len(failures)} problem(s). See scripts/retired-claims.json and kn-mxxu.")
        return 1

    scope = []
    if args.content:
        scope.append(f"content={args.content}")
    if args.served:
        scope.append(f"served={len(args.served)} url(s)")
    if args.evidence_root:
        scope.append(f"evidence={args.evidence_root}")
    print(f"retired-claim guard: clean ({', '.join(scope) or 'nothing checked'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
