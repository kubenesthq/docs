// eslint-disable-next-line @typescript-eslint/no-explicit-any
import { useMDXComponents as getDocsMDXComponents } from 'nextra-theme-docs'

// Re-export nextra-theme-docs MDX components as-is.
// The any cast is needed because nextra-theme-docs and mdx/types have
// incompatible index signatures on MDXComponents.
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function useMDXComponents(components: any = {}): any {
  return getDocsMDXComponents(components)
}
