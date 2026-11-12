# DeepWiki 索引 — huggingface/xet-core

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-26
> 结构 24 页 · 全文 579888 字符

- [1 Overview](1-overview.md)
- [2 Architecture](2-architecture.md)
  - [2.1 Content-Addressable Storage Design](2.1-content-addressable-storage-design.md)
  - [2.2 Data Flow and Processing](2.2-data-flow-and-processing.md)
  - [2.3 Deduplication Architecture](2.3-deduplication-architecture.md)
- [3 Core Components](3-core-components.md)
  - [3.1 Python API (hf_xet)](3.1-python-api-hf-xet.md)
  - [3.2 Data Client and Sessions](3.2-data-client-and-sessions.md)
  - [3.3 CAS Client System](3.3-cas-client-system.md)
  - [3.4 CAS Object Format (XORB)](3.4-cas-object-format-xorb.md)
  - [3.5 Shard Management System](3.5-shard-management-system.md)
  - [3.6 Chunk Caching](3.6-chunk-caching.md)
  - [3.7 Configuration and Runtime](3.7-configuration-and-runtime.md)
  - [3.8 WASM Support](3.8-wasm-support.md)
- [4 User Interfaces](4-user-interfaces.md)
  - [4.1 Command Line Tools](4.1-command-line-tools.md)
  - [4.2 Git LFS Integration](4.2-git-lfs-integration.md)
- [5 File Processing Workflows](5-file-processing-workflows.md)
  - [5.1 Upload Workflow](5.1-upload-workflow.md)
  - [5.2 Download Workflow](5.2-download-workflow.md)
  - [5.3 File Reconstruction](5.3-file-reconstruction.md)
- [6 Development and Build](6-development-and-build.md)
  - [6.1 Workspace Structure and Dependencies](6.1-workspace-structure-and-dependencies.md)
  - [6.2 CI/CD and Release Process](6.2-ci-cd-and-release-process.md)

## 附：结构清单外的页
- [HTTP Client and Retry Logic](x1-http-client-and-retry-logic.md)
- [Remote Client Operations](x2-remote-client-operations.md)
- [Session Shard Interface](x3-session-shard-interface.md)
- [Shard Binary Format](x4-shard-binary-format.md)
- [Shard File Manager](x5-shard-file-manager.md)
