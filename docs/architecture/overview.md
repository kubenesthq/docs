---
sidebar_position: 1
title: Architecture Overview
---

# Kubenest Architecture

Kubenest is built on a distributed architecture that separates concerns between control plane, message routing, and cluster-side operations.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Control Plane                            │
│  ┌─────────┐     REST API    ┌─────────────┐                   │
│  │   UI    │ ───────────────→│   Backend   │                   │
│  │ Next.js │      SSE        │  FastAPI    │                   │
│  └─────────┘ ←───────────────└──────┬──────┘                   │
│                                      │                           │
│                                      ├─→ PostgreSQL              │
│                                      │   (Multi-tenant DB)       │
│                                      │                           │
│                                      └─→ Redis (Background Jobs) │
└──────────────────────────────────────┬──────────────────────────┘
                                        │ WebSocket
                                        ↓
                        ┌───────────────────────────┐
                        │    WebSocket Hub (Go)     │
                        │  Message Router & Broker  │
                        └───────────┬───────────────┘
                                    │ Redis (Connection Registry)
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
            WebSocket              WebSocket      WebSocket
                    │               │               │
                    ↓               ↓               ↓
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │  Operator    │  │  Operator    │  │  Operator    │
        │  Cluster 1   │  │  Cluster 2   │  │  Cluster N   │
        └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
               │                  │                  │
        ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐
        │  Kubernetes  │  │  Kubernetes  │  │  Kubernetes  │
        │   Cluster    │  │   Cluster    │  │   Cluster    │
        └──────────────┘  └──────────────┘  └──────────────┘
```

## Component Interaction Flow

### 1. User Request Flow

```
User → UI → Backend API → WebSocket Hub → Operator → Kubernetes
```

Example: Deploying a workload

1. User submits deployment form in UI
2. UI sends POST request to Backend API (`/v1/workloads`)
3. Backend validates request and stores in PostgreSQL
4. Backend sends `workload_deploy` message to Hub
5. Hub routes message to appropriate Operator (by `cluster_id`)
6. Operator receives message and creates Workload CRD
7. Operator reconciles CRD → commits to Git → ArgoCD syncs

### 2. Status Update Flow

```
Kubernetes → Operator → WebSocket Hub → Backend → UI (SSE)
```

Example: Build completion

1. Kaniko build pod completes in Kubernetes
2. Operator watches BuildRequest CRD status
3. Operator sends `build_complete` message to Hub
4. Hub forwards message to Backend
5. Backend updates database record
6. Backend broadcasts SSE event to connected UI clients
7. UI updates workload status badge in real-time

## Design Principles

### 1. Zero Trust Security

**Problem**: Storing kubeconfig credentials in backend creates security risks.

**Solution**: Backend never holds cluster credentials. All operations are event-driven via WebSocket messages.

```
Backend CANNOT:
❌ Run kubectl commands
❌ Create Kubernetes resources directly
❌ Access cluster API servers

Backend CAN:
✅ Send deployment requests via WebSocket
✅ Receive status updates via WebSocket
✅ Store metadata in PostgreSQL
```

### 2. GitOps Workflow

**Problem**: Direct kubectl apply bypasses audit trails and CI/CD.

**Solution**: Every resource change goes through Git.

```
Workload CRD → Operator reconciles → Commits to Git → ArgoCD syncs → Kubernetes
```

**Benefits**:
- Declarative state in Git
- Audit trail of all changes
- Automatic rollback capabilities
- CI/CD integration

### 3. Event-Driven Communication

**Problem**: Polling for status is inefficient and delays updates.

**Solution**: WebSocket for operator-backend communication, SSE for UI updates.

```
Operator ──WebSocket──→ Hub ──WebSocket──→ Backend ──SSE──→ UI
         ←─────────────     ←─────────────        ←────────
```

### 4. Multi-Tenancy

**Problem**: Need to isolate resources between organizations and teams.

**Solution**: Hierarchical tenant model with enforced isolation.

```
Organization
  ├── Team A
  │   ├── Project 1 (namespace: org-teamA-project1)
  │   └── Project 2 (namespace: org-teamA-project2)
  └── Team B
      └── Project 3 (namespace: org-teamB-project3)
```

**Isolation Mechanisms**:
- Database: Row-level security by `org_id`
- Kubernetes: Namespace per project with RBAC
- Operator: Cluster-scoped, enforces project boundaries

## Data Flow Patterns

### Synchronous Operations

Used for CRUD operations that need immediate feedback:

```
UI → Backend API → Database → Response → UI
```

Examples:
- Login
- Create project (database record only)
- List workloads
- Get deployment status

### Asynchronous Operations

Used for long-running cluster operations:

```
UI → Backend API → WebSocket Hub → Operator
                ↓
           Database (status: Pending)

Operator → ... processing ... → Status Update → Hub → Backend → SSE → UI
                                                        ↓
                                                   Database (status: Running)
```

Examples:
- Deploy workload
- Scale deployment
- Install addon
- Build container image

### Background Jobs

Used for maintenance and cleanup tasks:

```
Backend → ARQ (Redis) → Worker → Database/External APIs
```

Examples:
- Delete stale resources
- Aggregate metrics
- Send notifications
- Cleanup old build images

## Scalability Considerations

### Backend API

- Stateless design allows horizontal scaling
- PostgreSQL connection pooling
- Redis caching for frequently accessed data
- Background job processing with ARQ workers

**Bottlenecks**:
- Database queries (solved: indexing, query optimization)
- WebSocket connection overhead (solved: connection pooling in Hub)

### WebSocket Hub

- Single Hub instance can handle thousands of connections
- Redis for connection registry (shared state)
- Connection pooling per cluster
- Message routing with O(1) lookup

**Bottlenecks**:
- Redis memory (solved: TTL on stale connections)
- Network bandwidth (solved: message batching)

### Operator

- One operator per cluster
- Leader election for HA (multiple replicas)
- Kubernetes controller pattern with caching
- Event-driven reconciliation (no polling)

**Bottlenecks**:
- Git commits (solved: batch commits when possible)
- ArgoCD sync speed (solved: ArgoCD scaling)

## Security Architecture

### Authentication & Authorization

```
┌─────────┐
│   UI    │  JWT (access_token)
└────┬────┘
     │
     ↓
┌─────────────┐
│   Backend   │  Validates JWT, checks RBAC
└────┬────────┘
     │
     ↓
┌──────────┐
│ Database │  Row-level security by org_id
└──────────┘
```

### Operator Authentication

```
┌──────────┐
│ Operator │  Cluster JWT (long-lived, cluster-specific)
└────┬─────┘
     │
     ↓
┌──────────┐
│   Hub    │  Validates JWT, registers connection
└────┬─────┘
     │
     ↓
┌─────────────┐
│   Backend   │  Trusts Hub authentication
└─────────────┘
```

**Token Hierarchy**:
- **User Access Token**: Short-lived (15 min), user-scoped
- **User Refresh Token**: Medium-lived (7 days), user-scoped
- **Cluster Token**: Long-lived (no expiry), cluster-scoped

### Network Security

- **UI ↔ Backend**: HTTPS (TLS 1.3)
- **Backend ↔ Hub**: WSS (WebSocket over TLS)
- **Operator ↔ Hub**: WSS (WebSocket over TLS)
- **Backend ↔ Database**: TLS with certificate validation
- **Operator ↔ Kubernetes**: In-cluster service account

## High Availability

### Backend

```
┌───────────┐   ┌───────────┐   ┌───────────┐
│ Backend 1 │   │ Backend 2 │   │ Backend 3 │
└─────┬─────┘   └─────┬─────┘   └─────┬─────┘
      └────────────┬────────────────┘
                   │
              Load Balancer
                   │
           ┌───────▼────────┐
           │   PostgreSQL   │
           │  (Primary +    │
           │   Replicas)    │
           └────────────────┘
```

### Hub

```
┌─────────┐   ┌─────────┐
│  Hub 1  │   │  Hub 2  │  (Active-Active with Redis coordination)
└────┬────┘   └────┬────┘
     │             │
     └──────┬──────┘
            │
      ┌─────▼─────┐
      │   Redis   │  (Connection registry)
      │ (Cluster) │
      └───────────┘
```

### Operator

```
┌────────────┐   ┌────────────┐
│ Operator 1 │   │ Operator 2 │  (Leader election)
│  (Leader)  │   │ (Standby)  │
└────────────┘   └────────────┘
```

## Disaster Recovery

### Backup Strategy

**PostgreSQL**:
- Daily full backups
- Continuous WAL archiving
- Point-in-time recovery (PITR)

**Git Repositories**:
- Distributed nature provides redundancy
- Remote mirrors for critical repos

**Kubernetes State**:
- Declarative in Git (can rebuild from Git)
- Velero for cluster backup (optional)

### Recovery Scenarios

**Backend Failure**:
1. Load balancer routes to healthy instances
2. If all instances fail: deploy new instances
3. Restore database from backup if corrupted

**Hub Failure**:
1. Operators reconnect to healthy Hub instance
2. Redis provides connection state
3. Message replay from backend queue

**Operator Failure**:
1. Standby replica takes over via leader election
2. Kubernetes state unchanged (declarative)
3. Sync from Git if needed

**Cluster Failure**:
1. User redeploys to different cluster
2. Git history provides full deployment state
3. No data loss (state in Git + Database)

## Monitoring & Observability

### Metrics

- **Backend**: Request rate, latency, error rate, database connections
- **Hub**: WebSocket connections, message throughput, routing latency
- **Operator**: Reconciliation duration, CRD status, ArgoCD sync health

### Logging

- **Structured JSON logs** for all components
- **Correlation IDs** for request tracing across components
- **Log aggregation** (ELK, Loki, or CloudWatch)

### Tracing

- **Distributed tracing** with OpenTelemetry
- **Trace spans**: UI → Backend → Hub → Operator → Kubernetes

### Alerting

- Backend API errors > threshold
- Hub connection failures
- Operator reconciliation failures
- Database connection pool exhaustion
- ArgoCD sync failures

## Performance Characteristics

### Latency Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| API Request | < 200ms | 95th percentile |
| WebSocket Message | < 50ms | Hub routing |
| CRD Reconciliation | < 5s | Operator to Git commit |
| ArgoCD Sync | < 30s | Git to Kubernetes |
| End-to-End Deployment | < 2min | For pre-built images |

### Throughput

- **Backend**: 1000 req/sec per instance
- **Hub**: 10,000 messages/sec
- **Operator**: 100 reconciliations/sec

## Future Enhancements

1. **Multi-Region Support**: Deploy Hub and Backend in multiple regions
2. **Edge Caching**: Cache static resources closer to users
3. **Smart Routing**: Route requests to nearest Hub instance
4. **Autoscaling**: Automatic scaling of backend and operator replicas
5. **Advanced RBAC**: Fine-grained permissions at resource level
