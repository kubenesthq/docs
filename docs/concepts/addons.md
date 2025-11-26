---
sidebar_position: 3
title: Addons
---

# Addons

Addons are managed services that you can install alongside your workloads. Kubenest provides pre-configured Helm charts for popular databases, caches, and message queues.

## What is an Addon?

An **Addon** is a service dependency for your workloads, such as:
- Databases (PostgreSQL, MySQL, MongoDB)
- Caches (Redis, Memcached)
- Message Queues (RabbitMQ, Kafka)
- Search engines (Elasticsearch)
- Object storage (MinIO)

Kubenest manages the entire lifecycle: installation, configuration, upgrades, and connection info export.

## Available Addons

| Addon | Type | Description |
|-------|------|-------------|
| PostgreSQL | `postgresql` | Relational database |
| MySQL | `mysql` | Relational database |
| MongoDB | `mongodb` | Document database |
| Redis | `redis` | In-memory cache/database |
| RabbitMQ | `rabbitmq` | Message broker |
| Kafka | `kafka` | Event streaming platform |
| Elasticsearch | `elasticsearch` | Search and analytics |
| MinIO | `minio` | S3-compatible object storage |

## Installing an Addon

### PostgreSQL Example

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
      "storage": "10Gi",
      "cpu": "1",
      "memory": "2Gi"
    }
  }'
```

## Export System

Addons export connection information that workloads can import.

### Example Flow

1. Install PostgreSQL addon
2. Operator creates database and extracts connection string
3. Addon status updated with exports:
   ```yaml
   status:
     exports:
       connection_string: "postgresql://user:pass@postgres:5432/myapp"
       host: "postgres.my-project.svc.cluster.local"
       port: "5432"
       database: "myapp"
       username: "myapp_user"
       password: "<stored-in-secret>"
   ```
4. Deploy workload with import:
   ```json
   {
     "imports": [
       {
         "from": "postgres",
         "key": "connection_string",
         "as": "DATABASE_URL"
       }
     ]
   }
   ```
5. Operator injects `DATABASE_URL` environment variable into workload

## Best Practices

- Use addons for development/staging
- Consider managed services (RDS, CloudSQL) for production
- Enable backups for databases
- Set appropriate resource limits

See [Managing Addons Guide](/docs/guides/managing-addons) for more details.
