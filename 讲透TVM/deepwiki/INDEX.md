# 讲透TVM · DeepWiki 索引

> 来源 https://deepwiki.com/apache/tvm · 44 页

> ⚠️【2026-09-07 深研勘误】本索引内容基于旧架构期 DeepWiki 快照。tvm @15b607d（2026-09）已发生大清洗：**relay 彻底删除**（relax 独占图 IR）、**TE schedule API 删除**（s_tir Schedule 71 方法替代）、**AutoTVM/Ansor 删库**（meta_schedule+dlight 存活）、**GraphExecutor/AOT/microTVM/tvmc 执行器全删**（只剩 Relax VM）、target CLI 字符串废除（只认 JSON dict）、主干已 LLM serving 化（VM 内置 paged KV/disagg）。勘误全文见 hpc-agent 仓 docs/research/2026-09-07-tvm-deepread.md（勘误 8 条）与三份轴深读 deepread/2026-09-07-tvm-*.md。

- [1-overview](deepwiki/1-overview.md) — Overview
- [1.1-architecture-overview](deepwiki/1.1-architecture-overview.md) — Architecture Overview
- [2-core-irs-and-languages](deepwiki/2-core-irs-and-languages.md) — Core IRs and Languages
- [2.1-tensorir-(tir)](deepwiki/2.1-tensorir-(tir).md) — TensorIR (TIR)
- [2.2-relax-ir](deepwiki/2.2-relax-ir.md) — Relax IR
- [2.3-tvmscript](deepwiki/2.3-tvmscript.md) — TVMScript
- [2.4-tirx-next-generation-kernel-dsl](deepwiki/2.4-tirx-next-generation-kernel-dsl.md) — 2.4 TIRx — Next-Generation Kernel DSL
- [3-operator-libraries](deepwiki/3-operator-libraries.md) — Operator Libraries
- [3.1-transform-operations](deepwiki/3.1-transform-operations.md) — Transform Operations
- [3.2-topi-tvm-operator-inventory](deepwiki/3.2-topi-tvm-operator-inventory.md) — TOPI - TVM Operator Inventory
- [3.3-relax-operators](deepwiki/3.3-relax-operators.md) — Relax Operators
- [4-frontend-systems](deepwiki/4-frontend-systems.md) — Frontend Systems
- [4.1-onnx-frontend](deepwiki/4.1-onnx-frontend.md) — ONNX Frontend
- [4.1.1-onnx-to-relay](deepwiki/4.1.1-onnx-to-relay.md) — ONNX to Relay
- [4.1.2-onnx-to-relax](deepwiki/4.1.2-onnx-to-relax.md) — ONNX to Relax
- [4.2-pytorch-frontend](deepwiki/4.2-pytorch-frontend.md) — PyTorch Frontend
- [4.3-other-model-format-importers](deepwiki/4.3-other-model-format-importers.md) — Other Model Format Importers
- [4.4-nn.module-frontend](deepwiki/4.4-nn.module-frontend.md) — nn.Module Frontend
- [5-compiler-transformations](deepwiki/5-compiler-transformations.md) — Compiler Transformations
- [5.1-relax-transformations](deepwiki/5.1-relax-transformations.md) — Relax Transformations
- [5.2-tir-transformations](deepwiki/5.2-tir-transformations.md) — TIR Transformations
- [5.3-arithmetic-analysis-and-simplification](deepwiki/5.3-arithmetic-analysis-and-simplification.md) — Arithmetic Analysis and Simplification
- [5.4-metaschedule-and-auto-tuning](deepwiki/5.4-metaschedule-and-auto-tuning.md) — MetaSchedule and Auto-Tuning
- [5.5-dataflow-pattern-language](deepwiki/5.5-dataflow-pattern-language.md) — Dataflow Pattern Language
- [6-code-generation](deepwiki/6-code-generation.md) — Code Generation
- [6.1-target-system](deepwiki/6.1-target-system.md) — Target System
- [6.2-llvm-backend](deepwiki/6.2-llvm-backend.md) — LLVM Backend
- [6.3-cuda-backend](deepwiki/6.3-cuda-backend.md) — CUDA Backend
- [6.4-cutlass-integration](deepwiki/6.4-cutlass-integration.md) — CUTLASS Integration
- [6.5-webgpu-backend](deepwiki/6.5-webgpu-backend.md) — WebGPU Backend
- [6.6-byoc-and-external-library-backends](deepwiki/6.6-byoc-and-external-library-backends.md) — BYOC and External Library Backends
- [7-runtime-systems](deepwiki/7-runtime-systems.md) — Runtime Systems
- [7.1-virtual-machine](deepwiki/7.1-virtual-machine.md) — Virtual Machine
- [7.2-webassembly-runtime](deepwiki/7.2-webassembly-runtime.md) — WebAssembly Runtime
- [7.3-runtime-apis-and-device-management](deepwiki/7.3-runtime-apis-and-device-management.md) — Runtime APIs and Device Management
- [7.4-rpc-and-remote-execution](deepwiki/7.4-rpc-and-remote-execution.md) — RPC and Remote Execution
- [7.5-disco-distributed-runtime](deepwiki/7.5-disco-distributed-runtime.md) — Disco Distributed Runtime
- [7.6-java-runtime-(tvm4j)](deepwiki/7.6-java-runtime-(tvm4j).md) — Java Runtime (TVM4J)
- [8-development-infrastructure](deepwiki/8-development-infrastructure.md) — Development Infrastructure
- [8.1-build-system](deepwiki/8.1-build-system.md) — Build System
- [8.2-cicd-pipeline](deepwiki/8.2-cicd-pipeline.md) — CI/CD Pipeline
- [8.3-documentation-system](deepwiki/8.3-documentation-system.md) — Documentation System
- [8.4-community-and-governance](deepwiki/8.4-community-and-governance.md) — Community and Governance
- [9-glossary](deepwiki/9-glossary.md) — Glossary
