# Kubenest Documentation

Official documentation for Kubenest - GitOps-driven Kubernetes Platform for Enterprise Self-Hosting.

Visit the live documentation at: [docs.kubenest.io](https://docs.kubenest.io)

## What's Inside

This documentation site is built with [Docusaurus 3](https://docusaurus.io/) and includes:

- **Getting Started Guides**: Installation and first deployment tutorials
- **Architecture Documentation**: System design and component details
- **Core Concepts**: Projects, Workloads, Addons, and Builds
- **User Guides**: Deployment patterns, addon management, monitoring
- **API Reference**: Auto-generated from OpenAPI specification

## Local Development

### Prerequisites

- Node.js 20.0 or higher
- npm or yarn

### Installation

```bash
npm install
```

### Start Development Server

```bash
npm start
```

This opens a browser window at `http://localhost:3000`. Most changes are reflected live without restarting the server.

### Build

```bash
npm run build
```

This generates static content into the `build` directory that can be served using any static hosting service.

### Serve Production Build Locally

```bash
npm run serve
```

## Project Structure

```
kubenest-docs/
├── docs/                           # Documentation content
│   ├── intro.md                    # Landing page
│   ├── getting-started/            # Installation and setup
│   │   ├── index.md
│   │   ├── installation.md
│   │   └── first-deployment.md
│   ├── architecture/               # System architecture
│   │   ├── overview.md
│   │   ├── components.md
│   │   └── gitops.md
│   ├── concepts/                   # Core concepts
│   │   ├── projects.md
│   │   ├── workloads.md
│   │   ├── addons.md
│   │   └── builds.md
│   ├── guides/                     # User guides
│   │   ├── cluster-registration.md
│   │   ├── deploying-applications.md
│   │   ├── managing-addons.md
│   │   └── monitoring.md
│   └── api/                        # API reference (auto-generated)
│       ├── index.md
│       └── *.api.mdx
├── src/                            # Custom React components and pages
│   ├── css/
│   │   └── custom.css
│   └── pages/
│       └── index.tsx
├── static/                         # Static assets
│   └── img/
├── docusaurus.config.ts            # Docusaurus configuration
├── sidebars.ts                     # Sidebar structure
└── package.json
```

## API Documentation

The API reference is automatically generated from the OpenAPI specification located at:

```
../kubenest-contracts/api/openapi.yaml
```

To regenerate the API documentation after updating the OpenAPI spec:

```bash
npx docusaurus gen-api-docs kubenest
```

## Configuration

### Docusaurus Config

Edit `docusaurus.config.ts` to modify:
- Site metadata (title, tagline, URL)
- Navigation bar
- Footer
- Theme settings
- Plugin configuration

### Sidebar Structure

Edit `sidebars.ts` to customize the documentation sidebar organization.

### OpenAPI Plugin

The OpenAPI plugin configuration in `docusaurus.config.ts`:

```typescript
plugins: [
  [
    'docusaurus-plugin-openapi-docs',
    {
      id: 'api',
      docsPluginId: 'classic',
      config: {
        kubenest: {
          specPath: '../kubenest-contracts/api/openapi.yaml',
          outputDir: 'docs/api',
          sidebarOptions: {
            groupPathsBy: 'tag',
          },
        },
      },
    },
  ],
],
```

## Deployment

### GitHub Pages

The documentation is configured for deployment to GitHub Pages:

```bash
npm run deploy
```

This builds the site and pushes to the `gh-pages` branch.

### Other Platforms

The static build can be deployed to any hosting platform:

- **Vercel**: Connect your repository and Vercel auto-deploys
- **Netlify**: Drag and drop the `build` folder or connect via Git
- **AWS S3**: Upload `build` folder to S3 bucket with static hosting
- **Cloudflare Pages**: Connect repository for automatic deployments

## Contributing

### Adding New Documentation

1. Create a new Markdown file in the appropriate directory under `docs/`
2. Add frontmatter with `sidebar_position` and `title`
3. Update `sidebars.ts` if creating a new section
4. Test locally with `npm start`
5. Build to verify: `npm run build`

### Updating API Documentation

1. Update the OpenAPI spec in `kubenest-contracts/api/openapi.yaml`
2. Regenerate API docs: `npx docusaurus gen-api-docs kubenest`
3. Review changes in `docs/api/`
4. Commit both the OpenAPI spec and generated docs

### Style Guide

- Use clear, concise language
- Include code examples for all concepts
- Add diagrams where helpful (use ASCII art or Mermaid)
- Use proper Markdown formatting
- Test all code examples before committing

## Related Repositories

- [Backend](https://github.com/kubenesthq/backend) - FastAPI control plane
- [Hub](https://github.com/kubenesthq/hub) - WebSocket message router
- [Operator](https://github.com/kubenesthq/operator) - Kubernetes operator
- [UI](https://github.com/kubenesthq/ui) - Next.js web console
- [Contracts](https://github.com/kubenesthq/contracts) - OpenAPI specs and schemas

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- [GitHub Issues](https://github.com/kubenesthq/docs/issues)
- [Kubenest Organization](https://github.com/kubenesthq)
- [Live Documentation](https://docs.kubenest.io)
