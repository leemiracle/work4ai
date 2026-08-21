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
| **01** | [探针与表征几何](./01-探针与表征几何.md) | ✅ | linear probe、ROME、anisotropy、representation structure |
| **02** | [稀疏自编码器 SAE](./02-稀疏自编码器SAE.md) | ✅ | Anthropic SAE 找 monosemantic features、toy model、superposition |
| **03** | [Circuits 与超级可解释性](./03-Circuits与超级可解释性.md) | ✅ | induction heads、automated circuit discovery、scaling monosemanticity |
| **04** | [Attribution 与梯度方法](./04-Attribution与梯度方法.md) | ✅ | Saliency / Integrated Gradients / SHAP 的局限 |
| **05** | [Scaling monosemanticity + 激活导向](./05-Scaling-Monosemanticity与激活导向.md) | ✅ | 在 Claude/GPT-4 级别模型上找特征、steering vectors |
| **06** | [应用：安全审计、debug 幻觉、检测欺骗](./06-应用安全审计与幻觉debug.md) | ✅ | 实战 + 局限（interpretability illusion）|

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

---

## 🔗 理论锚点（§12-15 横向打通）

> 横向总纲：本单元在 [`激活大语言模型能力-总结.md`](../激活大语言模型能力-总结.md) 中担任**机制显微镜**层——induction head / SAE / attribution graphs 验证各层激活的真实性，feature steering 本身是 L1 白盒激活手段。

> 本系列讲"为什么模型这样做"的工程方法；这门课揭示**AI 自评的数学边界**：
> 枢纽：[`§12-15 整合`](../§12-15%20理论·形式化·安全·可信AI%20整合.md) §21

| 课程 | 产物 | 公理化的内容 |
|---|---|---|
| §12.2 CMU 15-251 GITCS | [`gitcs.py`](../top-cs-projects/cmu-cs-projects/topic12-theory/gitcs.py) | 对角线/自指暗线（Cantor→Gödel→Turing→Lawvere）——任何形式系统不能证明自己的一致性，对应**AI 不能完美解释/评估自己**（constitutional AI / self-rewarding LM 的理论边界）|

---


---

## 🎭 欺骗动力学视角：AI 纪的识谎学

> 承接 [`欺骗动力学-社会进步的隐秘引擎.md`](../欺骗动力学-社会进步的隐秘引擎.md) §5。

### 三问

1. **讲透可解释性 防的是什么欺骗？** → 模型黑箱藏诈（hallucination / deceptive alignment / sycophancy）。
2. **被什么攻破？** → interpretability illusion / SAE 病态 / probing 覆盖度不足。
3. **沉淀进哪条主链？** → AI 安全主链（核心）+ 验证主链（科学方法 AI 版）。

### 一句话

> 可解释性研究的全部动机一句话：我们怀疑模型可能在骗我们。不懂内部，无法区分「真对齐」和「装的对齐」。
