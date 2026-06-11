import nextra from 'nextra'

const withNextra = nextra({
  contentDirBasePath: '/',
})

export default withNextra({
  trailingSlash: true,
  images: { unoptimized: true },
})
