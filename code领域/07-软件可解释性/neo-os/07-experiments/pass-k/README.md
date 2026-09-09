# pass@k 实验（系统域 RLVR）

> **状态**：设计 + 骨架就绪，**待移植到 GPU 环境**
> **设计文档**：[`02-research/rl/06-pass-k-experiment-design.md`](../../02-research/rl/06-pass-k-experiment-design.md)
> **依据**：[Limit of RLVR 精读](../../02-research/rl/05-paper-limit-of-rlvr.md)

## 目标

在系统域（Lean4 规则蒸馏）复现 Limit of RLVR（arXiv:2504.13837）的 pass@k 反转：
- **H1**：RLVR model 小 k 赢 base，大 k 被反超（系统域首次实证 RLVR 是锐化器）
- **H2**：buggy trace 先验 → RLVR 强化 buggy 规则（R5§6 命门验证）

## 本机约束

❌ 无 GPU / HuggingFace 不通 / LeanDojo 未装 → **完整实验本机不可行**

## 移植运行

```bash
# 在有 GPU + HF 的环境：
pip install verl lean-dojo vllm torch transformers
huggingface-cli download Qwen/Qwen2.5-Math-7B

python data_prep.py          # 数据准备
python train_grpo.py         # GRPO 训练（~12-24h A100）
python eval_passk.py         # pass@k 评估
```

## 文件

| 文件 | 作用 | 状态 |
|------|------|------|
| `lean_reward.py` | Lean4 验证作 GRPO reward（核心）| ✅ 骨架 |
| `data_prep.py` | 规则变体生成 + dsyme 切分 | 待移植时从设计文档提取 |
| `train_grpo.py` | GRPO 训练（veRL）| 待移植时从设计文档提取 |
| `eval_passk.py` | pass@k 评估 | 待移植时从设计文档提取 |

代码骨架在设计文档 §三，移植时提取为独立文件。
