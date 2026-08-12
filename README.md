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
