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
import { execFileSync } from 'node:child_process'
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

// Beads per entry, in registry order, so we can tell which page owns a stale one.
const entryBeads = new Map()
for (const [i, path] of specPaths.entries()) {
  const start = body.indexOf(`  '${path}':`)
  const end = i + 1 < specPaths.length ? body.indexOf(`  '${specPaths[i + 1]}':`) : body.length
  const block = body.slice(start, end)
  const arr = block.match(/beads:\s*\[([^\]]*)\]/)
  entryBeads.set(path, arr ? [...arr[1].matchAll(/'([^']+)'/g)].map((m) => m[1]) : [])
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

// 3. No entry cites a bead that has already closed.
//
// This is the failure the first two checks cannot see. A page stays marked, the
// marker still renders, CI stays green — and the entry quietly describes a gap
// that has since been filled. It happened twice on 2026-08-20 within six hours of
// the registry being written: kn-boj closed, and /platform/ha went from stale to
// flatly wrong ("no etcd anywhere") while every other check passed.
//
// A closed bead in `beads` is stale by definition: the array means "must close
// before this page is true". So closing one is the moment to revisit the entry —
// usually moving a line from `missing` to `today` — and then drop it from the
// array. When the array empties, the entry and its marker go together.
//
// Skipped where `br` is unavailable, which includes CI: the beads database lives
// in the parent workspace and is not part of this repo. Local runs and the
// pre-commit hook are where this bites, which is where the closing happens.
const allBeads = [...new Set([...entryBeads.values()].flat())]
if (allBeads.length) {
  // `br list -a` rather than `br show <ids>`: given an id it does not recognise,
  // `br show` returns a single error object for the whole call instead of the
  // rows it did find. That made one typo silently disable this entire check —
  // the parse threw, the catch treated it as "br unavailable", and the run went
  // green. Listing everything and looking ids up locally has no such cliff, and
  // an unknown id simply fails to appear.
  let statuses = null
  try {
    const out = execFileSync('br', ['list', '-a', '--json'], {
      cwd: root,
      encoding: 'utf8',
      stdio: ['ignore', 'pipe', 'ignore'],
    })
    const issues = JSON.parse(out).issues
    if (!Array.isArray(issues)) throw new Error('unexpected br list payload')
    statuses = new Map(issues.map((b) => [b.id, b.status]))
  } catch {
    console.log('check:status — bead freshness skipped (br unavailable or no beads database in reach).')
  }

  if (statuses) {
    for (const [path, beads] of entryBeads) {
      const closed = beads.filter((b) => statuses.get(b) === 'closed')
      const unknown = beads.filter((b) => !statuses.has(b))

      if (unknown.length) {
        errors.push(
          `${path} cites ${unknown.join(', ')}, which ${unknown.length > 1 ? 'do' : 'does'} not exist in the tracker. Fix the id, or drop it.`,
        )
      }
      if (closed.length && closed.length === beads.length) {
        errors.push(
          `${path} — every bead it cites has closed (${closed.join(', ')}). The software this page describes now exists: remove the entry from SPEC_PAGES and the <BuildStatus /> marker from the page, in the same change.`,
        )
      } else if (closed.length) {
        errors.push(
          `${path} cites ${closed.join(', ')}, already closed. Re-read the entry against what landed — usually a line moves from "missing" to "today" — then drop the closed bead from its beads array.`,
        )
      }
    }
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
