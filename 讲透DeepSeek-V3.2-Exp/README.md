# 讲透 DeepSeek-V3.2-Exp

> 通往下一代架构的中间实验步：在 V3.1-Terminus（671B MoE）上继续训练引入首个可训练细粒度稀疏注意力 **DSA**——lightning indexer 为每个 query 挑 top-2048 token，复杂度 O(L²)→O(Lk) 而性能与稠密版打平。commit `87e509a`（2025-11-18）· 生成 2026-09-05

## 产物清单

| 产物 | 规模 / 说明 |
|---|---|
| DeepWiki | 18 页（deepwiki/） |
| 论文精读 | 1 篇：《DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models》（arXiv:2512.02556；论文明言 V3.2 与 V3.2-Exp 架构相同） |
| 知识图谱 | 43 节点 / 82 边 / 4 层 / 8 步导览（发布仓，源码薄，重点在论文） |

## 论文精读要点

- **DSA（DeepSeek Sparse Attention）**：小型 lightning indexer 选 top-2048 token 做注意力；本地 inference/model.py::Indexer 含 non-interleaved RoPE 勘误注释——核心注意力从 O(L²) 降 O(Lk)，benchmark 与稠密打平
- ⚠️ **ID 核实**：README 无 arXiv 链接，V3.2 技术报告经检索核实 = **2512.02556**，论文明言 *"DeepSeek-V3.2 uses exactly the same architecture as DeepSeek-V3.2-Exp"*——解读本仓以该论文为主体+发布说明补充
- 完整版 V3.2 叠加规模化 RL 与大规模 agent 任务合成，对标 GPT-5；agent 侧 Tool-Decathlon 35.2 vs GPT-5 的 29.0
- 高算力变体 **Speciale**：IMO 2025 与 IOI 2025 双金牌（开源首次）、AIME 96.0；靠"想更长"换分（45k tokens/题）
- 128K 上下文（承自 V3.1-Terminus 扩展）；对 Kimi-K2-Thinking 多数领先、逊于 Gemini-3.0-Pro 但成本显著更低

## 知识图谱

路径：`~/ai/explore/deepseek-ai/DeepSeek-V3.2-Exp/.understand-anything/knowledge-graph.json`。发布仓（推理脚本+Indexer 实现），图谱小属正常，重点在论文。

## 姊妹篇

- 架构前作：[讲透DeepSeek-V3](../讲透DeepSeek-V3/README.md)
- 稀疏谱系：[讲透Engram](../讲透Engram/README.md)（一个砍注意力计算，一个补知识查表）
- 基座下游：[讲透DeepSeek-Math-V2](../讲透DeepSeek-Math-V2/README.md)（V3.2-Exp-Base 底座）
