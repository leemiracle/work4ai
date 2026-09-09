# 混合精度训练精读：FP16 / BF16 / FP8

> 参照：NVIDIA Mixed Precision / Micikevicius 2017 / LLaMA 训练
>
> csdiy 对应：tinyquantize + nanoGPT精读 + AI前沿

---

## 一、为什么用低精度

```
FP32 (单精度):  4 bytes × 7B 参数 = 28GB → 一张 A100 放不下
FP16 (半精度):  2 bytes × 7B 参数 = 14GB → 能放下
BF16:           2 bytes × 7B 参数 = 14GB → 能放下
FP8:            1 byte  × 7B 参数 = 7B   → 多放一倍
```

**低精度 = 少显存 = 更大模型 / 更大 batch = 更快训练**。

---

## 二、三种浮点格式

### FP32（标准单精度）

```
[1 sign][8 exponent][23 mantissa]  = 32 bits
动态范围: ±3.4×10^38
精度: ~7 位有效数字
```

### FP16（半精度）

```
[1 sign][5 exponent][10 mantissa]  = 16 bits
动态范围: ±65504          ← 很小！
精度: ~3 位有效数字
问题: 动态范围小 → 梯度溢出/下溢
```

### BF16（Brain Float 16，Google）

```
[1 sign][8 exponent][7 mantissa]  = 16 bits
动态范围: ±3.4×10^38        ← 和 FP32 相同！
精度: ~2 位有效数字         ← 比 FP16 更粗
优势: 不溢出 → 训练最稳定
```

### FP8（最新标准）

```
E4M3: [1 sign][4 exponent][3 mantissa] = 8 bits → 精度优先
E5M2: [1 sign][5 exponent][2 mantissa] = 8 bits → 范围优先
```

---

## 三、混合精度训练策略

### 核心原则

```
前向传播:  FP16/BF16（快 + 省显存）
梯度计算:  FP16/BF16（快）
梯度更新:  FP32（精确，防止精度损失）
master 权重: FP32（保持高精度累积）
```

### NVIDIA AMP（Automatic Mixed Precision）

```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()  # 梯度缩放器（FP16 专用）

for batch in dataloader:
    optimizer.zero_grad()

    with autocast(dtype=torch.bfloat16):  # 或 torch.float16
        output = model(batch)
        loss = criterion(output, target)

    scaler.scale(loss).backward()  # 放大梯度（防 FP16 下溢）
    scaler.step(optimizer)
    scaler.update()
```

### 为什么 BF16 不需要 GradScaler

```
FP16: 梯度可能 < 2^(-24) → 下溢为 0 → 需要 scaler 放大
BF16: 指数位和 FP32 相同 → 不会下溢 → 不需要 scaler
→ BF16 更简单，是当前训练首选
```

---

## 四、精度问题的症状

### FP16 溢出

```
loss = NaN / Inf
→ 梯度 > 65504 → 溢出
→ 修复: 降低 lr / 用 BF16 / 用 GradScaler
```

### FP16 下溢

```
训练不收敛（loss 不降）
→ 梯度 < 2^(-14) → 变成 0 → 不更新
→ 修复: GradScaler 放大梯度
```

### BF16 精度不足

```
优化器累积误差大（Adam 的 m/v 累积）
→ 修复: 优化器状态保持 FP32（AMP 自动处理）
```

---

## 五、量化训练（更激进）

### FP8 训练（Hopper GPU）

```
H100 GPU 原生支持 FP8 → 训练速度再翻倍

# NVIDIA Transformer Engine
import transformer_engine as te
model = te.TransformerLayer(d_model, n_heads)
# 自动在 FP8/FP16/BF16 之间切换
```

### 量化感知训练（QAT）

```
训练时模拟量化噪声 → 模型学会适应低精度
→ 推理时全量化（INT8）→ 速度快 4x

# PyTorch QAT
model.qconfig = torch.quantization.get_default_qat_qconfig('fbgemm')
model = torch.quantization.prepare_qat(model)
```

---

## 六、精度选择指南

```
你有 H100 GPU 吗？
├── 是 → FP8（最快）或 BF16
└── 否 → 你有 A100/V100 吗？
    ├── 是 → BF16（首选）或 FP16+AMP
    └── 否（消费级 GPU）
        └── FP16 + GradScaler（唯一选择，BF16 不支持）
```

### 各场景推荐

| 场景 | 推荐精度 | 原因 |
|------|---------|------|
| 从头训练 LLM | BF16 | 稳定，不溢出 |
| 微调（LoRA） | BF16 | 同上 |
| 推理（部署） | INT8/INT4 | 速度/省显存 |
| 研究实验 | FP32 | 精确复现 |
| 移动端部署 | INT4 | 内存限制 |

---

## 七、和 tinyquantize 的交叉

你的 `tinyquantize`（已整合）实现了 INT8 量化：
```python
def quantize_fp32_to_int8(weights):
    max_abs = max(abs(w) for w in weights)
    scale = max_abs / 127
    return [round(w / scale) for w in weights], scale
```

**推理量化** vs **训练量化**：
- 推理量化：训完再量化（Post-Training Quantization）→ 简单但精度损失大
- 训练量化：训练时量化（QAT）→ 复杂但精度好

---

## 八、一句话总结

> BF16 = FP32 的指数 + 更少的尾数 → 同样动态范围 + 省一半显存。
>
> **当前 LLM 训练的事实标准：BF16 训练 + FP32 优化器状态 + INT8/INT4 推理。**
>
> 混合精度 = 用低精度计算 + 用高精度累积 → 速度/精度两全。

---

*配套：[tinyquantize](../projects/tinyquantize/) | [nanoGPT精读](nanoGPT-读懂最小GPT.md) | [weight-init精读](weight-init-精读.md)*
