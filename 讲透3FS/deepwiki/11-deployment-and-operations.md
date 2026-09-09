> 来源: [https://deepwiki.com/deepseek-ai/3FS/11-deployment-and-operations](https://deepwiki.com/deepseek-ai/3FS/11-deployment-and-operations)
> DeepWiki deepseek-ai/3FS

# Deployment and Operations

  Relevant source files 
 - [.clang-tidy](https://github.com/deepseek-ai/3FS/blob/22fca045/.clang-tidy)
 - [README.md](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1)
 - [deploy/README.md](https://github.com/deepseek-ai/3FS/blob/22fca045/deploy/README.md?plain=1)
 - [deploy/data_placement/README.md](https://github.com/deepseek-ai/3FS/blob/22fca045/deploy/data_placement/README.md?plain=1)
 - [dockerfile/dev.opencloudos9.dockerfile](https://github.com/deepseek-ai/3FS/blob/22fca045/dockerfile/dev.opencloudos9.dockerfile)
 
  This section provides a high-level overview of the deployment process, hardware requirements, and operational procedures for the Fire-Flyer File System (3FS). 3FS is designed for high-performance AI workloads and utilizes a disaggregated architecture that separates metadata management from data storage.

 
## System Topology and Service Roles

 A standard 3FS deployment consists of four primary service types and two external dependencies (FoundationDB and ClickHouse). The services are typically distributed across metadata nodes and storage nodes to maximize throughput and reliability.

 
### Service Architecture Diagram

 The following diagram illustrates the relationship between the physical nodes and the software entities defined in the codebase.

 
```

```

 **Sources:** [deploy/README.md41-53](https://github.com/deepseek-ai/3FS/blob/22fca045/deploy/README.md?plain=1#L41-L53) [README.md9-11](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1#L9-L11)

 
### Service Definitions

 
| Service | Binary | Code Entity | Description |
|---|---|---|---|
| Monitor | monitor_collector_main | MonitorCollector | Collects metrics and reports to ClickHouse deploy/README.md47 |
| Mgmtd | mgmtd_main | MgmtdService | Manages cluster state, node leases, and routing deploy/README.md49 |
| Meta | meta_main | MetaService | Handles file system metadata via FoundationDB deploy/README.md50 |
| Storage | storage_main | StorageOperator | Manages data chunks on NVMe SSDs using CRAQ deploy/README.md51 |
| Client | hf3fs_fuse_main | FuseOps | Provides FUSE mount point for user applications deploy/README.md52 |

 
## Hardware Requirements

 3FS is optimized for modern hardware, specifically targeting NVMe SSDs and high-speed RDMA networking (InfiniBand or RoCE).

 
 - **Storage Nodes:** Typically equipped with multiple NVMe SSDs (e.g., 16 x 14TiB) and high-bandwidth NICs (200Gbps/400Gbps) [README.md30](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1#L30-L30) [deploy/README.md12-16](https://github.com/deepseek-ai/3FS/blob/22fca045/deploy/README.md?plain=1#L12-L16)
 - **Metadata Nodes:** Require high memory capacity (e.g., 128GB+) and low-latency access to the FoundationDB cluster [deploy/README.md11](https://github.com/deepseek-ai/3FS/blob/22fca045/deploy/README.md?plain=1#L11-L11)
 - **Network:** RDMA connectivity is mandatory for performance. Connectivity should be verified using `ib_write_bw` [deploy/README.md18-20](https://github.com/deepseek-ai/3FS/blob/22fca045/deploy/README.md?plain=1#L18-L20)
 
 For details on specific hardware configurations and OS prerequisites, see [Cluster Setup Guide](https://deepwiki.com/deepseek-ai/3FS/11.1-cluster-setup-guide).

 
## Data Placement and Fault Tolerance

 3FS uses a sophisticated data placement strategy based on **Balanced Incomplete Block Design (BIBD)** to ensure uniform load distribution and fault tolerance.

 
### Data Placement Logic

 The system utilizes a solver-based approach to generate "chain tables," which define how data chunks are replicated across storage targets. This process involves:

 
 - Formulating the placement as an optimization problem using `Pyomo` [deploy/data_placement/README.md11-12](https://github.com/deepseek-ai/3FS/blob/22fca045/deploy/data_placement/README.md?plain=1#L11-L12)
 - Solving for an optimal distribution using the `HiGHS` solver [deploy/data_placement/README.md11-12](https://github.com/deepseek-ai/3FS/blob/22fca045/deploy/data_placement/README.md?plain=1#L11-L12)
 - Generating an incidence matrix that maps replication chains to specific storage nodes and disks [deploy/data_placement/README.md63-64](https://github.com/deepseek-ai/3FS/blob/22fca045/deploy/data_placement/README.md?plain=1#L63-L64)
 
 
```

```

 **Sources:** [deploy/data_placement/README.md23-24](https://github.com/deepseek-ai/3FS/blob/22fca045/deploy/data_placement/README.md?plain=1#L23-L24) [deploy/data_placement/README.md63-72](https://github.com/deepseek-ai/3FS/blob/22fca045/deploy/data_placement/README.md?plain=1#L63-L72)

 For details on generating these tables and optimizing for your specific node count, see [Data Placement and Chain Table Generation](https://deepwiki.com/deepseek-ai/3FS/11.2-data-placement-and-chain-table-generation).

 
## Operational Workflow

 Operating a 3FS cluster involves several key stages:

 
 - **Deployment:** Services are managed via `systemd`. Units like `mgmtd_main.service` and `storage_main.service` are used to control the lifecycle of the daemons [deploy/README.md157-158](https://github.com/deepseek-ai/3FS/blob/22fca045/deploy/README.md?plain=1#L157-L158)
 - **Configuration:** Cluster-wide settings are managed through `.toml` files and the `admin_cli` tool. 3FS supports hot-updating certain configurations via the management service [deploy/README.md107-113](https://github.com/deepseek-ai/3FS/blob/22fca045/deploy/README.md?plain=1#L107-L113)
 - **Initialization:** The `admin_cli` command `init-cluster` is used to bootstrap the management service with initial chunk sizes and striping configurations [deploy/README.md146-154](https://github.com/deepseek-ai/3FS/blob/22fca045/deploy/README.md?plain=1#L146-L154)
 - **Monitoring:** Metrics are exported to ClickHouse and can be visualized to monitor throughput, IOPS, and latency [deploy/README.md74-85](https://github.com/deepseek-ai/3FS/blob/22fca045/deploy/README.md?plain=1#L74-L85)
 
 For a full list of configuration parameters and their effects, see [Configuration Reference](https://deepwiki.com/deepseek-ai/3FS/11.3-configuration-reference).

 
## Child Pages

 
 - [Cluster Setup Guide](https://deepwiki.com/deepseek-ai/3FS/11.1-cluster-setup-guide) — Step-by-step guide for deploying a 3FS cluster including hardware prerequisites, service installation order, and configuration management.
 - [Data Placement and Chain Table Generation](https://deepwiki.com/deepseek-ai/3FS/11.2-data-placement-and-chain-table-generation) — Documentation of the data placement optimization model, the `gen_chain_table.py` script, and balanced fault tolerance.
 - [Configuration Reference](https://deepwiki.com/deepseek-ai/3FS/11.3-configuration-reference) — Reference documentation for all service configuration files (`mgmtd_main.toml`, `meta_main.toml`, `storage_main.toml`, `hf3fs_fuse_main.toml`).
