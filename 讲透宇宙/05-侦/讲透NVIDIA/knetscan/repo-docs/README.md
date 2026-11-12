# KNetScan
## A Kubernetes scalable port discovery and reachability analyzer

* Performs comprehensive port scans across all pods, services, and nodes (both internal and external IPs)
* Intelligently optimized port collection to limit the port scans, enabling rapid scans on large clusters
* Highly configurable targeting - specify namespaces, nodes, selective ports, or specific IP ranges to scan
* Rich output formats including interactive network graphs, Jupyter notebooks, Elasticsearch integration, and Grafana dashboard support
* Internal and external network visibility - deploy both inside and outside the cluster to scan targets within the cluster and on external networks, helping validate ingress and egress rules
* Flexible scheduling options - run one-time assessments or continuous monitoring with regular automated scans
* Advanced scanning techniques - initiates SYN scans by default with automatic fallback to CONNECT scans on failure

## Repository Structure

This repository contains several components:

- **knetscan**: Kubernetes resource discovery and port scanning engine
- **knetscan-init**: DaemonSet for discovery of open ports on nodes
- **knetscan-wf**: Workflow orchestrator that automates the entire scanning process - deploys components, coordinates scans, collects results, and generates visualizations (similar to a Kubernetes Operator)

## High Level Design

![Workflow Architecture](docs/workflow-arch-diag.png)

*Figure: Knetscan-workflow architecture*

![Tool Architecture](docs/simplistic-arch-diag.png)

*Figure: Knetscan tool architecture*

## Deployment Options

KNetScan offers two primary ways to deploy and use the tool:

### Option 1: Using knetscan-wf (Recommended)

This approach is the simplest way to run KNetScan. [knetscan-wf](knetscan-wf/README.md) automates the entire process, running both external and internal scans, and generating visualization outputs.

The workflow orchestrator sequentially performs the following:
- Runs external scans against your cluster
- Deploys KNetScan-Init to discover open ports
- Deploys KNetScan for internal scanning
- Collects and combines all results
- Generates network graphs and Jupyter notebooks
- Cleans up all resources when done

#### Workflow Results

After running KNetScan using the workflow orchestrator, you'll find these outputs in your results directory (see examples at [docs/wf/sample-output](docs/wf/sample-output)):

* Raw JSON scan results for both internal and external scans
* Interactive network graph in HTML format
* Jupyter notebook for advanced queries and analysis
* Visualization resources (JavaScript, CSS)

### Option 2: Custom Deployment (For Advanced Users)

If you need more control over the scanning process, you can run the internal and external scanners separately.

The external scanner:
- Runs from outside the cluster
- Scans externally accessible IPs and services
- Uses kubeconfig to access cluster information (targets can be overridden via command-line arguments)

The internal scanner:
- Intended to be run as a DaemonSet
- Scans from each node to all the discovered targets across the cluster
- If not using knetscan-init (included as part of the knetscan workflow), knetscan will simply leverage the information it gathers from the K8s API to determine the targets - All internal pod, service, and node IPs.


For more detailed information about each component, see the README files in their respective directories.

## Quick Start

Goto [knetscan-wf README](knetscan-wf/README.md)

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details. 