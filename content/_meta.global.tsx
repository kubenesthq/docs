import type { MetaRecord } from 'nextra'

const meta: MetaRecord = {
  index: 'KubeNest',
  why: 'Why these choices',
  prerequisites: 'Prerequisites',
  quickstart: 'Quickstart',

  '-- install': { type: 'separator', title: 'Install' },
  install: 'Install the platform',
  'connect-cluster': 'Connect a cluster',

  '-- use': { type: 'separator', title: 'Use it' },
  concepts: 'Concepts',
  deploying: 'Deploying apps',
  addons: 'Addons and templates',
  console: 'Console',

  '-- operate': { type: 'separator', title: 'Operate it' },
  'day-2': 'Day 2',
  upgrades: 'Upgrades',
  'backup-restore': 'Backup and restore',
  ha: 'HA tiers',
  'os-patching': 'OS patching and reboots',

  '-- reference': { type: 'separator', title: 'Reference' },
  bundle: 'What is in the bundle',
  architecture: 'Architecture',
  api: 'API reference',
}

export default meta
