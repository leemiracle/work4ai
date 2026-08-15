# 00 · AI for Complex Systems 是什么

> **第一性问题**：复杂系统科学是 **21 世纪的"通用科学"**——从大脑到城市到气候到经济，**涌现 + 非线性 + 网络**。AI 是复杂系统研究的**新引擎**——但 AI 本身也是复杂系统。

## 一、复杂系统的特征

### 1.1 核心概念

- **涌现**（emergence）：整体 > 部分之和
- **非线性**：小输入 → 大输出
- **网络**：节点 + 边的拓扑
- **反馈**：正 / 负反馈循环
- **临界**（criticality）：相变点

### 1.2 经典方法

- **统计力学**（Ising 模型 / 渗流）
- **动力系统**（微分方程 / 混沌）
- **网络科学**（Barabási / Watts-Strogatz）
- **代理模型**（Schelling / Epstein）

### 1.3 AI 的角色

- **处理高维**（复杂系统的诅咒）
- **发现模式**（人眼看不到）
- **预测 + 控制**（部分）

## 二、AI 在复杂系统的应用

### 2.1 网络科学 + GNN

- **图神经网络**（GNN）处理网络数据
- 应用：社交网络 / 生物网络 / 交通

### 2.2 动力系统 + Neural ODE

- **Neural ODE**：连续时间神经网络
- 学复杂动力学
- **Chen 2018 NeurIPS**

### 2.3 多智能体 RL

- agent 相互作用
- 涌现行为
- 详见 [`讲透RL`](../../../讲透RL/)

### 2.4 LLM 多智能体

- SmallVille 等
- 社会涌现
- 详见 [`社会学`](../社会学/)

### 2.5 复杂网络基础模型

- 跨域网络模型
- **早期研究**

## 三、复杂系统的"反 AI"

### 3.1 不可预测性

- **混沌**（蝴蝶效应）
- AI 也不能精确预测长期
- **Lorenz 系统**

### 3.2 涌现的不可还原

- 整体性质不能从部分推出
- AI 学部分 → 学不到整体？
- **强涌现**（不可计算）

### 3.3 复杂适应系统（CAS）

- agent 适应 + 学习
- 系统永远在变
- AI 必须在线学习

## 四、博士级练习

1. 实现简单 Schelling 模型 + AI
2. 用 GNN 分析社交网络
3. 测试 Neural ODE 在 Lorenz

## 关键引用

- Barabási *Network Science*
- Mitchell *Complexity: A Guided Tour*
- Wolfram *A New Kind of Science*
- Noble *The Music of Life*


---

## 领域知识深化：复杂系统核心概念

| 概念 | 含义 | AI 对应 |
|---|---|---|
| **涌现** | 整体>部分之和 | LLM 涌现能力 |
| **自组织** | 局部规则→全局秩序 | 训练=熵减 |
| **相变** | 跨阈值行为突变 | 涌现阈值 |
| **网络拓扑** | 小世界/无标度 | 神经网络结构 |
| **混沌** | 确定性不可预测 | 训练敏感性 |
| **反馈环** | 正反馈→雪崩/负反馈→稳定 | RLHF 闭环 |

**关键人物**：Bertalanffy(1968系统论) / Prigogine(耗散结构) / Holland(CAS) / Barabasi(无标度网络)

**研究方法**：Agent-based modeling(NetLogo) / 网络科学(NetworkX) / 动力系统(分岔图) / 信息论(熵)
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
| NetworkX（GitHub）| Gitee 镜像 / PyPI 清华镜像 |
| Neural ODE / 朱家鹏工作 | Semantic Scholar / Gitee |
| Santa Fe Institute 数据 | 论文 / 中科院系统科学所 |

📌 **一句话**：论文→Semantic Scholar/NSTL；代码→Gitee；模型→ModelScope；数据→天池/AI Studio；全程无需翻墙。
