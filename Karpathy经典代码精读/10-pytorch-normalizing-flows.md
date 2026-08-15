# 10 · pytorch-normalizing-flows — 644 行讲透 Normalizing Flows

> **Andrej Karpathy · pytorch-normalizing-flows**（917★）。Normalizing Flows（NF）教学实现——`flows.py` 294 行 + `spline_flows.py` 253 + `made.py` 97。覆盖 NICE / RealNVP / MAF / IAF / Glow 全家族。**精确密度估计**的生成模型，和 [VQ-VAE](./05-deep-vector-quantization-VQVAE.md) 同属生成模型但思路完全不同。
>
> 源码：``repos/pytorch-normalizing-flows/nflib/flows.py`` ｜ 论文：NICE/RealNVP/MAF/Glow（文件头 L1-34 列全谱系）

---

## 0. NF 在生成模型谱系的定位

| 生成模型 | 能算密度 log p(x)? | 架构自由度 | 训练 |
|---|:---:|---|---|
| **GAN** | ❌（对抗，无显式密度）| 高 | 不稳定 |
| **VAE** | ⚠️（只有 ELBO 下界）| 高 | 稳定但有 gap |
| **NF** | ✅ **精确** | **受限**（必须可逆）| 稳定最大似然 |
| **Diffusion** | ✅（间接）| 高 | 慢 |

> 🎯 **NF 的独特价值**：唯一能**精确算 log p(x)** 的生成模型。这让它在密度估计、异常检测、似然比较等任务上不可替代。代价是架构受限——变换必须可逆 + Jacobian 行列式好算。

---

## Step 1 · 改变变量公式（NF 的核心数学）

NF 的根基是概率论的**改变变量公式**：

$$\boxed{\;\text{若 } u \sim \mathcal{N}(0,I),\ x = f(u),\ \text{则}\quad \log p(x) = \log \mathcal{N}(f^{-1}(x); 0, I) \;-\; \log\left|\det \frac{df}{du}\right|\;}$$

- 左项 $\log \mathcal{N}(f^{-1}(x))$：把 x 反变换回 u，算标准正态密度
- 右项 $\log|\det df/du|$：**Jacobian 行列式校正**（因为变换会拉伸/压缩概率密度）

**训练目标**：最大化 $\log p(x)$（最大似然）。这要求：
1. $f$ **可逆**（能算 $f^{-1}$）
2. **Jacobian 行列式好算**（否则 $O(D^3)$ 算行列式，高维爆炸）

**整个 NF 领域就是设计"既可逆又 Jacobian 好算"的变换**。

---

## Step 2 · AffineConstantFlow（L43-65）—— 最简 flow

```python
class AffineConstantFlow:
    def __init__(self, dim, scale=True, shift=True):
        self.s = nn.Parameter(torch.randn(1, dim))   # 缩放
        self.t = nn.Parameter(torch.randn(1, dim))   # 平移
    def forward(self, x):
        z = x * torch.exp(s) + t                      # 正变换
        log_det = torch.sum(s, dim=1)                 # Jacobian 行列式
        return z, log_det
    def backward(self, z):
        x = (z - t) * torch.exp(-s)                   # 逆变换
        return x, -log_det
```

**逐维度仿射变换**：z_i = x_i · exp(s_i) + t_i。

- **可逆**：x_i = (z_i - t_i) · exp(-s_i)
- **Jacobian**：dz_i/dx_i = exp(s_i)，对角矩阵 → 行列式 = prod(exp(s_i)) = exp(sum(s_i)) → **log_det = sum(s)**

bash 验证：可逆误差 1.19e-07 ✓，log_det = sum(s) = -0.18。

> 这是 NICE/RealNVP 的"缩放层"特殊形式。s/t 是**常数**（不依赖 x）——表达能力弱，但作为 flow 的基础组件。

---

## Step 3 · AffineHalfFlow / RealNVP（L88-119）—— 分半耦合 + 三角 Jacobian

RealNVP（Dinh 2016）的核心创新——**仿射耦合层**：

```python
class AffineHalfFlow:
    def forward(self, x):
        x0, x1 = x[:, ::2], x[:, 1::2]     # 维度分两半
        if parity: x0, x1 = x1, x0         # 奇偶翻转
        s = self.s_cond(x0)                # s 是 x0 的函数
        t = self.t_cond(x0)                # t 是 x0 的函数
        z0 = x0                            # z0 直接拷贝（不变）
        z1 = torch.exp(s) * x1 + t         # z1 仿射变换
        log_det = torch.sum(s, dim=1)
        return z, log_det
```

**精妙之处**：z1 只依赖 x0（不依赖 x1），这让 Jacobian 是**三角矩阵**：

$$\frac{dz}{dx} = \begin{pmatrix} I & 0 \\ * & \text{diag}(\exp(s)) \end{pmatrix}$$

**三角矩阵的行列式 = 对角元素之积** → 不用 $O(D^3)$ 算行列式，$O(D)$ 就够：

$$\det\frac{dz}{dx} = \prod_i \exp(s_i) = \exp(\text{sum}(s)) \implies \log|\det| = \text{sum}(s)$$

> 🤯 **这是 NF 工程的核心突破**：通过"分半 + 一半不变"的耦合设计，把"算行列式"从 $O(D^3)$ 降到 $O(D)$，让高维 flow 可行。**多个耦合层堆叠 + parity 翻转**，让两半轮流被变换，最终整个空间都得到表达。

bash 验证：分半耦合可逆误差 1.19e-07 ✓，log_det = sum(s) = -0.46。

---

## Step 4 · MAF / IAF：用 MADE 当条件器

`s/t` 是 x0 的函数——用什么网络算？**MAF（Masked Autoregressive Flow）用 [MADE](./03-pytorch-made-掩码自编码器.md)**：

- MADE 输入 x，输出每个维度的 (s_i, t_i)，且保证 s_i/t_i 只依赖 x_<i（自回归性）
- 这样 z_i = exp(s_i(x_<i)) * x_i + t_i(x_<i) —— **每维仿射变换的条件是该维之前的所有维度**

**MAF vs IAF 的方向区别**：
- **MAF**（密度估计快）：f 是自回归的，算 log p(x) 一次前向（密度估计友好）；但采样要 D 次前向
- **IAF**（采样快）：f⁻¹ 是自回归的，采样一次前向；但算 log p(x) 要 D 次

> 📌 **MADE 回顾**（[03 精读](./03-pytorch-made-掩码自编码器.md)）：用 mask 让 output k 只依赖 input <k。MAF 复用 MADE 作为 flow 的条件器——**讲透 MADE 就懂了 MAF 的一半**。

---

## Step 5 · NF 家族谱系（flows.py 文件头 L1-34）

```
NICE (2014)      ── 只有 shift (无 scale)，AffineHalfFlow 的特例
   │
RealNVP (2016)   ── 加了 scale，affine coupling (本精读核心)
   │
Glow (2018)      ── 用 invertible 1×1 conv 替代固定分半
   │
MAF (2017)       ── 用 MADE 当条件器，自回归 flow
IAF (2016)       ── MAF 的逆方向（采样快）
```

**所有家族都遵循同一个框架**：可逆变换 + 三角/可算 Jacobian + 堆叠多层。差异在"怎么分半/怎么参数化 s,t"。

---

## Step 6 · bash 跑通验证

```bash
python3 /tmp/opencode/nf_verify.py
```

```
① AffineConstantFlow: z = x*exp(s)+t
  反向还原误差 = 1.19e-07 ✓可逆
  log|det dz/dx| = sum(s) = -0.1814

② AffineHalfFlow (RealNVP): 分半耦合
  Jacobian 是【三角】→ det = prod(exp(s)) → log_det = sum(s) = -0.4600
  反向误差 = 1.19e-07 ✓

③ 改变变量公式
  log p(x) = log N(u) - log|det| = -2.0079 - 0.2000 = -2.2079

④ NF vs VAE vs GAN
  NF: 可逆 + 精确 log p(x), 架构受限
  VAE: 不可逆 + ELBO 下界, 架构自由但有 gap
  GAN: 对抗, 锐利样本但无显式密度
```

**三个铁证**：
1. **可逆性精确**：forward→backward 还原误差 < 1e-7（机器精度）
2. **三角 Jacobian 的威力**：log_det = sum(s)，O(D) 不用 O(D³)
3. **改变变量公式数值正确**：log p(x) = log N(u) - log|det|

---

## 三个关键洞察

### 洞察 1 · 三角 Jacobian 是 NF 工程的命门

高维空间算一般矩阵的行列式是 $O(D^3)$，不可行。RealNVP 的"分半 + 一半不变"让 Jacobian 强制三角，行列式变 $O(D)$。**这个"用结构换计算"的思想贯穿整个 NF 家族**（MADE 的 mask、Glow 的 1×1 conv 都是为了让 Jacobian 好算）。

### 洞察 2 · NF = 精确密度，代价是架构受限

VAE 架构自由但只能给 ELBO 下界；NF 能给精确 log p(x)，但每层必须可逆。**这是"表达力 vs 可处理性"的经典权衡**。需要精确似然的场景（异常检测、模型比较）选 NF；需要强大编码器的场景选 VAE。

### 洞察 3 · MADE 是 NF 和自回归 LM 的桥梁

MAF 用 MADE 当条件器，而 MADE 的 mask 和 [GPT causal attention](./06-minGPT-minimal-GPT.md) 同源（都是"只看过去"）。**所以 NF（连续可逆）和自回归 LM（离散因果）共享同一个"因果约束"思想**，只是用不同方式实现（mask 权重 vs attention 掩码 vs flow 的分半）。

---

## 与 work4ai 对接

| 本精读讲透的 | work4ai 深度版 |
|---|---|
| NF 改变变量公式 / 可逆变换 | [`讲透生成模型`](../讲透生成模型/)（Flow 家族）|
| RealNVP 三角 Jacobian | [`讲透生成模型`](../讲透生成模型/)（耦合层）|
| MADE 当条件器 | [03-pytorch-made 精读](./03-pytorch-made-掩码自编码器.md) |
| NF vs VAE vs GAN vs Diffusion | [`讲透生成模型`](../讲透生成模型/)（生成模型全谱）|

**阅读路径**：[VQ-VAE 精读](./05-deep-vector-quantization-VQVAE.md)（离散生成）+ 本篇（精确密度）+ [讲透生成模型]（VAE/GAN/Diffusion 全谱）= 完整生成模型图景。

---

## 📌 下一步

- **剩余大件**：`11-llama2.c`（2632 行 C 推理）+ `12-llm.c`（1904 行 CUDA 训练）+ notebook 集合并。这两个是 Karpathy 系列最难的，建议各拆段精读。
- **动手**：`python -m nflib.flows` 在 2D moons/circles 数据上训 flow，可视化变换过程（仓库有 demo）。
- **延伸**：读 `spline_flows.py`（Cubic Spline Flow），看连续流（neural ODE 风）怎么用 spline 做可逆变换。

## ✍️ 练习

1. **（验证可逆）** 把 AffineConstantFlow 堆 5 层（不同 s/t），验证 forward 5 次 + backward 5 次还原误差仍 < 1e-6。
2. **（手算 Jacobian）** 对 AffineHalfFlow（D=4, parity=0），手写 4×4 Jacobian 矩阵，确认是下三角，行列式 = exp(s0)*exp(s1)。
3. **（思考）** RealNVP 每层只变换一半维度。堆 K 层后，是否所有维度都被变换过？parity 翻转起什么作用？
4. **（开放）** NF 能精确算 log p(x)，那为什么 LLM 不用 NF 做语言模型？（提示：离散 token 不可逆；文本维度高且语义复杂；自回归 LM 已经能算 log p。）

---

> **源码**：``repos/pytorch-normalizing-flows/nflib/flows.py``（294 行）｜ ``spline_flows.py``（253 行）｜ ``made.py``（97 行，复用 pytorch-made）
