---
sidebar_position: 3
title: GitOps Workflow
---

# GitOps Workflow

Kubenest uses GitOps as the foundation for all deployments. Every resource change is tracked in Git and synced to Kubernetes via ArgoCD.

## Why GitOps?

Traditional approaches use `kubectl apply` or direct API calls to modify Kubernetes resources. This creates several problems:

- **No Audit Trail**: Who made what change and when?
- **No Rollback**: Hard to revert to previous state
- **No CI/CD Integration**: Manual deployment steps
- **Drift Detection**: Cluster state diverges from desired state

GitOps solves these by making **Git the single source of truth**.

## The GitOps Flow

```
User Action → Backend → Hub → Operator → CRD → Git → ArgoCD → Kubernetes
                                          ↓
                                     Commit to Git
                                          ↓
                                    Pull Request (optional)
                                          ↓
                                     Merge to Main
                                          ↓
                                  ArgoCD Detects Change
                                          ↓
                                    Syncs to Cluster
```

## Step-by-Step Example

Let's trace a workload deployment through the GitOps workflow.

### Step 1: User Creates Workload

User submits a deployment via UI:

```json
{
  "name": "hello-world",
  "project_id": "project-abc",
  "source": {
    "type": "image",
    "image": {
      "repository": "nginx",
      "tag": "1.25-alpine"
    }
  },
  "runtime": {
    "replicas": 2
  }
}
```

### Step 2: Backend Stores Metadata

Backend creates database record:

```sql
INSERT INTO workloads (id, name, project_id, source_type, config, status)
VALUES (
  'workload-xyz',
  'hello-world',
  'project-abc',
  'image',
  '{"source": {...}, "runtime": {...}}',
  'pending'
);
```

### Step 3: Operator Creates CRD

Operator receives message and creates Workload CRD:

```yaml
apiVersion: kubenest.io/v1alpha1
kind: Workload
metadata:
  name: hello-world
  namespace: my-app
spec:
  source:
    type: image
    image:
      repository: nginx
      tag: 1.25-alpine
  runtime:
    replicas: 2
status:
  phase: Pending
```

### Step 4: Operator Generates Helm Chart

Operator reconciles the Workload CRD and generates Helm chart:

**Chart.yaml**:
```yaml
apiVersion: v2
name: hello-world
version: 1.0.0
appVersion: "1.25-alpine"
```

**values.yaml**:
```yaml
image:
  repository: nginx
  tag: 1.25-alpine
  pullPolicy: IfNotPresent

replicaCount: 2

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: true
  className: nginx
  hosts:
    - host: hello-world.example.com
      paths:
        - path: /
          pathType: Prefix
```

**templates/deployment.yaml**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Chart.Name }}
  labels:
    app: {{ .Chart.Name }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Chart.Name }}
  template:
    metadata:
      labels:
        app: {{ .Chart.Name }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        ports:
        - containerPort: 80
```

### Step 5: Commit to Git

Operator commits the Helm chart to Git repository:

```
deployments/
├── projects/
│   └── my-app/
│       ├── namespace.yaml
│       └── workloads/
│           └── hello-world/
│               ├── Chart.yaml
│               ├── values.yaml
│               └── templates/
│                   ├── deployment.yaml
│                   ├── service.yaml
│                   └── ingress.yaml
```

Git commit:
```bash
commit a1b2c3d4e5f6
Author: Kubenest Operator <operator@kubenest.io>
Date:   Tue Nov 26 10:30:00 2025 +0000

    Deploy workload: hello-world

    Project: my-app
    Workload ID: workload-xyz
    Source: nginx:1.25-alpine
    Replicas: 2
```

### Step 6: Create ArgoCD Application

Operator creates ArgoCD Application CRD:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: hello-world
  namespace: argocd
spec:
  project: my-app
  source:
    repoURL: https://github.com/org/deployments
    targetRevision: main
    path: projects/my-app/workloads/hello-world
  destination:
    server: https://kubernetes.default.svc
    namespace: my-app
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

### Step 7: ArgoCD Syncs

ArgoCD detects the new Application:

1. **Clone Git repo** and read Helm chart
2. **Render templates** with values.yaml
3. **Compare** rendered manifests with cluster state
4. **Sync** resources to cluster (create Deployment, Service, Ingress)
5. **Wait** for resources to be healthy
6. **Update** Application status to "Synced" and "Healthy"

### Step 8: Operator Updates Status

Operator watches ArgoCD Application status:

```yaml
status:
  phase: Running
  url: https://hello-world.example.com
  argocd:
    syncStatus: Synced
    health: Healthy
  conditions:
    - type: Ready
      status: "True"
      reason: DeploymentAvailable
      message: "Deployment has 2/2 replicas available"
```

Operator sends status update to Hub → Backend → UI.

### Step 9: User Sees Live Status

UI displays:
- **Status**: Running ✅
- **URL**: https://hello-world.example.com
- **Replicas**: 2/2
- **Last Deployed**: 2 minutes ago

## Git Repository Structure

```
deployments/
├── projects/
│   ├── project-abc/
│   │   ├── namespace.yaml
│   │   ├── resource-quota.yaml
│   │   ├── workloads/
│   │   │   ├── hello-world/
│   │   │   │   ├── Chart.yaml
│   │   │   │   ├── values.yaml
│   │   │   │   └── templates/
│   │   │   │       ├── deployment.yaml
│   │   │   │       ├── service.yaml
│   │   │   │       └── ingress.yaml
│   │   │   └── api-server/
│   │   │       └── ...
│   │   └── addons/
│   │       ├── postgres/
│   │       │   ├── Chart.yaml
│   │       │   └── values.yaml
│   │       └── redis/
│   │           └── ...
│   └── project-xyz/
│       └── ...
└── README.md
```

## ArgoCD Applications

Each Kubenest resource creates an ArgoCD Application:

| Resource Type | ArgoCD Application Name | Path |
|---------------|-------------------------|------|
| Project | `{project-name}-namespace` | `projects/{project-name}/namespace.yaml` |
| Workload | `{workload-name}` | `projects/{project-name}/workloads/{workload-name}` |
| Addon | `{addon-name}` | `projects/{project-name}/addons/{addon-name}` |
| StackDeploy | `{stack-name}` | `projects/{project-name}/stacks/{stack-name}` |

## Update Flow

When a workload is updated (e.g., scale to 5 replicas):

1. User clicks "Scale" in UI
2. Backend updates database: `status = scaling`
3. Operator receives `workload_scale` message
4. Operator updates Workload CRD: `spec.runtime.replicas = 5`
5. Operator updates `values.yaml` in Git: `replicaCount: 5`
6. Operator commits change:
   ```
   commit b2c3d4e5f6a7
   Author: Kubenest Operator
   Date:   Tue Nov 26 11:00:00 2025 +0000

       Scale workload: hello-world

       Replicas: 2 → 5
   ```
7. ArgoCD detects change and syncs
8. Deployment scales: 2 → 3 → 4 → 5 pods
9. Operator updates status: `phase = Running`, `replicas = 5`
10. UI updates: "5/5 replicas available"

## Deletion Flow

When a workload is deleted:

1. User clicks "Delete" in UI
2. Backend marks database record: `status = deleting`
3. Operator receives `workload_delete` message
4. Operator deletes Workload CRD
5. Operator deletes ArgoCD Application
6. ArgoCD deletes all resources (Deployment, Service, Ingress)
7. Operator deletes Helm chart from Git:
   ```
   commit c3d4e5f6a7b8
   Author: Kubenest Operator
   Date:   Tue Nov 26 12:00:00 2025 +0000

       Delete workload: hello-world

       Reason: User requested deletion
   ```
8. Operator updates status: `phase = Deleted`
9. Backend deletes database record
10. UI removes workload from list

## Rollback

Since everything is in Git, rollback is simple:

### Option 1: Git Revert

```bash
# Revert to previous commit
git revert HEAD
git push origin main

# ArgoCD automatically detects and syncs
```

### Option 2: ArgoCD Rollback

```bash
# Rollback to previous revision
argocd app rollback hello-world

# Or via UI: Applications → hello-world → History → Rollback
```

### Option 3: Kubenest Redeploy

```bash
# Redeploy to a specific version (stored in Git tag)
curl -X POST /v1/workloads/{id}/redeploy \
  -d '{"revision": "v1.0.0"}'
```

## Drift Detection

ArgoCD continuously monitors for drift:

**Scenario**: Someone manually edits the Deployment:

```bash
kubectl scale deployment hello-world --replicas=10 -n my-app
```

**What happens**:
1. ArgoCD detects drift: Cluster has 10 replicas, Git has 5
2. ArgoCD marks Application as "OutOfSync"
3. If `selfHeal: true`, ArgoCD automatically reverts to Git state (5 replicas)
4. If `selfHeal: false`, admin must manually sync

Operator watches ArgoCD Application status and reports drift to backend.

## Benefits of GitOps

### 1. Audit Trail

Every change is a Git commit:
- **Who**: Git author
- **What**: Diff of changes
- **When**: Commit timestamp
- **Why**: Commit message

```bash
# View deployment history
git log --oneline projects/my-app/workloads/hello-world/

# See what changed
git show a1b2c3d4e5f6
```

### 2. Disaster Recovery

Cluster destroyed? Rebuild from Git:

```bash
# Create new cluster
# Install ArgoCD
# Point ArgoCD to Git repo
# All resources automatically recreated
```

### 3. Multi-Environment

Same Git repo, different branches:

```
main          → Production
staging       → Staging
development   → Dev
```

ArgoCD Application per environment:

```yaml
# Production
targetRevision: main

# Staging
targetRevision: staging
```

### 4. Collaboration

Teams can review changes before deployment:

1. Operator commits to feature branch
2. Creates Pull Request
3. Team reviews Helm chart changes
4. Merge to main triggers deployment

### 5. Compliance

Git history provides compliance evidence:
- Change management records
- Approval workflows (via PR reviews)
- Separation of duties (PR approvers)

## Advanced: Multi-Cluster GitOps

For multiple clusters:

```
deployments/
├── clusters/
│   ├── production-us-east/
│   │   └── projects/
│   │       └── my-app/
│   ├── production-eu-west/
│   │   └── projects/
│   │       └── my-app/
│   └── staging/
│       └── projects/
│           └── my-app/
```

Each cluster has its own ArgoCD pointing to its directory.

## Troubleshooting

### Sync Failed

```bash
# Check ArgoCD Application status
kubectl get application hello-world -n argocd -o yaml

# View sync errors
argocd app get hello-world

# Manually sync
argocd app sync hello-world
```

### Git Conflicts

Operator handles merge conflicts by:
1. Pull latest from Git
2. Apply changes
3. Commit and push
4. If push fails (conflict): retry with rebase

### ArgoCD Not Detecting Changes

```bash
# Force refresh
argocd app get hello-world --refresh

# Check webhook configuration
kubectl get secret argocd-secret -n argocd -o yaml
```

## Best Practices

1. **Meaningful Commit Messages**: Include workload ID and reason
2. **Atomic Commits**: One resource change per commit
3. **Branch Protection**: Require PR reviews for production
4. **Automated Testing**: Run tests on PR before merge
5. **Signed Commits**: Use GPG signing for audit trail
