# AI 论文精读方法论：李沐三遍法 + 67 篇必读清单 + 工具链与实战

> **本文定位**：这是一份给"已经会调 PyTorch、但还没真正读懂过一篇论文"的工程师写的论文阅读指南。核心是李沐在 B 站 BV1H44y1t75x《如何读论文》里提出的**三遍法（Three-Pass Method）**，并配套他在 [github.com/mli/paper-reading](https://github.com/mli/paper-reading) 仓库里精选的 **67 篇十年内必读论文**。
>
> **配套阅读**：本文属于 `05-model-engineering/` 工程方法论卷，与同卷 `01-experiment-design.md`（实验设计）、`02-reproducibility.md`（可复现性）互为表里。读论文是输入端，做实验是输出端，可复现是中间的检验标准。

---

## 0. TL;DR（先看这段）

| 关键问题 | 一句话答案 |
|---|---|
| 论文要不要从头读到尾？ | **不要**。用三遍法：第一遍 5-10 分钟筛掉 80%，第二遍 1-2 小时读懂骨架，第三遍只在你要复现/基于它做研究时才做。 |
| 一个月读几篇合适？ | 工程师 4-8 篇精读 + 20-40 篇泛读；研究者 8-15 篇精读。**质量远比数量重要**。 |
| 不读论文行不行？ | 短期行（看博客/视频），长期不行——你的知识会停留在 1 年前，且无法判断新工作的真假好坏。 |
| 入门第一篇读什么？ | **Transformer（1706.03762）**。它是过去十年最重要的论文，李沐本人 1 小时 27 分钟逐段精读（BV1pu411o7BE）是最好的入门教材。 |
| 工具首选？ | arXiv + HuggingFace Papers（发现）→ Semantic Scholar / Connected Papers（关系）→ Notion/Obsidian（笔记）→ Papers With Code（实现）。 |

---

## 1. 为什么"读论文"是一项核心能力

### 1.1 AI 进展的速度已经超过了"靠博客跟"的能力

按 Stanford AI Index 2024 的统计，**arXiv 上 cs.CL + cs.CV + cs.LG 三个分类的年发文量已经突破 24 万篇**，比 2014 年增长约 12 倍。这意味着：

- 每个月有 **约 2 万篇** 与 ML 相关的新预印本；
- 你关注的子领域（假设 5% 相关）每月也有 **~1000 篇** 新论文；
- 任何"AI 周报/月报"都不可能覆盖你真正需要的那 5-10 篇。

更糟的是，**博客和科普文章平均比论文晚 3-6 个月**。等你看懂一篇某大 V 写的"Transformer 详解"时，工业界已经在用 Mamba / Hybrid 架构了。**读论文是把你的"知识半衰期"从 12 个月压到 1-2 个月的唯一手段**。

### 1.2 "只看 abstract"等于没读

很多工程师的"读论文"流程是这样：

```
看标题 → 看 abstract → 看 intro 第一段 → 看结论 → 看实验表的第一行 → 截图发朋友圈
```

这种读法的问题在于：abstract 是作者写的"营销文案"。它会告诉你"我们提出了 X，在 Y 上取得了 SOTA"，但**不会告诉你**：

- 这个 SOTA 是怎么来的（数据筛选？超参搜索？还是真的方法创新？）
- 跟你已知的方法比，到底新在哪
- 实验设计有没有漏洞（baseline 是不是被故意挑弱的？测试集有没有泄漏？）
- 哪些是 marketing，哪些是 substance

**判断这一切的唯一办法，是去读 method 和 experiment 的细节**。李沐在《如何读论文》视频里反复强调："abstract 是用来骗你读下去的，不是用来理解论文的。"

### 1.3 论文是一种"压缩过的、可质疑的、可复现的"知识载体

和博客/视频相比，论文有三个不可替代的属性：

| 属性 | 论文 | 博客 | 视频 |
|---|---|---|---|
| **可质疑** | 审稿人（理论上）挑过毛病 | 通常没有 | 通常没有 |
| **可复现** | 必须给 method + hyperparam | 经常省略 | 几乎从不给 |
| **可引用** | 有 DOI/arXiv ID，永久可查 | URL 会失效 | BV 号会下架 |
| **可累积** | 引用网络清晰 | 弱 | 几乎无 |

这就是为什么**研究者和资深工程师谈技术时，默认引用论文而不是博客**。不是 elitism，是因为论文是当前 AI 知识体系里**最稳定、最可验证、最可追溯**的形态。

### 1.4 读论文培养的两种元能力

除了具体知识，长期读论文会训练出两种"博客训练不出来"的能力：

1. **品味（taste）**：能闻出一篇论文是"真创新"还是"小修补 + 大话术"。这种品味只能靠读 100+ 篇顶级论文喂出来，没有捷径。
2. **研究直觉（research instinct）**：看到一个新方法，能立刻反应过来"这个 trick 在 5 年前的某篇论文里出现过，作者是怎么改的"。这种跨论文的关联记忆，必须靠你自己读 + 记笔记，GPT 帮不了你。

> 💡 **李沐原话（BV1H44y1t75x, 01:30）**：「读论文和写论文是research的两面……你读得多了之后，你才能知道哪些东西是真正有价值的工作，哪些东西是过眼云烟。」

---

## 2. 李沐「如何读论文」三遍法（核心方法）

李沐在 2021 年 10 月 6 日发布的 6 分 39 秒短视频《如何读论文》（[BV1H44y1t75x](https://www.bilibili.com/video/BV1H44y1t75x/)，YouTube: [txjl_Q4jCyQ](https://youtu.be/txjl_Q4jCyQ)）提出了一个朴素但极其有效的方法。这个方法的原型来自 S. Keshav 教授的经典文章《[How to Read a Paper](https://web.stanford.edu/class/ee384m/Project/List/reading.pdf)》（ACM SIGCOMM CCR, 2007），李沐把它本地化、口语化、AI 化了。

### 2.1 三遍法的总体框架

```
                   ┌──────────────────────────────────┐
                   │  拿到一篇论文                     │
                   └─────────────┬────────────────────┘
                                 ▼
                ┌────────────────────────────────┐
                │  第一遍（5-10 min）：筛选       │
                │  - title/abstract/intro/concl  │
                │  - 看图表                       │
                │  - 决定：还要不要读？           │
                └─────────────┬──────────────────┘
                              │
                  ┌───────────┴────────────┐
                  ▼                        ▼
            不读了 ✋                继续读第二遍 ✅
                                          │
                                          ▼
                ┌────────────────────────────────┐
                │  第二遍（1-2 h）：通读          │
                │  - 抓主干，不深究细节           │
                │  - 圈不懂的术语和引用           │
                │  - 决定：要不要精读？           │
                └─────────────┬──────────────────┘
                              │
                  ┌───────────┴────────────┐
                  ▼                        ▼
            不精读了 ✋              精读第三遍 ✅
                                          │
                                          ▼
                ┌────────────────────────────────┐
                │  第三遍（数小时-数天）：复现     │
                │  - 脑内/纸面重做一遍            │
                │  - 假设自己是作者，每个选择     │
                │    都问"为什么这样？"           │
                │  - 找弱点、找可改进点           │
                └────────────────────────────────┘
```

李沐的精髓在于**不是每篇都三遍**——三遍法本质上是**一个分级的注意力分配系统**：用 10 分钟筛掉 80% 的论文，用 2 小时筛掉剩下 80%，只对最后那 4% 投入数小时甚至数天。一个研究者一年可能读 200 篇，但真正走完三遍的可能只有 10-20 篇。

### 2.2 第一遍：5-10 分钟，决定要不要继续

**目标**：在 10 分钟内回答五个问题。

| # | 问题 | 看哪里 |
|---|---|---|
| 1 | 这篇论文讲什么？ | Title + Abstract |
| 2 | 它属于哪个子领域？跟谁相关？ | Intro 第 1 段 + References |
| 3 | 它的核心贡献是什么？（作者自陈） | Intro 最后一段（"Our contributions are..."） |
| 4 | 它跟同领域其他工作相比，亮点在哪？ | Abstract 里的"Unlike prior work..." |
| 5 | 我现在需要花时间读它吗？ | 综合判断 |

**关键技巧**：**只看图表，不看公式**。一篇好论文的核心图表（架构图 / 主结果表 / 关键 ablation 表）通常能让你 80% 理解它在干什么。如果图表都看不懂，要么这篇论文不适合现在的你，要么它写得不好——两种情况都意味着可以放一放。

> 💡 **李沐原话**：「我读论文第一遍，从来不去碰公式。公式是最后才看的。」

**第一遍结束后的判断**：
- ❌ 跟我的研究/工作无关 → **归档，不读**
- 🟡 有点相关，但现在用不上 → **存进 Zotero，标记 "maybe later"**
- ✅ 强相关，且看起来有料 → **进入第二遍**

经验法则：**第一遍会刷掉 70-80% 的论文**。

### 2.3 第二遍：1-2 小时，抓住骨架

**目标**：在不查任何参考资料的情况下，能用 3-5 句话向同事讲清楚这篇论文。

第二遍要做的事：

1. **通读全文**，但**遇到不懂的细节先跳过**。具体跳过什么？
   - 数学推导的中间步骤（只记结论）
   - 实现细节（具体超参数值、训练 trick）
   - 你不熟悉的术语（先标黄，集中查）

2. **重点读三块**：
   - **Method 部分**：核心思想是什么？输入输出是什么？关键模块是什么？
   - **Experiments 部分**：在哪些数据集上测的？跟谁比的？主要结果是什么？
   - **Related Work 部分**：作者把这篇论文放在哪条研究脉络里？（这是判断论文"真正创新点"的关键）

3. **圈出不懂的术语和没读过的引用**。这些都是你下一步要补的知识点。

4. **画一张图**：可以是架构图，也可以是"问题 → 方法 → 实验 → 结论"的思维导图。**手画比软件画记得更牢**（见 Mueller & Oppenheimer 2014, *Psychological Science*）。

**第二遍结束后的判断**：
- ❌ 方法不新颖 / 实验不可信 / 跟我关系不大 → **到此为止**
- ✅ 我要基于这篇论文做研究 / 我要在产品里用这个方法 / 我要在组会上讲它 → **进入第三遍**

经验法则：**第二遍会再刷掉 60-70%**。两遍累计后，剩下大约 6-12% 的论文。

### 2.4 第三遍：数小时到数天，脑内复现

**目标**：把自己当成作者，在脑子里（或纸上，或代码里）**重新做一遍这篇论文**。

第三遍要回答的问题（这是研究者的核心训练）：

| 维度 | 问题 |
|---|---|
| **问题** | 作者解决的是什么问题？为什么这个问题重要？这个问题之前为什么没被很好地解决？ |
| **动机** | 作者为什么想到这个方法？是观察到某个现象？还是某个理论启发？ |
| **方法** | 每一个设计选择，作者为什么这么做？换一种做法会怎样？（**这是第三遍最重要的训练**） |
| **实验** | 实验设计是否公平？baseline 是否够强？数据集是否合适？评测指标是否合理？ |
| **结果** | 结果是否支持论文的主张？有没有被回避的负面结果？ablation 是否充分？ |
| **局限** | 这个方法在什么情况下会失效？作者有没有承认？没承认的话你能想到什么？ |
| **可改进** | 如果我来做，我会怎么改？是基于这个方法的延伸，还是替换某个模块？ |

**第三遍的终极检验**（来自李沐视频）：

> 「读完之后，你应该能够：① 给一个没读过这篇论文的人讲清楚它的核心思想；② 回答他追问的任何细节问题；③ 想出至少一个改进方向。」

如果能做到这三条，这篇论文才算"读进去了"。

> 💡 **可选进阶**：第三遍可以伴随**代码复现**。不是每篇都要复现，但每半年至少完整复现 1-2 篇。复现会逼你看懂论文里所有被省略的细节（初始化、warmup、weight decay、optimizer state），这是任何阅读都替代不了的训练。

---

## 3. 三遍法的实践要点

### 3.1 笔记怎么记

李沐本人在视频里推荐 **Notion 或 Obsidian**，理由是：① 都支持双向链接（论文 A 引用论文 B，点击就能跳过去）；② 都支持 Markdown，方便复制公式和代码；③ 都有移动端，地铁上能看。

**推荐的笔记模板**（一份笔记对应一篇精读论文）：

```markdown
# [论文标题] (年份)

## 元信息
- 作者：
- 机构：
- Venue：NeurIPS / ICML / ICLR / arXiv
- arXiv ID：xxxx.xxxxx
- 链接：https://arxiv.org/abs/xxxx.xxxxx
- 代码：https://github.com/...
- 读过日期：2026-MM-DD
- 阅读遍数：1 / 2 / 3

## 一句话总结
（用 30 个字以内说清楚这篇论文干了什么）

## 问题
- 作者要解决什么问题？
- 为什么之前的方法不够好？

## 方法
- 核心思想：
- 关键模块：（画图）
- 跟已有方法的区别：

## 实验
- 数据集：
- Baselines：
- 主要结果：
- Ablation 是否充分：

## 我的判断
- 真创新 / 小修补 / 刷榜：
- 局限性：
- 可以改进的方向：

## 关联论文
- 前作：
- 同期工作：
- 后续工作：
```

> 💡 **Obsidian 技巧**：用 `[[论文名]]` 双向链接 + `#cv/transformer` 标签体系，半年后你会拥有一张自己的"AI 论文知识图谱"。这比任何 PDF 管理软件都强大。

### 3.2 论文之间如何关联（Idea Tree）

不要孤立地读论文。**好论文总是嵌在一条研究脉络里**。读的时候要主动构建"家族树"：

```
        [Vaswani 2017 Transformer]
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
[BERT]    [GPT-1]    [ViT]
(2018)    (2018)    (2020)
    │         │         │
    ▼         ▼         ▼
[RoBERTa] [GPT-3]   [Swin / MAE]
(2019)    (2020)    (2021)
              │
              ▼
         [InstructGPT]
            (2022)
              │
              ▼
           [GPT-4]
            (2023)
```

构建 idea tree 的三个动作：

1. **向上找根**：读这篇论文时，作者反复引用的那篇"老论文"是什么？（比如读 BERT 时一定要回去读 Transformer）
2. **横向找对手**：同期发表的、解决同样问题的论文有哪些？（比如 BERT vs GPT vs RoBERTa）
3. **向下找延伸**：这篇论文之后被高频引用的论文做了什么改进？（用 Google Scholar 的 "Cited by" 功能）

> 💡 **工具推荐**：[Connected Papers](https://www.connectedpapers.com/) 输入一篇论文，自动生成它的"前作 + 同期 + 后续"图谱，是构建 idea tree 的最佳起点。

### 3.3 如何决定"读到什么程度"

**不是每篇都要读到第三遍**。决定深度的标准是"这篇论文对我接下来要做的事有多关键"：

| 我的角色 | 这篇论文对我 | 读到第几遍 |
|---|---|---|
| 工程师，要用这个方法 | 直接相关 | 第二遍 + 看 code |
| 工程师，了解趋势 | 间接相关 | 第一遍 + 看 video |
| 研究者，要做这个方向 | 直接相关 | 第三遍 + 复现 |
| 研究者，相关方向 | 间接相关 | 第二遍 |
| 学生，准备组会讲 | 要讲 | 第三遍（必须能讲） |
| 学生，准备面试 | 简历写过 | 第三遍（必须能答追问） |
| 任何人 | 完全无关 | 第一遍筛选后归档 |

> ⚠️ **常见误区**：很多人觉得"我读得不够多"。其实**读得多但读得浅** 比 **读得少但读得深** 危险得多——前者会让你产生"我懂了"的幻觉，后者至少让你知道自己不懂什么。

---

## 4. 不同类型论文的读法

不同类型的论文需要不同的"读法肌肉"。下面是李沐在 paper-reading 系列里反复示范的五种读法。

### 4.1 理论论文（数学重）

**典型代表**：
> 论文：[Transformer 中 Attention 的理论研究](https://arxiv.org/abs/2103.03404) [arXiv:2103.03404]
> 论文：[LayerNorm 的深入研究](https://arxiv.org/abs/1911.07013) [arXiv:1911.07013]

**读法**：
- **跟着推导走**：拿一支笔，把每一步推导都重写一遍。看不懂就停下来查。
- **必要时手动验证**：选一个最简单的例子（比如 2 维向量），手动跑一遍公式，看是不是真的成立。
- **抓住"假设"和"结论"之间的距离**：很多理论 paper 的结论在假设极强时才成立，但作者会用文字模糊处理。要问"这个假设在现实中成立吗？"

**陷阱**：理论 paper 的 abstract 经常夸张（"我们证明了 X"），但正文里的定理可能只在极特殊条件下成立。**永远看 theorem statement 和它的 assumptions**，不要被 abstract 带跑。

### 4.2 架构论文（如 Transformer）

**典型代表**：
> 论文：[Attention Is All You Need](https://arxiv.org/abs/1706.03762) [arXiv:1706.03762]（Vaswani et al., NeurIPS 2017）
> 论文：[ResNet](https://arxiv.org/abs/1512.03385) [arXiv:1512.03385]（He et al., CVPR 2016）
> 论文：[ViT](https://arxiv.org/abs/2010.11929) [arXiv:2010.11929]（Dosovitskiy et al., ICLR 2021）

**读法**：
- **画架构图**：合上论文，凭记忆画一遍。画不出来 = 没读懂。
- **自己复现**：用 PyTorch 写一个最小实现（哪怕只有 50 行），跑通一个玩具任务。李沐《动手学深度学习》的 PyTorch 版就是这种"复现驱动"的范本。
- **理解每个设计选择**：为什么用 multi-head 而不是 single-head？为什么用 LayerNorm 而不是 BatchNorm？为什么位置编码用 sinusoidal？每个选择都问一遍。

**这类论文第三遍的产出**：一份能跑通的最小代码 + 一份"如果去掉这个模块会怎样"的 ablation 思路。

### 4.3 实验论文（如 GPT-3）

**典型代表**：
> 论文：[Language Models are Few-Shot Learners (GPT-3)](https://arxiv.org/abs/2005.14165) [arXiv:2005.14165]（Brown et al., NeurIPS 2020）

**读法**：
- **精读实验设计**：用了什么数据？多少数据？多少卡？训了多久？这决定了你能不能判断结果是否可信。
- **细看评测协议**：few-shot 是怎么定义的？是 0-shot / 1-shot / 5-shot？prompt 是怎么写的？这种细节决定结果能不能复现。
- **质疑 baseline**：作者跟谁比的？是不是挑了弱的 baseline？（GPT-3 论文里很多 baseline 是 fine-tuned 的 BERT-large，参数量差了一个数量级——这是经典的"不公平比较"）
- **看 ablation 是否充分**：实验论文最怕没有 ablation。如果一篇"超大模型"论文没告诉你"小模型不行"，那它的核心主张（scaling law）就没被验证。

### 4.4 综述论文（Survey）

**典型代表**：
> 论文：[A Survey on Vision Transformer](https://arxiv.org/abs/2012.12556) [arXiv:2012.12556]
> 论文：[Chain-of-Thought Prompting 综述](https://arxiv.org/abs/2201.11903) [arXiv:2201.11903]（虽然不是综述，但 Li Mu 把它当综述讲）

**读法**：
- **先看 taxonomy 图**：好的综述一定会有一张"分类树"图，把领域分成几个子方向。这张图比正文重要 10 倍。
- **把综述当导航，不当终点**：综述是给你指路的，真正要读的是它引用的那些"叶子论文"。读完综述后，挑 3-5 篇核心引用去精读。
- **注意综述的时效性**：AI 综述半年就过时。读 2022 年的 Diffusion 综述，不如直接读 2024 年的 Sora 技术报告。

### 4.5 System 论文

**典型代表**：
> 论文：[Megatron-LM](https://arxiv.org/abs/1909.08053) [arXiv:1909.08053]（Shoeybi et al., 2019）
> 论文：[ZeRO: Memory Optimizations Toward Training Trillion Parameter Models](https://arxiv.org/abs/1910.02054) [arXiv:1910.02054]（Rajbhandari et al., 2020）
> 论文：[Pathways: Asynchronous Distributed Dataflow for ML](https://arxiv.org/abs/2203.12533) [arXiv:2203.12533]（Google, 2022）
> 论文：[Parameter Server](https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-li_mu.pdf)（Mu Li et al., OSDI 2014）⭐ 李沐本人的代表作

**读法**：
- **理解瓶颈**：System 论文的核心永远是"上一个系统的瓶颈在哪？我们怎么解决的？"。抓住这个主线。
- **看懂设计选择的 trade-off**：所有 system 设计都是 trade-off（用内存换时间、用一致性换吞吐）。要问"作者牺牲了什么换来了什么？"
- **看实验的硬件配置**：System 论文的结果高度依赖硬件。A100 上的结果不能直接推到 H100 上。
- **如果有开源实现，跑一下**：Megatron / DeepSpeed 都开源，在自己机器上跑个玩具任务，比读 10 遍论文都有用。

---

## 5. 李沐 paper-reading 67 篇必读清单（按主题分类）

下面是李沐在 [github.com/mli/paper-reading](https://github.com/mli/paper-reading) 维护的 **67 篇十年内必读论文**完整清单（截至 2025 年 1 月，已录制 50+ 期视频讲解）。选取原则是"**10 年内深度学习里有影响力的文章**"。

> 📺 **配套视频**：所有 ✅ 标记的论文，李沐本人都在 B 站 / YouTube 录制了 30 分钟到 1.5 小时的逐段精讲。**强烈建议先看视频再读论文**——李沐的精读会把论文里被省略的背景、动机、设计权衡全部补齐。

### 5.1 计算机视觉 - CNN 奠基

| 年份 | 论文 | arXiv / Venue | 一句话 |
|---|---|---|---|
| ✅ 2012 | [AlexNet](https://papers.nips.cc/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf) | NIPS 2012 | 深度学习热潮的奠基作，GPU 训练 + ReLU + Dropout |
| 2014 | [VGG](https://arxiv.org/abs/1409.1556) | [arXiv:1409.1556](https://arxiv.org/abs/1409.1556) | 用 3×3 卷积构造更深的网络，证明"深度有用" |
| 2014 | [GoogLeNet / Inception](https://arxiv.org/abs/1409.4842) | [arXiv:1409.4842](https://arxiv.org/abs/1409.4842) | 用并行架构（Inception module）构造更深的网络 |
| ✅ 2015 | [ResNet](https://arxiv.org/abs/1512.03385) | [arXiv:1512.03385](https://arxiv.org/abs/1512.03385) | **撑起 CV 半边天**的残差连接，训到 152 层 |
| 2017 | [MobileNet](https://arxiv.org/abs/1704.04861) | [arXiv:1704.04861](https://arxiv.org/abs/1704.04861) | 适合终端设备的小 CNN，depthwise separable conv |
| 2019 | [EfficientNet](https://arxiv.org/abs/1905.11946) | [arXiv:1905.11946](https://arxiv.org/abs/1905.11946) | 通过 NAS（神经架构搜索）得到的 CNN，统一缩放 |
| 2021 | [Non-deep Networks](https://arxiv.org/abs/2110.07641) | [arXiv:2110.07641](https://arxiv.org/abs/2110.07641) | 让不深的网络也能在 ImageNet 刷到 SOTA（"ParNet"） |

### 5.2 计算机视觉 - Transformer 时代

| 年份 | 论文 | arXiv | 一句话 |
|---|---|---|---|
| ✅ 2020 | [ViT: An Image is Worth 16×16 Words](https://arxiv.org/abs/2010.11929) | [arXiv:2010.11929](https://arxiv.org/abs/2010.11929) | Transformer 杀入 CV 界，把图片切成 patch |
| ✅ 2021 | [Swin Transformer](https://arxiv.org/abs/2103.14030) | [arXiv:2103.14030](https://arxiv.org/abs/2103.14030) | 多层次的 Vision Transformer，引入 shifted window |
| 2021 | [MLP-Mixer](https://arxiv.org/abs/2105.01601) | [arXiv:2105.01601](https://arxiv.org/abs/2105.01601) | 用 MLP 替换 self-attention，"够简单所以够好" |
| ✅ 2021 | [MAE: Masked Autoencoders Are Scalable Vision Learners](https://arxiv.org/abs/2111.06377) | [arXiv:2111.06377](https://arxiv.org/abs/2111.06377) | BERT 的 CV 版，何恺明回归 CV |

### 5.3 生成模型（GAN → Diffusion → 视频）

| 年份 | 论文 | arXiv / Venue | 一句话 |
|---|---|---|---|
| ✅ 2014 | [GAN: Generative Adversarial Nets](https://papers.nips.cc/paper/2014/file/5ca3e9b122f61f8f06494c97b1afccf3-Paper.pdf) | NIPS 2014 | 生成模型的开山之作，generator vs discriminator |
| 2015 | [DCGAN](https://arxiv.org/abs/1511.06434) | [arXiv:1511.06434](https://arxiv.org/abs/1511.06434) | 用 CNN 的 GAN，第一次生成高质量图 |
| 2016 | [pix2pix](https://arxiv.org/abs/1611.07004) | [arXiv:1611.07004](https://arxiv.org/abs/1611.07004) | Image-to-image translation 的开山 |
| 2016 | [SRGAN](https://arxiv.org/abs/1609.04802) | [arXiv:1609.04802](https://arxiv.org/abs/1609.04802) | 图片超分辨率 |
| 2017 | [WGAN](https://arxiv.org/abs/1701.07875) | [arXiv:1701.07875](https://arxiv.org/abs/1701.07875) | 用 Wasserstein 距离让 GAN 训练更稳定 |
| 2017 | [CycleGAN](https://arxiv.org/abs/1703.10593) | [arXiv:1703.10593](https://arxiv.org/abs/1703.10593) | 无监督 image-to-image，马变骆驼的经典 demo |
| 2018 | [StyleGAN](https://arxiv.org/abs/1812.04948) | [arXiv:1812.04948](https://arxiv.org/abs/1812.04948) | 控制"风格"的生成器 |
| 2019 | [StyleGAN2](https://arxiv.org/abs/1912.04958) | [arXiv:1912.04958](https://arxiv.org/abs/1912.04958) | 修掉 StyleGAN 的伪影 |
| 2020 | [DDPM](https://arxiv.org/abs/2006.11239) | [arXiv:2006.11239](https://arxiv.org/abs/2006.11239) | **Diffusion Models** 的现代化开山 |
| 2021 | [Improved DDPM](https://arxiv.org/abs/2102.09672) | [arXiv:2102.09672](https://arxiv.org/abs/2102.09672) | 改进的 DDPM |
| 2021 | [Diffusion Models Beat GANs](https://arxiv.org/abs/2105.05233) | [arXiv:2105.05233](https://arxiv.org/abs/2105.05233) | classifier guidance 让 diffusion 超越 GAN |
| 2021 | [StyleGAN3](https://arxiv.org/abs/2106.12423) | [arXiv:2106.12423](https://arxiv.org/abs/2106.12423) | 解决"纹理粘贴"问题 |
| ✅ 2022 | [DALL·E 2](https://arxiv.org/abs/2204.06125) | [arXiv:2204.06125](https://arxiv.org/abs/2204.06125) | CLIP + Diffusion，文本生成图像新高度 |
| ✅ 2024 | [Sora](https://openai.com/index/video-generation-models-as-world-simulators/) | OpenAI blog | 开启视频生成热潮，"世界模拟器"叙事 |
| ✅ 2024 | [Movie Gen](https://arxiv.org/abs/2410.13720) | [arXiv:2410.13720](https://arxiv.org/abs/2410.13720) | Meta 的精确文本指导视频编辑 |
| ✅ 2025 | [HunyuanVideo](https://arxiv.org/abs/2412.03603) | [arXiv:2412.03603](https://arxiv.org/abs/2412.03603) | 开源视频生成框架（腾讯混元） |

### 5.4 目标检测（Object Detection）

| 年份 | 论文 | arXiv | 一句话 |
|---|---|---|---|
| 2014 | [R-CNN](https://arxiv.org/abs/1311.2524) | [arXiv:1311.2524](https://arxiv.org/abs/1311.2524) | Two-stage 检测的开山 |
| 2015 | [Fast R-CNN](https://arxiv.org/abs/1504.08083) | [arXiv:1504.08083](https://arxiv.org/abs/1504.08083) | 把 R-CNN 加速 100× |
| 2015 | [Faster R-CNN](https://arxiv.org/abs/1506.01497) | [arXiv:1506.01497](https://arxiv.org/abs/1506.01497) | 引入 RPN，端到端检测 |
| 2016 | [SSD](https://arxiv.org/abs/1512.02325) | [arXiv:1512.02325](https://arxiv.org/abs/1512.02325) | Single-stage 检测 |
| 2016 | [YOLO](https://arxiv.org/abs/1506.02640) | [arXiv:1506.02640](https://arxiv.org/abs/1506.02640) | 实时检测的开山 |
| 2017 | [Mask R-CNN](https://arxiv.org/abs/1703.06870) | [arXiv:1703.06870](https://arxiv.org/abs/1703.06870) | 检测 + 分割 |

### 5.5 对比学习（Contrastive Learning）

| 年份 | 论文 | arXiv | 一句话 |
|---|---|---|---|
| ✅ 2019 | [MoCo: Momentum Contrast](https://arxiv.org/abs/1911.05722) | [arXiv:1911.05722](https://arxiv.org/abs/1911.05722) | 何恺明组，把对比学习推向大规模 |
| 2020 | [SimCLR](https://arxiv.org/abs/2002.05709) | [arXiv:2002.05709](https://arxiv.org/abs/2002.05709) | Google 的对比学习，简单但有效 |
| ✅ 2021 | [对比学习综述串讲](https://www.bilibili.com/video/BV19S4y1M7hm/) | 视频 | 李沐 1.5 小时把 MoCo/SimCLR/BYOL/SimSiam 一锅端 |

### 5.6 多模态

| 年份 | 论文 | arXiv | 一句话 |
|---|---|---|---|
| ✅ 2021 | [CLIP: Learning Transferable Visual Models](https://arxiv.org/abs/2103.00020) | [arXiv:2103.00020](https://arxiv.org/abs/2103.00020) | 4 亿图文对训练，开启多模态时代 |
| ✅ 2021 | [ViLT](https://arxiv.org/abs/2102.03334) | [arXiv:2102.03334](https://arxiv.org/abs/2102.03334) | 去掉 region feature 的极简多模态 |
| ✅ 2022 | [DALL·E 2](https://arxiv.org/abs/2204.06125) | [arXiv:2204.06125](https://arxiv.org/abs/2204.06125) | CLIP + Diffusion（同 5.3） |
| ✅ 2022 | [多模态论文串讲 上/下](https://www.bilibili.com/video/BV1Vd4y1v77v/) | 视频 | 李沐把 ViLBERT→CLIP→DALL·E 串成一条线 |

### 5.7 视频理解

| 年份 | 论文 | arXiv / Venue | 一句话 |
|---|---|---|---|
| ✅ 2014 | [Two-Stream Networks](https://proceedings.neurips.cc/paper/2014/file/00ec53c4682d36f5c4359f4ae7bd7ba1-Paper.pdf) | NIPS 2014 | 空间流 + 时间流，视频理解奠基 |
| ✅ 2017 | [I3D](https://arxiv.org/abs/1705.07750) | [arXiv:1705.07750](https://arxiv.org/abs/1705.07750) | inflate 2D 到 3D 的巧思 |
| ✅ 2022 | [视频理解综述串讲 上/下](https://arxiv.org/abs/2012.06567) | [arXiv:2012.06567](https://arxiv.org/abs/2012.06567) | 李沐基于这篇综述做了 2 期视频 |

### 5.8 检测之外的其他 CV

| 年份 | 论文 | arXiv | 一句话 |
|---|---|---|---|
| ✅ 2020 | [DETR: End-to-End Object Detection with Transformers](https://arxiv.org/abs/2005.12872) | [arXiv:2005.12872](https://arxiv.org/abs/2005.12872) | 把检测变成 set prediction，去掉 NMS |
| ✅ 2021 | [GNN 综述（distill.pub）](https://distill.pub/2021/gnn-intro/) | distill.pub | 零基础多图详解 GNN/GCN |

### 5.9 大语言模型（核心，从 GPT 到 Llama 3.1）

| 年份 | 论文 | arXiv / Venue | 一句话 |
|---|---|---|---|
| ✅ 2018 | [GPT-1: Improving Language Understanding by Generative Pre-Training](https://s3-us-west-2.amazonaws.com/openai-assets/research-covers/language-unsupervised/language_understanding_paper.pdf) | OpenAI blog | 预训练 + fine-tune 范式确立 |
| ✅ 2019 | [GPT-2: Language Models are Unsupervised Multitask Learners](https://d4mucfpksywv.cloudfront.net/better-language-models/language_models_are_unsupervised_multitask_learners.pdf) | OpenAI blog | zero-shot，"足够大的 LM 就是多任务学习器" |
| ✅ 2020 | [GPT-3: Language Models are Few-Shot Learners](https://arxiv.org/abs/2005.14165) | [arXiv:2005.14165](https://arxiv.org/abs/2005.14165) | 175B 参数，in-context learning 震惊世界 |
| ✅ 2018 | [BERT: Pre-training of Deep Bidirectional Transformers](https://arxiv.org/abs/1810.04805) | [arXiv:1810.04805](https://arxiv.org/abs/1810.04805) | encoder-only，MLM 任务，NLP 刷榜神器 |
| ✅ 2022 | [InstructGPT: Training language models to follow instructions](https://arxiv.org/abs/2203.02155) | [arXiv:2203.02155](https://arxiv.org/abs/2203.02155) | RLHF 工程化，ChatGPT 的真正技术基础 |
| ✅ 2023 | [GPT-4 Technical Report](https://arxiv.org/abs/2303.08774) | [arXiv:2303.08774](https://arxiv.org/abs/2303.08774) | 多模态，但仍大量细节未公开 |
| ✅ 2022 | [Anthropic: A General Language Assistant as a Laboratory for Alignment](https://arxiv.org/abs/2204.05862) | [arXiv:2204.05862](https://arxiv.org/abs/2204.05862) | Anthropic 早期对齐研究 |
| ✅ 2022 | [HELMS: Holistic Evaluation of Language Models](https://arxiv.org/abs/2211.09110) | [arXiv:2211.09110](https://arxiv.org/abs/2211.09110) | 全面语言模型评测框架 |
| ✅ 2022 | [Chain-of-Thought Prompting](https://arxiv.org/abs/2201.11903) | [arXiv:2201.11903](https://arxiv.org/abs/2201.11903) | "Let's think step by step"，推理能力涌现 |
| ✅ 2024 | [Llama 3.1 Herd of Models](https://arxiv.org/abs/2407.21783) | [arXiv:2407.21783](https://arxiv.org/abs/2407.21783) | Meta 开源 405B，李沐分 5 期精读（数据/模型/infra/训练/总结） |

### 5.10 系统与训练（System）

| 年份 | 论文 | arXiv / Venue | 一句话 |
|---|---|---|---|
| ✅ 2014 | [Parameter Server](https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-li_mu.pdf) | OSDI 2014 | **李沐本人的代表作**，分布式 ML 的基础设施 |
| ✅ 2019 | [Megatron-LM](https://arxiv.org/abs/1909.08053) | [arXiv:1909.08053](https://arxiv.org/abs/1909.08053) | 层内模型并行（tensor parallel） |
| ✅ 2019 | [GPipe](https://proceedings.neurips.cc/paper/2019/file/093f65e080a295f8076b1c5722a46aa2-Paper.pdf) | NeurIPS 2019 | 流水线并行 |
| ✅ 2020 | [ZeRO](https://arxiv.org/abs/1910.02054) | [arXiv:1910.02054](https://arxiv.org/abs/1910.02054) | DeepSpeed 的核心，把 optimizer state 切片 |
| ✅ 2022 | [Pathways](https://arxiv.org/abs/2203.12533) | [arXiv:2203.12533](https://arxiv.org/abs/2203.12533) | Google 的异步分布式数据流，PaLM 的训练底座 |

### 5.11 检索与代码生成

| 年份 | 论文 | arXiv / Venue | 一句话 |
|---|---|---|---|
| ✅ 2022 | [Neural Corpus Indexer (NCI)](https://arxiv.org/abs/2206.02743) | [arXiv:2206.02743](https://arxiv.org/abs/2206.02743) | 用生成式模型做文档检索 |
| ✅ 2022 | [Whisper](https://cdn.openai.com/papers/whisper.pdf) | OpenAI blog | 68 万小时多语言 ASR，鲁棒性强 |
| ✅ 2022 | [Codex](https://arxiv.org/abs/2107.03374) | [arXiv:2107.03374](https://arxiv.org/abs/2107.03374) | GitHub Copilot 背后的模型 |
| ✅ 2022 | [AlphaCode](https://storage.googleapis.com/deepmind-media/AlphaCode/competition_level_code_generation_with_alphacode.pdf) | Science 2022 / DeepMind blog | 竞赛级代码生成 |

### 5.12 AI4Science 标杆

| 年份 | 论文 | Venue | 一句话 |
|---|---|---|---|
| ✅ 2021 | [AlphaFold 2](https://www.nature.com/articles/s41586-021-03819-2.pdf) | Nature 596:583-589 | 蛋白质结构预测，DeepMind 封神之作 |
| ✅ 2021 | [指导数学直觉（DeepMind + Topology）](https://www.nature.com/articles/s41586-021-04086-x) | Nature 600:70-74 | 用 ML 帮数学家发现新定理（纽结理论 + 表示论） |
| ✅ 2022 | [Stanford AI Index 2022](https://aiindex.stanford.edu/wp-content/uploads/2022/03/2022-AI-Index-Report_Master.pdf) | Stanford HAI | 年度 AI 全景报告，必读 |

### 5.13 方法论与研究方法（李沐本人的研究哲学）

这部分**比论文本身更重要**——它是李沐本人作为资深研究者（Amazon Principle Scientist、MXNet/D2L 作者）对"怎么做研究"的元反思。

| 日期 | 视频 | BV 号 | 一句话 |
|---|---|---|---|
| 2021-10-06 | **如何读论文** | [BV1H44y1t75x](https://www.bilibili.com/video/BV1H44y1t75x/) | **本文的核心方法来源**，三遍法 6 分 39 秒讲完 |
| 2021-12-09 | 如何找研究想法 1（MAE 案例） | [BV1qq4y1z7F2](https://www.bilibili.com/video/BV1qq4y1z7F2/) | 用 MAE 示范"如何从一个 idea 长成一篇论文" |
| 2022-01-18 | 如何判断（你自己的）研究价值 | [BV1oL411c7Us](https://www.bilibili.com/video/BV1oL411c7Us/) | 9 分 59 秒短讲，4 条标准 |
| 2022-02-06 | 论文不够 novel 怎么办 | [BV1ea41127Bq](https://www.bilibili.com/video/BV1ea41127Bq/) | 14 分钟谈"什么是真正的 novelty" |
| 2022-03-23 | 大模型时代下做科研的四个思路 | [BV1oX4y1d7X6](https://www.bilibili.com/video/BV1oX4y1d7X6/) | **强推**：算力有限的人怎么活下来 |
| 2022-06-24 ~ 07-22 | **研究的艺术** 四讲（基于 Booth 等《The Craft of Research》） | [BV1hY411T7vy](https://www.bilibili.com/video/BV1hY411T7vy/) 起 | 跟读者建立联系 / 问题的重要性 / 讲故事 / 理由论据担保 |

> 💡 **建议入门顺序**：先看《如何读论文》（6 分钟）→ 看《如何判断研究价值》（10 分钟）→ 看《大模型时代下做科研》（1 小时）→ 再开始读 67 篇里的第一篇。这三段视频加起来不到 1.5 小时，但会让你后面 100 小时的阅读效率翻倍。

---

## 6. AI 论文的常见"套路"识别

读多了你会发现，AI 论文（尤其是非顶级 venue 的论文）有大量模板化的"话术"。识别这些套路是研究者必备的品味训练。

### 6.1 "First to..." 句式：小心 marketing

```
"We are the first to ..."
"To the best of our knowledge, this is the first work that ..."
```

**问题**：这个句式几乎一定会出现在 intro 里，而且经常是错的。作者说"first"是因为他没搜到——不等于没人做过。看到这种句子，**第一反应是去 Google Scholar 搜关键词**，70% 的情况你能找到前作。

**应对**：把"first"读成"novel in some specific sense"，然后看作者具体在什么意义上 novel。

### 6.2 SOTA 刷榜的"小技巧"

很多"SOTA"是工程努力堆出来的，不是方法创新。常见的"刷榜 trick"：

| Trick | 表现 | 危险 |
|---|---|---|
| **数据筛选** | 训练集经过精心清洗/筛选 | 在干净数据上有效 ≠ 在真实数据上有效 |
| **超参搜索** | 在测试集上 grid search 选超参 | 测试集变成验证集，结果不可复现 |
| **大模型 + 强 trick** | 用更大模型 + longer training + label smoothing | 跟小模型 + 没 trick 比不公平 |
| **挑弱 baseline** | 跟 3 年前的模型比 | 没跟同期 SOTA 比 |
| **挑有利指标** | 只报对自己有利的 metric | BLEU 高 ≠ 真的好 |

**应对**：看到 SOTA，先问 4 个问题：
1. **跟谁比的？** 同期 SOTA 是什么？
2. **在什么数据集上？** 这个数据集是公认的吗？
3. **用了多少算力？** 同等算力下还能赢吗？
4. **ablation 充分吗？** 哪个模块贡献了主要提升？

### 6.3 Ablation 缺失 = 警惕

**没有 ablation 的论文几乎一定有问题**。Ablation 是"去掉某个模块看性能掉多少"，是验证"这个模块真的有用"的唯一手段。

警惕信号：
- 整篇论文只有一个主表，没有 ablation 表
- Ablation 只去掉无关紧要的模块（比如 dropout）
- Ablation 的结果"恰好"都支持主张，没有意外

> 💡 **李沐判断论文价值的标准之一**：「一篇好的论文，ablation 表往往比主表还有意思——因为它告诉你哪些设计真的重要，哪些是装饰。」

### 6.4 Baseline 弱 = 警惕

**作者挑 baseline 时有强烈的动机挑弱的**。常见手段：

- 跟 3-5 年前的旧模型比（不动用同期 SOTA）
- 跟没有 fine-tune 的 baseline 比
- 跟用更少数据训的 baseline 比
- 跟用更少算力训的 baseline 比
- 跟作者自己重新实现（且故意没调好）的 baseline 比

**应对**：去 [Papers With Code](https://paperswithcode.com/) 查这个任务的当前 SOTA，跟论文里的 baseline 对比。如果论文的 baseline 比 Papers With Code 上的中位数还低，就要警惕。

### 6.5 "Outperforms by X%"：分母是什么？

```
"Our method outperforms the previous SOTA by 15%."
```

**问题**：15% 是相对提升还是绝对提升？如果是相对提升，分母是什么？

举例：
- 错误率从 20% → 17%，作者会说"降低 15%"（相对），但绝对只降了 3 个点。
- BLEU 从 30 → 34.5，"提升 15%"（相对），但人感知可能没差别。

**应对**：永远问"绝对值是多少"。Absolute improvement 才是有意义的指标。

### 6.6 "Demonstrate" / "Show" 的真假

```
"We demonstrate that our method generalizes to ..."
```

**问题**：在 1-2 个数据集上"show"不等于"demonstrate generalize"。真正的泛化需要：① 多个数据集；② 多个分布（in-distribution + OOD）；③ 多个 seed。

**应对**：数实验设置的数量。如果一篇论文从头到尾就在 1 个数据集上做实验，它的所有"generalize"主张都要打折。

---

## 7. 如何判断论文质量

### 7.1 五个维度评分卡

读到第二遍结束时，给这篇论文打一个分（0-5 分），加权得出总体判断：

| 维度 | 权重 | 0 分 | 5 分 |
|---|---|---|---|
| **Novelty（新颖性）** | 25% | 完全是已有方法的重新组合 | 提出全新的范式 |
| **Significance（重要性）** | 25% | 没人会在意 | 改变了子领域的方向 |
| **Soundness（严谨性）** | 25% | 实验有明显漏洞 | ablation 充分，baseline 公平 |
| **Reproducibility（可复现）** | 15% | 无代码、缺关键超参 | 开源代码 + 详细 readme + 复现脚本 |
| **Clarity（清晰度）** | 10% | 读完不知道在讲什么 | 一遍读懂 |

**总分参考**：
- 4.0+ ：必精读，影响你的研究方向
- 3.0-4.0：值得读，但你不必复现
- 2.0-3.0：扫一眼就行
- < 2.0：别浪费时间

### 7.2 作者声誉：necessary but not sufficient

**顶级作者（如 Hinton, LeCun, Bengio, He Kaiming, Vaswani, Sutton）的论文默认可信度更高**，但**不等于**一定好。即使是图灵奖得主也会发一般的论文。反过来，**没有名气的作者也能写出开山之作**——Attention Is All You Need 发表时，8 位作者都不是顶级大佬。

**作者声誉的真正用法**：当你在两个矛盾结论之间犹豫时，倾向于相信声誉更好的作者。但当证据足够时，证据优先于声誉。

### 7.3 Venue：NeurIPS / ICML / ICLR > arXiv，但顶级 arXiv 也很重要

AI 顶级会议排名（按 2024 年共识）：

| Tier | Venue | 备注 |
|---|---|---|
| **顶会** | NeurIPS, ICML, ICLR | ML 三大顶会，录用率 20-26% |
| **顶会** | CVPR, ICCV, ECCV | CV 三大顶会 |
| **顶会** | ACL, EMNLP, NAACL | NLP 三大顶会 |
| **顶会** | AAAI, IJCAI | 综合 AI，质量参差 |
| **期刊** | JMLR, TPAMI, TMLR | JMLR/TPAMI 顶级，TMLR 是开放审稿的新期刊 |
| **预印本** | arXiv | **重要**：顶级 arXiv（如 OpenAI/DeepMind/Anthropic/Meta 的技术报告）比一般会议论文更有影响力 |

**关键认知**：**大模型时代之后，arXiv 的权重急剧上升**。GPT-4、Sora、Claude 都只在 arXiv / blog 发，从未投会议。**只看 venue 已经不够了**，要看作者机构 + 引用增速 + 社区讨论热度。

### 7.4 引用数与下载量

引用数是滞后指标（一篇论文发表 2-3 年后引用才达到高峰），但对**老论文**（发表 3 年以上）很有参考价值：

- 引用 > 10000：经典（AlexNet, ResNet, Transformer, BERT, GPT-3）
- 引用 1000-10000：领域内有影响
- 引用 100-1000：值得读
- 引用 < 100（且发表 > 2 年）：可能小众，可能不好

**对新论文**（发表 < 1 年），看 **arXiv 月下载量**和 **Twitter/HackerNews 讨论热度**。可以用 [arxiv-sanity](http://arxiv-sanity-lite.com/) 或 [HuggingFace Papers](https://huggingface.co/papers) 看趋势。

### 7.5 GitHub stars 与 issue 活跃度

| 信号 | 含义 |
|---|---|
| 有官方 repo，star > 1000 | 实现靠谱，社区认可 |
| repo 有近期 commit | 仍在维护，bug 会被修 |
| issue 区有作者回复 | 作者在乎复现，可信度高 |
| 无 repo 或 repo 是空的 | 复现难度大，谨慎 |
| 第三方复现失败 | 论文可能有未公开的 trick |

### 7.6 ⭐ 复现难易度：最重要的指标

**这是李沐反复强调的**。一篇论文真正的质量，最终要靠"你能不能复现"来检验。

- **复现成功** = 你独立跑出了论文报告的数字（误差 5% 以内）
- **复现失败**的常见原因：
  1. 关键超参没写（learning rate warmup 多长？weight decay 多少？）
  2. 数据预处理 trick 没写（resize 还是 random crop？哪种 augmentation？）
  3. 初始化策略没写
  4. 评测协议不一致（few-shot 的 K 怎么取？）
  5. 硬件依赖（在 A100 上训的，你用 V100 复现不出来）

**经验**：**顶级论文（ResNet, BERT, Transformer）几乎都能被独立复现**。**复现不出来的论文，无论 abstract 多漂亮，价值都要打折**。

---

## 8. 论文阅读工具链（2026 推荐）

### 8.1 发现层（怎么找到要读的论文）

| 工具 | 链接 | 用途 |
|---|---|---|
| **arXiv** | [arxiv.org](https://arxiv.org/) | 论文源头，订阅 RSS / mailing list |
| **arxiv-sanity-preserver / arxiv-sanity-lite** | [arxiv-sanity-lite.com](http://arxiv-sanity-lite.com/) | Karpathy 写的，按你的兴趣推荐 arXiv 论文 |
| **HuggingFace Papers** | [huggingface.co/papers](https://huggingface.co/papers) | 每日热门论文，社区 upvote 排序 |
| **AK / Yannic Kilcher YouTube** | AK: [@akhaliq](https://twitter.com/akhaliq) | 第一时间讲解最新论文 |
| **Twitter ML 圈** | 关注 @karpathy, @_akhaliq, @_philschmid, @clefourrier | 大佬们讨论最热的论文 |
| **机器之心 / PaperWeekly** | 微信公众号 | 中文 AI 资讯，比英文晚 1-3 天 |

### 8.2 关系层（怎么理解论文之间的关系）

| 工具 | 链接 | 用途 |
|---|---|---|
| **Semantic Scholar** | [semanticscholar.org](https://www.semanticscholar.org/) | Allen AI 出品，比 Google Scholar 更适合 AI 论文；有 API |
| **Connected Papers** | [connectedpapers.com](https://www.connectedpapers.com/) | 输入一篇论文，生成"前作 + 同期 + 后续"图谱 |
| **Research Rabbit** | [researchrabbitapp.com](https://www.researchrabbitapp.com/) | 类似 Connected Papers，但支持订阅 |
| **Inciteful** | [inciteful.xyz](https://inciteful.xyz/) | 输入 2 篇论文，找它们共同的"桥接论文" |
| **Google Scholar "Cited by"** | [scholar.google.com](https://scholar.google.com/) | 找一篇论文的所有后续工作 |

### 8.3 AI 辅助阅读层（2024 之后的新工具）

| 工具 | 链接 | 用途 | 注意 |
|---|---|---|---|
| **SciSpace (Typeset.io)** | [typeset.io](https://typeset.io/) | 上传 PDF，AI 解释公式、术语 | 公式解释有幻觉，需核对原文 |
| **Elicit** | [elicit.com](https://elicit.com/) | 用自然语言问论文问题 | 适合做 survey，不适合精读 |
| **Consensus** | [consensus.app](https://consensus.app/) | 搜索论文库找共识 | 偏学术综述 |
| **ChatPDF / Claude / Gemini** | 上传 PDF 直接问 | 解释、翻译、摘要 | **关键**：让 AI 解释后，**必须回到原文核对**，AI 会编造 |
| **NotebookLM** | [notebooklm.google.com](https://notebooklm.google.com/) | 上传多篇论文，做交叉问答 | Google 出品，免费 |

> ⚠️ **AI 辅助阅读的边界**：AI 适合做"翻译 / 解释术语 / 总结要点"，**不适合做"判断论文质量 / 推导公式 / 复现实验"**。把 AI 当成"高级 Google"，不要当成"导师"。

### 8.4 笔记与管理层

| 工具 | 链接 | 用途 |
|---|---|---|
| **Notion** | [notion.so](https://www.notion.so/) | 推荐：富文本 + 数据库 + 双向链接 |
| **Obsidian** | [obsidian.md](https://obsidian.md/) | 推荐：本地 Markdown + 强大插件生态 + 知识图谱 |
| **Logseq** | [logseq.com](https://logseq.com/) | 大纲式，适合快速记 |
| **Zotero** | [zotero.org](https://www.zotero.org/) | **必装**：文献管理 + 浏览器插件一键存 PDF + 自动提取元数据 |
| **Readwise Reader** | [readwise.io/read](https://readwise.io/read) | 阅读 + 高亮 + 笔记同步 |

**李沐推荐组合**：Zotero（管理 PDF）+ Obsidian / Notion（记笔记）+ Connected Papers（找关系）。

### 8.5 实现层

| 工具 | 链接 | 用途 |
|---|---|---|
| **Papers With Code** | [paperswithcode.com](https://paperswithcode.com/) | 论文 + 代码 + SOTA 排行榜，**必看** |
| **HuggingFace Hub** | [huggingface.co](https://huggingface.co/) | 模型权重 + datasets + demos |
| **GitHub** | 直接搜论文名 | 找官方/第三方实现 |
| **labml.ai annotated** | [nn.labml.ai](https://nn.labml.ai/) | PyTorch 实现带详细注释，学复现的范本 |

---

## 9. 从读到写：基于阅读的研究 idea 生成

读论文的终极目的是产出你自己的研究。李沐在《如何找研究想法 1》（[BV1qq4y1z7F2](https://www.bilibili.com/video/BV1qq4y1z7F2/)）里用 MAE 示范了"idea 怎么从读论文中长出来"。下面是三个生成 idea 的常用套路。

### 9.1 "缝隙法"：读 10 篇同主题论文，找没人做的角落

**操作**：
1. 选定一个你感兴趣的方向（比如"长上下文 LLM"）
2. 在 arXiv 上找最近 12 个月的 10-15 篇代表论文
3. 每篇都用三遍法的"第二遍"读完，画一张"方法对比表"
4. 找到表里的"空白格"——某个维度上没人尝试过的组合

**例子**：你读 10 篇长上下文论文，发现 8 篇都在改 attention（sparse / linear / recurrent），但只有 2 篇在改位置编码。这就是一个"缝隙"——位置编码方向可能还有空间。

> 💡 **MAE 的诞生就是缝隙法**：李沐在视频里讲，何恺明读了一堆 contrastive learning（MoCo / SimCLR）论文后，发现"masked image modeling 在 CV 里几乎没人系统做过"（NLP 的 BERT 已经做了 3 年），这就是 MAE 的起点。

### 9.2 "时间机器法"：读 5 年前的论文，问"如果用今天的算力/数据"

**操作**：
1. 找一篇 5-10 年前被引用很高、但你以为"已经过时"的论文
2. 问自己：如果用今天（2026）的算力（H100 集群）、数据（Common Crawl 全量）、模型（10B+ 参数），这个方法会怎样？
3. 如果答案是"会变得很强"，那就是一个 idea

**例子**：
- 2017 年的 Transformer，到 2020 年的 GPT-3，本质就是"把 Transformer 放大到 175B"。
- 2014 年的 GAN，到 2022 年的 Stable Diffusion，本质是"把 diffusion（GAN 的远亲）放大到 LAION-5B 数据集"。

> 💡 **Karpathy 名言**："Most ideas in deep learning are 30 years old. The only thing that changed is compute and data."（深度学习里大多数 idea 都有 30 年历史，变的只是算力和数据。）

### 9.3 "跨界法"：看跨领域论文，问"这个方法能搬到我的领域吗"

**操作**：
1. 每月读 2-3 篇**你领域之外**的论文（比如你做 NLP，就读 CV / RL / System 的论文）
2. 问：这个方法的核心思想（不是具体实现）能搬到我的领域吗？
3. 如果能，第一个实验是什么？

**例子**：
- BERT 的 MLM 任务从 NLP 搬到 CV = MAE（何恺明）
- Transformer 从 NLP 搬到 CV = ViT
- RLHF 从游戏 AI 搬到 LLM = InstructGPT → ChatGPT
- 物理学里的扩散方程搬到生成模型 = Diffusion Models

**跨界法的优势**：竞争小（同领域的人都在看同样的论文），创新性强（搬过来就是新的）。

### 9.4 李沐的"四个研究思路"（大模型时代）

李沐在 2023 年 3 月《大模型时代下做科研的四个思路》（[BV1oX4y1d7X6](https://www.bilibili.com/video/BV1oX4y1d7X6/)）提出了算力有限的研究者的生存策略：

| 思路 | 描述 | 适合谁 |
|---|---|---|
| **① 做 benchmark / 分析** | 不训大模型，做评测、分析、解释 | 数学好、写作好的人 |
| **② 做 application** | 把大模型用到新领域（医疗、法律、科学） | 有领域知识的人 |
| **③ 做 efficient ML** | 用更少算力做到同样的事（量化、蒸馏、稀疏） | 系统能力强的人 |
| **④ 做 long-term bet** | 押注一个 5-10 年的方向（世界模型、具身智能） | 有耐心的博士生 |

> 💡 这四个思路都建立在"读了很多论文"之上——你必须先知道大模型能做什么、不能做什么，才能找到合适的切入点。

---

## 10. 论文精读范例：以 Transformer（1706.03762）为例

这一节用三遍法精读 **Attention Is All You Need**（Vaswani et al., NeurIPS 2017），演示完整流程。**这是过去十年最重要的 AI 论文，没有之一**——BERT / GPT / ViT / CLIP / Sora 全部建立在它之上。

> 论文：[Attention Is All You Need](https://arxiv.org/abs/1706.03762) [arXiv:1706.03762]
> 配套：李沐逐段精读 [BV1pu411o7BE](https://www.bilibili.com/video/BV1pu411o7BE/)（1 小时 27 分钟）

### 10.1 第一遍（5-10 分钟）

**Title**：Attention Is All You Need
→ "All you need" 暗示"不要 RNN, 不要 CNN, 只要 attention"——一个 bold 的主张。

**Abstract 关键句**：
- "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely."
- "WMT 2014 English-to-German translation: 28.4 BLEU, outperforming existing ensembles by over 2 BLEU."
- "63% / 85% of a single GPU"

**Intro 最后一段（contributions）**：
1. 提出 Transformer（首个纯 attention 序列模型）
2. 在翻译任务上 SOTA
3. 训练更快（并行化）

**图表扫一眼**：
- Figure 1（架构图）：encoder-decoder 结构，多头 attention，position-wise FFN
- Table 2（主结果）：Transformer big 28.4 BLEU，比之前最好的 ensemble 还高 2+

**第一遍判断**：✅ **必须读，且要精读**。这是奠基性论文。

### 10.2 第二遍（1-2 小时通读）

通读时建立以下心智模型：

**问题**：序列建模（翻译）当时主流是 RNN / LSTM / GRU + attention。RNN 的问题是**不能并行**——必须一步步算，所以训练慢。

**核心思想**：**完全抛弃 RNN，只用 attention**。
- Attention 本身就是"全局信息混合"，不需要序列递归
- 没有 RNN 的依赖链，可以**完全并行**
- 加上 positional encoding 注入位置信息

**关键模块**（合上论文你能否复述？）：

| 模块 | 作用 |
|---|---|
| **Scaled Dot-Product Attention** | 核心：Q × Kᵀ / √dₖ → softmax → × V |
| **Multi-Head Attention** | 并行 h 个 attention，再 concat |
| **Positional Encoding** | sin/cos 函数注入位置信息 |
| **Position-wise Feed-Forward** | 每个 position 独立的 2 层 MLP |
| **Encoder（×6）** | self-attention + FFN，每个子层残差 + LayerNorm |
| **Decoder（×6）** | masked self-attention + cross-attention + FFN |

**实验**：WMT 2014 英德/英法翻译任务，跟当时 SOTA 的 ensemble 比，BLEU 高 2+。训练时间从几天降到 12 小时（8 P100 GPU）。

**Related Work**：把这篇放在"attention 作为独立模块"的脉络里（Bahdanau 2014, Luong 2015 等），核心创新是"完全用 attention，不要别的"。

**圈出不懂的术语 / 待查引用**：
- "scaled dot-product"——为什么除以 √dₖ？（第三遍要查）
- "label smoothing"——是什么？（第三方 trick）
- "byte-pair encoding"——子词切分
- 引用 [3] Bahdanau 2014 additive attention——前置论文，要读

**第二遍判断**：✅ **必须精读到第三遍**。这是后续所有 LLM 的基础。

### 10.3 第三遍（数小时-数天，脑内复现）

逐个回答第三遍的 7 个问题：

#### Q1：作者解决什么问题？
神经机器翻译（NMT）里 RNN/LSTM 训练慢（顺序依赖，无法并行）。即使有 attention，attention 也只是 RNN 顶上的"装饰"。

#### Q2：为什么之前没被解决？
- RNN 是 NLP 主流，没人敢完全去掉它
- Attention 一直被当成"辅助模块"，没人想过它能独立撑起整个模型
- positional encoding 之前没人系统地用过

#### Q3：每一个设计选择，为什么？

| 选择 | 理由 |
|---|---|
| **除以 √dₖ** | 防止内积过大导致 softmax 进入饱和区（梯度消失）。具体推导见原论文 3.2.1 脚注 |
| **Multi-Head（h=8）** | 单头 attention 只能学一种"关系"，多头能同时学多种（类似 CNN 的多通道） |
| **Positional Encoding 用 sin/cos** | 相对位置可学、可外推到更长序列 |
| **Encoder self-attention** | 每个 token 能直接看到所有 token，不像 RNN 要传递 |
| **Decoder masked attention** | 防止"看到未来"，保证自回归 |
| **Cross-attention** | Decoder 用 encoder 的输出作为 K/V，是"翻译"发生的真正地方 |
| **6 层 encoder + 6 层 decoder** | 经验选择，太浅学不到深层特征，太深难训 |
| **LayerNorm + 残差** | 让深网络可训（ResNet 的遗产） |

#### Q4：实验设计公平吗？
- ✅ 数据集（WMT 2014）是公认基准
- ✅ 跟 ensemble 比（而不是单模型）——很自信
- ⚠️ BLEU 是机器翻译的指标，但翻译质量人感知差很多——这是 NMT 通病，不是这篇的问题
- ⚠️ 没测其他任务（如文本分类、问答）——但后续 BERT/GPT 都证明 Transformer 通用

#### Q5：结果支持主张吗？
- ✅ "outperforming by 2+ BLEU" 完全成立
- ✅ "训练快"完全成立（12 小时 vs 几天）
- ⚠️ 论文标题"All You Need"是夸张——后续发现 RNN/CNN 在某些任务上仍有优势（长序列、低资源），但 Transformer 在大多数情况下确实够用

#### Q6：局限性？
- **序列长度 O(n²)**：self-attention 的复杂度是序列长度的平方，长序列吃不消（催生了 Longformer / Linformer / Mamba）
- **位置编码外推差**：sin/cos 在训练长度之外效果不好（催生了 RoPE / ALiBi）
- **数据饥饿**：Transformer 比 RNN 更吃数据，小数据集上 RNN/LSTM 仍有竞争力
- **没有 inductive bias**：图像上不如 CNN（直到 ViT 用超大训练数据解决）

#### Q7：我能想到的改进方向？
（这是 2017 年读完时该问的，今天回看有些已被验证）
1. ✅ 降低 O(n²) 复杂度 → Longformer / Flash Attention（已实现）
2. ✅ 更好的位置编码 → RoPE（已实现）
3. ✅ 去掉 encoder-decoder 不对称 → decoder-only（GPT 系列，已实现）
4. ✅ 用到图像 → ViT（已实现）
5. ✅ 用到音频 → Whisper（已实现）
6. ❓ 用纯 attention 做 RL 的 world model？

**第三遍的产出**：
- ✅ 能合上论文凭记忆画架构图
- ✅ 能讲清楚每个模块的 why
- ✅ 能用 PyTorch 写一个 50 行的最小 Transformer（推荐看 [The Annotated Transformer](http://nlp.seas.harvard.edu/annotated-transformer/)）
- ✅ 能列出至少 5 个改进方向，且知道哪些已经被做

> 🎯 **检验**：如果你能做到上面 4 条，你才真正"读懂"了 Transformer。如果做不到，回去重读 + 看李沐视频。

---

## 11. 资源大全

### 11.1 论文精读视频系列（中文）

| 系列 | 作者 | 链接 | 特点 |
|---|---|---|---|
| **李沐 paper-reading** | 李沐（Amazon / D2L 作者） | [github.com/mli/paper-reading](https://github.com/mli/paper-reading) / B 站搜"李沐" | **本文核心**，67 篇必读，逐段精讲 |
| **跟李沐学 AI** | 李沐 | B 站频道 | 大量方法论短讲（研究的艺术 4 讲） |
| **Yannic Kilcher** | Yannic Kilcher | [YouTube](https://www.youtube.com/@YannicKilcher) | 英文，第一时间精读最新论文 |
| **AI Coffee Break with Letitia** | Letitia | [YouTube](https://www.youtube.com/@AICoffeeBreak) | 英文短讲，概念解释 |
| **李宏毅 ML 课** | 李宏毅（台大） | B 站 / YouTube | 系统课，配套论文讲解 |

### 11.2 论文与资讯订阅（中文 + 英文）

| 来源 | 类型 | 频率 |
|---|---|---|
| [HuggingFace Papers](https://huggingface.co/papers) | 每日热门 | 每日 |
| [AK @akhaliq](https://twitter.com/akhaliq) | Twitter | 每日（第一时间） |
| [The Batch (Andrew Ng)](https://www.deeplearning.ai/the-batch/) | Newsletter | 每周 |
| [Import AI (Jack Clark)](https://jack-clark.net/) | Newsletter | 每周 |
| [机器之心](https://www.jiqizhixin.com/) | 中文媒体 | 每日 |
| [PaperWeekly](https://www.paperweekly.site/) | 中文社区 | 每周 |
| [量子位](https://www.qbitai.com/) | 中文媒体 | 每日 |

### 11.3 工具速查

```
发现 ─→ arXiv + HuggingFace Papers + arxiv-sanity-lite
       │
关系 ─→ Semantic Scholar + Connected Papers + Research Rabbit
       │
精读 ─→ Zotero（管理）+ Obsidian/Notion（笔记）+ NotebookLM/SciSpace（AI 辅助）
       │
实现 ─→ Papers With Code + HuggingFace Hub + GitHub
```

### 11.4 必读书单（论文之外）

| 书 | 作者 | 用途 |
|---|---|---|
| **《动手学深度学习》** | 李沐 等 | [d2l.ai](https://d2l.ai/)，论文精读的代码基础 |
| **《The Craft of Research》** | Booth 等 | 李沐"研究的艺术"四讲的母本，研究方法论的圣经 |
| **《Deep Learning》** | Goodfellow 等 | "花书"，理论参考 |
| **《Dive into Deep Learning》交互版** | 同 D2L | 代码驱动的入门 |
| **《Designing Machine Learning Systems》** | Chip Huyen | ML 工程实践 |

---

## 📌 进一步阅读

1. **核心方法论短讲**（< 1 小时，强烈推荐先看）：
   - 李沐《如何读论文》[BV1H44y1t75x](https://www.bilibili.com/video/BV1H44y1t75x/)（6 分 39 秒）
   - 李沐《如何判断研究价值》[BV1oL411c7Us](https://www.bilibili.com/video/BV1oL411c7Us/)（9 分 59 秒）
   - 李沐《大模型时代下做科研的四个思路》[BV1oX4y1d7X6](https://www.bilibili.com/video/BV1oX4y1d7X6/)（1 小时）

2. **方法论原著**：
   - S. Keshav, "[How to Read a Paper](https://web.stanford.edu/class/ee384m/Project/List/reading.pdf)", ACM SIGCOMM CCR, 2007. 三遍法的原始出处。
   - Booth, Colomb, Williams, **《The Craft of Research》**, 4th ed., Univ. Chicago Press, 2016. 李沐"研究的艺术"四讲的母本。

3. **进阶精读**：
   - 本文同卷 `01-experiment-design.md`：如何设计能复现的实验。
   - 本文同卷 `02-reproducibility.md`：可复现性危机与对策。
   - 本文同卷 `04-llm-training-stack.md`：Llama 3.1 等大模型训练的工程细节（配合李沐 Llama 3.1 五期精读）。

4. **配套代码**：
   - [The Annotated Transformer](http://nlp.seas.harvard.edu/annotated-transformer/)：哈佛 NLP 用 PyTorch 逐行注释 Transformer，最好的复现教材。
   - [labml.ai annotated implementations](https://nn.labml.ai/)：大量论文的逐行注释 PyTorch 实现。

5. **AI 辅助阅读工具的边界**（2024-2025 讨论）：
   - 关于 LLM 在科研阅读中的幻觉问题，可参考 Science 杂志的多篇文章（搜 "ChatGPT scientific literature review hallucination"）。
   - **核心原则**：AI 辅助发现 + 解释，**判断必须由人来做**。

---

## ✍️ 思考题（5 道）

> 完成本文阅读后，用 30-60 分钟独立思考下面 5 个问题。建议把答案写进你的 Obsidian 笔记。

**1. 三遍法的"成本-收益"分析**
如果你每周有 5 小时读论文时间，按三遍法的分级（10 min / 2 h / 1 day），你应该分配为：第一遍 X 篇、第二遍 Y 篇、第三遍 Z 篇？请算出 X、Y、Z，并说明你的优先级原则。

**2. Abstract 是营销文案**
找一篇你最近读过的、abstract 让你很兴奋的论文（最好是 arXiv 上的）。重新读它的 method 和 experiment，列出 abstract 里**至少 3 个被夸大或被省略**的点。这一题训练你识别"套路"的肌肉。

**3. Transformer 第三遍**
合上本文和论文，**不看任何资料**，画出 Transformer 的完整架构图（encoder + decoder），并标注每个模块的输入输出维度。画不出来的部分，就是你还没懂的部分，回去重读。

**4. 跨界 idea 训练**
读一篇**你完全陌生领域**的论文（比如你做 NLP，就读 [AlphaFold 2](https://www.nature.com/articles/s41586-021-03819-2.pdf) 或 [GraphCast](https://www.science.org/doi/10.1126/science.adi2336)）。问自己：这篇论文的核心思想（不是具体方法）能搬到你的领域吗？写出 1 个具体的实验设计。

**5. 你自己的 67 篇**
李沐的 67 篇清单偏向 2014-2024 的 CV 和 NLP。如果你要为自己的子领域（比如 AI4Science / LLM 推理 / 多模态 / World Models）列一份"必读 20 篇"，你会选哪些？请给出清单 + 每篇一句话理由。这一题没有标准答案，但**完成它本身就是最好的学习**。

---

> **结语**：读论文是一种**复利技能**——前 10 篇会非常痛苦（每个术语都要查、每个公式都要推导），但读到第 50 篇时你会发现"套路开始浮现"，读到第 100 篇时你能"闻出论文的好坏"，读到第 300 篇时你已经能"看见整个领域的形状"。
>
> 李沐本人在视频里说过：「读论文就像练肌肉，没有捷径，但只要你坚持，6 个月后你会发现自己完全不一样了。」
>
> 从今天开始，挑一篇你感兴趣的，用三遍法读一遍。**Just start.**

<!-- delegate 直接写入，2026-07-20 -->
