// eslint-disable-next-line @typescript-eslint/no-explicit-any
import { useMDXComponents as getDocsMDXComponents } from 'nextra-theme-docs'
import { BuildStatus } from './components/build-status'

// Re-export nextra-theme-docs MDX components, plus our own.
//
// BuildStatus is registered globally on purpose. It marks pages describing
// unbuilt software, and a marker you can forget to import is a marker you will
// forget to add — which is the failure it exists to prevent. See
// lib/build-status.ts and `bun run check:status`.
//
// The any cast is needed because nextra-theme-docs and mdx/types have
// incompatible index signatures on MDXComponents.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function useMDXComponents(components: any = {}): any {
  return getDocsMDXComponents({ BuildStatus, ...components })
}
