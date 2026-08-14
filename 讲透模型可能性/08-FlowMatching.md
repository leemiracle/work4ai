# 08 — Flow Matching / Rectified Flow：比 Diffusion 更直的路

> 07 讲 DiT（diffusion 架构 Transformer 化）。本篇讲 **Flow Matching**（2022-2023）——diffusion 的"下一代"：它让生成路径从"弯弯绕"变"笔直"，训练更稳、采样更快。Stable Diffusion 3 转向了它。

---

## 1. 灵魂：直线最短

$$
\boxed{\text{Flow Matching} : \text{学一个向量场 } v_\theta(x_t, t) \text{，把噪声直线推到数据}}
$$

- Diffusion：前向加噪（随机游走），反向去噪（曲线路径）
- **Flow Matching**：直接学"噪声→数据"的**直线速度场**

---

## 2. Diffusion 的"弯路"问题

标准 diffusion（DDPM）的反向过程是一条**曲线路径**——因为前向加噪用的是随机微分方程（SDE），反向去噪要沿 SDE 的逆时间走，路径弯弯绕绕。

后果：
- 采样需要很多步（DDPM 1000 步，DDIM 20-50 步）
- 每步要跑一次神经网络，慢

---

## 3. Rectified Flow：把弯路拉直

Liu et al. 2022（Rectified Flow）和 Lipman et al. 2023（Flow Matching）的核心洞察：

**两个分布之间，最短的传输是直线**。

$$
x_t = (1-t) \cdot x_{\text{noise}} + t \cdot x_{\text{data}}, \quad t \in [0, 1]
$$

- $t=0$：纯噪声
- $t=1$：数据
- 中间：噪声和数据的**线性插值**

学的向量场：$v_\theta = \frac{d x_t}{d t} = x_{\text{data}} - x_{\text{noise}}$（指向数据的常数速度）。

### 3.1 为什么更稳

- 直线路径 → 数值积分误差小 → 少步数就够（5-10 步 vs DDIM 20-50 步）
- 没有 SDE 的随机性 → 训练方差小

### 3.2 "Rectified" 的含义

原始噪声-数据对连成的是曲线（因为噪声和数据分布形状不规则）。Rectified Flow 做**一步"拉直"**：先训一个 flow，再用它重新配对（让传输更直），迭代几次路径越来越直。

---

## 4. Stable Diffusion 3 转向 Rectified Flow

SD3（2024）的核心变化之一：从 DDPM/DDIM 转向 **Rectified Flow** + DiT 架构。

收益：
- 更少采样步数（质量同等）
- 训练更稳定
- 文本理解更强（配合新文本编码器）

---

## 5. Diffusion vs Flow Matching 的统一

实际上，Flow Matching 是**扩散的推广**：

| | Diffusion（DDPM）| Flow Matching |
|---|---|---|
| 前向 | SDE（随机）| ODE（确定，直线）|
| 路径 | 弯曲 | 笔直 |
| 采样步数 | 多（20-1000）| 少（5-20）|
| 训练目标 | 预测噪声 $\epsilon$ | 预测速度场 $v$ |

**Score-based / SDE / Flow Matching 都是"连续时间生成模型"的不同视角**（讲透生成模型 06 章的统一视角）。

---

## 6. 批判性

- **Flow Matching 不是"全新"**：它是 Schrödinger Bridge / 连续 normalizing flow 的特例
- **少步采样的代价**：5 步采样的质量仍不如 50 步——"直"不等于"完美"
- **被 SD3 带火，但理论仍发展中**：多模态/视频的 flow matching 还在探索

> **诚实结论**：Flow Matching 是 diffusion 的"改进版"——同样的思想（学噪声→数据的传输），但用直线替代曲线，工程上更快更稳。它可能成为下一代生成模型的标配。

---

## 📌 下一步

[09-能量模型与Score](09-能量模型与Score.md)——回到 diffusion 的理论源头：能量模型和 score matching，看它们怎么统一。

## ✍️ 练习

1. Rectified Flow 的 $x_t = (1-t) \cdot \text{noise} + t \cdot \text{data}$ 是直线。DDPM 的 $x_t$ 是曲线吗？为什么？
2. Flow Matching 采样 5 步 vs DDIM 50 步，质量差多少？为什么"直线路径"能少步？（提示：直线积分误差小。）
