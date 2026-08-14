# 01 · 数据获取与 Common Crawl：从原始网页到训练数据

> 承接 [00-数据是新的代码](./00-数据是新的代码.md)。00 章给出第一性问题：算力-数据必须同步增长，**数据墙先到**。但"数据"不是一个抽象概念——它从哪来、长什么样、怎么变成能喂给模型的 token 流？这一章把数据金字塔拆开，钻进最底层也最被低估的工程：**Common Crawl 清洗与数据质量评分**。
>
> 配套：[02-数据清洗与去重](./02-数据清洗与去重.md)（紧接本章的管线下游）+ [05-数据混合与配比](./05-数据混合与配比.md)（清洗完之后怎么配比）

---

## 直觉层

### 一个具体时刻

> 2023 年，Meta 的 LLaMA 团队在做一件事：训练一个能与 GPT-3 叫板的开源模型。预算有限，算力只有 OpenAI 的零头。团队负责人 Hugo Touvron 翻开 GPT-3 的论文，发现一个反直觉细节——GPT-3 用了 **1750 亿参数**，但训练数据只有 **300B tokens**，其中 60% 来自 Common Crawl。
>
> Touvron 的赌注是：**与其堆参数，不如把数据管线做透**。LLaMA 团队花了大半年时间，不是设计新架构，而是反复清洗 Common Crawl——去重、过滤低质、剔除 toxic、保留高质量子集。结果：LLaMA-7B（7B 参数 + 1T tokens）在多数 benchmark 上**超过 GPT-3 的 175B**。
>
> **角色**：你（数据工程师）。**冲突**：算力输在起跑线，唯一能赢的维度是数据质量。**时刻**：你看着 benchmark 曲线交叉的那一刻，意识到——**数据不是免费的，清洗掉 50% 反而是胜利**。

这就是本章要讲的：Common Crawl 这个"看起来无限"的数据源，**真正能用的部分远小于想象**，而"怎么挑出可用的部分"是一门没有统一理论的工程手艺。

### 为什么这是真问题

业界常说"Common Crawl 是 LLM 的石油"。但石油需要炼油——原油里只有 30-50% 能变成汽油。Common Crawl 同理：

- **HTML 噪声**：导航栏、广告、SEO 文本、机器翻译垃圾
- **重复**：同一篇文章被 N 个站点镜像，不去重等于浪费算力
- **毒性**：色情、仇恨、违法内容必须过滤
- **AI 生成垃圾**：2024 年起，CC 里开始大量混入低质 AI 生成内容（"AI slop"）

**不去清洗直接训，等于用脏油开车**——引擎会坏。

---

## 数学层

### 数据金字塔与质量评分

预训练数据按质量从高到低分层（[00 章](./00-数据是新的代码.md) 已给出金字塔），Common Crawl 处于**底座但低质**的位置：

```
                ┌────────────────┐
                │  代码/书籍/论文  │  高质量、稀缺（<5% 总量）
                ├────────────────┤
                │   维基/新闻     │  中等质量（10-20%）
                ├────────────────┤
                │  Common Crawl  │  海量但噪声大（60-80% 总量）
                ├────────────────┤
                │   社交媒体      │  低质、毒性高
                └────────────────┘
```

### 质量评分的形式化

给定一个文档 $d$，定义其**质量分数** $Q(d)$ 为多维度加权：

$$Q(d) = \sum_{i=1}^{k} w_i \cdot q_i(d)$$

其中 $q_i$ 是第 $i$ 个质量维度（如困惑度、信息熵、长度、语言流畅度），$w_i$ 是经验权重。**没有理论最优的 $w_i$**——这是 Phi 团队的"textbook quality"和 CCNet 启发式都靠经验调出来的根本原因。

### 核心工具：困惑度过滤

用一个小语言模型 $M_{\text{ref}}$（如 KenLM 训练在维基百科上的 5-gram 模型）给文档打分：

$$\text{PPL}_M(d) = \exp\left(-\frac{1}{|d|}\sum_{t=1}^{|d|} \log P_M(w_t \mid w_{<t})\right)$$

**直觉**：PPL 低 = 文档"像维基百科"（流畅、规范）；PPL 高 = 像垃圾网页（乱码、SEO 堆砌）。CCNet 的策略是**丢弃 PPL 最高的 30-50%**，只保留流畅的子集。

**适用边界**：PPL 过滤有偏见——它偏好"维基百科风格"，会丢弃方言、口语、非主流文体。对英语外的语言尤其要小心。

---

## 代码层

下面用 Python + `ccnet` 风格的伪代码演示 Common Crawl 清洗管线核心步骤：

```python
# 依赖：pip install ccnet kenlm fasttext-langdetect datasketch
import kenlm
from langdetect import detect
from datasketch import MinHash, MinHashLSH

# 步骤 1：下载 + 解析 WARC（Common Crawl 的原始格式）
def parse_warc(warc_path):
    """从 WARC 文件提取 (url, html_text) 对"""
    for record in warc_reader(warc_path):
        text = justext.extract(record.html)  # 去 HTML 标签 + 去样板
        if len(text) > 200:                  # 丢短文本
            yield record.url, text

# 步骤 2：语言识别 + 困惑度打分
lm = kenlm.LanguageModel("en_wiki.arpa.bin")  # 预训练在维基上

def quality_score(text):
    lang = detect(text)
    if lang != "en":
        return None                           # 非目标语言丢弃
    ppl = 10 ** (-lm.score(text) / len(text.split()))
    return ppl                                # 越低越好

# 步骤 3：质量过滤（保留 PPL 最低 70%）
def is_high_quality(ppl, threshold):
    return ppl < threshold                    # threshold 经验调参

# 步骤 4：MinHash 近似去重（详见 02 章的数学推导）
def minhash_dedup(documents, threshold=0.8):
    lsh = MinHashLSH(threshold=threshold, num_perm=128)
    kept = []
    for doc_id, text in enumerate(documents):
        m = MinHash(num_perm=128)
        for shingle in shingles(text, k=5):   # 5-gram shingle
            m.update(shingle.encode())
        if not lsh.query(m):                  # 近似重复则丢弃
            lsh.insert(str(doc_id), m)
            kept.append(text)
    return kept

# 完整管线
def cc_pipeline(warc_path):
    raw = parse_warc(warc_path)
    scored = [(t, quality_score(t)) for _, t in raw]
    clean = [t for t, ppl in scored if ppl and is_high_quality(ppl, threshold=500)]
    deduped = minhash_dedup(clean)
    return deduped                            # 最终训练数据
```

**反直觉数字**：跑完这条管线，**Common Crawl 通常只剩 10-20% 能用**——LLaMA 论文报告 1T tokens 的训练集，背后过滤掉了数倍于此的原始数据。清洗本身就是"烧算力的副业"。

---

## 不足层

诚实标注 Common Crawl 清洗的边界：

- **已证明的**：MinHash/LSH 在大语料上的去重近似误差有理论上界（[02 章](./02-数据清洗与去重.md) 详述）。
- **经验但未证**：PPL 阈值（如 500）和保留比例（70%）都是经验值，**不同下游任务最优值不同**。
- **未解**：
  1. **AI slop 检测**：2024 年后 CC 里混入大量低质 AI 生成内容（营销文、SEO 农场），如何在不误伤的前提下检测是开放问题。
  2. **质量没有理论最优**：$w_i$ 权重靠 grid search + 下游 benchmark 调，**换任务就要重调**。
  3. **语言偏见**：PPL 模型主要训在英语维基，对小语种、方言、非主流文体系统性歧视。
  4. **可重复性危机**：同一份 CC，不同团队清洗出的语料**差异巨大**，benchmark 可比性存疑（见 [`讲透科学的现代性/02`](../讲透科学的现代性/02-可重复性危机.md)）。

---

## 📌 下一步 + ✍️ 练习

- **下一章**：[02-数据清洗与去重](./02-数据清洗与去重.md) 钻进 MinHash/LSH 的数学和 Contamination 检测——这是本章管线的核心算法层。
- **练习**：
  1. 给定两个文档 $d_1, d_2$，如何定义它们的 Jaccard 相似度？为什么精确计算在大语料上不可行？（提示：shingle 集合爆炸）
  2. CCNet 用 KenLM 做 PPL 过滤。如果目标语言是低资源语言（如斯瓦希里语），没有维基语料训 KenLM，怎么办？
  3. 思考：为什么"清洗掉 50% 数据"反而能让模型变好？（提示：信息密度 vs 噪声）

---

## 费曼回炉记录（L2 自检）

- **F2 卡壳点**：我最初以为"Common Crawl 清洗"就是"去 HTML 标签"。重读 CCNet 和 LLaMA 论文后发现，**真正的清洗是质量评分 + 去重 + 毒性过滤 + PII 脱敏**的组合，HTML 解析只是第一步。卡壳原因是低估了数据工程的复杂度。
- **F3 术语翻译**：
  - "WARC" → Common Crawl 存网页的标准格式，每条记录是 (URL, 元数据, HTML 内容)。
  - "shingle" → 把文档切成 k 个连续词的小段，用于比较两个文档是否相似。
  - "PPL 过滤" → 用小模型给文档打"流畅度分"，丢掉最不流畅的那批。
- **F4 回炉**：v1 把质量评分写成单维（只用 PPL）；v2 改成多维度加权 $Q(d) = \sum w_i q_i$，因为单维评分会系统偏见（如全保留"维基风格"会丢多样性）。

---

## 🔗 跨系列引用

- 上游：[`00-数据是新的代码`](./00-数据是新的代码.md)（数据墙与 Chinchilla 配比）
- 下游：[`02-数据清洗与去重`](./02-数据清洗与去重.md)（MinHash 数学 + Contamination）
- 模型侧：[`讲透基础模型`](../讲透基础模型/)（LLaMA / Phi 训练细节）
- 微调侧：[`讲透微调`](../讲透微调/)（预训练数据 vs 微调数据的差异）
- 可重复性：[`讲透科学的现代性/02-可重复性危机`](../讲透科学的现代性/02-可重复性危机.md)（数据污染如何破坏可比性）
