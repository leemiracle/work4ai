# 讲透 CopilotKit

> CopilotKit/CopilotKit · 38k star（A 层第 2 位）· 开源 AI copilot 应用框架：React 前端组件 + Agent runtime（AG-UI 协议）+ Python SDK + agent skills，pnpm monorepo 20 包
> 本地仓 /usr-data/data2/repos/ai-trending/CopilotKit @a0840c0（2026-06-09）· 流水线 understand-anything 全链

## 全链状态

| 步骤 | 状态 | 产物 |
|---|---|---|
| deepwiki | ✅ 52 页 100%（832K 字符，2026-10-30 MCP 通道） | `deepwiki/` |
| understand 图谱 | ✅ **1892 节点 / 4250 边 / 16 层 / 16 步 tour**，validator 0 issues 0 warnings，fingerprints 842 文件@a0840c0a | 仓内 `.understand-anything/knowledge-graph.json` |
| onboarding | ✅ 7480 字符 8 节 25 锚（主会话抽验 3/3 命中） | `onboarding/ONBOARDING.md` |
| explain 12 篇 | ✅ 组A 核心链路 6（52061 字符/276 锚）+ 组B 外围 6（52356 字符/305 锚），合计 104417 字符/581 锚，主会话抽验 16/16 命中（1 条 OOB 经消歧改判=验证器 glob 选错同名文件） | `explain/` |

## 裁剪口径（图谱范围声明）

聚焦核心 16 包 842 文件；**裁剪**（DeepWiki 文档层恰好互补覆盖）：
- `examples/`（3924）`showcase/`（10195）`docs/`（1112）`community/` `assets/` `.github/` `codemods/` `scripts/qa/`（65）
- **框架移植层 4 包**：`packages/vue`（215）`angular`（83）`react-native`（59）`react-textarea`（70）——与 react-core 高度冗余的适配 API 面（OpenHands 轮 enterprise/frontend 先例），可作后续 fingerprint 增量补录
- 测试资产（`__tests__/` `*.test.*` `*.stories.*` 等 453 文件）+ `CHANGELOG.md`（react-ui 18130 行自动流水）
- `.env*`（实测仅 .example 模板）+ 11 个嵌套 `.understand-anything` untracked 空脚手架

## 批阶段执行账（2026-11-01 16:14-19:5x）

63 批 4 并发，含一次 1308 五小时团灭（17:38 四批同杀→19:02 watchdog 恢复→SendMessage 四批复活**零损失**）。批产物 1978n/4425e → merge 1891n/4233e → 悬空边 12 条全处置（10 条 file:→config: 前缀错位回补 + randomId 函数节点补建 + 2 calls）→ **1892n/4250e**；87 重复节点 ID 去重（多批镜像文档归一）。file 级 842/842 与扫描集精确一致。

### scanner 盲区总账（TS 漏报为主/Python 多报，双向对账）
- barrel index.ts 全空/空报 25+ 处（shared 主 barrel 13 目标只报 1 最重）
- `@copilotkit/*` workspace 内部包误当外部过滤（累计 100+ 边手扫补齐；入口后缀因包而异：react-core/react-ui=.tsx，shared/runtime/sdk-js=.ts）
- CSS `@import` 全漏（15 条）；`export {} from` 再导出漏；tree-sitter 盲区七类（React 箭头组件/forwardRef·memo/enum/type-alias/abstract class/async generator/对象字面量方法）
- Python 假边 7 条剔除（stdlib 误解析/自环/docstring 示例）

## 勘误精选（源码级实证，完整版见 ONBOARDING 第 7 节）

1. **generateCopilotResponse=agents 重构中间态**：`copilot.resolver.ts:255` runtimeResponse 声明未赋值即解构，直接调用必抛
2. **use-copilot-chat_internal 返回对象缺 `visibleMessages`+`mcpServers` 未实现**——上游 useCopilotChat 解构得 undefined（文档与实现不符）
3. `lib/index.ts` LangGraphAgent/HttpAgent = deprecated 哨兵（构造即 throw），真身在 `agent-integrations/langgraph/`
4. **sdk-python README Quick Start 是幻觉 API**（`from copilotkit import Copilot` 不存在）；`langgraph.json` autotale_ai 死引用
5. **eval.yaml 与 SKILL.md v1.1.2 自相矛盾**：grader 检查旧包名 `@copilotkit/react|core|agent`——按新指南施工判 0 分
6. **publicApiKey 才是源码主字段**（`CopilotKitProvider.tsx:102-106` JSDoc 自述 alias + `:380` `publicApiKey ?? publicLicenseKey`）——react-core/SKILL.md L91 声明反转（三证）
7. **skills 文档目录快照三层漂移**（2026-03-28 生成）：`packages/v1|v2/*` 已扁平化；sources.md 43 条旧引用按机械迁移规则重定向 38 条
8. `@copilotkit/agent` 假包名（全仓 20 个 package.json 零定义）；`@copilotkit/runtime/express` 子路径不存在（仅 `./v2/express`）
9. TelemetryClient 硬编码 Segment writeKey + claim-only 不验 Ed25519 + 采样双汇流（identified 100%/匿名 5%）
10. v2 CopilotChatInput **Enter 键慢网络丢键击**已知 bug（e2e 全改 copilot-send-button 规避）
11. `typedoc.base.json` 全仓 7 处断链（git 历史从未跟踪）+ entryPoints 只覆盖主入口系统性缺口
12. A2UIViewer.tsx 不可编译 v0.8 遗留（import 不存在的 registry 目录）；`@a2ui/lit/0.8` 幽灵依赖；utils.ts 6 行纯 import 死文件
13. 根 `skills/` 双层结构：8 独立 lifecycle skill + 3 组 `packages/*/skills` 镜像（`sync-plugin-skills.ts` 生成，diff SAME）
14. AGENTS.md 过时（v1/v2 分层说法错误，CLAUDE.md 正确）；lefthook pre-commit 实 6 命令文档列 4
15. AG-UI 协议：SSE 默认 + protobuf 可选（4 字节大端前缀）+ Deprecated Events（Remove in 1.0.0）节

## 相关文档

- `deepwiki/` — 52 页官方 wiki 全量（含被裁剪的 vue/angular 移植层文档，与图谱互补）
- 仓库台账：`/usr-data/data2/repos/agent-repos/deepwiki-batch/understand-wave2.md`（2026-11-01 各 checkpoint）
