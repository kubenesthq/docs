---
sidebar_position: 2
title: Component Details
---

# System Components

Kubenest consists of four main components, each with distinct responsibilities and technologies.

## Backend API (FastAPI)

**Repository**: [kubenest-backend](https://github.com/kubenesthq/backend)
**Language**: Python 3.11+
**Framework**: FastAPI + SQLAlchemy (async) + ARQ

### Responsibilities

1. **User Management**
   - Authentication with JWT (access + refresh tokens)
   - Multi-tenant organization and team management
   - Role-based access control (RBAC)

2. **Cluster Registry**
   - Register new Kubernetes clusters
   - Generate install commands with cluster-specific JWT tokens
   - Track cluster connection status

3. **Resource Management**
   - CRUD operations for Projects, Workloads, Addons
   - Store resource metadata in PostgreSQL
   - Validate deployment configurations

4. **WebSocket Hub Client**
   - Maintain persistent WebSocket connection to Hub
   - Send deployment commands (`workload_deploy`, `addon_install`, etc.)
   - Receive status updates from operators

5. **SSE Streaming**
   - Broadcast real-time events to UI clients
   - Per-user event filtering
   - Connection management and heartbeats

6. **Background Jobs**
   - Resource cleanup (delete orphaned resources)
   - Metrics aggregation
   - Notification dispatch

### Technology Stack

```python
# Core
FastAPI              # Web framework
SQLAlchemy 2.0      # ORM with async support
Alembic             # Database migrations
Pydantic            # Data validation

# Database
asyncpg             # PostgreSQL async driver
Redis               # Caching and job queue

# Background Jobs
ARQ                 # Async task queue

# WebSocket
websockets          # WebSocket client

# Authentication
python-jose         # JWT encoding/decoding
passlib             # Password hashing
```

### API Endpoints (25 total)

See [API Reference](/docs/api) for complete documentation.

**Authentication** (4 endpoints):
- POST `/v1/auth/login` - User login
- POST `/v1/auth/register` - User registration
- POST `/v1/auth/refresh` - Refresh access token
- POST `/v1/auth/logout` - Logout

**Clusters** (5 endpoints):
- POST `/v1/clusters/register` - Register cluster
- GET `/v1/clusters` - List clusters
- GET `/v1/clusters/{id}` - Get cluster details
- DELETE `/v1/clusters/{id}` - Unregister cluster
- GET `/v1/clusters/{id}/install-command` - Get Helm install command

**Projects** (5 endpoints):
- POST `/v1/projects` - Create project
- GET `/v1/projects` - List projects
- GET `/v1/projects/{id}` - Get project details
- PATCH `/v1/projects/{id}` - Update project
- DELETE `/v1/projects/{id}` - Delete project

**Workloads** (6 endpoints):
- POST `/v1/workloads` - Deploy workload
- GET `/v1/workloads` - List workloads
- GET `/v1/workloads/{id}` - Get workload details
- PATCH `/v1/workloads/{id}/scale` - Scale workload
- POST `/v1/workloads/{id}/redeploy` - Trigger redeployment
- DELETE `/v1/workloads/{id}` - Delete workload

**Addons** (4 endpoints):
- POST `/v1/addons` - Install addon
- GET `/v1/addons` - List addons
- GET `/v1/addons/{id}` - Get addon details
- DELETE `/v1/addons/{id}` - Uninstall addon

**Events** (1 endpoint):
- GET `/v1/events` - SSE stream of real-time events

### Database Schema

```sql
-- Organizations (top-level tenant)
CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Users
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    org_id UUID REFERENCES organizations(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Clusters
CREATE TABLE clusters (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    org_id UUID REFERENCES organizations(id),
    status VARCHAR(50) DEFAULT 'disconnected',
    jwt_token VARCHAR(1024) NOT NULL,
    last_heartbeat TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Projects
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    cluster_id UUID REFERENCES clusters(id),
    org_id UUID REFERENCES organizations(id),
    namespace VARCHAR(253),
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Workloads
CREATE TABLE workloads (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    project_id UUID REFERENCES projects(id),
    source_type VARCHAR(50) NOT NULL,
    build_mode VARCHAR(50),
    status VARCHAR(50) DEFAULT 'pending',
    url VARCHAR(512),
    created_at TIMESTAMP DEFAULT NOW(),
    config JSONB NOT NULL
);

-- Addons
CREATE TABLE addons (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    project_id UUID REFERENCES projects(id),
    addon_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    connection_info JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    config JSONB NOT NULL
);
```

### Configuration

Environment variables (`.env`):

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/kubenest

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# WebSocket Hub
HUB_URL=ws://localhost:8081
HUB_RECONNECT_DELAY=5

# Redis
REDIS_URL=redis://localhost:6379

# Server
HOST=0.0.0.0
PORT=8080
```

---

## WebSocket Hub (Go)

**Repository**: [kubenest-hub](https://github.com/kubenesthq/hub)
**Language**: Go 1.21+
**Framework**: gorilla/websocket + Redis

### Responsibilities

1. **Connection Registry**
   - Track all connected operators (cluster_id → connection mapping)
   - Track backend connections
   - Store connection metadata in Redis

2. **Message Routing**
   - Route backend messages to specific operators by `cluster_id`
   - Broadcast operator messages to backend
   - Queue messages for disconnected operators

3. **Authentication**
   - Validate JWT tokens for operator and backend connections
   - Enforce cluster-specific access

4. **Health Monitoring**
   - Detect operator disconnections
   - Send reconnection prompts
   - Heartbeat mechanism

### Technology Stack

```go
// Core
gorilla/websocket    // WebSocket server
go-redis/redis       // Redis client

// Auth
golang-jwt/jwt       // JWT validation

// Utilities
uber-go/zap          // Structured logging
```

### Message Types

#### Backend → Operator

```json
{
  "type": "workload_deploy",
  "cluster_id": "cluster-abc123",
  "payload": {
    "workload_id": "workload-xyz",
    "name": "hello-world",
    "config": { ... }
  }
}
```

Message types:
- `workload_deploy` - Deploy new workload
- `workload_scale` - Scale existing workload
- `workload_delete` - Delete workload
- `addon_install` - Install addon
- `addon_delete` - Uninstall addon
- `project_create` - Create project/namespace

#### Operator → Backend

```json
{
  "type": "status_update",
  "cluster_id": "cluster-abc123",
  "payload": {
    "workload_id": "workload-xyz",
    "status": "Running",
    "phase": "Ready",
    "url": "https://hello-world.example.com"
  }
}
```

Message types:
- `status_update` - Resource status change
- `build_complete` - Image build finished
- `deployment_ready` - Deployment is healthy
- `error_report` - Error occurred
- `heartbeat` - Keep-alive ping

### Connection Flow

```
┌──────────┐                          ┌──────────┐
│ Operator │                          │ Backend  │
└────┬─────┘                          └────┬─────┘
     │                                     │
     │  WSS://hub:8081/operator            │  WSS://hub:8081/backend
     │  Authorization: Bearer <token>      │  Authorization: Bearer <token>
     │                                     │
     ├──────────────┐         ┌────────────┤
     │              ▼         ▼            │
     │        ┌─────────────────┐          │
     │        │   WebSocket Hub │          │
     │        │                 │          │
     │        │  1. Validate JWT│          │
     │        │  2. Register in │          │
     │        │     Redis       │          │
     │        │  3. Start routing          │
     │        └─────────────────┘          │
     │                                     │
```

### Configuration

Environment variables:

```bash
# Redis
REDIS_URL=redis://localhost:6379
REDIS_CONNECTION_POOL_SIZE=100

# JWT
JWT_SECRET=your-secret-key-here

# Server
PORT=8081
HOST=0.0.0.0

# WebSocket
WS_READ_BUFFER_SIZE=1024
WS_WRITE_BUFFER_SIZE=1024
WS_HEARTBEAT_INTERVAL=30s
WS_HEARTBEAT_TIMEOUT=90s
```

---

## Kubernetes Operator (Go)

**Repository**: [kubenest-operator](https://github.com/kubenesthq/operator)
**Language**: Go 1.21+
**Framework**: controller-runtime + Helm SDK

### Responsibilities

1. **CRD Management**
   - Reconcile 5 Custom Resource Definitions
   - Watch for CRD changes
   - Update status conditions

2. **GitOps Workflow**
   - Commit resource changes to Git
   - Create/update ArgoCD Applications
   - Monitor ArgoCD sync status

3. **Helm Deployments**
   - Unified Helm-based deployments for all resources
   - Template rendering
   - Release management

4. **WebSocket Client**
   - Connect to Hub on startup
   - Receive deployment commands
   - Broadcast status updates

5. **Resource Lifecycle**
   - Create: Namespace, RBAC, Secrets, Deployments, Services, Ingress
   - Update: Scale, redeploy, configuration changes
   - Delete: Cleanup resources, remove from Git

### Custom Resource Definitions

#### 1. Project CRD

```yaml
apiVersion: kubenest.io/v1alpha1
kind: Project
metadata:
  name: my-app
  namespace: kubenest-system
spec:
  namespace: my-app
  resourceQuota:
    cpu: "4"
    memory: "8Gi"
    pods: "20"
  registrySecrets:
    - name: docker-hub
      server: docker.io
      username: user
      password: pass
```

**Reconciliation**:
1. Create namespace
2. Create resource quota
3. Create registry secrets
4. Set up RBAC
5. Commit to Git → ArgoCD syncs

#### 2. Workload CRD

```yaml
apiVersion: kubenest.io/v1alpha1
kind: Workload
metadata:
  name: hello-world
  namespace: my-app
spec:
  source:
    type: git
    git:
      url: https://github.com/example/app
      branch: main
  build:
    mode: buildpack
    buildpack:
      builder: paketobuildpacks/builder:base
  runtime:
    replicas: 2
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
  networking:
    port: 3000
    expose: true
```

**Reconciliation**:
1. If build needed: Create BuildRequest CRD
2. Wait for image to be available
3. Generate Helm values
4. Commit to Git
5. Create ArgoCD Application
6. Monitor deployment status
7. Update Workload status

#### 3. Addon CRD

```yaml
apiVersion: kubenest.io/v1alpha1
kind: Addon
metadata:
  name: postgres
  namespace: my-app
spec:
  type: postgresql
  version: "15"
  config:
    database: myapp
    username: myapp_user
  resources:
    storage: 10Gi
    cpu: "1"
    memory: "2Gi"
```

**Reconciliation**:
1. Select Helm chart for addon type
2. Generate values from spec
3. Commit to Git
4. Create ArgoCD Application
5. Wait for deployment
6. Extract connection info (from Secret)
7. Update Addon status with connection details

#### 4. BuildRequest CRD

```yaml
apiVersion: kubenest.io/v1alpha1
kind: BuildRequest
metadata:
  name: hello-world-build-1
  namespace: my-app
spec:
  source:
    git:
      url: https://github.com/example/app
      branch: main
  builder:
    type: buildpack
    image: paketobuildpacks/builder:base
  destination:
    registry: registry.example.com
    repository: my-app/hello-world
    tag: v1.0.0
```

**Reconciliation**:
1. Create Kaniko or Buildpack Job
2. Mount source (Git)
3. Run build
4. Push image to registry
5. Update BuildRequest status

#### 5. StackDeploy CRD

```yaml
apiVersion: kubenest.io/v1alpha1
kind: StackDeploy
metadata:
  name: full-stack-app
  namespace: my-app
spec:
  components:
    - name: database
      type: addon
      addon:
        type: postgresql
    - name: backend
      type: workload
      workload:
        source:
          type: git
          git:
            url: https://github.com/example/backend
      imports:
        - from: database
          key: connection_string
          as: DATABASE_URL
    - name: frontend
      type: workload
      workload:
        source:
          type: git
          git:
            url: https://github.com/example/frontend
      imports:
        - from: backend
          key: url
          as: REACT_APP_API_URL
```

**Reconciliation**:
1. Topological sort of components (dependency order)
2. Deploy components sequentially
3. Wire exports between components
4. Update StackDeploy status

### Technology Stack

```go
// Controller Runtime
sigs.k8s.io/controller-runtime
k8s.io/client-go
k8s.io/api

// Helm
helm.sh/helm/v3

// Git
go-git/go-git

// WebSocket
gorilla/websocket

// ArgoCD
github.com/argoproj/argo-cd/v2/pkg/apiclient
```

### Configuration

Helm values:

```yaml
hub:
  url: ws://hub.kubenest.io:8081
  token: <JWT_TOKEN>

cluster:
  id: cluster-abc123

gitops:
  provider: argocd
  namespace: argocd
  repoUrl: https://github.com/org/deployments
  repoToken: <GITHUB_TOKEN>

image:
  repository: kubenest/operator
  tag: v1.0.0

replicas: 1

leaderElection:
  enabled: true
```

---

## Web UI (Next.js)

**Repository**: [kubenest-ui](https://github.com/kubenesthq/ui)
**Language**: TypeScript
**Framework**: Next.js 14+ (App Router) + React 19

### Responsibilities

1. **User Interface**
   - Dashboard with cluster and workload overview
   - Cluster management
   - Project and workload deployment wizards
   - Real-time status updates

2. **Authentication**
   - Login/logout
   - Token management (access + refresh)
   - Protected routes

3. **Real-Time Updates**
   - SSE connection to backend
   - Auto-update status badges
   - Toast notifications for events

4. **Forms & Validation**
   - Multi-step deployment wizard
   - Form validation with Zod
   - Error handling

### Technology Stack

```json
{
  "framework": "Next.js 14+",
  "ui": "Tailwind CSS + shadcn/ui",
  "state": "TanStack Query (React Query)",
  "forms": "React Hook Form + Zod",
  "api": "Fetch API with typed clients",
  "real-time": "EventSource (SSE)"
}
```

### Key Features

- **Dashboard**: Cluster health, workload counts, recent deployments
- **Cluster Management**: Register, view status, install commands
- **Deployment Wizard**: Git/image/buildpack modes with live preview
- **Status Visualization**: Phase indicators (Pending → Building → Deploying → Running)
- **Log Viewer**: Real-time logs from pods
- **Addon Marketplace**: Browse and install managed services

### Configuration

Environment variables (`.env.local`):

```bash
NEXT_PUBLIC_API_URL=http://localhost:8080/v1
NEXT_PUBLIC_SSE_URL=http://localhost:8080/v1/events
```

---

## Contracts Repository

**Repository**: [kubenest-contracts](https://github.com/kubenesthq/contracts)
**Format**: OpenAPI 3.0 + JSON Schema

### Contents

1. **OpenAPI Specification** (`api/openapi.yaml`)
   - Complete REST API documentation
   - Request/response schemas
   - Authentication requirements

2. **Event Schemas** (`events/*.json`)
   - WebSocket message definitions
   - Status update payloads

3. **CRD Definitions** (`crds/*.yaml`)
   - Kubernetes CRD YAML files
   - Copied from operator repository

4. **Code Generation** (`scripts/`)
   - TypeScript type generation for UI
   - Python Pydantic model generation for backend
   - Go struct generation for operator

### Usage

```bash
# Generate TypeScript types for UI
npm run generate:typescript

# Generate Python models for backend
npm run generate:python

# Generate Go structs for operator
npm run generate:go
```

This ensures type safety across all components.
