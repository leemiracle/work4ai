# 讲透 LPLB

> DeepSeek 基于线性规划的 MoE 专家并行动态负载均衡器：按负载统计重排专家（重排由 EPLB 完成），单 SM 内点法（IPM）在 GPU 上解最优 token 分配 · commit `0490f79`（2025-11-19）· 产物生成 2026-09-04/05

## 产物清单

| 产物 | 规模（截至 2026-09-05） |
|---|---|
| deepwiki/ | 34 页（抓取仍在进行，以目录为准） |
| onboarding/ | 1998 字（不计空格字符） |
| explain/ | 3 篇精讲 |
| 知识图谱 | 47 节点 / 79 边 / 7 层 / 12 步导览 |

- [deepwiki/](deepwiki/) DeepWiki 全站抓取（无 INDEX，按目录浏览）
- [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md) 新人上手指南
- [explain/](explain/) 3 篇文件级精讲：planner / plugin.cpp / minilp.cu（含 README 索引）

## 知识图谱

- 路径：仓内 `.understand-anything/knowledge-graph.json`（`~/ai/explore/deepseek-ai/LPLB`，44KB）
- 规模：47 节点 / 79 边 / 7 层 / 12 步导览
- fingerprints 基线已生成，支持增量更新

## 推荐阅读顺序

1. [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)——LP 建模到 GPU 求解的全链路
2. [explain/03-minilp-cu.md](explain/03-minilp-cu.md)——嵌入式 LP 求解器（cuSolverDx/cuBLASDx）精讲，再看 planner 与 plugin 接线
3. [deepwiki/](deepwiki/) 章节补全；注意项目自述"early research stage"

## 姊妹篇

- [讲透EPLB](../讲透EPLB/)——前代启发式路线，专家重排依赖它
- [讲透DeepEP](../讲透DeepEP/)——负载统计来源之一
- [讲透DeepSeek-Harness](../讲透DeepSeek-Harness/README.md)——本批 35 仓系列总索引
