# Diagram briefs — hand-drawn set for docs.kubenest.io

Nine sketches for the kubenest docs site (bead `kn-baj`). Each brief below is
written to be pasted into an image model more or less as-is. They are separated
by `---` dividers.

Screenshots of the UI are a separate effort and are not covered here.

## How to use this file

Prepend the **shared style block** to every prompt so the nine read as one set
rather than nine unrelated pictures. Then paste the individual brief.

Each entry lists the exact label text. Keep to those labels — the temptation is
to let the model add its own, and it will invent component names that do not
exist.

## Shared style block

> Back-of-the-napkin technical sketch, hand-drawn with a fine black felt-tip pen
> on off-white paper with a faint grain. Slightly wobbly hand-drawn boxes and
> arrows, visibly imperfect but confident and legible. Neat handwritten block
> capitals for labels. One single accent colour — a muted orange highlighter —
> used sparingly for emphasis only where the brief says so; everything else is
> black ink. No gradients, no drop shadows, no 3D, no icons from an icon set, no
> corporate flat-illustration look. Generous white space. Nothing cropped at the
> edges. The drawing should look like a senior engineer explaining a system at a
> whiteboard-turned-notebook, not like clip art.

## Practical notes

Image models garble handwritten text at small sizes. Three things help:

1. Keep the label count per drawing low — the briefs below are already pruned to
   the minimum, so resist adding more.
2. Generate at the largest size available, and prefer landscape unless the brief
   says otherwise.
3. Expect to re-letter. If a sketch has the right *layout* but mangled words, it
   is usually faster to keep it and fix the text in an editor than to reroll.

Files land in `kubenest-docs/public/images/`. The static export sets
`images.unoptimized`, so plain `<img>` tags in MDX are fine — no `next/image`
needed. Save as PNG with a transparent or paper-toned background that reads on
both light and dark theme; if the paper texture is opaque, that is acceptable
too, since a paper card on a dark page still looks deliberate.

---

## 1. System topology

**Goes on:** `content/architecture/index.mdx` (full version) and
`content/index.mdx` (simplified — see the variant note at the end).
**Replaces:** the large ASCII topology block in `architecture/index.mdx`.
**Canvas:** landscape, roughly 16:10.

Draw the five kubenest components as a vertical stack of hand-drawn boxes, top
to bottom, with a fleet of clusters fanning out at the bottom.

At the top, a wide box labelled **KUBENEST-UI** with a smaller subtitle line
inside it reading *Next.js console*. Below it, a second wide box labelled
**KUBENEST-BACKEND**, subtitle *FastAPI · Postgres · Redis*. Below that, a third
wide box labelled **KUBENEST-HUB**, subtitle *Go WebSocket broker*.

Between UI and backend, draw two parallel downward arrows: one labelled **HTTPS
REST**, one labelled **SSE (live status)** with the SSE arrow pointing *upward*
instead, so the pair reads as request going down and events streaming back up.

Between backend and hub, a single double-headed vertical arrow labelled **WSS
(persistent)**.

Below the hub, fan three arrows downward and outward to three smaller boxes
sitting side by side, each labelled **OPERATOR** with a subtitle underneath
reading *cluster A*, *cluster B*, *cluster C* respectively. Draw a dashed
hand-drawn enclosure around each operator box and label the enclosures
**CUSTOMER CLUSTER**.

Critically: draw each of these three arrows as originating at the operator and
pointing **up** into the hub, not down from the hub. Label the middle one
**operator dials out — nothing dials in**, and put that label in the orange
accent. This is the single most important thing the drawing must convey.

Under one operator box only (to avoid clutter), draw two short arrows going
down: one to a small box labelled **KUBERNETES API**, one to a small cylinder or
folder shape labelled **GIT**, with the Git arrow annotated *writes Helm values*.
From Git, draw a curving arrow back into the cluster enclosure ending at a small
box labelled **ARGOCD**, annotated *syncs*.

Finally, off to the right side and clearly detached from the flow — no arrows
into or out of it — draw a small box labelled **KUBENEST-CONTRACTS** with the
subtitle *JSON Schema · not a running service*, and a thin dashed leader line
pointing at the hub with the note *validates every event*.

**Must be legible at a glance:** the control plane never reaches into a customer
cluster; the cluster reaches out.

**Landing-page variant:** same drawing with the contracts box, the Kubernetes
API box, and the ArgoCD/Git detail all removed — just UI, backend, hub, and three
operators dialling out. Keep the orange *operator dials out* annotation.

---

## 2. Cluster registration and operator handshake

**Goes on:** `content/guides/cluster-registration.mdx` and
`content/concepts/clusters.mdx`.
**Replaces:** the ASCII sequence block in `concepts/clusters.mdx`.
**Canvas:** portrait or square — this is a tall sequence.

A hand-drawn sequence diagram with four vertical lifelines, evenly spaced, each
topped by a small box. Left to right, the four are: **YOU (CLI)**, **BACKEND**,
**HUB**, **OPERATOR**.

Draw horizontal arrows between lifelines, stacked top to bottom in this order:

1. YOU → BACKEND, labelled **POST /orgs/{id}/clusters**, with a small note under
   the arrow reading *no provider = bring your own cluster*.
2. BACKEND → YOU, a return arrow (draw it dashed), labelled **201 · cluster JWT
   + helm command**. Beside this arrow, in the margin, a small hand-drawn
   sticky-note shape containing **status: pending**.
3. A gap in the sequence with a horizontal dividing line across all lifelines,
   labelled in the middle **— you run the helm install —**.
4. OPERATOR → OPERATOR, a small self-looping arrow, labelled **reads JWT from
   Secret**.
5. OPERATOR → HUB, labelled **WSS connect + JWT**. Draw this arrow noticeably
   thicker than the others and put it in the orange accent.
6. HUB → HUB, a small self-loop, labelled **verify signature**.
7. HUB → BACKEND, labelled **cluster connected**.
8. A second margin sticky-note beside the backend lifeline at this height,
   containing **status: connected**.

The two sticky notes should visually rhyme so the reader's eye jumps between
them and reads the state change.

**Must be legible at a glance:** the operator initiates the connection, and the
cluster goes `pending → connected` with no inbound firewall rule anywhere in the
story.

**Do not** draw an arrow from the hub or backend down into the operator before
step 5. That inversion is the exact misconception this diagram exists to kill.

---

## 3. App deployment, end to end

**Goes on:** `content/architecture/gitops.mdx` and
`content/guides/creating-apps.mdx`.
**Replaces:** nothing directly — this is the missing overview that ties the
GitOps page together.
**Canvas:** wide landscape, roughly 16:9. The most detailed drawing in the set.

A horizontal swimlane sketch. Draw four horizontal bands separated by light
hand-ruled lines. Label the bands down the left edge, rotated or in the margin:
**UI**, **BACKEND**, **OPERATOR**, **CLUSTER**.

Work left to right as a single connected path that snakes down through the
bands:

In the **UI** band, start with a small box labelled **create app** and an arrow
heading right and down into the backend band.

In the **BACKEND** band: a box labelled **POST /apps → 202**, then an arrow
right to a small drum or cylinder labelled **record app** with a tag beside it
reading *phase: pending*, then an arrow right and down, crossing into the
operator band, labelled **command event via hub**.

In the **OPERATOR** band, a chain of four boxes connected left to right:
**StackDeploy CRD** → **render Helm values** → **commit to Git** → **upsert
ArgoCD App**. Under the *commit to Git* box, draw a small folder shape labelled
with the path fragment **.../apps/{app}/{component}/values.yaml** in smaller
handwriting.

In the **CLUSTER** band: an arrow down from *upsert ArgoCD App* into a box
labelled **ARGOCD SYNC**, then an arrow right to a cluster of three small circles
labelled **PODS RUNNING**.

Now the return path — draw this entire path in the orange accent so it is
visually distinct from the outbound path. From **PODS RUNNING**, an arrow going
back up and left, labelled **status event**, travelling up through the operator
band, through the backend band (passing a small tag reading *phase: deploying →
running*), and ending in the UI band at a box labelled **LIVE UPDATE (SSE)**.

The outbound path should read as a clean left-to-right descent and the return
path as a single sweeping arc back up to the top left.

**Must be legible at a glance:** the write path goes down through Git before it
touches the cluster, and status comes back up the same chain to the browser
without polling.

---

## 4. exportRef wiring

**Goes on:** `content/concepts/apps.mdx`.
**Replaces:** nothing — this section has no visual at all today.
**Canvas:** landscape, roughly 4:3.

Draw one large hand-drawn rounded enclosure labelled at the top **APP:
my-store**. Inside it, two boxes side by side.

Left box, labelled **postgres**, with a small tag in its corner reading *addon*.
Underneath, inside the box, a short list in smaller handwriting under a heading
**exports:** with two items: `connection_string` and `port`.

Right box, labelled **api**, with a corner tag reading *workload*. Underneath,
inside the box, a heading **env:** and one item: `DATABASE_URL`.

Draw a thick curving arrow from the `connection_string` line in the left box to
the `DATABASE_URL` line in the right box. Put this arrow in the orange accent.
Label it along its length **export_ref**, and add a smaller annotation beneath:
*operator resolves at reconcile time*.

Above the postgres box, a small hand-drawn starburst or callout containing
**password generated on first deploy — you never see it**.

Now, outside and below the App enclosure, draw a separate detached box labelled
**shared-db** with a corner tag reading *existing addon instance*. Draw a
second arrow from it up into the `DATABASE_URL` line, drawn dashed to contrast
with the solid one, and label it **export_ref by addon_instance_id**. Add a
short margin note beside it: *for addons outside this app*.

**Must be legible at a glance:** a value moves from one component to another
without any human handling the secret, and there are two ways to point at the
source — inside the app by name, outside it by ID.

---

## 5. Trust boundaries

**Goes on:** `content/architecture/index.mdx`.
**Replaces:** nothing — currently prose only.
**Canvas:** landscape, roughly 16:10.

Three large hand-drawn zones side by side, separated by two heavy vertical
dashed lines that clearly read as walls. Label the zones along the top:
**BROWSER**, **KUBENEST CONTROL PLANE**, **YOUR CLUSTER**.

In the BROWSER zone: a small box labelled **UI**.

In the CONTROL PLANE zone: two stacked boxes, **BACKEND** and **HUB**. Under the
backend box, write in smaller handwriting: *holds no kubeconfig · never calls
the K8s API*. Under the hub box: *routes by cluster id · does not interpret
payloads*.

In the YOUR CLUSTER zone: a box labelled **OPERATOR**, and beneath it a box
labelled **KUBERNETES API**, joined by a short arrow. Under the operator box, in
smaller handwriting: *the only component with cluster access*. Draw a small key
or padlock shape next to the operator labelled **cluster JWT (in a Secret)**.

Across each of the two dashed walls, draw exactly one arrow, and annotate what
crosses:

- Across the first wall (browser → control plane): a double-headed arrow
  labelled **REST + SSE**.
- Across the second wall (cluster → control plane): a single arrow pointing
  **left**, from the operator to the hub, labelled **outbound WSS only**. Put
  this arrow in the orange accent.

In the bottom margin, spanning the width, write one line in slightly larger
handwriting: **no inbound connection to your cluster, ever.**

**Must be legible at a glance:** the walls, and the fact that only one thin,
outbound thing crosses the second one.

**Do not** add any label suggesting the cluster JWT can be revoked or rotated
independently. It currently cannot — see bead `kn-i3c` — and the diagram should
not promise a property the system does not have.

---

## 6. GitOps repository layout

**Goes on:** `content/architecture/gitops.mdx`.
**Replaces:** complements the existing ASCII tree rather than replacing it — the
tree stays for copy-paste accuracy; this drawing shows what the tree *means*.
**Canvas:** landscape, roughly 4:3.

Left half of the drawing: a hand-drawn folder tree with the classic elbow
connectors, nested as follows, each level indented:

```
gitops-repo/
  clusters/
    {cluster-id}/
      namespaces/
        {project}/
          apps/
            my-store/
              web/     values.yaml
              postgres/ values.yaml
```

Draw the two `values.yaml` leaves as small page/document shapes rather than
plain text, so they stand out as the payload.

Right half: two stacked pairs of boxes. Top pair: a box labelled **ARGOCD APP:
web** with an arrow to a box labelled **HELM RELEASE: web**. Bottom pair: a box
labelled **ARGOCD APP: postgres** with an arrow to **HELM RELEASE: postgres**.

Now draw two long horizontal arrows from left to right, one from each
`values.yaml` document shape across to its matching ArgoCD App box. Draw these
two arrows in the orange accent and keep them clearly parallel and
non-crossing.

In the gap between the halves, write vertically or in a margin note: **one
values.yaml = one ArgoCD App = one Helm release**.

**Must be legible at a glance:** the one-to-one-to-one correspondence. The
parallel non-crossing arrows are doing the work here, so keep them clean.

---

## 7. Cluster connection state machine

**Goes on:** `content/concepts/clusters.mdx`.
**Replaces:** the ASCII state diagram.
**Canvas:** landscape, roughly 16:10.

A hand-drawn state diagram. Draw states as ovals, transitions as labelled
arrows.

Start with **pending** at the left. From it, draw two clearly divergent paths
that rejoin later:

- The **upper** path is a single long arrow from `pending` straight across to
  **connected**. Label this arrow **bring-your-own cluster**. Draw it in the
  orange accent.
- The **lower** path goes `pending` → **provisioning** → **awaiting_operator** →
  **connected**, three arrows through two intermediate ovals. Label the first
  arrow of this path **cloud-provisioned**.

Both paths must visibly converge on the same **connected** oval.

From `connected`, draw a downward arrow to an oval **disconnected**, labelled
*session lost*, and a return arrow from `disconnected` back up to `connected`
labelled *auto-reconnect*. The pair should read as a loop.

From `connected`, also draw an arrow to an oval **error** off to the right. Draw
a second arrow into `error` coming from `provisioning`.

Draw the two ovals `provisioning` and `awaiting_operator` with a light dashed
enclosure around just those two, tagged in the margin: **cloud-provisioned
clusters only**.

**Must be legible at a glance:** a BYO cluster never enters `awaiting_operator`.
The divergence of the two paths out of `pending` is the whole point of the
drawing.

---

## 8. App lifecycle phases

**Goes on:** `content/concepts/apps.mdx`.
**Replaces:** the ASCII phase diagram.
**Canvas:** landscape, roughly 16:10.

A hand-drawn state diagram, ovals and labelled arrows, reading left to right
along a main spine.

Main spine: **pending** → **deploying** → **running**. Draw these three ovals in
a straight horizontal line, evenly spaced, with the arrows between them plain
and unlabelled.

Below the spine, an oval **degraded**. Draw an arrow from `running` down to
`degraded`, labelled *component unhealthy*, and an arrow from `degraded` back up
to `running`, labelled *operator retries*. This should read as a recoverable
dip beneath the happy path.

To the right and below, an oval **failed**, drawn with a heavier double outline
to mark it terminal. Draw arrows into `failed` from `deploying` (labelled
*timeout*) and from `degraded` (labelled *gives up*).

Above the spine, draw a wide arc arrow that leaves `running`, loops up and back
to the left, and re-enters `deploying`. Label this arc **redeploy / patch /
rollback**. Put this arc in the orange accent.

**Must be legible at a glance:** `running` is not the end — the arc back to
`deploying` is what makes this a lifecycle rather than a pipeline. And
`degraded` returns to health while `failed` does not.

---

## 9. Drift detection

**Goes on:** `content/architecture/gitops.mdx`.
**Replaces:** nothing — currently prose only.
**Canvas:** landscape, roughly 16:10.

Top half of the drawing: two boxes side by side with a gap between them. Left
box labelled **DESIRED (GIT)**, containing a tiny hand-drawn snippet suggesting
YAML — three or four short indented lines with one line reading `replicas: 3`.
Right box labelled **LIVE (CLUSTER)**, containing a matching snippet where the
same line reads `replicas: 5`.

Circle the two differing `replicas` values and connect them with a short
double-headed arrow across the gap, labelled **operator compares**. Put the
circles and this arrow in the orange accent.

From that comparison, draw a single arrow downward that immediately forks into
two diverging arrows, splitting the bottom half of the drawing into a left and
a right branch.

Left branch ends in a box labelled **recoverable**. Inside or beneath it, two
short lines: *ArgoCD self-heals* and *informational only*. Draw a small tick or
checkmark beside this box.

Right branch ends in a box labelled **blocked_sync**. Inside or beneath it,
three short lines: *409 on writes*, *banner in UI*, *fix Git, then redeploy*.
Draw a small warning triangle beside this box.

Make the left branch visibly the wider, more travelled path — draw its arrow
thicker — and the right branch thinner, with a margin note beside it reading
*uncommon — someone edited Git or ArgoCD by hand*.

**Must be legible at a glance:** most drift heals itself; the rare kind that
does not will block your API writes until you resolve it.
