# 讲透 DualPipe

> DeepSeek-V3 技术报告提出的双向流水线并行算法：前向-反向计算与通信完全重叠，显著削减流水线气泡 · commit `030ce43`（2026-01-14）· 产物生成 2026-09-04/05

## 产物清单

| 产物 | 规模（截至 2026-09-05） |
|---|---|
| deepwiki/ | 16 页 |
| onboarding/ | 1977 字（不计空格字符） |
| explain/ | 2 篇精讲 |
| 知识图谱 | 40 节点 / 92 边 / 6 层 / 9 步导览 |

- [deepwiki/](deepwiki/) DeepWiki 全站抓取（无 INDEX，按目录浏览）
- [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md) 新人上手指南（微型库，一篇即可通读）
- [explain/](explain/) 2 篇文件级精讲：dualpipe.py 主算法 / utils.py 工具（含 README 索引）

## 知识图谱

- 路径：仓内 `.understand-anything/knowledge-graph.json`（`~/ai/explore/deepseek-ai/DualPipe`，40KB）
- 规模：40 节点 / 92 边 / 6 层 / 9 步导览（库极小，图谱轻量）
- fingerprints 基线已生成，支持增量更新

## 推荐阅读顺序

1. [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)——算法动机与调度图景
2. [explain/01-dualpipe.md](explain/01-dualpipe.md)——核心实现逐行精讲
3. [deepwiki/](deepwiki/) 2.x 实现与用例章节；背景配合 DeepSeek-V3 技术报告（arXiv:2412.19437）

## 姊妹篇

- [讲透DeepSeek-V3](../讲透DeepSeek-V3/)——算法出处技术报告精读
- [讲透DeepEP](../讲透DeepEP/)——同为 V3 并行策略基础设施
- [讲透DeepSeek-Harness](../讲透DeepSeek-Harness/README.md)——本批 35 仓系列总索引
