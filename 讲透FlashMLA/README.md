# 讲透 FlashMLA

> DeepSeek Multi-head Latent Attention 优化内核库：驱动 DeepSeek-V3 / V3.2-Exp 的 MLA 与 DSA（稀疏注意力）解码 · commit `15f13e5`（2026-07-28）· 产物生成 2026-09-04/05

## 产物清单

| 产物 | 规模（截至 2026-09-05） |
|---|---|
| deepwiki/ | 28 页（抓取仍在进行，以目录为准） |
| onboarding/ | 4492 字（不计空格字符） |
| explain/ | 4 篇精讲 |
| 知识图谱 | 273 节点 / 442 边 / 9 层 / 11 步导览 |

- [deepwiki/](deepwiki/) DeepWiki 全站抓取（无 INDEX，按目录浏览）
- [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md) 新人上手指南
- [explain/](explain/) 4 篇文件级精讲：Python 门面层 / sparse_decode.h 分派中枢 / get_decoding_sched_meta.cu 瓦片调度器 / combine.cu splitKV 归并（含 README 索引）

## 知识图谱

- 路径：仓内 `.understand-anything/knowledge-graph.json`（`~/ai/explore/deepseek-ai/FlashMLA`，196KB）
- 规模：273 节点 / 442 边 / 9 层 / 11 步导览
- fingerprints 基线已生成，支持增量更新

## 推荐阅读顺序

1. [onboarding/ONBOARDING.md](onboarding/ONBOARDING.md)——MLA/DSA 内核族与调用链全景
2. [explain/01-flash_mla_interface-Python门面层.md](explain/01-flash_mla_interface-Python门面层.md)→[04](explain/04-combine.cu-splitKV归并.md)——Python 门面 → C++ 分派 → 瓦片调度 → 归并，四层下钻
3. [deepwiki/](deepwiki/) 稀疏/稠密内核章节补全；DSA 背景可配合姊妹篇 V3.2-Exp 精读

## 姊妹篇

- [讲透DeepGEMM](../讲透DeepGEMM/)——GEMM 侧姊妹内核库
- [讲透DeepSeek-V3.2-Exp](../讲透DeepSeek-V3.2-Exp/)——DSA（DeepSeek Sparse Attention）论文出处
- [讲透TileKernels](../讲透TileKernels/)——TileLang 内核对照
- [讲透DeepSeek-Harness](../讲透DeepSeek-Harness/README.md)——本批 35 仓系列总索引
