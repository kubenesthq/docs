import type { MetaRecord } from 'nextra'

const meta: MetaRecord = {
  index: 'KubeNest',
  'getting-started': 'Getting Started',
  // kn-nlaf: day-2 platform docs, written as the build spec. Every page here is a DRAFT and
  // must not reach main until kn-ze1 has verified it against a real cluster.
  platform: {
    title: 'Platform (draft)',
    items: {
      install: 'Install the platform',
      bundle: 'What is in the bundle',
      profiles: 'Profiles',
      upgrades: 'Upgrades',
      'backup-restore': 'Backup and restore',
      'os-patching': 'OS patching and reboots',
      ha: 'HA tiers',
      'deploying-an-app': 'Deploying an app',
    },
  },
  concepts: 'Concepts',
  architecture: 'Architecture',
  guides: 'Guides',
  api: 'API Reference',
}

export default meta
