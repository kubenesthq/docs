#!/usr/bin/env python3
"""Fail when a page presents a command the released CLI does not have as if it worked.

WHAT THIS GUARDS. A reader who types the first command a page gives them and gets
"command not found" has been told something false by us, and it does not matter
that the page is otherwise accurate. scripts/unsupported-commands.json lists the
commands we know are not in the command tree; every occurrence of one of them
under the scanned content must sit inside a callout whose first sentence is
exactly "Not supported by the current release." -- the one exception README.md's
"The docs are the specification" section grants, and the marker G0.7's CLI
metadata will skip on.

WHAT THIS DOES NOT CHECK, because the list is an enumeration written by hand:
a command that is missing from the CLI and ALSO missing from the list. G0.7
compares the whole command tree to the pages and is the check that closes that;
this one closes the smaller, cheaper hole -- a documented command losing its
callout, or a new occurrence appearing outside one.

WHY A CALLOUT AND NOT A DELETION. The pages describe how the product is meant to
work, and the app layer is frozen by D1 rather than unfinished. The honest
rendering is the page plus one standardized sentence, not a page with the
paragraph knocked out.

Usage:
    check_unsupported_callouts.py                        # the real content/
    check_unsupported_callouts.py --content tests/...     # a fixture corpus
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
LIST = HERE / "unsupported-commands.json"
MARKER = "Not supported by the current release."
# The release that removes the callout has to be named, per PLAN section 7.12:
# a callout with no release on it is a note that never expires.
RELEASE = re.compile(r"\bBundle\s+\d+\.\d+\b")
CALLOUT = re.compile(r"<Callout\b[^>]*>(.*?)</Callout>", re.S)


def load_commands() -> list[str]:
    entries = json.loads(LIST.read_text(encoding="utf-8"))["unsupported"]
    return [e["command"] for e in entries]


def callouts(text: str) -> list[tuple[int, int, str]]:
    """Every <Callout> as (start, end, body). Not nested, and not meant to be."""
    return [(m.start(), m.end(), m.group(1)) for m in CALLOUT.finditer(text)]


def enclosing_problem(body: str) -> str | None:
    """Why this callout does not carry the marker, or None when it does."""
    if not re.match(r"\*{0,2}\s*" + re.escape(MARKER), body.strip()):
        return ("it does not open with exactly "
                f"\"{MARKER}\" as its first sentence")
    if not RELEASE.search(body):
        return ("it does not name the release that removes it "
                "(e.g. \"Bundle 1.2, on promotion\")")
    return None


def check_text(label: str, text: str, commands: list[str]) -> tuple[list[str], int]:
    """Return (failures, occurrences found inside a proper callout)."""
    spans = callouts(text)
    failures: list[str] = []
    covered = 0
    for command in commands:
        for m in re.finditer(re.escape(command), text):
            line = text.count("\n", 0, m.start()) + 1
            for start, end, body in spans:
                if start <= m.start() < end:
                    problem = enclosing_problem(body)
                    if problem is None:
                        covered += 1
                    else:
                        failures.append(
                            f"{label}:{line}: `{command}` is inside a callout, but {problem}."
                        )
                    break
            else:
                failures.append(
                    f"{label}:{line}: `{command}` is presented with no callout. Wrap it in\n"
                    f"    <Callout type=\"warning\">\n"
                    f"    {MARKER} ... arrives with Bundle 1.2, on promotion.\n"
                    f"    </Callout>\n"
                    f"    See scripts/unsupported-commands.json and README.md, section\n"
                    f"    \"The docs are the specification\"."
                )
    return failures, covered


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--content", type=Path, default=REPO / "content",
                    help="directory of MDX to scan (default: content/)")
    args = ap.parse_args()

    commands = load_commands()
    failures: list[str] = []
    covered = 0
    scanned = 0
    for path in sorted(args.content.rglob("*.mdx")):
        scanned += 1
        found, ok = check_text(str(path), path.read_text(encoding="utf-8"), commands)
        failures += found
        covered += ok

    if failures:
        print("UNSUPPORTED-COMMAND GUARD FAILED\n")
        for f in failures:
            print(f + "\n")
        print(f"{len(failures)} problem(s). A command the released CLI does not have is on the")
        print("page without the one callout that says so. See scripts/unsupported-commands.json.")
        return 1

    if covered == 0:
        print("unsupported-command guard: nothing checked. No listed command occurs under")
        print(f"{args.content}, which means the list or the pages moved -- a guard that checks")
        print("nothing passes forever. scripts/selftest_unsupported_callouts.py fails on it.")
        return 0

    print(f"unsupported-command guard: clean ({covered} occurrence(s) of {len(commands)} "
          f"command(s) inside a callout, {scanned} file(s) scanned)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
