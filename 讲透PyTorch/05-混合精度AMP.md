# 05 · 混合精度 AMP

> **自动混合精度**（Automatic Mixed Precision）：前向用低精度（fp16/bf16）省一半内存+加速，关键计算仍保 fp32 保精度。是 GPU 训练加速的标配。

---

## 一、为什么用低精度

| 精度 | 字节 | 速度 | 风险 |
|------|------|------|------|
| fp32 | 4 | 基准 | 无 |
| **fp16** | 2 | GPU 快 1.5–3× | 指数位窄，**梯度下溢**（小数变 0）|
| **bf16** | 2 | 快 | 指数位同 fp32（不下溢），但尾数少 |

> bf16 是"安全的 fp16"——不丢数值范围，近年（H100/A100）首选。

## 二、AMP 两件套

```python
scaler = torch.cuda.amp.GradScaler()   # fp16 才需要(bf16 不用)
with torch.autocast("cuda", dtype=torch.float16):   # 前向自动选低精度
    loss = loss_fn(model(x), y)
scaler.scale(loss).backward()          # 放大 loss 防梯度下溢
scaler.step(opt); scaler.update()      # 反缩放后更新
```

- **`autocast`**：上下文内自动把"安全"的算子（matmul/conv）降精度，"危险"的（softmax/sum）保 fp32。
- **`GradScaler`**：fp16 专用，放大 loss 让小梯度不下溢，更新前再反缩放。**bf16 不需要 scaler**（指数位够）。

## 三、CPU 上的情况
CPU 也支持 bfloat16 autocast（实验09 实测），但主要是省内存，加速有限（CPU 浮点算力本就弱）。

## 四、批判性视角
- **不是所有算子都该降精度**。autocast 有白名单/黑名单，涉及数值稳定（softmax/norm）的保 fp32。
- **bf16 优先**。新硬件上 bf16 兼顾速度和安全，逐步取代 fp16。
- **评估也要 autocast**，保持训练/推理一致。

## 📌 下一步
- 跑 `experiments/09_amp_scheduler.py`（autocast 实测）。
- 进阶训练工程 → [03-训练循环](03-训练循环.md)（含调度器/累积/裁剪）。

## ✍️ 练习
1. fp16 为何会梯度下溢？bf16 为何不会？
2. GradScaler 为何 bf16 不需要？
3. autocast 为何不把所有算子都降精度？
