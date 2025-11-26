---
sidebar_position: 2
title: Operator Installation
---

# Installing the Kubenest Operator

The Kubenest Operator runs in your Kubernetes cluster and manages the lifecycle of your applications through Custom Resource Definitions (CRDs).

## Prerequisites

- Kubernetes cluster v1.24 or later
- `kubectl` configured with cluster-admin access
- Helm v3 installed
- Kubenest Backend and Hub running and accessible

## Step 1: Register Your Cluster

First, register your cluster with the Kubenest backend to get an installation command with a unique JWT token.

### Using the API

```bash
# Login to get access token
TOKEN=$(curl -X POST http://localhost:8080/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access_token')

# Register cluster
curl -X POST http://localhost:8080/v1/clusters/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "production-cluster",
    "description": "Production Kubernetes cluster"
  }' | jq
```

### Using the UI

1. Navigate to the Kubenest UI
2. Go to **Clusters** → **Register New Cluster**
3. Enter cluster name and description
4. Click **Generate Install Command**

You'll receive a Helm install command with a pre-configured JWT token.

## Step 2: Install ArgoCD (if not already installed)

Kubenest uses ArgoCD for GitOps deployments. If you don't have ArgoCD installed:

```bash
# Create namespace
kubectl create namespace argocd

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for ArgoCD to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server -n argocd --timeout=300s
```

## Step 3: Install the Operator

Use the Helm command generated during cluster registration:

```bash
# Add Kubenest Helm repository
helm repo add kubenest https://charts.kubenest.io
helm repo update

# Install the operator
helm install kubenest-operator kubenest/operator \
  --namespace kubenest-system \
  --create-namespace \
  --set hub.url=ws://your-hub-url:8081 \
  --set hub.token=YOUR_JWT_TOKEN_HERE \
  --set cluster.id=YOUR_CLUSTER_ID
```

### Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| `hub.url` | WebSocket Hub URL | Required |
| `hub.token` | JWT token for authentication | Required |
| `cluster.id` | Unique cluster identifier | Required |
| `gitops.provider` | GitOps provider (argocd) | `argocd` |
| `gitops.namespace` | ArgoCD namespace | `argocd` |
| `gitops.repoUrl` | Git repository URL for deployments | Required |
| `gitops.repoToken` | Git repository access token | Optional |
| `image.repository` | Operator image repository | `kubenest/operator` |
| `image.tag` | Operator image tag | Chart version |
| `replicas` | Number of operator replicas | `1` |

### Example with Git Repository

```bash
helm install kubenest-operator kubenest/operator \
  --namespace kubenest-system \
  --create-namespace \
  --set hub.url=ws://hub.kubenest.io:8081 \
  --set hub.token=eyJhbGciOiJIUzI1NiIs... \
  --set cluster.id=cluster-abc123 \
  --set gitops.repoUrl=https://github.com/yourorg/kubenest-deployments \
  --set gitops.repoToken=ghp_your_github_token
```

## Step 4: Verify Installation

Check that the operator is running:

```bash
# Check operator pod status
kubectl get pods -n kubenest-system

# Expected output:
# NAME                                  READY   STATUS    RESTARTS   AGE
# kubenest-operator-5d8f9c6b7d-abcde   1/1     Running   0          2m

# Check operator logs
kubectl logs -n kubenest-system -l app=kubenest-operator

# Verify CRDs are installed
kubectl get crds | grep kubenest.io
```

You should see these Custom Resource Definitions:

- `projects.kubenest.io`
- `workloads.kubenest.io`
- `addons.kubenest.io`
- `buildrequests.kubenest.io`
- `stackdeploys.kubenest.io`

## Step 5: Verify Connectivity

Check that the operator has connected to the Hub:

```bash
# Check operator logs for connection messages
kubectl logs -n kubenest-system -l app=kubenest-operator | grep "Connected to hub"

# In the backend, list connected clusters
curl -X GET http://localhost:8080/v1/clusters \
  -H "Authorization: Bearer $TOKEN" | jq
```

The cluster should show `status: "connected"`.

## Troubleshooting

### Operator pod not starting

```bash
# Check pod events
kubectl describe pod -n kubenest-system -l app=kubenest-operator

# Check operator logs
kubectl logs -n kubenest-system -l app=kubenest-operator
```

Common issues:
- Invalid JWT token (check `hub.token` value)
- Hub URL not accessible from cluster
- Missing RBAC permissions

### CRDs not installed

```bash
# Manually install CRDs
helm template kubenest-operator kubenest/operator | kubectl apply -f -
```

### ArgoCD integration not working

```bash
# Verify ArgoCD is running
kubectl get pods -n argocd

# Check ArgoCD API access
kubectl exec -n kubenest-system deploy/kubenest-operator -- \
  curl -k https://argocd-server.argocd.svc.cluster.local
```

### Git repository access issues

```bash
# Test Git credentials
kubectl create secret generic git-test \
  --from-literal=token=$GITHUB_TOKEN \
  -n kubenest-system

# Check if operator can access repository
kubectl logs -n kubenest-system -l app=kubenest-operator | grep "repository"
```

## Uninstallation

To remove the operator:

```bash
# Uninstall Helm release
helm uninstall kubenest-operator -n kubenest-system

# Remove namespace
kubectl delete namespace kubenest-system

# Remove CRDs (WARNING: This deletes all Kubenest resources)
kubectl delete crd projects.kubenest.io
kubectl delete crd workloads.kubenest.io
kubectl delete crd addons.kubenest.io
kubectl delete crd buildrequests.kubenest.io
kubectl delete crd stackdeploys.kubenest.io
```

## Next Steps

Now that the operator is installed:

1. **[Deploy Your First Application](./first-deployment.md)** - Create a project and deploy a workload
2. **[Learn About Projects](/docs/concepts/projects)** - Understand namespace isolation
3. **[Explore Workloads](/docs/concepts/workloads)** - Different deployment modes

## Advanced Configuration

### High Availability

For production environments, run multiple operator replicas:

```bash
helm upgrade kubenest-operator kubenest/operator \
  --namespace kubenest-system \
  --reuse-values \
  --set replicas=3 \
  --set leaderElection.enabled=true
```

### Custom Resource Limits

```bash
helm upgrade kubenest-operator kubenest/operator \
  --namespace kubenest-system \
  --reuse-values \
  --set resources.limits.cpu=500m \
  --set resources.limits.memory=512Mi \
  --set resources.requests.cpu=100m \
  --set resources.requests.memory=128Mi
```

### Webhook Configuration

Enable validating and mutating webhooks:

```bash
helm upgrade kubenest-operator kubenest/operator \
  --namespace kubenest-system \
  --reuse-values \
  --set webhook.enabled=true \
  --set webhook.certManager.enabled=true
```
