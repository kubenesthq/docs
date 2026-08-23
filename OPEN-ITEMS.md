# Open items register

Every unfinished thing the docs site admits to, in one place: the `OQ-*` design questions, the
`<BuildStatus />` publication boundaries, and the gap-class callouts on the app-layer pages. It
replaces `OPEN-QUESTIONS.md`, which covered only `content/platform/` and was last reconciled
against decision A alone.

This file lives at the repo root, **outside `content/`**, so Nextra cannot route it and it can
never be published to docs.kubenest.io. Keep it that way — it names unmeasured numbers and unfixed
defects.

**Reconciled 2026-08-23** against the bundle manifest, the beads, and the source of all five
repos. Every "verified" line below was checked in code on that date, not inferred from a bead
title. Update this file when you change a page or close one of its items.

> **Every design question is now decided.** Decisions A–G (2026-08-20) and H–Y (2026-08-23) close
> all 43 `OQ-*` questions; the reasoning for each is in `PLAN-BUILD-2026-08-20.md` §2 and §2a.
> What remains against these pages is **measurement and build**, both tracked as beads. There is
> nothing left in this file that is waiting on a judgment call.

| Bucket | Count |
|---|---|
| Design questions — decided | 43 of 43 |
| — closed by decisions H–Y on 2026-08-23 | 18 |
| Numbers still to be measured | 5 |
| Decided policy not yet built | 9 |
| Pages carrying a `<BuildStatus />` boundary | 7 |
| App-layer gaps documented in page callouts | 10 |
| Permanent operational warnings (**not** open items) | ~20 |

---

## 1. Design questions

### 1a. Closed 2026-08-23 — decisions H–Y

Full reasoning for each is in `PLAN-BUILD-2026-08-20.md` §2a. Summarised here so this file stays a
complete index.

| ID | Decision | Where it now lives |
|---|---|---|
| OQ-BUNDLE-1 | **A major bump means the upgrade asks something of you** — a profile removed, a default changed under you, an API version dropped. Everything else is minor, Kubernetes minors included | Decision J; `bundle.mdx` § Version numbers |
| OQ-BUNDLE-3 | **A CVE gets its own release**: the next minor, patched pin only. Assessment within 2 business days, patched bundle within 7 days of an upstream fix, for critical/high in core | Decisions H and I; `bundle.mdx` § When a CVE lands between releases; `kn-eewa` |
| OQ-BUNDLE-4 | **Two bundles supported (N, N-1); a hop of more than one is refused.** A security release does not consume the window | Decision K; `upgrades.mdx` § Skipping versions; `kn-mtpf` |
| OQ-BUNDLE-5 | **The control plane accepts agents from the current bundle and the one before it** | Decision L; `bundle.mdx` § Agent and control plane; `kn-opj8` |
| OQ-PROFILE-1 | **Each profile declares its own backup set**, and the drill covers what it declared | Decision O; `profiles.mdx` § Why profiles and not options; `kn-436i` |
| OQ-PROFILE-2 | **One component set per profile name.** `secrets` is sealed-secrets; external-secrets returns as `secrets-external` when a client needs it | Decision M; both manifests; `profiles.mdx`; `kn-ynaq` |
| OQ-PROFILE-4 | **`replicated-storage` is cut from 1.x.** The engine is chosen when a client needs replicated volumes | Decision N; both manifests; `profiles.mdx`; `kn-54ni` **closed** |
| OQ-PROFILE-5 | **Adding a profile is an upgrade** — same gates, journal, rollback and window, with the gate list derived from the diff | Decision P; `profiles.mdx` § Changing a profile later; `kn-avk0` |
| OQ-UPGRADE-1 | **The scan covers Git as well as live objects.** Live findings block; Git findings warn, naming file and ref | Decision S; `upgrades.mdx` § The deprecated API scan; `kn-tczn` |
| OQ-UPGRADE-3 | **Warn now, refuse once measured** — the window-fit gate turns on when `kn-btk8` replaces the provisional per-node figure | Decision T; `upgrades.mdx` § Maintenance windows; `kn-ght1` |
| OQ-UPGRADE-4 | **Automatic before the point of no return; operator-initiated after it** | Decision Q; `upgrades.mdx` § What actually rolls back |
| OQ-UPGRADE-5 | Follows OQ-BUNDLE-4: **step through one bundle at a time** | Decision K; `kn-mtpf` |
| OQ-UPGRADE-7 | **Operator-initiated only for 1.x.** Auto-applying security releases inside the window is stated direction, not a feature | Decision R; `upgrades.mdx` § Who starts an upgrade |
| OQ-BACKUP-1 | **Proof set plus a rotating sample of real volumes**, with the result naming what it verified. Full-cluster drill on demand | Decision V; `backup-restore.mdx` § What a drill covers; `kn-odyo` |
| OQ-PATCH-1 | **Warn at 7 days pending, critical at 14.** A critical kernel CVE escalates on arrival rather than waiting out the threshold | Decision Y; `os-patching.mdx` § Seeing patch state; `kn-nqj` |
| OQ-PATCH-2 | **Livepatching is respected, not provided** | Decision W; `os-patching.mdx` § Patches that need a reboot; `kn-nqj` |
| OQ-PATCH-3 | **The installer writes the APT policy**: security pocket only, no APT-initiated reboot, k3s and the runtime held | Decision X; `os-patching.mdx` § What gets patched; `kn-nqj` |
| OQ-INSTALL-9 | **The three-node `ha` tier ships in bundle 1, and proving it is a release gate** | Decision U; `ha.mdx`; `kn-kp3` |

Two of these — OQ-INSTALL-9 and OQ-PROFILE-4 — had been parked on a Crest answer that never
arrived, and were decided on our own judgment instead. Continuing to wait was itself the cost.

### 1b. Closed 2026-08-20 — decisions A–G

| ID | Decision |
|---|---|
| OQ-HA-1 | **Embedded etcd on every tier** (`k3s --cluster-init`), `single-server` included. Decision A |
| OQ-BACKUP-4 | **Resolved by A** — one snapshot path, not two |
| OQ-BUNDLE-2 | **Track k3s stable minus one minor**, pinned to that minor's current patch. Decision B |
| OQ-BUNDLE-6 | **Done** — every core and profile pin recorded and verified against upstream |
| OQ-BUNDLE-7 | **Yes, published** — schema and manifests both ship in `kubenest-contracts`. Choice S2 |
| OQ-BUNDLE-8 | Structure settled and shipped with `provisional: true`. Decision C. The numbers are §1c |
| OQ-UPGRADE-2 | **pluto, dataset pinned. No blanket override** — findings acknowledged one at a time. Decision D |
| OQ-BACKUP-3 | **Snapshot hourly/keep 24; workload backup daily/keep 14; drill weekly.** Decision E |
| OQ-PROFILE-3 | **Verified** — the chart moved to `bitnami.github.io/sealed-secrets`; the old index is a 404 |
| OQ-INSTALL-3 … -8, -10 … -14 | Closed on the `install.mdx` decisions table. Four of them — -5, -8, -9, -12 — were closed on an assumption rather than an answer, and are mirrored in `STRATEGY-2026-08.md` §9.3 |

Decision A's consequence is routinely misread, so it is worth restating: `single-server → ha` is
now a join rather than a rebuild, but **the join is not implemented and not tested** (`kn-kp3`), so
the tier is still an install-time choice in practice. The pages say exactly that, and must not be
"corrected" into promising a migration.

### 1c. Numbers still to be measured

Not decisions. `kn-0i0` closed and `lab/hetzner` is a working host profile, so none of these is
blocked any more — what is left is turning single gate timings into figures we are willing to put
in front of a customer.

| ID | What to measure | What hardware has already shown | Owner |
|---|---|---|---|
| OQ-BUNDLE-8 | Every threshold and timeout in `limits` | Install 4m14s against a 30m `install-total` | `kn-btk8` |
| OQ-UPGRADE-6 | Upgrade duration as fixed overhead plus per-node cost | One point: 0.9 → 1.0 on two nodes in 3m11s against a provisional 30m per node. Decision T makes this figure turn a warning into a refusal | `kn-btk8` |
| OQ-INSTALL-2 | Minimum and recommended host sizing | Provisional floors in the manifest; preflight warns rather than fails; `install.mdx` quotes real cloud-host figures | `kn-btk8` |
| OQ-BACKUP-2 | Full cluster restore duration — **X in "we restore within X hours"** | Clean Velero object + PVC restore 33s; datastore recovery from an S3-only snapshot 17s; full `kn-f9lm` gate 434.70s — all proof-sized, so this is the fixed overhead, not the answer | `kn-ze1` |
| OQ-HA-2 | The same number, seen from the tier that promises it | Blocked on OQ-BACKUP-2 | `kn-ze1` |

**OQ-BACKUP-2 is still the most important unmeasured number in the product**, and the gate figures
above do not answer it. They were taken against a proof Pod, a ConfigMap and one small PVC. What a
customer is buying is a restore of *their* data, and the shape of that answer is fixed overhead
plus per-GB — which needs a run at a realistic volume. Until then the `single-server` tier's
promise is a sentence with a blank in it. Do not quote it with a number.

### 1d. Decided policy the pages state and the code does not do yet

Every one of these reads as settled on the page, with the page saying plainly that it is not built.
That is the intended state; the risk is forgetting which is which, so they are listed together.

| What the page states | Bead |
|---|---|
| A CVE gets a patched bundle within 7 days, on a 2-business-day assessment clock | `kn-eewa` |
| The control plane accepts only in-window agents | `kn-opj8` |
| The bundle-path gate refuses a hop of more than one bundle | `kn-mtpf` |
| The deprecation scan reads the Git desired state, warning where live blocks | `kn-tczn` |
| Pre-flight estimates the upgrade against the remaining window | `kn-ght1` (needs `kn-nqj`) |
| Each profile declares a backup set the drill covers | `kn-436i` |
| The drill verifies a rotating sample of real volumes and names them | `kn-odyo` |
| The installer writes the APT policy; livepatching is respected; pending reboots warn at 7d and go critical at 14d | `kn-nqj` |
| Adding a profile to a running cluster runs through the upgrade path | `kn-avk0` |

**Do not add a manifest field ahead of the code that reads it.** `kn-iqtd` is the precedent — a
threshold that is required, parsed and never read. Where one of the above needs a new manifest
key, land the schema and its consumer together.

---

## 2. Publication boundaries — the seven pages carrying `<BuildStatus />`

The registry is `src/lib/build-status.ts`; `bun run check:status` enforces in both directions that
a listed page carries the marker and an unlisted one does not. Reproduced here so this file is a
complete index — **do not edit these words here**, edit the registry.

| Page | Availability | Blocking beads |
|---|---|---|
| `/platform/install` | partial | `kn-kp3` `kn-sev5` `kn-ynaq` `kn-0d73` `kn-j5s` `kn-hyl7` `kn-nqj` |
| `/platform/bundle` | partial | `kn-twe` `kn-ze1` `kn-nqj` |
| `/platform/profiles` | **unavailable** | `kn-ynaq` `kn-sev5` |
| `/platform/upgrades` | partial | `kn-1krv` `kn-kp3` `kn-nqj` `kn-mtpf` `kn-tczn` |
| `/platform/backup-restore` | partial | `kn-x0wv` `kn-hyl7` `kn-odyo` |
| `/platform/os-patching` | **unavailable** | `kn-nqj` |
| `/platform/ha` | partial | `kn-kp3` `kn-hyl7` `kn-nqj` |

Verified 2026-08-23 — every claim above is still true in source:

- **No profile installs.** `kubenest-cli/pkg/install/plan.go:591` refuses `observability` and
  `secrets` by name rather than installing core in their place.
- **No reboot is coordinated on either tier.** `kubenest cluster set-reboot-window` and
  `kubenest node reboot` are not commands; `NewClusterCommand` registers exactly one subcommand,
  `set-window` (`kubenest-cli/pkg/cmd/cluster.go:18`).
- **The maintenance window is not in force.** `set-window` validates its input and then stores it
  through a control-plane route that does not exist — no window handler appears anywhere in
  `kubenest-backend/app/api/v1/`. The upgrade gate consequently passes every cluster as
  unconfigured, and the decision-T estimate has nothing to compare against.
- **`kubenest backup restore` is a stub.** Registered via `newBackupSkeletonCommand`
  (`kubenest-cli/pkg/cmd/backup.go:82`); `set-target`, `now` and `drill` are real.
- **`checkBundlePath` has no adjacency rule** (`kubenest-cli/pkg/upgrade/gates.go:209`), and
  `deprecation.Scan` reads live workloads only.
- The `ha` tier has still never been installed on three machines — now a **release gate**
  (`kn-kp3`, decision U) rather than an open-ended caveat — and the post-point-of-no-return
  rollback has still only run in unit tests (`kn-1krv`).

`/platform/profiles` should be the first of these to clear: with `replicated-storage` cut and
`secrets` resolved to one component, its remaining blockers are two profiles that install.

---

## 3. App-layer gaps documented in page callouts

Nine of these are defects or unbuilt surfaces; one is intended scope. None was covered by the old
index, which stopped at `content/platform/`. Each was re-verified in source on 2026-08-22.

| Gap | Pages | Verified against | Bead |
|---|---|---|---|
| `dsn` / `DATABASE_URL` carry a literal `${postgres-password}` that nothing substitutes | addons, apps, creating-apps, managing-addons, first-deployment | export resolver copies the value verbatim | `kn-kgu5` |
| A standalone `AddonInstance` is not a working shared-export source | addons, apps | `stack_templates.py:956` feeds `addon_instance_id` into a `component` key; `apps.py` attach-addon injects `ref_component=addon.name` without adding a component of that name | `kn-l8z5` |
| Cluster create returns `kubenest cluster connect`, which is not a subcommand | first-deployment | `clusters.py:66,250` emit it; the CLI's `cluster` command registers only `set-window` | `kn-887b` |
| No `ResourceQuota` is created, and the API rejects `resource_quota` | projects | no `ResourceQuota` anywhere in `kubenest-backend/app/` | `kn-k6zd` — **docs half done**, backend half open |
| Deleting a project sends no event; namespace and Project CR keep running | projects | `delete_project` (`projects.py:218`) calls only `crud_project.db_delete`. `send_project_delete` exists at `websocket/sender.py:256` with **zero callers** | `kn-ezf4` |
| A failed `project_create` hub send is swallowed with no replay path | clusters | `projects.py:98-100` logs and continues | `kn-z7g7` |
| The control plane holds a cluster-admin bearer for every tenant cluster | index, architecture | `models/cluster.py:102` — `kubenest_sa_token`, cluster-admin, plaintext, never expires | `kn-cjqw` `kn-p61d` |
| The console cannot approve a `kubenest login` device code or issue a CLI token | install | no `/cli-authorize` page in `kubenest-ui` | `kn-0d73` |
| Rate limiting is configurable but enforced on one sample route; no usage endpoint, no headers | api | enforcement dependency attached only to `POST /tasks/task` | `kn-3m3z` — **docs half done**, backend half open |
| Provisioning is wired for `aws` only; other providers return 422 "coming soon" | cluster-registration | `clusters.py:128,426` | intended scope, tracked by `kn-hn7` — **not a defect** |

Every gap on this list now names a bead on its page. `kn-k6zd` and `kn-3m3z` were both corrected by
the pre-publication truth pass (`4ba3d49`) and their remaining work is backend-only; their bead
text still quotes docs that no longer say what it quotes, and both carry a comment saying so.

---

## 4. Not open items

Roughly twenty warning callouts across the site are permanent operational warnings, not gaps
waiting to close. They are listed here so a future consolidation pass does not mistake them for
work and try to "resolve" them:

Direct edits to KubeNest-managed Git state get overwritten · the cluster JWT is an SSH-key-grade
credential · secure the install values file and delete it after Helm accepts · deleting a project
or cluster needs the org admin role, and projects block cluster deletion with a 409 · a
`components` PATCH replaces a component wholesale rather than merging fields · removing a
component another `exportRef` depends on is a 409 · rolling back an addon or an App containing
addons can force a Helm downgrade the chart never designed for · nothing lists an addon's
dependents before you delete it · the API never returns export values, by design · the
sealed-secrets sealing key is the most important thing in the cluster and is in the backup set ·
the single-server datastore is the thing people forget · the drill's teardown is unconditional on
purpose · convergence checks report the last state they saw and are not single samples (install
and upgrade both) · advertised host size and kernel-reported host size are the same machine ·
restoring the platform does not restore application data · a single-server control-plane reboot is
recurring toil the `ha` tier does not have · KubeNest is self-hosted, with no SaaS to sign up for ·
a cross-cluster App needs every target registered first · re-running an install without a profile
is not a resume.

---

## 5. What needs a decision from you

**Nothing.** Every `OQ-*` is decided. What is left is work, and all of it is on a bead:

- **Measure the five numbers in §1c.** `kn-btk8` for the manifest's provisional limits, `kn-ze1`
  for the restore duration at realistic volume. OQ-BACKUP-2 is the one with a customer promise
  hanging off it.
- **Build the nine decided-but-unbuilt items in §1d.** `kn-eewa` is the one with a release
  blocker's weight: the CVE commitment is now written on a public page, and a commitment with no
  advisory feed behind it is worse than none.
- **Prove the `ha` tier on three hosts** (`kn-kp3`) — decision U made that a gate on 1.0, not a
  caveat.
- **Ship two profiles** (`kn-ynaq`, `kn-sev5`) and `/platform/profiles` stops being a
  specification page.

---

## Cross-page dependencies

What is left unlocks along these lines.

```
kn-nqj  (window + reboot + APT policy)
   ├─→ kn-ght1     the window-fit estimate has something to compare against
   └─→ upgrades.mdx and os-patching.mdx both stop being partly aspirational

kn-btk8  (measurements replace the provisional limits)
   └─→ kn-ght1     the estimate becomes a refusal rather than a warning

kn-kp3  (three-node install, upgrade, restore — a 1.0 release gate)
   └─→ ha.mdx, install.mdx, upgrades.mdx all lose their multi-node caveat

kn-twe  (the matrix, five configurations)
   ├─→ every profile's `provisional: true`
   ├─→ needs kn-opj8's two agent-compatibility rows
   └─→ needs kn-mtpf's supported transitions

kn-eewa  (advisory feed + security-release runbook)
   └─→ bundle.mdx's CVE commitment becomes a claim we can make

kn-ze1  (restore at realistic volume)
   └─→ OQ-BACKUP-2 → OQ-HA-2, the single-server promise
```

## Where else these live

- **Decisions A–G, with reasoning:** `PLAN-BUILD-2026-08-20.md` §2.
- **Decisions H–Y, with reasoning:** `PLAN-BUILD-2026-08-20.md` §2a.
- **Publication boundaries, in full:** `src/lib/build-status.ts`, rendered by `<BuildStatus />`.
  Edit there, never here.
- **Gap callouts, in full:** inline on the page where the reader meets the gap. That is deliberate
  — a reader hitting the `dsn` defect needs it next to the example, not in an index.
- **Crest-dependent assumptions:** `STRATEGY-2026-08.md` §9.3, with what to unwind if wrong. Two
  of its entries — OQ-INSTALL-9 and OQ-PROFILE-4 — no longer wait on Crest.
