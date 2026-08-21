/**
 * Which documented behaviour actually exists.
 *
 * A page listed here describes software that is not built. It is a specification,
 * and it must carry a <BuildStatus /> marker so a reader can tell the difference
 * between a thing we ship and a thing we intend. `bun run check:status` enforces
 * that in CI, in both directions — a listed page without a marker fails, and a
 * marker on an unlisted page fails.
 *
 * The `beads` are the work that makes the page true. When they all close, delete
 * the entry and the marker in the same change. That is the whole lifecycle: this
 * file should shrink to `{}` and then be removed.
 *
 * Verified against the repos on 2026-08-20 (PLAN-BUILD-2026-08-20.md §1), not
 * inferred from bead titles. Do not add an entry without checking the code.
 */

export type BuildStatusEntry = {
  /** Beads that must close before this page describes reality. */
  beads: string[]
  /** What does not exist yet. One sentence, concrete, no hedging. */
  missing: string
  /** What is true today, if anything. Omit when the answer is "nothing". */
  today?: string
}

export const SPEC_PAGES: Record<string, BuildStatusEntry> = {
  '/platform/install': {
    beads: ['kn-kp3', 'kn-sev5', 'kn-ynaq', 'kn-54ni', 'kn-0d73', 'kn-j5s', 'kn-fuo', 'kn-nqj', 'kn-f9lm'],
    missing:
      'Only the single-server shape has ever been installed. The three-node `ha` tier is written and unit-tested but has never run on real hardware, no component profile is installable (stage 11 refuses one rather than installing core silently), the console has no page to approve a `kubenest login` device code or issue a CLI token, and the cluster reports no backup configuration state. The page also describes the day-2 product the install leads into — upgrades, OS patching and verified restore — and none of that is built.',
    today:
      'The installer is real and gated on a real host: `kubenest platform install` runs all thirteen stages against a control plane, single-server core in 4m14s against a fifteen-minute budget, five acceptance checks green, an identical re-run converging in 14s from the journal, a failure naming its stage and component, and uninstall leaving a clean machine with the customer volume group intact.',
  },
  '/platform/bundle': {
    beads: ['kn-twe', 'kn-fuo', 'kn-ze1', 'kn-f9lm', 'kn-nqj'],
    missing:
      '"Tested together as one thing" is still the aspirational half. The compatibility matrix has never run, so no configuration has been through install, workload, backup, restore drill and upgrade on a release; every profile in the manifest is marked provisional and none has been tested against core. The upgrade path that would make the version a transition rather than a label does not exist, and the manifest\'s limits are provisional numbers awaiting measurement.',
    today:
      'The version number now means "this is what you are running" for core: `kubenest platform install` fetches the manifest from the control plane, takes every pin and every deadline from it, and its last acceptance check compares those pins against the running cluster — kubelet version per node, chart version per component — before reporting success. Verified on a real host.',
  },
  '/platform/profiles': {
    beads: ['kn-ynaq', 'kn-sev5', 'kn-54ni'],
    missing:
      'No component profile installs anything, and asking for one fails the install: stage 11 refuses `observability`, `secrets` and `replicated-storage` rather than installing core in their place, so the run stops with core already on the machines and the cluster marked install-failed. Nothing adds a profile to a cluster afterwards either.',
    today:
      'Core installs, and the profile set is recorded and validated as of kn-boj — an unknown profile is rejected with 422 rather than ignored. `ha` is the exception in the list: it is an install-time topology stage 3 builds, not components stage 11 installs.',
  },
  '/platform/upgrades': {
    beads: ['kn-fuo', 'kn-f9lm'],
    missing:
      'There is no bundle transition yet: `kubenest platform diff` and rollback do not exist, `kubenest platform upgrade` exits as unavailable, and there is no deprecated-API scan, verified restore-drill input, pre-flight gate set, upgrade journal, eight-stage orchestration, maintenance-window resume or post-upgrade record.',
    today:
      'The core installer places pinned `system-upgrade-controller` v0.20.1 and waits for its CRDs and controller to become Ready, but creates no upgrade Plan. The proven install journal resumes installs only; it is not the upgrade journal described here.',
  },
  '/platform/backup-restore': {
    beads: ['kn-f9lm', 'kn-j5s'],
    missing:
      'The restore drill does not exist — no schedule, no drill result record, no alerting, and no upgrade gate reading it. That is the half of this page that matters: a backup nobody has restored is what every competitor already ships. `kubenest backup drill` and `kubenest backup restore` are skeletons that exit non-zero, `kubenest platform restore` is not a command at all, the hourly datastore-snapshot cadence in the manifest is parsed and acted on by nothing, and no heartbeat yet carries `backup: unconfigured`.',
    today:
      'Velero installs as stage 8 of the installer, pinned at chart 12.1.0 and unconfigured by default (kn-mzn). `kubenest backup set-target` proves the target rather than assuming it — it waits for Velero to mark the storage location Available before writing the default schedule from the bundle manifest — and `kubenest backup now` takes one backup and waits for it to complete. Decision A also collapsed the two documented snapshot mechanisms into one — every tier runs etcd.',
  },
  '/platform/os-patching': {
    beads: ['kn-nqj'],
    missing:
      'No patching or reboot policy. `unattended-upgrades` is never configured by the installer, kured watches a platform sentinel file that nothing yet creates, so no reboot is ever coordinated, and reboot windows do not exist — neither `kubenest cluster set-reboot-window` nor `kubenest node reboot` is a command. The cluster record carries no patch or reboot state.',
    today:
      'The machinery is on the cluster. Stage 9 installs system-upgrade-controller v0.20.1 and kured 6.1.0 at the bundle pins, and acceptance check 2 of 5 fails the install if either is not Running. kured is deliberately pointed at `/var/run/kubenest-reboot-approved` rather than the Ubuntu default `/var/run/reboot-required`, so placing the component cannot reboot a node before the policy that decides when exists.',
  },
  '/platform/ha': {
    beads: ['kn-kp3', 'kn-f9lm'],
    missing:
      'No cluster has ever been installed on three machines. The `ha` path is written — stage 3 joins servers 2 and 3, preflight demands three control-plane nodes and probes the etcd peer ports — but the real-host gate was single-server only, nothing checks that etcd has quorum after the join, and growing a running `single-server` cluster into `ha` is not built at all. The restore drill that makes the single-server promise honest does not exist yet either.',
    today:
      'Single-server is real and proven on a real host: thirteen stages, five acceptance checks, resume and uninstall. Every tier runs embedded etcd as of decision A — `single-server` as one node, `ha` as three, the first initialising and the other two joining — and the tier is recorded against the cluster at install, so growing into `ha` is a join rather than a rebuild, once that path is built.',
  },
}

/** True when the page describes software that does not exist. */
export function isSpecPage(path: string): boolean {
  return path in SPEC_PAGES
}
