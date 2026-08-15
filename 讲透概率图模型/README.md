---
card_id: PGM-00
title: "讲透概率图模型：VAE/扩散/大模型推理的理论祖父"
universe: 讲透概率图模型
burke:
  scene: "高维概率分布指数级不可表达，但真实变量间有稀疏结构"
  agent: "想读懂 VAE 的 ELBO、扩散的反向链、大模型推理数学根源的研究者"
  agency: "贝叶斯网络 / MRF / 精确推断 / 变分推断 / MCMC / HMM"
  act: "用图结构压缩联合分布，用图读出条件独立，用三大推断家族算后验"
  purpose: "给当代生成模型与大模型推理配上数学 X 光"
  tension: "精确推断可证正确但指数爆炸，近似推断可行但有偏/慢——可算与可证不可兼得"
  arc: [表示(01-02), 精确(04), 近似(03变分/05采样), 时序(06), 几何(A01), 当代形态(A02), 开放(A03)]
status: done
refs:
  - "Pearl, Probabilistic Reasoning in Intelligent Systems, 1988"
  - "Koller & Friedman, Probabilistic Graphical Models, 2009"
  - "Wainwright & Jordan, Graphical Models, Exponential Families, and Variational Inference, 2008"
updated: 2026-08-15
---

# 讲透概率图模型（Probabilistic Graphical Models）

> **博士级地基**——VAE / 扩散 / 大模型推理的**理论祖父**。
>
> 一句话定位：[`讲透生成模型`](../讲透生成模型/) 给"扩散怎么 work"，本系列问"**变分推断从哪来**"。
>
> **博士级标准**：图论 + 概率论 + 优化。Strikingly elegant。
>
> 配套：[`讲透生成模型`](../讲透生成模型/)（直系后代）+ [`讲透因果推断`](../讲透因果推断/)（图上的因果）+ [`讲透信息论`](../讲透信息论/)（ELBO 的信息论根基）

---

## 为什么单独开

- **理论祖父**：VAE 的 ELBO、扩散的 score、Diffusion 的 reverse process——都是概率图模型的概念
- **被深度学习圈遗忘**——但缺它你只能"调 API"
- **博士必修**：Koller-Friedman 教科书是经典

---

## 篇目（基础层 00-06 + advanced 层 A00-A03，全部 ✅ 2026-08-15）

### 基础层

| # | 文件 | 核心 |
|---|------|------|
| **00** | [概率图模型是什么](./00-概率图模型是什么.md) | 三大派：贝叶斯网 / MRF / 因子图；大模型推理对照表 |
| 01 | [贝叶斯网络](./01-贝叶斯网络.md) | DAG / d-分离 / 条件独立；VAE 的直系祖先 |
| 02 | [马尔可夫随机场](./02-马尔可夫随机场.md) | 无向图 / 势函数 / Hammersley-Clifford |
| 03 | [变分推断](./03-变分推断.md) | ELBO / mean-field / VI——近似的第一个家族 |
| 04 | [精确推断](./04-精确推断.md) | 变量消除 / 信念传播 / junction tree；treewidth 指数墙（03 转向近似的理由）|
| 05 | [MCMC](./05-MCMC.md) | Metropolis-Hastings / Gibbs / HMC；采样家族 + 扩散=朗之万亲戚 |
| 06 | [HMM 与动态贝叶斯网](./06-HMM.md) | 前向-后向 / Viterbi / Baum-Welch；被取代史与算法遗产 |

### advanced 层（博士级，[`advanced/`](./advanced/)）

| # | 文件 | 核心 |
|---|------|------|
| A00 | [经典论文清单](./advanced/A00-经典论文清单.md) | Pearl 1988 → Koller-Friedman → Wainwright-Jordan，三条读法路线 |
| A01 | [变分推断的几何](./advanced/A01-变分推断的几何.md) | ELBO=投影 / KL 非对称（M-投影 vs I-投影）/ 自然梯度 / 指数族统一 |
| A02 | [VAE/扩散作为图模型](./advanced/A02-VAE扩散作为图模型.md) | 图结构照旧、因子换网络；三代一统表；PGM 换马甲住在生成模型里 |
| A03 | [开放问题](./advanced/A03-开放问题.md) | LLM 推理=PGM 推理？/ 概率化 LLM / 神经符号 / 世界模型中的 PGM |

### 辅助

| 文件 | 一句话 |
|---|---|
| [00-讲透笔记-算法经验枢纽.md](./00-讲透笔记-算法经验枢纽.md) | 跨单元算法经验索引 |

> **编号说明**：实际学习顺序 01→02→03→04 也通（先尝近似再回头理解精确为何爆炸）；04 亦可在 02 后插入。`00 §大模型对照表` 与 `A03` 互相收口。

---

## 配套

- 后代：[`讲透生成模型`](../讲透生成模型/)
- 因果：[`讲透因果推断`](../讲透因果推断/)（PGM + do-calculus）
- 信息论：[`讲透信息论`](../讲透信息论/)（ELBO 的根基）
- 优化：[`讲透优化理论`](../讲透优化理论/)（变分 = 优化）
- 能力激活：[`激活大语言模型能力-总结.md`](../激活大语言模型能力-总结.md)（CoT=隐变量推理的机制锚点在本库 00）

---

## 更新日志

- **2026-08-15**：基础层补齐 04-精确推断/05-MCMC/06-HMM，advanced 层建成 A00-A03；README 篇目对齐实际编号（原 03/04 顺序声明与文件不符），补 frontmatter，收编枢纽笔记。全系列 11 篇 ✅
