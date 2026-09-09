# Transformer 训练全流程精读：从 Pre-training 到 Deployment

> 参照：GPT-3 / LLaMA / nanoGPT train.py / HuggingFace Trainer
>
> csdiy 对应：nanoGPT精读 + data-pipeline精读 + lr-scheduling精读 + llm-deployment精读

---

## 一、LLM 生命周期

```
① Pre-training（预训练）
  数据: 万亿 token 的互联网文本
  目标: 预测下一个 token（自回归）
  成本: $1M-$100M+（GPU 集群训练数月）
  产出: base model（如 LLaMA-7B-base）

② Post-training（后训练）
  ├── SFT（指令微调）
  │   数据: 10K-1M 条指令-回复对
  │   成本: ~$100-1000（单 GPU 可做）
  │   产出: instruct model
  │
  ├── RLHF / DPO（对齐）
  │   数据: 偏好对（chosen > rejected）
  │   成本: ~$500-5000
  │   产出: aligned model
  │
  └── Continued Pre-training（领域适应）
      数据: 领域文本（医疗/法律/代码）
      产出: domain-specific model

③ 部署
  量化 → 推理引擎 → API 服务
```

---

## 二、Pre-training 详解

### 数据准备

```
原始数据 → 去重 → 质量过滤 → 分词 → 训练 batch

LLaMA-3 数据:
  15T tokens（混合: 网页 67% + 代码 5% + 书籍 5% + ...）
  分词: tiktoken BPE, 词表 128K
```

### 训练超参数（LLaMA-3 8B 参考）

```python
config = {
    "model": {
        "d_model": 4096, "n_heads": 32, "n_layers": 32,
        "vocab_size": 128256, "max_seq": 8192,
        "intermediate_size": 14336,  # FFN 中间维度
        "rope_theta": 500000,  # RoPE base
    },
    "training": {
        "batch_size": 512,  # global batch (gradient accumulation)
        "lr": 3e-4,  # max learning rate
        "min_lr": 3e-5,
        "warmup_steps": 2000,
        "total_steps": 630000,  # ~15T tokens / 8192 seq / 512 batch
        "weight_decay": 0.1,
        "grad_clip": 1.0,
        "optimizer": "AdamW",
        "precision": "BF16",
        "gradient_checkpointing": True,  # 省显存
    },
    "parallel": {
        "tensor_parallel": 1,  # 8B 不需要 TP
        "pipeline_parallel": 1,
        "data_parallel": 512,  # 512 GPU
        "sequence_parallel": True,
    }
}
```

### 训练循环（参照 nanoGPT train.py）

```python
for step in range(max_steps):
    # ① 学习率调度（warmup → cosine）
    lr = cosine_schedule(step)
    for g in optimizer.param_groups: g['lr'] = lr

    # ② 获取 batch
    x, y = get_batch()  # x=input tokens, y=target tokens (shifted by 1)

    # ③ 前向 + 计算 loss（交叉熵）
    logits = model(x)  # [B, T, vocab]
    loss = cross_entropy(logits.view(-1, vocab), y.view(-1))

    # ④ 梯度累积（模拟大 batch）
    (loss / grad_accum_steps).backward()

    # ⑤ 每 grad_accum_steps 步更新一次
    if (step + 1) % grad_accum_steps == 0:
        # 梯度裁剪
        clip_grad_norm_(model.parameters(), 1.0)
        # 优化器更新
        optimizer.step()
        optimizer.zero_grad()

    # ⑥ 日志 + checkpoint
    if step % log_interval == 0:
        log({"loss": loss.item(), "lr": lr, "step": step})
    if step % save_interval == 0:
        save_checkpoint(f"checkpoint-{step}.pt")
```

---

## 三、SFT 详解（指令微调）

### 数据格式

```json
{
    "messages": [
        {"role": "system", "content": "你是一个有帮助的助手。"},
        {"role": "user", "content": "解释什么是递归"},
        {"role": "assistant", "content": "递归是一种函数自己调用自己的编程技术..."}
    ]
}
```

### 训练

```python
# 只对 assistant 的回复计算 loss（不对 user 的输入计算）
for example in dataset:
    input_ids = tokenize(example)
    labels = input_ids.copy()
    # mask 掉 user 的部分
    labels[user_start:user_end] = -100  # PyTorch 的 ignore_index
    loss = cross_entropy(model(input_ids), labels)

# LoRA 微调（省显存）
model = AutoModelForCausalLM.from_pretrained("llama-7b", load_in_4bit=True)
model = get_peft_model(model, LoraConfig(r=16, target_modules=["q_proj","v_proj"]))
# 只训练 LoRA 参数（~50MB），冻结原始 7B 参数
```

---

## 四、DPO 详解（Direct Preference Optimization）

```python
# 数据: 同一个 prompt 的两个回复（chosen > rejected）
data = [
    {"prompt": "什么是 AI？",
     "chosen": "AI 是模拟人类智能的技术...",
     "rejected": "AI 就是机器人。"}
]

# DPO loss（参照 fine-tuning-landscape精读）
def dpo_loss(policy_chosen_logp, policy_rejected_logp,
             ref_chosen_logp, ref_rejected_logp, beta=0.1):
    chosen_reward = beta * (policy_chosen_logp - ref_chosen_logp)
    rejected_reward = beta * (policy_rejected_logp - ref_rejected_logp)
    return -F.logsigmoid(chosen_reward - rejected_reward).mean()
```

---

## 五、训练调试技巧

### Loss 不降

```
检查清单:
① 学习率太大/太小 → LR Finder
② 梯度爆炸 → clip_grad_norm=1.0
③ 梯度消失 → 检查激活值 std（应≈1）
④ 数据问题 → 检查 token 分布
⑤ 初始化 → std=0.02
⑥ Bug → 用最小数据集过拟合验证（loss 应能降到接近 0）
```

### 过拟合

```
训练 loss 降但验证 loss 涨:
① 数据不够 → 增加数据
② 正则化 → 增大 weight_decay / dropout
③ 早停 → 保存最优 checkpoint
④ LoRA rank 太大 → 降 rank
```

### 显存不够

```
梯度检查点 → 用计算换显存（省 30-60%）
gradient_accumulation → 小 batch 模拟大 batch
LoRA → 只训练 0.5% 参数
QLoRA → 4-bit 冻结权重
Flash Attention → 减少 attention 内存
```

---

## 六、训练成本估算

| 模型大小 | GPU | 时间 | 成本 | 方法 |
|---------|-----|------|------|------|
| nanoGPT (1M) | 1× RTX 4090 | 5 min | $0.01 | 从头训练 |
| GPT-2 small (124M) | 1× A100 | 4 hours | $10 | 从头训练 |
| LLaMA-7B SFT | 1× A100 | 3 hours | $10 | QLoRA |
| LLaMA-70B SFT | 4× A100 | 10 hours | $200 | QLoRA |
| LLaMA-7B 全参 FT | 8× A100 | 10 hours | $200 | Full FT |
| LLaMA-3-70B 预训练 | 16384× H100 | 54 days | ~$65M | Pre-training |

---

## 七、一句话总结

> Pre-training: 自回归 + AdamW + Warmup/Cosine + BF16 + Flash Attention。
> SFT: 指令数据 + LoRA/QLoRA（$10 微调 7B）。
> DPO: 偏好数据 → 直接优化策略（不需要 RM/PPO）。
>
> **从 nanoGPT train.py 到 LLaMA-3 的训练循环，核心逻辑完全一样——只是规模不同。**

---

*配套：[nanoGPT精读](nanoGPT-读懂最小GPT.md) | [lr-scheduling精读](lr-scheduling-精读.md) | [fine-tuning-landscape精读](fine-tuning-landscape-精读.md) | [data-pipeline精读](data-pipeline-精读.md) | [llm-deployment精读](llm-deployment-精读.md)*
