# 损失函数全景精读：从 MSE 到 Contrastive

> 参照：PyTorch nn.functional / Goodfellow Deep Learning §6-8
>
> csdiy 对应：tinytorch/loss.py + nanoGPT精读 + AI核心

---

## 一、损失函数的本质

损失函数 L(y_pred, y_true) 衡量"预测和真相的差距"。训练 = 最小化 L。

**好的损失函数**：
1. 在零附近梯度大（快速学习）
2. 在远处梯度不爆炸（稳定训练）
3. 和评估指标一致（优化目标 = 业务目标）

---

## 二、回归损失

### MSE（Mean Squared Error）

```
L = (1/N) Σ (y_pred - y_true)²
∂L/∂y_pred = (2/N)(y_pred - y_true)
```

- **优点**：凸函数，梯度平滑
- **缺点**：对离群值敏感（误差被平方放大）
- **适用**：回归、年龄预测、温度预测

### MAE（Mean Absolute Error）

```
L = (1/N) Σ |y_pred - y_true|
∂L/∂y_pred = (1/N) sign(y_pred - y_true)
```

- **优点**：对离群值不敏感
- **缺点**：梯度恒定（不随误差变化）→ 训练后期收敛慢
- **适用**：有离群值的回归

### Huber Loss（MSE + MAE 折中）

```
L = { 0.5(y_pred-y_true)²     if |error| < δ
    { δ(|error| - 0.5δ)      otherwise
```

- 小误差时用 MSE（平滑梯度）
- 大误差时用 MAE（不爆炸）
- **适用**：强化学习（PPO 的 value loss）

---

## 三、分类损失

### Cross Entropy（交叉熵）

```
L = -Σ y_true × log(y_pred)
```

多分类简化版（target 是 one-hot）：
```
L = -log(y_pred[target_class])
```

**和 Softmax 的合并梯度**（参照 softmax-temperature精读）：
```
∂L/∂logits = softmax(logits) - one_hot(target)
```

→ 梯度 = 预测概率 - 目标 → 非常直觉！

### Binary Cross Entropy

```
L = -(y log(p) + (1-y) log(1-p))
∂L/∂p = (p - y) / (p(1-p))
```

- **适用**：二分类（垃圾邮件/欺诈检测）
- **注意**：输入是概率（0-1），不是 logits

### Focal Loss（Lin 2017）

```
L = -α(1-p_t)^γ log(p_t)
```

- `p_t`：正确类别的预测概率
- `γ`：聚焦参数（通常 2.0）
- `(1-p_t)^γ`：降低易分样本的权重

**直觉**：
```
样本分类正确 (p_t=0.99)：权重 = (0.01)^2 = 0.0001 → 几乎不学
样本分类错误 (p_t=0.3)：权重 = (0.7)^2 = 0.49 → 大幅学习
```

**适用**：类别不平衡（目标检测中背景远多于前景）

---

## 四、排序/嵌入损失

### Triplet Loss（FaceNet）

```
L = max(0, d(anchor, positive) - d(anchor, negative) + margin)
```

- anchor, positive：同类（如同一个人的两张照片）
- negative：异类
- 目标：让 anchor-positive 的距离 < anchor-negative 的距离 - margin

### Contrastive Loss（SimCLR）

```
# 正样本对
L_pos = -log(exp(sim(z_i, z_j)/τ) / Σ exp(sim(z_i, z_k)/τ))
```

- z_i, z_j：同一样本的两个增强视图（正样本对）
- z_k：其他样本（负样本）
- τ：温度
- **适用**：自监督学习（SimCLR/MoCo/CLIP）

### InfoNCE（GPT 预训练用的）

```
# 预测下一个 token = 分类问题
L = -log P(token_t | token_1, ..., token_{t-1})
= CrossEntropy(logits, target_token)
```

→ GPT/LLaMA 的预训练损失就是 Cross Entropy！

---

## 五、正则化损失

### L2 正则化（Weight Decay）

```
L_total = L_task + λ × ||W||²
```

- 惩罚大权重 → 防止过拟合
- AdamW 的 weight_decay 就是解耦版 L2

### L1 正则化

```
L_total = L_task + λ × ||W||₁
```

- 产生稀疏权重（很多=0）→ 特征选择

### KL Divergence（知识蒸馏）

```
L_distill = α × CE(student, hard_labels) + (1-α) × T² × KL(student_T || teacher_T)
```

- T：温度（让 softmax 输出更"软"）
- 学生模型学习教师模型的"暗知识"（soft labels）

---

## 六、损失函数选择指南

```
你的任务是什么？
│
├── 回归
│   ├── 无离群值 → MSE
│   ├── 有离群值 → Huber
│   └── 健壮需求 → MAE
│
├── 分类
│   ├── 二分类 → BCE
│   ├── 多分类（平衡）→ Cross Entropy
│   └── 多分类（不平衡）→ Focal Loss
│
├── 嵌入/排序
│   ├── 人脸/相似度 → Triplet
│   ├── 对比学习 → Contrastive / InfoNCE
│   └── 检索 → Margin Ranking
│
└── 特殊
    ├── 知识蒸馏 → KL Divergence
    ├── GAN → min-max（非标准损失）
    └── VAE → ELBO（重建 + KL）
```

---

## 七、你的 tinytorch/loss.py

```python
# 已实现的损失函数
mse_loss(pred, target)           # 回归
cross_entropy(logits, target)    # 分类（softmax+CE合并）
binary_ce(pred_prob, target)     # 二分类
focal_loss(logits, target, γ)   # 不平衡分类
```

每个都返回 `Value`（支持自动微分）→ 梯度由 `backward()` 自动计算。

---

## 八、一句话总结

> MSE 用于回归，Cross Entropy 用于分类，Focal 解决不平衡，Contrastive 用于嵌入。
>
> GPT 的预训练损失 = Cross Entropy（预测下一个 token = 多分类）。
>
> **损失函数 = "告诉模型它做得怎么样" → 选对损失函数 = 一半的成功。**

---

*配套：[tinytorch/loss.py](../projects/tinytorch/loss.py) | [softmax-temperature精读](softmax-temperature-精读.md) | [backprop-graph精读](backprop-graph-精读.md)*
