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
├── content/                        # All documentation, as MDX
│   ├── _meta.global.tsx            # Sidebar order and section titles
│   ├── index.mdx                   # Landing page
│   ├── getting-started/            # Installation, first deployment
│   ├── concepts/                   # Clusters, projects, apps, addons, stack templates
│   ├── architecture/               # System design, GitOps flow
│   ├── guides/                     # Task-oriented walkthroughs
│   └── api/                        # REST API reference
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

## The publication boundary — read this before writing a platform page

Some pages here describe software that **does not exist yet**. They were written as build
specifications, in the present tense, because that is what the implementation is built against.
That is fine, and it is also how a reader ends up believing we ship something we do not.

The rule: **a page whose subject is not built carries a `<BuildStatus />` marker, directly under
the H1.**

- The registry is [`src/lib/build-status.ts`](src/lib/build-status.ts). It maps the page to the
  beads that make it true, and to a plain statement of what is missing and what is true today.
- `<BuildStatus />` is registered globally in `src/mdx-components.tsx`, so there is no import to
  forget. It reads its text from the registry — never write the warning inline, or the page and
  the tracker will drift.
- `bun run check:status` enforces it in both directions: a registered page without a marker fails,
  and a marker on an unregistered page fails. It runs in CI on every branch and again before every
  deploy to `main`.

**When the work lands, delete the entry and the marker in the same change.** The registry is meant
to shrink to `{}` and then be deleted. If you find yourself editing a `missing:` line to make it
sound better rather than to make it accurate, stop.

Do not add an entry from a bead title. Check the code. Every current entry was verified against the
repositories on 2026-08-20 and is cited in `PLAN-BUILD-2026-08-20.md` §1 in the workspace root.

Separately, and not covered by this mechanism: the platform pages do not merge to `main` until
`kn-ze1` has verified them against a real cluster. The marker is for honesty, not for permission.

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
