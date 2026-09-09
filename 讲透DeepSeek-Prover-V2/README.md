# 讲透 DeepSeek-Prover-V2

> 子目标分解 RL 的 671B MoE Lean 证明模型：用 DeepSeek-V3 把难题分解成 `have ... sorry` 证明草图、7B 模型递归求解再冷启动 RL，miniF2F-test 88.9%（pass@8192）——V1.5 两个坑（MCTS 昂贵/模型太小）的官方填法。commit `e598a57`（2025-07-18）· 生成 2026-09-05

## 产物清单

| 产物 | 规模 / 说明 |
|---|---|
| DeepWiki | 9 页（deepwiki/） |
| 论文精读 | 无本地篇：V2 要点从 [讲透DeepSeek-Prover-V1.5/paper/](../讲透DeepSeek-Prover-V1.5/paper/PAPER-DEEPREAD.md) **展望节**提取，论文《Advancing Formal Mathematical Reasoning via RL for Subgoal Decomposition》（arXiv:2504.21801，已核实） |
| 知识图谱 | 4 节点 / 0 边 / 3 层 / 5 步导览（发布仓，源码薄，重点在论文） |

## 论文精读要点（摘自 V1.5 篇展望节）

- **子目标分解取代 MCTS**：V3 分解难题 → `have ... sorry` 链 → 7B 小模型递归求解各子目标 → 逐步形式证明与 V3 的 CoT 配对成**冷启动推理数据** → 上 RL（binary reward）
- 模型从 7B dense 换成 DeepSeek-V3 底座的 **671B MoE**
- 战果：miniF2F-test **88.9%**（pass@8192；pass@32 即 82.4%）、ProofNet-test 37.1%（pass@1024）、ProverBench 325 题中 15 道 AIME 24-25 解出 6 道（V3 多数投票 8 道——形式与非形式推理差距大幅收窄）
- PutnamBench 49/658（论文 v2 修订为 47）
- 演进哲学：V1.5 是"推理时暴力探索"，V2 是"训练时把分解能力内化"，与 AlphaProof 思路殊途同归

## 知识图谱

路径：`~/ai/explore/deepseek-ai/DeepSeek-Prover-V2/.understand-anything/knowledge-graph.json`。纯发布仓（模型卡+脚本），图谱极小属正常，重点在论文。

## 姊妹篇

- 前作与要点出处：[讲透DeepSeek-Prover-V1.5](../讲透DeepSeek-Prover-V1.5/README.md)；底座：[讲透DeepSeek-V3](../讲透DeepSeek-V3/README.md)
- 自然语言证明对照线：[讲透DeepSeek-Math-V2](../讲透DeepSeek-Math-V2/README.md)
