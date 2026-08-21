# DeepWiki 全量归档 · deepseek-ai/deepseek-harness

> 来源：https://deepwiki.com/deepseek-ai/deepseek-harness （DeepWiki/Devin 自动生成 wiki）
> 索引：2026-08-20，commit `141eb6fe`（dsh 0.1.0-rc.8）——与本地克隆 `~/ai/agent/awesome-agents/repos/deepseek-harness` HEAD 一致，全部引文可在本地复核。
> 抓取方式：curl 拉 SSR HTML → 解析 Next.js Flight `id:T<hexlen>` 行内嵌 markdown 源串（39 页 × 每 5 页交叉去重，0 冲突 0 截断）。
> 引文格式：正文 `[path:line-line]()` 指向该 commit 下仓库文件；`<details>` 块列出各页依据源文件。
> 上级：[../02-全量归档与刷新对照.md](../02-全量归档与刷新对照.md)（新旧 wiki 差异与错误复核）· [../01-DeepWiki对照与增补.md](../01-DeepWiki对照与增补.md)（首版对照，基于 2026-08-13/`47f94385` 快照）

## 完整性清单（39/39，按 DeepWiki 导航序）

| # | 归档文件 | 标题 | 字节 | sha1-10 | 二级标题数 |
|---|---|---|---|---|---|
| 1 | [1-overview.md](1-overview.md) | Overview | 9695 | `ba05affeef` | 6 |
| 2 | [1.1-getting-started-and-development-setup.md](1.1-getting-started-and-development-setup.md) | Getting Started & Development Setup | 11469 | `f1c1d9afcb` | 17 |
| 3 | [1.2-monorepo-structure-and-package-families.md](1.2-monorepo-structure-and-package-families.md) | Monorepo Structure & Package Families | 11223 | `5fb3ad0574` | 13 |
| 4 | [2-core-architecture.md](2-core-architecture.md) | Core Architecture | 11710 | `d42b08b6a2` | 9 |
| 5 | [2.1-cordis-framework-and-vendored-dependencies.md](2.1-cordis-framework-and-vendored-dependencies.md) | Cordis Framework & Vendored Dependencies | 12304 | `335fa7cdf8` | 14 |
| 6 | [2.2-plugin-composition-profiles-bundles-and-configuration.md](2.2-plugin-composition-profiles-bundles-and-configuration.md) | Plugin Composition: Profiles, Bundles & Configuration | 13856 | `79c804aba8` | 13 |
| 7 | [2.3-event-bus-and-capability-seams.md](2.3-event-bus-and-capability-seams.md) | Event Bus & Capability Seams | 11807 | `82eab7af36` | 10 |
| 8 | [3-agent-system.md](3-agent-system.md) | Agent System | 8859 | `a5f17fa594` | 10 |
| 9 | [3.1-agent-loop-and-lifecycle.md](3.1-agent-loop-and-lifecycle.md) | Agent Loop & Lifecycle | 10876 | `9fd30892ea` | 15 |
| 10 | [3.2-tool-registry-and-execution-pipeline.md](3.2-tool-registry-and-execution-pipeline.md) | Tool Registry & Execution Pipeline | 12188 | `60eaf7cbe7` | 10 |
| 11 | [3.3-session-log-and-persistence.md](3.3-session-log-and-persistence.md) | Session Log & Persistence | 13629 | `9ea7a032ae` | 13 |
| 12 | [3.4-subagent-orchestration.md](3.4-subagent-orchestration.md) | Subagent Orchestration | 17909 | `302d013b58` | 17 |
| 13 | [3.5-llm-adapters-and-streaming.md](3.5-llm-adapters-and-streaming.md) | LLM Adapters & Streaming | 14802 | `e06afc0b8c` | 13 |
| 14 | [4-execution-environment.md](4-execution-environment.md) | Execution Environment | 10217 | `2c28d6dfe6` | 7 |
| 15 | [4.1-filesystem-tools-and-observation.md](4.1-filesystem-tools-and-observation.md) | Filesystem Tools & Observation | 12664 | `497a546240` | 19 |
| 16 | [4.2-shell-subprocess-and-terminal.md](4.2-shell-subprocess-and-terminal.md) | Shell, Subprocess & Terminal | 11423 | `f7df8fa444` | 14 |
| 17 | [4.3-sandboxing-and-security.md](4.3-sandboxing-and-security.md) | Sandboxing & Security | 13413 | `7f0450a6ee` | 13 |
| 18 | [5-api-layer-and-host-client-bridge.md](5-api-layer-and-host-client-bridge.md) | API Layer & Host-Client Bridge | 10478 | `def07307fc` | 6 |
| 19 | [5.1-api-proxy-and-rpc-protocol.md](5.1-api-proxy-and-rpc-protocol.md) | API Proxy & RPC Protocol | 10598 | `ea52e73d79` | 12 |
| 20 | [5.2-typert-type-safe-rpc-generation.md](5.2-typert-type-safe-rpc-generation.md) | Typert: Type-Safe RPC Generation | 10605 | `835dcbac7f` | 12 |
| 21 | [5.3-client-runtime-and-session-management.md](5.3-client-runtime-and-session-management.md) | Client Runtime & Session Management | 13288 | `3a71560dcf` | 14 |
| 22 | [6-web-ui.md](6-web-ui.md) | Web UI | 10812 | `9147965a2b` | 11 |
| 23 | [6.1-conversation-ui-and-chat-view.md](6.1-conversation-ui-and-chat-view.md) | Conversation UI & Chat View | 20873 | `abddeea321` | 15 |
| 24 | [6.2-workspace-browser-and-sidebar.md](6.2-workspace-browser-and-sidebar.md) | Workspace Browser & Sidebar | 14914 | `b148bc8c29` | 14 |
| 25 | [6.3-ui-primitives-trajectory-and-tool-views.md](6.3-ui-primitives-trajectory-and-tool-views.md) | UI Primitives, Trajectory & Tool Views | 14397 | `f622d92bf5` | 12 |
| 26 | [6.4-settings-agent-presets-and-onboarding.md](6.4-settings-agent-presets-and-onboarding.md) | Settings, Agent Presets & Onboarding | 20899 | `3be3478c57` | 15 |
| 27 | [7-extensions-and-integrations.md](7-extensions-and-integrations.md) | Extensions & Integrations | 10849 | `625130fb29` | 11 |
| 28 | [7.1-acp-protocol-and-agent-communication.md](7.1-acp-protocol-and-agent-communication.md) | ACP Protocol & Agent Communication | 10937 | `83faef4dcd` | 16 |
| 29 | [7.2-mcp-client-hooks-and-skills.md](7.2-mcp-client-hooks-and-skills.md) | MCP Client, Hooks & Skills | 12786 | `11c5397a8c` | 10 |
| 30 | [7.3-goals-todos-workflows-and-web-tools.md](7.3-goals-todos-workflows-and-web-tools.md) | Goals, Todos, Workflows & Web Tools | 16540 | `7f7d335222` | 15 |
| 31 | [7.4-python-sdk-and-runtime-distribution.md](7.4-python-sdk-and-runtime-distribution.md) | Python SDK & Runtime Distribution | 14605 | `e3dab7a40f` | 11 |
| 32 | [8-testing-and-quality-infrastructure.md](8-testing-and-quality-infrastructure.md) | Testing & Quality Infrastructure | 10494 | `894b13a2a7` | 11 |
| 33 | [8.1-unit-and-integration-testing.md](8.1-unit-and-integration-testing.md) | Unit & Integration Testing | 13239 | `98c3e8cea0` | 12 |
| 34 | [8.2-browser-e2e-testing.md](8.2-browser-e2e-testing.md) | Browser E2E Testing | 14943 | `3619750a09` | 14 |
| 35 | [8.3-cicd-pipeline.md](8.3-cicd-pipeline.md) | CI/CD Pipeline | 14989 | `7a983f1929` | 18 |
| 36 | [9-documentation-and-internationalization.md](9-documentation-and-internationalization.md) | Documentation & Internationalization | 9043 | `d6a79ac128` | 6 |
| 37 | [9.1-bilingual-documentation-and-translation-pairing.md](9.1-bilingual-documentation-and-translation-pairing.md) | Bilingual Documentation & Translation Pairing | 10073 | `75ee62592b` | 15 |
| 38 | [9.2-type-equivalence-and-doc-verification-gates.md](9.2-type-equivalence-and-doc-verification-gates.md) | Type Equivalence & Doc Verification Gates | 10580 | `e285ef3691` | 14 |
| 39 | [10-glossary.md](10-glossary.md) | Glossary | 17602 | `8712d4adc9` | 24 |

## 章节树

```
1  Overview（总览）            6  Web UI（浏览器端）
   1.1 Getting Started           6.1 Conversation UI
   1.2 Monorepo Structure        6.2 Workspace Browser
2  Core Architecture            6.3 UI Primitives/Trajectory
   2.1 Cordis & Vendoring        6.4 Settings/Presets/Onboarding
   2.2 Plugin Composition     7  Extensions & Integrations
   2.3 Event Bus & Seams         7.1 ACP Protocol
3  Agent System                 7.2 MCP Client/Hooks/Skills
   3.1 Agent Loop                7.3 Goals/Todos/Workflows/Web
   3.2 Tool Registry             7.4 Python SDK
   3.3 Session Log            8  Testing & Quality
   3.4 Subagent                  8.1 Unit & Integration
   3.5 LLM Adapters              8.2 Browser E2E
4  Execution Environment        8.3 CI/CD Pipeline
   4.1 Filesystem Tools       9  Documentation & i18n
   4.2 Shell/Subprocess/Terminal 9.1 Bilingual Pairing
   4.3 Sandboxing & Security    9.2 Type Equivalence Gates
5  API Layer & Bridge         10 Glossary（术语表）
   5.1 API Proxy & RPC
   5.2 Typert RPC Gen
   5.3 Client Runtime
```
