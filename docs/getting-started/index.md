---
sidebar_position: 1
title: Overview
---

# Getting Started with Kubenest

This guide will walk you through setting up Kubenest and deploying your first application.

## Prerequisites

Before you begin, ensure you have:

- **Kubernetes cluster** (v1.24 or later) with cluster-admin access
- **PostgreSQL database** (v13 or later) for the backend
- **Redis instance** (v6 or later) for the WebSocket Hub
- **Git repository** for GitOps workflows
- **ArgoCD** installed in your cluster (or Kubenest can install it for you)

## Installation Steps

The Kubenest installation consists of three main components:

### 1. Backend API Setup

The Backend API serves as the control plane for all operations:

```bash
# Clone the backend repository
git clone https://github.com/kubenesthq/backend.git
cd backend

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the API server
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

The Backend API will be available at `http://localhost:8080`.

### 2. WebSocket Hub Setup

The Hub manages real-time communication between the backend and operators:

```bash
# Clone the hub repository
git clone https://github.com/kubenesthq/hub.git
cd hub

# Build the binary
go build -o kubenest-hub ./cmd/hub

# Set up environment variables
export REDIS_URL="redis://localhost:6379"
export JWT_SECRET="your-secret-key"

# Start the hub
./kubenest-hub
```

The Hub will listen for WebSocket connections on port 8081.

### 3. Kubernetes Operator Installation

The Operator runs in your Kubernetes cluster and manages resources:

See the [Installation Guide](./installation.md) for detailed instructions on installing the operator in your cluster.

## Next Steps

Once you have the components running:

1. **[Install the Operator](./installation.md)** in your Kubernetes cluster
2. **[Deploy Your First Application](./first-deployment.md)** using Kubenest

## Architecture Quick Reference

```
┌─────────────┐
│   Backend   │  Port 8080 (HTTP/REST)
│   FastAPI   │
└──────┬──────┘
       │
       ├─────→ PostgreSQL (Database)
       │
       ├─────→ WebSocket Hub (Port 8081)
       │
       └─────→ Redis (via Hub)

┌─────────────┐
│     Hub     │  Port 8081 (WebSocket)
│     Go      │
└──────┬──────┘
       │
       └─────→ Operators in Clusters
```

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/kubenest

# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# WebSocket Hub
HUB_URL=ws://localhost:8081

# Redis (for background jobs)
REDIS_URL=redis://localhost:6379
```

### Hub

```bash
# Redis
REDIS_URL=redis://localhost:6379

# JWT Secret (same as backend)
JWT_SECRET=your-secret-key-here

# Server Configuration
PORT=8081
```

## Verification

To verify your installation:

1. Check Backend API health:
   ```bash
   curl http://localhost:8080/health
   ```

2. Check Hub health:
   ```bash
   curl http://localhost:8081/health
   ```

3. View operator status:
   ```bash
   kubectl get pods -n kubenest-system
   ```

## Troubleshooting

### Backend won't start

- Verify PostgreSQL is running and accessible
- Check database credentials in `.env`
- Ensure migrations have been applied: `alembic upgrade head`

### Hub connection issues

- Verify Redis is running and accessible
- Check JWT_SECRET matches between backend and hub
- Ensure WebSocket port (8081) is not blocked by firewall

### Operator not connecting

- Check hub URL in operator configuration
- Verify JWT token is valid
- Review operator logs: `kubectl logs -n kubenest-system -l app=kubenest-operator`

## Need Help?

- [Installation Guide](./installation.md) - Detailed operator installation
- [Architecture Overview](/docs/architecture/overview) - System design
- [GitHub Issues](https://github.com/kubenesthq/docs/issues) - Report problems
