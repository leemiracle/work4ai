# 讲透 DeepSeek Harness（dsh）

> DeepSeek 开源 Agent Harness 全量知识库——DeepWiki 39 页全量 + 中文知识图谱（3368 节点/5160 边/12 层架构/16 步导览）+ 新人上手指南 + 14 篇重要文件精讲。
> 生成于 2026-09-04，仓库 commit `76fda729`（v0.1.2-rc.1，master）。

## 项目一句话

**DeepSeek Harness（`dsh`）** 是 DeepSeek 出品的开源 Agent Harness：TypeScript pnpm monorepo，**everything-is-a-plugin** 架构，底层基于 [Cordis](https://github.com/cordiverse/cordis)（[时空可组合编程范式](https://arxiv.org/abs/2608.25512)）。50+ packages（core/host/llm/mcp/sandbox/session/skill/subagent/todo/workflow/goal/plan/guard/...）+ apps（cli/web）+ Python SDK + native landlock 沙箱。developer preview 阶段。

## 产物清单

| 目录/文件 | 内容 | 规模 |
|---|---|---|
| [`deepwiki/`](./deepwiki/INDEX.md) | DeepWiki 全站抓取（39/39 页零遗漏）+ 3 个 related 仓概览（cordis/V3.2/MCP servers）+ 覆盖率检查 | 42 md |
| [`onboarding/ONBOARDING.md`](./onboarding/ONBOARDING.md) | 新人上手指南：12 层架构 mermaid + 核心模块巡礼 + 请求旅程数据流 + 三条学习路径 | 5088 字 8 节 |
| [`explain/`](./explain/README.md) | 重要文件精讲（六节结构：角色/结构/连接/数据流/设计决策/新人提示） | 14 篇 21405 字 |

## 知识图谱（understand 中文版）

图谱在仓库内（支持 fingerprints 增量更新）：
- **图谱**: `~/ai/explore/deepseek-ai/deepseek-harness/.understand-anything/knowledge-graph.json`（2.6MB）
- **规模**: 3368 节点（file 772 / function 1660 / class 253 / config 325 / document 357）· 5160 边（imports 830 / contains 1913 / calls 317 / documents 467 / configures 289...）· 12 架构层 · 16 步导览
- **覆盖**: T0 精选 232 批 / 493 批全量批（1410 文件深度分析；源码主线+文档+配置全取，测试/翻译/i18n/快照裁剪）
- **校验**: inline-validate 0 issues；imports 边与 importMap 1:1 对账；跨批边全部 grep 实证

## 12 层架构速览

CLI 应用入口(78) → Web 客户端(194) → 服务网关(83) → 内核与宿主(117) → 会话与上下文(210) → Agent 编排能力(168) → 模型接入(87) → 工具与交互(142) → 安全沙箱(81) → 运行支撑(64) → SDK 与工程化(97) → 文档与规范(134)

## 推荐阅读顺序

1. `onboarding/ONBOARDING.md` 第 1-3 节（是什么 + 上手 + 架构）
2. `explain/` 主干五篇：bin → core → agent-loop → llm-runtime → deepseek-adapter
3. `deepwiki/` 按需深读（1-overview 起步，2.x 插件体系，7.x 工具生态）
4. 专题线：沙箱安全（sandbox-local + landlock-main）/ Python 接入（python-client）/ 编排（goal + child-agent）

## 姊妹篇

[`讲透vLLM/`](../讲透vLLM/README.md) · [`讲透SGLang/`](../讲透SGLang/README.md) · [`讲透TIRx/`](../讲透TIRx/README.md)（同一流水线：pipeline-bin 脚本库 + understand 三代工艺）
