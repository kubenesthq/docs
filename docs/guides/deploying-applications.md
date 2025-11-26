---
sidebar_position: 2
title: Deploying Applications
---

# Deploying Applications

This guide covers different deployment scenarios and best practices.

## Deployment Scenarios

### 1. Deploy from Docker Hub

Simplest option for getting started:

```bash
curl -X POST /v1/workloads \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "nginx",
    "project_id": "project-abc",
    "source": {
      "type": "image",
      "image": {
        "repository": "nginx",
        "tag": "1.25-alpine"
      }
    },
    "networking": {
      "port": 80,
      "expose": true
    }
  }'
```

### 2. Deploy Node.js App from Git

Using Cloud Native Buildpacks (no Dockerfile needed):

```bash
curl -X POST /v1/workloads \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "nodejs-api",
    "project_id": "project-abc",
    "source": {
      "type": "git",
      "git": {
        "url": "https://github.com/yourorg/nodejs-api.git",
        "branch": "main"
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
      "env": [
        {"name": "NODE_ENV", "value": "production"},
        {"name": "PORT", "value": "3000"}
      ]
    },
    "networking": {
      "port": 3000,
      "expose": true
    }
  }'
```

### 3. Deploy with Custom Dockerfile

For applications with specific build requirements:

```bash
curl -X POST /v1/workloads \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "custom-app",
    "project_id": "project-abc",
    "source": {
      "type": "git",
      "git": {
        "url": "https://github.com/yourorg/app.git",
        "branch": "main"
      }
    },
    "build": {
      "mode": "dockerfile",
      "dockerfile": {
        "path": "./Dockerfile",
        "target": "production"
      }
    },
    "networking": {
      "port": 8080,
      "expose": true,
      "domain": "app.example.com"
    }
  }'
```

## Environment Variables

### Static Values

```json
{
  "env": [
    {"name": "LOG_LEVEL", "value": "info"},
    {"name": "API_URL", "value": "https://api.example.com"}
  ]
}
```

### From Secrets

First, create a Kubernetes secret:

```bash
kubectl create secret generic api-secrets \
  --from-literal=api_key=your-api-key \
  -n your-project
```

Then reference it:

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

### From Addons

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

## Resource Management

### Setting Resource Limits

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

### Auto-Scaling

```json
{
  "autoscaling": {
    "enabled": true,
    "minReplicas": 2,
    "maxReplicas": 10,
    "targetCPUUtilizationPercentage": 70
  }
}
```

## Health Checks

```json
{
  "healthCheck": {
    "liveness": {
      "httpGet": {
        "path": "/health",
        "port": 8080
      }
    },
    "readiness": {
      "httpGet": {
        "path": "/ready",
        "port": 8080
      }
    }
  }
}
```

## Best Practices

1. Always set resource requests and limits
2. Use health checks for production workloads
3. Run at least 2 replicas for high availability
4. Use specific image tags (not `latest`)
5. Store secrets in Kubernetes Secrets, not environment variables

See [Workloads Concept](/docs/concepts/workloads) for comprehensive documentation.
