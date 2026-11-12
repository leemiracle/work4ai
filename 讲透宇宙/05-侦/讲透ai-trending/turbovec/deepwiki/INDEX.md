# DeepWiki 索引 — RyanCodrai/turbovec

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-30
> 结构 24 页 · 全文 188631 字符

- [1 Overview](1-overview.md)
  - [1.1 Getting Started](1.1-getting-started.md)
  - [1.2 Repository Layout](1.2-repository-layout.md)
- [2 Core Rust Library (turbovec)](2-core-rust-library-turbovec.md)
  - [2.1 TurboQuantIndex and IdMapIndex — Public API and Lifecycle](2.1-turboquantindex-and-idmapindex-public-api-and-lifecycle.md)
  - [2.2 TurboQuant Algorithm — Rotation, Codebook, and Encoding](2.2-turboquant-algorithm-rotation-codebook-and-encoding.md)
  - [2.3 SIMD Search Engine — Repacking and Scoring Kernels](2.3-simd-search-engine-repacking-and-scoring-kernels.md)
  - [2.4 Persistence — v7 File Format and Incremental Sync](2.4-persistence-v7-file-format-and-incremental-sync.md)
- [3 Python Bindings and API](3-python-bindings-and-api.md)
  - [3.1 PyO3 Extension Module (_turbovec)](3.1-pyo3-extension-module-turbovec.md)
  - [3.2 Python Package Structure, Utilities, and Build](3.2-python-package-structure-utilities-and-build.md)
- [4 Framework Integrations](4-framework-integrations.md)
  - [4.1 LangChain Integration](4.1-langchain-integration.md)
  - [4.2 LlamaIndex Integration](4.2-llamaindex-integration.md)
  - [4.3 Haystack Integration](4.3-haystack-integration.md)
  - [4.4 Agno Integration](4.4-agno-integration.md)
- [5 Benchmarks](5-benchmarks.md)
  - [5.1 Benchmark Suite](5.1-benchmark-suite.md)
  - [5.2 Results and Visualization](5.2-results-and-visualization.md)
- [6 Build, CI/CD, and Release](6-build-ci-cd-and-release.md)
  - [6.1 Cargo Workspace and Compiler Configuration](6.1-cargo-workspace-and-compiler-configuration.md)
  - [6.2 GitHub Actions — CI and Release Pipelines](6.2-github-actions-ci-and-release-pipelines.md)
  - [6.3 AI-Assisted Development — @tq-bot and PR Review](6.3-ai-assisted-development-tq-bot-and-pr-review.md)
- [7 Glossary](7-glossary.md)
