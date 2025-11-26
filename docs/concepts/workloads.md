---
sidebar_position: 2
title: Workloads
---

# Workloads

Workloads are the core deployable units in Kubenest. A workload represents a containerized application with its configuration, build settings, and runtime requirements.

## What is a Workload?

A **Workload** in Kubenest is an abstraction over Kubernetes Deployments, Services, and Ingresses. It provides a simplified interface for deploying applications without needing to write Kubernetes YAML.

Each workload consists of:
- **Source**: Where the application code/image comes from
- **Build**: How to build the container image (if applicable)
- **Runtime**: Resource requirements, replicas, environment variables
- **Networking**: Ports, ingress, service type

## Deployment Modes

Kubenest supports three deployment modes:

### 1. Container Image

Deploy a pre-built container image directly.

**Use case**: Deploy official images or images from your CI/CD pipeline.

```json
{
  "name": "nginx-app",
  "project_id": "project-abc",
  "source": {
    "type": "image",
    "image": {
      "repository": "nginx",
      "tag": "1.25-alpine",
      "pullPolicy": "IfNotPresent"
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
    "port": 80,
    "expose": true,
    "domain": "myapp.example.com"
  }
}
```

**Workflow**:
```
User submits → Backend stores → Operator creates Workload CRD →
Commits Helm chart to Git → ArgoCD deploys → Status: Running
```

No build phase needed.

### 2. Dockerfile

Build an image from a Dockerfile in your Git repository.

**Use case**: Custom builds with specific dependencies.

```json
{
  "name": "custom-api",
  "project_id": "project-abc",
  "source": {
    "type": "git",
    "git": {
      "url": "https://github.com/yourorg/api.git",
      "branch": "main",
      "path": "."
    }
  },
  "build": {
    "mode": "dockerfile",
    "dockerfile": {
      "path": "./Dockerfile",
      "context": ".",
      "target": "production",
      "args": {
        "NODE_ENV": "production"
      }
    }
  },
  "runtime": {
    "replicas": 3
  },
  "networking": {
    "port": 8080,
    "expose": true
  }
}
```

**Workflow**:
```
User submits → Backend stores → Operator creates Workload CRD →
Creates BuildRequest CRD → Kaniko builds image →
Image pushed to registry → Commits Helm chart to Git →
ArgoCD deploys → Status: Running
```

Build takes 2-5 minutes depending on image size.

### 3. Cloud Native Buildpacks

Automatically detect and build your application (no Dockerfile needed).

**Use case**: Standard apps (Node.js, Python, Go, Java, Ruby, etc.)

```json
{
  "name": "nodejs-app",
  "project_id": "project-abc",
  "source": {
    "type": "git",
    "git": {
      "url": "https://github.com/yourorg/nodejs-app.git",
      "branch": "main"
    }
  },
  "build": {
    "mode": "buildpack",
    "buildpack": {
      "builder": "paketobuildpacks/builder:base",
      "env": {
        "BP_NODE_VERSION": "20.*"
      }
    }
  },
  "runtime": {
    "replicas": 2
  },
  "networking": {
    "port": 3000,
    "expose": true
  }
}
```

**Supported Builders**:
- `paketobuildpacks/builder:base` - Node.js, Python, Go, Java, .NET, Ruby, PHP
- `paketobuildpacks/builder:full` - Base + additional languages
- `heroku/builder:22` - Heroku-compatible buildpacks

**Workflow**:
```
User submits → Backend stores → Operator creates Workload CRD →
Creates BuildRequest CRD → Buildpack auto-detects language →
Builds image → Pushes to registry → Commits Helm chart to Git →
ArgoCD deploys → Status: Running
```

## Workload Lifecycle

```
Pending → Building → Deploying → Running
           (skip if image mode)
```

### Status Phases

1. **Pending**: Workload CRD created, waiting for reconciliation
2. **Building**: Container image being built (dockerfile/buildpack modes)
3. **Deploying**: ArgoCD syncing resources to cluster
4. **Running**: All pods are healthy and serving traffic
5. **Error**: Deployment failed (see conditions for details)
6. **Scaling**: Replica count changing
7. **Updating**: Configuration update in progress
8. **Deleting**: Workload being removed

## Workload Configuration

### Runtime Configuration

```json
{
  "runtime": {
    "replicas": 3,
    "resources": {
      "requests": {
        "cpu": "100m",
        "memory": "128Mi"
      },
      "limits": {
        "cpu": "1000m",
        "memory": "1Gi"
      }
    },
    "env": [
      {
        "name": "NODE_ENV",
        "value": "production"
      },
      {
        "name": "DATABASE_URL",
        "valueFrom": {
          "secretKeyRef": {
            "name": "db-creds",
            "key": "connection_string"
          }
        }
      }
    ],
    "command": ["/app/start.sh"],
    "args": ["--port", "8080"],
    "healthCheck": {
      "httpGet": {
        "path": "/health",
        "port": 8080
      },
      "initialDelaySeconds": 10,
      "periodSeconds": 5
    }
  }
}
```

### Networking Configuration

```json
{
  "networking": {
    "port": 8080,
    "targetPort": 8080,
    "protocol": "TCP",
    "expose": true,
    "domain": "api.example.com",
    "tls": {
      "enabled": true,
      "secretName": "tls-cert"
    },
    "serviceType": "ClusterIP"
  }
}
```

**Service Types**:
- `ClusterIP`: Internal only (default)
- `LoadBalancer`: External load balancer (cloud providers)
- `NodePort`: Expose on node IP

### Storage Configuration

```json
{
  "storage": {
    "volumes": [
      {
        "name": "data",
        "persistentVolumeClaim": {
          "size": "10Gi",
          "storageClass": "standard"
        },
        "mountPath": "/data"
      },
      {
        "name": "config",
        "configMap": {
          "name": "app-config"
        },
        "mountPath": "/etc/config"
      }
    ]
  }
}
```

## Scaling Workloads

### Manual Scaling

```bash
curl -X PATCH /v1/workloads/{id}/scale \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"replicas": 5}'
```

Operator updates Workload CRD → Updates Helm values → Commits to Git → ArgoCD scales Deployment.

### Auto-Scaling (HPA)

```json
{
  "autoscaling": {
    "enabled": true,
    "minReplicas": 2,
    "maxReplicas": 10,
    "targetCPUUtilizationPercentage": 70,
    "targetMemoryUtilizationPercentage": 80
  }
}
```

Operator creates HorizontalPodAutoscaler:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app
  namespace: my-project
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

## Redeployment

Trigger a new deployment (useful after Git changes):

```bash
curl -X POST /v1/workloads/{id}/redeploy \
  -H "Authorization: Bearer $TOKEN"
```

**What happens**:
1. Operator updates Workload annotation: `kubenest.io/redeploy-at=<timestamp>`
2. Commits change to Git
3. ArgoCD detects change and triggers sync
4. Kubernetes performs rolling update

## Environment Variables

### Static Values

```json
{
  "env": [
    {"name": "LOG_LEVEL", "value": "info"},
    {"name": "PORT", "value": "8080"}
  ]
}
```

### From Secrets

```json
{
  "env": [
    {
      "name": "API_KEY",
      "valueFrom": {
        "secretKeyRef": {
          "name": "api-secrets",
          "key": "api_key"
        }
      }
    }
  ]
}
```

### From ConfigMaps

```json
{
  "env": [
    {
      "name": "CONFIG_FILE",
      "valueFrom": {
        "configMapKeyRef": {
          "name": "app-config",
          "key": "config.json"
        }
      }
    }
  ]
}
```

### From Addons (Export System)

When deploying a workload that depends on an addon:

```json
{
  "imports": [
    {
      "from": "postgres-addon",
      "key": "connection_string",
      "as": "DATABASE_URL"
    }
  ]
}
```

Operator fetches the exported value from the Addon status and injects it as an environment variable.

## Health Checks

### Liveness Probe

Restarts container if check fails:

```json
{
  "healthCheck": {
    "liveness": {
      "httpGet": {
        "path": "/health",
        "port": 8080
      },
      "initialDelaySeconds": 30,
      "periodSeconds": 10,
      "failureThreshold": 3
    }
  }
}
```

### Readiness Probe

Removes pod from service if check fails:

```json
{
  "healthCheck": {
    "readiness": {
      "httpGet": {
        "path": "/ready",
        "port": 8080
      },
      "initialDelaySeconds": 5,
      "periodSeconds": 5
    }
  }
}
```

### Startup Probe

For slow-starting applications:

```json
{
  "healthCheck": {
    "startup": {
      "httpGet": {
        "path": "/health",
        "port": 8080
      },
      "failureThreshold": 30,
      "periodSeconds": 10
    }
  }
}
```

## Viewing Workload Status

### Via API

```bash
curl -X GET /v1/workloads/{id} \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
{
  "id": "workload-xyz",
  "name": "my-app",
  "status": "Running",
  "phase": "Ready",
  "url": "https://my-app.example.com",
  "replicas": {
    "desired": 3,
    "ready": 3,
    "available": 3
  },
  "build": {
    "status": "Succeeded",
    "image": "registry.example.com/my-app:abc123"
  },
  "argocd": {
    "syncStatus": "Synced",
    "health": "Healthy"
  },
  "created_at": "2025-11-26T10:00:00Z",
  "updated_at": "2025-11-26T10:05:00Z"
}
```

### Via kubectl

```bash
# Get Workload CRD
kubectl get workload my-app -n my-project

# Describe Workload
kubectl describe workload my-app -n my-project

# Get Deployment
kubectl get deployment my-app -n my-project

# Get Pods
kubectl get pods -n my-project -l app=my-app

# View logs
kubectl logs -n my-project -l app=my-app --tail=100 -f
```

## Deleting Workloads

```bash
curl -X DELETE /v1/workloads/{id} \
  -H "Authorization: Bearer $TOKEN"
```

**Deletion flow**:
1. Operator deletes Workload CRD
2. Operator deletes ArgoCD Application
3. ArgoCD deletes Deployment, Service, Ingress
4. Operator removes Helm chart from Git
5. Backend deletes database record

## Best Practices

### Resource Requests & Limits

Always set both:

```json
{
  "resources": {
    "requests": {
      "cpu": "100m",
      "memory": "128Mi"
    },
    "limits": {
      "cpu": "1000m",
      "memory": "1Gi"
    }
  }
}
```

**Why**:
- Requests ensure scheduler places pod on node with capacity
- Limits prevent pod from consuming all node resources
- Missing limits can cause OOM kills

### Replica Count

- **Development**: 1 replica (saves resources)
- **Production**: 2+ replicas (high availability)
- **High traffic**: Enable autoscaling

### Health Checks

Always configure:
- **Liveness**: Restart unhealthy containers
- **Readiness**: Don't send traffic to unready pods
- **Startup**: Give slow apps time to start

### Build Optimization

**Dockerfile**:
- Use multi-stage builds
- Minimize layer count
- Use `.dockerignore`

**Buildpacks**:
- Pin builder version
- Set specific language version
- Use cache optimization

## Troubleshooting

### Build Failing

```bash
# Check BuildRequest status
kubectl get buildrequest -n my-project

# View build logs
kubectl logs -n my-project -l job-name=my-app-build
```

### Pods Crash Looping

```bash
# Check pod status
kubectl get pods -n my-project

# View pod logs
kubectl logs my-app-xyz -n my-project

# Describe pod
kubectl describe pod my-app-xyz -n my-project
```

### Ingress not working

```bash
# Check Ingress
kubectl get ingress -n my-project

# Describe Ingress
kubectl describe ingress my-app -n my-project

# Test service
kubectl port-forward svc/my-app -n my-project 8080:80
curl localhost:8080
```

### ArgoCD out of sync

```bash
# Check Application
kubectl get application my-app -n argocd

# Sync manually
argocd app sync my-app
```
