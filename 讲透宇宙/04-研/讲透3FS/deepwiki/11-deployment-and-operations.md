<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/3FS · page 11 Deployment and Operations · fetched 2026-10-30 -->

# Deployment and Operations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.clang-tidy](.clang-tidy)
- [README.md](README.md)
- [deploy/README.md](deploy/README.md)
- [deploy/data_placement/README.md](deploy/data_placement/README.md)
- [dockerfile/dev.opencloudos9.dockerfile](dockerfile/dev.opencloudos9.dockerfile)

</details>



This section provides a high-level overview of the deployment process, hardware requirements, and operational procedures for the Fire-Flyer File System (3FS). 3FS is designed for high-performance AI workloads and utilizes a disaggregated architecture that separates metadata management from data storage.

## System Topology and Service Roles

A standard 3FS deployment consists of four primary service types and two external dependencies (FoundationDB and ClickHouse). The services are typically distributed across metadata nodes and storage nodes to maximize throughput and reliability.

### Service Architecture Diagram

The following diagram illustrates the relationship between the physical nodes and the software entities defined in the codebase.

```mermaid
graph TD
    subgraph "Control & Metadata Plane"
        [admin_cli] --> [MgmtdService]
        [MgmtdService] --> [FDB_Cluster]
        [MetaService] --> [FDB_Cluster]
    end

    subgraph "Data Plane"
        [StorageService] --> [ChunkEngine]
        [ChunkEngine] --> [RocksDB]
        [StorageService] --> [RDMA_Network]
    end

    subgraph "Client Side"
        [FUSE_Client] --> [MgmtdService]
        [FUSE_Client] --> [MetaService]
        [FUSE_Client] --> [StorageService]
    end

    style [MgmtdService] stroke-dasharray: 5 5
    style [MetaService] stroke-dasharray: 5 5
    style [StorageService] stroke-dasharray: 5 5
```
**Sources:** [deploy/README.md:41-53](), [README.md:9-11]()

### Service Definitions
| Service | Binary | Code Entity | Description |
| :--- | :--- | :--- | :--- |
| **Monitor** | `monitor_collector_main` | `MonitorCollector` | Collects metrics and reports to ClickHouse [deploy/README.md:47](). |
| **Mgmtd** | `mgmtd_main` | `MgmtdService` | Manages cluster state, node leases, and routing [deploy/README.md:49](). |
| **Meta** | `meta_main` | `MetaService` | Handles file system metadata via FoundationDB [deploy/README.md:50](). |
| **Storage** | `storage_main` | `StorageOperator` | Manages data chunks on NVMe SSDs using CRAQ [deploy/README.md:51](). |
| **Client** | `hf3fs_fuse_main` | `FuseOps` | Provides FUSE mount point for user applications [deploy/README.md:52](). |

## Hardware Requirements

3FS is optimized for modern hardware, specifically targeting NVMe SSDs and high-speed RDMA networking (InfiniBand or RoCE).

*   **Storage Nodes:** Typically equipped with multiple NVMe SSDs (e.g., 16 x 14TiB) and high-bandwidth NICs (200Gbps/400Gbps) [README.md:30](), [deploy/README.md:12-16]().
*   **Metadata Nodes:** Require high memory capacity (e.g., 128GB+) and low-latency access to the FoundationDB cluster [deploy/README.md:11]().
*   **Network:** RDMA connectivity is mandatory for performance. Connectivity should be verified using `ib_write_bw` [deploy/README.md:18-20]().

For details on specific hardware configurations and OS prerequisites, see [Cluster Setup Guide](#11.1).

## Data Placement and Fault Tolerance

3FS uses a sophisticated data placement strategy based on **Balanced Incomplete Block Design (BIBD)** to ensure uniform load distribution and fault tolerance.

### Data Placement Logic

The system utilizes a solver-based approach to generate "chain tables," which define how data chunks are replicated across storage targets. This process involves:
1.  Formulating the placement as an optimization problem using `Pyomo` [deploy/data_placement/README.md:11-12]().
2.  Solving for an optimal distribution using the `HiGHS` solver [deploy/data_placement/README.md:11-12]().
3.  Generating an incidence matrix that maps replication chains to specific storage nodes and disks [deploy/data_placement/README.md:63-64]().

```mermaid
graph LR
    [Input_Params] --> [Pyomo_Model]
    [Pyomo_Model] --> [HiGHS_Solver]
    [HiGHS_Solver] --> [Incidence_Matrix]
    [Incidence_Matrix] --> [gen_chain_table.py]
    [gen_chain_table.py] --> [generated_chain_table.csv]
```
**Sources:** [deploy/data_placement/README.md:23-24](), [deploy/data_placement/README.md:63-72]()

For details on generating these tables and optimizing for your specific node count, see [Data Placement and Chain Table Generation](#11.2).

## Operational Workflow

Operating a 3FS cluster involves several key stages:

1.  **Deployment:** Services are managed via `systemd`. Units like `mgmtd_main.service` and `storage_main.service` are used to control the lifecycle of the daemons [deploy/README.md:157-158]().
2.  **Configuration:** Cluster-wide settings are managed through `.toml` files and the `admin_cli` tool. 3FS supports hot-updating certain configurations via the management service [deploy/README.md:107-113]().
3.  **Initialization:** The `admin_cli` command `init-cluster` is used to bootstrap the management service with initial chunk sizes and striping configurations [deploy/README.md:146-154]().
4.  **Monitoring:** Metrics are exported to ClickHouse and can be visualized to monitor throughput, IOPS, and latency [deploy/README.md:74-85]().

For a full list of configuration parameters and their effects, see [Configuration Reference](#11.3).

## Child Pages

*   [Cluster Setup Guide](#11.1) — Step-by-step guide for deploying a 3FS cluster including hardware prerequisites, service installation order, and configuration management.
*   [Data Placement and Chain Table Generation](#11.2) — Documentation of the data placement optimization model, the `gen_chain_table.py` script, and balanced fault tolerance.
*   [Configuration Reference](#11.3) — Reference documentation for all service configuration files (`mgmtd_main.toml`, `meta_main.toml`, `storage_main.toml`, `hf3fs_fuse_main.toml`).

---

