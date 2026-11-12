# DeepWiki deepseek-ai/deepseek-harness 抓取索引（39/39 全量）

> 来源: https://deepwiki.com/deepseek-ai/deepseek-harness | 抓取: 2026-09-04 | 工具: pipeline-bin/deepwiki/dw_fetch.py（直连模式）

| # | 页面 | 主题 |
|---|---|---|
| 1 | [1-overview](1-overview.md) | Overview |
| 2 | [1.1-getting-started-and-development-setup](1.1-getting-started-and-development-setup.md) | Getting Started & Development Setup |
| 3 | [1.2-monorepo-structure-and-package-families](1.2-monorepo-structure-and-package-families.md) | Monorepo Structure & Package Families |
| 4 | [10-glossary](10-glossary.md) | Glossary |
| 5 | [2-core-architecture](2-core-architecture.md) | Core Architecture |
| 6 | [2.1-cordis-framework-and-vendored-dependencies](2.1-cordis-framework-and-vendored-dependencies.md) | Cordis Framework & Vendored Dependencies |
| 7 | [2.2-plugin-composition:-profiles-bundles-and-configuration](2.2-plugin-composition：-profiles-bundles-and-configuration.md) | Plugin Composition: Profiles, Bundles & Configuration |
| 8 | [2.3-event-bus-and-capability-seams](2.3-event-bus-and-capability-seams.md) | Event Bus & Capability Seams |
| 9 | [3-agent-system](3-agent-system.md) | Agent System |
| 10 | [3.1-agent-loop-and-lifecycle](3.1-agent-loop-and-lifecycle.md) | Agent Loop & Lifecycle |
| 11 | [3.2-tool-registry-and-execution-pipeline](3.2-tool-registry-and-execution-pipeline.md) | Tool Registry & Execution Pipeline |
| 12 | [3.3-session-log-and-persistence](3.3-session-log-and-persistence.md) | Session Log & Persistence |
| 13 | [3.4-subagent-orchestration](3.4-subagent-orchestration.md) | Subagent Orchestration |
| 14 | [3.5-llm-adapters-and-streaming](3.5-llm-adapters-and-streaming.md) | LLM Adapters & Streaming |
| 15 | [4-execution-environment](4-execution-environment.md) | Execution Environment |
| 16 | [4.1-filesystem-tools-and-observation](4.1-filesystem-tools-and-observation.md) | Filesystem Tools & Observation |
| 17 | [4.2-shell-subprocess-and-terminal](4.2-shell-subprocess-and-terminal.md) | Shell, Subprocess & Terminal |
| 18 | [4.3-sandboxing-and-security](4.3-sandboxing-and-security.md) | Sandboxing & Security |
| 19 | [5-api-layer-and-host-client-bridge](5-api-layer-and-host-client-bridge.md) | API Layer & Host-Client Bridge |
| 20 | [5.1-api-proxy-and-rpc-protocol](5.1-api-proxy-and-rpc-protocol.md) | API Proxy & RPC Protocol |
| 21 | [5.2-typert:-type-safe-rpc-generation](5.2-typert：-type-safe-rpc-generation.md) | Typert: Type-Safe RPC Generation |
| 22 | [5.3-client-runtime-and-session-management](5.3-client-runtime-and-session-management.md) | Client Runtime & Session Management |
| 23 | [6-web-ui](6-web-ui.md) | Web UI |
| 24 | [6.1-conversation-ui-and-chat-view](6.1-conversation-ui-and-chat-view.md) | Conversation UI & Chat View |
| 25 | [6.2-workspace-browser-and-sidebar](6.2-workspace-browser-and-sidebar.md) | Workspace Browser & Sidebar |
| 26 | [6.3-ui-primitives-trajectory-and-tool-views](6.3-ui-primitives-trajectory-and-tool-views.md) | UI Primitives, Trajectory & Tool Views |
| 27 | [6.4-settings-agent-presets-and-onboarding](6.4-settings-agent-presets-and-onboarding.md) | Settings, Agent Presets & Onboarding |
| 28 | [7-extensions-and-integrations](7-extensions-and-integrations.md) | Extensions & Integrations |
| 29 | [7.1-acp-protocol-and-agent-communication](7.1-acp-protocol-and-agent-communication.md) | ACP Protocol & Agent Communication |
| 30 | [7.2-mcp-client-hooks-and-skills](7.2-mcp-client-hooks-and-skills.md) | MCP Client, Hooks & Skills |
| 31 | [7.3-goals-todos-workflows-and-web-tools](7.3-goals-todos-workflows-and-web-tools.md) | Goals, Todos, Workflows & Web Tools |
| 32 | [7.4-python-sdk-and-runtime-distribution](7.4-python-sdk-and-runtime-distribution.md) | Python SDK & Runtime Distribution |
| 33 | [8-testing-and-quality-infrastructure](8-testing-and-quality-infrastructure.md) | Testing & Quality Infrastructure |
| 34 | [8.1-unit-and-integration-testing](8.1-unit-and-integration-testing.md) | Unit & Integration Testing |
| 35 | [8.2-browser-e2e-testing](8.2-browser-e2e-testing.md) | Browser E2E Testing |
| 36 | [8.3-cicd-pipeline](8.3-cicd-pipeline.md) | CI/CD Pipeline |
| 37 | [9-documentation-and-internationalization](9-documentation-and-internationalization.md) | Documentation & Internationalization |
| 38 | [9.1-bilingual-documentation-and-translation-pairing](9.1-bilingual-documentation-and-translation-pairing.md) | Bilingual Documentation & Translation Pairing |
| 39 | [9.2-type-equivalence-and-doc-verification-gates](9.2-type-equivalence-and-doc-verification-gates.md) | Type Equivalence & Doc Verification Gates |
| 40 | [_coverage-check](_coverage-check.md) | DeepWiki 抓取覆盖率检查 |

## related 仓概览（生态依赖）

| 页面 | 说明 |
|---|---|
| [related/cordis.md](related/cordis.md) | 底层组合式框架（时空可组合编程范式，everything-is-a-plugin 的根基） |
| [related/deepseek-v32.md](related/deepseek-v32.md) | DeepSeek 主力模型（dsh 接入的模型家族） |
| [related/mcp-servers.md](related/mcp-servers.md) | MCP 官方服务器生态（mcp 包对接的外部工具源） |
