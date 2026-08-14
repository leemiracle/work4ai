# 00 · AI for Materials 是什么

> **第一性问题**：人类用材料定义时代（**石器 / 青铜 / 铁 / 硅**）。**下一时代的材料**（室温超导、固态电池、可控核聚变容器）会被 AI 发现吗？
>
> **GNoME**（DeepMind 2023）：AI 发现 **220 万新晶体材料**——**800 年传统矿物学的总量**。这是 AI for Materials 的"ImageNet 时刻"。
>
> 配套：[`讲透AIfor各学科/化学`](../化学/) + [`讲透AIfor各学科/物理`](../物理/)（凝聚态）+ [`讲透AI应用全景/01-AI4Science`](../../讲透AI应用全景/01-AI4Science.md)

---

## 一、材料为什么需要 AI

### 1.1 材料空间巨大

- 已知晶体材料：~20,000
- 理论稳定的可能：**数百万**
- **GNoME 预测**：**220 万新稳定**——人类只探索了 **1%**

### 1.2 实验周期长

- 传统：合成 → 测试 → 重复
- **一个新材料从发现到商用：10-20 年**
- 失败率高

### 1.3 应用驱动紧迫

- **气候**：电池 / 光伏 / 氢能
- **计算**：芯片材料 / 量子硬件
- **健康**：生物相容材料
- **国防**：超材料 / 高温合金

---

## 二、AI 在材料的四大应用

### 2.1 材料性质预测

**给定结构 → 预测性质**（形成能 / 带隙 / 弹性 / 导电性）。

**数据集**：
- **Materials Project**（LBNL）：~15 万 DFT 材料
- **OQMD / AFLOW**：相似规模
- **JARVIS**（NIST）

**代表模型**：
- **CGCNN**（2019）：Crystal Graph CNN
- **ALIGNN**（2021）：Atomistic Line Graph Neural Network
- **M3GNet**（2022, Materials Project）：通用势能函数
- **MACE**（2022）：等变消息传递
- **EquiformerV2**（2024 SOTA）

### 2.2 材料生成 / 发现

**给定目标性质 → 生成结构**。

**代表**：
- **GNoME**（DeepMind 2023, *Nature*）：220 万新稳定材料
  - 方法：**结构生成 + DFT 验证 + 主动学习**
  - 380,000+ 进入 Materials Project
- **CrystaLLM**（2024）：LLM 生成晶体结构
- **DiffCSP**（2024）：扩散 + 晶体空间群

### 2.3 分子动力学加速

**经典 MD**：用 DFT 算力——太慢（纳秒级）。
**AI MD**：神经网络势能（NNP），快 1000-10000 倍。

**代表**：
- **NequIP / Allegro / MACE**：等变 NNP
- **ANNI** / **SchNet**：早期
- **应用**：蛋白折叠模拟 / 催化反应 / 固态离子

### 2.4 自主实验室

**A-Lab**（LBNL 2023 *Nature*）：
- 机器人 + AI 自主合成 + 测试
- **17 天发现 41 种新材料**（人可能要数年）
- 与 GNoME 协同：GNoME 预测 → A-Lab 验证

---

## 三、材料专属的方法学

### 3.1 周期性 + 等变性

晶体有**空间群对称性**（230 种）。

**等变网络**：保证旋转 / 平移 / 镜像不变——大幅提升效率。

**演进**：
- **SchNet**（2017）：不变
- **NequIP**（2021）：SE(3) 等变
- **MACE / Equiformer**（2022-2024）：高阶等变 + 高效

### 3.2 DFT 的瓶颈

- DFT 精确但慢（每结构 ~CPU 小时）
- AI 学 DFT——但**误差累积**
- 开放问题：**AI 能替代 DFT 吗**？

### 3.3 主动学习

- 数据少 + 标注贵（DFT）
- **Active Learning**：AI 选最值得算 DFT 的样本
- GNoME 用此方法高效扩展数据库

---

## 四、当前前沿（2024-2026）

### 4.1 GNoME 的后续

- 扩展到 **材料-性能** 全面 mapping
- **Materials Project 融合**——业界标准
- 开源工具：**matbench**（benchmark）

### 4.2 催化剂发现

**Open Catalyst Project**（Meta + CMU）：
- **OC20** 数据集（5 亿+ DFT 计算）
- **OC22**（2022）：扩展到 CO2 还原
- **EquiformerV2-OC**（2024 SOTA）
- 应用：**可再生能源催化**（电解水、CO2 还原）

### 4.3 超导 / 电池 / 光伏

- **超导预测**：2023 LK-99 事件—— AI 跑预测（部分错）
- **固态电池电解质**：AI 设计新候选
- **钙钛矿光伏**：AI 优化效率

### 4.4 材料基础模型

- **MatterGen**（2024）：微软通用材料生成
- **Universal NNP**：跨元素势能函数
- 趋势：**一个模型解多种材料任务**

---

## 五、AI 改变了材料学的什么

### 5.1 发现速度

- 传统：~20 新材料/年/课题组
- AI：**GNoME 220 万 / 1 年**
- **800 年的探索，1 年完成**——类比 AlphaFold 对生物

### 5.2 实验自动化

- **A-Lab** 自主实验室
- 机器人 24/7 实验
- **材料学家从"做实验"变成"设计实验"**

### 5.3 产业加速

- **电池**：从发现到商用 5-10 年（vs 传统 15-20）
- **药物辅料** / **催化剂** / **超材料**

---

## 六、开放问题

1. **AI 发现的材料能合成吗**？预测稳定 ≠ 能合成
2. **DFT 替代**？AI 势能函数能完全替代 DFT 吗？
3. **超导发现的 AI**？室温超导存在吗？AI 能找到吗？
4. **材料基础模型**能统一吗？
5. **AI + 机器人实验室的伦理**？取代材料学家？

---

## 七、一句话总结

> 🎯 **四句话**：
> 1. **GNoME**（2023）发现 **220 万新材料**——800 年传统矿物学的总量。
> 2. **四大应用**：性质预测（CGCNN→Equiformer）/ 生成（GNoME）/ NNP（MACE）/ 自主实验室（A-Lab）。
> 3. **方法学**：周期性 + 等变网络（NequIP/MACE）+ 主动学习。
> 4. **AI 改变材料**：发现速度 × 1000 + 实验自动化 + 产业加速（电池 / 催化 / 超导）。

---

📌 **下一步**

1. **读**：GNoME Nature 2023 + A-Lab Nature 2023 + EquiformerV2。
2. **和 [`讲透AIfor各学科/化学`](../化学/) + [`讲透AIfor各学科/物理`](../物理/) 对照**。
3. **思考开放问题**——AI 能找到室温超导吗？博士论文级。
4. **进入 [01 GNoME 深挖](./)**（待补）。
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
| GNoME（DeepMind 220 万新材料）| Semantic Scholar 取论文 / 阿里云天池 |
| Materials Project（美国数据库）| 可直连（公开）/ 国内镜像天池 |
| OQMD / AFLOW | 可直连 / 中科院物理所数据 |
| A-Lab 自主实验室 | 论文（Semantic Scholar）|

📌 **一句话**：论文→Semantic Scholar/NSTL；代码→Gitee；模型→ModelScope；数据→天池/AI Studio；全程无需翻墙。
