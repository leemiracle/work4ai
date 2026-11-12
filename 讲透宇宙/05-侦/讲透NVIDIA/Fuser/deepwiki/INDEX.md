# DeepWiki 索引 — NVIDIA/Fuser

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-26
> 结构 24 页 · 全文 349314 字符

- [1 Overview](1-overview.md)
  - [1.1 System Architecture](1.1-system-architecture.md)
  - [1.2 Getting Started](1.2-getting-started.md)
- [2 Core IR System](2-core-ir-system.md)
  - [2.1 IR Nodes and Tensor Views](2.1-ir-nodes-and-tensor-views.md)
  - [2.2 Fusion Representation](2.2-fusion-representation.md)
  - [2.3 Expression Simplification](2.3-expression-simplification.md)
- [3 Code Generation](3-code-generation.md)
  - [3.1 CUDA Kernel Generation](3.1-cuda-kernel-generation.md)
  - [3.2 Index Computation](3.2-index-computation.md)
  - [3.3 Host IR and Execution](3.3-host-ir-and-execution.md)
- [4 Scheduling System](4-scheduling-system.md)
  - [4.1 Scheduler Registry and Types](4.1-scheduler-registry-and-types.md)
  - [4.2 Matrix Multiplication Scheduling](4.2-matrix-multiplication-scheduling.md)
  - [4.3 Normalization and Reduction Scheduling](4.3-normalization-and-reduction-scheduling.md)
- [5 Multi-Device Support](5-multi-device-support.md)
  - [5.1 Tensor Sharding](5.1-tensor-sharding.md)
  - [5.2 Communication Primitives](5.2-communication-primitives.md)
- [6 Python Frontend](6-python-frontend.md)
  - [6.1 Fusion Definition](6.1-fusion-definition.md)
  - [6.2 Fusion Cache and Serialization](6.2-fusion-cache-and-serialization.md)
- [7 Build System](7-build-system.md)
  - [7.1 CMake Configuration](7.1-cmake-configuration.md)
  - [7.2 Python Package Setup](7.2-python-package-setup.md)
