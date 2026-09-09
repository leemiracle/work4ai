# 讲透 Engram

> PKU×DeepSeek 架构论文（ACL 2026）：把经典 N-gram 嵌入现代化成 O(1) 查表的条件记忆模块，与 MoE 同参数同 FLOPs 对比发现 U 形稀疏分配律，Engram-27B 全面胜过 MoE-27B——与 V3.2 的 DSA 同属"下一代稀疏建模原语"谱系。commit `fb7f84a`（2026-01-14）· 生成 2026-09-05

## 产物清单

| 产物 | 规模 / 说明 |
|---|---|
| DeepWiki | 32 页（deepwiki/） |
| 论文精读 | 1 篇：《Conditional Memory via Scalable Lookup: A New Axis of Sparsity for Large Language Models》（arXiv:2601.07372，ACL 2026 long.226） |
| 知识图谱 | 14 节点 / 21 边 / 3 层 / 8 步导览（论文发布仓，源码薄，重点在论文） |

## 论文精读要点

- ⚠️ **定位勘误（钉版）**：Engram **不是 agent 记忆项目、与 Mem0 零关联**——是模型架构研究：给 Transformer 加可训练"N-gram 查表记忆模块"，memory 指参数化静态记忆（embedding 表）而非对话记忆
- **机制**：语言中命名实体/固定搭配局部、静态、高度刻板，不必用深层注意力"算"——直接查表取静态嵌入、上下文门控融合进隐状态
- **Sparsity Allocation**：形式化"稀疏预算在 MoE（条件计算）与 Engram（条件记忆）间怎么分"，实验发现 U 形分配律，最优 ρ≈75-80% 给查表
- Engram-27B 等参数等 FLOPs 全面胜 MoE-27B；MQ-NIAH 84.2→97.0
- 版本注记：ACL camera-ready 曾用名 **DSE**（Deep Sparse Embedding），arXiv v2 统一为 Engram；社区解读为"V4 架构预告"（梁文锋署名）

## 知识图谱

路径：`~/ai/explore/deepseek-ai/Engram/.understand-anything/knowledge-graph.json`。论文发布仓，图谱小属正常，重点在论文（本模型仓 PDF 可直读）。

## 姊妹篇

- 稀疏谱系同门：[讲透DeepSeek-V3.2-Exp](../讲透DeepSeek-V3.2-Exp/README.md)（DSA 砍注意力计算，Engram 补知识查表）
- 架构主线：[讲透DeepSeek-V3](../讲透DeepSeek-V3/README.md)、[讲透DeepSeek-MoE](../讲透DeepSeek-MoE/README.md)
