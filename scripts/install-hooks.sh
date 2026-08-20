#!/usr/bin/env bash
# Install the publication-boundary check as a pre-commit hook.
#
# CI runs `bun run check:status` too, but there it cannot see the beads database —
# that lives in the parent workspace and is not part of this repo — so the bead
# freshness half is skipped. Locally it is not, and locally is where beads close.
#
# Idempotent. Safe to re-run. Composes with the Agent Mail guard: both land in
# .git/hooks/hooks.d/pre-commit/ and run in filename order.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
hooks_dir="$repo_root/.git/hooks"
chain_dir="$hooks_dir/hooks.d/pre-commit"

mkdir -p "$chain_dir"

# The Agent Mail guard installs a chain-runner at .git/hooks/pre-commit that runs
# everything executable in hooks.d/pre-commit. If it is not there, we are the only
# hook and need to be the entry point ourselves.
if [ ! -x "$hooks_dir/pre-commit" ]; then
  cat > "$hooks_dir/pre-commit" <<'RUNNER'
#!/usr/bin/env bash
set -euo pipefail
for hook in "$(dirname "$0")"/hooks.d/pre-commit/*; do
  [ -x "$hook" ] || continue
  "$hook" || exit $?
done
RUNNER
  chmod +x "$hooks_dir/pre-commit"
  echo "installed chain-runner at .git/hooks/pre-commit"
fi

cat > "$chain_dir/60-build-status" <<'HOOK'
#!/usr/bin/env bash
# Publication boundary: no page may describe unbuilt software without saying so,
# and no entry may cite a bead that has already closed. See README.md.
set -euo pipefail
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
if command -v bun >/dev/null 2>&1; then
  bun run check:status
else
  node scripts/check-build-status.mjs
fi
HOOK
chmod +x "$chain_dir/60-build-status"

echo "installed $chain_dir/60-build-status"
echo
echo "Verify with:  bun run check:status"
echo "Bypass once:  git commit --no-verify"
