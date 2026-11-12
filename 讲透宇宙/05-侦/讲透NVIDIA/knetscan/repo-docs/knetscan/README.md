# KNetScan
## A Kubernetes Network Scanner

![image](resources/simplistic-arch-diag.png)

*[Refer to the website for detailed architecture diagrams]*

Gain visibility on your Kubernetes cluster network using this tool.
 * Fetch available pods, services, and node IPs - cluster and external, and run port scans on each.
 * Port scan initiates CONNECT scans by default, and falls back to SYN scans on failure.
 * Run the tool inside or outside the target cluster.
 * Configure it to check for specific namespaces or nodes.
 * Check egress rules by deploying inside the cluster and setting an external target on an internet.
 * One-time scans or regular scans for monitoring.

## Building from Source

```bash
cd knetscan/knetscan

# Build the binary
make build-all
```

## Using Docker

```bash
# Build the Docker image
make docker-build
```

## Deployment Models

**Internal Scanner:**
* Intended to be run inside a Kubernetes cluster.
* Uses Kubernetes client to fetch all IPs (pods, services, and nodes) and then run nmap scans on their internal and external IPs.
* With the `add-scan-ips` argument add target IPs/domains to check for your cluster's egress rules.
* Any dashboard (Grafana, Kibana, etc) can be used to visualize relevant data.

**External Scanner:**
* Intended to be run outside a Kubernetes cluster. Expects path to the kubeconfig (for the target cluster) as input.
* Fetches all relevant external IPs (services and nodes) and then run nmap scans on their external IPs.
* Database and dashboard options remain the same.

## Command Line Arguments

| Argument | Data type | Description |
| -------- | --------- | ----------- |
| version | bool | Display knetscan version information and exit |
| one-time | bool | Run the scan only once |
| freq | int | Scan frequency in minutes (if not a one-time scan) |
| in-cluster | bool | Is the code deployed inside the target cluster |
| kubeconfig | string | Absolute path to the kubeconfig to access the target cluster (if not deployed inside the target cluster) |
| local-storage-only | bool | Post data to local storage only (Elasticsearch is ignored) |
| local-storage-path | string | Path to store results in local storage |
| scan-if-no-ports | bool | Run the default nmap scan behavior if no ports are found by knetscan |
| scan-ports-override | string | Override the default ports to be scanned by nmap (Provide in nmap compliant format - "1,2,4-6") |
| add-targets-file | string | File containing additional targets to scan. Generally from knetscan-init container |
| add-scan-targets | string | Add target CIDRs:Ports to scan. Note - In this argument the values are separated by a semicolon to allow use of comma for ports. Ideally used to test egress rules. (format - "192.168.0.1:1-2;google.com:443;10.0.0.0/24:4-10") |
| skip-auto-detect | bool | Skip fetching IPs from api-server and only scan the IPs provided in 'add-scan-targets' |
| single-host-scan-timeout | int | Override the recommended 60 seconds per host scan timeout |
| namespaces | string | Restrict the scan to specific namespaces (Provide in format - "ns1,ns2,ns3") |
| nodes | string | Restrict the scan to specific nodes (Provide in format - "node1,node2") |
| es | string | Elasticsearch endpoint |
| es-user | string | Elasticsearch username |
| es-pass | string | Elasticsearch password |
| es-ca-fp | string | Elasticsearch certificate fingerprint |
| es-index | string | Elasticsearch index for posting scan results (default: knetscan-index) |
| log-dir | string | Directory where the log file resides. If not specified, logs to stderr |
| log-format | string | Defines the logging mode to either console or json |
| log-level | string | Defines the logging level. Choose from one of: fatal, error, warn, info, debug |

## Example Usage

### Running inside a cluster

```bash
# Create a namespace for knetscan
kubectl create ns knscan

# Run knetscan
helm install -f charts/knetscan/values.yaml knetscan charts/knetscan/. --namespace=knscan
```

### Running outside a cluster

```bash
# Run directly on your system
sudo ./knetscan -one-time=true -in-cluster=false -local-storage-only=true -local-storage-path=$HOME/knetscan-results -kubeconfig=$HOME/.kube/config
```

### Important configuration differences for external scanner

1. `in-cluster` must be set to `false` (tells the program that it's run outside the target cluster)
2. `kubeconfig` must be provided (provides access to the target cluster's api-server)
3. `local-storage-path` should be set to save the results locally

## Using with Visualization Tools

The scan results can be visualized using tools like Grafana. A sample dashboard template is provided at [/resources/sample-grafana-dashboard.json](resources/sample-grafana-dashboard.json).

For a more comprehensive approach with automated visualization, consider using the KNetScan Workflow tool which automatically generates network graphs and Jupyter notebooks.

## License
SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.

SPDX-License-Identifier: Apache-2.0