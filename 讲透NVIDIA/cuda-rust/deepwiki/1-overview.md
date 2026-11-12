<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/cuda-rust · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/clippy.yml](.github/workflows/clippy.yml)
- [.github/workflows/fmt.yml](.github/workflows/fmt.yml)
- [.github/workflows/unit-tests.yml](.github/workflows/unit-tests.yml)
- [.gitignore](.gitignore)
- [Cargo.lock](Cargo.lock)
- [Cargo.toml](Cargo.toml)
- [README.md](README.md)
- [cutile-rs/CONTRIBUTING.md](cutile-rs/CONTRIBUTING.md)
- [cutile-rs/LICENSE](cutile-rs/LICENSE)
- [cutile-rs/README.md](cutile-rs/README.md)
- [cutile-rs/cutile-benchmarks/paper/README.md](cutile-rs/cutile-benchmarks/paper/README.md)

</details>



This wiki page presents a high-level introduction to the **NVIDIA cuda-rust monorepo**, a comprehensive Rust-based ecosystem designed for GPU programming targeting NVIDIA CUDA platforms. The repository integrates multiple related projects and libraries to provide both low-level CUDA driver bindings and high-level Rust abstractions for writing, compiling, and launching CUDA kernels in Rust, as well as an advanced Tile IR framework for safe and flexible GPU kernel development.

The cuda-rust monorepo contains three main components, each with their own specialized responsibilities and synergies:

---

## 1. Shared Host Runtime Crates

A foundational suite of Rust crates that provide safe and ergonomic host-side bindings and runtimes for CUDA development. These crates serve as the shared infrastructure supporting higher-level codebases in this repository.

- **`cuda-bindings`**: A bindgen-generated, raw FFI binding crate for the NVIDIA CUDA driver API. It dynamically loads the `libcuda` library at runtime, enabling flexible compatibility with installed CUDA drivers. The crate abstracts loading and initialization concerns while exposing the full low-level API for fine-grained control.  
- **`cuda-core`**: Implements core abstractions such as `CudaContext`, device memory management types like `DeviceBuffer`, and utilities for CUDA context and runtime management. It also includes support for virtual memory management (VMM), multicast transfers, and single instruction multiple thread (SIMT) host helpers. This crate includes derive macros (`cuda-core-derive`) for convenience attributes like `DeviceCopy` and kernel launch contracts.  
- **`cuda-async`**: Provides facilities for asynchronous execution models of device operations, offering types like `DeviceOperation` and `DeviceFuture`. It handles CUDA stream submission, completion reactors versus spin-loop wait strategies, scheduling policies, CUDA graph capture support, and automatic resource leak detection. This crate builds upon `cuda-core` and shares its runtime.

These crates are designed to be low-level, stable foundations that can be broadly shared and integrated into both the `cuda-oxide` and `cutile-rs` projects.

For deep details on these, see the child page **[Shared Host Runtime Crates](#2)**.

---

## 2. cuda-oxide: Rust-to-PTX Compiler and Runtime

`cuda-oxide` is a cutting-edge Rust compiler backend and runtime tailored to compile native Rust GPU kernels targeting NVIDIA's PTX intermediate representation for CUDA devices.

Key points:

- **Single-source compilation model**: Host and device code live in the same Rust file and are compiled together via the custom `cargo oxide` subcommand, enabling seamless coding workflows without domain-specific languages or separate toolchains.  
- **rustc codegen backend**: Implements a custom rustc backend that generates MIR (Rust's mid-level IR) and progressively lowers it using an MLIR-like internal IR framework called Pliron, eventually emitting LLVM IR and PTX code.  
- **Device-side APIs**: Provides idiomatic Rust-style device APIs for CUDA programming, such as `#[kernel]` and `#[cuda_module]` attributes to define GPU kernels and modules; intrinsics for thread indexing, warp/cluster operations, shared memory, atomics, and barriers; and compile-time kernel policies for specialization without runtime overhead.  
- **Host-side runtime**: Includes the host APIs that leverage `cuda-core` and `cuda-async` for memory management, kernel launching, and asynchronous GPU workflows, supporting closures, typed launch configurations, and safe kernel launches with contracts.  
- **Extensive tooling**: The `cargo-oxide` CLI exposes subcommands for building, running, testing, inspecting generated PTX, viewing compilation pipelines, debugging, sanitizing, and more.

The `cuda-oxide` project's core compiler crates and utilities live under the `cuda-oxide` directory and maintain a complex, evolving compilation pipeline from Rust MIR through custom dialects to PTX.

See the child page **[cuda-oxide: Rust-to-PTX Compiler and Runtime](#3)** for a full breakdown.

---

## 3. cutile-rs: Tile IR GPU Programming Framework

`cutile-rs` is a Rust-native framework built around the Tile IR intermediate representation for GPU kernels, providing a type-safe, memory-safe, and flexible tile-based programming model.

Key features:

- **Memory-safe GPU kernels**: The framework extends Rust's ownership and borrowing rules to device code. Outputs are split into disjoint tiles (mutable regions), while multiple inputs can be safely shared. This ensures data-race freedom by design.  
- **Tile IR backend**: Kernels are written in Rust and JIT-compiled at runtime into Tile IR bytecode which captures the tiled data access patterns and is specialized for the target GPU architecture.  
- **Device DSL and core types**: Provides core abstractions like `Tile`, `Tensor`, `Partition`, `Token`, and atomic types. Supports pointer tiles, shapes, rounding modes, and ordering to enable expressive GPU algorithms.  
- **Compiler frontend passes**: Implements compiler passes for compiling Rust expressions, binary operations, intrinsics, and tile operations, with type inference, bounds checks, and specialization support.  
- **JIT compilation and caching**: Supports runtime compilation, multi-layered caching of specialized kernels keyed by `TileFunctionKey`, host API launchers, and CUDA graph replay.  
- **Host API**: Facilitates launching kernels synchronously, asynchronously, or as CUDA graph replays. Supports autotuning, benchmarking, and warmup phases to optimize execution.  
- **Rich ecosystem**: Includes a variety of example kernels, benchmarks, and tutorials organized in a dedicated book.

`cutile-rs` is provided as a self-contained workspace and crate set alongside `cuda-oxide`. It leverages the shared host crates (`cuda-bindings`, `cuda-core`, `cuda-async`) and runtime, but offers a distinct, higher-level, tile-oriented programming model.

For extensive information, see the child page **[cutile-rs: Tile IR GPU Programming](#4)**.

---

# Relationship and Integration Diagram

```mermaid
graph TB
  subgraph SharedHostCrates["Shared Host Crates"]
    A[cuda-bindings]
    B[cuda-core]
    Bx[cuda-core-derive]
    C[cuda-async]
  end

  subgraph CUDA_OXIDE["cuda-oxide Project"]
    D[rustc-codegen-cuda backend]
    E[Device APIs: #[kernel], #[cuda_module]]
    F[cargo-oxide CLI and tooling]
    G[Host runtime: uses cuda-core + cuda-async]
  end

  subgraph CUTILE_RS["cutile-rs Project"]
    H[Tile IR compiler and JIT]
    I[Device DSL: Tile, Tensor, Partition, Token]
    J[Host API & Kernel Launchers]
    K[Examples, Benchmarks, Tutorials]
  end

  A --> B --> C
  Bx --> B
  B --> G
  C --> G

  B --> H
  C --> J

  H --> I --> J
  J --> K

  D -->|compiles| E
  F -->|invokes| D & G

  style SharedHostCrates fill:#f9f9f9,stroke:#333,stroke-width:1px
  style CUDA_OXIDE fill:#f0f0f0,stroke:#333,stroke-width:1px
  style CUTILE_RS fill:#f0f0f0,stroke:#333,stroke-width:1px
```

*Diagram showing the major components and their code-level relationships. The shared host crates `cuda-bindings`, `cuda-core` (+ `cuda-core-derive`), and `cuda-async` provide foundational runtime and API functionality consumed by both `cuda-oxide` (rustc backend and CLI) and `cutile-rs` (Tile IR compiler and runtime).*

---

# Repository Structure and Workspaces

The repository is organized into multiple Cargo workspaces and nested projects:

| Workspace / Directory | Purpose |
|-----------------------|---------|
| **Root host workspace** | Contains stable host crates shared by both products (`cuda-bindings`, `cuda-core`, `cuda-core-derive`, `cuda-async`). These crates avoid rustc-nightly dependencies where possible to remain broadly compatible. |
| **`cuda-oxide` workspace** | Contains the rustc codegen backend for CUDA as well as device APIs and the `cargo-oxide` CLI tool for building/running/testing Rust CUDA projects. This workspace requires Rust nightly with specialized components and LLVM toolchain. |
| **`cutile-rs` workspace** | Dedicated to the Tile IR framework, comprising libraries for the device DSL, compiler passes, host API, examples, and benchmarks. This workspace targets usability and safety centered on the Tile IR abstraction. |
| **Device-only fixtures** | Kernel-only crates and tests that compile device code without a host component, verifying compile-time properties. |
| **`examples/`** | Cross-workspace examples demonstrating usage of both `cuda-oxide` and `cutile-rs`. |

The workspaces are separate to isolate dependencies, pin toolchains, and scaffold independent development lifecycles. The root workspace dependencies are managed independently to maintain a stable surface for shared runtime crates, while the nested workspaces focus on product-specific needs.  
For detailed layout, workspace rules, dependency pinning, and rationale see the child page **[Repository Layout and Workspaces](#1.1)**.

---

# Getting Started and Toolchain Setup

Setting up a development environment requires several components, including:

- **CUDA Toolkit 13.0+** (recommended 13.3+) for driver libraries and headers. The `cuda-bindings` crate loads the NVIDIA `libcuda` dynamically at runtime.  
- **Rust nightly toolchain** with `rust-src`, `rustc-dev`, and `llvm-tools` components pinned in `rust-toolchain.toml`, required mainly by the `cuda-oxide` backend for compilation. The `cutile-rs` framework primarily supports Rust stable.  
- **Clang and libclang development headers** needed for bindgen to generate CUDA binding crates.  
- **Linux OS**, tested on Ubuntu 24.04 as primary target.  
- Optional: Nix shells or development containers for environment reproducibility.

The repository includes devcontainers and Nix flakes to simplify environment provisioning. The `cargo-oxide` CLI drives the build pipeline for the cuda-oxide backend, handling all toolchain orchestration internally. Example workflows for building, running, inspecting artifacts and debugging are provided via `cargo oxide` subcommands.

For a step-by-step installation guide, toolchain configuration, and first build instructions, see **[Getting Started and Toolchain Setup](#1.2)**.

---

# Summary

The cuda-rust monorepo is a modular, evolving ecosystem designed to empower Rust developers with native support for CUDA GPU programming. It integrates:

- Shared host-side runtime crates (`cuda-bindings`, `cuda-core`, `cuda-async`) that underpin higher-level tooling.  
- `cuda-oxide`, a rustc backend that compiles single-source Rust kernels to PTX with advanced device APIs and a robust CLI.  
- `cutile-rs`, a Tile IR-driven framework with Rust-friendly safety, composability, and JIT compilation for tiled GPU kernels.

These components are developed and versioned in separate Cargo workspaces with stable runtime dependencies shared across projects. Together, they present a path forward for modern, safe, and ergonomic GPU programming in Rust.

---

**Links to Child Pages:**

- Repository Layout and Workspaces: [Repository Layout and Workspaces](#1.1)  
- Getting Started and Toolchain Setup: [Getting Started and Toolchain Setup](#1.2)  
- Shared Host Runtime Crates: [Shared Host Runtime Crates](#2)  
- cuda-oxide Compiler and Runtime: [cuda-oxide: Rust-to-PTX Compiler and Runtime](#3)  
- cutile-rs Tile IR Framework: [cutile-rs: Tile IR GPU Programming](#4)  
- Testing and Quality Infrastructure: [Testing and Quality Infrastructure](#5)  
- Glossary of Terms: [Glossary](#6)  

---

Sources:  
- `README.md:1-159`()  
- `cutile-rs/README.md:1-177`()  
- `Cargo.toml:1-19`()  
- `.github/workflows/unit-tests.yml:1-151`()

---

