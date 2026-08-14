# 00 · AI for Chemistry 是什么

> **第一性问题**：化学本质上是**分子的科学**——但分子空间是 $10^{60}$ 量级（远超宇宙原子）。**人类探索过的 < $10^{10}$**——99.99...% 是未知。
>
> AI 能让化学家**在这个不可能大的空间里搜索**——分子设计、反应预测、合成规划、催化剂发现。AlphaFold 解的是蛋白质结构，但化学是**整个分子宇宙**。
>
> 配套：[`讲透AI应用全景/01-AI4Science`](../../讲透AI应用全景/01-AI4Science.md) + [`讲透生成模型`](../../讲透生成模型/)（扩散用于分子）

---

## 一、化学为什么需要 AI

### 1.1 分子空间太大

```
可能的小分子（< 500 Da）：~10^60
已知 CAS 注册：              ~10^8
人类合成过：                  ~10^7
```

**搜索空间比宇宙原子数大 ~40 个数量级**——经典方法（一一尝试）不可能。

### 1.2 反应空间组合爆炸

- 一个分子有 10+ 反应位点
- 多步合成：每步选 10 个反应 → 5 步 = $10^5$ 路径
- **逆合成规划**（retrosynthesis）= 反应树搜索

### 1.3 实验成本

- 一个新药研发：**$2B + 10-15 年**
- 失败率：~90%
- 化学合成 + 生物测试 + 临床试验

**AI 解药**：**虚拟筛选 + 生成**——把实验量降到 1%。

---

## 二、AI 在化学的五大应用

### 2.1 分子表示学习

**核心问题**：怎么把分子变成机器能学的表示？

**三类方法**：

| 表示 | 描述 | 代表 |
|---|---|---|
| **1D SMILES** | 字符串（如 `CC(=O)O` 乙酸）| RNN/Transformer |
| **2D Graph** | 原子=节点，键=边 | GNN（MPNN, SchNet）|
| **3D 结构** | xyz 坐标 | Equiformer / NequIP（等变网络）|

**2024 SOTA**：**EquiformerV2**——3D 等变 Transformer。

### 2.2 分子性质预测（QSAR）

**目标**：给定分子，预测性质（结合亲和力 / 毒性 / 溶解度）。

- **毒性**：Tox21 / ClinTox benchmark
- **药物性**：ADMET（吸收/分布/代谢/排泄/毒性）
- **催化活性**：Open Catalyst Project

**代表**：
- **SchNet / DimeNet / PaiNN / Equiformer**（GNN 演进）
- **AlphaFold 3**（2024）扩展到小分子相互作用

### 2.3 分子生成（inverse design）

**目标**：给定想要的性质，**生成新分子**。

**方法**：
- **VAE**：Junction-Tree VAE（JT-VAE, 2018）
- **GAN**：MolGAN
- **扩散**：**GeoDiff / DiffSBDD**（2022-2024 SOTA）
- **Flow Matching**：2024 新范式

**应用**：
- **药物设计**：口袋定制的分子（structure-based drug design, SBDD）
- **材料设计**：有机发光材料 / 电池电解液

### 2.4 反应预测

**正向**：反应物 → 产物
- **USPTO** 数据集（100 万+ 反应）
- **Molecular Transformer**（Schwaller 2019）—— SOTA

**逆向**：产物 → 反应物（逆合成）
- ** retrosynthesis** 是化学家的核心技能
- **AiZynthFinder**（AstraZeneca）
- **ASKCOS**（MIT）
- 用 **MCTS + 神经网络** 搜索反应树

### 2.5 自动化化学（闭环 AI）

**Coscientist**（CMU 2023 *Nature*）：GPT-4 + 化学 API + 实验机器人——**自主设计 + 执行化学反应**。

**意义**：AI 不只是预测，**直接做实验**——化学研究的范式转变。

---

## 三、化学专属的方法学

### 3.1 等变性（Equivariance）

分子有 **SE(3) 对称性**（旋转 + 平移不变）。

**等变网络**：保证网络输出随输入变换——大幅提升样本效率。

**演进**：
- **Tensor Field Networks**（2017）
- **NequIP**（2021, *Nature Communications*）
- **Allegro**（2023, *Nature Communications*）
- **Equiformer / EquiformerV2**（2023-2024 SOTA）

### 3.2 物理约束

- **能量守恒**：网络输出能量 + 力（梯度）
- **对称性**：置换不变（同种原子可交换）
- **守恒律**：电荷守恒、原子守恒

### 3.3 数据集

| 数据集 | 用途 |
|---|---|
| **QM9** | 13 万小分子，DFT 性质 |
| **Open Catalyst 2020/2022** | 催化反应（千万级）|
| **GEOM / QM7b / QM8** | 3D 构象 |
| **USPTO** | 100 万+ 化学反应 |
| **ChEMBL / PubChem** | 生物活性 |

---

## 四、当前前沿（2024-2026）

### 4.1 AlphaFold 3（2024）

DeepMind 的扩展——从蛋白质到**所有生物分子**：
- 蛋白-蛋白 / 蛋白-核酸 / 蛋白-小分子
- 精度超 AlphaFold-Multimer
- **对药物发现是地震级**

### 4.2 Boltzmann Generators（扩散用于分子）

- **Noé 团队**（Microsoft Research Cambridge）：扩散模型生成符合玻尔兹曼分布的分子构象
- **意义**：物理严格的生成模型

### 4.3 大型化学 LLM

- **ChemCrow**（2024）：LLM + 18 个化学工具
- **Coscientist**：GPT-4 自主做化学实验
- **ChemLLM**（2024）：化学领域专用 LLM

### 4.4 自主实验室

- **A-Lab**（LBNL 2023 *Nature*）：自主合成 + 测试新材料
- 17 天发现 41 种新材料（人可能要数年）

---

## 五、化学的 AI 改变

### 5.1 药物发现加速

- **Insilico Medicine**：AI 设计药物进入临床 II 期（2024）
- **Recursion**：AI 表型筛选
- **Isomorphic Labs**（DeepMind 分拆）：AlphaFold 商业化

### 5.2 绿色化学

- 催化剂设计减少能耗
- 塑料降解酶设计
- 新电池材料

### 5.3 化学教育

- LLM 解化学题
- 自动反应解释
- 学生训练

---

## 六、开放问题

1. **分子空间的真实大小**？AI 能覆盖多少？
2. **反应预测的极限**？复杂多步反应能 100% 预测吗？
3. **AI 设计的药物的安全性**？如何监管？
4. **AI + 自动化的伦理**？AI 能造危险物质（如毒品/武器）怎么办？
5. **AI 发现的新机理**算化学发现吗？

---

## 七、一句话总结

> 🎯 **四句话**：
> 1. 化学是**分子宇宙的科学**（$10^{60}$ 空间），AI 是唯一可行的探索工具。
> 2. **五大应用**：分子表示 / 性质预测 / 生成 / 反应预测 / 自动化实验。
> 3. **方法学核心**：SE(3) 等变性（Equiformer）+ 物理约束 + 大数据集。
> 4. **2024 前沿**：AlphaFold 3 + ChemCrow + Coscientist + 自主实验室——**化学研究的范式转变**。

---

📌 **下一步**

1. **读**：AlphaFold 3 / EquiformerV2 / Coscientist *Nature* 2023。
2. **和 [`讲透生成模型`](../../讲透生成模型/) 对照**：扩散用于分子。
3. **思考开放问题**——AI 能造危险品，化学 AI 的伦理是博士论文级方向。
4. **进入 [01 分子生成深挖](./)**（待补）。
---


---

## 🇨🇳 国内可访问资源映射

> 本领域核心资源多托管在大陆不易访问的平台（Google 系被墙、GitHub/HuggingFace 不稳定、Nature/Science 付费墙）。下表给出**国内可直接访问**的对应入口。

### 通用映射（所有 AI for 学科共享）

| 类型 | 境外 | 国内可访问 |
|---|---|---|
| 论文检索 | Google Scholar | [百度学术](https://xueshu.baidu.com) / [Semantic Scholar](https://semanticscholar.org)（可直连）/ [知网](https://cnki.net) |
| 论文全文 | Nature/Science/arXiv | [NSTL](https://nstl.gov.cn) 免费文献传递 / Semantic Scholar / 中科院文献情报中心 |
| 代码 | GitHub | [Gitee](https://gitee.com) / [ghproxy](https://ghproxy.com) 加速 |
| 模型/权重 | HuggingFace | [ModelScope 魔搭](https://modelscope.cn) / [百度千帆](https://cloud.baidu.com/product/wenxinworkshop) |
| 数据集 | 境外数据托管 | [阿里云天池](https://tianchi.aliyun.com) / [百度 AI Studio](https://aistudio.baidu.com) |
| 算力 | Colab / AWS GPU | [阿里 PAI](https://pai.alibaba.com) / [百度 BCC](https://cloud.baidu.com/product/bcc/gpu.html) / 各地**智算中心** |
| 大模型 API | GPT-4 / Claude | [智谱 GLM](https://zhipuai.cn) / [DeepSeek](https://deepseek.com) / [通义千问](https://tongyi.aliyun.com) / [文心](https://yiyan.baidu.com) |
| 视频/课程 | YouTube / Coursera | [B站](https://bilibili.com) / [学堂在线](https://xuetangx.com) / [中国大学 MOOC](https://icourse163.org) |

### 本学科特有

| 境外资源 | 国内可访问对应 |
|---|---|
| RDKit（开源化学信息学）| 可直连（开源）/ PyPI 清华镜像装 |
| AlphaFold 3 / Coscientist | Semantic Scholar 取论文 / ModelScope 搜 AlphaFold |
| PubChem / ChEMBL（数据库）| 可直连（NIH 公开）/ 阿里云天池化学数据集 |
| ChemDraw（商业）| 国产：**KingDraw**（免费，中文化学绘图）|

📌 **一句话**：论文→Semantic Scholar/NSTL；代码→Gitee；模型→ModelScope；数据→天池/AI Studio；全程无需翻墙。
