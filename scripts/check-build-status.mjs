#!/usr/bin/env node
/**
 * Enforces the publication boundary.
 *
 * Every page in SPEC_PAGES must carry its <BuildStatus /> marker, and no other
 * page may carry one. Both directions matter: the first stops unbuilt software
 * being published as shipped, the second stops a stale warning outliving the
 * work that justified it.
 *
 * Run by CI before any build. Exits non-zero with the specific file on failure.
 */
import { readFileSync, existsSync } from 'node:fs'
import { readdir } from 'node:fs/promises'
import { join, relative } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(fileURLToPath(new URL('.', import.meta.url)), '..')
const contentDir = join(root, 'content')

// Parse the registry without a TS toolchain: we only need the top-level keys,
// and importing TS from a plain node script would mean adding a build step to a
// check that has to be able to run before the build.
const registrySrc = readFileSync(join(root, 'src/lib/build-status.ts'), 'utf8')
const body = registrySrc.slice(registrySrc.indexOf('export const SPEC_PAGES'))
const specPaths = [...body.matchAll(/^ {2}'([^']+)':\s*\{/gm)].map((m) => m[1])

if (specPaths.length === 0) {
  console.error('check:status — parsed zero entries from SPEC_PAGES. The regex and the file have drifted apart; fix this script rather than deleting the check.')
  process.exit(1)
}

const pathToFile = (p) => join(contentDir, `${p.replace(/^\//, '')}.mdx`)

async function walk(dir) {
  const out = []
  for (const e of await readdir(dir, { withFileTypes: true })) {
    const full = join(dir, e.name)
    if (e.isDirectory()) out.push(...(await walk(full)))
    else if (e.name.endsWith('.mdx')) out.push(full)
  }
  return out
}

const errors = []
const MARKER = '<BuildStatus'

// 1. Every registered page exists and is marked.
for (const p of specPaths) {
  const file = pathToFile(p)
  if (!existsSync(file)) {
    errors.push(`${p} is in SPEC_PAGES but ${relative(root, file)} does not exist.`)
    continue
  }
  const src = readFileSync(file, 'utf8')
  if (!src.includes(MARKER)) {
    errors.push(
      `${relative(root, file)} describes unbuilt software (SPEC_PAGES has ${p}) but carries no <BuildStatus path="${p}" /> marker. Add it directly under the H1.`,
    )
  } else if (!src.includes(`path="${p}"`)) {
    errors.push(
      `${relative(root, file)} has a <BuildStatus /> marker with the wrong path. It must be path="${p}".`,
    )
  }
}

// 2. No unregistered page is marked.
for (const file of await walk(contentDir)) {
  const src = readFileSync(file, 'utf8')
  if (!src.includes(MARKER)) continue
  const p = '/' + relative(contentDir, file).replace(/\.mdx$/, '')
  if (!specPaths.includes(p)) {
    errors.push(
      `${relative(root, file)} carries a <BuildStatus /> marker but is not in SPEC_PAGES. If the software now exists, remove the marker; if it does not, add the entry.`,
    )
  }
}

if (errors.length) {
  console.error('\nPublication boundary check failed:\n')
  for (const e of errors) console.error(`  • ${e}`)
  console.error(
    '\nSee src/lib/build-status.ts. A page describing software we have not built must say so.\n',
  )
  process.exit(1)
}

console.log(`check:status — ${specPaths.length} specification pages, all marked correctly.`)
