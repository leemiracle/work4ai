# 学习率调度精读：Warmup + Cosine Annealing

> 参照：nanoGPT train.py §8.3 / Vaswani 2017 / Loshchilov 2017
>
> csdiy 对应：nanoGPT精读 + tinytorch/optim.py + AI核心

---

## 一、为什么固定学习率不够好

```
训练初期（权重随机）：
  → 梯度方向噪声大 → 大 lr 会"跑偏" → 需要 warmup

训练中期（接近最优）：
  → 需要"大步探索" → 保持较高 lr

训练后期（接近收敛）：
  → 需要"小步精调" → 降低 lr → cosine annealing
```

---

## 二、Warmup（预热）

### 问题

Transformer 的训练初期非常不稳定：
- 初始权重随机 → 梯度方向几乎随机
- 大 lr → 参数被随机推到坏的区域 → 无法恢复

### 解法：线性 Warmup

```
lr(t) = max_lr × (t+1) / warmup_steps   （t < warmup_steps）
```

前 warmup_steps 步，lr 从 0 线性增长到 max_lr。

### 效果

```
Step 0:   lr = 0.0001  → 几乎不更新（安全）
Step 500: lr = 0.003   → 到达目标 lr（开始正式训练）
```

### 典型值

| 模型 | warmup_steps | max_lr |
|------|-------------|--------|
| nanoGPT | 100-500 | 3e-4 |
| GPT-3 | 375M (总步数的 0.3%) | 6e-5 |
| LLaMA-7B | 2000 | 3e-4 |

---

## 三、Cosine Annealing（余弦退火）

### 公式

```
After warmup:
progress = (t - warmup) / (max_steps - warmup)
lr = min_lr + (max_lr - min_lr) × 0.5 × (1 + cos(π × progress))
```

### 曲线

```
lr
max_lr ─────╮
            │ ╲
            │   ╲
            │     ╲
            │       ╲
min_lr     │         ╰──────
           └──┬──────────┬────→ step
           warmup      max_steps
```

### 为什么余弦

1. **平滑下降**：没有突变 → 训练稳定
2. **初期下降慢**：保持探索能力
3. **末期下降快**：精确定位最小值

### 你的 tinytorch/optim.py 的实现

```python
class CosineScheduler:
    def step(self):
        t = self.opt.t
        if t < self.warmup:
            lr = self.max_lr * (t + 1) / self.warmup  # 线性 warmup
        else:
            progress = (t - self.warmup) / (self.max_steps - self.warmup)
            lr = self.min_lr + (self.max_lr - self.min_lr) * 0.5 * (1 + cos(π * progress))
        self.opt.lr = lr
```

---

## 四、其他调度策略

### Step Decay（阶梯衰减）

```
lr = max_lr × γ^floor(t / step_size)

例：每 1000 步 × 0.1
Step 0:    lr = 0.001
Step 1000: lr = 0.0001
Step 2000: lr = 0.00001
```

代表：ResNet 训练（ImageNet）。

### Exponential Decay

```
lr = max_lr × γ^t  （每步衰减 γ 倍）
```

### OneCycle（Super-Convergence）

```
Phase 1 (0%→30%): lr 从 max_lr/25 → max_lr（快速上升）
Phase 2 (30%→100%): lr 从 max_lr → max_lr/25（余弦下降）
```

代表：fast.ai / 超收敛训练。

### WSD（Warmup-Stable-Decay，LLaMA 2 用）

```
Phase 1: warmup（线性上升）
Phase 2: stable（保持 max_lr）
Phase 3: decay（余弦下降到 min_lr）
```

---

## 五、学习率太大/太小的症状

### 太大

```
Loss 震荡不下降 / NaN / Inf
→ 检查：梯度范数 > 10 → lr 太大
→ 修复：lr /= 10
```

### 太小

```
Loss 下降极慢（100 步只降 0.001）
→ 检查：梯度范数 < 0.001 → lr 可能太小
→ 修复：lr *= 3
```

### 刚好

```
Loss 平滑下降，偶尔有小波动
梯度范数 ∈ [0.1, 10]
```

---

## 六、学习率查找（LR Finder，Smith 2017）

```python
# 从极小 lr 开始，逐步增大，记录 loss
lr = 1e-7
for batch in dataloader:
    loss = train_step(batch, lr)
    losses.append(loss); lrs.append(lr)
    lr *= 1.01  # 指数增长

# 画 loss vs lr 曲线
# 最低点对应的 lr × 10 = 最佳 lr
```

**经验值**：
- Transformer: 1e-4 ~ 5e-4
- CNN: 1e-3 ~ 1e-2
- Fine-tuning: 1e-5 ~ 1e-4（比从头训练小 10x）

---

## 七、Gradient Clipping（梯度裁剪）

和 lr 调度配合使用（参照 nanoGPT §8.4）：

```python
# 裁剪梯度范数（防止梯度爆炸）
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
optimizer.step()
```

**效果**：如果梯度范数 > 1.0 → 缩放到 1.0 → 防止单步更新太大。

---

## 八、完整训练调度（nanoGPT 实践）

```python
# nanoGPT train.py 的完整 lr 策略
max_lr = 6e-4
min_lr = 6e-5
warmup_steps = 100
max_steps = 10000

# 每步：
scheduler.step()  # 更新 lr（warmup → cosine）
loss.backward()
clip_grad_norm_(1.0)  # 梯度裁剪
optimizer.step()
```

---

## 九、一句话总结

> Warmup（初期安全）+ Cosine（平滑退火）= Transformer 标配调度。
>
> nanoGPT/Llama/Qwen 全用这个组合。固定 lr 是业余做法。
>
> **如果训练不收敛，第一检查学习率，第二检查初始化，第三检查数据。**

---

*配套：[nanoGPT精读 §8.3](nanoGPT-读懂最小GPT.md) | [tinytorch/optim.py](../projects/tinytorch/optim.py) | [weight-init精读](weight-init-精读.md)*
