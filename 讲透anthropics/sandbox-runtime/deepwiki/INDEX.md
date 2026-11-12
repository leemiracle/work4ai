# DeepWiki 索引 — anthropics/sandbox-runtime

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-26
> 结构 26 页 · 全文 208223 字符

- [1 Overview](1-overview.md)
  - [1.1 Getting Started](1.1-getting-started.md)
  - [1.2 Library API](1.2-library-api.md)
- [2 Core Architecture](2-core-architecture.md)
  - [2.1 Configuration System](2.1-configuration-system.md)
  - [2.2 SandboxManager Orchestration](2.2-sandboxmanager-orchestration.md)
  - [2.3 Violation Monitoring](2.3-violation-monitoring.md)
- [3 Platform Backends](3-platform-backends.md)
  - [3.1 Linux Backend (bubblewrap + seccomp)](3.1-linux-backend-bubblewrap-seccomp.md)
  - [3.2 macOS Backend (Seatbelt / sandbox-exec)](3.2-macos-backend-seatbelt-sandbox-exec.md)
  - [3.3 Windows Backend (srt-win + WFP)](3.3-windows-backend-srt-win-wfp.md)
- [4 Network Filtering Layer](4-network-filtering-layer.md)
  - [4.1 HTTP Proxy and TLS Termination](4.1-http-proxy-and-tls-termination.md)
  - [4.2 SOCKS5 Proxy](4.2-socks5-proxy.md)
  - [4.3 Domain Pattern Matching](4.3-domain-pattern-matching.md)
- [5 Credential Protection System](5-credential-protection-system.md)
  - [5.1 Sentinel Registry and Body Substitution](5.1-sentinel-registry-and-body-substitution.md)
  - [5.2 File and Environment Variable Masking](5.2-file-and-environment-variable-masking.md)
  - [5.3 AWS SigV4 Re-signing](5.3-aws-sigv4-re-signing.md)
- [6 Vendor Components](6-vendor-components.md)
  - [6.1 Java Proxy Agent](6.1-java-proxy-agent.md)
  - [6.2 Build System and CI/CD](6.2-build-system-and-ci-cd.md)
- [7 Testing Infrastructure](7-testing-infrastructure.md)
  - [7.1 Integration Tests](7.1-integration-tests.md)
  - [7.2 Unit and Component Tests](7.2-unit-and-component-tests.md)
- [8 Glossary](8-glossary.md)

## 附：结构清单外的页
- [apply-seccomp Native Binary](x1-apply-seccomp-native-binary.md)
- [srt-win Rust Implementation](x2-srt-win-rust-implementation.md)
