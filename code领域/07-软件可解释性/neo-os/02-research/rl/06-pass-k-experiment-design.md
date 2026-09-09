# 系统域 pass@k 实验 · 设计文档（可移植）

> **目标**：在系统域（Lean4 规则蒸馏）复现 Limit of RLVR（arXiv:2504.13837）的 pass@k 反转——验证「RLVR 在系统域只是分布锐化器」
> **状态**：设计完成 + 代码骨架就绪，**待移植到有 GPU + HuggingFace 访问的环境运行**
> **本机约束**：无 GPU / HF 不通 / LeanDojo 未装 → 完整实验本机不可行
> **依据**：[Limit of RLVR 精读](./05-paper-limit-of-rlvr.md) §六 + §八

---

## 一、实验假设（可证伪）

**H1（复现 Limit of RLVR）**：在系统域 Lean4 规则蒸馏上，RLVR model（GRPO 训练）在小 k（pass@1）赢 base，但在大 k（pass@256）被 base 反超。

**H2（系统域强化版，R5§6）**：如果用 buggy trace 作 base 先验，RLVR 会强化 buggy 规则（pass@1 升但规则语义错），Lean4 仍证明通过——实证「完美证明错误规则」。

**H1 若成立** = 系统域首次实证 RLVR 是锐化器（论文级贡献）。
**H2 若成立** = R5§6 命门的实验验证（position paper 的核心证据）。

---

## 二、实验设计（对标 Limit of RLVR §3）

### 2.1 数据准备

| 数据集 | 来源 | 角色 |
|--------|------|------|
| **训练集** | SpinlockPreempt v2 的规则变体（自动生成 200+ 条）+ dsyme 716 定理子集（Raft 域，~100 条）| GRPO 训练 |
| **in-domain 测试** | SpinlockPreempt 持出 50 条规则变体 | pass@k 评估 |
| **out-of-domain 测试** | dsyme Raft 定理持出 50 条 | 泛化性 |
| **系统域 f2f**（新建）| 从 SpinlockPreempt/dsyme/Atmosphere 抽 (state, spec, proof) 三元组 100 条 | benchmark（B1 §8.2 建议）|

### 2.2 模型与算法

| 维度 | 选择 | 理由 |
|------|------|------|
| Base model | **Qwen2.5-7B-Math** 或 DeepSeek-Prover-V2-7B | 数学推理基座，Limit of RLVR 同款 |
| RL 算法 | **GRPO**（DeepSeek 标准）+ 对照 PPO/Reinforce++ | 对标论文 6 算法 |
| RL 框架 | **veRL**（论文同款）或 OpenRLHF | 复现一致性 |
| Lean 后端 | **LeanDojo-v2 + Pantograph**（Lean4 RPC）| GRPO reward = Lean 验证通过 |
| 训练步数 | 832 步（对标 Code-R1）|  |

### 2.3 评估协议（严格对标 Limit of RLVR）

- **pass@k**：k ∈ {1, 8, 32, 128, 256}
- 采样：temperature=0.6, top-p=0.95, max 16384 tokens
- **base model 不用 few-shot**（消除混淆），zero-shot 同 RLVR prompt
- 低方差无偏 pass@k 估计（论文 Appendix A.2）
- 每个规则采样 256 次，统计「至少一次证明成立」的比例

### 2.4 关键指标

| 指标 | 定义 | 期望（H1）|
|------|------|----------|
| pass@1 | 单次采样证明成立率 | RLVR > base |
| pass@256 | 256 次采样至少一次成立 | **base > RLVR**（反转）|
| Δ_SE | base.pass@256 − RLVR.pass@1 | 大（RLVR 远离最优）|
| 覆盖率 | RLVR 解的规则集合 | ⊂ base 解的规则集合 |
| PPL_base(Y_RL) | RLVR 输出在 base 下的困惑度 | 低（在 base 分布内）|

---

## 三、代码骨架（可移植）

文件结构（`../../07-experiments/pass-k`）：

```
../../07-experiments/pass-k
├── README.md              ← 本设计的简化版 + 运行指南
├── data_prep.py           ← 数据准备（规则变体生成 + dsyme 切分）
├── train_grpo.py          ← GRPO 训练（veRL 框架）
├── eval_passk.py          ← pass@k 评估
├── lean_reward.py         ← LeanDojo reward（Lean4 验证）
└── configs/
    └── grpo_spinlock.yaml ← 训练超参
```

### 3.1 `lean_reward.py`（核心：Lean4 验证作 reward）

```python
"""
Lean4 验证作 GRPO 的 reward。
用 LeanDojo-v2 + Pantograph 作 Lean4 RPC。
reward = 1.0 if Lean 接受证明 else 0.0（二元，RLVR 标准）
"""
from lean_dojo import LeanGitRepo, Dojo, TacticState, CommandError

class Lean4Verifier:
    """Lean4 证明验证器（GRPO reward 后端）"""
    def __init__(self, repo_path, lean_version="4.21.0"):
        self.repo = LeanGitRepo.of(repo_path)
        self.dojo = Dojo(self.repo)  # Pantograph RPC
    
    def verify(self, theorem_statement: str, proof: str) -> bool:
        """验证 proof 是否证明 theorem。返回 True/False（reward）。"""
        try:
            state = self.dojo.run_tac(theorem_statement, proof)
            return state.is_solved  # Lean 接受 = reward 1.0
        except CommandError:
            return False  # Lean 拒绝 = reward 0.0

# GRPO 训练时调用：
# verifier = Lean4Verifier("04-layers/l2_5-formal-rules/formal-seed")
# reward = 1.0 if verifier.verify(rule, generated_proof) else 0.0
```

### 3.2 `train_grpo.py`（骨架）

```python
"""
GRPO 训练：base model → RLVR model。
框架：veRL（对标 Limit of RLVR）。
数据：(规则陈述, 正确证明) 对，从 SpinlockPreempt/dsyme 生成。
"""
# 伪代码骨架（需 veRL + GPU + HuggingFace 环境）
#
# from verl import GRPOTrainer, GRPOConfig
# from transformers import AutoModelForCausalLM, AutoTokenizer
#
# # 1. 加载 base model
# model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-7B-Math")
# tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Math")
#
# # 2. GRPO 配置（对标 Limit of RLVR §4.3）
# config = GRPOConfig(
#     num_rollouts_per_prompt=8,      # G=8（GRPO 组大小）
#     learning_rate=1e-6,             # 论文同款
#     max_rollout_length=8192,
#     sampling_temperature=1.0,
#     kl_coef=0.0,                    # DAPO/Oat-Zero 去 KL
#     total_steps=832,
# )
#
# # 3. reward = Lean4 验证
# verifier = Lean4Verifier("04-layers/l2_5-formal-rules/formal-seed")
# def reward_fn(prompts, responses):
#     return [1.0 if verifier.verify(p, r) else 0.0 
#             for p, r in zip(prompts, responses)]
#
# # 4. 训练
# trainer = GRPOTrainer(model=model, config=config, reward_fn=reward_fn,
#                       train_dataset=load_spinlock_rules())
# trainer.train()
#
# # 5. 保存
# model.save_pretrained("outputs/rlvr-spinlock-step832")

if __name__ == "__main__":
    print("⚠️ 本脚本需 GPU + HuggingFace + veRL + LeanDojo 环境")
    print("当前环境（neo-os 本机）无这些依赖，需移植到 GPU 机器运行")
    print("参见 02-research/rl/06-pass-k-experiment-design.md 的运行指南")
```

### 3.3 `eval_passk.py`（骨架）

```python
"""
pass@k 评估：对标 Limit of RLVR §2.2。
对每条规则采样 k 次，统计「至少一次证明成立」。
"""
import numpy as np

def pass_at_k(n: int, c: int, k: int) -> float:
    """无偏 pass@k 估计（Chen 2021）。n=总采样, c=成功数, k=查询数。"""
    if n - c < k:
        return 1.0
    return 1.0 - np.prod(1.0 - k / np.arange(n - c + 1, n + 1))

def evaluate_passk(model, verifier, rules, k_values=[1, 8, 32, 128, 256],
                   n_samples=256, temperature=0.6, top_p=0.95):
    """
    对每条 rule 采样 n_samples 次，算各 k 的 pass@k。
    返回 {k: avg_pass_at_k}。
    """
    results = {k: [] for k in k_values}
    for rule in rules:
        # 采样 n_samples 个证明尝试
        proofs = model.generate([rule.statement]*n_samples,
                                temperature=temperature, top_p=top_p)
        # 验证每个
        successes = sum(verifier.verify(rule.statement, p) for p in proofs)
        c, n = successes, n_samples
        for k in k_values:
            results[k].append(pass_at_k(n, c, k))
    return {k: np.mean(v) for k, v in results.items()}

# 运行：
# base_results = evaluate_passk(base_model, verifier, test_rules)
# rlvr_results = evaluate_passk(rlvr_model, verifier, test_rules)
# 画 pass@k 曲线，观察反转
```

---

## 四、H2 实验：buggy trace 先验（R5§6 验证）

**目标**：验证「trace 固化 bug → 完美证明错误规则」。

### 4.1 构造 buggy 先验

1. 取 SpinlockPreempt v2 的正确 Inv
2. 人为构造 buggy Inv（如去掉 `¬deadlocked` 子句，或加一个错误的 schedule 约束）
3. 生成 buggy 证明（Lean4 仍能证——因为 buggy Inv 在 buggy safe 上成立）

### 4.2 RLVR 训练

- Base = Qwen2.5-7B-Math
- 训练数据 = buggy 规则（来自 buggy trace 蒸馏）
- reward = Lean4 验证通过（二元）

### 4.3 评估

| 指标 | 期望（H2）|
|------|----------|
| pass@1（buggy 规则）| RLVR > base（强化 buggy 规则）|
| 语义正确性 | 🟥 RLVR model 输出的规则 100% 是 buggy 的 |
| Lean4 soundness | ✅ 全部证明通过（数学级可靠）|
| 人工审计 | 规则编码了错误行为 |

**H2 若成立**：实证「Lean4 完美证明错误规则」——这是 position paper 的核心证据，也是对抗层 v2.0 的实验支撑。

---

## 五、运行指南（移植到 GPU 环境）

### 5.1 环境要求

```bash
# 硬件
GPU: 1× A100 80GB 或 2× RTX 4090（7B 模型训练 + 256× rollout）
RAM: 64GB+

# 软件
pip install vllm torch transformers
pip install lean-dojo  # Lean4 Python 接口
pip install verl       # GRPO 训练框架（github.com/volcengine/verl）

# Lean4
curl https://raw.githubusercontent.com/leanprover/elan/.../elan-init.sh | sh
# lean-toolchain pin 4.21.0（与 SpinlockPreempt v2 一致）

# 模型（HuggingFace）
huggingface-cli download Qwen/Qwen2.5-Math-7B
```

### 5.2 运行步骤

```bash
cd 07-experiments/pass-k

# 1. 数据准备
python data_prep.py  # 生成规则变体 + 切分 train/test

# 2. 训练 RLVR model（~12-24h on A100）
python train_grpo.py --config configs/grpo_spinlock.yaml

# 3. pass@k 评估（~6h on A100，256 采样 × 100 规则）
python eval_passk.py --model base --rules test/
python eval_passk.py --model outputs/rlvr-spinlock-step832 --rules test/

# 4. 画 pass@k 曲线，观察反转
python plot_results.py
```

### 5.3 预期产出

- `results/passk_curve.png`：base vs RLVR 的 pass@k 曲线（期望大 k 反转）
- `results/coverage_venn.png`：可解规则集合的 Venn 图（期望 RLVR ⊂ base）
- `results/buggy_h2.json`：H2 实验的 buggy 规则强化数据

---

## 六、价值与风险

### 价值
- **H1 成立** → 系统域首次实证 RLVR 是锐化器（NeurIPS/ICML 级贡献）
- **H2 成立** → R5§6 命门的实验验证（position paper 核心证据）
- **系统域 f2f 基准**（新建）→ 蓝海研究资产

### 风险
- **H1 不成立**（系统域与数学域不同）→ 也是有趣发现（为什么不同？）
- **LeanDojo reward 慢**（每次验证秒级，256×100 = 25600 次）→ 需批量并行 + 缓存
- **GRPO 训练不稳**（超参敏感）→ 用论文同款配置降低风险

---

## 七、📌 下一步（待环境就绪）

1. **移植**：把 `../../07-experiments/pass-k` 移到有 GPU + HF 的环境
2. **装依赖**：veRL + LeanDojo + Pantograph + 模型权重
3. **跑 H1**：先复现 Limit of RLVR 反转（系统域版）
4. **跑 H2**：buggy trace 先验实验（R5§6 验证）
5. **写论文**：H1+H2 结果 → position paper 实证章节

---

*本设计文档 + 代码骨架作为 pass@k 实验的可移植蓝图。本机约束使其不能立即跑，但在有 GPU 的环境可直接执行。*
