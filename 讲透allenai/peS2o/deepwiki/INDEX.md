# DeepWiki 索引 — allenai/peS2o

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-26
> 结构 15 页 · 全文 87939 字符

- [1 Overview](1-overview.md)
  - [1.1 Dataset Description and Schema](1.1-dataset-description-and-schema.md)
  - [1.2 Filtering Heuristics and Quality Criteria](1.2-filtering-heuristics-and-quality-criteria.md)
- [2 Data Pipeline Architecture](2-data-pipeline-architecture.md)
  - [2.1 Stage 1 – Data Extraction (SQL Queries)](2.1-stage-1-data-extraction-sql-queries.md)
  - [2.2 Stage 2 – Python Processing Scripts](2.2-stage-2-python-processing-scripts.md)
  - [2.3 Stage 3 – Loading Data as Athena Tables](2.3-stage-3-loading-data-as-athena-tables.md)
  - [2.4 Stage 4 – Final Mixing and Dataset Production](2.4-stage-4-final-mixing-and-dataset-production.md)
- [3 Quality Metrics and Statistics](3-quality-metrics-and-statistics.md)
  - [3.1 get_stats.py – Token and Document Counting](3.1-get-stats.py-token-and-document-counting.md)
  - [3.2 Perplexity and Language Quality Signals](3.2-perplexity-and-language-quality-signals.md)
- [4 Development Environment and Tooling](4-development-environment-and-tooling.md)
  - [4.1 Dependencies and Environment Setup](4.1-dependencies-and-environment-setup.md)
  - [4.2 IDE and Repository Configuration](4.2-ide-and-repository-configuration.md)
- [5 Glossary](5-glossary.md)
