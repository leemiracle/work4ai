# DeepWiki 索引 — openJiuwen-ai/agent-infer

> 通道 mcp.deepwiki.com API（网页端被 Vercel 盾，MCP 直连可用）· 抓取 2026-11-02
> 结构 27 页 · 全文 302761 字符

- [1 Overview](1-overview.md)
  - [1.1 Getting Started & Installation](1.1-getting-started-installation.md)
  - [1.2 Documentation Map (docs/ en & zh)](1.2-documentation-map-docs-en-zh.md)
- [2 Scheduling Core (agentinfer.scheduling)](2-scheduling-core-agentinfer.scheduling.md)
  - [2.1 Scheduling Contracts and Domain Model](2.1-scheduling-contracts-and-domain-model.md)
  - [2.2 ProgramScheduler Runtime](2.2-programscheduler-runtime.md)
  - [2.3 Progress-TTL Policy](2.3-progress-ttl-policy.md)
  - [2.4 Observability and Metrics](2.4-observability-and-metrics.md)
- [3 AgentCache: vLLM Integration Layer](3-agentcache-vllm-integration-layer.md)
  - [3.1 Scheduler Bridges and Controller Factory](3.1-scheduler-bridges-and-controller-factory.md)
  - [3.2 API Adapter: Identity and Lifecycle Middleware](3.2-api-adapter-identity-and-lifecycle-middleware.md)
  - [3.3 Entrypoints, LLM Wrapper and AgentRouter](3.3-entrypoints-llm-wrapper-and-agentrouter.md)
- [4 AgentBench: Benchmarking Harness](4-agentbench-benchmarking-harness.md)
  - [4.1 Benchkit Orchestration and CLI](4.1-benchkit-orchestration-and-cli.md)
  - [4.2 Artifacts, Metrics and Comparison](4.2-artifacts-metrics-and-comparison.md)
  - [4.3 Agent Runtime Adapters](4.3-agent-runtime-adapters.md)
  - [4.4 Request Proxy and Trace Replay](4.4-request-proxy-and-trace-replay.md)
- [5 Testing and Quality Infrastructure](5-testing-and-quality-infrastructure.md)
  - [5.1 Test Suites and Markers](5.1-test-suites-and-markers.md)
  - [5.2 End-to-End Scheduler Comparison Harness](5.2-end-to-end-scheduler-comparison-harness.md)
  - [5.3 CI, Pre-commit and Contribution Workflow](5.3-ci-pre-commit-and-contribution-workflow.md)
- [6 Developer Skills and Tooling](6-developer-skills-and-tooling.md)
  - [6.1 ac-* Skill Packs](6.1-ac-skill-packs.md)
  - [6.2 ac-review Criteria System](6.2-ac-review-criteria-system.md)
  - [6.3 Calibration Tools](6.3-calibration-tools.md)
  - [6.4 Design Documents](6.4-design-documents.md)
- [7 Glossary](7-glossary.md)

## 附：结构清单外的页
- [Configuration, Factors and Rolling Statistics](x1-configuration-factors-and-rolling-statistics.md)
- [ProgressTTLStrategy Decision Logic](x2-progressttlstrategy-decision-logic.md)
- [Transitions and Strategy Interface](x3-transitions-and-strategy-interface.md)
