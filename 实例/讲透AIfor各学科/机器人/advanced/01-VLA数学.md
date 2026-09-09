# 机器人 · VLA 数学（Vision-Language-Action）

> **博士级**：VLA 架构的数学 + Flow Matching（π₀ 用）。

## 一、VLA 是什么

**输入**：图像 $I$ + 语言指令 $l$
**输出**：动作 $a$（机器人关节）

$$a = f_\theta(I, l)$$

**关键**：跨 embodiment（不同机器人用同一模型）。

## 二、RT-2 架构

### 2.1 核心：VLM → 动作 token 化

```
图像 I → ViT → 视觉 token
语言 l → LLM token
   ↓ Co-training
联合表示
   ↓ 动作 head
动作 token → 离散化（256 bins × 7 维）
```

### 2.2 动作 token 化

每个动作维度**离散化**为 256 bins，变成 token：

$$a_i = \text{token}_i \in \{0, 1, ..., 255\}$$

→ LLM 可以用标准 next-token prediction 训练。

### 2.3 训练

- 预训练：互联网图文数据
- 微调：机器人数据（co-fine-tune）

## 三、π₀ 的 Flow Matching

### 3.1 为什么不用 diffusion

- **Diffusion**：去噪过程慢（几十步）
- **Flow Matching**：连续流，可少步

### 3.2 数学

学一个向量场 $v_\theta(x_t, t)$，将噪声分布 $p_0$ 流到数据分布 $p_1$：

$$dx_t = v_\theta(x_t, t) dt$$

训练目标：

$$\mathcal{L} = \mathbb{E}_{t, x_0, x_1} \|v_\theta(x_t, t) - (x_1 - x_0)\|^2$$

其中 $x_t = (1-t) x_0 + t x_1$（线性插值）。

### 3.3 π₀ 具体

- $x_0$：噪声动作
- $x_1$：真实动作
- $v_\theta$：用 VLM + 扩散头
- **1-10 步推理**（vs diffusion 50+）

## 四、跨 Embodiment 的数学

### 4.1 Open-X-Embodiment

- 22 机构 / 60+ 数据集
- 统一动作空间（按 embodiment 标记）
- **condition on embodiment**

### 4.2 通用 policy

$$a = f_\theta(I, l, e)$$

其中 $e$ 是 embodiment ID。

## 五、Sim2Real 的数学

### 5.1 域随机化

仿真参数随机化（摩擦 / 重力 / 光照）：

$$\xi \sim P(\xi), \quad \text{训练于 } s_{t+1} = f(s_t, a_t; \xi)$$

→ 学到 robust policy。

### 5.2 域适应

学 invariant 表示（真实 ↔ 仿真）。

## 六、博士级练习

1. 实现 Flow Matching（PyTorch 50 行）
2. 训练简单 VLA（OpenVLA）
3. 分析 Sim2Real gap

## 关键引用

- Brohan 2023 RT-2
- Black 2024 π₀
- Kim 2024 OpenVLA
- Lipman 2023 Flow Matching
