#!/usr/bin/env python3
"""Prove the CLI-example guard fires on its fixtures, and does not over-fire.

WHY THIS EXISTS, and it is the same reason as scripts/selftest_retired_claims.py
and scripts/selftest_unsupported_callouts.py: this guard protects the publish,
and its failure mode lives entirely in its GREEN path. A metadata file that is
absent, mis-shaped or from the wrong release; a callout parser that stops finding
the marker; a fixture whose command quietly appears in the CLI -- any of these
makes it print "clean" and exit 0 forever, and nothing downstream notices,
because A RED RESULT GETS INVESTIGATED AND A GREEN ONE DOES NOT.

WHAT THIS ASSERTS
  1. EVERY must-trip fixture trips, and is named as `file:line` with the reason
     the metadata gives. A fixture that passes unmodified proves the corpus is
     decorative.
  2. EVERY must-pass fixture passes, including one inside a "Not supported by
     the current release." callout, one under a page-level marker callout, and
     one using flags the CLI does have. Over-firing blocks a publish and trains
     people to bypass the gate.
  3. THE AVAILABILITY BIT IS WHAT GATES THE STUB, not the callout: with
     `kubenest backup restore` flipped to available: true in a copy of the
     metadata, the same example that fails now passes.
  4. A MISSING OR BROKEN metadata file FAILS the guard rather than printing
     clean: a command the metadata does not carry still trips, a metadata
     document with no `kubenest` root fails, and a path that does not exist
     fails. "Cannot read the CLI's command tree" must never read as "no
     problems found".
  5. THE ALLOWLIST IS A DEFERRAL, NOT A HOLE: a matching entry is reported and
     not fatal, and an entry whose page no longer shows its command fails.
  6. THE REAL PAGES pass against the committed metadata with a non-zero number
     of invocations checked, so the guard is not vacuous on the corpus that
     ships. A defect on a real page fails HERE, which is why the deploy workflow
     can gate the publish on this file.

WHAT THIS DOES NOT PROVE. That the committed metadata is the RELEASED binary's
tree (that is cli-contract.json, and moving the target release is a review
obligation), or that a checked flag behaves as the page says. It proves the
guard still fires, on fixtures written by the person who wrote the guard -- an
enumerated set of the shapes they thought of, and nothing more.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
GUARD = "scripts/check_examples_against_cli.py"
FIXTURES = Path("tests/cli-examples")
FIXTURE_METADATA = FIXTURES / "command-metadata.json"
REAL_METADATA = Path("cli-metadata/command-metadata.json")
ALLOWLIST = Path("scripts/cli-examples-allowlist.json")
TRIP_DIR = FIXTURES / "must-trip"
PASS_DIR = FIXTURES / "must-pass"

# What each must-trip fixture must be told, by name: the guard naming the file
# and line is not enough if it names the wrong reason.
TRIPS = {
    "health-not-a-command": "is not a command in this CLI",
    "prose-invocation": "is not a command in this CLI",
    "exception-is-scoped": "`kubenest node reboot` is not a command in this CLI",
    "backup-restore-stub": "available: false",
    "unknown-flag": "`--servver` is not a flag of",
    "quoted-comment-character": "`--prefxi` is not a flag of",
    "ha-misspelled": "`--haa` is not a flag of",
    "flag-from-another-command": "`--to` is not a flag of",
}


def run(metadata: Path | str, content: Path | str, allowlist: Path | str | None = None):
    args = [sys.executable, GUARD, "--metadata", str(metadata), "--content", str(content)]
    if allowlist is not None:
        args += ["--allowlist", str(allowlist)]
    return subprocess.run(args, cwd=REPO, capture_output=True, text=True)


def failures_by_file(out: str) -> dict[str, list[int]]:
    """{page: [line, ...]} from the guard's output blocks."""
    found: dict[str, list[int]] = {}
    for block in out.split("\n\n"):
        m = re.match(r"(\S+\.mdx):(\d+): ", block)
        if m:
            found.setdefault(m.group(1), []).append(int(m.group(2)))
    return found


def checked_count(out: str) -> int | None:
    m = re.search(r"(\d+) invocation\(s\) checked", out)
    return int(m.group(1)) if m else None


def temp_json(doc: dict, name: str) -> Path:
    path = Path(tempfile.mkdtemp(prefix="cli-examples-")) / name
    path.write_text(json.dumps(doc), encoding="utf-8")
    return path


def main() -> int:
    problems: list[str] = []

    # 1: must-trip trips, names file:line, and names the reason.
    tripped = run(FIXTURE_METADATA, TRIP_DIR)
    if tripped.returncode == 0:
        problems.append(
            "THE GUARD DID NOT FAIL on tests/cli-examples/must-trip. Every page there runs "
            "something the fixture metadata says the CLI does not have, so a clean result means "
            "the guard has stopped working -- exactly the failure it cannot report about itself."
        )
    named = failures_by_file(tripped.stdout)
    for stem, needle in sorted(TRIPS.items()):
        page = f"{TRIP_DIR}/{stem}.mdx"
        if page not in named:
            problems.append(
                f"the guard did not report {page} while scanning must-trip: either its fixture is "
                "missing or it no longer trips."
            )
            continue
        if needle not in tripped.stdout:
            problems.append(
                f"the guard failed on {page} but did not say {needle!r}, so it is reporting some "
                "other problem than the one the fixture is about."
            )
    # The exception is scoped to its callout: the example inside the callout in
    # `exception-is-scoped.mdx` must be silent while the one after it fails.
    scoped = f"{TRIP_DIR}/exception-is-scoped.mdx"
    if len(named.get(scoped, [])) != 1:
        problems.append(
            f"the guard reported {len(named.get(scoped, []))} failure(s) on {scoped}, want exactly "
            "1: the example inside the marker callout must be excepted and the bare one after it "
            "must fail."
        )
    for stale in sorted(set(TRIPS) - {p.stem for p in TRIP_DIR.glob("*.mdx")}):
        problems.append(
            f"NO FIXTURE for the must-trip expectation [{stale}]. Add "
            f"tests/cli-examples/must-trip/{stale}.mdx, or the expectation goes."
        )

    # 2: must-pass passes, and checks something.
    passed = run(FIXTURE_METADATA, PASS_DIR)
    if passed.returncode != 0:
        problems.append(
            "THE GUARD FIRED on tests/cli-examples/must-pass, which is only commands, callouts "
            "and near misses the released CLI has:\n" + passed.stdout.strip()
        )
    elif (count := checked_count(passed.stdout)) is None or count < 4:
        problems.append(
            f"the guard checked {count} invocation(s) on must-pass. The corpus is supposed to "
            "exercise the checking path (invocations outside callouts), not only the exception."
        )

    # 3: the availability bit gates the stub, and not the callout around it.
    doc = json.loads(FIXTURE_METADATA.read_text(encoding="utf-8"))
    for command in doc["commands"]:
        if command["path"] == "kubenest backup restore":
            command["available"] = True
            command["reason"] = "the verb landed in the fixture"
    flipped = temp_json(doc, "restore-available.json")
    stub = TRIP_DIR / "backup-restore-stub.mdx"
    if (after := run(flipped, stub)).returncode != 0:
        problems.append(
            "the guard still failed on the `kubenest backup restore` example with the metadata "
            "saying available: true, so something other than the availability bit is gating it:\n"
            + after.stdout.strip()
        )

    # 4: missing or broken metadata fails closed.
    broken = json.loads(FIXTURE_METADATA.read_text(encoding="utf-8"))
    broken["commands"] = [c for c in broken["commands"] if not c["path"].startswith("kubenest platform")]
    after_break = run(temp_json(broken, "no-platform.json"), TRIP_DIR / "unknown-flag.mdx")
    if after_break.returncode == 0 or "unknown-flag.mdx" not in after_break.stdout:
        problems.append(
            "a metadata file with `kubenest platform` missing did not fail the unknown-flag "
            "fixture, so a broken metadata file can print clean:\n" + after_break.stdout.strip()
        )
    headless = {"cli_version": "fixture", "commit": "x", "generated_at": "x",
                "commands": [{"path": "kubectl", "available": True, "reason": "", "hidden": False,
                              "flags": []}]}
    no_root = run(temp_json(headless, "no-root.json"), PASS_DIR)
    if no_root.returncode == 0 or "no `kubenest` root command" not in no_root.stdout:
        problems.append(
            "a metadata file with no `kubenest` root command did not fail:\n" + no_root.stdout.strip()
        )
    absent = run(Path("cli-metadata/does-not-exist.json"), PASS_DIR)
    if absent.returncode == 0 or "clean" in absent.stdout:
        problems.append(
            "a metadata path that does not exist did not fail the guard, so a missing metadata "
            "file is being read as \"no problems found\":\n" + absent.stdout.strip()
        )

    # 5: the allowlist defers an occurrence and cannot outlive it.
    one = TRIP_DIR / "health-not-a-command.mdx"
    defer = temp_json({"allow": [{"page": str(one), "command": "kubenest health",
                                  "owning_bead": "kn-0000"}]}, "allow.json")
    allowed = run(FIXTURE_METADATA, one, defer)
    if allowed.returncode != 0 or "allowlist" not in allowed.stdout:
        problems.append(
            "an allowlisted occurrence was not reported-and-not-fatal, so the escape hatch the "
            "bead's deferrals rely on does not work:\n" + allowed.stdout.strip()
        )
    rot = temp_json({"allow": [
        {"page": str(PASS_DIR / "not-invocations.mdx"), "command": "kubenest scale",
         "owning_bead": "kn-0001"},
        {"page": "content/gone.mdx", "command": "kubenest health", "owning_bead": "kn-0002"},
    ]}, "rot.json")
    rotted = run(FIXTURE_METADATA, PASS_DIR, rot)
    if rotted.returncode == 0 or "ALLOWLIST IS STALE" not in rotted.stdout:
        problems.append(
            "an allowlist entry whose page no longer shows its command, and one whose page does "
            "not exist, did not fail -- so an entry can outlive the example it was written for:\n"
            + rotted.stdout.strip()
        )

    # 6: the pages that ship, against the metadata CI reads.
    real = run(REAL_METADATA, "content", ALLOWLIST)
    if real.returncode != 0:
        problems.append(
            f"THE GUARD FIRED on the real pages (content/) against {REAL_METADATA}. That is a "
            "page telling a reader to run something the released CLI does not have, which is the "
            "defect this guard exists for -- the page is fixed, or the occurrence is allowlisted "
            "with the bead that owns it:\n" + real.stdout.strip()
        )
    elif (count := checked_count(real.stdout)) is None or count == 0:
        problems.append(
            "the guard checked no invocation on content/. Either the pages or the metadata moved, "
            "and a guard that checks nothing passes forever."
        )
    problems += _real_metadata_expectations(REAL_METADATA)

    if problems:
        print("CLI-EXAMPLE GUARD SELF-TEST FAILED\n")
        for p in problems:
            print(f"  - {p}\n")
        return 1

    print(f"cli-example guard self-test: clean ({len(TRIPS)} must-trip fixture(s) proven to trip, "
          f"{len(list(PASS_DIR.glob('*.mdx')))} must-pass fixture(s) proven to pass, the committed "
          "metadata and the real pages checked)")
    return 0


def _real_metadata_expectations(metadata: Path) -> list[str]:
    """The committed metadata must still say what the guard's fixtures assume."""
    doc = json.loads((REPO / metadata).read_text(encoding="utf-8"))
    commands = {c["path"]: c for c in doc["commands"]}
    out: list[str] = []
    if len(commands) < 15:
        out.append(
            f"{metadata} carries {len(commands)} command(s); the released CLI's tree has more than "
            "that, so this file looks truncated."
        )
    stub = commands.get("kubenest backup restore")
    if stub is None or stub["available"] or not stub["reason"]:
        out.append(
            f"{metadata} does not report `kubenest backup restore` as available: false with a "
            "reason, which is the stub the guard's fixture and the pages rely on."
        )
    install = commands.get("kubenest platform install")
    if install is None or {"--ha", "--server"} - {f["name"] for f in install["flags"]}:
        out.append(
            f"{metadata} does not carry --ha and --server on `kubenest platform install`, so the "
            "metadata is not from the CLI's own command tree."
        )
    return out


if __name__ == "__main__":
    raise SystemExit(main())
