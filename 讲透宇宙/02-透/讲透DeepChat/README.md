# 讲透 DeepChat

[ThinkInAIXYZ/DeepChat](https://github.com/thinkinaixyz/deepchat)——跨平台 AI 聊天客户端（Electron + Vue3 + Pinia），多 provider 接入、MCP、知识库 RAG、多窗口。本地仓 `/usr-data/data1/browser/deepchat`（v1.1.3-beta.6，dev 分支）。

## 产物

| 目录 | 内容 |
|---|---|
| [deepwiki/](deepwiki/INDEX.md) | DeepWiki 全量 56 页中文索引 + 英文原文（2026-10-08 抓取，覆盖率 100%） |
| [onboarding/](onboarding/ONBOARDING.md) | ONBOARDING.md（6000 字 8 节，基于图谱+tour 16 步，2026-10-09） |
| [explain/](explain) | 12 篇重要文件/子系统精讲（六节结构，行号实证，多含 DeepWiki 勘误） |

## 知识图谱（understand-anything）

- 位置：仓内 `.understand-anything/knowledge-graph.json`（7093 节点 / 16655 边 / 15 层 / 16 步导览，校验 0 issues）
- 基线：fingerprints.json 2570 文件（commit c3cf25c5f），支持增量更新
- 中间产物：intermediate/（layers.json / tour.json / final-graph.json / scan-result.json）

## 快速入口（按问题找页）

- **整体架构**：1.2 应用架构总览 → 2 核心架构（Presenter 模式是主↔渲染进程的唯一通道）
- **加一个 LLM 厂商**：5.1 Provider 基类 → 5.2 各实现 → 5.4 消息格式转换
- **MCP 工具链**：4.1 架构 → 4.4 工具执行与权限 → 4.6 内置服务
- **知识库/RAG**：8 章（DuckDB 向量库 + 任务队列 + 相似度检索）
- **文件/图片输入**：7 章文件适配器 → 7.3 @mention 注入
- **消息流渲染**：6.2 生成流 → 6.3 变体分叉 → 9.6 Artifact 渲染

## 后续可接（已完成）

- ~~understand 中文知识图谱（13 仓流水线标准第二步）~~ ✅ 2026-10-09
- ~~onboarding + explain 系列（第三步）~~ ✅ 2026-10-09
- DeepWiki 恢复可达后增量补最新版快照（当前为 2026-04 世代）
