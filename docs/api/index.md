---
sidebar_position: 0
title: API Overview
---

# Kubenest API Reference

Welcome to the Kubenest Backend API documentation. This API provides a centralized control plane for deploying and managing applications across multiple Kubernetes clusters with GitOps-style workflows.

## Base URL

```
Production:  https://api.kubenest.io/v1
Staging:     https://api-staging.kubenest.io/v1
Local:       http://localhost:8080/v1
```

## Authentication

All API endpoints (except login and register) require JWT authentication.

### Get Access Token

```bash
curl -X POST http://localhost:8080/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 900
}
```

### Using Access Token

Include the access token in the `Authorization` header:

```bash
curl -X GET http://localhost:8080/v1/clusters \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..."
```

### Refresh Token

When your access token expires (after 15 minutes), use the refresh token to get a new one:

```bash
curl -X POST http://localhost:8080/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
  }'
```

## API Endpoints

The API is organized into the following categories:

### Authentication
- [User Login](./user-login.api.mdx) - Authenticate and get access token
- [User Registration](./user-registration.api.mdx) - Create new user account
- [Refresh Token](./refresh-jwt-token.api.mdx) - Get new access token
- [Logout](./user-logout.api.mdx) - Invalidate tokens

### Clusters
- [Register Cluster](./register-new-cluster.api.mdx) - Register a new Kubernetes cluster
- [List Clusters](./list-all-clusters.api.mdx) - Get all registered clusters
- [Get Cluster](./get-cluster-details.api.mdx) - Get cluster details
- [Delete Cluster](./unregister-cluster.api.mdx) - Unregister a cluster
- [Install Command](./get-helm-install-command.api.mdx) - Get Helm install command

### Projects
- [Create Project](./create-project.api.mdx) - Create a new project
- [List Projects](./list-projects.api.mdx) - Get all projects
- [Get Project](./get-project-details.api.mdx) - Get project details
- [Delete Project](./delete-project.api.mdx) - Delete a project
- [List Project Workloads](./list-workloads-in-project.api.mdx) - Get workloads in a project

### Workloads
- [Deploy Workload](./deploy-workload.api.mdx) - Deploy a new workload
- [List Workloads](./list-workloads.api.mdx) - Get all workloads
- [Get Workload](./get-workload-details.api.mdx) - Get workload details
- [Update Workload](./update-workload.api.mdx) - Update workload configuration
- [Delete Workload](./delete-workload.api.mdx) - Delete a workload
- [Redeploy](./trigger-redeployment.api.mdx) - Trigger redeployment

### Addons
- [Install Addon](./install-addon.api.mdx) - Install a new addon
- [List Addons](./list-addons.api.mdx) - Get all addons
- [Get Addon](./get-addon-details.api.mdx) - Get addon details
- [Delete Addon](./uninstall-addon.api.mdx) - Uninstall an addon

### Events
- [SSE Stream](./server-sent-events-stream.api.mdx) - Real-time event stream

## Rate Limiting

API requests are rate-limited to prevent abuse:

- **Authenticated requests**: 1000 requests per hour
- **Unauthenticated requests**: 100 requests per hour

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1638360000
```

## Error Handling

The API uses standard HTTP status codes:

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Unprocessable Entity |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

Error responses include details:

```json
{
  "error": "Invalid request",
  "message": "Field 'name' is required",
  "field": "name"
}
```

## Pagination

List endpoints support pagination:

```bash
curl "/v1/workloads?page=1&per_page=20" \
  -H "Authorization: Bearer $TOKEN"
```

Response includes pagination metadata:

```json
{
  "items": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5
  }
}
```

## Filtering

Most list endpoints support filtering:

```bash
# Filter workloads by project
curl "/v1/workloads?project_id=project-abc" \
  -H "Authorization: Bearer $TOKEN"

# Filter by status
curl "/v1/workloads?status=Running" \
  -H "Authorization: Bearer $TOKEN"

# Combine filters
curl "/v1/workloads?project_id=project-abc&status=Running" \
  -H "Authorization: Bearer $TOKEN"
```

## Sorting

Sort results with the `sort` parameter:

```bash
# Sort by creation date (newest first)
curl "/v1/workloads?sort=-created_at" \
  -H "Authorization: Bearer $TOKEN"

# Sort by name (ascending)
curl "/v1/workloads?sort=name" \
  -H "Authorization: Bearer $TOKEN"
```

Use `-` prefix for descending order.

## Webhooks (Future)

Webhook support for event notifications is planned for a future release.

## SDKs

Official SDKs are in development:

- JavaScript/TypeScript (Coming Soon)
- Python (Coming Soon)
- Go (Coming Soon)

## Support

- [GitHub Issues](https://github.com/kubenesthq/backend/issues)
- [Documentation](/docs/intro)
- [Architecture Guide](/docs/architecture/overview)
