# I · 评估（1 篇）

> 怎么知道模型"好不好"？——CS336 L12（Evaluation）的引用。
> Percy Liang 是 HELM（Holistic Evaluation of Language Models）作者，评估是他的一亩三分地。

---

## I1. Hendrycks et al. – MMLU / Measuring Massive Multitask Language Understanding (2021) ⭐⭐⭐

- **链接**：[arxiv.org/abs/2009.03300](https://arxiv.org/pdf/2009.03300.pdf) · Berkeley

**核心问题**：之前的基准（GLUE/SuperGLUE）只测窄任务且已饱和。需要一个**广覆盖**的基准衡量模型的"世界知识"。

**方法**：**57 个学科**的四选一选择题（~1.4 万道测试题），覆盖 STEM（数学/物理/计算机）、人文（历史/哲学/法律）、社会科学（经济/心理/地理）等，难度从高中到专家级。题型示例——大学物理、MBA 会计考试、临床医学执照题。

**关键结果**（2020 年时）：绝大多数模型**接近随机水平（25%）**；GPT-3 175B few-shot 也只有 ~44%——揭示当时 LLM 的知识广度严重不足。

**💡 工程经验**：
1. **MMLU 成为事实上的"知识广度"标准**——2021-2025 几乎每篇模型报告都报 MMLU。从 GPT-3 的 44% → 2024 模型 85%+ → 2025 reasoning 模型 90%+。
2. **基准会饱和也会"漏题"**——MMLU 的题目多来自网络公开考试题，**数据污染**（benchmark 泄漏进训练数据）是最大威胁。后来出现去污染版（MMLU-Redux）、加难版（MMLU-Pro、GPQA）。
3. **多选题格式的局限**——现实任务多是生成而非选择；多选好会"蒙"。所以现代评估还要配 open-ended generation + LLM-as-judge。
4. CS336 L12 用它讲"静态基准的生命周期"：出生 → 广泛采用 → 污染/饱和 → 被替代。**设计评估和设计模型同等重要**（Percy 的 HELM 哲学：多场景、多指标、透明报告）。

**📍 CS336 角色**：L12 Evaluation。

---

## I 类总结

> 评估是被低估的学科——**没有好评估，scaling law 和对齐都无从验证**。CS336 A3/A4/A5 的 leaderboard 本质上都是"设计一个小型评估体系"。读模型报告时，先看它报了什么 benchmark、怎么防污染，再信分数。
