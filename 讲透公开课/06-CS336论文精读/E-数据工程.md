# E · 数据工程（8 篇）

> **CS336 A4 的核心**——预训练数据怎么来、怎么洗、怎么配。
> 对应讲座：**L13（数据源）、L14（过滤/去重/混合）**｜ 作业：**A4（Common Crawl → 训练数据）**

---

## E1. OpenWebText (2019) ⭐⭐

- **链接**：[skylion007.github.io/OpenWebTextCorpus](https://skylion007.github.io/OpenWebTextCorpus/)

**核心**：GPT-2 的 WebText 数据集（Reddit karma≥3 链接）的**开源复刻**。38GB。

**💡 工程经验**：
1. **社区填坑**——OpenAI 不开源 WebText，社区自己抓。这种"开源复刻闭源数据集"的模式后来反复出现（RedPajama 复刻 LLaMA 数据配方）。
2. CS336 A1 用 OpenWebText sample 做训练数据——它是"够大又够干净"的入门数据集。

---

## E2. The Pile (2020) ⭐⭐⭐

- **链接**：[arxiv.org/abs/2101.00027](https://arxiv.org/pdf/2101.00027.pdf) · EleutherAI

**核心**：**825GB**，**22 个领域子集**——CommonCrawl、PubMed、ArXiv、GitHub、StackExchange、USPTO（专利）、OpenWebText2、Books3 等。

**💡 工程经验**：
1. **"多样性 > 纯量"的开创性理念**——The Pile 证明混合多领域数据能提升泛化。GPT-NeoX-20B、OPT、BLOOM 全用它训练。
2. **Books3 的版权争议**——它包含盗版书，后被法律投诉下架。这是**预训练数据版权问题**的标志性事件，催生了更谨慎的数据合规。
3. **领域配比**是艺术——The Pile 给的经验配比（如 CommonCrawl 占大头、代码占 8%）成为后续配方的参考起点。
4. CS336 L13 把它当"多领域混合"的教科书案例。

**📍 CS336 角色**：L13。

---

## E3. C4 – Colossal Clean Crawled Corpus (in T5) ⭐⭐

- **链接**：T5 论文 §2.2 [arxiv.org/abs/1910.10683](https://arxiv.org/pdf/1910.10683.pdf)

**核心**：750GB，从 Common Crawl 清洗。**过滤 recipe 是核心贡献**：
- 只留英文（langdetect）
- 去掉"脏"行（必须以标点结尾、长度 3+ 句）
- 去 boilerplate（菜单/页脚，用 bert-like 分类器）
- 去重复行

**💡 工程经验**：
1. **CS336 A4 教的就是 C4 式过滤**——学生要实现 `is_english` 等过滤器。
2. **过滤 = 质量**——C4 的过滤规则简单但有效。后来的 FineWeb/DCLM 用更复杂的 classifier（如 fasttext 训练质量分类器）。
3. 过度过滤会丢数据——过滤太狠，剩余量不够训大模型。**召回 vs 精度**的权衡。

---

## E4. MassiveText (in Chinchilla) ⭐

- **链接**：Chinchilla 论文 §3 [arxiv.org/abs/2203.15556](https://arxiv.org/pdf/2203.15556.pdf)

**核心**：DeepMind 的 1.5T tokens 数据集，比 Gopher 的 MassiveWeb 更大更精。**不同子集用于不同训练阶段**（高质量数据放后期）。

**💡 工程经验**：**分阶段喂不同质量数据**——先训海量普通数据建语言能力，后期用高质量数据"抛光"。LLaMA-3、Nemotron 都用这个策略。

---

## E5. Dolma (2024) ⭐⭐

- **链接**：[arxiv.org/abs/2402.00159](https://arxiv.org/abs/2402.00159) · AI2

**核心**：AI2 为 OLMo 模型建的 **3T tokens** 开源数据集。包含 CommonCrawl、The Stack（代码）、Reddit 等。**完全开源**（数据 + 过滤代码 + 训练流程）。

**💡 工程经验**：
1. **OLMo 的"全开源"哲学**——不只开源模型权重，还开源**数据**和**训练日志**。这是对 LLaMA"只开源权重不开源数据"的反叛。
2. Dolma 的过滤 pipeline 是 A4 的工业级范本——classifier 过滤 + 去重 + 去有害内容。

**📍 CS336 角色**：L13/L14 + A4 参考。

---

## E6. DCLM (2024) ⭐⭐

- **链接**：[arxiv.org/abs/2406.11794](https://arxiv.org/abs/2406.11794) · DataComp for Language Models

**核心**：**数据集 benchmark**——把"数据选择"变成可量化比较的竞赛。提供固定模型 + 固定算力，让参与者比拼**数据过滤策略**。

**💡 工程经验**：
1. **数据选择是系统工程**——DCLM 证明：固定模型，光改数据过滤策略就能让 loss 差很多。**数据 > 模型微调**。
2. 最佳策略：fasttext 质量分类器 + MinHash 去重 + 领域配比。
3. CS336 A4 leaderboard 思路与之同源——固定训练，比数据 pipeline。

---

## E7. Nemotron CC (2024) ⭐

- **链接**：[arxiv.org/abs/2412.02595](https://arxiv.org/abs/2412.02595) · NVIDIA

**核心**：NVIDIA 的 Common Crawl 清洗版，强调**分类器驱动的质量过滤**和**去重**。用于 Nemotron 系列训练。

**💡 工程经验**：NVIDIA 的数据 pipeline 极工业级——分类器、去重、有害内容过滤全自动化。代表 2024 数据工程的最高工艺。

---

## E8. RegMix (2025) ⭐⭐⭐

- **链接**：[arxiv.org/abs/2407.01492](https://arxiv.org/abs/2407.01492)

**核心问题**：预训练数据该**怎么配比各领域**（多少网页、多少代码、多少论文、多少书）？传统靠直觉/消融实验，贵且不系统。

**方法**：**用回归模型预测最优配比**。在小模型上试不同配比，记录（配比, loss/下游指标），拟合一个**配比 → 性能**的回归函数（类似 scaling law 但是在数据维度），然后预测大模型的最优配比。

**💡 工程经验**：
1. **把"数据配比"从艺术变科学**——和 scaling law 一样的思路：小实验拟合规律，外推到大规模。
2. 不同下游任务最优配比不同——代码任务要更多代码数据，常识任务要更多网页。**配比是任务相关的**。
3. 这是 CS336 L14（数据混合）的前沿内容。

**📍 CS336 角色**：L14 前沿。

---

## E 类总结：数据工程的进化

```
2019 OpenWebText (Reddit过滤, 朴素)
   ↓
2020 The Pile (22领域混合, 多样性)
   ↓ 系统化
2022 C4/MassiveText (规则过滤 + 分阶段)
   ↓ 开源透明
2024 Dolma/DCLM (分类器过滤 + benchmark)
   ↓ 量化
2025 RegMix (回归预测配比)
```

> **核心经验**：数据是 LLM 的"食物"，**食物质量决定模型上限**。模型架构再好，喂垃圾数据也白搭。这就是为什么 CS336 专门花 L13-14 两讲 + A4 一整个作业讲数据——**数据工程是 LLM 训练里最被低估的环节**。
>
> 现代数据 pipeline 的黄金组合：**质量分类器过滤 + MinHash 去重 + RegMix 配比 + 分阶段喂**。
