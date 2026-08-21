# 讲透可解释性 · 思想史

> **一句话定位**：可解释性五十年——从"机器天然会说人话"（MYCIN），到"给黑箱贴热力图"（LIME/SHAP），到"给神经网络做解剖"（机械可解释性），再到"理解模型是为了控制模型"（对齐工具），每一次范式转移都在回答同一个问题的不同变体：**我们能不能信任一个自己不理解的东西？**

> **方法论声明**：本文是**思想史**（history of ideas），不是年代史。不只问"何时发生"，更问"为什么此时此地发生、为什么被淘汰、为什么复兴"。参考 [`讲透AI历史/00-为什么学AI历史`](../讲透AI历史/00-为什么学AI历史.md) 的五条原则。

---

## 0. 方法论：怎么读这段历史

### 0.1 五十年，四次范式转移

```
1970s   符号主义：解释是"自然的"（规则即推理链）
  ↓ 第一次范式转移
2010s   黑盒 ML + 事后解释：解释是"贴上去的"（LIME/SHAP/attention 可视化）
  ↓ 第二次范式转移
2020    机械可解释性：解释是"解剖出来的"（circuits / Olah）
  ↓ 第三次范式转移
2023    SAE / 超叠加：解释是"分解出来的"（稀疏自编码器找到 monosemantic 特征）
  ↓ 第四次范式转移
2024-   可解释性 = 对齐工具：解释是为了"干预和控制"（steering / safety auditing）
```

### 0.2 驱动每次转移的根本动力

| 转移 | 根本矛盾 | 催化剂 |
|---|---|---|
| 符号→黑盒 | 符号系统的知识瓶颈（无法从数据自动学）| 深度学习 2012 的性能碾压 |
| 事后→机械 | 事后解释不可靠（sanity check 2017）| Olah 的逆向工程愿景 |
| 手工→SAE | superposition 使手工找 circuit 不可扩展 | Anthropic 2023 toy model 理论突破 |
| 理解→对齐 | 单纯"理解"不足以保证安全 | GPT-4 / Claude 级别模型的部署压力 |

### 0.3 一个贯穿全文的反问

> **如果解释只是"听起来合理的故事"，那它和幻觉有什么区别？**

这五十年里，这个追问反复出现。MYCIN 的规则解释很"合理"但系统仍然误诊；saliency map 的热力图很"直观"但和模型实际计算无关；SAE 找到的"特征"很"可读"但可能是 interpretability illusion。**真正的理解标志是可预测、可干预——能关掉一个 circuit 然后精确预测行为变化，才算"找到了"，而不是"讲了个好听的故事"。**

---

## 1. 前夜：符号主义的"自然解释"（1970s-1980s）

### 1.1 MYCIN：解释是免费的

1972-1980 年，斯坦福大学的 Edward Shortliffe 开发了 MYCIN——一个诊断细菌感染并推荐抗生素的专家系统。MYCIN 由约 600 条 IF-THEN 规则构成，例如：

```
RULE 050
IF:  (1) 感染部位是血液, 且
     (2) 感染菌的革兰氏染色是阴性, 且
     (3) 感染菌的形态是杆状, 且
     (4) 患者是宿主 compromised
THEN: 有 0.6 的把握认为感染菌是 Pseudomonas
```

**关键事实**：MYCIN 的推理链**天然就是人类可读的**。当医生问"你为什么推荐庆大霉素？"，系统只需把触发的规则链打印出来——这就是"解释"。

MYCIN 有一个专门的 `WHY` 命令和 `HOW` 命令：
- **WHY**：为什么需要这条信息？→ 回溯到上级规则的前提
- **HOW**：你如何得出这个结论？→ 展开下级规则的推理链

> 🎯 **符号主义的解释哲学**：解释 = 推理过程的外化。系统怎么算的，就怎么解释——**没有黑箱，因为计算过程本身就是符号化的、可读的**。

### 1.2 为什么这种"自然解释"失败了

**根本原因不是解释能力不够，而是符号系统的知识获取瓶颈**：

1. **知识工程师瓶颈**：600 条规则是专家一条一条口述出来的——MYCIN 花了 5 年。覆盖哪怕一个狭窄医学领域都需要数万条规则
2. **脆弱性**：碰到规则库里没覆盖的情况，系统直接崩溃（或给出荒谬建议）
3. **无法从数据学习**：所有知识必须手工编码，无法从病历数据中自动发现模式

> **思想史洞察**：MYCIN 的失败不是"解释"的失败，而是"手工知识工程"的失败。但当深度学习取代符号系统时，**连带把"可解释"也一起扔了**——因为深度学习用分布式表示取代了符号推理，旧的解释方法（打印规则链）瞬间失效。这就是第一次范式转移的代价。

### 1.3 符号主义解释的遗产

MYCIN 的"解释即推理链"思想没有完全消失：

- **决策树**（§2）直接继承了符号主义的可解释性
- **规则提取**（§2.3）试图从神经网络里"重新挖出"符号规则
- **2024-2026 的 chain-of-thought** 让 LLM 自己输出推理过程——某种意义上是符号主义解释的"连接主义复活"

> **反常识**：今天让 GPT-4 输出 chain-of-thought 来"解释"自己，本质上是回到了 MYCIN 的哲学——**让推理过程显式化就是解释**。区别是 MYCIN 的规则是人写的、确定可靠的；GPT-4 的推理是模型生成的、可能是在"编故事"。

---

## 2. 决策树与规则提取：最后的"天然可解释"（1986-2000s）

### 2.1 Quinlan 的 ID3 与 C4.5

1986 年，悉尼大学的 J. Ross Quinlan 发表 ID3 算法，后来发展为 C4.5（1993）。决策树是**唯一同时满足高精度和天然可解释**的经典 ML 模型。

一棵决策树就是一棵嵌套的 IF-THEN 树：

```
                    年龄 > 65?
                   /          \
                 是            否
                 /              \
          血压 > 140?      家族史?
          /        \       /      \
        是         否     是       否
     高风险     中风险  中风险    低风险
```

**为什么决策树"天然可解释"**：每一条从根到叶的路径就是一条人类可读的规则。**推理路径 = 解释**，不需要任何额外的事后工具。

这引出了那个时代的主导哲学：

> **If the model isn't interpretable, it shouldn't be used in high-stakes decisions.**（如果模型不可解释，就不该用于高风险决策。）

这句话在 1990s 是共识。信用评分、医疗诊断的监管要求（如美国 Equal Credit Opportunity Act）强制要求模型可解释，因此决策树和线性回归主导了这些领域几十年。

### 2.2 随机森林的"解释悖论"

2001 年，Leo Breiman 发表随机森林——把决策树从"单棵可解释"变成"百棵投票"。随机森林在精度上碾压单棵决策树，但**失去了路径可读性**。

Breiman 自己提供了两个补偿工具：
- **特征重要性**（feature importance）：哪个特征对预测贡献最大
- **部分依赖图**（partial dependence plot）：改变某个特征，预测怎么变

这两个工具**成为了后世"事后解释"的先驱**——它们不是决策树固有的解释能力，而是从外面"贴上去"的。当深度学习取代随机森林时，这些工具继续适用于新模型。

> **思想史转折点**：随机森林是一个"过渡物种"——精度接近黑盒但保留了部分可解释性。它让社区养成了"事后解释"的习惯，为 LIME/SHAP 的出现铺了路。但同时也**埋下了隐患**：人们开始相信"只要事后贴个特征重要性就够了"，而没有追问"这个解释是否忠实于模型内部"。

### 2.3 规则提取：从神经网络里挖符号

1990s 出现了一个现在几乎被遗忘的研究方向——**规则提取**（rule extraction）。代表工作：Tickle & Andrews（1993）的综述把方法分为两类：

- **教学法**（pedagogical）：把神经网络当黑箱，观察"输入→输出"对，用决策树拟合
- **解剖法**（decompositional）：打开网络，分析每个权重/神经元，逐层翻译成规则

**为什么它失败了**：

1. 提取出的规则要么太简单（丢失模型能力）要么太复杂（比模型本身还难懂）
2. 网络变大后规则数量爆炸——100 个神经元的网络能提取出上万条规则
3. 缺乏理论基础——你不知道提取出的规则是否忠实于模型内部

> **思想史遗产**：规则提取的"解剖法"（decompositional）是**机械可解释性的思想祖先**——都是"打开网络内部看权重"。区别是 1990s 的网络太小、表征太密集、没有理论框架；2020 年的 Olah 有了 attention head、circuits 概念和 superposition 理论，才让"解剖"真正有效。

---

## 3. 第一次范式转移：黑盒 ML 与事后解释（2012-2017）

### 3.1 深度学习的黑箱困境

2012 年 AlexNet 在 ImageNet 上碾压传统方法——精度提升 10 个百分点。但深度神经网络彻底打破了"模型必须可解释"的共识：

- 精度大幅提升，**没有可解释的替代品能达到相同性能**
- 监管要求和高性能之间的张力越来越大
- 神经网络的分布式表示使任何"打开看权重"的尝试都无意义（参见 [00-为什么AI是黑箱](./00-为什么AI是黑箱.md) §1.2）

**社区的反应**：不再要求模型"天然可解释"，转而发展**事后解释方法**——训练完之后，用额外工具来"解释"黑箱模型的决策。

### 3.2 LIME：局部线性近似（2016）

2016 年，华盛顿大学的 Marco Ribeiro、Sameer Singh、Carlos Guestrin 发表 **"Why Should I Trust You?: Explaining the Predictions of Any Classifier"**。

LIME（Local Interpretable Model-agnostic Explanations）的核心思想极其简洁：

1. 取一个待解释的输入 $x$
2. 在 $x$ 附近**采样大量扰动样本**
3. 用原模型 $f$ 对这些样本打标签
4. 在局部拟合一个**简单的可解释模型** $g$（通常是线性回归）
5. 用 $g$ 的系数作为"解释"

```
全局：f 是一个复杂的非线性黑箱
局部：在 x 附近，f ≈ 一个线性函数 g
解释：g 的系数告诉你"在这个预测里，哪些特征重要"
```

**为什么 LIME 火了**：它是 **model-agnostic** 的——不关心你用的是什么模型（CNN / RNN / 树集成），都能解释。加上 Ribeiro 团队做了一个好用的可视化界面，立刻被工业界广泛采用。

**为什么 LIME 有根本性缺陷**（事后看）：
- "在 $x$ 附近"的定义依赖于扰动方式——换一种扰动，解释就变了
- 局部线性假设在非线性边界附近严重失真
- **它解释的是"扰动空间里的局部行为"，不是"模型内部在算什么"**——你永远在黑箱外面

### 3.3 SHAP：博弈论的唯一解（2017）

2017 年，同一年的 NIPS 上，Scott Lundberg 和 Su-In Lee 发表 **"A Unified Approach to Interpreting Model Predictions"**，提出 SHAP（SHapley Additive exPlanations）。

SHAP 把每个特征当作博弈论中的"玩家"，把模型输出当作"联盟收益"，用 **Shapley 值**分配每个玩家的贡献：

$$\phi_i = \sum_{S \subseteq N \setminus \{i\}} \frac{|S|! (|N|-|S|-1)!}{|N|!} [f(S \cup \{i\}) - f(S)]$$

Lundberg-Lee 的贡献是证明：**Shapley 值是同时满足四个公理（效率/对称/虚拟/可加）的唯一归因方法**。这让 SHAP 有了"博弈论保证"的光环。

**SHAP 在工业界的影响**：几乎每个风控、信贷、保险团队都在用 SHAP。它成了"AI 可解释性"的工业标准。很多公司把 SHAP 值直接嵌入决策系统，作为"合规证据"。

### 3.4 反事实解释（2017）

同期，牛津大学的 Sandra Wachter、Brent Mittelstadt、Chris Russell 发表 **"Counterfactual Explanations Without Opening the Black Box"**。

他们提出了一个完全不同的思路：**不解释模型为什么这么做，而是告诉用户"你需要改变什么，模型才会给出不同结果"**。

```
贷款申请被拒。
传统解释（SHAP）："你的收入对拒贷贡献最大。"
反事实解释："如果你的年收入增加 5000 元，你会被批准。"
```

反事实解释的优势：
- 不需要"打开黑箱"——只在输入端搜索
- 更符合人类直觉（"我该怎么做"比"为什么"更实用）
- 在 GDPR 框架下有法律意义（"知情权"的满足方式）

### 3.5 第一次范式转移的局限

事后解释这一波（LIME/SHAP/反事实）有一个共同的、根本性的局限：

> **它们解释的是"输入和输出的关系"，而非"模型内部在做什么"。**

2017 年 MIT 的 Adebayo 等人发表 **"Sanity Checks for Saliency Maps"**——这记耳光打得太狠了（详见 [04-Attribution与梯度方法](./04-Attribution与梯度方法.md)）：

1. 把模型最后一层权重**随机化** → 热力图几乎不变
2. 把上面几层**全部随机化** → 热力图**还是那张图**
3. 换一个完全不同的模型 → 热力图**看上去差不多**

**结论**：你看到的"模型在关注眼睛和鼻子"的热力图，很大一部分来自**输入图像本身的边缘结构**，不是模型学到的判别依据。**这些事后解释方法与模型参数的相关性远低于预期。**

> 🎯 **思想史意义**：Sanity Check 是事后解释方向的"危机信号"——它证明了事后解释（至少是第一代方法）**可能根本不在解释模型**，而是在解释输入数据的自然结构。这直接催生了第二次范式转移：**必须打开模型内部看，不能只在外面看。**

---

## 4. Attention 解释的争议：一个"解释"的自我否定（2017-2019）

### 4.1 Attention 权重作为解释

Transformer（2017）让 attention 权重成了最直观的"解释"：看到 attention 热力图高亮了某些词，人们自然而然认为"模型在看这些词"。

2018-2019 年，大量论文把 attention 可视化当作 BERT/GPT 的"解释工具"——医疗 NLP 用 attention 证明模型"关注了症状词"，法律 NLP 用 attention 证明模型"关注了法条"。

### 4.2 Jain-Wallace 的挑战

2019 年 NAACL，Sarthak Jain 和 Byron Wallace 发表 **"Attention is not Explanation"**。他们做了三件事：

1. 训练一个文本分类模型，拿到 attention 权重 $a$
2. **把 attention 权重随机打乱**（完全打乱），模型性能不变
3. 训练一个**不同的 attention 分布** $a' \neq a$，但和 $a$ 预测结果一致

**结论**：attention 权重 ≠ 解释。模型可以有完全不同的 attention 分布但做出相同预测——这说明 attention 不承载因果信息。

### 4.3 Wiegrebe-Wattenberg 的反驳

Jain-Wallace 引发了激烈辩论。Wiegrebe 和 Wattenberg（以及 Sara Sarti、Sebastian Gehrmann 等）在后续工作中反驳：

- attention **可以是**解释的一部分，但不是全部
- 关键是区分 **attention weights**（计算图的一部分）和 **attribution**（因果贡献）——它们是不同的东西
- 多头 attention 里，不同 head 承载不同功能，简单加总有误导性

### 4.4 争议的深层意义

> **attention 争议暴露了一个思想史级的问题：模型计算图的哪一部分可以当"解释"？**

attention 权重是模型前向计算的一部分——它不是"事后贴上去的"（像 SHAP），而是模型内部的计算量。但即使如此，它也不等于"因果贡献"。

这个认识直接推动了后来机械可解释性的**因果验证标准**：**任何声称"找到了重要部件"的工作，必须通过 ablation（关掉它看效果）或 activation patching（替换它看效果）来验证因果性**——不能只看相关性。

> **反常识**：attention 争议是好事。它把社区从"看到什么就信什么"的幼稚阶段推到了"必须因果验证"的成熟阶段。没有这个争议，机械可解释性可能不会那么早建立严格的验证标准。

---

## 5. Probing：问模型"你知不知道 X"（2017-2020）

### 5.1 什么是 Probing

**Probing**（探针）是深度学习时代最早的可解释性方法之一。思路：训练一个小分类器（叫"探针"），从模型中间层激活预测某个属性。如果探针准确率高，说明模型"知道"这个属性。

```python
hidden = bert.layer_7(input).hidden_state   # 取 BERT 第 7 层激活
probe = Linear(d_model, n_labels)            # 小线性分类器
probe.fit(hidden, labels)                     # 用词性标签训练
# probe.acc > 90% → BERT 第 7 层"编码了"词性信息
```

### 5.2 Belinkov 与 BERT probing 浪潮

2017 年起，Yonatan Belinkov（MIT/Harvard）发表了一系列 NMT probing 论文，发现翻译模型的中间层编码了语法信息（词性、依存关系）。

2018 年 BERT 发布后，probing 论文井喷：

- **Tenney et al. (2019)**："BERT for what?"——设计了 NLP 任务的 probing 套件
- **Hewitt & Manning (2019)**：发现 BERT 内部有**语法树结构**（structural probe）
- **Clark et al. (2019)**：BERT 哪些 attention head 在做什么

这些工作形成了一个**丰富但碎片化的图景**：我们知道 BERT 底层学语法、中层学语义、顶层学任务——但我们**不知道这些信息怎么被使用**。

### 5.3 Probing 的根本局限

2020 年，精英研究院的 Hewitt 与 Stanford 的 Percy Liang、Chris Manning 合作，发表了 **"Designing and Interpreting Probes with Control Tasks"**——首次严格界定了 probing 的边界：

**核心区分**：
- **探针准确率高 ≠ 模型"用了"这个信息**
- 探针可能从冗余编码中"偷"到信息——模型根本没有在计算中使用这些表征

Hewitt 引入了 **control task**：构造一个与模型无关的随机任务，如果探针在这个任务上也表现好，说明探针本身太强，不是模型真有这个信息。

> 🎯 **思想史意义**：Probing 从"黄金标准"变成了"必要非充分条件"——探针高分只能说明信息**存在**，不能说明信息**被使用**。这个认识直接催生了后来的 **causal scrubbing** 和 **activation patching**——你必须**干预**才能证明因果性，不能只观察。

### 5.4 Probing 到 Mechanistic 的桥

Probing 回答"模型知道 X 吗"——这只是在模型表征上贴标签。下一个自然的问题是：

- **模型怎么使用这个信息？** → 需要找计算路径
- **这个信息在哪个计算步骤被使用？** → 需要因果追踪
- **能不能关掉它看效果？** → 需要 ablation / patching

这些问题从"观察"转向了"干预"——这就是机械可解释性的入口。

---

## 6. 第二次范式转移：机械可解释性（Olah 2020）

### 6.1 Chris Olah 与 Circuits 议程

2020 年 3 月，**Chris Olah** 在 Distill 期刊发表了 **"Zoom In: An Introduction to Circuits"**。这篇文章是机械可解释性的**独立宣言**。

Olah 的核心主张可以浓缩为一句话：

> **神经网络可以被逆向工程为可理解的计算回路（circuits）。就像生物学家用显微镜看细胞结构一样，我们可以用可视化工具看神经网络内部的"功能模块"。**

Olah 提出了三个"野心勃勃的假设"：

1. **可解释性假设**（Interpretability Hypothesis）：神经网络的每个组件——从单个神经元到整个层——都可以被翻译成人类可理解的概念
2. **电路假设**（Circuits Hypothesis）：神经网络由可识别的功能回路组成，每个回路实现一个可理解的计算
3. **通用性假设**（Universality Hypothesis）：不同模型（甚至不同架构）会学到相似的特征和回路——就像生物视觉皮层在不同物种间保守

### 6.2 为什么是 2020 年

**思想史问**：为什么机械可解释性在 2020 而不是 2010 或 2015 兴起？

1. **Transformer 的统一性**：2020 年 Transformer 已经统一了 NLP，它的 attention head 结构比 CNN 更"可分解"——每个 head 有清晰的 Q/K/V 功能划分，这给了人们"可以一个 head 一个 head 看"的信心
2. **Distill 期刊的可视化传统**：Olah 从 2014 年起在 Distill 上发表 CNN 可视化论文（feature visualization），积累了"如何让神经网络内部可视化"的方法论
3. **AI 安全的紧迫性**：2020 年 GPT-3 发布，大模型能力突飞猛进，"我们不理解自己造的东西"的焦虑达到顶峰
4. **Olah 加入 Anthropic**：2019 年 Olah 离开 OpenAI 加入 Anthropic——Anthropic 的使命是 AI 安全，可解释性是其中的核心。Olah 在这里获得了长期资源支持（不需要发会议论文），建立了 **Transformer Circuits Thread**——一个发长文、不设篇幅限制、追求深度的研究平台

### 6.3 Olah 的方法论革命

Olah 做了三件之前没人系统做过的事：

**第一，把单个神经元当研究对象**。不是看整个模型，而是"这个神经元在做什么？"——用 feature visualization（最优激活图像）和 dataset examples（激活最高的训练样本）来回答。

**第二，找 neuron-to-neuron 的连线**。不仅看单个神经元，还看它们之间的权重连接——哪些神经元一起协作，形成功能回路。

**第三，坚持跨尺度一致性**。从单个神经元 → 到几个神经元的回路 → 到整个层 → 到整个模型。每一步都要能"翻译"成人类语言。

> 🎯 **方法论核心**：机械可解释性不问"输入哪部分重要"（attribution），也不问"模型知道 X 吗"（probing），而是问**"模型内部怎么算的"**——这是从模型外部到模型内部的根本性转向。

### 6.4 第一次范式转移 vs 第二次

| 维度 | 事后解释（LIME/SHAP）| 机械可解释性（Olah）|
|---|---|---|
| **在模型外面还是里面** | 外面（黑箱外的扰动/归因）| **里面**（逆向工程）|
| **可预测性** | 弱（只能回顾性解释）| **强**（找到 circuit 后能预测行为）|
| **能否干预** | 否（只解释不修改）| **是**（ablation / steering）|
| **能否发现新现象** | 否（只回答预设问题）| **是**（可以发现模型自发学到的功能）|
| **可扩展性** | 强（任何模型都能跑）| 弱（需要大量手工/半自动分析）|

---

## 7. Anthropic Circuits：从 Vision 到 Transformer（2021-2022）

### 7.1 Vision Circuits（2020）

Olah 的早期 circuits 工作在 CNN 上进行。他们发现了 CNN 里的**曲线检测器**（curve detector）、**方向检测器**（orientation detector）和高频边缘检测器——这些是视觉皮层 V1 里经典已知的功能模块。

**关键发现**：这些 circuit 在不同 CNN 模型间**高度一致**——不同架构、不同数据集训出的 CNN 都长出了相似的检测器。这支持了**通用性假设**。

### 7.2 Transformer Circuits Thread（2021-）

2021 年，Olah 团队（此时已在 Anthropic）建立了 **Transformer Circuits Thread**，系统地在 Transformer 上做逆向工程。第一阶段成果：

**a) 零层 Transformer 的分析**（Elhage et al. 2021）：一个只有 attention + 残差连接、没有 MLP 的两层 Transformer，可以被完全理解——每个 head 的 QK 和 OV 矩阵可以直接翻译为"这个 head 在匹配什么 / 输出什么"。

**b) Induction Heads（Olsson et al. 2022）**：这是机械可解释性迄今最重要的发现。

### 7.3 Induction Heads：ICL 的物理基础

2022 年 3 月 8 日，Catherine Olsson、Nelson Elhage、Neel Nanda 等人在 Transformer Circuits Thread 发表 **"In-context Learning and Induction Heads"**。

**发现**：跨 40+ 个 Transformer（从 1 层到 40 层，从不同实验室、不同训练数据），**只要模型有 2 层以上 attention，几乎所有模型都长出了 induction head**。

Induction head 做的事很简单——**复制匹配模式**：

```
输入：[A][B]  ...  [A]
                  ↓
预测：            [B]
```

**它是怎么实现的**：induction head 是**两个 attention head 的协作**——

1. **Previous Token Head**（前一层）：把"前一个 token 是什么"的信息复制到当前位置
2. **Induction Head**（后一层）：用这个信息做匹配——"我在找前面是 [A] 的位置"，找到后把下一个 token [B] 复制过来

**为什么这是革命性的**：

- Olsson 证明了 induction head 是 **in-context learning（ICL）的物理基础**——所有"few-shot 学新任务"的能力，底层都是这个复制-匹配回路在工作
- 它在**几乎所有 Transformer 上自发涌现**——说明它是计算的原语，模型一有能力就先长出它
- **Ablation 验证**：关掉 induction head → ICL 能力消失。这满足了因果验证标准

> **思想史意义**：induction heads 是机械可解释性第一个"完整闭环"——从发现 circuit → 理解机制 → 验证因果性 → 解释涌现能力。它证明了"找 circuit"这条路是可行的。

### 7.4 IOI Circuit（Wang 2022）

2022 年，Anthropic 的 Kevin Wang 等人发表了 **"Interpretability in the Wild: a Circuit for Indirect Object Identification in GPT-2 Small"**。

他们完全逆向工程了 GPT-2 Small 处理 **"John gave the book to Mary, then he gave it to ___"** 这类句子的计算回路——涉及 26 个 attention head，分成多个功能组：

- **Name Mover Heads**：把正确答案的信息搬运到输出
- **Backup Name Mover Heads**：当主 Name Mover 被破坏时接管
- **S-Inhibition Heads**：抑制错误候选

IOI 证明了**完整逆向工程**在小模型上是可行的——不仅仅是"找到了一个 circuit"，而是**完全描述了模型在这个任务上的计算过程**。

### 7.5 但小模型 ≠ 大模型

这两个经典 circuit（induction heads / IOI）都是在**小模型**上发现的。当研究者转向 GPT-3/4 级别模型时，他们撞上了一堵墙——**Superposition**。

---

## 8. 第三次范式转移：SAE / 超叠加（2023-）

### 8.1 Superposition 问题

2022 年底，Anthropic 的 Nelson Elhage 等人发表了 **"Toy Models of Superposition"**——这篇论文解释了为什么大模型上找 circuit 那么难。

**核心发现**：当特征数量 $N$ 远大于表征维度 $d$ 时（$N \gg d$），模型不是"丢掉"多余特征，而是**把它们挤进有限维度里**——用**近似正交的方向**编码所有特征。

```
模型有 100 维激活空间
但需要编码 10000 个概念
解法：每个概念用一个 100 维空间里的方向表示
      10000 个方向在 100 维空间里"几乎正交"
      单个神经元（一个维度）同时参与多个概念
```

**后果**：单个神经元**不再 monosemantic（单语义）**——一个神经元可能同时编码"法国"、"首都"、"蓝色"、"名词"……这使得手工看单个神经元变成了无意义的操作。

### 8.2 Sparse Autoencoder：拆解叠加

2023 年，多个团队几乎同时提出了用 **Sparse Autoencoder（SAE）** 解决 superposition 的方案。

**SAE 的结构**：

```
模型激活 x（d 维，密集）
    ↓ 编码器 W_enc
稀疏特征 z（N >> d 维，但大部分为 0）
    ↓ 解码器 W_dec
重建 x' ≈ x
```

**核心约束**：$z$ 是**稀疏的**——对于任何输入，只有少数特征激活。这迫使 SAE 学习**有意义的特征方向**，而不是简单地复制。

如果 SAE 训练成功，$z$ 的每一维就对应一个 **monosemantic 特征**——一个清晰的可解释概念。

### 8.3 Anthropic "Towards Monosemanticity"（2023）

2023 年 10 月，Anthropic 的 Bricken、Templeton 等人发表了 **"Towards Monosemanticity: Decomposing Language Models With Dictionary Learning"**。

他们在一个只有 1 层的小 Transformer 上训了 SAE，找到了数千个特征。每个特征都清晰对应一个人类可理解的概念：

- 有"DNA 序列"特征——在生物学文本上激活
- 有"阿拉伯语"特征——在阿拉伯语文本上激活
- 有"星期一"特征——在日期相关文本上激活

**关键验证**：
1. **Ablation**：关掉"阿拉伯语"特征 → 模型在阿拉伯语文本上的预测能力下降
2. **Activation Steering**：人为激活"DNA"特征 → 模型在所有回答里都提到 DNA
3. **组合性**：特征可以组合——"阿拉伯语" + "DNA" = 在阿拉伯语生物学文本上激活

> 🎯 **这就是"单义性"的含义**：每个 SAE 特征只表示一个概念，不再像单个神经元那样混叠。

### 8.4 Scaling Monosemanticity（2024）

2024 年 5 月 21 日，Anthropic 的 Templeton 团队把 SAE 推到了生产级模型——**在 Claude 3 Sonnet 上训了一个有十亿维字典的 SAE**。

这是机械可解释性历史上最大的单次突破：

- 在 Claude 3 Sonnet 中找到了**数百万个可解释特征**
- 包括具体概念（"金鱼"、"萨特"、"德克萨斯州奥斯汀市"）
- 包括抽象概念（"背叛"、"安全隐患"、"欺骗"）
- 包括跨语言概念（"金鱼"特征在英语/法语/中文文本上同时激活）

**金鱼实验**（steering 验证）：找到"金鱼"特征 → 人为放大它 → 模型在所有回答里都提到金鱼。

**欺骗特征**：找到了"安全隐患 / 欺骗"相关特征——这是可解释性第一次可能**检测到模型的欺骗倾向**，直接连接到 AI 安全。

### 8.5 OpenAI / DeepMind 的跟进

SAE 方向在 2024 年迅速扩散：

- **OpenAI**（Gao et al. 2024）：在 GPT-4 上训了更大的 SAE，发表 "Scaling and evaluating sparse autoencoders"
- **DeepMind**：跟进 SAE 方法学改进（JumpReLU SAE、TopK SAE）
- **独立研究者 Neel Nanda**：建立了 TransformerLens 工具链，降低了 SAE 研究的入门门槛

### 8.6 第三次范式转移的本质

| 之前 | SAE 之后 |
|---|---|
| 手工找 circuit（耗时、不可扩展）| **自动化**找特征（SAE 训练即找）|
| 单神经元 = 多概念（无法解释）| SAE 特征 = **单概念**（可解释）|
| 小模型上有效，大模型上放弃 | **大模型上有效**（Claude 3 Sonnet）|

> **但 SAE 不是万能的**。它面临的挑战包括：① 字典要多大才够？（覆盖模型能力的多少？）② SAE 找到的特征是真机制还是 interpretability illusion？③ SAE 特征之间的连线（circuit）仍然极难找。这些是 2024-2026 的前沿战场。

---

## 9. 第四次范式转移：可解释性作为对齐工具（2024-2026）

### 9.1 从"理解"到"控制"

到 2024 年，可解释性经历了一个微妙但深刻的目标转变：

**之前**（2020-2023）：可解释性 = 学术好奇心。我们想"理解"模型是怎么工作的——这本身就是一个科学目标。

**之后**（2024-）：可解释性 = **安全基础设施**。我们不是为理解而理解，而是为了**控制和对齐**而理解。

驱动这个转变的是大模型部署的现实压力：

- GPT-4 / Claude 3 已经在生产环境大规模部署
- "模型是否对齐"不再只是学术问题——关系到数亿用户
- RLHF 训练后的模型可能"sycophancy"（讨好）或"deceptive alignment"（伪装对齐）
- 没有可解释性，**无法区分"真的对齐"和"装的对齐"**

### 9.2 激活导向（Activation Steering）

2023-2024 年，**activation steering** 成为一个应用热点。原理直接来自 SAE 研究：

```
找到"拒绝"方向（refusal direction）
    ↓
人为往这个方向加向量
    ↓
模型变得"更拒绝"或"更不拒绝"
```

**安全应用**：
- 检测和抑制 harmful content（找到"暴力"特征 → 抑制它）
- 检测 sycophancy（找到"讨好"特征 → 观察它在什么情况下激活）
- 检测 deception（找到"欺骗"特征 → 监控它是否在推理过程中激活）

### 9.3 Causal Tracing 与 Activation Patching

2022-2024 年，另一条因果分析路径成熟：

**ROME**（Meng et al. 2022）：**"Locating and Editing Factual Associations in GPT"**。他们发现事实知识存储在 MLP 层的特定位置，可以通过**编辑这些位置**来修改模型的知识——比如把"埃菲尔铁塔在巴黎"改成"在罗马"。

**Activation Patching**（Heimersheim & Nanda 2023）：更通用的因果分析工具——从一个 prompt 的激活"打补丁"到另一个 prompt，看模型行为怎么变。

这些方法提供了**因果验证的标准化工具**——不再只看相关性，而是通过干预来证明因果性。

### 9.4 LLM-based Interpretability

2024-2026 年，一个新方向兴起：**用 LLM 来解释 LLM**。

- 用 GPT-4 自动标注 SAE 特征的含义（而不是人工看）
- 用 LLM 来总结 circuit 的功能
- 用 LLM 来生成反事实测试

这引入了一个**循环验证问题**：用 LLM 解释 LLM，解释器本身也可能是幻觉。但这是一个实用性上的突破——人工标注数百万个 SAE 特征不现实，自动化标注是唯一的可扩展路径。

### 9.5 Conjecture 与独立研究者社区

2023-2024 年，独立研究者社区在可解释性领域扮演了关键角色：

**Neel Nanda**：在加入 Anthropic 的 induction heads 工作后，独立创建了 **TransformerLens**——一个专门为可解释性研究设计的 Transformer 分析库。TransformerLens 降低了入门门槛，让大量独立研究者能够参与 circuit 分析。Nanda 还撰写了 **"A Mechanistic Interpretability Roadmap"**——一份为独立研究者指明方向的长文。

**Conjecture**（公司）：由 Connor Leahy 创立，专注于可解释性和 AI 安全。他们的工作聚焦在可解释性的工程化——把学术发现转化为可部署的安全工具。

**EleutherAI** 社区：开放模型（GPT-Neo / Pythia）的可解释性研究的重要基地。

> **思想史观察**：可解释性是 AI 领域里**独立研究者占比最高的方向之一**。原因是：① 工具（TransformerLens）门槛低；② 小模型上就能做有意义的工作；③ 社区文化开放，长文和博客比论文更重要。

### 9.6 2026 年的 Circuit Analysis

到 2026 年，circuit analysis 已经从"手工找单个 circuit"进化为：

1. **Automated Circuit Discovery**：ACDC（Conmy 2023）、EAP（Syed 2023）等算法能半自动找 circuit
2. **SAE-based Circuits**：不再用单个神经元找 circuit，而是用 SAE 特征——更清晰、更可扩展
3. **Cross-model Universality**：跨模型比较 circuit——不同实验室的模型是否有相同结构
4. **Multimodal Circuits**：在视觉-语言模型上找跨模态 circuit
5. **Scaling Circuits**：从 GPT-2 small 到 Claude 3 级别的 circuit 跨尺度分析

**但诚实的评估是**：在大模型上，我们仍然只覆盖了模型能力的极小部分。已发现的 circuit 和 SAE 特征是冰山一角。

---

## 10. 思想史反思：五个反常识

### 反常识 1：可解释性不是"越来越难"，而是"难度类型在变"

**直觉**：深度学习让 AI 更难解释了。

**真相**：MYCIN 时代模型"自然可解释"但**能力极低**；深度学习模型"极难解释"但**能力极高**。这不是退步——这是"用可解释性换能力"的交易。而且机械可解释性证明：**神经网络内部有结构**——不是不可理解的混沌。

**方法论训练**：不要把"当前难解释"等同于"永远不可解释"。难度的类型在变（从"获取知识"到"理解分布式表示"），但不是单调递增。

### 反常识 2：事后解释的"黄金时代"（2016-2018）是一场错觉

**直觉**：LIME/SHAP 让黑盒 ML 变可解释了。

**真相**：Sanity Check（Adebayo 2017）证明很多事后解释方法**根本不在解释模型**——它们在解释输入数据的自然结构。整个"SHAP 工业标准"建立在**未经严格验证的前提上**。

**方法论训练**：广泛采用 ≠ 正确。工业标准可能建立在有缺陷的假设上——这需要 5-10 年才能暴露。

### 反常识 3：Mechanistic Interpretability 的"创始论文"不在会议

**直觉**：重要的 AI 研究都发 NeurIPS/ICML/ICLR。

**真相**：机械可解释性最重要的工作——Olah 的 Circuits Thread、induction heads、Scaling Monosemanticity——**都不在会议论文里**。它们发表在 Transformer Circuits Thread（Anthropic 自建平台）和 Distill（可视化期刊）。原因：① 这些工作篇幅长、可视化多，不适合会议格式；② Olah 团队有 Anthropic 的长期资金支持，不需要会议认可。

**方法论训练**：前沿思想的载体在变——博客、长文、平台可能比会议更重要。不看 Transformer Circuits Thread 就等于错过了一个整个子领域。

### 反常识 4：Superposition 不是缺陷，是特性

**直觉**：模型把多个概念挤进一个神经元是"表征不够用"的缺陷。

**真相**：Elhage 的 Toy Models 证明——**superposition 是模型主动选择的策略**。当概念比维度多时，用"近似正交"的叠加编码比"丢弃"多余概念更高效。模型选择 superposition 是为了**在有限维度内最大化信息容量**。

**方法论训练**：不要假设"人类觉得好的结构"就是模型应该有的结构。superposition 看起来"乱"，但它是信息论最优的。

### 反常识 5：最强的可解释性工具不是显微镜，是手术刀

**直觉**：可解释性 = 理解模型（像显微镜看细胞）。

**真相**：2024-2026 的趋势证明——可解释性最有价值的用途不是"理解"而是**"干预"**。steering vectors、activation editing、refusal direction——这些不是在看模型，而是**在改模型**。理解只是手段，控制才是目的。

**方法论训练**：可解释性的终极价值不在学术论文里，而在 AI 安全的工程实践中。一个"能检测欺骗"的粗略特征比一百篇"理解模型"的论文更重要。

---

## 11. 关键人物谱系

### 11.1 Chris Olah：可解释性的"Olah 时代"

**Chris Olah** 是机械可解释性的公认创始人。

- 2014 年起在 Distill 发表 CNN 可视化论文（feature visualization）
- 曾在 OpenAI 短暂工作
- 2019 年加入 Anthropic，建立 Transformer Circuits Thread
- 核心贡献：circuits 概念框架、induction heads、superposition 理论、SAE 方向的推动

Olah 的影响力不仅来自他的研究——更来自他的**写作风格**。他的论文/长文极度注重可视化、极度注重可读性，建立了一种"可解释性论文就该长这样"的标准。

### 11.2 Anthropic Circuits 团队

| 人物 | 核心贡献 |
|---|---|
| **Nelson Elhage** | Superposition theory（toy models）、零层 Transformer 分析 |
| **Catherine Olsson** | Induction heads 的发现者——ICL 物理基础 |
| **Neel Nanda** | Induction heads 合作者；后来独立创建 TransformerLens |
| **Templeton** | Scaling Monosemanticity（2024 Claude 3 Sonnet SAE）|
| **Bricken** | Towards Monosemanticity（2023 小模型 SAE）|

### 11.3 独立研究者网络

| 人物 | 角色 |
|---|---|
| **Neel Nanda** | TransformerLens 创建者；可解释性路线图作者；独立研究者社区的核心 |
| **Connor Leahy** | Conjecture 创始人；可解释性工程化 |
| **Stephen Casper** | MIT；可解释性评估方法论 |

### 11.4 "外部"贡献者

| 人物 | 核心贡献 |
|---|---|
| **Adebayo (MIT)** | Sanity Checks——事后解释的"审判者" |
| **Jain & Wallace** | Attention 争议——推动因果验证标准 |
| **Hewitt & Liang (Stanford)** | Probing control tasks——探针边界 |
| **Meng (Stanford→Anthropic)** | ROME——事实知识的定位与编辑 |
| **Wachter (Oxford)** | 反事实解释——法律视角的可解释性 |

### 11.5 谱系图

```
Chris Olah
├── Anthropic Circuits Thread
│   ├── Nelson Elhage → superposition theory
│   ├── Catherine Olsson → induction heads
│   ├── Templeton → scaling monosemanticity
│   └── (Neel Nanda → 独立后 TransformerLens)
├── 方法论影响
│   ├── Adebayo → sanity checks (受 Olah "忠实性"理念影响)
│   └── Hewitt → probing control tasks (受 "因果验证" 影响)
└── 派生方向
    ├── Meng → ROME / knowledge editing
    ├── Conjecture → 工程化
    └── 独立社区 → TransformerLens 生态
```

---

## 12. 失败方向

### 12.1 规则提取（1990s）

**当时为什么合理**：神经网络刚兴起，符号主义传统还在，从网络里"挖出"规则的想法很自然。

**为什么失败**：规则数量爆炸（大网络→上万条规则）；提取的规则不忠实于模型；缺乏理论基础。

**教训**：**不能把符号主义的解释方法硬套在连接主义模型上**。分布式表示不适合"翻译"成符号规则——这就像把油画翻译成音乐，类别不匹配。

### 12.2 Attention 作为解释（2018-2019）

**当时为什么合理**：attention 权重是模型内部的量，高亮它看起来最"忠实"。

**为什么失败**：Jain-Wallace 证明 attention 可以被完全打乱而模型行为不变。

**教训**：**模型计算图的一部分不等于因果贡献**。attention weights 是"怎么算的"，不是"为什么这么算"——混淆这两者是可解释性最常见的错误。

### 12.3 Saliency Map 作为证据（2013-2017）

**当时为什么合理**：梯度对输入最敏感的地方"应该"最重要——直觉上完全说得通。

**为什么失败**：Adebayo 的 sanity check 证明 saliency map 和模型参数的相关性远低于预期。

**教训**：**任何"看起来合理"的解释方法都必须通过因果验证**——否则它可能只是在描述输入数据的自然结构，而非模型的计算。

### 12.4 "LLM 自我解释"（2023-）

**为什么可能失败**：让 GPT-4 输出 chain-of-thought 来"解释"自己的推理——看起来合理，但模型可能是在**生成一个听起来合理的后验故事**，而非报告真实计算过程。

**当前状态**：这是一个**尚未被否定但高度可疑**的方向。机械可解释性的研究表明，模型的 chain-of-thought 和其内部计算之间**可能存在系统性偏差**。

**教训**：**模型的自我报告不是解释**——它是另一层需要被验证的输出。这与 MYCIN 时代的"解释即推理链"形成了有趣的历史呼应：MYCIN 的推理链是人写的（可靠的），GPT-4 的推理链是模型生成的（可能不可靠）。

---

## 13. 路径依赖与偶然性

### 13.1 如果 Olah 没有加入 Anthropic

机械可解释性的发展轨迹可能完全不同。Olah 在 OpenAI 时的 circuits 工作已经开始了，但 OpenAI 的文化更偏向 scaling 和产品——不太可能给 Olah 一个**不需要发会议论文、长期支持**的研究环境。Anthropic 的 AI 安全使命 + Dario Amodei 的个人支持，是 Transformer Circuits Thread 能长期存在的关键。

**反事实**：如果 Olah 留在 OpenAI，circuits 议程可能发展得更慢、更碎片化——会被 conference deadline 驱动，难以做长达数年的长线研究。

### 13.2 如果 Sanity Check 没有发表

如果 Adebayo 2017 的 "Sanity Checks for Saliency Maps" 没有发表，事后解释（LIME/SHAP）可能继续被当作"解释金标准"使用多年。社区可能在更长时间里**不知道自己的解释工具可能无效**——直到更严重的后果（如医疗误诊）暴露问题。

Sanity Check 论文本身不是"发明"了什么——它只是做了一个**本应在方法提出时就做的验证**。但没有人提前做。这是科学社区集体盲点的一个案例。

### 13.3 Transformer 的 Q/K/V 分解

机械可解释性之所以能在 Transformer 上取得进展，部分归功于 Transformer 的**架构设计**——每个 attention head 有清晰的 Q/K/V 分解，这使得"这个 head 在匹配什么"有了可操作的入口。

**反事实**：如果主流模型是 RNN 或 MLP-Mixer（没有显式的 attention head 分解），机械可解释性可能无法发展得这么快。attention head 是**天然的解剖单元**——这降低了逆向工程的难度。

### 13.4 Neel Nanda 的 TransformerLens

TransformerLens 是一个工具，但它的影响**远超工具本身**。在 TransformerLens 之前，做可解释性研究需要从零搭基础设施——读取中间层激活、hook attention pattern、做 ablation……TransformerLens 把这些都打包好了，使得一个博士生在一个周末就能复现 induction heads。

**反事实**：如果没有 TransformerLens，独立研究者社区可能无法如此快速地成长——可解释性会更封闭地留在几个大实验室内部。

### 13.5 Distill 的遗产

Distill 期刊在 2021 年停刊了。但它在 2016-2020 发表的可视化论文（包括 Olah 的 circuits 工作）**建立了可解释性论文的审美标准**——注重可视化、注重可读性、不追求"数学多难"而追求"道理多清楚"。

**反事实**：如果没有 Distill，Olah 的 circuits 工作可能不得不改成会议格式——丢失大量可视化细节，影响力大减。Distill 虽然停了，但它塑造的**论文风格遗产**在 Transformer Circuits Thread 里延续。

---

## 14. 开放问题

### 14.1 Superposition 能完全解吗？

SAE 能找到的特征空间有多大？是否有根本性局限——某些类型的 superposition 永远无法被解开？目前 Scaling Monosemanticity 在 Claude 3 Sonnet 上找到了数百万特征，但相对于模型的万亿参数，这可能只是冰山一角。

### 14.2 Interpretability Illusion 的边界

找到的"特征"可能是 SAE 的构造，而非模型真用的。怎么验证？目前的因果验证（ablation / steering）是必要的，但**覆盖度极低**——你不可能对数百万特征逐一做 ablation。

### 14.3 Circuit 概念在大模型上是否成立

在小模型上，IOI circuit 涉及 26 个 head——可控。但在 GPT-4 级别，一个 reasoning 行为可能涉及**几百万神经元**。这时"circuit"概念本身是否还有意义？还是需要一种全新的、分布式的理解框架？

### 14.4 理解能否预测能力

找到 circuit 能不能预测**未测试场景**的行为？这是真理解的标志——就像物理定律不仅能解释已知现象，还能预测未知。目前可解释性几乎完全是**回顾性**的——它解释已发生的行为，不能预测未发生的行为。

### 14.5 可解释性能跟上 Scaling 吗

模型参数每 6 个月翻倍。可解释性工具的进展速度跟得上吗？如果模型 scale 到 10T 参数，SAE 的字典需要多大？能不能训得动？这是一个工程极限问题。

### 14.6 Deceptive Alignment 的可检测性

如果模型真的有 deceptive alignment——测试时友好、部署时恶意——可解释性能检测到吗？如果欺骗行为分散在全模型（而非局部 circuit），steering 和 ablation 可能无法定位。这是 AI 安全最根本的开放问题。

### 14.7 解释的"忠实度"如何度量

什么算"忠实的解释"？目前没有统一的度量标准。SHAP 有公理保证但被 sanity check 否定；SAE 特征有因果验证但覆盖度未知。**缺乏统一的"忠实度度量"**是可解释性最根本的理论缺口。

---

## 15. 配套资源

### 15.1 必读论文/长文（按时间线）

| 年份 | 作者 | 标题 | 意义 |
|---|---|---|---|
| 1970s | Shortliffe | MYCIN | 符号主义"自然解释"的典范 |
| 1986 | Quinlan | Induction of Decision Trees (ID3) | 可解释 ML 的黄金标准 |
| 1993 | Tickle & Andrews | The Truth Will Come Forth | 规则提取综述 |
| 2016 | Ribeiro et al. | Why Should I Trust You (LIME) | 事后解释的开山 |
| 2017 | Lundberg & Lee | A Unified Approach (SHAP) | 博弈论归因 |
| 2017 | Wachter et al. | Counterfactual Explanations | 反事实解释 |
| 2017 | Adebayo et al. | Sanity Checks for Saliency Maps | 事后解释的审判 |
| 2019 | Jain & Wallace | Attention is not Explanation | attention 争议 |
| 2020 | Olah et al. | Zoom In: Circuits | 机械可解释性宣言 |
| 2021 | Elhage et al. | A Mathematical Framework for Transformer Circuits | Transformer 逆向工程 |
| 2022 | Olsson et al. | Induction Heads & ICL | ICL 的物理基础 |
| 2022 | Wang et al. | IOI Circuit (GPT-2 Small) | 完整逆向工程 |
| 2022 | Elhage et al. | Toy Models of Superposition | 叠加理论 |
| 2023 | Bricken et al. | Towards Monosemanticity | SAE 找特征 |
| 2024 | Templeton et al. | Scaling Monosemanticity | 生产级模型 SAE |

### 15.2 必读博客/平台

- **Transformer Circuits Thread**（transformer-circuits.pub）—— Anthropic 可解释性长文
- **Distill**（distill.pub）—— 虽停刊，但经典论文仍在
- **Neel Nanda 的博客**（neelnanda.io）—— 可解释性路线图 + TransformerLens 教程
- **Anthropic Blog**（anthropic.com/research）—— 最新 SAE / safety 论文
- **3Blue1Brown + Chris Olah**—— 神经网络可视化传统

### 15.3 工具链

- **TransformerLens**（Neel Nanda）—— 可解释性专用 Transformer 分析库
- **SAELens**—— SAE 训练和分析工具
- **Captum**（Facebook）—— Attribution 方法库（IG / SHAP / DeepLift）
- **nnsight**（NDIF）—— 远程大模型可解释性分析

### 15.4 本系列配套

| 章节 | 联动 |
|---|---|
| [00-为什么AI是黑箱](./00-为什么AI是黑箱.md) | 三条路径总览 |
| [01-探针与表征几何](./01-探针与表征几何.md) | Probing 深度展开 |
| [02-稀疏自编码器SAE](./02-稀疏自编码器SAE.md) | SAE 技术细节 |
| [03-Circuits与超级可解释性](./03-Circuits与超级可解释性.md) | Circuits 技术细节 |
| [04-Attribution与梯度方法](./04-Attribution与梯度方法.md) | Attribution 的失败史 |
| [05-Scaling-Monosemanticity与激活导向](./05-Scaling-Monosemanticity与激活导向.md) | 2024 前沿 |
| [06-应用安全审计与幻觉debug](./06-应用安全审计与幻觉debug.md) | 工程应用 |
| [讲透AI历史](../讲透AI历史/) | AI 大历史背景 |
| [讲透科学的现代性/03](../讲透科学的现代性/03-AI时代的科学哲学.md) | "AI 发现的规律算科学理解吗" |

---

## 16. 费曼回炉

### F1：一句话讲给高中生

> 五十年来，人类一直在想办法搞清楚 AI 到底在怎么"想"的。最早的 AI（专家系统）会说人话，解释是免费的；后来的 AI（深度学习）变强了但变黑了，解释要靠"贴热力图"；现在最前沿的做法是直接"解剖" AI 的内部结构——找到它的功能回路，把概念一个一个分离出来。最终的目的是：**不只理解 AI，还要能控制它、信任它。**

### F2：卡壳点

我最初把可解释性的历史理解为"技术越来越进步"的线性叙事——从"不能解释"到"能解释"。重读后才意识到这是一个**钟摆运动**：

1. MYCIN 能解释（规则可读）→ 但能力低
2. 深度学习不能解释 → 但能力高
3. LIME/SHAP 给了"假"解释（事后贴标签）→ sanity check 打脸
4. 机械可解释性给了"真"解释（内部解剖）→ 但只覆盖小模型
5. SAE 让大模型可解释 → 但 interpretability illusion 风险

**每一次"突破"都伴随着对"解释"这个词的重新定义**——MYCIN 的解释是推理链，SHAP 的解释是特征归因，Olah 的解释是功能回路。它们不是同一个东西。

### F3：术语翻译

- **"事后解释"（post-hoc）** → 模型训完之后，在它外面装一个"解释器"——就像给一个外国人配翻译，翻译可能翻错，外国人内部怎么想的你不知道
- **"机械可解释性"（mechanistic interpretability）** → 不配翻译，直接打开外国人的脑壳看神经回路——虽然难，但看到的是真的
- **"叠加"（superposition）** → 模型有 10000 个概念但只有 100 个"抽屉"，于是每个抽屉塞了好几个概念——你必须用 SAE 把它们一个个拆出来才能看清
- **"单义性"（monosemanticity）** → 一个特征只表示一个意思，不像单个神经元那样"又爱又恨又蓝又法国"

### F4：回炉记录

v1 我把可解释性写成了"不断进步的技术史"——每次新方法都比旧方法好。v2 修正了这个**进步主义叙事**：

1. 事后解释（LIME/SHAP）在某些维度上**比**机械可解释性更好——它更通用、更易部署、计算成本更低。机械可解释性"更好"只是在"忠实度"这一维度上更好
2. MYCIN 的"自然解释"并非一无可取——它的推理链**完全可靠**（规则是人写的），而 GPT-4 的 chain-of-thought **可能不可靠**（推理是模型生成的）。在某些维度上，1970s 的解释质量**高于** 2020s
3. SAE 不是终点——它只解决"特征分解"问题，circuit 发现、因果验证、覆盖度问题仍然开放

**Diff**：从"技术进步史"改为"问题重新定义史"——每次范式转移不是"更好的答案"，而是"问了不同的问题"。这才是思想史该有的深度。

---

## ✍️ 思考题

1. **方法论题**：选一个当前热门的可解释性方向（如 LLM-based interpretability），用思想史视角分析——它是真突破还是旧想法换包装？
2. **反事实题**：如果 2017 年 Adebayo 的 Sanity Check 没有发表，可解释性领域会怎样发展？事后解释还会被信任多久？
3. **判断题**：SAE 找到的"特征"是真机制还是 interpretability illusion？你怎么设计实验来验证？
4. **历史题**：MYCIN 的"解释即推理链"和 GPT-4 的 chain-of-thought 有什么本质区别？哪个更可靠？为什么？
5. **前瞻题**：可解释性能跟上模型 scaling 的速度吗？如果不能，会发生什么？

---

> **一句话总结**：可解释性五十年 = 人类对自己造的东西反复追问"我能信任你吗"的历史。答案从"能（规则可读）"到"不能（黑箱）"到"也许能（解剖看看）"到"必须能（安全要你命）"——驱动这个追问的，永远不是好奇心，而是**恐惧**。
