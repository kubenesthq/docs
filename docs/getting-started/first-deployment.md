---
sidebar_position: 3
title: First Deployment
---

# Deploy Your First Application

This guide walks you through deploying your first application on Kubenest, from creating a project to accessing your running workload.

## Prerequisites

- Kubenest operator installed in your cluster ([Installation Guide](./installation.md))
- Cluster showing as "connected" in the Kubenest backend
- Access to the Kubenest API or UI

## Step 1: Create a Project

Projects in Kubenest are isolated namespaces with resource quotas and RBAC policies.

### Using the API

```bash
# Get your access token
TOKEN=$(curl -X POST http://localhost:8080/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access_token')

# Create a project
curl -X POST http://localhost:8080/v1/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-first-app",
    "cluster_id": "YOUR_CLUSTER_ID",
    "description": "My first Kubenest application"
  }' | jq
```

### Using the UI

1. Navigate to **Projects** → **Create New Project**
2. Enter project details:
   - **Name**: `my-first-app`
   - **Cluster**: Select your cluster
   - **Description**: `My first Kubenest application`
3. Click **Create Project**

### What Happens Behind the Scenes

When you create a project, the following occurs:

1. Backend creates a database record
2. Backend sends a `project_create` message to the Hub
3. Hub routes the message to the operator in your cluster
4. Operator creates a `Project` CRD
5. Operator reconciles: creates namespace, resource quotas, and RBAC
6. Operator commits changes to Git
7. ArgoCD syncs the namespace to your cluster
8. Status updates flow back: Operator → Hub → Backend → UI

You'll see the project status change: `Pending` → `Creating` → `Ready`

## Step 2: Deploy a Workload

Now let's deploy a simple Node.js application from a Git repository.

### Using the API

```bash
curl -X POST http://localhost:8080/v1/workloads \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "hello-world",
    "project_id": "PROJECT_ID_FROM_STEP_1",
    "source": {
      "type": "git",
      "git": {
        "url": "https://github.com/kubenest/examples.git",
        "branch": "main",
        "path": "hello-node"
      }
    },
    "build": {
      "mode": "buildpack",
      "buildpack": {
        "builder": "paketobuildpacks/builder:base"
      }
    },
    "runtime": {
      "replicas": 2,
      "resources": {
        "requests": {
          "cpu": "100m",
          "memory": "128Mi"
        },
        "limits": {
          "cpu": "500m",
          "memory": "512Mi"
        }
      }
    },
    "networking": {
      "port": 3000,
      "expose": true
    }
  }' | jq
```

### Using the UI

1. Navigate to your project → **Deploy Workload**
2. Enter workload configuration:

   **Source**:
   - **Source Type**: Git Repository
   - **Repository URL**: `https://github.com/kubenest/examples.git`
   - **Branch**: `main`
   - **Path**: `hello-node`

   **Build**:
   - **Build Mode**: Cloud Native Buildpack
   - **Builder**: `paketobuildpacks/builder:base`

   **Runtime**:
   - **Replicas**: `2`
   - **CPU Request**: `100m`
   - **Memory Request**: `128Mi`
   - **CPU Limit**: `500m`
   - **Memory Limit**: `512Mi`

   **Networking**:
   - **Port**: `3000`
   - **Expose Publicly**: Yes

3. Click **Deploy**

## Step 3: Monitor Deployment Progress

Watch your deployment progress through multiple phases:

### Deployment Phases

1. **Pending** - Workload CRD created, waiting for reconciliation
2. **Building** - Container image being built (if using buildpack/dockerfile)
3. **Deploying** - ArgoCD syncing resources to cluster
4. **Running** - Application pods are healthy and serving traffic

### Using the API

```bash
# Get workload status
curl -X GET http://localhost:8080/v1/workloads/WORKLOAD_ID \
  -H "Authorization: Bearer $TOKEN" | jq '.status'

# Stream real-time events (SSE)
curl -N http://localhost:8080/v1/events \
  -H "Authorization: Bearer $TOKEN"
```

### Using the UI

The UI automatically updates via Server-Sent Events (SSE). You'll see:

- Build logs (if applicable)
- Phase transitions
- Pod status
- Resource URLs

### Checking Resources in Kubernetes

```bash
# View the Workload CRD
kubectl get workloads.kubenest.io -n my-first-app

# View ArgoCD Application
kubectl get application -n argocd | grep hello-world

# View deployed resources
kubectl get all -n my-first-app

# Check pod logs
kubectl logs -n my-first-app -l app=hello-world
```

## Step 4: Access Your Application

Once the workload reaches `Running` status:

### Get the URL

```bash
# From API
curl -X GET http://localhost:8080/v1/workloads/WORKLOAD_ID \
  -H "Authorization: Bearer $TOKEN" | jq '.status.url'

# From Kubernetes
kubectl get ingress -n my-first-app
```

### Test the Application

```bash
# Get the URL from the workload status
URL=$(curl -s -X GET http://localhost:8080/v1/workloads/WORKLOAD_ID \
  -H "Authorization: Bearer $TOKEN" | jq -r '.status.url')

# Test the endpoint
curl $URL
# Expected output: Hello, World!
```

## Alternative Deployment Modes

### Deploy from Container Image

Instead of building from source, you can deploy a pre-built image:

```json
{
  "name": "nginx-app",
  "project_id": "PROJECT_ID",
  "source": {
    "type": "image",
    "image": {
      "repository": "nginx",
      "tag": "1.25-alpine"
    }
  },
  "runtime": {
    "replicas": 1,
    "resources": {
      "requests": {
        "cpu": "50m",
        "memory": "64Mi"
      }
    }
  },
  "networking": {
    "port": 80,
    "expose": true
  }
}
```

### Deploy from Dockerfile

Build an image from a Dockerfile in your Git repository:

```json
{
  "name": "custom-app",
  "project_id": "PROJECT_ID",
  "source": {
    "type": "git",
    "git": {
      "url": "https://github.com/yourorg/your-app.git",
      "branch": "main"
    }
  },
  "build": {
    "mode": "dockerfile",
    "dockerfile": {
      "path": "./Dockerfile",
      "context": ".",
      "target": "production"
    }
  },
  "runtime": {
    "replicas": 2
  },
  "networking": {
    "port": 8080,
    "expose": true
  }
}
```

## Managing Your Workload

### Scale the workload

```bash
curl -X PATCH http://localhost:8080/v1/workloads/WORKLOAD_ID/scale \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"replicas": 5}'
```

### Redeploy

Trigger a new deployment (useful after Git changes):

```bash
curl -X POST http://localhost:8080/v1/workloads/WORKLOAD_ID/redeploy \
  -H "Authorization: Bearer $TOKEN"
```

### View Logs

```bash
# Via kubectl
kubectl logs -n my-first-app -l app=hello-world --tail=100 -f

# Via API (coming soon)
curl http://localhost:8080/v1/workloads/WORKLOAD_ID/logs \
  -H "Authorization: Bearer $TOKEN"
```

### Delete the workload

```bash
curl -X DELETE http://localhost:8080/v1/workloads/WORKLOAD_ID \
  -H "Authorization: Bearer $TOKEN"
```

## Troubleshooting

### Workload stuck in "Pending"

Check the Workload CRD status:

```bash
kubectl describe workload hello-world -n my-first-app
```

Look for error messages in the status conditions.

### Build failing

View BuildRequest status:

```bash
kubectl get buildrequests -n my-first-app
kubectl describe buildrequest BUILDREQUEST_NAME -n my-first-app
```

Check build pod logs:

```bash
kubectl logs -n my-first-app -l job-name=BUILD_JOB_NAME
```

### ArgoCD sync issues

Check ArgoCD Application:

```bash
kubectl get application -n argocd hello-world -o yaml
```

View ArgoCD UI:

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
# Visit https://localhost:8080
```

### Pods not starting

```bash
# Check pod status
kubectl get pods -n my-first-app

# Describe pod
kubectl describe pod POD_NAME -n my-first-app

# Check events
kubectl get events -n my-first-app --sort-by='.lastTimestamp'
```

## Next Steps

Congratulations! You've successfully deployed your first application on Kubenest.

Now you can:

- **[Install Addons](/docs/concepts/addons)** - Add PostgreSQL, Redis, or other services
- **[Learn About Workloads](/docs/concepts/workloads)** - Deep dive into deployment modes
- **[Explore Monitoring](/docs/guides/monitoring)** - Set up observability
- **[API Reference](/docs/api)** - Complete API documentation

## Example Applications

Check out our [example repository](https://github.com/kubenest/examples) for more sample applications:

- Node.js Express API
- Python Flask application
- Go HTTP server
- Static React SPA
- Full-stack Next.js app
- Multi-service stack with database
