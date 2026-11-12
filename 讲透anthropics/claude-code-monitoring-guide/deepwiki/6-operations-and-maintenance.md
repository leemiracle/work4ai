<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/claude-code-monitoring-guide · page 6 Operations and Maintenance · fetched 2026-10-26 -->

# Operations and Maintenance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [claude_code_roi_full.md](claude_code_roi_full.md)
- [troubleshooting.md](troubleshooting.md)

</details>



This page provides operational guidance for maintaining, monitoring, and optimizing the Claude Code ROI measurement system in production environments. It covers system health monitoring, routine maintenance procedures, component lifecycle management, and operational workflows.

For specific troubleshooting procedures and solutions to common issues, see [Troubleshooting Guide](#6.1). For performance tuning and resource optimization guidance, see [Performance Optimization](#6.2). For security configurations and operational best practices, see [Security and Best Practices](#6.3).

## System Health Monitoring

### Service Status Verification

The ROI measurement system consists of multiple interconnected services that require coordinated monitoring. Use these commands to verify system health:

```bash
# Check all Docker services status
docker-compose ps

# Verify service endpoints
curl -f http://localhost:4317  # OTEL Collector gRPC
curl -f http://localhost:4318  # OTEL Collector HTTP  
curl -f http://localhost:9090  # Prometheus Web UI
curl -f http://localhost:3000  # Grafana Dashboard
curl -f http://localhost:8889/metrics  # OTEL Collector metrics
```

### Health Check Monitoring Architecture

```mermaid
graph TB
    subgraph "Health Check Endpoints"
        HC1["localhost:8889/metrics<br/>OTEL Collector Health"]
        HC2["localhost:9090/-/healthy<br/>Prometheus Health"]
        HC3["localhost:3000/api/health<br/>Grafana Health"]
    end
    
    subgraph "Service Dependencies"
        OC["otel-collector<br/>Container"]
        PROM["prometheus<br/>Container"]
        GR["grafana<br/>Container"]
    end
    
    subgraph "Data Flow Validation"
        DV1["claude_code_cost_usage_USD_total<br/>Metrics Presence"]
        DV2["claude_code_token_usage_tokens_total<br/>Token Metrics"]
        DV3["claude_code_session_count<br/>Session Tracking"]
    end
    
    HC1 --> OC
    HC2 --> PROM
    HC3 --> GR
    
    OC --> DV1
    PROM --> DV2
    GR --> DV3
    
    OC -.->|"depends_on"| PROM
    GR -.->|"depends_on"| PROM
```

**Sources**: [docker-compose.yml](), [troubleshooting.md:144-156]()

### Critical Metrics Monitoring

Monitor these key operational metrics to ensure system health:

| Metric | Threshold | Action |
|--------|-----------|--------|
| `up{job="otel-collector"}` | `< 1` | Restart OTEL Collector |
| `prometheus_tsdb_head_series` | `> 1M` | Review retention policy |
| `grafana_alerting_result_state` | `alerting` | Check dashboard alerts |
| Container memory usage | `> 80%` | Scale resources |
| Disk usage (`/prometheus`) | `> 85%` | Extend storage |

```bash
# Query critical metrics
curl -s 'http://localhost:9090/api/v1/query?query=up{job="otel-collector"}' | jq '.data.result[0].value[1]'
curl -s 'http://localhost:9090/api/v1/query?query=prometheus_tsdb_head_series' | jq '.data.result[0].value[1]'
```

**Sources**: [claude_code_roi_full.md:91-121](), [troubleshooting.md:144-156]()

## Routine Maintenance Procedures

### Configuration Management Workflow

```mermaid
sequenceDiagram
    participant Op as "Operations Team"
    participant Git as "Configuration Repo"
    participant DC as "docker-compose.yml"
    participant OC as "otel-collector-config.yaml"
    participant PC as "prometheus.yml"
    participant GC as "grafana/provisioning/"
    
    Op->>Git: "Pull latest configs"
    Git->>DC: "Update service definitions"
    Git->>OC: "Update OTLP pipeline config"
    Git->>PC: "Update scrape targets"
    Git->>GC: "Update dashboard configs"
    
    Op->>DC: "docker-compose down"
    Op->>DC: "docker-compose up -d"
    
    Note over Op: "Verify service health"
    Op->>OC: "Check OTLP receivers"
    Op->>PC: "Verify metrics ingestion"
    Op->>GC: "Validate dashboards"
```

**Sources**: [docker-compose.yml](), [otel-collector-config.yaml](), [prometheus.yml]()

### Data Retention Management

Configure appropriate data retention policies to balance storage costs with analytical needs:

```yaml
# prometheus.yml retention configuration
global:
  retention: "200h"  # ~8.3 days default
  retention_size: "15GB"  # Size-based limit
```

### Backup Procedures

Critical data backup includes Prometheus time-series data and Grafana dashboards:

```bash
# Backup Prometheus data
docker-compose exec prometheus tar -czf /prometheus/backup-$(date +%Y%m%d).tar.gz /prometheus/data

# Export Grafana dashboards
curl -s "http://admin:admin@localhost:3000/api/search?type=dash-db" | \
  jq -r '.[].uid' | \
  xargs -I {} curl -s "http://admin:admin@localhost:3000/api/dashboards/uid/{}" > grafana-backup-$(date +%Y%m%d).json
```

**Sources**: [claude_code_roi_full.md:54-89](), [grafana/provisioning/]()

## Component Lifecycle Management

### Service Update Procedures

```mermaid
flowchart TD
    subgraph "Update Process"
        START["Maintenance Window"]
        BACKUP["Create Data Backup"]
        PULL["docker-compose pull"]
        DOWN["docker-compose down"]
        UP["docker-compose up -d"]
        VERIFY["Health Check Validation"]
        ROLLBACK["Rollback if Failed"]
        END["Update Complete"]
    end
    
    subgraph "Validation Steps"
        CHECK1["Verify OTLP endpoints<br/>4317, 4318"]
        CHECK2["Validate Prometheus<br/>targets and scraping"]
        CHECK3["Confirm Grafana<br/>dashboard functionality"]
        CHECK4["Test metric ingestion<br/>claude_code_* metrics"]
    end
    
    START --> BACKUP
    BACKUP --> PULL
    PULL --> DOWN
    DOWN --> UP
    UP --> VERIFY
    VERIFY --> CHECK1
    CHECK1 --> CHECK2
    CHECK2 --> CHECK3
    CHECK3 --> CHECK4
    CHECK4 --> END
    
    VERIFY -.->|"Failure"| ROLLBACK
    ROLLBACK --> DOWN
```

**Sources**: [docker-compose.yml](), [troubleshooting.md:145-156]()

### Configuration Drift Detection

Monitor for configuration changes that may impact system performance:

```bash
# Check container configuration changes
docker-compose config --quiet && echo "Config valid" || echo "Config error"

# Verify environment variable consistency
docker-compose exec otel-collector env | grep OTEL_
docker-compose exec prometheus env | grep PROMETHEUS_
```

## Operational Workflows

### Daily Operations Checklist

| Task | Frequency | Command | Expected Result |
|------|-----------|---------|-----------------|
| Service health check | Daily | `docker-compose ps` | All services `Up` |
| Metric ingestion verification | Daily | Query `claude_code_cost_usage_USD_total` | Recent data present |
| Storage usage check | Daily | `df -h /var/lib/docker` | `< 80%` usage |
| Log rotation check | Weekly | `docker system df` | Reasonable log sizes |
| Dashboard functionality | Weekly | Access Grafana UI | All panels loading |

### Automated Monitoring Script

```bash
#!/bin/bash
# system-health-check.sh
set -e

# Check service status
if ! docker-compose ps | grep -q "Up"; then
    echo "ERROR: Services not running"
    exit 1
fi

# Verify metric availability
TOTAL_COST=$(curl -s "http://localhost:9090/api/v1/query?query=sum(claude_code_cost_usage_USD_total)" | jq -r '.data.result[0].value[1] // "0"')
if [[ "$TOTAL_COST" == "0" ]]; then
    echo "WARNING: No cost metrics found"
fi

# Check disk usage
DISK_USAGE=$(df /var/lib/docker | awk 'NR==2 {print $5}' | sed 's/%//')
if [[ "$DISK_USAGE" -gt 85 ]]; then
    echo "WARNING: Disk usage at ${DISK_USAGE}%"
fi

echo "System health check passed"
```

**Sources**: [claude_code_roi_full.md:91-121](), [troubleshooting.md:1-187]()

### Scaling Operations

Monitor system load and scale components as needed:

```yaml
# docker-compose.yml scaling configuration
services:
  otel-collector:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
  
  prometheus:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

## Key Operational Metrics

### System Performance Indicators

Track these metrics to ensure optimal system operation:

```promql
# OTEL Collector performance
otelcol_processor_batch_batch_send_size_sum / otelcol_processor_batch_batch_send_size_count

# Prometheus ingestion rate
rate(prometheus_tsdb_head_samples_appended_total[5m])

# Memory usage patterns
container_memory_usage_bytes{name=~".*otel-collector.*|.*prometheus.*|.*grafana.*"}

# Query response times
histogram_quantile(0.95, rate(prometheus_http_request_duration_seconds_bucket[5m]))
```

### Business Metrics Validation

Ensure business-critical metrics are being collected correctly:

```promql
# Verify Claude Code metrics presence
up{job="otel-collector"} == 1
increase(claude_code_session_count[1h]) > 0
sum(claude_code_cost_usage_USD_total) by (model)
```

**Sources**: [claude_code_roi_full.md:91-121](), [prometheus.yml]()

## Integration Points

The Operations and Maintenance procedures interact with several system components:

- **Telemetry Collection**: Monitor OTLP endpoint health at `localhost:4317` and `localhost:4318`
- **Report Generation**: Ensure Prometheus API availability at `localhost:9090` for automated reporting
- **Dashboard Access**: Maintain Grafana service at `localhost:3000` for visualization
- **Configuration Management**: Track changes to `docker-compose.yml`, `prometheus.yml`, and `otel-collector-config.yaml`

For detailed troubleshooting of specific components, see [Troubleshooting Guide](#6.1). For performance tuning guidance, see [Performance Optimization](#6.2). For security and deployment best practices, see [Security and Best Practices](#6.3).

**Sources**: [claude_code_roi_full.md:1-537](), [troubleshooting.md:1-187]()

---

