# 讲透 DeepSeek-Prover-V1.5

> 7B 开源 Lean 4 定理证明模型：训练侧 SFT+RLPAF、推理侧 RMaxTS 树搜索双线改造，把 miniF2F-test 从 50.0% 推到 63.5%、ProofNet 推到 25.3% 双榜 SOTA（2024-08 时点）。commit `2c4ba91`（2024-08-16）· 生成 2026-09-05

## 产物清单

| 产物 | 规模 / 说明 |
|---|---|
| DeepWiki | 17 页（deepwiki/） |
| 论文精读 | 1 篇：《DeepSeek-Prover-V1.5: Harnessing Synthetic Data for Tool-Integrated Reasoning》（arXiv:2408.08152） |
| 知识图谱 | 54 节点 / 96 边 / 6 层 / 8 步导览（发布仓，源码薄，重点在论文） |

## 论文精读要点

- **truncate-and-resume**：whole-proof 生成出错即从第一个错误处截断续写，让"一次出整段证明"的模型也能看见中间 tactic state，单模型覆盖两种范式
- **RMaxTS**：推理时蒙特卡洛树搜索暴力探索（V1.5 的"推理时暴力"与 V2 的"训练时内化"形成演进对照）
- **RLPAF**（RL from Proof Assistant Feedback）：证明助手当免费验证器，算法复用 GRPO（组内 32 候选相对奖励）；团队即 DeepSeekMath 班底
- SFT 双增强：DeepSeek-Coder-V2 236B 注入 CoT 注释 + tactic state 注释（辅助任务预测证明状态），expert iteration 滚到 9.6M 序列
- 篇末展望节完整预告了 Prover-V2（2504.21801）——V2 要点的本地出处

## 知识图谱

路径：`~/ai/explore/deepseek-ai/DeepSeek-Prover-V1.5/.understand-anything/knowledge-graph.json`。发布仓（模型卡+数据生成脚本），图谱小属正常，重点在论文。

## 姊妹篇

- 后继：[讲透DeepSeek-Prover-V2](../讲透DeepSeek-Prover-V2/README.md)（其论文要点在本文展望节）
- GRPO 班底：[讲透DeepSeek-Math](../讲透DeepSeek-Math/README.md)；CoT 注释器：[讲透DeepSeek-Coder-V2](../讲透DeepSeek-Coder-V2/README.md)
