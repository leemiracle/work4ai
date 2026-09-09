# 讲透 EPLB

> DeepSeek 专家并行负载均衡器（Expert Parallelism Load Balancer）：冗余专家策略 + 启发式打包，为 MoE 模型均衡各 GPU 负载 · commit `d52c72d`（2025-03-24）· 产物生成 2026-09-04/05

## 产物清单

| 产物 | 规模（截至 2026-09-05） |
|---|---|
| deepwiki/ | 10 页 |
| onboarding/ | 1799 字（不计空格字符） |
| 知识图谱 | 8 节点 / 12 边 / 4 层 / 8 步导览 |

- [deepwiki/](deepwiki/) DeepWiki 全站抓取（无 INDEX，按目录浏览）
- [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md) 新人上手指南

## 知识图谱

- 路径：仓内 `.understand-anything/knowledge-graph.json`（`~/ai/explore/deepseek-ai/EPLB`，12KB）
- 规模：8 节点 / 12 边 / 4 层 / 8 步导览（库极小，图谱轻量）
- fingerprints 基线已生成，支持增量更新

## 推荐阅读顺序

1. [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)——冗余专家与均衡打包算法全景（库小，此篇为主）
2. [deepwiki/](deepwiki/) 2.x 章节读负载均衡策略 / 专家复制算法 / 均衡打包算法三连

## 姊妹篇

- [讲透LPLB](../讲透LPLB/)——新一代 LP 求解路线（专家重排即由 EPLB 承担）
- [讲透DeepEP](../讲透DeepEP/)——专家并行通信底座
- [讲透DeepSeek-Harness](../讲透DeepSeek-Harness/README.md)——本批 35 仓系列总索引
