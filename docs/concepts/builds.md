---
sidebar_position: 4
title: Container Builds
---

# Container Builds

Kubenest can build container images from your source code using Dockerfile or Cloud Native Buildpacks.

## Build Modes

### 1. Dockerfile Build

Uses Kaniko to build images from Dockerfiles inside Kubernetes (no Docker daemon required).

**Configuration**:
```json
{
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
  }
}
```

### 2. Buildpack Build

Auto-detects your application type and builds an optimized image.

**Configuration**:
```json
{
  "build": {
    "mode": "buildpack",
    "buildpack": {
      "builder": "paketobuildpacks/builder:base",
      "env": {
        "BP_NODE_VERSION": "20.*"
      }
    }
  }
}
```

## Build Process

```
Workload CRD → BuildRequest CRD → Kaniko/Buildpack Job →
Image Built → Pushed to Registry → Build Status Updated
```

### BuildRequest CRD

```yaml
apiVersion: kubenest.io/v1alpha1
kind: BuildRequest
metadata:
  name: my-app-build-1
  namespace: my-project
spec:
  source:
    git:
      url: https://github.com/org/app
      branch: main
  builder:
    type: buildpack
    image: paketobuildpacks/builder:base
  destination:
    registry: registry.example.com
    repository: my-app
    tag: abc123
status:
  phase: Building
  startTime: "2025-11-26T10:00:00Z"
```

## Build Cache

Kubenest caches build layers to speed up subsequent builds:
- Dockerfile: Layer caching via Kaniko
- Buildpacks: Cache volumes for dependencies

## Troubleshooting

**Build fails**:
```bash
kubectl get buildrequest -n my-project
kubectl logs -n my-project -l job-name=my-app-build
```

**Common issues**:
- Missing dependencies in Dockerfile
- Network timeout (pulling base images)
- Registry authentication failed
