#!/usr/bin/env python3
"""T7.5 docs promotion check against the CLI metadata of the release being cut.

Every page that mentions a runnable kubenest command needs a stated minimum in
the form "Minimum versions: CLI v2.1.0; bundle 1.2." A stale unsupported
callout around a command the metadata marks available refuses the release.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parent.parent
MINIMUM = re.compile(
    r"Minimum versions:\s*CLI\s+v?(\d+)\.(\d+)\.(\d+)\s*;\s*bundle\s+(\d+)\.(\d+)",
    re.I,
)
COMMAND = re.compile(r"\bkubenest\s+[a-z][a-z-]*(?:\s+[a-z][a-z-]*)?\b")
CALLOUT = re.compile(r"<Callout\b[^>]*>(.*?)</Callout>", re.S | re.I)
MARKER = "Not supported by the current release."
PROMOTED_COMMANDS = (
    "kubenest health",
    "kubenest node reboot",
    "kubenest backup restore",
)


class Refusal(Exception):
    pass


def version(value: str, parts: int) -> tuple[int, ...]:
    match = re.fullmatch(r"v?" + r"\.".join([r"(\d+)"] * parts), value)
    if match is None:
        raise Refusal(f"invalid promoted version: {value}")
    return tuple(int(piece) for piece in match.groups())


def scan(path: Path, available: list[str], cli: tuple[int, ...],
         bundle: tuple[int, ...]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    problems: list[str] = []
    minima = list(MINIMUM.finditer(text))
    if COMMAND.search(text) and not minima:
        problems.append(f"{path}: minimum CLI and bundle versions missing")
    for match in minima:
        required_cli = tuple(int(match.group(i)) for i in (1, 2, 3))
        required_bundle = tuple(int(match.group(i)) for i in (4, 5))
        if required_cli > cli or required_bundle > bundle:
            problems.append(f"{path}: minimum version exceeds promoted CLI or bundle")
    for callout in CALLOUT.finditer(text):
        body = callout.group(1)
        if MARKER not in body:
            continue
        for command in available:
            if re.search(r"(?<![\w-])" + re.escape(command) + r"(?![\w-])", body):
                line = text.count("\n", 0, callout.start()) + 1
                problems.append(f"{path}:{line}: stale unsupported callout for {command}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    parser.add_argument("--content", type=Path, default=ROOT / "content")
    parser.add_argument("--metadata", type=Path,
                        default=ROOT / "cli-metadata/command-metadata.json")
    parser.add_argument("--cli-version", default="v2.1.0")
    parser.add_argument("--bundle-version", default="1.2")
    parser.add_argument("root", nargs="?", type=Path, default=Path("."),
                        help="repository root for relative content and metadata paths")
    args = parser.parse_args()
    try:
        content = args.content if args.content.is_absolute() else args.root / args.content
        metadata_path = args.metadata if args.metadata.is_absolute() else args.root / args.metadata
        cli = version(args.cli_version, 3)
        bundle = version(args.bundle_version, 2)
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        commands = metadata.get("commands")
        if not isinstance(commands, list) or not commands:
            raise Refusal("CLI metadata has no command tree")
        available = {entry["path"] for entry in commands
                     if isinstance(entry, dict) and entry.get("available") is True
                     and isinstance(entry.get("path"), str)}
        missing = set(PROMOTED_COMMANDS) - available
        if missing:
            raise Refusal("promoted CLI metadata lacks released command(s): "
                          + ", ".join(sorted(missing)))
        paths = ([content] if content.is_file()
                 else sorted(content.rglob("*.mdx")))
        if not paths:
            raise Refusal("no MDX pages found")
        if args.dry_run:
            print(f"release docs dry-run: would check {len(paths)} page(s) against "
                  f"CLI {args.cli_version}, bundle {args.bundle_version}")
            return 0
        problems = [problem for path in paths
                    for problem in scan(path, PROMOTED_COMMANDS, cli, bundle)]
        if problems:
            for problem in problems:
                print(problem, file=sys.stderr)
            print(f"release docs check refused: {len(problems)} problem(s)", file=sys.stderr)
            return 1
        print(f"release docs check: {len(paths)} page(s) valid for "
              f"CLI {args.cli_version}, bundle {args.bundle_version}")
        return 0
    except (OSError, ValueError, Refusal) as exc:
        print(f"release docs check refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
