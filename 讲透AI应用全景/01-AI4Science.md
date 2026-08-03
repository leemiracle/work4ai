# 01 · AI4Science — AI 做科学发现

> AI4Science 是 2024-2026 最有突破感的方向。AlphaFold 3 预测所有生命分子结构、GraphCast 的天气预报击败百年数值模型、GNoME 一次发现 800 年都验不完的新材料——**AI 正在把"科学发现"从'天才的灵光一现'变成'算力的工程问题'**。
>
> 本章深入讲四个代表系统（AlphaFold 系列 / GraphCast / GNoME / Aurora），提炼它们共有的方法论，最后给开放问题。本章是本系列最深入的一篇。
>
> 配套：[`讲透公开课/02-P5 David Tong 笔记`](../讲透公开课/02-数理计算机神课清单.md)（统计场论，扩散模型的理论根基）+ [`讲透生成模型/05-Diffusion`](../讲透生成模型/05-Diffusion.md)

---

## 一、范式转移：从"假设驱动"到"数据驱动发现"

### 1.1 传统科学方法 vs AI4Science

**传统科学方法**（伽利略 → 至今）：
```
观察现象 → 提出假设 → 设计实验 → 验证/证伪 → 形成理论
       （依赖科学家的直觉 + 灵感）
```

**AI4Science 方法**：
```
海量数据 → AI 学到规律 → 预测新现象 → 实验验证 → 反馈数据
       （依赖算力 + 数据 + 表征学习）
```

> 🎯 **关键差异**：传统方法受限于"人能想出多少假设"，AI4Science 受限于"有多少数据 + 多少算力"。前者是认知瓶颈，后者是工程瓶颈——**工程瓶颈是可以花钱解决的，认知瓶颈不行**。

### 1.2 AI4Science 的三个成熟条件（为什么是 2020 之后爆发）

1. **数据**：PDB（蛋白结构库）积累 20 万+ 实验结构；ERA5（气象）40 年再分析数据；材料数据库（Materials Project）成规模
2. **算力**：GPU + Transformer 让训练亿万参数模型可行
3. **方法**：Transformer 的表征学习 + 扩散模型 + GNN 的几何归纳偏置——三者在 2017-2022 成熟

三个条件同时成熟，才有 AlphaFold 2（2020）、GraphCast（2023）这类突破。

---

## 二、AlphaFold 系列：蛋白质结构预测的彻底革命

### 2.1 问题为什么难（50 年的"蛋白折叠问题"）

蛋白质是一串氨基酸，但它在 3D 空间会折叠成特定形状，**形状决定功能**。给一串氨基酸序列（1D），预测它的 3D 结构——这个问题困扰生物学 50 年。

- 序列空间：$20^{n}$（n = 氨基酸数，典型蛋白 n=300，空间 = $20^{300}$）
- 结构空间：连续 3D 坐标
- 物理仿真（分子动力学）算不动——一个蛋白要折叠毫秒级，仿真要算几年

### 2.2 AlphaFold 2（2020）—— Evoformer + 结构模块

**架构核心**（DeepMind，2020-11，2021 Nature）：

```
氨基酸序列 + 多序列比对(MSA) + 结构模板
        ↓
   Evoformer（双流：单序列表示 + 配对表示）
        ↓  （48 层，让序列和结构信息互相更新）
   结构模块（Invariant Point Attention, IPA）
        ↓
   3D 坐标（端到端回归）
```

**为什么 AF2 是革命**：
- CASP14（2020 国际结构预测竞赛）准确率从 ~40 GDT 跳到 ~92 GDT——**直接从"勉强能用"到"实验精度"**
- 论文发 Science/Nature 量级的应用：预测了几乎所有已知蛋白（2 亿+）的结构，开源 UniProt 数据库
- 一个蛋白的预测从"几个月湿实验"变成"几分钟计算"

### 2.3 AlphaFold 3（2024）—— 为什么改用扩散模型

**AF2 的局限**：
- 只能预测**单一蛋白质**，不能预测**复合物**（蛋白 + 小分子药物 + DNA/RNA + 离子）
- 但**真实的生命过程是复合物的相互作用**——药物怎么结合靶点蛋白？蛋白怎么结合 DNA？

**AF3 的突破**（DeepMind + Isomorphic Labs，2024-05-08 Nature）：

```
所有生命分子（蛋白 + 小分子 + DNA/RNA + 离子 + 修饰）
        ↓
   Pairformer（AF2 Evoformer 的进化版）
        ↓
   扩散模块（Diffusion Module）  ← 关键改变！
        ↓
   所有原子的 3D 坐标
```

**为什么 AF3 用扩散，不用 AF2 的回归？**

1. **回归只能输出一个确定答案**；扩散能建模**结构的内在柔性**（同一个蛋白不同状态下形状不同）
2. **复合物的对称性**（蛋白有平移/旋转不变性）扩散更好处理
3. **小分子的化学灵活性**——扩散能采样多个候选构象

**性能**：在蛋白-配体相互作用上比 AF2 提升 50%，比传统对接方法（AutoDock Vina）准确 2-3 倍。

**影响**：Isomorphic Labs（DeepMind 子公司）用 AF3 做药物发现，和礼来/诺华合作——**这是 AI 改变制药工业的实质一步**。

> 🎯 **方法论洞察**：AF2 → AF3 的演化，是"**专用回归模型 → 通用生成模型**"的范式转移。这个转移和 ChatGPT（判别 → 生成）、Stable Diffusion（专用 → 通用扩散）同步——**扩散模型正在统一所有"预测结构"类问题**。

### 2.4 AlphaFold Server —— 民主化的关键

AF3 的模型权重没完全开源（只开源了部分），但 DeepMind 提供 **AlphaFold Server**（af.alphafold.com）——生物学家免费在线提交复合物，拿回结构。**这让百万非 AI 背景的生物学家能用上最前沿 AI**——这是 AI4Science 的产品形态范本。

---

## 三、GraphCast（2023）：天气预报的百年革命

### 3.1 传统数值天气预报有多贵

天气预报过去 100 年靠**数值天气预报**（NWP）：把大气方程（流体力学 + 热力学）离散化求解。全球模型（如 ECMWF 的 IFS）：
- 网格分辨率 ~9km，每 6 小时跑一次
- 需要超级计算机 + 数千核 + 大量物理参数化
- 一次 10 天预报要算几十分钟到几小时

### 3.2 GraphCast 怎么做（DeepMind，2023-11 Science）

**核心**：用 GNN（图神经网络）直接学"过去大气状态 → 未来大气状态"的映射。

```
ERA5 数据（40 年全球气象再分析，0.25° 网格）
        ↓ 训练
   GraphCast（编码器-处理器-解码器 GNN）
        ↓
   输入：当前 + 6 小时前的大气状态（~10^5 网格点 × 多变量）
   输出：6 小时后的大气状态
        ↓ 自回归递推
   10 天预报（40 步）
```

**为什么用 GNN 不用 Transformer**：
- 地球是球面，GNN 的图结构天然适配（用 icosahedron 网格）
- 局部性：天气系统的相互作用是局部的（邻接网格），GNN 的消息传递正好
- 内存效率：比全局 attention 省显存

**结果**：
- 10 天预报，**90% 的预测准确率超 ECMWF IFS**（百年黄金标准）
- 推理速度快 1000 倍（单台 TPU 几十秒 vs 超算几十分钟）
- 还能预测**极端天气的轨迹**（台风路径），这是 NWP 的传统弱项

### 3.3 Aurora（2024）：气象 foundation model

GraphCast 是"专用模型"（一个变量/一个分辨率）。微软研究院的 **Aurora**（2024-05）更进一步：用 foundation model 范式，**一个模型**做大气、海洋、空气污染三个领域。

**意义**：从"每个科学问题训一个模型"到"一个气象 foundation model 适配所有"——和 LLM 的 foundation model 路径一致。

---

## 四、GNoME（2023）：材料发现的炼金术

### 4.1 为什么材料发现难

新材料（电池、半导体、超导、催化剂）是工业的命脉，但发现一个新材料平均要 **10-20 年 + 几十亿美元**——靠"试错"。

### 4.2 GNoME 做了什么（DeepMind，2023-11 Nature）

**GNoME**（Graph Networks for Materials Exploration）：
- 用 GNN 预测"无机晶体的稳定性"（一个化学式能不能形成稳定晶体）
- 在 Materials Project 数据上训练，然后用**主动学习**（active learning）：
  1. 模型预测一批候选
  2. 用 DFT（密度泛函理论，物理仿真）验证
  3. 把验证结果加回训练集
  4. 迭代

**结果**：发现 **220 万种新晶体**，其中 **38 万种是稳定的**（热力学上能存在）——**相当于人类过去几千年发现的所有材料的 8 倍**。

**影响**：其中包含 528 个潜在锂离子电池材料、潜在的超导候选。伯克利实验室用 A-Lab（自动化实验室）合成了其中 41 个——**AI 预测 + 机器人合成**的闭环，是新范式。

> 🎯 **方法论**：GNoME 展示了 AI4Science 的关键模式——**AI 做大规模筛选 + 物理仿真（DFT）做验证 + 自动化实验做闭环**。三者结合，把"试错成本"压到原来的千分之一。

---

## 五、AI4Science 的方法论共性

把四个系统放一起看，能提炼出**所有 AI4Science 系统共有的方法论**：

| 共性 | 体现 |
|------|------|
| **物理归纳偏置** | AlphaFold 的 IPA（旋转不变）、GraphCast 的球面 GNN、GNoME 的图结构——**领域知识编码进架构** |
| **生成模型范式** | AF3 扩散、AlphaProeo 扩散——从"预测一个答案"到"采样分布" |
| **主动学习闭环** | GNoME 的"预测→DFT 验证→迭代"，AlphaFold 的实验数据反馈 |
| **规模化的对称性建模** | 等变神经网络（E(n)-equivariant）、球面谐波——把物理守恒定律编码进网络 |
| **foundation model 化** | Aurora（气象）、MatterGen（材料）——从专用模型走向通用 foundation |

> 🔑 **一句话**：AI4Science = **物理归纳偏置（领域知识）+ 生成模型（采样能力）+ 主动学习（数据飞轮）**。三者缺一不可。

---

## 六、开放问题 + 顶会 workshop

### 6.1 开放问题

1. **可解释性**：AlphaFold 给出结构，但**为什么**这样折叠？AI 学到的"规律"人类理解不了
2. **OOD 推广**：训练集没覆盖的蛋白/材料（如膜蛋白、极端条件），AI 预测可靠吗？
3. **物理一致性**：AI 预测的结构是否满足能量最低、对称性约束？AF3 有时不满足
4. **闭环自动化**：从 AI 预测到机器人合成/实验验证的闭环（GNoME + A-Lab 模式）还在早期
5. **科学发现的"原创性"**：AI 能做"预测"，但能做"提出新概念/新理论"吗？（OpenAI o1 的 CoT 给了一线希望，但还很远）

### 6.2 顶会 workshop（每年关注）

- **NeurIPS AI for Science Workshop**（每年 12 月）——最大最全
- **ICML AI for Science**（每年 7 月）
- **ICLR AI4Science**（每年 5 月）
- **ML4PS**（Machine Learning for the Physical Sciences，NeurIPS 配套）
- **物理领域**：PIRSA（Perimeter）近年大量 AI4Physics 内容

### 6.3 顶级 Lab（追踪前沿）

- **DeepMind Science**（deepmind.google/discover/blog）——AlphaFold/GraphCast/GNoME 都出自这里
- **Microsoft Research AI4Science**（research.microsoft.com/ai4science）
- **Caltech AI4Science** / **MIT CSAIL** / **Stanford AI Lab**
- **国内**：北大 AI4Science（BISS）、上交 AI4Science、清华深智院、深势科技（DP Technology）

---

## 七、一句话总结 + 配套

> 🎯 **三句话**：
> 1. AI4Science 是范式转移——从"假设驱动"到"数据驱动发现"，把认知瓶颈换成工程瓶颈。
> 2. 四大代表：AlphaFold 3（扩散预测复合物）、GraphCast（GNN 天气超 NWP）、GNoME（材料发现 ×800 年）、Aurora（气象 foundation model）。
> 3. 方法论共性：**物理归纳偏置 + 生成模型 + 主动学习闭环**——三者缺一不可。

**配套**：
- 方法论根基：[`讲透公开课/02-P5 David Tong`](../讲透公开课/02-数理计算机神课清单.md)（统计场论）+ [`讲透生成模型/05-Diffusion`](../讲透生成模型/05-Diffusion.md)
- 前沿追踪：DeepMind discoveries blog + NeurIPS AI4Science workshop + PIRSA AI4Physics

---

📌 **下一步**

1. **进入 [02 AI4Math](./02-AI4Math.md)**：AlphaProof 用 Lean + RL 在 IMO 拿银牌——AI4Math 方法论更深刻。
2. **想做 AI4Science 研究**：从 NeurIPS AI4Science Workshop 的 accepted papers 倒着读。
3. **想深入某个系统**：AlphaFold 3 论文（Nature 2024-05）+ DeepMind blog 是起点。
