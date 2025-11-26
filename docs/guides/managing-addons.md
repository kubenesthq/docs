---
sidebar_position: 3
title: Managing Addons
---

# Managing Addons

Learn how to install and configure managed services for your applications.

## Installing PostgreSQL

```bash
curl -X POST /v1/addons \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "postgres",
    "project_id": "project-abc",
    "type": "postgresql",
    "version": "15",
    "config": {
      "database": "myapp",
      "username": "myapp_user"
    },
    "resources": {
      "storage": "20Gi",
      "cpu": "2",
      "memory": "4Gi"
    }
  }'
```

## Connecting Workloads to Addons

After installing an addon, connect it to your workload:

```bash
curl -X POST /v1/workloads \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "api",
    "project_id": "project-abc",
    "source": {...},
    "imports": [
      {
        "from": "postgres",
        "key": "connection_string",
        "as": "DATABASE_URL"
      }
    ]
  }'
```

The `DATABASE_URL` environment variable is automatically injected into your workload.

## Available Addons

### Redis

```json
{
  "type": "redis",
  "version": "7",
  "config": {
    "maxmemory": "2gb",
    "maxmemory-policy": "allkeys-lru"
  }
}
```

**Exports**:
- `connection_string`: `redis://:password@redis:6379`
- `host`: `redis.my-project.svc.cluster.local`
- `port`: `6379`

### MongoDB

```json
{
  "type": "mongodb",
  "version": "7",
  "config": {
    "database": "myapp",
    "username": "myapp_user"
  }
}
```

**Exports**:
- `connection_string`: `mongodb://user:pass@mongodb:27017/myapp`
- `database`: `myapp`

### RabbitMQ

```json
{
  "type": "rabbitmq",
  "version": "3.12",
  "config": {
    "username": "admin"
  }
}
```

**Exports**:
- `connection_string`: `amqp://admin:pass@rabbitmq:5672`
- `management_url`: `http://rabbitmq:15672`

## Backup and Restore

For production addons, enable backups:

```json
{
  "backup": {
    "enabled": true,
    "schedule": "0 2 * * *",
    "retention": "7d",
    "storage": {
      "type": "s3",
      "bucket": "my-backups",
      "region": "us-east-1"
    }
  }
}
```

## Upgrading Addons

```bash
curl -X PATCH /v1/addons/{addon_id} \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "version": "16"
  }'
```

Kubenest performs a rolling upgrade with minimal downtime.

## Uninstalling Addons

```bash
curl -X DELETE /v1/addons/{addon_id} \
  -H "Authorization: Bearer $TOKEN"
```

Warning: This deletes all data. Ensure you have backups before uninstalling.

## Best Practices

1. Use managed cloud services (RDS, CloudSQL) for production databases
2. Enable backups for all stateful addons
3. Set appropriate resource limits
4. Use separate addons for dev/staging/prod environments
5. Monitor addon resource usage

See [Addons Concept](/docs/concepts/addons) for full documentation.
