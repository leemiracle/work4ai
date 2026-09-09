# 讲透 DeepGEMM

> DeepSeek LLM 核心算子 CUDA 内核库：FP8/FP4/BF16 GEMM、融合 MoE（Mega MoE 通信重叠）、MQA indexer 打分等，JIT 运行时编译 · commit `559d79f`（2026-07-15）· 产物生成 2026-09-04/05

## 产物清单

| 产物 | 规模（截至 2026-09-05） |
|---|---|
| deepwiki/ | 32 页 |
| onboarding/ | 4157 字（不计空格字符） |
| explain/ | 4 篇精讲 |
| 知识图谱 | 571 节点 / 1117 边 / 10 层 / 12 步导览 |

- [deepwiki/](deepwiki/) DeepWiki 全站抓取（无 INDEX，按目录浏览）
- [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md) 新人上手指南
- [explain/](explain/) 4 篇文件级精讲：apis-gemm.hpp / jit-compiler.hpp / heuristics-sm90.hpp / sm90_fp8_gemm_1d2d.cuh（含 README 索引）

## 知识图谱

- 路径：仓内 `.understand-anything/knowledge-graph.json`（`~/ai/explore/deepseek-ai/DeepGEMM`，452KB）
- 规模：571 节点 / 1117 边 / 10 层 / 12 步导览
- fingerprints 基线已生成，支持增量更新

## 推荐阅读顺序

1. [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)——JIT 编译体系与内核族全景
2. [explain/02-csrc-jit-compiler.hpp.md](explain/02-csrc-jit-compiler.hpp.md)——先懂 JIT 再读内核：SM90 heuristics → FP8 1D2D GEMM 实现
3. [deepwiki/](deepwiki/) 2.x GEMM/Attention 章节补全
4. 知识图谱 12 步导览收尾

## 姊妹篇

- [讲透FlashMLA](../讲透FlashMLA/)——注意力侧姊妹内核库
- [讲透TileKernels](../讲透TileKernels/)——TileLang 路线的内核库对照
- [讲透DeepEP](../讲透DeepEP/)——Mega MoE 融合的通信对端
- [讲透DeepSeek-Harness](../讲透DeepSeek-Harness/README.md)——本批 35 仓系列总索引
