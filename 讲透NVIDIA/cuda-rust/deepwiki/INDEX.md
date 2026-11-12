# DeepWiki 索引 — NVIDIA/cuda-rust

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-26
> 结构 25 页 · 全文 420129 字符

- [1 Overview](1-overview.md)
  - [1.1 Repository Layout and Workspaces](1.1-repository-layout-and-workspaces.md)
  - [1.2 Getting Started and Toolchain Setup](1.2-getting-started-and-toolchain-setup.md)
- [2 Shared Host Runtime Crates](2-shared-host-runtime-crates.md)
  - [2.1 cuda-bindings: Raw Driver FFI](2.1-cuda-bindings-raw-driver-ffi.md)
  - [2.2 cuda-core: Contexts, Buffers, VMM](2.2-cuda-core-contexts-buffers-vmm.md)
  - [2.3 cuda-async: Async Device Operations](2.3-cuda-async-async-device-operations.md)
- [3 cuda-oxide: Rust-to-PTX Compiler and Runtime](3-cuda-oxide-rust-to-ptx-compiler-and-runtime.md)
  - [3.1 Compilation Pipeline: MIR to PTX](3.1-compilation-pipeline-mir-to-ptx.md)
  - [3.2 Device and Host APIs (cuda-device, cuda-host, cuda-macros)](3.2-device-and-host-apis-cuda-device-cuda-host-cuda-macros.md)
  - [3.3 cargo-oxide CLI](3.3-cargo-oxide-cli.md)
  - [3.4 Examples, Fuzzer and the cuda-oxide Book](3.4-examples-fuzzer-and-the-cuda-oxide-book.md)
- [4 cutile-rs: Tile IR GPU Programming](4-cutile-rs-tile-ir-gpu-programming.md)
  - [4.1 Device DSL and Core Types](4.1-device-dsl-and-core-types.md)
  - [4.2 cutile-compiler: Rust to Tile IR](4.2-cutile-compiler-rust-to-tile-ir.md)
  - [4.3 cutile-macro and Kernel Launchers](4.3-cutile-macro-and-kernel-launchers.md)
  - [4.4 Host API: Launching, Graphs and Autotuning](4.4-host-api-launching-graphs-and-autotuning.md)
  - [4.5 Kernels, Examples and Benchmarks](4.5-kernels-examples-and-benchmarks.md)
  - [4.6 cutile Book and Tutorials](4.6-cutile-book-and-tutorials.md)
- [5 Testing and Quality Infrastructure](5-testing-and-quality-infrastructure.md)
  - [5.1 CI Workflows](5.1-ci-workflows.md)
  - [5.2 Guard Scripts and Policy Enforcement](5.2-guard-scripts-and-policy-enforcement.md)
  - [5.3 Test Suites and Harnesses](5.3-test-suites-and-harnesses.md)
  - [5.4 Contributing and Project Governance](5.4-contributing-and-project-governance.md)
- [6 Glossary](6-glossary.md)

## 附：结构清单外的页
- [Artifacts, Linking and Finalization](x1-artifacts-linking-and-finalization.md)
- [Intrinsics and Target Specs](x2-intrinsics-and-target-specs.md)
- [JIT Compilation, Caching and tileiras](x3-jit-compilation-caching-and-tileiras.md)
- [cutile-ir: Bytecode Representation](x4-cutile-ir-bytecode-representation.md)
