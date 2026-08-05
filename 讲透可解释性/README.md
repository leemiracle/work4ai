# 讲透可解释性（Interpretability）

> 神经网络是**人类造出却最不被理解的工具**——我们能训练它，能调参，但**说不清它内部在算什么**。可解释性（interpretability）就是要打开这个黑箱。
>
> 本系列从"**为什么 AI 是黑箱**"这个第一性问题切入，沿三条研究路径（probing → attribution → mechanistic）钻到底，重点深挖 **mechanistic interpretability**——找神经网络内部的 **circuits**（功能回路），用 sparse autoencoder 把稠密激活分解成可解释特征，最终落到**激活导向（steering）**和**安全应用**。
>
> 2024-2026 是 mechanistic interpretability 的爆发期：Anthropic 的 scaling monosemanticity、OpenAI 的 SAE 研究都让人乐观。但**完全理解大模型还远**——这是 AI for AI 里**最深刻的方向**（[`07-AI for AI`](../讲透AI应用全景/07-AI for AI.md) 第⑥层）。
>
> 配套：[`讲透AI应用全景/07-AI for AI`](../讲透AI应用全景/07-AI for AI.md) 第⑥层（AI 理解 AI）+ [`讲透基础模型`](../讲透基础模型/)（理解模型才能理解它的内部）+ [`讲透科学的现代性/03-AI时代的科学哲学`](../讲透科学的现代性/03-AI时代的科学哲学.md)（"AI 发现的规律算不算理解"）

---

## 为什么单独开

- **安全需求**：理解 AI 才能控制 AI（防 deceptive alignment）
- **工程需求**：知道为什么模型出错，才能修对
- **科学需求**：理解"AI 是怎么思考的"是心智哲学的实验场
- **AI for AI 的核心**：07 的第⑥层，AGI 讨论的关键拼图

---

## 篇目

| # | 标题 | 状态 | 核心 |
|---|------|------|------|
| **00** | [为什么 AI 是黑箱](./00-为什么AI是黑箱.md) | ✅ | 黑箱定义、三条研究路径、为什么 mechanistic 最深 |
| 01 | Probing 与 representation geometry | 🟡 | 探针、几何视角（anisotropy/centering）、representation structure |
| 02 | Attribution 与梯度方法 | 🟡 | Saliency / Integrated Gradients / SHAP 的局限 |
| 03 | Mechanistic interpretability 地基 | 🟡 | circuits 工作五原则、induction heads、automated circuit discovery |
| 04 | Sparse Autoencoder（SAE） | 🟡 | 稠密→稀疏分解、monosemanticity、Anthropic/OpenAI 实证 |
| 05 | Scaling monosemanticity + 激活导向 | 🟡 | 在 Claude/GPT-4 级别模型上找特征、steering vectors |
| 06 | 应用：安全审计、debug 幻觉、检测欺骗 | 🟡 | 实战 + 局限（interpretability illusion）|

### 姊妹方向：AI 驱动的软件可解释性（用 AI 解释软件）

> 与上面 00-06（解释 AI 模型内部）对偶——这里 AI 是**解释工具**，软件是被解释对象。2024-2026 随 LLM 兴起的新赛道。源自 neo-os 立项调研回流（[`neo-os知识桥梁`](../neo-os知识桥梁.md)）。

| # | 标题 | 状态 | 核心 |
|---|------|------|------|
| **S1** | [AI 驱动的软件可解释性](./S1-AI驱动的软件可解释性.md) | ✅ | 四类竞品（代码理解/可观测性/学术RCA/形式化）、解释性幻觉71.2%、三件套开放问题 |

---

## 怎么用

- **想懂"为什么 LLM 不可解释"**：从 00 开始
- **想跟前沿**：直接跳 03→04→05（mechanistic + SAE + scaling）
- **想做安全研究**：06 + [`讲透AI应用全景/07-AI for AI`](../讲透AI应用全景/07-AI for AI.md) 第④⑤层
- **想思考"AI 算不算理解"**：[`讲透科学的现代性/03`](../讲透科学的现代性/03-AI时代的科学哲学.md)

---

## 配套

- 系列：[`讲透AI应用全景/07-AI for AI`](../讲透AI应用全景/07-AI for AI.md) 第⑥层
- 模型基础：[`讲透基础模型`](../讲透基础模型/) + [`讲透Transformer`](../讲透Transformer/)
- 哲学反思：[`讲透科学的现代性/03`](../讲透科学的现代性/03-AI时代的科学哲学.md)
- 信息源：[`前沿与媒体/01-AI顶级信息源`](../前沿与媒体/01-AI顶级信息源实时清单.md) 的 Anthropic blog + Transformer Circuits Thread
