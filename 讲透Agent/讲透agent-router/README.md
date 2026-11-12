# 讲透 agent-router

> theagentrouter/agent-router —— agent 路由器（Go，K8s 原生）：CRD+控制面+Envoy ext_proc 数据面，MCP Gateway+provider fallback+模型虚拟化。
> 本地仓：/usr-data/data2/repos/aaif-projects/repos/agent-router（HEAD 7bcb4547，2026-10-21 聚合）

## 状态（2026-10-26 全链完成 ✅）

| 步骤 | 状态 | 产物 |
|---|---|---|
| DeepWiki 全量 | ✅ | [deepwiki/](deepwiki/)（**43 页 100%**，全文 388K 字符，mcp.deepwiki.com 直连，2026-10-21） |
| understand 中文图谱 | ✅ | 仓内 `.understand-anything/knowledge-graph.json`（**3083 节点/12740 边/15 层/16 步 tour，validator 0 issues 0 warnings，fingerprints 1010 文件@7bcb4547**；57 批 4 并发，site/ 文档站 473 文件已裁——其知识由 DeepWiki 43 页覆盖，2026-10-26） |
| onboarding | ✅ | [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)（4008 汉字/16,405 非空白字符/8 节） |
| explain 系列 | ✅ | [explain/](explain/) 12 篇（44,574 非空白字符合计；主线：01 extproc 数据面 · 02 translator 契约 · 03 OpenAI/Bedrock provider · 04 MCPProxy 时代 · 05 quota 链 · 06 token 成本累计 · 07 双版本 CRD · 08 controller 装配 · 09 凭据轮换跨 ns · 10 tracing 双 semconv · 11 ExtensionServer xDS · 12 测试资产 cassettes/spans） |

## DeepWiki 章节速览（13 章）

1 Overview · 2 Kubernetes API and CRDs · 3 Control Plane · 4 Data Plane: External Processor · 5 API Schemas and Translation · 6 MCP Gateway · 7 Observability · 8 aigw CLI and Standalone Mode · 9 Deployment and Operations · 10 Testing Infrastructure · 11 Documentation Site · 12 Traffic Management Capabilities · 13 Glossary

深水区提示：12.1 Provider Fallback and Model Virtualization 是本仓差异化能力所在。

入口：[deepwiki/INDEX.md](deepwiki/INDEX.md) · 覆盖率：[deepwiki/_coverage-check.md](deepwiki/_coverage-check.md)
