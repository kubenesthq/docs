import { Callout } from 'nextra/components'
import { SPEC_PAGES } from '../lib/build-status'

/**
 * Marks a page with behaviour that is not built yet.
 *
 * Put it directly under the H1, before any prose. It reads from the registry in
 * lib/build-status.ts rather than taking its text inline, so the claim and the
 * work that retires it stay in one place and cannot drift apart.
 *
 *   <BuildStatus path="/platform/upgrades" />
 */
export function BuildStatus({ path }: { path: string }) {
  const entry = SPEC_PAGES[path]

  // An unknown path is a bug in the page, not a reason to render nothing —
  // silence here would be the exact failure this component exists to prevent.
  if (!entry) {
    throw new Error(
      `<BuildStatus path="${path}" /> — no entry in SPEC_PAGES. ` +
        `Add one to src/lib/build-status.ts, or remove the marker if the page now describes shipped behaviour.`,
    )
  }

  return (
    <Callout type="warning">
      {entry.availability === 'partial' ? (
        <>
          <strong>Part of this page is not available yet.</strong> The page documents both shipped
          behaviour and open work. The exact boundary is below.
        </>
      ) : (
        <>
          <strong>This describes software that does not exist yet.</strong> The page is a
          specification, written in the present tense because it is what we are building to. It is
          not a description of anything you can run today.
        </>
      )}
      <br />
      <br />
      {entry.missing}
      {entry.today ? (
        <>
          <br />
          <br />
          <strong>What is true today:</strong> {entry.today}
        </>
      ) : null}
      <br />
      <br />
      Tracked as {entry.beads.map((b, i) => (
        <span key={b}>
          {i > 0 ? ', ' : ''}
          <code>{b}</code>
        </span>
      ))}
      . This notice remains until they close and the page is reverified against the implementation.
    </Callout>
  )
}
