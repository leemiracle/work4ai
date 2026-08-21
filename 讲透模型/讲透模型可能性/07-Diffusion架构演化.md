# 07 — Diffusion 架构演化：U-Net → DiT → Sora

> 01-06 讲的是**语言模型**的架构替代（SSM/Linear Attention/RWKV/混合）。本篇跨到**生成模型**——diffusion 的 backbone 怎么从卷积（U-Net）演化到 Transformer（DiT），最终催生 Sora。这是"Transformer 统一一切"趋势的视觉版。

---

## 1. 灵魂：diffusion 的 backbone 在变

$$
\boxed{\text{U-Net（2020-2022）} \to \text{DiT（2022）} \to \text{Sora（2024）}}
$$

diffusion 模型生成图像/视频，核心是"去噪网络" $\epsilon_\theta(x_t, t)$。这个网络的**架构**经历了从卷积到 Transformer 的迁移——和语言模型从 RNN 到 Transformer 是同一条路。

---

## 2. 第一代：U-Net（DDPM/SD1.x/SD2.x）

### 2.1 U-Net 结构

```
输入图像
  ├─ 下采样（编码器）：卷积 + 下采样，提取多尺度特征
  ├─ 瓶颈层：最深层
  ├─ 上采样（解码器）：卷积 + 上采样，恢复分辨率
  └─ skip connection：编码器每层直连解码器对应层（保留细节）
```

形状像字母 U——编码器和解码器对称，skip connection 是 U 的底部连线。

### 2.2 U-Net 的优势

- **卷积归纳偏置**：局部性 + 平移不变性，适合图像
- **多尺度**：下采样捕捉语义，上采样恢复细节
- **成熟**：医学图像分割几十年验证

### 2.3 U-Net 的局限

- **scaling 不友好**：卷积网络的"放大规律"不如 Transformer 清晰
- **跨模态难**：U-Net 是为图像设计的，做视频/3D 要大改
- **全局注意力弱**：U-Net 里加 attention 是局部（某些层），不是全局

---

## 3. 第二代：DiT（Diffusion Transformer，Peebles 2022）

### 3.1 核心思想

**把 U-Net 换成 Transformer**：图像 patch 化（像 ViT），用纯 Transformer 做 diffusion 的去噪网络。

```
图像 → patch 化（16×16 patch）→ 线性投影成 token → Transformer blocks → 还原 patch
```

### 3.2 DiT 的关键设计

- **Patch 化**：和 ViT 一样，把图像切成 patch 当 token
- **条件注入**：时间步 $t$ 和文本条件通过 **adaLN**（自适应 LayerNorm）注入——不是拼接，而是控制 LayerNorm 的仿射参数
- **-scalable**：DiT-XL/2L、DiT-XL/3B... 靠堆 block 和调 patch 大小扩展

### 3.3 为什么 DiT 赢了 U-Net

**Scaling Law 友好**：Peebles & Xie 证明 DiT 的 FID 随计算量**平滑下降**（power law），而 U-Net 的 scaling 曲线不规则。

> **洞察**：DiT 的胜利不是"Transformer 比卷积强"，而是"**Transformer 的 scaling 更可预测**"——这和 GPT 的成功逻辑完全一样。

---

## 4. 第三代：Sora（OpenAI，2024）

### 4.1 Sora = DiT + 视频 + 时空 patch

Sora 把 DiT 从图像推广到视频：

- **时空 patch（spatiotemporal patch）**：视频切成 3D patch（时间 × 空间），像 ViT 的 2D patch 升级版
- **大规模 DiT**：参数量大（据传数十 B），长视频生成
- **文本条件**：用 DALL-E 级别的文本编码器

### 4.2 Sora 的"涌现"

- **物理一致性**：物体不会凭空消失（虽然不完美）
- **长视频**：生成长达 1 分钟的视频（U-Net 时代难以想象）
- **3D 一致性**：镜头旋转时物体保持形状

### 4.3 Sora 之后

- **Stable Diffusion 3**：也转向 DiT（不再用 U-Net）
- **Movie Gen（Meta）/ Veo（Google）**：都是 DiT 路线
- **U-Net 时代结束**：2024 后新模型几乎都是 DiT

---

## 5. 架构演化的大图

```
语言模型：RNN(2010s) → Transformer(2017) → [SSM/Mamba(2023) 挑战]
生成模型：U-Net(2020) → DiT(2022) → Sora(2024)
                 ↑                    ↑
            卷积归纳偏置          Transformer 统一
```

**共同规律**：
1. 先用领域专用架构（U-Net/RNN）启动
2. Transformer 证明 scaling 优势
3. 转向 Transformer（DiT/GPT）
4. 部分 O(n) 挑战者出现（Mamba 对语言，但 diffusion 还没出现 SSM 替代）

---

## 6. 批判性

- **DiT 不是"无代价"的胜利**：卷积的归纳偏置在**小数据/小模型**上仍有优势——DiT 需要大规模才赢
- **Sora 的"物理"仍是隐式的**：它学的是统计模式，不是真物理引擎——分布外仍崩
- **视频生成的算力门槛**：DiT + 视频 = 巨大算力，只有大厂能玩

> **诚实结论**：DiT 的胜利是 **Transformer scaling 优势**的又一次确认。但"统一架构"的趋势是否到头（像语言模型遇到 O(n²) 瓶颈），仍是开放问题。

---

## 📌 下一步

模型可能性的核心 4 章（01 SSM / 02 Linear Attn / 03 RWKV / 06 混合 / 07 DiT）到此补全。回顾本系列要传达的：**Transformer 不是终点，但替代者（SSM/Linear/RWKV）和混合（Jamba）各有所长，最终可能是"混合 + 场景选型"的格局**。

继续：
- [`../讲透生成模型/`](../讲透生成模型/)：diffusion 的数学（DDPM/DDIM/Karras）
- [`../讲透Transformer/`](../讲透Transformer/)：被挑战的主流
- [16-未来展望](16-未来展望.md)：推理时计算（o1 范式）/ 混合格局 / AGI——本系列的收官章

## ✍️ 练习

1. DiT 用 adaLN 注入条件（时间步/文本）。为什么不用拼接？（提示：拼接增加维度，adaLN 控制归一化参数，更优雅。）
2. Sora 的"时空 patch"和 ViT 的"空间 patch"区别在哪？为什么视频需要时间维度？
3. U-Net 在小数据上比 DiT 强（归纳偏置优势）。这对"只有少量数据的领域"（如医学影像）意味着什么？（提示：别盲目上 DiT，卷积仍有价值。）
