# 讲透 TileKernels

> DeepSeek 基于 TileLang DSL 的 LLM GPU 内核库：MoE 门控/topk-sum 等算子逼近硬件算力与带宽极限，部分已用于内部训练推理 · commit `36d9e45`（2026-04-23）· 产物生成 2026-09-04/05

## 产物清单

| 产物 | 规模（截至 2026-09-05） |
|---|---|
| deepwiki/ | 25 页（抓取仍在进行，以目录为准） |
| onboarding/ | 2498 字（不计空格字符） |
| explain/ | 4 篇精讲 |
| 知识图谱 | 503 节点 / 1151 边 / 10 层 / 12 步导览 |

- [deepwiki/](deepwiki/) DeepWiki 全站抓取（无 INDEX，按目录浏览）
- [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md) 新人上手指南
- [explain/](explain/) 4 篇文件级精讲：moe-top2_sum_gate_kernel / config.py SM 配置中心 / pytest_benchmark_plugin 基准回归 / engram_gate_kernel 记忆门控内核（含 README 索引）

## 知识图谱

- 路径：仓内 `.understand-anything/knowledge-graph.json`（`~/ai/explore/deepseek-ai/TileKernels`，424KB）
- 规模：503 节点 / 1151 边 / 10 层 / 12 步导览
- fingerprints 基线已生成，支持增量更新

## 推荐阅读顺序

1. [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)——TileLang 内核族与基准体系全景
2. [explain/02-config.py-SM配置中心.md](explain/02-config.py-SM配置中心.md)——先懂 SM 配置调度，再读 [explain/01-moe-top2_sum_gate_kernel.md](explain/01-moe-top2_sum_gate_kernel.md) 核心内核
3. [deepwiki/](deepwiki/) 各算子章节补全
4. 知识图谱 12 步导览收尾

## 姊妹篇

- [讲透DeepGEMM](../讲透DeepGEMM/)——CUDA/CUTLASS 路线内核对照
- [讲透FlashMLA](../讲透FlashMLA/)——注意力内核姊妹库
- [讲透DeepSeek-Harness](../讲透DeepSeek-Harness/README.md)——本批 35 仓系列总索引
