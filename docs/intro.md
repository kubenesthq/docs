---
sidebar_position: 1
title: Introduction
---

# Welcome to Kubenest

Kubenest is a **GitOps-driven Kubernetes Platform** designed for enterprises who want a Railway-like developer experience, but running entirely on their own infrastructure.

## What is Kubenest?

Kubenest provides platform engineering capabilities without SaaS vendor lock-in. It combines the developer experience of modern PaaS solutions with the control and security of self-hosted infrastructure.

### Key Features

- **Multi-Cluster Management**: Register and manage multiple Kubernetes clusters from a single control plane
- **GitOps Workflows**: Every deployment is tracked in Git and synced via ArgoCD
- **Zero Trust Architecture**: Backend never holds cluster credentials - all operations via secure WebSocket events
- **Multi-Tenant**: Built-in organization, team, and project hierarchy
- **Real-Time Updates**: Live status updates via Server-Sent Events (SSE)
- **Flexible Deployments**: Support for container images, Dockerfiles, and Cloud Native Buildpacks

## System Components

Kubenest consists of four main components:

1. **Backend API** (FastAPI) - Multi-tenant orchestration and control plane
2. **WebSocket Hub** (Go) - Real-time message router between backend and operators
3. **Kubernetes Operator** (Go) - Cluster-side controller managing Custom Resource Definitions (CRDs)
4. **Web UI** (Next.js) - Management console for platform operations

## Architecture Overview

```
┌─────────┐     REST API    ┌─────────────┐    WebSocket    ┌─────────┐
│   UI    │ ───────────────→│   Backend   │←───────────────→│   Hub   │
│ Next.js │                 │  FastAPI    │                 │   Go    │
└─────────┘                 └─────────────┘                 └─────────┘
                                   │                              ↕
                              PostgreSQL                   WebSocket Pool
                              (multi-tenant)                     ↕
                                                          ┌──────────────┐
                                                          │  Operator    │
                                                          │ (per cluster)│
                                                          └──────────────┘
                                                                 ↓
                                                      ┌──────────────────────┐
                                                      │  GitOps Workflow     │
                                                      │  CRD → Git → ArgoCD  │
                                                      │  → Kubernetes        │
                                                      └──────────────────────┘
```

## Quick Start

Ready to get started? Follow our [Getting Started Guide](/docs/getting-started) to:

1. Set up the Kubenest backend and hub
2. Register your first Kubernetes cluster
3. Deploy your first application

## Learn More

- [Architecture Overview](/docs/architecture/overview) - Deep dive into system design
- [Core Concepts](/docs/concepts/projects) - Understand Projects, Workloads, and Addons
- [API Reference](/docs/api) - Complete REST API documentation
- [GitHub Organization](https://github.com/kubenesthq) - Source code and repositories

## Philosophy

Kubenest is built on these principles:

- **GitOps First**: CRD is the source of truth → Git → ArgoCD → Kubernetes (no direct kubectl apply)
- **Zero Trust**: Backend never holds kubeconfigs, all operations via WebSocket events
- **Event-Driven**: Real-time communication for responsive user experience
- **Unified Deployment**: All deployments (workloads, addons) use Helm charts via ArgoCD
- **Multi-Tenant by Design**: Backend enforces isolation, operators are cluster-scoped

## Support

- [GitHub Issues](https://github.com/kubenesthq/docs/issues)
- [API Documentation](/docs/api)
- [Architecture Guide](/docs/architecture/overview)
