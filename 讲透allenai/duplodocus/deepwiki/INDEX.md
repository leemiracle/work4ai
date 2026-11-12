# DeepWiki 索引 — allenai/duplodocus

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-26
> 结构 25 页 · 全文 462778 字符

- [1 Overview](1-overview.md)
  - [1.1 Getting Started](1.1-getting-started.md)
  - [1.2 Architecture Overview](1.2-architecture-overview.md)
- [2 Suffix Array System](2-suffix-array-system.md)
  - [2.1 SA Pipeline Stages](2.1-sa-pipeline-stages.md)
  - [2.2 SA Utilities and Data Structures](2.2-sa-utilities-and-data-structures.md)
  - [2.3 Suffix Table Implementation](2.3-suffix-table-implementation.md)
  - [2.4 Compact Integer Types](2.4-compact-integer-types.md)
  - [2.5 SA Configuration](2.5-sa-configuration.md)
- [3 MinHash Fuzzy Deduplication](3-minhash-fuzzy-deduplication.md)
  - [3.1 MinHash Theory and Algorithm](3.1-minhash-theory-and-algorithm.md)
  - [3.2 MinHash Memory Pipeline](3.2-minhash-memory-pipeline.md)
  - [3.3 MinHash Disk Pipeline](3.3-minhash-disk-pipeline.md)
- [4 Exact Deduplication](4-exact-deduplication.md)
  - [4.1 Exact Memory-Based Deduplication](4.1-exact-memory-based-deduplication.md)
  - [4.2 Exact Disk-Based Deduplication](4.2-exact-disk-based-deduplication.md)
- [5 Advanced Analysis Tools](5-advanced-analysis-tools.md)
  - [5.1 True Jaccard Calculation](5.1-true-jaccard-calculation.md)
- [6 Operational Tools](6-operational-tools.md)
- [7 Development Guide](7-development-guide.md)
  - [7.1 Building and Dependencies](7.1-building-and-dependencies.md)
  - [7.2 Release Process](7.2-release-process.md)
- [8 Reference](8-reference.md)
  - [8.1 Legacy Suffix Table Implementation](8.1-legacy-suffix-table-implementation.md)
  - [8.2 License](8.2-license.md)

## 附：结构清单外的页
- [Make Tables Stage](x1-make-tables-stage.md)
- [Match Finding Stage](x2-match-finding-stage.md)
- [Merge and Annotate Stages](x3-merge-and-annotate-stages.md)
