---
sidebar_position: 1
title: Projects
---

# Projects

Projects in Kubenest are isolated environments that map to Kubernetes namespaces. They provide resource isolation, RBAC boundaries, and organizational structure.

## What is a Project?

A **Project** is a logical grouping of workloads and addons within a specific Kubernetes cluster. Each project:

- Creates a dedicated Kubernetes namespace
- Enforces resource quotas (CPU, memory, storage)
- Manages access control (RBAC)
- Provides registry credentials for private images
- Groups related workloads together

## Project Hierarchy

```
Organization (Tenant)
  ├── Team A
  │   ├── Project: frontend (namespace: org-teamA-frontend)
  │   └── Project: backend (namespace: org-teamA-backend)
  └── Team B
      └── Project: analytics (namespace: org-teamB-analytics)
```

**Namespace Naming**: `{org-slug}-{team-slug}-{project-name}`

This ensures global uniqueness and tenant isolation.

## Creating a Project

### Via API

```bash
curl -X POST http://localhost:8080/v1/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-app",
    "cluster_id": "cluster-abc123",
    "description": "My application project",
    "resource_quota": {
      "cpu": "4",
      "memory": "8Gi",
      "storage": "100Gi",
      "pods": "20"
    },
    "registry_secrets": [
      {
        "name": "docker-hub",
        "server": "docker.io",
        "username": "myuser",
        "password": "mypassword"
      }
    ]
  }'
```

### Via UI

1. Navigate to **Projects** → **Create New Project**
2. Select cluster
3. Enter project details
4. Configure resource quotas
5. Add registry credentials (optional)
6. Click **Create**

### Project CRD

Behind the scenes, the operator creates a Project CRD:

```yaml
apiVersion: kubenest.io/v1alpha1
kind: Project
metadata:
  name: my-app
  namespace: kubenest-system
spec:
  namespace: org-team-my-app
  resourceQuota:
    cpu: "4"
    memory: "8Gi"
    storage: "100Gi"
    pods: "20"
  registrySecrets:
    - name: docker-hub
      server: docker.io
      username: myuser
      password: mypassword
status:
  phase: Creating
  conditions:
    - type: NamespaceCreated
      status: "False"
```

## What Gets Created

When a project is created, the operator:

### 1. Creates Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: org-team-my-app
  labels:
    kubenest.io/project: my-app
    kubenest.io/managed-by: kubenest
```

### 2. Sets Resource Quota

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: project-quota
  namespace: org-team-my-app
spec:
  hard:
    requests.cpu: "4"
    requests.memory: "8Gi"
    requests.storage: "100Gi"
    pods: "20"
    services: "10"
    configmaps: "50"
    secrets: "50"
```

### 3. Creates Registry Secrets

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: docker-hub
  namespace: org-team-my-app
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: <base64-encoded-credentials>
```

### 4. Sets Up RBAC

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: kubenest-deployer
  namespace: org-team-my-app
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: kubenest-deployer
  namespace: org-team-my-app
rules:
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  - apiGroups: [""]
    resources: ["pods", "services", "configmaps", "secrets"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: kubenest-deployer
  namespace: org-team-my-app
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: kubenest-deployer
subjects:
  - kind: ServiceAccount
    name: kubenest-deployer
    namespace: org-team-my-app
```

### 5. Commits to Git

```
deployments/
└── projects/
    └── org-team-my-app/
        ├── namespace.yaml
        ├── resource-quota.yaml
        ├── secrets/
        │   └── docker-hub.yaml
        └── rbac/
            ├── service-account.yaml
            ├── role.yaml
            └── role-binding.yaml
```

## Project Lifecycle

```
User Creates → Backend Stores → Operator Creates CRD → Reconciliation
                                        ↓
                            Create Namespace + RBAC + Secrets
                                        ↓
                                  Commit to Git
                                        ↓
                              ArgoCD Syncs to Cluster
                                        ↓
                                 Status: Ready
```

### Status Phases

1. **Pending**: Project created in database, waiting for operator
2. **Creating**: Operator creating namespace and resources
3. **Ready**: All resources created successfully
4. **Error**: Creation failed (check conditions for details)
5. **Deleting**: Project being deleted
6. **Deleted**: All resources removed

## Listing Projects

### Via API

```bash
curl -X GET http://localhost:8080/v1/projects \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
{
  "items": [
    {
      "id": "project-abc",
      "name": "my-app",
      "namespace": "org-team-my-app",
      "cluster_id": "cluster-abc123",
      "cluster_name": "production-us-east",
      "status": "Ready",
      "workload_count": 5,
      "addon_count": 2,
      "resource_usage": {
        "cpu": "2.5 / 4",
        "memory": "4Gi / 8Gi",
        "pods": "8 / 20"
      },
      "created_at": "2025-11-26T10:00:00Z"
    }
  ]
}
```

### Via kubectl

```bash
# List Project CRDs
kubectl get projects.kubenest.io -n kubenest-system

# Get project details
kubectl describe project my-app -n kubenest-system

# View namespace
kubectl get namespace org-team-my-app

# Check resource quota usage
kubectl get resourcequota -n org-team-my-app
kubectl describe resourcequota project-quota -n org-team-my-app
```

## Updating a Project

### Update Resource Quota

```bash
curl -X PATCH http://localhost:8080/v1/projects/project-abc \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "resource_quota": {
      "cpu": "8",
      "memory": "16Gi"
    }
  }'
```

Operator updates ResourceQuota in cluster and commits to Git.

### Add Registry Secret

```bash
curl -X PATCH http://localhost:8080/v1/projects/project-abc \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "registry_secrets": [
      {
        "name": "github-cr",
        "server": "ghcr.io",
        "username": "myuser",
        "password": "ghp_token"
      }
    ]
  }'
```

## Deleting a Project

```bash
curl -X DELETE http://localhost:8080/v1/projects/project-abc \
  -H "Authorization: Bearer $TOKEN"
```

### Deletion Flow

1. Backend marks project: `status = deleting`
2. Operator receives `project_delete` message
3. Operator deletes all Workload and Addon CRDs in project
4. Operator waits for workload/addon deletions to complete
5. Operator deletes Project CRD
6. Operator deletes namespace (cascades to all resources)
7. Operator removes project directory from Git
8. Backend deletes database record

**Warning**: Deleting a project deletes all workloads, addons, and data. This cannot be undone.

## Resource Quotas

Resource quotas prevent projects from consuming excessive cluster resources.

### Default Quotas

If not specified, default quotas are applied:

```yaml
cpu: "2"
memory: "4Gi"
storage: "50Gi"
pods: "10"
services: "5"
```

### Quota Enforcement

When a workload deployment exceeds quota:

1. Kubernetes rejects pod creation
2. Deployment remains in pending state
3. Operator detects quota error
4. Status updated: `phase = Error`, `reason = QuotaExceeded`
5. UI displays: "Insufficient resources. Increase project quota."

Example error:
```
Error creating pods: exceeded quota: project-quota,
requested: requests.cpu=2, used: requests.cpu=3, limited: requests.cpu=4
```

## Multi-Tenancy

Projects provide strong multi-tenancy:

### Database Isolation

```sql
-- Row-level security
CREATE POLICY org_isolation ON projects
  FOR ALL
  USING (org_id = current_setting('app.current_org_id')::uuid);
```

User can only see projects in their organization.

### Kubernetes Isolation

- **Namespace**: Each project has its own namespace
- **RBAC**: Service accounts scoped to namespace
- **Network Policies**: Restrict pod-to-pod communication
- **Resource Quotas**: Prevent resource hogging

### ArgoCD Isolation

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: my-app
  namespace: argocd
spec:
  sourceRepos:
    - 'https://github.com/org/deployments'
  destinations:
    - namespace: org-team-my-app
      server: https://kubernetes.default.svc
  # Restrict to specific namespace
  namespaceResourceWhitelist:
    - group: '*'
      kind: '*'
```

## Best Practices

### 1. Project Naming

Use descriptive names:
- ✅ `payment-service`
- ✅ `frontend-prod`
- ❌ `proj1`
- ❌ `test`

### 2. Resource Quotas

Set quotas based on workload needs:

**Small Project** (1-2 workloads):
```yaml
cpu: "2"
memory: "4Gi"
storage: "20Gi"
pods: "5"
```

**Medium Project** (3-10 workloads):
```yaml
cpu: "8"
memory: "16Gi"
storage: "100Gi"
pods: "20"
```

**Large Project** (10+ workloads):
```yaml
cpu: "32"
memory: "64Gi"
storage: "500Gi"
pods: "50"
```

### 3. Registry Secrets

- Store secrets securely (use Vault or Sealed Secrets)
- Rotate credentials regularly
- Use minimal permissions (read-only for pulling images)

### 4. Separation of Concerns

Create separate projects for:
- **Environment**: `frontend-prod`, `frontend-staging`
- **Team**: `team-a-services`, `team-b-services`
- **Application**: `auth-service`, `payment-service`

### 5. Monitoring

Track project resource usage:
```bash
# Via API
curl http://localhost:8080/v1/projects/project-abc/metrics

# Via kubectl
kubectl top pods -n org-team-my-app
kubectl describe resourcequota -n org-team-my-app
```

## Troubleshooting

### Project stuck in "Creating"

```bash
# Check Project CRD status
kubectl describe project my-app -n kubenest-system

# Check operator logs
kubectl logs -n kubenest-system -l app=kubenest-operator | grep my-app
```

Common issues:
- Git repository access denied (check credentials)
- Namespace already exists (delete manually)
- ArgoCD not ready (wait for ArgoCD)

### Quota errors

```bash
# View current usage
kubectl describe resourcequota -n org-team-my-app

# Increase quota
curl -X PATCH /v1/projects/project-abc \
  -d '{"resource_quota": {"cpu": "8"}}'
```

### Registry pull errors

```bash
# Check secret exists
kubectl get secret docker-hub -n org-team-my-app

# Test credentials
kubectl run test --image=myuser/myimage --dry-run=server -n org-team-my-app
```

## Advanced: Network Policies

Restrict network access between projects:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-from-other-namespaces
  namespace: org-team-my-app
spec:
  podSelector: {}
  policyTypes:
    - Ingress
  ingress:
    - from:
      - podSelector: {}  # Allow from same namespace only
```

This prevents pods in other projects from accessing your services.
