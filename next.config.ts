import nextra from 'nextra'

const withNextra = nextra({
  contentDirBasePath: '/',
})

export default withNextra({
  // Static export — the site is served from GitHub Pages, which has no Node runtime.
  output: 'export',
  // Pages serves /foo/ as /foo/index.html, so every route needs a trailing slash.
  trailingSlash: true,
  images: { unoptimized: true },
})
