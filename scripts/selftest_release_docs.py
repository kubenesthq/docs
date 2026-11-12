#!/usr/bin/env python3
"""T7.5: the release docs guard must distinguish stale and still-needed callouts."""
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "retired-claims" / "release"
GUARD = ROOT / "scripts" / "check_release_docs.py"
METADATA = FIXTURES / "command-metadata.json"


def run(name: str, mode: str, *, root: bool = False) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(GUARD), mode, "--content", str(FIXTURES / name),
               "--metadata", str(METADATA), "--cli-version", "v2.1.0",
               "--bundle-version", "1.2"]
    if root:
        command.append(".")
    return subprocess.run(
        command,
        text=True, capture_output=True, check=False,
    )


def main() -> int:
    passing = run("must-pass.mdx", "--check", root=True)
    stale = run("must-trip-stale-callout.mdx", "--check")
    too_new = run("must-trip-future-minimum.mdx", "--check")
    preview = run("must-pass.mdx", "--dry-run")
    if (passing.returncode != 0 or stale.returncode == 0 or
            too_new.returncode == 0 or preview.returncode != 0):
        print("release docs self-test FAILED")
        for label, result in (("pass", passing), ("stale", stale),
                              ("future", too_new), ("dry-run", preview)):
            print(f"{label}: exit={result.returncode} {result.stdout}{result.stderr}")
        return 1
    print("release docs self-test: stale callout and future minimum refused; still-needed callout passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
