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
    beads: ['kn-kp3', 'kn-sev5', 'kn-ynaq', 'kn-54ni', 'kn-0d73', 'kn-j5s', 'kn-hyl7', 'kn-nqj'],
    missing:
      'Only the single-server shape has ever been installed. The three-node `ha` tier is written and unit-tested but has never run on real hardware, no component profile is installable (stage 11 refuses one rather than installing core silently), and the console has no page to approve a `kubenest login` device code or issue a CLI token. Of the day-2 product the install leads into, OS patching is the part still unbuilt: no reboot window, no patch state. The health report the install starts also cannot yet collect datastore or bundle-drift facts, so the single-server tier\'s only recovery path is unmonitored.',
    today:
      'The installer is real and gated on a real host: `kubenest platform install` runs all thirteen stages against a control plane, single-server core in 4m14s against a fifteen-minute budget, five acceptance checks green, an identical re-run converging in 14s from the journal, a failure naming its stage and component, and uninstall leaving a clean machine with the customer volume group intact. Two of the day-2 features it leads into were gated on real hardware since: bundle upgrades with rollback, and verified restore drills whose result reaches fleet health and the console.',
  },
  '/platform/bundle': {
    beads: ['kn-twe', 'kn-ze1', 'kn-nqj'],
    missing:
      '"Tested together as one thing" is still the aspirational half. The compatibility matrix has never run, so no configuration has been through install, workload, backup, restore drill and upgrade on a release; every profile in the manifest is marked provisional and none has been tested against core. The limits are still marked provisional, and the two figures real hardware has now measured have not replaced any of them.',
    today:
      'The version number now means "this is what you are running" for core: `kubenest platform install` fetches the manifest from the control plane, takes every pin and every deadline from it, and its last acceptance check compares those pins against the running cluster — kubelet version per node, chart version per component — before reporting success. The upgrade path that makes a version a transition rather than a label exists too: eight stages components-first and Kubernetes-last, seven pre-flight gates, and rollback. Both proven on real hosts.',
  },
  '/platform/profiles': {
    beads: ['kn-ynaq', 'kn-sev5', 'kn-54ni'],
    missing:
      'No component profile installs anything, and asking for one fails the install: stage 11 refuses `observability`, `secrets` and `replicated-storage` rather than installing core in their place, so the run stops with core already on the machines and the cluster marked install-failed. Nothing adds a profile to a cluster afterwards either.',
    today:
      'Core installs, and the profile set is recorded and validated as of kn-boj — an unknown profile is rejected with 422 rather than ignored. `ha` is the exception in the list: it is an install-time topology stage 3 builds, not components stage 11 installs.',
  },
  '/platform/upgrades': {
    beads: ['kn-1krv', 'kn-kp3', 'kn-nqj'],
    missing:
      'Two things on this page have never run on hardware, and they are the two that matter when an upgrade goes wrong. The datastore-restore rollback — recovery from a failure *after* the point of no return, which is what every pre-flight gate and the stage-2 backup are insurance against — has only ever run in unit tests (kn-1krv). And no upgrade has run on the three-node `ha` tier, so the drain-and-return behaviour described for a multi-node control plane is untested (kn-kp3). Separately, the maintenance window is not in force at all: `kubenest cluster set-window` stores it through a control-plane route that does not exist, and the upgrade never reads one back, so the gate passes every cluster as unconfigured and the mid-upgrade pause never fires (kn-nqj).',
    today:
      'The upgrade runs, gated on a real host: `kubenest platform upgrade` took a two-node cluster from bundle 0.9 to 1.0 in 3m11s through all eight stages, components-first and Kubernetes-last, with a two-replica workload reachable on every one of 146 one-second probes. The seven pre-flight gates, the deprecated-API scan, the upgrade journal and the fast Helm rollback for a failure before the point of no return are all real.',
  },
  '/platform/backup-restore': {
    beads: ['kn-j5s', 'kn-hyl7'],
    missing:
      '`kubenest backup restore` — restoring a namespace or workload into a live cluster — is still a guarded stub that exits non-zero, and no open bead owns it. Datastore snapshot freshness is not collected: the operator cannot read etcd membership or snapshot times from inside a pod, so the manifest\'s three-hour `max-snapshot-age` threshold is fed by nothing and the single-server tier\'s only recovery path is the one part of this page with no alert (kn-hyl7). The operator-to-hub-to-backend path that carries all of this has never run on a real cluster — the collector is unit-tested against a fake Kubernetes client (kn-j5s).',
    today:
      'The restore drill exists and is gated on real hardware. Weekly, the cluster restores a labelled proof Pod, ConfigMap and PVC into an isolated namespace, compares objects and PVC bytes, requires every PodVolumeRestore to complete, tears the scratch down unconditionally, and persists stage, reason code, counts and duration. `kubenest backup set-target`, `backup now`, `backup drill` and `kubenest platform restore` are all implemented. The release gate restored clean PVC bytes, failed a corrupted archive as `BACKUP_CONTENT_UNREADABLE` rather than trusting the still-Completed Backup object, and recovered embedded etcd from an S3-only snapshot. The result reaches fleet telemetry as a `backup` health group, a failed drill is a critical alert with webhook delivery, an unconfigured target is a warning, the console renders passed, failed, never-run and stale distinctly, and the upgrade pre-flight refuses to run when the last drill did not pass.',
  },
  '/platform/os-patching': {
    beads: ['kn-nqj'],
    missing:
      'No patching or reboot policy. `unattended-upgrades` is never configured by the installer, kured watches a platform sentinel file that nothing yet creates, so no reboot is ever coordinated, and reboot windows do not exist — neither `kubenest cluster set-reboot-window` nor `kubenest node reboot` is a command. The cluster record carries no patch or reboot state.',
    today:
      'The machinery is on the cluster. Stage 9 installs system-upgrade-controller v0.20.1 and kured 6.1.0 at the bundle pins, and acceptance check 2 of 5 fails the install if either is not Running. kured is deliberately pointed at `/var/run/kubenest-reboot-approved` rather than the Ubuntu default `/var/run/reboot-required`, so placing the component cannot reboot a node before the policy that decides when exists.',
  },
  '/platform/ha': {
    beads: ['kn-kp3', 'kn-hyl7', 'kn-nqj'],
    missing:
      'No cluster has ever been installed on three machines. The `ha` path is written — stage 3 joins servers 2 and 3, preflight demands three control-plane nodes and probes the etcd peer ports — but the real-host gate was single-server only, nothing checks that etcd has quorum after the join, and growing a running `single-server` cluster into `ha` is not built at all. Redundancy is derived from control-plane node health rather than etcd membership, so an `ha` cluster that lost a member while its nodes stay Ready still reads as `quorum` (kn-hyl7). The automatic one-at-a-time control-plane reboot the `ha` column promises also needs the patching policy, and no reboot is coordinated on either tier yet (kn-nqj).',
    today:
      'Single-server is real and proven on a real host: thirteen stages, five acceptance checks, resume and uninstall — and so now is the restore path its promise rests on, including recovery of embedded etcd from a snapshot held only in S3, which is exactly the disaster this page describes. Every tier runs embedded etcd as of decision A — `single-server` as one node, `ha` as three, the first initialising and the other two joining — and the tier is recorded against the cluster at install, so growing into `ha` is a join rather than a rebuild, once that path is built. Fleet telemetry reports control-plane redundancy as `none`, `quorum` or `degraded-quorum` rather than a boolean, so no cluster is ambiguous about which tier it bought.',
  },
}

/** True when the page describes software that does not exist. */
export function isSpecPage(path: string): boolean {
  return path in SPEC_PAGES
}
