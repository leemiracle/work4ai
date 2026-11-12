# DeepWiki 索引 — NVIDIA/go-ratelimit

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-26
> 结构 23 页 · 全文 137947 字符

- [1 Overview](1-overview.md)
  - [1.1 Getting Started](1.1-getting-started.md)
  - [1.2 Design & Architecture](1.2-design-architecture.md)
- [2 Core Limiter Package](2-core-limiter-package.md)
  - [2.1 Redis-backed Limiters](2.1-redis-backed-limiters.md)
  - [2.2 Resilient & In-Memory Limiters](2.2-resilient-in-memory-limiters.md)
  - [2.3 Limiter Testing](2.3-limiter-testing.md)
- [3 Middleware Layer](3-middleware-layer.md)
  - [3.1 Middleware Variants](3.1-middleware-variants.md)
  - [3.2 ByteCounterWriter & Response Instrumentation](3.2-bytecounterwriter-response-instrumentation.md)
- [4 Key Extraction & Utilities](4-key-extraction-utilities.md)
  - [4.1 Key Generation Functions](4.1-key-generation-functions.md)
  - [4.2 Header Sanitizers](4.2-header-sanitizers.md)
- [5 Configuration & Admin API](5-configuration-admin-api.md)
  - [5.1 ConfigManager & Per-Client Overrides](5.1-configmanager-per-client-overrides.md)
  - [5.2 Admin HTTP Endpoints](5.2-admin-http-endpoints.md)
- [6 High-Level Service Facade](6-high-level-service-facade.md)
- [7 Observability & Logging](7-observability-logging.md)
- [8 Examples & Reference Server](8-examples-reference-server.md)
  - [8.1 Basic & Header-Based Examples](8.1-basic-header-based-examples.md)
  - [8.2 Resilient & Dynamic-Resilient Examples](8.2-resilient-dynamic-resilient-examples.md)
- [9 Development & Contributing](9-development-contributing.md)
- [10 Glossary](10-glossary.md)
