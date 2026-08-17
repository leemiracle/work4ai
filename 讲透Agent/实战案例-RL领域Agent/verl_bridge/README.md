# verl_bridge —— rl_agent ↔ verl / verl_tool 三层集成

> **日期**：2026-08-17 · **本机**：无 GPU（torch 2.10 CPU）——Layer 1 本地实测 ✅，Layer 3 配方待 GPU 机
> **一句话关系**：rl_agent 给 verl 贡献**任务环境**（4 工具 + kb + RLVR 判分器），不是 brain——verl 训练时 policy=LLM（动权重）。这补上 [手册 11 章方案对决](../../../工程化手册库/prompt工程手册/11-自动化优化闭环-六步流水线.md)的缺口：Ctx-APO 是 A 形态（黑盒、不动权重），verl-GRPO 是 B 深水区（动权重）——**同一任务环境，两种进化引擎**。

---

## 三层架构

| 层 | 内容 | 状态 |
|---|---|---|
| **L1 环境接入**（本地可跑） | [`rl_agent_tool.py`](./rl_agent_tool.py)：4 动作 tag 协议（`<search>/<run_experiment>/<recall>/<answer>`）+ env_cache 轨迹状态 + `compute_score` RLVR 外部判分 | ✅ 14 项协议测试全过（[`test_rl_agent_tool.py`](./test_rl_agent_tool.py)） |
| **L2 读码对照**（学习层） | exp_grpo（21 行 toy）vs verl `compute_grpo_outcome_advantage` 逐项对照（下表） | ✅ 本 README |
| **L3 GPU 配方**（写好待跑） | [`train_grpo_gpu.sh`](./train_grpo_gpu.sh)（Qwen2.5-1.5B + GRPO + rl_agent env，骨架逐行对照 verl-tool 官方 mathcoder 配方）+ [`make_dataset.py`](./make_dataset.py)（24 题四态 parquet）+ [`install_tool.sh`](./install_tool.sh)（symlink 安装） | ⚠️ 本机无卡未实跑，参数按官方配方校准 |

## L1 快速验收（零 GPU 零 ray）

```bash
bash verl_bridge/install_tool.sh            # symlink 进 verl_tool + 注册验证
python3 verl_bridge/test_rl_agent_tool.py   # 14 项协议测试（轨迹/熔断/判分/边界）
```

## L2 对照表：exp_grpo vs verl GRPO（读码笔记）

verl 侧：`~/ai/verl/verl/trainer/ppo/core_algos.py:268` `compute_grpo_outcome_advantage`

| 维度 | rl_agent `exp_grpo`（toy，21 行） | verl（工业，~10⁴ 行体系） | 教学注 |
|---|---|---|---|
| 组均值 baseline | $(r-\bar r_{group})$ ✅ | 同（index 分组 scatter-mean） | 组相对思想同源 |
| std 归一 | **不除 std**（Dr.GRPO 风格，诚实标注） | `norm_adv_by_std_in_grpo` 开关：True=原版 GRPO / False=**Dr.GRPO**（arXiv:2503.20783） | toy 恰好走了 Dr.GRPO 路线——verl 里它是一行开关 |
| clip | 乘法 clip∈[0.8,1.25]（PPO 近似） | 完整 PPO ratio clip（policy 概率比） | toy 简化处，已在代码诚实标注 |
| importance sampling | 无（on-policy 单步） | 有（rollout-policy 版本差补偿，mini-batch 多 epoch） | 这就是 trainer 的存在理由 |
| advantage 粒度 | 轨迹级 | token 级（response_mask 广播） | LLM 的"动作"=token |
| rollout 引擎 | 概率表采样 | vLLM（gpu_memory_utilization/offload 一堆工程旋钮） | 训练:推理=1:1 的工程现实 |

**读码收获**：toy 的每一处"诚实简化"在 verl 里都有对应完整实现——简化标注 = 读工业码的地图。

## L3 跑法（GPU 机）

```bash
pip install -e ~/ai/verl-tool -e ~/ai/verl   # 需 vllm/ray/torch-cuda
bash verl_bridge/install_tool.sh
python3 verl_bridge/make_dataset.py        # 24 题 parquet（四态分布见输出）
bash verl_bridge/train_grpo_gpu.sh         # 4×A100 起；reward 挂点见脚本尾注
```

预期训练动力学（可证伪预测）：experiment 态题目 GRPO 组内对比会奖励"先 `<run_experiment>` 再 `<answer>`"的轨迹（反短路判分），概念题奖励"检索→简洁作答"——**LLM 学会 rl_agent 的 RLVR 规则，正如 RLBrain 学会 Q 表**。

## 诚实边界

1. L3 未实跑：参数按 mathcoder 官方配方校准，但 reward manager 挂点（脚本尾注）需按 verl_tool 当前版 main_ppo.py 微调
2. `compute_score` 是关键词 EM（toy 判分）——生产换 LLM judge 须先建裁判黄金集（手册 08 流程；GLM-APO 判分器 409 笔误教训）
3. gold_keywords 24 题为人工标注最小集——扩到 100+ 题再训练才有统计意义（手册 08 黄金集大小表：中等抽取 100-300）
