> 来源: [https://deepwiki.com/deepseek-ai/3FS/1-3fs-system-overview](https://deepwiki.com/deepseek-ai/3FS/1-3fs-system-overview)
> DeepWiki deepseek-ai/3FS

# 3FS System Overview

  Relevant source files 
 - [.clang-tidy](https://github.com/deepseek-ai/3FS/blob/22fca045/.clang-tidy)
 - [README.md](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1)
 - [dockerfile/dev.opencloudos9.dockerfile](https://github.com/deepseek-ai/3FS/blob/22fca045/dockerfile/dev.opencloudos9.dockerfile)
 - [docs/README.md](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/README.md?plain=1)
 - [docs/design_notes.md](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1)
 - [specs/README.md](https://github.com/deepseek-ai/3FS/blob/22fca045/specs/README.md?plain=1)
 - [src/lib/api/UsrbIo.md](https://github.com/deepseek-ai/3FS/blob/22fca045/src/lib/api/UsrbIo.md?plain=1)
 - [src/stubs/CMakeLists.txt](https://github.com/deepseek-ai/3FS/blob/22fca045/src/stubs/CMakeLists.txt)
 
  
## Purpose and Scope

 This document provides a comprehensive overview of the Fire-Flyer File System (3FS), a high-performance distributed file system specifically designed for AI and machine learning workloads. It introduces the system's disaggregated architecture, key design principles, and performance characteristics.

 For detailed technical explanations, refer to the following child pages:

 
 - [System Architecture](https://deepwiki.com/deepseek-ai/3FS/1.1-system-architecture) — Detailed explanation of 3FS's disaggregated architecture, CRAQ consistency model, storage layers, and supported workloads.
 - [Third-Party Dependencies](https://deepwiki.com/deepseek-ai/3FS/1.2-third-party-dependencies) — Comprehensive overview of external dependencies like RocksDB, FoundationDB, and Folly.
 
 
## What is 3FS?

 The Fire-Flyer File System (3FS) is a distributed file system designed to address the challenges of AI training and inference workloads [README.md6-7](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1#L6-L7) It leverages modern SSDs and RDMA networks to provide a shared storage layer that simplifies the development of distributed applications [README.md6-9](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1#L6-L9)

 
### High-Level System Architecture

 3FS consists of four primary components: a cluster manager (`mgmtd`), a metadata service (`meta`), a storage service (`storage`), and a client [docs/design_notes.md5](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1#L5-L5)

 
```

```

 Sources: [docs/design_notes.md3-14](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1#L3-L14) [src/lib/api/UsrbIo.md3-12](https://github.com/deepseek-ai/3FS/blob/22fca045/src/lib/api/UsrbIo.md?plain=1#L3-L12)

 
### Key Design Principles

 3FS is built around several core design principles that optimize for massive AI datasets:

 
| Principle | Implementation | Benefits |
|---|---|---|
| Disaggregated Architecture | Combines throughput of thousands of SSDs and network bandwidth of hundreds of storage nodes README.md9 | Locality-oblivious access; elastic scaling of compute and storage. |
| Strong Consistency | Chain Replication with Apportioned Queries (CRAQ) README.md10 | Simplifies application logic; "write-all-read-any" approach docs/design_notes.md11 |
| Stateless Metadata | Metadata services backed by FoundationDB README.md11 | High availability and horizontal scalability of metadata operations. |
| Zero-Copy I/O | USRBIO API using shared memory rings (Ior/Iov) src/lib/api/UsrbIo.md3-12 | Bypasses FUSE bottlenecks and memory copy overhead docs/design_notes.md29-32 |

 
## Supported Workloads

 3FS handles diverse AI/ML workload patterns through its flexible file interface and high-performance data path [README.md13-17](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1#L13-L17)

 
### Workload Architecture

 
```

```

 Sources: [README.md14-17](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1#L14-L17) [docs/design_notes.md11-13](https://github.com/deepseek-ai/3FS/blob/22fca045/docs/design_notes.md?plain=1#L11-L13)

 
### Workload Characteristics

 
 - **Data Preparation**: Manages large volumes of intermediate outputs efficiently using hierarchical directory structures [README.md14](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1#L14-L14)
 - **Dataloaders**: Enables random access to training samples across compute nodes, eliminating the need for prefetching or shuffling [README.md15](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1#L15-L15)
 - **Checkpointing**: Supports high-throughput parallel checkpointing for large-scale training [README.md16](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1#L16-L16)
 - **KVCache for Inference**: Provides a cost-effective alternative to DRAM-based caching for LLMs, offering significantly larger capacity [README.md17](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1#L17-L17)
 
 
## Performance Characteristics

 3FS delivers exceptional performance by utilizing RDMA networks and NVMe SSDs.

 
### Performance Metrics

 
 - **Peak Throughput**: Reached approximately 6.6 TiB/s aggregate read throughput on a 180-node cluster [README.md30](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1#L30-L30)
 - **GraySort**: Achieved 3.66 TiB/min average throughput when sorting 110.5 TiB of data [README.md40](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1#L40-L40)
 - **KVCache**: Peak read throughput reaching up to 40 GiB/s for inference clients [README.md50](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1#L50-L50)
 
 
### Benchmarking Infrastructure

 3FS includes specialized tools for performance validation:

 
 - **fio engine for USRBIO**: An FIO plugin located at `benchmarks/fio_usrbio/` for standard benchmarking [README.md34](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1#L34-L34)
 - **Storage Bench**: A C++ framework for stress testing the storage layer.
 
 
## System Components and Technology Stack

 3FS uses a polyglot approach, combining C++ for core services and networking with Rust for the storage engine and system utilities.

 
### Technology Mapping

 
| Category | Component / Library | Purpose |
|---|---|---|
| Core Services | C++17/20 | mgmtd, meta, storage, and hf3fs_fuse docs/design_notes.md5-13 |
| Storage Engine | Rust (chunk_engine) | High-performance local SSD management README.md120 |
| Metadata Store | FoundationDB | Transactional persistence for file metadata README.md98 |
| Networking | RDMA / InfiniBand | Low-latency, high-bandwidth communication docs/design_notes.md5 |
| Client Interface | libfuse 3.16.1+ | POSIX compatibility for standard applications README.md97 |

 
## Getting Started

 To begin working with 3FS, the repository must be cloned with submodules initialized and patches applied [README.md57-66](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1#L57-L66)

 
```

```

 
### Build Requirements

 
 - **Compiler**: Clang-14 is required for building the C++ components [README.md108](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1#L108-L108)
 - **Rust**: Version 1.75.0 (minimal) or 1.85.0 (recommended) [README.md99](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1#L99-L99)
 - **Build System**: CMake is used to orchestrate both C++ and Rust (via Cargo) builds [README.md107-111](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1#L107-L111)
 
 For detailed deployment instructions, see the [Setup Guide](https://github.com/deepseek-ai/3FS/blob/22fca045/Setup Guide) [README.md22](https://github.com/deepseek-ai/3FS/blob/22fca045/README.md?plain=1#L22-L22)
