# KNetScan Init
## Discovery Component for KNetScan

KNetScan Init collects the open ports on Kubernetes nodes by running as a privileged container on the host network. This information is then used by the main KNetScan tool to perform targeted scans, significantly improving scan performance.

## Purpose

This component is deployed as a DaemonSet in the Kubernetes cluster to:

1. Run on each node in the cluster
2. Discover all listening ports on each node
3. Output the discovered ports to a shared directory
4. Allow KNetScan to target only relevant ports for scanning

## Build using Docker

```bash
# Build the Docker image
make docker-build
```

## Example Usage

KNetScan Init is typically deployed automatically by the KNetScan Workflow (knetscan-wf), but you can also deploy it manually using its helm chart under charts/knetscan-init.

## Integration with KNetScan

When using the knetscan workflow (knetscan-wf), KNetScan Init is typically deployed automatically. The workflow will:

1. Deploy KNetScan Init as a DaemonSet
2. Wait for all pods to complete discovery
3. Collect the discovered ports
4. Use this data to configure KNetScan for an optimized scan
5. Clean up the KNetScan Init resources when the scan is complete

## License
SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.

SPDX-License-Identifier: Apache-2.0