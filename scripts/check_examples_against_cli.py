#!/usr/bin/env python3
"""Fail when a docs example runs a command, subcommand or flag the CLI does not have.

WHAT THIS GUARDS. Six pages told readers to run `kubenest health`, `kubenest
backup restore`, `kubenest node reboot` and friends. Four times a re-read of the
pages missed one, because the check was a person reading fourteen pages against
a binary's command tree they were remembering. The only durable form of that
check asks the binary. Cobra holds the command tree, `kubenest-cli`'s
`cmd/gen-command-metadata` emits it as JSON, and this compares the pages to that
document: the longest matching registered command path, whether it is available
or a registered stub, and every flag the example passes.

WHERE THE METADATA COMES FROM. `--metadata <file>`; CI decides the source.
`cli-contract.json` names which CLI a run is against (PLAN section 7.12), and the
committed `cli-metadata/command-metadata.json` is what the workflows read, so
publishing depends on this repository only and never on a download. A missing,
unreadable or rootless metadata file is a FAILURE, never a skip: a guard that
quietly checks nothing is the failure mode this file exists to prevent. A
`--content` path that does not exist fails for the same reason.

THE ONE EXCEPTION. An example inside a `<Callout>` carrying the exact marker
`Not supported by the current release.` is skipped -- the dated exception
README.md's "The docs are the specification" section grants, written by G0.6.
The callout parser and its marker come from
scripts/check_unsupported_callouts.py rather than being written a second time.
A marker callout that wraps code is the exception for that example; a marker
callout that wraps no code is the page-level exception for a whole frozen family
(`deploying.mdx`'s "Almost nothing on this page is in the command tree"),
which is one callout over a group of related commands, not one per occurrence.

THE ALLOWLIST is `scripts/cli-examples-allowlist.json`: `{page, command,
owning_bead}` entries for an occurrence that is known and deferred. An
allowlisted occurrence is REPORTED and not fatal, and the checker FAILS when an
allowlisted page no longer shows its command, so an entry cannot outlive the
example it was written for. Empty is the intended state.

WHAT IT DOES NOT CHECK. That a flag behaves as the page says, or that a command
prints what the page's sample output shows. It proves names: the longest path and
the flag set, nothing about behaviour. It does not read prose -- a command named
mid-sentence is not a runnable example -- except for a line that IS a bare
invocation, which is what an example looks like when it loses its fence. It does
not prove the metadata is the RELEASED binary's tree; that is `cli-contract.json`
and a review obligation when the site's target release moves.

Usage:
    check_examples_against_cli.py --metadata cli-metadata/command-metadata.json
    check_examples_against_cli.py --metadata tests/cli-examples/command-metadata.json \\
                                  --content tests/cli-examples
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent

# One parser for one convention: the callout detection is shared with the
# unsupported-command guard, not reimplemented here (PLAN section 8, G0.7).
# The import must not leave a __pycache__ directory behind: this runs from a
# shared worktree and from CI, and an untracked directory appearing after a
# check is noise nobody asked for.
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))
from check_unsupported_callouts import MARKER, callouts  # noqa: E402

FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,})", re.M)
ENV_PREFIX = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
PROMPT = re.compile(r"^[$\u276f>][ \t]+")
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)
FLAG = re.compile(r"^--?[A-Za-z][A-Za-z0-9-]*$")
# An example may elide the rest of its command line: `kubenest platform install ...`.
# That is a placeholder, not a subcommand the CLI is missing.
ELISION = {"...", "\u2026"}
ALLOWLIST = HERE / "cli-examples-allowlist.json"

# A line outside a fence is read as an invocation only when it IS one: a prose
# sentence that begins with the product's name ("kubenest does not manage
# ResourceQuota") is not a command, and reading it as one would fail the deploy
# for a sentence. Command lines have a verb, at most a subcommand, and flags.
PROSE_WORDS = 2


def blank_comments(text: str) -> str:
    """Replace HTML comments with spaces, keeping every newline and every offset."""
    return HTML_COMMENT.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


# A section heading, not the page title: `<h2>` and deeper.
HEADING = re.compile(r"^#{2,}[ \t]+\S", re.M)


def exception_spans(text: str) -> tuple[list[tuple[int, int]], bool]:
    """The skipping exception: (enclosing spans, is the whole page excepted).

    Only callouts carrying the G0.6 marker count. A marker callout with an
    example in it is the exception for that example. A marker callout with no
    code in it warns about a family rather than about one occurrence, and the
    one that opens a page -- before its first section heading -- is the
    page-level exception the app-layer pages are written with ("Almost nothing
    on this page is in the command tree"). One further down warns about ITS
    section and excepts nothing here, so a page cannot be blanketed by a note
    written for a paragraph.
    """
    spans: list[tuple[int, int]] = []
    page_level = False
    first_heading = HEADING.search(text)
    for start, end, body in callouts(text):
        if MARKER not in body:
            continue
        if FENCE.search(body):
            spans.append((start, end))
        elif first_heading is None or start < first_heading.start():
            page_level = True
    return spans, page_level


class Cli:
    """The CLI's command tree, exactly as the metadata generator emitted it."""

    def __init__(self, doc: dict, label: str) -> None:
        self.label = label
        self.version = str(doc.get("cli_version") or "unknown")
        commands = doc.get("commands")
        if not isinstance(commands, list) or not commands:
            raise ValueError(f"{label}: no `commands` array in the metadata")
        self.commands = {c["path"]: c for c in commands}
        if "kubenest" not in self.commands:
            raise ValueError(f"{label}: the metadata has no `kubenest` root command")

    def resolve(self, tokens: list[str]) -> tuple[str, list[str]]:
        """The longest registered path the line starts with, and the rest."""
        path = "kubenest"
        rest = list(tokens[1:])
        while rest and not rest[0].startswith("-") and (path + " " + rest[0]) in self.commands:
            path = path + " " + rest.pop(0)
        return path, rest

    def offered(self, path: str) -> str:
        prefix = path + " "
        names = {p[len(prefix):].split(" ")[0] for p in self.commands if p.startswith(prefix)}
        return ", ".join(sorted(names)) if names else "nothing further"

    def flag_names(self, path: str) -> str:
        return ", ".join(f["name"] for f in self.commands[path]["flags"])


def load_cli(path: Path) -> Cli:
    """Read the metadata, or raise with the reason. Unreadable is a failure."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as err:
        raise ValueError(f"{path}: cannot be read ({err.strerror}); the guard cannot check "
                         "anything without the CLI's command metadata") from err
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError as err:
        raise ValueError(f"{path}: is not JSON ({err}); expected the output of "
                         "kubenest-cli/cmd/gen-command-metadata") from err
    return Cli(doc, str(path))


def strip_comment(line: str) -> str:
    """Cut a trailing `# comment`, and nothing inside a quoted value.

    A `#` inside quotes is part of a value (`--bucket "kubenest #1"`), and
    cutting there would leave an unbalanced quote, which makes the line
    unparseable and therefore silently unchecked -- a false negative in a guard
    whose whole job is not to miss an example.
    """
    quote = ""
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = ""
            continue
        if ch in "\"'":
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1].isspace()):
            return line[:i].rstrip()
    return line


def invocation_of(line: str) -> list[str] | None:
    """Tokens of a `kubenest ...` invocation on this line, or None."""
    s = PROMPT.sub("", line.strip())
    s = strip_comment(s)
    if not s:
        return None
    try:
        tokens = shlex.split(s, comments=False, posix=True)
    except ValueError:
        return None
    while tokens and ENV_PREFIX.match(tokens[0]):
        tokens.pop(0)
    if tokens and tokens[0] == "sudo":
        tokens.pop(0)
    if not tokens or tokens[0] != "kubenest":
        return None
    return tokens


def fenced_blocks(lines: list[str]) -> list[tuple[int, int]]:
    """(first, last) line indices of every fenced block, openers included."""
    blocks = []
    i = 0
    while i < len(lines):
        opener = FENCE.match(lines[i])
        if not opener:
            i += 1
            continue
        fence = opener.group(1)
        j = i + 1
        while j < len(lines):
            closer = FENCE.match(lines[j])
            if closer and closer.group(1)[0] == fence[0] and len(closer.group(1)) >= len(fence):
                break
            j += 1
        blocks.append((i, min(j, len(lines) - 1)))
        i = j + 1
    return blocks


def invocation_problems(tokens: list[str], cli: Cli) -> list[str]:
    """Everything wrong with one invocation, or [] when the CLI has all of it."""
    path, rest = cli.resolve(tokens)
    entry = cli.commands[path]
    typed = path.split(" ")[1:]

    if rest and not rest[0].startswith("-") and rest[0] not in ELISION:
        what = command_text(tokens)
        return [
            f"`{what}` is not a command in this CLI.\n"
            f"    The deepest path the CLI knows here is `{path}`, and `{path}` offers: "
            f"{cli.offered(path)}."
        ]

    if not entry["available"]:
        what = "kubenest " + " ".join(typed)
        return [
            f"`{what}` is registered but available: false in this CLI.\n"
            f"    The CLI says: {entry['reason']}"
        ]

    problems = []
    known = {f["name"] for f in entry["flags"]}
    short = {f["shorthand"] for f in entry["flags"] if f["shorthand"]}
    for token in rest:
        name = token.split("=", 1)[0]
        if not FLAG.match(name):
            continue
        if name in known or (not name.startswith("--") and name[1:] in short):
            continue
        problems.append(
            f"`{name}` is not a flag of `{path}`.\n"
            f"    `{path}` takes: {cli.flag_names(path)}"
        )
    return problems


def command_text(tokens: list[str]) -> str:
    """The command words of an invocation, flags and their values dropped."""
    words = []
    for token in tokens:
        if token.startswith("-"):
            break
        words.append(token)
    return " ".join(words)


def scan(path: Path, cli: Cli, allow: list[dict]) -> tuple[list[str], list[str], int, int]:
    """(failures, allowlisted reports, invocations checked, invocations excepted)."""
    text = blank_comments(path.read_text(encoding="utf-8"))
    lines = text.split("\n")
    offsets, off = [], 0
    for line in lines:
        offsets.append(off)
        off += len(line) + 1

    spans, page_level = exception_spans(text)
    label = str(path)

    def excepted(index: int) -> bool:
        if page_level:
            return True
        return any(start <= offsets[index] < end for start, end in spans)

    def look(index: int, line: str) -> tuple[list[str], list[str], str]:
        """(failures, allowlisted reports, status) for one line.

        Status is "checked" for an invocation the guard judged, "excepted" for
        one the callout exception covered, and "empty" for a line that is not an
        invocation at all -- a guard that reports checking nothing must not be
        able to call that success.
        """
        tokens = invocation_of(line)
        if tokens is None:
            return [], [], "empty"
        if excepted(index):
            return [], [], "excepted"
        command = command_text(tokens)
        for entry in allow:
            if entry["page"] == label and (
                command == entry["command"] or command.startswith(entry["command"] + " ")
            ):
                return [], [
                    f"{label}:{index + 1}: `{command}` is on the allowlist "
                    f"(owning bead {entry['owning_bead']}), reported, not fatal."
                ], "checked"
        problems = invocation_problems(tokens, cli)
        return [f"{label}:{index + 1}: {p}" for p in problems], [], "checked"

    failures: list[str] = []
    reports: list[str] = []
    checked = excepted_count = 0

    blocks = fenced_blocks(lines)
    fenced = {i for start, end in blocks for i in range(start, end + 1)}
    for start, end in blocks:
        i = start + 1
        while i < end:
            line = lines[i]
            first = i
            # A backslash continuation is one invocation, reported at its first line.
            while line.rstrip().endswith("\\") and i + 1 < end:
                i += 1
                line = line.rstrip()[:-1] + " " + lines[i].strip()
            found, allowed, status = look(first, line)
            if status == "checked":
                checked += 1
                failures += found
                reports += allowed
            elif status == "excepted":
                excepted_count += 1
            i += 1

    for i, line in enumerate(lines):
        if i in fenced:
            continue
        tokens = invocation_of(line)
        # A sentence is not a command: only a line that is a bare invocation is.
        if tokens is None or len([t for t in tokens[1:] if not t.startswith("-")]) > PROSE_WORDS:
            continue
        found, allowed, status = look(i, line)
        if status == "checked":
            checked += 1
            failures += found
            reports += allowed
        elif status == "excepted":
            excepted_count += 1

    return failures, reports, checked, excepted_count


def load_allowlist(path: Path) -> list[dict]:
    if not path.exists():
        return []
    doc = json.loads(path.read_text(encoding="utf-8"))
    entries = doc.get("allow", [])
    for entry in entries:
        missing = {"page", "command", "owning_bead"} - set(entry)
        if missing:
            raise ValueError(f"{path}: entry {entry} is missing {sorted(missing)}")
    return entries


def allowlist_rot(allow: list[dict], content: Path) -> list[str]:
    """An entry whose example left the page is an entry outliving its reason."""
    problems = []
    for entry in allow:
        page = REPO / entry["page"]
        if not page.exists():
            problems.append(f"ALLOWLIST IS STALE: {entry['page']} does not exist, so the entry "
                            f"for `{entry['command']}` checks nothing. Remove it, or point it at "
                            "the page the example moved to.")
            continue
        if entry["command"] not in page.read_text(encoding="utf-8"):
            problems.append(f"ALLOWLIST IS STALE: {entry['page']} no longer shows "
                            f"`{entry['command']}`, so the entry outlives the example it was "
                            "written for. Remove it.")
    return problems


def sources(content: Path) -> list[Path]:
    if content.is_file():
        return [content]
    return sorted(content.rglob("*.mdx"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metadata", required=True, type=Path,
                    help="the CLI command metadata to check against (required; the source is "
                         "CI's decision, see cli-contract.json)")
    ap.add_argument("--content", type=Path, default=REPO / "content",
                    help="directory (or single file) of MDX to scan (default: content/)")
    ap.add_argument("--allowlist", type=Path, default=ALLOWLIST,
                    help=f"deferred occurrences (default: {ALLOWLIST.name})")
    args = ap.parse_args()

    problems: list[str] = []
    try:
        cli = load_cli(args.metadata)
    except ValueError as err:
        print("CLI-EXAMPLE GUARD FAILED\n")
        print(f"  - {err}")
        return 1

    if not args.content.exists():
        print("CLI-EXAMPLE GUARD FAILED\n")
        print(f"  - {args.content}: cannot be read; the guard would check nothing and report "
              "clean. Pass the directory of MDX to scan.")
        return 1

    try:
        allow = load_allowlist(args.allowlist)
    except (OSError, json.JSONDecodeError, ValueError) as err:
        print("CLI-EXAMPLE GUARD FAILED\n")
        print(f"  - {args.allowlist}: {err}")
        return 1

    failures: list[str] = []
    reports: list[str] = []
    checked = excepted_count = 0
    scanned = 0
    for path in sources(args.content):
        scanned += 1
        found, allowed, n, exc = scan(path, cli, allow)
        failures += found
        reports += allowed
        checked += n
        excepted_count += exc

    if reports:
        print(f"Allowlisted, reported, not fatal ({len(reports)}):")
        for r in reports:
            print(f"  - {r}")
        print()

    problems += allowlist_rot(allow, args.content)

    if failures:
        print("CLI-EXAMPLE GUARD FAILED\n")
        for failure in failures:
            print(failure + "\n")
        problems.append(
            f"{len(failures)} example(s) run something the CLI at {cli.version} does not have. "
            "Either the page is wrong, or the command is real and this check is reading stale "
            "metadata (see cli-contract.json). An occurrence that is genuinely deferred goes in "
            f"{args.allowlist.name} with the bead that owns it."
        )
    if problems:
        for p in problems:
            print(f"  - {p}")
        return 1

    if checked == 0:
        print("cli-example guard: nothing checked. No runnable example under "
              f"{args.content} runs a `kubenest` command, which means the pages or the metadata "
              "moved -- a guard that checks nothing passes forever, and "
              "scripts/selftest_cli_examples.py fails on it.")
        return 0

    print(f"cli-example guard: clean ({checked} invocation(s) checked against the CLI at "
          f"{cli.version}, {excepted_count} excepted by a \"{MARKER}\" callout, "
          f"{len(allow)} allowlist entry(ies), {scanned} file(s) scanned)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
