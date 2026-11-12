<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/hf-mount · page 6 Testing · fetched 2026-10-26 -->

# Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/test_mocks.rs](src/test_mocks.rs)
- [src/virtual_fs/prefetch.rs](src/virtual_fs/prefetch.rs)
- [src/virtual_fs/tests.rs](src/virtual_fs/tests.rs)
- [tests/common/mod.rs](tests/common/mod.rs)

</details>



The `hf-mount` test infrastructure is designed to ensure data integrity, POSIX compatibility, and high performance across both FUSE and NFS backends. The suite ranges from low-level unit tests with mocked remote services to full integration tests that interact with the live Hugging Face Hub API and Xet CAS (Content Addressable Storage).

## Test Infrastructure Overview

The testing strategy is divided into three primary layers, each targeting different aspects of the system's reliability:

| Layer | Focus | Key Components |
| :--- | :--- | :--- |
| **Unit Tests** | VFS logic and state transitions | `MockHub`, `MockXet`, `VirtualFs` tests |
| **Integration Tests** | End-to-end bucket/repo lifecycles | `tests/common/mod.rs`, `hf-mount-fuse` binary |
| **POSIX & Benchmarks** | Compliance and performance | `pjdfstest`, `fsx`, `fio`, `bench.rs` |

### Code-to-System Mapping: Test Entities
The following diagram illustrates how testing entities in the codebase map to the functional components they validate.

**Test Entity Relationship Diagram**
```mermaid
graph TD
    subgraph "Unit Test Space"
        ["MockHub"] -- "implements" --> ["HubOps"]
        ["MockXet"] -- "implements" --> ["XetOps"]
        ["VirtualFsTests"] -- "validates" --> ["VirtualFs"]
    end

    subgraph "Integration Test Space"
        ["tests/common/mod.rs"] -- "spawns" --> ["hf-mount-fuse"]
        ["tests/common/mod.rs"] -- "manages" --> ["TestBucket"]
        ["fs_tests.rs"] -- "runs POSIX ops on" --> ["MountPoint"]
    end

    ["VirtualFs"] -- "uses" --> ["HubOps"]
    ["VirtualFs"] -- "uses" --> ["XetOps"]
```
Sources: [src/test_mocks.rs:18-30](), [src/virtual_fs/tests.rs:32-39](), [tests/common/mod.rs:176-193]()

---

## 1. Unit Testing with Mocks

Unit tests reside primarily in `src/virtual_fs/tests.rs` and use a comprehensive mocking layer defined in `src/test_mocks.rs`. This allows for deterministic testing of complex filesystem behaviors like concurrent writes, error propagation, and cache invalidation without requiring network access.

*   **`MockHub`**: Implements the `HubOps` trait to simulate Hub API responses, including tree listings, file metadata (`head_file`), and batch commit operations [src/test_mocks.rs:18-127]().
*   **`MockXet`**: Implements the `XetOps` trait to simulate CAS interactions, including streaming uploads and range downloads [src/test_mocks.rs:209-215]().
*   **State Validation**: Tests verify that `InodeEntry` flags (e.g., `is_dirty`) and `InodeTable` states transition correctly during the `open` -> `write` -> `flush` -> `release` lifecycle [src/virtual_fs/tests.rs:80-106]().

For details on VFS internal testing, see [Functional and POSIX Tests](#6.2).

---

## 2. Integration Test Framework

The integration framework in `tests/common/mod.rs` provides the "glue" for end-to-end testing. It automates the lifecycle of temporary Hugging Face buckets and manages the daemonized mount processes.

*   **Bucket Lifecycle**: Helpers like `setup_bucket` and `delete_bucket` handle authentication via `HF_TOKEN` and communicate with the Hub API to create isolated environments for each test run [tests/common/mod.rs:23-41]().
*   **Mount Management**: The `mount_bucket` function locates the compiled `hf-mount-fuse` binary and spawns it as a child process, polling `/proc/mounts` (on Linux) or checking the mount directory until the filesystem is ready [tests/common/mod.rs:176-210]().
*   **Data Integrity**: The framework includes deterministic pattern generation to verify that bytes written to the mount are identical to those retrieved via the Hub API [tests/common/mod.rs:45-79]().

For details, see [Integration Test Framework](#6.1).

---

## 3. POSIX Compliance and Functional Tests

To ensure `hf-mount` behaves like a standard filesystem, it is subjected to several industry-standard test suites. These tests are orchestrated via `tests/common/fs_tests.rs`.

*   **POSIX Suites**: The system runs `pjdfstest` for syscall correctness and `fsx` for stress-testing concurrent file operations.
*   **Revalidation Logic**: Specific tests verify that the background polling mechanism correctly invalidates the kernel cache when files are modified out-of-band on the Hub.
*   **Write Modes**: Tests cover both `Streaming` (append-only) and `Advanced` (random-access staging) write modes to ensure consistency across different application workloads.

For details, see [Functional and POSIX Tests](#6.2).

---

## 4. Benchmarks and Performance

Performance is tracked using both internal Rust benchmarks and external tools like `fio`.

*   **Throughput**: `bench.rs` measures sequential and random read/write throughput, specifically focusing on the efficiency of the `PrefetchState` adaptive windowing [src/virtual_fs/prefetch.rs:11-22]().
*   **Deduplication**: Benchmarks validate the Xet CAS deduplication speedup when uploading similar files or re-uploading modified files.
*   **Latency**: Close-to-open latency and metadata operation speeds (e.g., `ls -R`) are monitored to ensure the Hub API pagination and caching are performing optimally.

For details, see [Benchmarks and Performance Tests](#6.3).

**Performance Measurement Flow**
```mermaid
graph LR
    ["fio_bench.rs"] -- "triggers" --> ["FUSE/NFS Ops"]
    ["FUSE/NFS Ops"] -- "calls" --> ["VirtualFs"]
    ["VirtualFs"] -- "monitors" --> ["PrefetchState"]
    ["PrefetchState"] -- "adjusts" --> ["window_size"]
    ["window_size"] -- "affects" --> ["Xet_CAS_Download"]
```
Sources: [src/virtual_fs/prefetch.rs:66-85](), [tests/common/mod.rs:3-5]()

---
**Sources:**
- [tests/common/mod.rs:1-210]()
- [src/test_mocks.rs:1-215]()
- [src/virtual_fs/tests.rs:1-211]()
- [src/virtual_fs/prefetch.rs:8-58]()

---

