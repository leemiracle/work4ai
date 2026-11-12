# DeepWiki 索引 — NVIDIA/nvalchemi-toolkit

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-26
> 结构 23 页 · 全文 177067 字符

- [1 Overview](1-overview.md)
  - [1.1 Getting Started: Installation and Setup](1.1-getting-started-installation-and-setup.md)
  - [1.2 Core Concepts and Architecture](1.2-core-concepts-and-architecture.md)
- [2 Data Layer](2-data-layer.md)
  - [2.1 AtomicData and Batch Data Structures](2.1-atomicdata-and-batch-data-structures.md)
  - [2.2 Zarr I/O: AtomicDataZarrWriter and AtomicDataZarrReader](2.2-zarr-i-o-atomicdatazarrwriter-and-atomicdatazarrreader.md)
  - [2.3 DataLoader and SizeAwareSampler](2.3-dataloader-and-sizeawaresampler.md)
- [3 Model Layer](3-model-layer.md)
  - [3.1 BaseModelMixin and ModelCard Interface](3.1-basemodelmixin-and-modelcard-interface.md)
  - [3.2 Available Model Wrappers](3.2-available-model-wrappers.md)
- [4 Dynamics Engine](4-dynamics-engine.md)
  - [4.1 BaseDynamics: Core Execution Loop](4.1-basedynamics-core-execution-loop.md)
  - [4.2 Integrators and Optimizers](4.2-integrators-and-optimizers.md)
  - [4.3 Hook System](4.3-hook-system.md)
  - [4.4 Data Sinks: GPUBuffer, HostMemory, and ZarrData](4.4-data-sinks-gpubuffer-hostmemory-and-zarrdata.md)
  - [4.5 FusedStage and DistributedPipeline](4.5-fusedstage-and-distributedpipeline.md)
- [5 Examples and Tutorials](5-examples-and-tutorials.md)
  - [5.1 Basic and Intermediate Examples](5.1-basic-and-intermediate-examples.md)
  - [5.2 Advanced and Distributed Examples](5.2-advanced-and-distributed-examples.md)
- [6 Infrastructure and Development](6-infrastructure-and-development.md)
  - [6.1 CI/CD, Testing, and Code Quality](6.1-ci-cd-testing-and-code-quality.md)
  - [6.2 Documentation Build System](6.2-documentation-build-system.md)
- [7 Glossary](7-glossary.md)
