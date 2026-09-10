"""Report unpublished docs content that differs from the holding branch.

The report deliberately does not fail when it finds drift.  A holding branch is
valid for unreviewed work; the purpose is to make the difference visible so a
reviewed correction cannot quietly remain off the published branch.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent


def differing_content_paths(base: str, holding: str) -> list[str]:
    """Return the content paths that differ between two already-fetched refs."""
    git = shutil.which("git")
    if git is None:
        raise RuntimeError("git is required to report holding-branch content drift")
    result = subprocess.run(
        [git, "diff", "--name-only", base, holding, "--", "content/"],
        check=True,
        capture_output=True,
        text=True,
        timeout=10,
        cwd=REPOSITORY_ROOT,
    )
    return sorted(path for path in result.stdout.splitlines() if path)


def write_step_summary(lines: list[str]) -> None:
    """Mirror the report into GitHub Actions' summary when available."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with Path(summary_path).open("a", encoding="utf-8") as summary:
            summary.write("\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--holding", default="origin/docs/platform-public")
    args = parser.parse_args()

    paths = differing_content_paths(args.base, args.holding)
    heading = f"Docs holding-branch drift: {args.holding} vs {args.base}"
    if paths:
        lines = [heading, "Differing content/ files:", *[f"- {path}" for path in paths]]
        print("::notice title=Docs holding-branch content drift::" + ", ".join(paths))
    else:
        lines = [heading, "No differing content/ files."]
        print("::notice title=Docs holding-branch content drift::No differing content/ files")

    print("\n".join(lines))
    write_step_summary(["## " + heading, *lines[1:]])


if __name__ == "__main__":
    main()
