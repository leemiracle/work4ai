# KNetScan Workflow

KNetScan Workflow is an orchestration tool that automates the complete port scanning process for Kubernetes clusters using knetscan and knetscan-init. It simplifies deployment by running all necessary components in the right sequence and collecting results for visualization.

## What KNetScan Workflow Does

1. Runs external scans from your machine (outside the cluster) against your target cluster
2. Deploys KNetScan Init as a DaemonSet in the cluster to discover listening ports
3. Deploys KNetScan for internal scanning
4. Collects all results from both scans
5. Generates visualization resources (network graph and Jupyter notebook)
6. Cleans up all resources when complete
7. Provides fault tolerance with proper cleanup on errors or interruptions

## Prerequisites

**Your system needs:**
1. `kubectl` installed and configured with admin access to the target cluster
2. `nmap` installed for external scans - https://nmap.org/download
3. Go 1.22.0+
4. `knetscan` binary (steps detailed below)

**The target cluster needs:**
1. `knetscan` and `knetscan-init` images available in a registry (steps detailed below)
2. Update the registry in helm values files if using custom images (steps detailed below)

### Step 1: Setting Up Docker Images

Before running the workflow, you need to build and push the knetscan and knetscan-init Docker images to a registry accessible by your cluster:

```bash
# Clone this repo
git clone https://github.com/NVIDIA/knetscan.git; cd knetscan

# Set your registry (replace with your actual registry)
export REGISTRY=your-registry.com

# Build and push both images (includes both amd64 and arm64)
cd knetscan
make docker-push

cd ../knetscan-init  
make docker-push
```

### Step 2: Configuring Image Registry in knetscan-wf

Update the embedded values files to use your registry:

```bash
# Edit knetscan values
vi knetscan-wf/values.yaml
# Update: image.repository: your-registry.com/knetscan
# Update: image.tag: v0.0.1  # Use your actual version

# Edit knetscan-init values  
vi knetscan-wf/values-init.yaml
# Update: image.repository: your-registry.com/knetscan-init
# Update: image.tag: v0.0.1  # Use your actual version
```

*Alternatively, you can create custom values files and use the `-values-yaml` and `-init-values-yaml` command-line options.*

### Step 3: Building knetscan binary (skip if Step 1 completed)

The knetscan-wf requires the knetscan binary for external scanning. Step 1's `make docker-push` automatically builds this binary, so you only need this step if you skipped Step 1.

```bash
cd knetscan
make build-all
```

## Quick Start

```bash
# Build knetscan-wf (assumes knetscan binary built per prerequisites)
cd knetscan-wf
make build-all

# Run the workflow (using v0.0.1 as example version)
sudo ./build/v0.0.1/linux-amd64/knetscan-wf \
  -kubeconfig=$HOME/.kube/config \
  -work-dir=/tmp/knetscan-results \
  -exec-path=../knetscan/build/v0.0.1/linux-amd64/knetscan \
  -docker-config=$HOME/.docker/config.json  # Required for accessing container registry during deployment
```
#### Note 1: The docker config file must contain credentials to pull the knetscan and knetscan-init images pushed in [Step 1 from the Prerequisites section](#step-1-setting-up-docker-images) above.
#### Note 2: Replace `linux-amd64` with `darwin-amd64`, `linux-arm64`, or `darwin-arm64` as needed for your platform. Replace `v0.0.1` with your actual version (extracted from git tag).
#### Note 3: MacOS users may need to remove quarantine attributes from the binaries to allow execution
```bash
sudo xattr -rd com.apple.quarantine ./build/v0.0.1/linux-amd64/knetscan-wf
sudo xattr -rd com.apple.quarantine ../knetscan/build/v0.0.1/linux-amd64/knetscan
```

## Command Line Arguments

| Argument | Data type | Description |
| -------- | --------- | ----------- |
| version | bool | Display knetscan-wf version information and exit |
| kubeconfig | string | Absolute path to kubeconfig - When deployed outside the cluster |
| work-dir | string | Path to directory in which workflow related files would be created |
| exec-path | string | Path to the knetscan executable. Default - './knetscan' |
| skip-scan | string | Skip one of the scan types - internal or external. Format - '-skip-scan internal OR -skip-scan external' |
| docker-config | string | Absolute path to the docker config file that provides access to the container repo. Default - $HOME/.docker/config.json |
| ext-scan-ports | string | Override the default ports scanned by the external scanner(Provide in nmap compliant format - "1,2,4-6") |
| init-values-yaml | string | Absolute path to the Knetscan-init chart values.yaml file for internal scan. If not provided, default settings would be used for the scan |
| values-yaml | string | Absolute path to the Knetscan chart values.yaml file for internal scan. If not provided, default settings would be used for the scan |
| helm-cache-path | string | Helm cache path. If not provided, will use helm's default values |
| helm-config-path | string | Helm config path. If not provided, will use helm's default values |
| only-parse-path | string | If mentioned, all scans will be skipped. KNetScan output .json files at this path will be used to generate cleansed results. Results posted at the same path |
| ignore-scan-fails | bool | Removes the scan failures from the generated results |
| log-dir | string | Directory where the log file resides. If not specified, logs to stderr |
| log-format | string | Defines the logging mode to either console or json |
| log-level | string | Defines the logging level. Choose from one of: fatal, error, warn, info, debug |

## Output Structure

After running the workflow, the results will be in the specified work directory with this structure:

```
/work-dir/knetscan/<timestamp>/
├── external/
│   └── <scan-results>.json    # Raw JSON output from external scans
├── internal/
│   └── <scan-results>.json    # Raw JSON output from internal scans
├── results/
│   ├── d3.v7.min.js
│   ├── network.js
│   └── network-graph.html     # Interactive network visualization
└── KNetScan-Queries.ipynb     # Jupyter notebook for advanced queries
```

## Using the Network Graph

Open the `network-graph.html` file in any web browser to visualize the network connections discovered by KNetScan. This interactive graph shows:

- Nodes representing Kubernetes resources
- Connections representing open network paths
- Port information on connections
- Filtering options for better analysis

## Using the Jupyter Notebook

To use the generated Jupyter notebook for advanced analysis:

1. Install [Jupyter](https://jupyter.org/install)
2. Install the [Go Kernel](https://github.com/gopherdata/gophernotes) for Jupyter
3. Run `jupyter lab` in the results directory
4. Open `KNetScan-Queries.ipynb` and run the cells
5. Customize queries as needed for your specific analysis needs

## License
SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.

SPDX-License-Identifier: Apache-2.0
