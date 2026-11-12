# GPU Usage Monitor

A comprehensive Helm chart for monitoring GPU resources in Kubernetes clusters. This tool provides real-time visibility into GPU allocation, utilization, memory usage, and pod status through an integrated Prometheus and Grafana monitoring stack.

![GPU Usage Monitor Dashboard](https://github.com/NVIDIA/gpu-usage-monitor/blob/main/dashboards/gpu-usage-dashboard.png?raw=true)

# Overview

The GPU Usage Monitor helps you:
- **Monitor GPU allocation**: Track total vs. allocated GPUs across your cluster
- **Measure GPU utilization**: View real-time GPU compute utilization percentages
- **Track memory usage**: Monitor GPU memory consumption and availability
- **Observe pod status**: See running and pending GPU-enabled pods
- **Filter by GPU type**: Dynamic filtering by GPU model (e.g., A100, V100, etc.)

The tool uses NVIDIA DCGM (Data Center GPU Manager) metrics collected by Prometheus and visualized through a pre-configured Grafana dashboard.

## Architecture

The tool consists of four main components:

1. **DCGM Exporter**: Exposes NVIDIA GPU metrics (external - deployed via GPU Operator)
2. **kube-state-metrics**: Exposes Kubernetes pod and resource metrics
3. **Prometheus**: Collects and stores metrics from DCGM and kube-state-metrics
4. **Grafana**: Provides visualization through the GPU Usage Monitor Dashboard

```
┌─────────────────┐       ┌──────────────────┐
│   DCGM Exporter │       │ kube-state-      │
│                 │       │ metrics          │
└────────┬────────┘       └────────┬─────────┘
         │ GPU Metrics             │ K8s Metrics
         │                         │
         └────────┬────────────────┘
                  │
                  ▼
         ┌─────────────────┐
         │   Prometheus    │ Scrapes & Stores Metrics
         └────────┬────────┘
                  │ Queries
                  ▼
         ┌─────────────────┐
         │    Grafana      │ Visualizes Dashboard
         └─────────────────┘
```

# Getting Started

## Step 1: Add Helm Chart Dependencies

First, update the Helm dependencies to download Prometheus and Grafana charts:

```bash
helm dependency update
```

This will download the required charts into the `charts/` directory.

## Step 2: Install the Chart

Install the chart with default configuration:

```bash
helm install gpu-usage-monitor . --namespace gpu-usage-monitor --create-namespace
```

Or install with custom values:

```bash
helm install gpu-usage-monitor . \
  --namespace gpu-usage-monitor \
  --create-namespace \
  --values custom-values.yaml
```

## Step 3: Access Grafana Dashboard

After installation, access the Grafana dashboard:

```bash
# Port-forward to Grafana service
kubectl port-forward -n gpu-usage-monitor svc/gpu-usage-monitor-grafana 3000:80
```

Open your browser and navigate to: `http://localhost:3000`

The GPU Usage Monitor dashboard will automatically load as the home dashboard.

To edit the dashboards, login with:
- Username: `admin`
- Password: `admin`

# Requirements

| Component | Version | Required |
|-----------|---------|----------|
| Kubernetes | 1.19+ | Yes |
| Helm | 3.0+ | Yes |
| DCGM Exporter | --- | Yes |
| Prometheus | 27.45.0 (included) | Yes |
| Grafana | 10.1.4 (included) | Yes |

### Verify DCGM Metrics

Ensure DCGM metrics are available in your cluster:

```bash
# Check if DCGM exporter pods are running
kubectl get pods -A | grep dcgm

# Verify metrics are being exposed
kubectl port-forward -n <dcgm-namespace> <dcgm-pod-name> 9400:9400
curl http://localhost:9400/metrics | grep DCGM_FI_DEV
```

# Usage

## Basic Configuration

The `values.yaml` file contains the default configuration. By default, the installation will spin up a Prometheus pod and a Grafana pod.

If you do not have Prometheus installed on your cluster, you likely do not have kube-state-metrics exporter. Enable it:

```yaml
prometheus:
  kube-state-metrics:
    enabled: true
```

> **Note**: Enabling kube-state-metrics when you already have one installed on your cluster might cause metrics duplication.

## Using External Prometheus

If you already have Prometheus running in your cluster, we recommend using it because it already holds historical data. To use it, disable the Prometheus installation and provide your Prometheus service endpoint:

```yaml
prometheus:
  enabled: false  # Disable built-in Prometheus

global:
  prometheusUrl: "http://my-prometheus-server.monitoring.svc:9090"
```

## Customizing Resources

If you experience slowness in the dashboard operation, try increasing the resources:

```yaml
prometheus:
  resources:
    limits:
      cpu: 1000m
      memory: 4096Mi
    requests:
      cpu: 200m
      memory: 1024Mi

grafana:
  resources:
    limits:
      cpu: 500m
      memory: 2048Mi
    requests:
      cpu: 100m
      memory: 512Mi
```

## Changing Grafana Credentials

If you plan on exposing the dashboard, changing the credentials is recommended:

```yaml
grafana:
  adminUser: your-admin-user
  adminPassword: your-secure-password
```

## Dashboard Features

The GPU Usage Monitor Dashboard provides:

| Feature | Description |
|---------|-------------|
| **GPU Allocation** | Time-series graph showing total GPUs vs. allocated GPUs, with percentage gauge |
| **GPU Utilization** | Average GPU compute utilization with threshold indicators (green: >80%, yellow: 50-80%, red: <50%) |
| **GPU Memory Usage** | Total memory capacity vs. used memory in mebibytes, with usage percentage |
| **Running GPU Pods** | Count of running pods using GPUs |
| **Pending GPU Pods** | Count of pods waiting for GPU resources to identify resource constraints |

## Uninstallation

To remove the GPU Usage Monitor:

```bash
helm uninstall gpu-usage-monitor --namespace gpu-usage-monitor
```

To also remove the namespace:

```bash
kubectl delete namespace gpu-usage-monitor
```

## Troubleshooting

### No GPU metrics showing in Grafana

1. Verify DCGM exporter is running:
   ```bash
   kubectl get pods -A | grep dcgm
   ```

2. Check Prometheus is scraping DCGM metrics:
   ```bash
   kubectl logs -n monitoring deployment/gpu-usage-monitor-prometheus-server
   ```

3. Ensure Prometheus has the correct ServiceMonitor or scrape configuration for DCGM

### Grafana dashboard is empty

1. Check Prometheus data source connection in Grafana
2. Verify the Prometheus URL is correct
3. Confirm DCGM metrics are available: `DCGM_FI_DEV_FB_FREE`, `DCGM_FI_DEV_GPU_UTIL`

### Pods failing to start

Check resource availability:

```bash
kubectl describe pod -n monitoring <pod-name>
```

# Contribution Guidelines

- Start here: `CONTRIBUTING.md`
- Code of Conduct: `CODE_OF_CONDUCT.md`

## Governance & Maintainers

- Governance: `GOVERNANCE.md`

## Security

- Vulnerability disclosure: `SECURITY.md`
- Do not file public issues for security reports.

## Support

- How to get help: Issues/Discussions

# References

- [DCGM Exporter](https://github.com/NVIDIA/dcgm-exporter)
- [kube-state-metrics Documentation](https://github.com/kubernetes/kube-state-metrics)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

# License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
