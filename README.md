# Kubenest Documentation

Official documentation for Kubenest — GitOps-driven Kubernetes platform for enterprise self-hosting.

Live at [docs.kubenest.io](https://docs.kubenest.io).

## Stack

Built with [Nextra 4](https://nextra.site/) on the Next.js App Router, using `bun` as the package manager. Content lives in `content/` as MDX and is routed by the catch-all page in `src/app/[[...mdxPath]]/page.tsx`.

The site is statically exported and published to GitHub Pages by `.github/workflows/deploy.yml` on every push to `main`.

## Local development

Requires Node.js 20+ and [bun](https://bun.sh/).

```bash
bun install
bun dev          # http://localhost:3000
bun run build    # static export into out/
bun run typecheck
```

## Project structure

```
kubenest-docs/
├── content/                        # All documentation, as MDX — 15 flat pages
│   ├── _meta.global.tsx            # Sidebar order and the five section headings
│   ├── index.mdx                   # Landing page
│   ├── prerequisites.mdx           # What you need: test and production
│   ├── quickstart.mdx              # One host to a running app
│   ├── install.mdx                 # kubenest platform install, in full
│   ├── connect-cluster.mdx         # A Kubernetes cluster you already run
│   ├── concepts.mdx                # The object model
│   ├── deploying.mdx               # Apps: deploy, wire, scale, roll back
│   ├── addons.mdx                  # Backing services and stack templates
│   ├── upgrades.mdx                # Gates, ordering, rollback
│   ├── backup-restore.mdx          # Backups and the restore drill
│   ├── ha.mdx                      # single-server versus ha
│   ├── os-patching.mdx             # Patches and reboot coordination
│   ├── bundle.mdx                  # Components, manifest, profiles, versioning
│   ├── architecture.mdx            # System design and the GitOps flow
│   └── api/index.mdx               # REST API reference — keeps its directory,
│                                   #   the backend route guard checks this path
├── OPEN-ITEMS.md                   # Where the code does not yet match the docs
├── src/
│   ├── app/
│   │   ├── layout.tsx              # Nextra theme layout, navbar, footer
│   │   └── [[...mdxPath]]/page.tsx # Catch-all MDX route
│   └── mdx-components.tsx          # MDX component overrides
└── next.config.ts                  # Nextra config + static export settings
```

## Adding a page

1. Create an `.mdx` file under the appropriate `content/` subdirectory.
2. Add `title` and `description` frontmatter.
3. If you are adding a new top-level section, add it to `content/_meta.global.tsx` — sidebar order comes from that file, not from filenames.
4. Verify with `bun run build`.

Within a section, page order also comes from `_meta.global.tsx`. Pages not listed there still render but fall to the end of the sidebar.

## API reference

`content/api/index.mdx` is written and maintained by hand. It is **not** generated from the OpenAPI spec — the Docusaurus OpenAPI plugin was dropped in the Nextra 4 migration.

This means it can drift from the backend. When you change routes in `kubenest-backend/app/api/v1/`, update the endpoint tables here in the same change. The canonical machine-readable reference is the live Swagger UI at `https://api.{your-domain}/docs`.

## The docs are the specification

The site describes KubeNest as it is meant to work. Where the implementation does not match, **the
implementation is what changes.** If it turns out it cannot, we come back and change the page
deliberately — as a decision, recorded with its reasoning — rather than bolting a disclaimer onto
it and moving on.

So: write the page as though the feature works. Do not add a "not built yet" note, a build-status
marker, or a callout explaining that an example fails today. A page full of hedges is a product
that has not been finished, and hiding that behind honest-sounding prose fixes nothing.

**Every gap goes in [`OPEN-ITEMS.md`](OPEN-ITEMS.md) instead**, which is the delta between what the
site says and what the code does. Add a row when a page makes a new claim; delete it when the code
catches up. Its first section is the security claims, kept separate because those are the rows
where the gap is a risk to a customer's cluster rather than a missing feature — and they gate the
first customer install.

Callouts are still right for things that are permanently true and easy to get wrong: a PATCH that
replaces a component wholesale, a Helm downgrade that cannot be reversed, a sealing key whose loss
is unrecoverable. The test is whether the warning would still be there once every bead is closed.

## Commit guard

This repo has an Agent Mail pre-commit and pre-push guard installed (`am guard status .`). It
blocks a commit that touches files another agent currently holds a reservation on — which is the
failure it exists to prevent: on 2026-08-20 four agents edited the same four platform pages at
once, and nothing noticed until the edits started failing against each other.

**If your commit is refused with "AGENT_NAME is unset and no current-pane identity could be
resolved":** you are committing from a plain shell rather than a registered agent pane. Either

```bash
AGENT_NAME=YourAgentName git commit ...   # if you hold an Agent Mail identity
AGENT_MAIL_BYPASS=1 git commit ...        # human commit, skip the guard
```

Agents running in registered tmux panes resolve their identity automatically and need neither.

To see who holds what: `am file_reservations list /data/projects/kubenest/kubenest-docs`.

## Deployment

Pushing to `main` triggers `.github/workflows/deploy.yml`, which builds the static export and publishes it to GitHub Pages at `docs.kubenest.io`. The custom domain is configured in the workflow via `public/CNAME`.

To deploy the built output elsewhere, `bun run build` produces a fully static site in `out/` that any static host will serve.

## Related repositories

- [kubenest-backend](https://github.com/kubenesthq/kubenest-backend) — FastAPI control plane
- [kubenest-hub](https://github.com/kubenesthq/kubenest-hub) — WebSocket message router
- [operator-v2](https://github.com/kubenesthq/operator-v2) — Kubernetes operator
- [kubenest-ui](https://github.com/kubenesthq/kubenest-ui) — Next.js web console
- [kubenest-contracts](https://github.com/kubenesthq/kubenest-contracts) — OpenAPI specs and shared schemas

## Support

- [GitHub Issues](https://github.com/kubenesthq/docs/issues)
- [Kubenest Organization](https://github.com/kubenesthq)
