> 来源: [https://deepwiki.com/deepseek-ai/3FS/3-core-components](https://deepwiki.com/deepseek-ai/3FS/3-core-components)
> DeepWiki deepseek-ai/3FS

# Core Components

  Relevant source files 
 - [src/client/trash_cleaner/Cargo.toml](https://github.com/deepseek-ai/3FS/blob/22fca045/src/client/trash_cleaner/Cargo.toml)
 - [src/client/trash_cleaner/src/main.rs](https://github.com/deepseek-ai/3FS/blob/22fca045/src/client/trash_cleaner/src/main.rs)
 - [src/storage/chunk_engine/Cargo.toml](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/Cargo.toml)
 - [src/storage/chunk_engine/src/bin/bench.rs](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/bin/bench.rs)
 - [src/storage/chunk_engine/src/core/engine.rs](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/core/engine.rs)
 - [src/storage/chunk_engine/src/cxx.rs](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/cxx.rs)
 - [src/storage/chunk_engine/src/meta/meta_store.rs](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/meta/meta_store.rs)
 
  This document provides an overview of the primary Rust-based components that form the core functionality of 3FS. These components implement the storage engine, maintenance utilities, and user-space I/O interfaces. The 3FS Rust workspace consists of crates that handle chunk-based storage operations, cleanup tasks, and FFI bindings for interoperability with the C++ layer.

 For detailed information about individual components, see:

 
 - Chunk storage engine implementation: [Chunk Engine](https://deepwiki.com/deepseek-ai/3FS/3.1-chunk-engine)
 - Cleanup utilities and maintenance: [System Utilities](https://deepwiki.com/deepseek-ai/3FS/3.2-system-utilities)
 - User I/O FFI bindings: [User I/O Interface (USRBIO)](https://deepwiki.com/deepseek-ai/3FS/3.3-user-io-interface-(usrbio))
 
 For information about how these components integrate with the C++ build system, see [Multi-Language Build System](https://deepwiki.com/deepseek-ai/3FS/2.1-multi-language-build-system) and [Rust-C++ Integration](https://deepwiki.com/deepseek-ai/3FS/5.1-rust-c++-integration).

 
## Workspace Architecture

 The Rust components are organized as a Cargo workspace. The workspace contains member crates with distinct responsibilities within the 3FS architecture.

 
### Workspace Structure

 
```

```

 **Sources**: [src/storage/chunk_engine/Cargo.toml1-10](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/Cargo.toml#L1-L10) [src/client/trash_cleaner/Cargo.toml1-8](https://github.com/deepseek-ai/3FS/blob/22fca045/src/client/trash_cleaner/Cargo.toml#L1-L8)

 
## Component Overview

 The core Rust components provide complementary functionality for the 3FS storage system.

 
| Component | Path | Primary Purpose | Key Technologies |
|---|---|---|---|
| chunk_engine | src/storage/chunk_engine | Chunk-based storage engine with RocksDB indexing | RocksDB, cxx, lockmap, derse |
| trash_cleaner | src/client/trash_cleaner | Time-based cleanup utility for removing stale data | chrono, nix, structopt |
| hf3fs-usrbio-sys | src/lib/rs/hf3fs-usrbio-sys | FFI bindings for user-space I/O operations | bindgen, shared_memory |

 **Sources**: [src/storage/chunk_engine/Cargo.toml2-15](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/Cargo.toml#L2-L15) [src/client/trash_cleaner/Cargo.toml2-21](https://github.com/deepseek-ai/3FS/blob/22fca045/src/client/trash_cleaner/Cargo.toml#L2-L21)

 
## Key Code Entities

 The following diagram bridges the natural language concepts to the specific Rust structures and functions used in the codebase.

 
```

```

 **Sources**: [src/storage/chunk_engine/src/core/engine.rs19-30](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/core/engine.rs#L19-L30) [src/storage/chunk_engine/src/meta/meta_store.rs13-34](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/meta/meta_store.rs#L13-L34) [src/client/trash_cleaner/src/main.rs62-135](https://github.com/deepseek-ai/3FS/blob/22fca045/src/client/trash_cleaner/src/main.rs#L62-L135) [src/storage/chunk_engine/src/cxx.rs10-23](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/cxx.rs#L10-L23)

 
## Component Interaction Model

 The storage engine (`chunk_engine`) serves as the primary data management layer, while `trash_cleaner` provides out-of-band maintenance.

 
### chunk_engine

 The `Engine` struct is the central entry point for storage operations [src/storage/chunk_engine/src/core/engine.rs19-28](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/core/engine.rs#L19-L28) It manages a `MetaStore` backed by RocksDB [src/storage/chunk_engine/src/meta/meta_store.rs13-16](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/meta/meta_store.rs#L13-L16) and coordinates chunk allocation across physical storage via `Allocators` [src/storage/chunk_engine/src/core/engine.rs44-49](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/core/engine.rs#L44-L49) It exposes a C++ interface via `cxx` to allow the main 3FS storage service to perform chunk operations [src/storage/chunk_engine/src/cxx.rs88-108](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/cxx.rs#L88-L108)

 For details, see [Chunk Engine](https://deepwiki.com/deepseek-ai/3FS/3.1-chunk-engine).

 
### trash_cleaner

 This utility manages the lifecycle of deleted data. It uses `nix` to perform low-level filesystem operations and `ioctl` to communicate with the 3FS FUSE client [src/client/trash_cleaner/src/main.rs15-30](https://github.com/deepseek-ai/3FS/blob/22fca045/src/client/trash_cleaner/src/main.rs#L15-L30) It identifies expired items based on timestamps in their filenames [src/client/trash_cleaner/src/main.rs175-187](https://github.com/deepseek-ai/3FS/blob/22fca045/src/client/trash_cleaner/src/main.rs#L175-L187) and removes them to reclaim space.

 For details, see [System Utilities](https://deepwiki.com/deepseek-ai/3FS/3.2-system-utilities).

 
### hf3fs-usrbio-sys

 This component provides the low-level FFI glue between the C++ user-space I/O implementation and Rust. It facilitates zero-copy data transfer and shared memory communication required for high-performance I/O paths.

 For details, see [User I/O Interface (USRBIO)](https://deepwiki.com/deepseek-ai/3FS/3.3-user-io-interface-(usrbio)).

 
## Data Flow and Persistence

 The following diagram illustrates how data flows through the Rust components into the underlying storage.

 
```

```

 **Sources**: [src/storage/chunk_engine/src/cxx.rs93-108](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/cxx.rs#L93-L108) [src/storage/chunk_engine/src/core/engine.rs184-206](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/core/engine.rs#L184-L206) [src/storage/chunk_engine/src/meta/meta_store.rs36-47](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/meta/meta_store.rs#L36-L47)

 
## Build Integration

 The Rust components are integrated into the CMake-based C++ build system. The `chunk_engine` crate is compiled as a static library [src/storage/chunk_engine/Cargo.toml9](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/Cargo.toml#L9-L9) and linked into the 3FS storage daemon. A specialized benchmark tool `bench.rs` is also provided for standalone performance validation of the engine [src/storage/chunk_engine/src/bin/bench.rs18-39](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/bin/bench.rs#L18-L39)

 **Sources**: [src/storage/chunk_engine/Cargo.toml8-15](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/Cargo.toml#L8-L15) [src/storage/chunk_engine/src/bin/bench.rs1-16](https://github.com/deepseek-ai/3FS/blob/22fca045/src/storage/chunk_engine/src/bin/bench.rs#L1-L16)
