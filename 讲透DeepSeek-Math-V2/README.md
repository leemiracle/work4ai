# 讲透 DeepSeek-Math-V2

> 数学 RL 的奖励升级实验：把"最终答案对不对"换成"verifier 给证明打的分数"，训出首个开源自然语言定理证明模型族，IMO 2025 金牌线 83.3%、Putnam 2024 拿 118/120（人类最高 90）。commit `665c840`（2025-12-01）· 生成 2026-09-05

## 产物清单

| 产物 | 规模 / 说明 |
|---|---|
| DeepWiki | 29 页（deepwiki/） |
| 论文精读 | 1 篇：《DeepSeekMath-V2: Towards Self-Verifiable Mathematical Reasoning》（arXiv:2511.22570，ID 经 websearch 核实） |
| 知识图谱 | 26 节点 / 28 边 / 4 层 / 8 步导览（发布仓，源码薄，重点在论文） |

## 论文精读要点

- **verifier-as-reward**：证明器（verifier）给候选证明打分当 reward，生成器显式知道自己的奖励函数、通过自我审查（deliberate reasoning）最大化它；64+64 候选池 × 16 轮验证引导搜索
- ⚠️ **勘误（预期偏差）**：预期"RL+工具集成"——实际是"迭代扩展 RL + 自验证"，**全程无工具集成**（无代码执行器/符号工具/搜索引擎）
- **meta-verification 全自动标注**：n 份验证分析 + m 份投票复核，最后两轮迭代完全替代人工标注，与专家判断对齐良好
- 基座 DeepSeek-V3.2-Exp-Base；一作 Zhihong Shao 即 GRPO 提出者（DeepSeekMath 一作），本文是对"答案可验证性"约束的正面回应
- 战绩：IMO 2025 金牌线 83.3%、CMO 2024 金牌线 73.8%、Putnam 2024 118/120

## 知识图谱

路径：`~/ai/explore/deepseek-ai/DeepSeek-Math-V2/.understand-anything/knowledge-graph.json`。发布仓（inference + 评测模板），图谱小属正常，重点在论文。

## 姊妹篇

- GRPO 出处：[讲透DeepSeek-Math](../讲透DeepSeek-Math/README.md)；基座：[讲透DeepSeek-V3.2-Exp](../讲透DeepSeek-V3.2-Exp/README.md)
- 形式证明对照线：[讲透DeepSeek-Prover-V2](../讲透DeepSeek-Prover-V2/README.md)、[讲透DeepSeek-Prover-V1.5](../讲透DeepSeek-Prover-V1.5/README.md)
