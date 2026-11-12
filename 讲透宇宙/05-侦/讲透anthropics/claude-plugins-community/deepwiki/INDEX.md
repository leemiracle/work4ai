# DeepWiki 索引 — anthropics/claude-plugins-community

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-10-26
> 结构 19 页 · 全文 152410 字符

- [1 Overview](1-overview.md)
  - [1.1 Repository Purpose and Architecture](1.1-repository-purpose-and-architecture.md)
  - [1.2 Getting Started: Installing and Using Plugins](1.2-getting-started-installing-and-using-plugins.md)
- [2 Plugin Marketplace Registry](2-plugin-marketplace-registry.md)
  - [2.1 marketplace.json Schema and Plugin Types](2.1-marketplace.json-schema-and-plugin-types.md)
  - [2.2 Plugin Functional Categories](2.2-plugin-functional-categories.md)
  - [2.3 Plugin Architecture Patterns](2.3-plugin-architecture-patterns.md)
- [3 CI/CD Pipeline: Validation, Bumping, and Scanning](3-ci-cd-pipeline-validation-bumping-and-scanning.md)
  - [3.1 validate-plugins Action](3.1-validate-plugins-action.md)
  - [3.2 bump-plugin-shas Action](3.2-bump-plugin-shas-action.md)
  - [3.3 scan-plugins Action](3.3-scan-plugins-action.md)
- [4 Security Model](4-security-model.md)
  - [4.1 Input Validation and SSRF Protection](4.1-input-validation-and-ssrf-protection.md)
  - [4.2 Signed Commits and Bot-Free Design](4.2-signed-commits-and-bot-free-design.md)
  - [4.3 Policy Scan Security: Credential Exfiltration Detection](4.3-policy-scan-security-credential-exfiltration-detection.md)
- [5 Releasing and Consumer Guidance](5-releasing-and-consumer-guidance.md)
  - [5.1 Action Release Process](5.1-action-release-process.md)
  - [5.2 Claude CLI Installation and Self-Healing](5.2-claude-cli-installation-and-self-healing.md)
- [6 Glossary](6-glossary.md)

## 附：结构清单外的页
- [Bump Workflow and Freeze List](x1-bump-workflow-and-freeze-list.md)
- [Change Detection and External Manifest Resolution](x2-change-detection-and-external-manifest-resolution.md)
- [Invariants I1–I11: Security and Policy Rules](x3-invariants-i1-i11-security-and-policy-rules.md)
- [Shared Library: common.sh Utilities](x4-shared-library-common.sh-utilities.md)

## 附：补页（第三轮）
- [3.1.1 Invariants I1–I11: Security and Policy Rules](x5-invariants-i1i11-security-and-policy-rules.md)
