# 讲透 smallpond

> DeepSeek 基于 3FS + DuckDB 的轻量级数据处理框架：Python API 声明式定义计算图，面向 AI 训推数据管道 · commit `52ecc5e`（2025-03-05）· 产物生成 2026-09-04/05

## 产物清单

| 产物 | 规模（截至 2026-09-05） |
|---|---|
| deepwiki/ | 29 页（抓取仍在进行，以目录为准） |
| onboarding/ | 4673 字（不计空格字符） |
| explain/ | 4 篇精讲 |
| 知识图谱 | 356 节点 / 898 边 / 9 层 / 12 步导览 |

- [deepwiki/](deepwiki/) DeepWiki 全站抓取（无 INDEX，按目录浏览）
- [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md) 新人上手指南
- [explain/](explain/) 4 篇文件级精讲：execution/task.py 执行器 / logical/node.py 逻辑计划 / io/arrow.py Arrow 读写 / dataframe.py 数据框门面（含 README 索引）

## 知识图谱

- 路径：仓内 `.understand-anything/knowledge-graph.json`（`~/ai/explore/deepseek-ai/smallpond`，284KB）
- 规模：356 节点 / 898 边 / 9 层 / 12 步导览
- fingerprints 基线已生成，支持增量更新

## 推荐阅读顺序

1. [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)——DataFrame→逻辑计划→物理执行的分层全景
2. [explain/04-dataframe.md](explain/04-dataframe.md)→[01](explain/01-execution-task.md)——从用户门面下钻到执行引擎
3. [deepwiki/](deepwiki/) 章节补全；配合 [讲透3FS](../讲透3FS/) 理解底层存储

## 姊妹篇

- [讲透3FS](../讲透3FS/)——smallpond 的存储底座
- [讲透DeepSeek-Harness](../讲透DeepSeek-Harness/README.md)——本批 35 仓系列总索引
