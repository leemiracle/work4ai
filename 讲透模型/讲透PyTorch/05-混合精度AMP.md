# 05 · 混合精度 AMP：用一半显存几乎不损精度

> 自动混合精度（AMP）是 GPU 训练加速的**标配**——前向用 fp16/bf16 省一半显存 + 加速 1.5-3×，关键计算仍保 fp32。但"为什么 fp16 会梯度下溢""为什么 bf16 不需要 GradScaler"——这些细节决定了你是用对还是用崩。本篇讲透。

---

## 一、为什么用低精度：显存 + 速度双赢

| 精度 | 字节 | 显存 | 速度 | 风险 |
|---|:---:|:---:|:---:|---|
| fp32 | 4 | 基准 | 基准 | 无 |
| **fp16** | 2 | **省一半** | **快 1.5-3×** | 指数位窄 → **梯度下溢** |
| **bf16** | 2 | 省一半 | 快 | 指数位同 fp32（不溢），但尾数少（精度略降）|

> **一句话**：bf16 = "安全的 fp16"——同样省一半显存，但不会梯度下溢。近年（A100/H100）首选。

---

## 二、fp16 vs bf16 的数值本质（关键差异）

### 2.1 浮点数的结构

$$
\text{值} = (-1)^{\text{sign}} \times 2^{\text{exponent} - \text{bias}} \times (1.\text{mantissa})
$$

| 格式 | 指数位 | 尾数位 | 动态范围 | 精度 |
|---|:---:|:---:|:---:|:---:|
| fp32 | 8 | 23 | 大 | 高 |
| **fp16** | **5** | 10 | **小**（~6e-5 ~ 65504）| 中 |
| **bf16** | **8** | **7** | **大**（同 fp32）| 低 |

### 2.2 为什么 fp16 梯度下溢

深度网络的梯度常很小（如 1e-7）。fp16 的最小正常数约 6e-5——**比这小的值变 0**（下溢）。梯度变 0 → 参数不更新 → 训练停。

### 2.3 为什么 bf16 不下溢

bf16 的指数位和 fp32 相同（8 位），动态范围一样大。小到 1e-38 都能表示。代价是尾数只有 7 位（精度低），但神经网络对精度不敏感（对动态范围敏感）。

> **洞察**：神经网络训练**宁要动态范围大、不要精度高**。这就是 bf16 胜出 fp16 的根本原因。

---

## 三、AMP 两件套：autocast + GradScaler

### 3.1 autocast：自动选精度

```python
with torch.autocast("cuda", dtype=torch.bfloat16):  # 或 torch.float16
    logits = model(x)       # matmul/conv 转 bf16
    loss = loss_fn(logits, y)  # 部分 op 保 fp32（见下）
```

**autocast 的白名单/黑名单**（关键设计）：

| 算子类型 | 处理 | 为什么 |
|---|---|---|
| **matmul / conv / linear** | **转低精度** | 计算密集，省显存收益大 |
| **softmax / log_softmax** | 保 fp32 | 涉及 exp，易溢出 |
| **sum / mean / norm** | 保 fp32 | 累加小数易丢精度 |
| **embedding** | 保 fp32 | 索引查找，不是计算 |
| **loss** | 通常 fp32 | 数值稳定 |

**不是所有算子都降精度**——这是"混合精度"的含义。

### 3.2 GradScaler（仅 fp16 需要）

```python
scaler = torch.cuda.amp.GradScaler()  # fp16 才需要

with torch.autocast("cuda", dtype=torch.float16):
    loss = model(x)
scaler.scale(loss).backward()    # 放大 loss 防梯度下溢
scaler.step(opt)                  # 反缩放后更新
scaler.update()                   # 动态调放大倍数
```

**原理**：
1. `scaler.scale(loss)`：把 loss 乘以一个大数（如 65536）→ 反向传播的梯度也放大 → 不下溢
2. `scaler.step(opt)`：更新前把梯度**除回去** → 还原真实梯度
3. `scaler.update()`：如果出现 inf/NaN，跳过这步并减小放大倍数；否则可能增大

**bf16 不需要 scaler**——因为 bf16 的动态范围足够，梯度不下溢。

---

## 四、完整 AMP 训练循环（可直接抄）

```python
import torch
from torch.cuda.amp import autocast, GradScaler

model = MyModel().cuda()
opt = torch.optim.AdamW(model.parameters(), lr=1e-4)
use_fp16 = True  # V100 用 fp16；A100/H100 建议改 bf16（不需 scaler）
scaler = GradScaler(enabled=use_fp16)
dtype = torch.float16 if use_fp16 else torch.bfloat16

for x, y in dataloader:
    x, y = x.cuda(), y.cuda()
    opt.zero_grad()
    with autocast(dtype=dtype):
        loss = loss_fn(model(x), y)
    scaler.scale(loss).backward()
    scaler.unscale_(opt)                # unscale 后才能 clip
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    scaler.step(opt)
    scaler.update()
```

**注意 grad clip 的顺序**：必须 `unscale_` 后再 clip，否则 clip 的是放大后的梯度。

---

## 五、常见坑

1. **NaN 检查**：fp16 训练出现 NaN，多半是 GradScaler 放大倍数不对——检查 `scaler.get_scale()` 是否震荡
2. **评估也要 autocast**：训练用 AMP，推理也要用，保持一致（否则数值不匹配）
3. **某些算子不支持 fp16**：报错 `operation does not have an fp16 implementation` → 该算子保 fp32
4. **CPU 上 AMP 有限**：CPU 支持 bf16 autocast（实验09 实测），但 fp16 几乎不支持；加速也有限

---

## 六、批判性

- **AMP 不是免费的**：bf16 精度低，某些数值敏感任务（如高精度科学计算）可能掉点
- **"加速 2×"是理论值**：实际取决于 GPU 利用率——如果原本 GPU 就闲（数据瓶颈），AMP 加速不明显
- **新一代硬件方向**：H100 的 fp8 / Blackwell 的 fp4 正在把精度推更低——AMP 会持续演化

> **诚实结论**：AMP 是"免费午餐"——几乎不损精度却省一半显存。但理解 fp16/bf16 的数值差异和 GradScaler 原理，才能在训练出问题时快速定位（而不是"关掉 AMP 凑合跑"）。

---

## 📌 下一步
- 跑 `experiments/09_amp_scheduler.py`（AMP + 余弦退火实测）。
- 进阶训练工程 → [06-编译与图模式](06-编译与图模式.md)（torch.compile 深入）。

## ✍️ 练习
1. fp16 的最大值是 65504。如果训练 loss 突然飙到 100000，fp16 会发生什么？（提示：溢出成 inf。）
2. 为什么 GradScaler 要"动态调整"放大倍数，而不固定一个值？（提示：训练初期梯度大，后期小。）
3. bf16 的尾数只有 7 位（精度低），为什么神经网络训练仍能收敛？（提示：SGD 本身有噪声，精度损失被噪声淹没。）
