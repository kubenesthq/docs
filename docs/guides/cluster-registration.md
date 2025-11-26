---
sidebar_position: 1
title: Cluster Registration
---

# Cluster Registration

Learn how to register a Kubernetes cluster with Kubenest and install the operator.

## Prerequisites

- Kubernetes cluster v1.24+ with cluster-admin access
- `kubectl` configured to access your cluster
- `helm` v3 installed
- Kubenest backend and hub running

## Step 1: Register Cluster via API

```bash
TOKEN=$(curl -X POST http://localhost:8080/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access_token')

curl -X POST http://localhost:8080/v1/clusters/register \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "production-us-east",
    "description": "Production cluster in US East"
  }'
```

Response includes cluster ID and JWT token.

## Step 2: Get Install Command

```bash
curl -X GET http://localhost:8080/v1/clusters/{cluster_id}/install-command \
  -H "Authorization: Bearer $TOKEN"
```

Returns a Helm command pre-configured with your cluster's JWT token.

## Step 3: Install Operator

Run the Helm command from step 2:

```bash
helm repo add kubenest https://charts.kubenest.io
helm repo update

helm install kubenest-operator kubenest/operator \
  --namespace kubenest-system \
  --create-namespace \
  --set hub.url=ws://your-hub-url:8081 \
  --set hub.token=YOUR_JWT_TOKEN \
  --set cluster.id=YOUR_CLUSTER_ID \
  --set gitops.repoUrl=https://github.com/yourorg/deployments \
  --set gitops.repoToken=YOUR_GITHUB_TOKEN
```

## Step 4: Verify

```bash
# Check operator pod
kubectl get pods -n kubenest-system

# Check CRDs
kubectl get crds | grep kubenest.io

# Verify connection in backend
curl http://localhost:8080/v1/clusters/{cluster_id} \
  -H "Authorization: Bearer $TOKEN"
# Should show status: "connected"
```

## Troubleshooting

See [Installation Guide](/docs/getting-started/installation) for detailed troubleshooting steps.
