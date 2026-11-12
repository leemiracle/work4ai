# DeepWiki 索引 — deepseek-ai/profile-data

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-30
> 结构 17 页 · 全文 141675 字符

- [1 Overview](1-overview.md)
  - [1.1 What is Profiling Data](1.1-what-is-profiling-data.md)
  - [1.2 DeepSeek Framework](1.2-deepseek-framework.md)
- [2 Training Process](2-training-process.md)
  - [2.1 DualPipe Architecture](2.1-dualpipe-architecture.md)
  - [2.2 MoE Layers](2.2-moe-layers.md)
- [3 Inference Process](3-inference-process.md)
  - [3.1 Prefilling Stage](3.1-prefilling-stage.md)
  - [3.2 Decoding Stage](3.2-decoding-stage.md)
  - [3.3 Micro-batch Strategy](3.3-micro-batch-strategy.md)
- [4 Parallel Configurations](4-parallel-configurations.md)
  - [4.1 Expert Parallelism (EP)](4.1-expert-parallelism-ep.md)
  - [4.2 Tensor and Pipeline Parallelism](4.2-tensor-and-pipeline-parallelism.md)
- [5 Visualization and Analysis](5-visualization-and-analysis.md)
  - [5.1 Using Chrome/Edge Tracing Tools](5.1-using-chrome-edge-tracing-tools.md)
  - [5.2 Interpreting the Profiling Data](5.2-interpreting-the-profiling-data.md)
  - [5.3 Performance Optimization Insights](5.3-performance-optimization-insights.md)
