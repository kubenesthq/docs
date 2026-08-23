# Where the software does not yet match the docs

**The docs are the specification.** As of 2026-08-23 the published site describes KubeNest as it is
meant to work, without hedges, build-status markers or defect notes. Where the code does not match,
the code is what changes — or, if it turns out it cannot, we come back and change the spec
deliberately rather than letting a page quietly rot into a disclaimer.

This file is the delta list: every place the published site currently says something the
implementation does not do yet. It lives at the repo root, **outside `content/`**, so Nextra cannot
route it and it can never be published.

Update it whenever a page makes a new claim, and delete a row when the code catches up.

> The previous apparatus — `<BuildStatus />`, `src/lib/build-status.ts`, `bun run check:status` and
> the per-page defect callouts — is gone. It was replaced on purpose. Do not reintroduce a
> "this is not built yet" marker on a page; put the gap here and fix the code.

---

## 1. Security claims the site now makes as fact

These are called out separately because they are the rows where the gap is a **risk to a customer's
cluster**, not a missing feature. The published pages describe the target trust model. Every one of
these must close **before the first customer install**, not merely before someone notices.

| The site says | The code does | Bead |
|---|---|---|
| Cluster operations flow through the hub to the agent; no cluster credential is held by the control plane | Registration persists a cluster-admin bearer token on the cluster record, and StackDeploy CRUD, ArgoCD registration, component secrets and addon mutations call the tenant cluster's API directly with it | `kn-cjqw`, `kn-p61d` |
| Three roles — `admin`, `member`, `viewer` — bind at organization, cluster and project scope | Only the organization role is enforced. Cluster- and project-scoped bindings are membership records no endpoint consults, so a `viewer` can create projects, deploy apps and write secrets | `kn-gdf` |
| Rotating the agent credential means the previous one stops being accepted | The hub validates the signature only, so a leaked 365-day JWT stays usable for its full lifetime | `kn-i3c` |
| The control plane never renders a credential into a browser | Fixed for the install command (`kn-kvc3`); the remaining phases of the per-tenant credential broker are in flight | `kn-rnyl` |

There is no live control plane and no customer cluster today, so nothing is exposed right now. That
is the reason this was an acceptable trade to make, and it is also the thing that stops being true
the moment a control plane runs for someone else.

## 2. The app layer the docs now specify

The 2026-08-23 pass replaced every `curl` example with a CLI, and specified a file format that does
not exist. This is the largest single gap on the list, and it is deliberate: the docs are the
design, and the design is what gets built against.

| The site says | Reality | Bead |
|---|---|---|
| `kubenest.yaml` describes an app; `kubenest deploy` applies it; `${component.export}` wires values and implies deploy order | No file format, no `deploy`, no interpolation. The CLI has `login`, `platform *`, `cluster set-window` and `backup *` and nothing else | `kn-xrxs` |
| `status`, `logs`, `open`, `exec`, `scale`, `pause`, `resume`, `deploys`, `rollback`, `diff`, `destroy`, `secret`, `project`, `addon`, `template` | None exist. The REST endpoints behind most of them do | `kn-xrxs` |
| `expose: true` yields a working HTTPS URL with no domain and no DNS configuration | Nothing generates a hostname; ingress requires a hostname you own | `kn-18c3` |
| `kubenest cluster set-domain` moves every exposed component and reissues certificates | Not a command | `kn-18c3` |
| `kubenest cluster connect` creates the record, mints the credential, installs the agent and waits | Not a command. The backend returns the string in cluster-create responses regardless | `kn-2mif`, `kn-887b` |
| `kubenest health` prints the fleet view | Not a command. The data and the verdicts exist behind the API | `kn-9pgx` |
| A component with a `port` gets a readiness probe and a rolling update that waits; `healthcheck:` overrides it | No probe is generated. A crash-looping image rolls out as a success | `kn-xrxs` (AA) |
| `${secret:NAME}` in the file, set by `kubenest secret set` through the hub | Component secrets exist in the API; there is no CLI verb and no reference syntax | `kn-xrxs` (AD) |
| `kubenest promote --from staging --to prod` moves the tested spec by digest | No such command. Nothing pins or carries a digest between projects | `kn-xrxs` (AC) |
| `kubenest login --token` and a `kubenest/deploy-action@v1` | `login` is device-flow only; no action is published. `kn-odqp` landed the revocable token behind it | `kn-xrxs` (Z) |
| The console can create, deploy, scale, roll back and promote — at parity with the CLI | The UI has app create, detail and deploys against the old API shapes; nothing speaks the new model, and promote has no screen | `kn-sb8z` (AE) |

One row went the other way. Per-component `cluster:` targeting was published as fact on
2026-08-23 and **withdrawn the same day** by decision AF: the docs now say an app is one cluster,
and `kn-u82w` removes the half-built backend path rather than finishing it. That is the spec-first
loop working as intended — the page forced the question, and the answer was to shrink the claim.

**`kn-xrxs` and `kn-18c3` together are the quickstart.** Neither the file nor the generated hostname
exists, so the page a first-time reader lands on is entirely specification today. They are the two
to build first, and `kn-xrxs` needs splitting before anyone starts.

## 3. Platform behaviour the site describes and the code does not do

| The site says | Reality | Bead |
|---|---|---|
| Maintenance windows govern when upgrades start and reboots are held | `kubenest cluster set-window` writes to a control-plane route that does not exist; the upgrade never reads one back, so the gate passes every cluster as unconfigured | `kn-nqj` |
| Ubuntu security patches apply under a policy the installer writes, with k3s held | The installer writes no APT policy and inherits the image's | `kn-nqj` |
| Reboots are coordinated one node at a time inside a window; livepatched nodes are not rebooted | kured is installed and pointed at a KubeNest sentinel that nothing yet creates, so no node has ever been rebooted by the platform | `kn-nqj` |
| A pending reboot warns at 7 days and goes critical at 14 | The cluster record carries no patch or reboot state, so there is nothing to evaluate | `kn-nqj` |
| `observability` and `secrets` install | Stage 11 refuses a component profile rather than installing core in its place | `kn-sev5`, `kn-ynaq` |
| Adding a profile to a running cluster runs through the upgrade path | Nothing adds a profile after install | `kn-avk0` |
| Each profile declares a backup set the drill covers | No such declaration exists | `kn-436i` |
| The three-node `ha` tier installs, upgrades and restores | Written and unit-tested; never run on three real machines. Decision U makes proving it a gate on the 1.0 release | `kn-kp3` |
| The drill verifies a rotating sample of real customer volumes and names what it verified | It restores the synthetic proof set only | `kn-odyo` |
| Datastore snapshot freshness is watched and alerts | The agent cannot read etcd membership or snapshot times from inside a pod, so `max-snapshot-age` is fed by nothing | `kn-hyl7` |
| `kubenest backup restore` restores a namespace or workload into a live cluster | A guarded stub that exits non-zero | `kn-x0wv` |
| The bundle-path gate refuses a hop of more than one bundle | Any forward hop is permitted | `kn-mtpf` |
| The deprecation scan reads the Git desired state, warning where live blocks | Live objects only | `kn-tczn` |
| Pre-flight refuses an upgrade that cannot finish inside its window | No estimate is computed | `kn-ght1` (needs `kn-nqj`) |
| The control plane accepts only in-window agents | Nothing enforces a compatibility window | `kn-opj8` |
| A CVE gets a patched bundle within 7 days on a 2-business-day assessment clock | No advisory feed meets that clock and no security-release runbook exists | `kn-eewa` |
| Rollback after the point of no return restores the datastore | Implemented and unit-tested only | `kn-1krv` |
| The console approves a `kubenest login` device code and issues CLI tokens | No such page | `kn-0d73` |
| Every configuration is tested together on every release | The compatibility matrix has never run | `kn-twe` |

## 4. App-layer behaviour the site describes and the code does not do

| The site says | Reality | Bead |
|---|---|---|
| `dsn` and `DATABASE_URL` are usable connection strings | The password segment is a literal `${postgres-password}` that nothing substitutes | `kn-kgu5` |
| A standalone addon instance can be referenced by `addon_instance_id` from an App | The CRD converter writes the instance UUID into a `component` key, so the create fails | `kn-l8z5` |
| Deleting a project removes the namespace and its workloads | Only the control-plane record is deleted; the namespace and Project CR keep running | `kn-ezf4` |
| A hub-dependent write either succeeds or fails visibly | A failed `project_create` send is swallowed and the record diverges silently | `kn-z7g7` |
| The API is rate limited | Enforcement is attached to one sample route; no usage endpoint, no `X-RateLimit-*` headers | `kn-3m3z` |
| `kubenest cluster connect` — the command the API returns | Not an implemented subcommand. The docs route around it by documenting the Helm path, so nothing on the site is wrong today; the API response still offers it | `kn-887b` |

**`kn-kgu5` is the one to fix first.** It is the only row where a reader following a documented
example gets a broken result immediately: the connection-string example on
[Deploying apps](/deploying) delivers placeholder text to the container.

## 5. Numbers the site quotes that need a measurement behind them

| Claim | Status | Bead |
|---|---|---|
| Host sizing floors and recommendations | Provisional in the manifest; preflight warns rather than fails against the recommendation | `kn-btk8` |
| `install-total`, `upgrade-per-node` and the health thresholds | Provisional. Two real figures exist — 4m14s install, 3m11s upgrade — and neither has replaced a deadline | `kn-btk8` |
| "We restore within X hours" on the `single-server` tier | Unmeasured at realistic data volume. Gate figures are proof-sized: 33s object+PVC restore, 17s datastore recovery from S3 | `kn-ze1` |

The manifest still carries `provisional: true` on `limits` and `health`; the published manifest
example no longer shows the flag. That is deliberate — the flag is a machine-readable marker for
us, not a caveat for a reader — but it means the two diverge until `kn-btk8` lands.

## 6. Design decisions

All 43 `OQ-*` questions are decided, and so is the app layer the docs specify.
`PLAN-BUILD-2026-08-20.md` carries the reasoning: §2 for A–G, §2a for H–Y, §2b for Z–AF. Nothing on
the docs site is waiting on a judgment call.

§2b also writes out the `kubenest.yaml` diff explicitly, so whoever builds `kn-xrxs` does not have
to re-derive the format from prose.

**Not in 1.x, decided rather than forgotten:** image building (`build_mode` in every form —
Shipwright is the named path when it returns, decision AB), per-component cluster targeting
(decision AF), replicated storage (decision N), and the `secrets-external` profile (decision M).

---

## Site structure

Eighteen pages, flat under `content/`, grouped by `_meta.global.tsx`:

```
Start     index · why · prerequisites · quickstart
Install   install · connect-cluster
Use       concepts · deploying · addons · console
Operate   day-2 · upgrades · backup-restore · ha · os-patching
Reference bundle · architecture · api
```

`day-2` is the page the product is actually sold on; the quickstart hands off to it explicitly,
because installing a cluster is the easy day. `why` carries the component rationale that used to be
buried in `bundle`, including why we are not using Kargo.

`content/api/index.mdx` keeps its directory on purpose: the backend's
`docs-route-compatibility.yml` workflow checks documented API routes against the live FastAPI route
table by that exact path, and moving the file breaks that guard.
