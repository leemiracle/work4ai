# DeepWiki 索引 — libingzheren/Jev-Mem

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-13
> 结构 26 页（7 章+19 子页，含 3.3 下两层嵌套）· 全文 267326 字符 · 覆盖 26/26=100%

- [1 Overview](1-overview.md)
  - [1.1 Getting Started](1.1-getting-started.md)
  - [1.2 Configuration Reference](1.2-configuration-reference.md)
- [2 Core System and CLI](2-core-system-and-cli.md)
  - [2.1 JevMemSystem Orchestrator](2.1-jevmemsystem-orchestrator.md)
  - [2.2 Command-Line Interface](2.2-command-line-interface.md)
- [3 Memory Subsystem](3-memory-subsystem.md)
  - [3.1 Memory Construction (Write Path)](3.1-memory-construction-write-path.md)
  - [3.2 Storage Layer](3.2-storage-layer.md)
  - [3.3 Retrieval and Query Engine](3.3-retrieval-and-query-engine.md)
    - [3.3.1 Query Engine Internals](3.3.1-query-engine-internals.md)
    - [3.3.2 Answer Formatting and Best-of-N](3.3.2-answer-formatting-and-best-of-n.md)
  - [3.4 Temporal Handling](3.4-temporal-handling.md)
- [4 System-One Controller (Jev)](4-system-one-controller-jev.md)
  - [4.1 Write and Read Policies](4.1-write-and-read-policies.md)
  - [4.2 Noul/Choice Question Protocol and Client](4.2-noul-choice-question-protocol-and-client.md)
- [5 Benchmarks and Evaluation](5-benchmarks-and-evaluation.md)
  - [5.1 LoCoMo Benchmark](5.1-locomo-benchmark.md)
  - [5.2 LongMemEval Benchmark](5.2-longmemeval-benchmark.md)
  - [5.3 Scoring, Judges and Metrics](5.3-scoring-judges-and-metrics.md)
  - [5.4 Datasets and Examples](5.4-datasets-and-examples.md)
- [6 Project Infrastructure](6-project-infrastructure.md)
  - [6.1 Packaging and Public Release](6.1-packaging-and-public-release.md)
  - [6.2 Testing](6.2-testing.md)
  - [6.3 Utilities and Docs](6.3-utilities-and-docs.md)
- [7 Glossary](7-glossary.md)

> 勘误：dw_fetch_mcp.py 结构解析只认两层缩进，3.3.1/3.3.2 三层嵌套子页曾被记为
> "结构外页"（x1/x2），实际属结构树内，已正名归位。
