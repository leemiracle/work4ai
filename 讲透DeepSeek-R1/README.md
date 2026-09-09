# 讲透 DeepSeek-R1

> 首次公开验证"无 SFT 冷启动、纯 RL + 可验证奖励"即可让基础模型自发涌现反思/验证/长链思考，追平 OpenAI-o1-1217，并蒸馏普惠到 1.5B-70B；正式刊登 Nature 645:633-638。commit `0cf7856`（2025-04-09）· 生成 2026-09-05

## 产物清单

| 产物 | 规模 / 说明 |
|---|---|
| DeepWiki | 13 页（deepwiki/） |
| 论文精读 | 1 篇：《DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning》（arXiv:2501.12948，Nature 645:633-638） |
| 知识图谱 | 4 节点 / 1 边 / 3 层 / 3 步导览（发布仓，源码薄，重点在论文） |

## 论文精读要点

- **R1-Zero**：不经任何人工标注推理轨迹，仅规则可验证奖励 + 大规模 RL，涌现 "aha moment"、自我验证与长链反思——开源推理模型的分水岭
- 算法 **GRPO**（砍掉 PPO 的 critic，用组内相对排名估 baseline），出自自家 DeepSeekMath（2402.03300）
- **R1 双管线**：R1-Zero 纯 RL 可读性差 → 冷启动 SFT → 推理 RL → 拒绝采样扩 SFT → 全场景 RL，最终追平 o1-1217
- **蒸馏**：用 R1 蒸馏 1.5B-70B（Qwen/Llama 底座），小模型能力大幅超过同尺寸 RL 训练
- 2025-01-22 春节前发布一天引爆全球；v2 为 Nature 修订版

## 知识图谱

路径：`~/ai/explore/deepseek-ai/DeepSeek-R1/.understand-anything/knowledge-graph.json`。发布仓（模型卡+蒸馏权重表），图谱小属正常，重点在论文。

## 姊妹篇

- GRPO 出处：[讲透DeepSeek-Math](../讲透DeepSeek-Math/README.md)；底座：[讲透DeepSeek-V3](../讲透DeepSeek-V3/README.md)
- 奖励进化续篇（verifier-as-reward）：[讲透DeepSeek-Math-V2](../讲透DeepSeek-Math-V2/README.md)
