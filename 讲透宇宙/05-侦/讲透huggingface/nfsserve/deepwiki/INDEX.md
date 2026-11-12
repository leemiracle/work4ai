# DeepWiki 索引 — huggingface/nfsserve

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-26
> 结构 21 页 · 全文 121759 字符

- [1 Overview](1-overview.md)
  - [1.1 Getting Started](1.1-getting-started.md)
  - [1.2 Project Structure and Module Map](1.2-project-structure-and-module-map.md)
- [2 Core Architecture](2-core-architecture.md)
  - [2.1 TCP Transport Layer](2.1-tcp-transport-layer.md)
  - [2.2 RPC Wire Protocol](2.2-rpc-wire-protocol.md)
  - [2.3 XDR Serialization Framework](2.3-xdr-serialization-framework.md)
  - [2.4 Request Context and Transaction Tracking](2.4-request-context-and-transaction-tracking.md)
- [3 Protocol Handlers](3-protocol-handlers.md)
  - [3.1 Portmap Handler](3.1-portmap-handler.md)
  - [3.2 Mount Handler](3.2-mount-handler.md)
  - [3.3 NFS v3 Handler](3.3-nfs-v3-handler.md)
- [4 Virtual File System (VFS) Interface](4-virtual-file-system-vfs-interface.md)
  - [4.1 NFSFileSystem Trait Reference](4.1-nfsfilesystem-trait-reference.md)
  - [4.2 DemoFS — In-Memory Filesystem](4.2-demofs-in-memory-filesystem.md)
  - [4.3 MirrorFS — Local Filesystem Proxy](4.3-mirrorfs-local-filesystem-proxy.md)
  - [4.4 Filesystem Utilities (fs_util)](4.4-filesystem-utilities-fs-util.md)
- [5 Infrastructure and Tooling](5-infrastructure-and-tooling.md)
  - [5.1 CI Pipeline](5.1-ci-pipeline.md)
  - [5.2 Build Configuration and Feature Flags](5.2-build-configuration-and-feature-flags.md)
- [6 Glossary](6-glossary.md)
