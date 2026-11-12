# DeepWiki 索引 — allenai/sinonym

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-26
> 结构 24 页 · 全文 488497 字符

- [1 Overview](1-overview.md)
- [2 Core Architecture](2-core-architecture.md)
  - [2.1 ChineseNameDetector: Main API](2.1-chinesenamedetector-main-api.md)
  - [2.2 Processing Pipeline](2.2-processing-pipeline.md)
  - [2.3 Batch Processing System](2.3-batch-processing-system.md)
- [3 Service Components](3-service-components.md)
  - [3.1 Normalization Service](3.1-normalization-service.md)
  - [3.2 Ethnicity Classification Service](3.2-ethnicity-classification-service.md)
  - [3.3 Name Parsing Service](3.3-name-parsing-service.md)
  - [3.4 Name Formatting Service](3.4-name-formatting-service.md)
  - [3.5 String Manipulation Utilities](3.5-string-manipulation-utilities.md)
- [4 Data and Type System](4-data-and-type-system.md)
  - [4.1 Name Data Structures](4.1-name-data-structures.md)
  - [4.2 Result Types and Data Classes](4.2-result-types-and-data-classes.md)
  - [4.3 Configuration System](4.3-configuration-system.md)
- [5 Testing](5-testing.md)
  - [5.1 Test Infrastructure and Baseline Management](5.1-test-infrastructure-and-baseline-management.md)
  - [5.2 Chinese Name Test Suites](5.2-chinese-name-test-suites.md)
  - [5.3 Production and Real-World Test Cases](5.3-production-and-real-world-test-cases.md)
  - [5.4 Performance Testing](5.4-performance-testing.md)
  - [5.5 Batch Processing Tests](5.5-batch-processing-tests.md)
- [6 Development and Deployment](6-development-and-deployment.md)
  - [6.1 Build System and Dependencies](6.1-build-system-and-dependencies.md)
  - [6.2 CI/CD Pipeline](6.2-ci-cd-pipeline.md)
