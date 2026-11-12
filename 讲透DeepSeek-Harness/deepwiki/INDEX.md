# DeepWiki deepseek-ai/deepseek-harness 抓取索引（46/46 全量）

> 来源: https://deepwiki.com/deepseek-ai/deepseek-harness | 抓取: 2026-11-04（0.2.2-alpha.3 世代刷新）| 工具: pipeline-bin/deepwiki/dw_fetch_mcp.py（MCP 通道）
>
> 前代: 2026-09-04 抓取的 39 页（0.1.2 世代）已归档 `_update-20261104/deepwiki-old-202609/`。本代新增 7 页（4.4 native 系统包 / 4.5 SSH 远程执行 / 6.5 桌面应用与 Web Shell 打包 / 7.5 experimental 包 / 7.6 liveshare / 8.4 性能基准与预算 / 9.3 用户指南 cookbook）；全部 slug 规范化（旧 slug 含全角冒号转义）。related/ 三仓概览（cordis/V3.2/MCP）保留前代版本。

| # | 页面 | 主题 |
|---|---|---|
| 1 | [1](1-overview.md) | Overview |
| 2 | [1.1](1.1-getting-started-development-setup.md) | Getting Started & Development Setup |
| 3 | [1.2](1.2-monorepo-structure-package-families.md) | Monorepo Structure & Package Families |
| 4 | [2](2-core-architecture.md) | Core Architecture |
| 5 | [2.1](2.1-cordis-framework-vendored-dependencies.md) | Cordis Framework & Vendored Dependencies |
| 6 | [2.2](2.2-plugin-composition-profiles-bundles-configuration.md) | Plugin Composition: Profiles, Bundles & Configuration |
| 7 | [2.3](2.3-event-bus-capability-seams.md) | Event Bus & Capability Seams |
| 8 | [3](3-agent-system.md) | Agent System |
| 9 | [3.1](3.1-agent-loop-lifecycle.md) | Agent Loop & Lifecycle |
| 10 | [3.2](3.2-tool-registry-execution-pipeline.md) | Tool Registry & Execution Pipeline |
| 11 | [3.3](3.3-session-log-persistence.md) | Session Log & Persistence |
| 12 | [3.4](3.4-subagent-orchestration.md) | Subagent Orchestration |
| 13 | [3.5](3.5-llm-adapters-streaming.md) | LLM Adapters & Streaming |
| 14 | [4](4-execution-environment.md) | Execution Environment |
| 15 | [4.1](4.1-filesystem-tools-observation.md) | Filesystem Tools & Observation |
| 16 | [4.2](4.2-shell-subprocess-terminal.md) | Shell, Subprocess & Terminal |
| 17 | [4.3](4.3-sandboxing-security.md) | Sandboxing & Security |
| 18 | [4.4](4.4-native-system-packages-platform-binaries.md) | Native System Packages & Platform Binaries |
| 19 | [4.5](4.5-ssh-remote-execution-backends.md) | SSH Remote Execution Backends |
| 20 | [5](5-api-layer-host-client-bridge.md) | API Layer & Host-Client Bridge |
| 21 | [5.1](5.1-api-proxy-rpc-protocol.md) | API Proxy & RPC Protocol |
| 22 | [5.2](5.2-typert-type-safe-rpc-generation.md) | Typert: Type-Safe RPC Generation |
| 23 | [5.3](5.3-client-runtime-session-management.md) | Client Runtime & Session Management |
| 24 | [6](6-web-ui.md) | Web UI |
| 25 | [6.1](6.1-conversation-ui-chat-view.md) | Conversation UI & Chat View |
| 26 | [6.2](6.2-workspace-browser-sidebar.md) | Workspace, Browser & Sidebar |
| 27 | [6.3](6.3-ui-primitives-trajectory-tool-views.md) | UI Primitives, Trajectory & Tool Views |
| 28 | [6.4](6.4-settings-agent-presets-onboarding.md) | Settings, Agent Presets & Onboarding |
| 29 | [6.5](6.5-desktop-app-web-shell-packaging.md) | Desktop App & Web Shell Packaging |
| 30 | [7](7-extensions-integrations.md) | Extensions & Integrations |
| 31 | [7.1](7.1-acp-protocol-agent-communication.md) | ACP Protocol & Agent Communication |
| 32 | [7.2](7.2-mcp-client-hooks-skills.md) | MCP Client, Hooks & Skills |
| 33 | [7.3](7.3-goals-todos-workflows-web-tools.md) | Goals, Todos, Workflows & Web Tools |
| 34 | [7.4](7.4-python-sdk-runtime-distribution.md) | Python SDK & Runtime Distribution |
| 35 | [7.5](7.5-experimental-packages-agent-teams-webworker-runtime-inspector.md) | Experimental Packages: Agent Teams, WebWorker Runtime, Inspector |
| 36 | [7.6](7.6-liveshare-session-sharing-tunnel-protocol.md) | Liveshare Session Sharing & Tunnel Protocol |
| 37 | [8](8-testing-quality-infrastructure.md) | Testing & Quality Infrastructure |
| 38 | [8.1](8.1-unit-integration-testing.md) | Unit & Integration Testing |
| 39 | [8.2](8.2-browser-e2e-testing.md) | Browser E2E Testing |
| 40 | [8.3](8.3-ci-cd-pipeline.md) | CI/CD Pipeline |
| 41 | [8.4](8.4-performance-benchmarks-budgets.md) | Performance Benchmarks & Budgets |
| 42 | [9](9-documentation-internationalization.md) | Documentation & Internationalization |
| 43 | [9.1](9.1-bilingual-documentation-translation-pairing.md) | Bilingual Documentation & Translation Pairing |
| 44 | [9.2](9.2-type-equivalence-doc-verification-gates.md) | Type Equivalence & Doc Verification Gates |
| 45 | [9.3](9.3-user-guides-cookbooks.md) | User Guides & Cookbooks |
| 46 | [10](10-glossary.md) | Glossary |
