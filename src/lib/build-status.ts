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
    beads: ['kn-7k8', 'kn-plcc'],
    missing:
      'The `kubenest` CLI does not exist — not `login`, not `platform install`, not the thirteen stages, preflight, journal, resume or `platform uninstall`. It is a greenfield binary with no build or signing pipeline.',
    today:
      'Clusters are created by a backend-driven Terraform job that runs k3sup and Helm, and it installs none of the bundle described here.',
  },
  '/platform/bundle': {
    beads: ['kn-boj', 'kn-twe'],
    missing:
      'No bundle has been released, pinned or tested. The manifest on this page contains literal `<pinned>` placeholders, nothing anywhere pins a k3s version, and the compatibility matrix has never run.',
    today:
      'The cluster record holds a free-form `components` blob of booleans — the model D11 explicitly rejects — with no bundle version, profile set or HA tier.',
  },
  '/platform/profiles': {
    beads: ['kn-boj', 'kn-ynaq', 'kn-sev5', 'kn-54ni'],
    missing:
      'No profile is implemented. There is no per-cluster profile record, and none of the components a profile would install are present in the tree.',
  },
  '/platform/upgrades': {
    beads: ['kn-fuo'],
    missing:
      'There is no upgrade path of any kind. No transition engine, no deprecated-API scan, no gates, no journal, no rollback, and no `system-upgrade-controller` anywhere in the tree.',
    today: 'The provisioner accepts exactly three operations: create, scale, destroy.',
  },
  '/platform/backup-restore': {
    beads: ['kn-mzn'],
    missing:
      'Nothing on this page is implemented. There is no Velero, no schedule, no restore drill, no drill result record, no alerting and no upgrade gate.',
  },
  '/platform/os-patching': {
    beads: ['kn-nqj'],
    missing:
      'No automatic patching and no coordinated reboots. `unattended-upgrades` is never configured and kured is not installed. The cluster record carries no patch or reboot state.',
  },
  '/platform/ha': {
    beads: ['kn-kp3'],
    missing:
      'HA is not an install-time tier. There is no tier field on the cluster record and no etcd anywhere — single-server k3s runs on SQLite today, unpinned.',
  },
  '/platform/deploying-an-app': {
    beads: ['kn-pgu'],
    missing:
      'There is no Gateway API controller. The installer disables Traefik and installs ingress-nginx — the EOL component we sell against — so the `HTTPRoute` this page describes has nothing to serve it.',
    today:
      'The app layer hardcodes `className: "nginx"` when it renders ingress, so it also cannot deploy onto a cluster built to this spec.',
  },
}

/** True when the page describes software that does not exist. */
export function isSpecPage(path: string): boolean {
  return path in SPEC_PAGES
}
