# Retired-claim guard fixtures

**Nothing in this directory is part of the site.** The pages here contain
DELIBERATELY WRONG PROSE — claims that were retired because they are not true.
The site builds from `content/`; these files exist only to be fed to
`scripts/check_retired_claims.py` by `scripts/selftest_retired_claims.py`.

## Why they exist

The guard protects the publish: if a retired security claim reappears in any
wording, the deploy stops. Its failure mode is therefore entirely in the GREEN
path. A broken regex, a renamed registry key, an exclusion that swallows
everything — any of those makes it print `retired-claim guard: clean` and exit 0
forever, and nothing downstream notices, because **a red result gets
investigated and a green one does not**.

The published-bundle workload gate had two defects in one day and both were in
its green path: a PASS branch that had never executed (kn-nlz8) and an
experiment arm that changed nothing (kn-i965). Neither was visible to review;
both were visible only to use. This guard has the same shape.

## The two corpora

- `must-trip/` — one page per retired claim in `scripts/retired-claims.json`,
  named `<claim-id>.mdx`, making that claim in prose. The self-test fails if any
  registry entry has no fixture, so **the registry cannot grow past its own
  evidence**, and fails if the guard does not name that id when run over them.
- `must-pass/` — prose that sits deliberately close to the retired claims
  without making them. Over-firing costs a publish and trains people to ignore
  the guard, which is its own way of going quiet.

## Adding a retired claim

Add the registry entry, then add `must-trip/<its-id>.mdx` making the claim in
your own words rather than by copying the regex. The self-test will tell you if
you forget.
