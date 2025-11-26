---
sidebar_position: 4
title: Monitoring & Observability
---

# Monitoring & Observability

Monitor your workloads and infrastructure with Kubenest's built-in observability features.

## Real-Time Status Updates

Kubenest provides real-time status updates via Server-Sent Events (SSE).

### UI Integration

The UI automatically subscribes to SSE events:

```typescript
const eventSource = new EventSource('/v1/events', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Update UI with status changes
};
```

### Event Types

- `workload.status_changed` - Workload status update
- `build.completed` - Container build finished
- `deployment.ready` - Deployment is healthy
- `error.occurred` - Error in deployment

## Viewing Logs

### Via kubectl

```bash
# View workload logs
kubectl logs -n my-project -l app=my-app --tail=100 -f

# View specific pod logs
kubectl logs my-app-xyz -n my-project

# View previous pod logs (after crash)
kubectl logs my-app-xyz -n my-project --previous
```

### Via API (Coming Soon)

```bash
curl /v1/workloads/{id}/logs?tail=100 \
  -H "Authorization: Bearer $TOKEN"
```

## Metrics

### Workload Metrics

```bash
curl /v1/workloads/{id}/metrics \
  -H "Authorization: Bearer $TOKEN"
```

Returns:
- CPU usage
- Memory usage
- Network I/O
- Request rate
- Error rate

### Project Metrics

```bash
curl /v1/projects/{id}/metrics \
  -H "Authorization: Bearer $TOKEN"
```

Returns aggregated metrics for all workloads in the project.

## Health Checks

Kubenest monitors workload health through:

1. **Kubernetes Health Checks**: Liveness, readiness, startup probes
2. **ArgoCD Sync Status**: Deployment synchronization
3. **Resource Availability**: Pod availability and replica counts

## Alerting (Future)

Planned features:
- Email/Slack notifications on deployment failures
- Custom alert rules
- Metric-based alerting
- Integration with PagerDuty, Opsgenie

## Recommended Tools

### Prometheus + Grafana

Install Prometheus Operator in your cluster:

```bash
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

### Elastic Stack (ELK)

For log aggregation:

```bash
helm install elasticsearch elastic/elasticsearch \
  --namespace logging \
  --create-namespace

helm install kibana elastic/kibana \
  --namespace logging
```

### Jaeger

For distributed tracing:

```bash
helm install jaeger jaegertracing/jaeger \
  --namespace tracing \
  --create-namespace
```

## Best Practices

1. Set up health checks for all workloads
2. Monitor resource usage to optimize costs
3. Use structured logging (JSON format)
4. Implement distributed tracing for microservices
5. Set up alerts for critical failures

See [Architecture Overview](/docs/architecture/overview) for system monitoring details.
