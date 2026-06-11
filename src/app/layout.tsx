import { Footer, Layout, Navbar } from 'nextra-theme-docs'
import { Head } from 'nextra/components'
import { getPageMap } from 'nextra/page-map'
import 'nextra-theme-docs/style.css'
import type { ReactNode } from 'react'

export const metadata = {
  title: {
    template: '%s – KubeNest Docs',
    default: 'KubeNest Docs',
  },
  description:
    'Official documentation for KubeNest — the multi-cluster Kubernetes application platform.',
  metadataBase: new URL('https://docs.kubenest.io'),
}

export default async function RootLayout({ children }: { children: ReactNode }) {
  const pageMap = await getPageMap()
  return (
    <html lang="en" dir="ltr" suppressHydrationWarning>
      <Head faviconGlyph="☸" />
      <body>
        <Layout
          navbar={
            <Navbar
              logo={
                <span style={{ fontWeight: 700, fontSize: '1.1rem', letterSpacing: '-0.02em' }}>
                  ☸ KubeNest
                </span>
              }
              projectLink="https://github.com/kubenesthq"
            />
          }
          pageMap={pageMap}
          docsRepositoryBase="https://github.com/kubenesthq/docs/tree/main"
          editLink="Edit this page on GitHub"
          feedback={{ content: 'Question? Give us feedback →', labels: 'feedback' }}
          footer={
            <Footer>
              <span>© {new Date().getFullYear()} KubeNest. All rights reserved.</span>
            </Footer>
          }
          sidebar={{ defaultMenuCollapseLevel: 1 }}
          toc={{ float: true, backToTop: true }}
        >
          {children}
        </Layout>
      </body>
    </html>
  )
}
