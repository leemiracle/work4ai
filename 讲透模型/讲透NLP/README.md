# 讲透NLP (Speech and Language Processing, 透) · 完整版

> 用「直觉 → 数学 → 代码跑通 → 不足 → 应用」的方式，基于 **Jurafsky & Martin《Speech and Language Processing》3rd edition**（2026-01-06 release, https://web.stanford.edu/~jurafsky/slp3/），把 NLP/语音从第一性原理讲透。
>
> 不写广度综述（教材本身已经是 NLP 领域 25 年来最好的综述），只往**底层和本质**钻。每一篇配一个能跑出反直觉结论的 Python 实验。

**25 章主线 + 11 附录**，按 SLP3 章节顺序组织。从最古早的 N-gram LM 一路讲到 LLM 时代的对齐与多模态——你能看到"为什么 attention 之前 RNN/HMM 主导，为什么 BERT 出现是分水岭，为什么 LLM 把前面所有方法都收编了"。

---

## 阅读顺序（SLP3 路径图）

```
                            00-开场 (NLP 全景与学习路径)
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        ▼                             ▼                             ▼
   Ch1-2 引言+词                Ch3 N-gram LM                Ch4 逻辑回归
   (基础概念)                   (统计LM地基)                 (文本分类入门)
        │                             │                             │
        └─────────────┬───────────────┴─────────────┬────────────────┘
                      ▼                             ▼
                Ch5 词嵌入                    Ch10 MLM/BERT
                (word2vec/GloVe)              (双向编码器)
                      │                             │
                      ▼                             ▼
        Ch6 NN → Ch7 LLM → Ch8 Transformer → Ch9 Post-training
        (与《讲透基础模型》系列交叉，本系列做导引)
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   Ch11 IR/RAG    Ch12 MT       Ch13 RNN/LSTM
   (与《讲透RAG》交叉)          (attention 之前的主流)
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
   Ch14-16 语音三件套           Volume II 语言结构
   (Phonetics/ASR/TTS)         Ch17-25 + 附录
                                (POS/NER/Parsing/IE/...)
```

---

## 全部章节

### Volume I: Large Language Models（16 章）

| # | 文件 | 核心问题 | 实验关键数字 |
|---|---|---|---|
| 00 | `00-开场.md` | 为什么用 SLP3 学 NLP？路径总图 | — |
| 01 | `01-导论-NLP全景.md` | NLP 解决什么问题？任务分类 | "I saw her duck" 仅词法层就有 8 种歧义组合；规则/统计/神经三代各只部分消歧 |
| 02 | `02-词与token-编辑距离.md` | 词怎么定义？token 化怎么做？编辑距离为何是基础 | intention→execution 标准=5 vs SLP版=8；归一化不对称 1/3≠1/4；Levenshtein 纠正 recieve→relieve(错!) |
| 03 | `03-N元语法语言模型.md` | 不用神经网络怎么做语言模型？为什么要平滑 | trigram PPL 反比 bigram 高(数据稀疏)；add-1 严重过度平滑，最优 K≈0.01-0.05 |
| 04 | `04-逻辑回归与文本分类.md` | 最简单的神经分类器长啥样？sigmoid 为何神奇 | TF-IDF→8 维固定稠密向量，准确率 ~100%→68.3%（同样分类器，特征从稀疏变固定就崩）|
| 05 | `05-词嵌入-word2vec与GloVe.md` | 词怎么变成向量？为什么"国王−男人+女人≈女王" | king-man+woman≈queen 命中；K≈5 甜区；小语料高维(dim↑)参数暴涨质量不升(过拟合) |
| 06 | `06-神经网络基础.md` | 反向传播与梯度下降（导引到《讲透基础模型》） | MLP(1377参)仅比 logistic(42参)高 1.1%(91.1→92.2%)；logistic 权重全部 ±1.112 对称 |
| 07 | `07-大语言模型.md` | GPT 类模型如何工作（导引） | mini-GPT 学到语法(CE 6.62→3.48bit 省 47%)学不到知识(生成"the big stone swam")；温度悬崖 T=0.7 最自然(0.46) |
| 08 | `08-Transformer.md` | attention 为何革命性（导引到《讲透Transformer》） | 多头注意力总有效秩随头数 12→62，每头骤降 12→2（多头=子空间分工）|
| 09 | `09-后训练-SFT对齐DPO-test-time.md` | 基座怎么变助手？DPO/RLHF/test-time compute + §8 后训练的镜子（探测与充分利用） | SFT 无对比信号:P(rejected) 先升后降; DPO β=0.05→KL 爆炸+熵坍塌 <35%; **§8 refusal direction 复现：玩具 GPT(39K参) PC1=99.9%、ablation ↓74.4%、addition coeff=0.5 让无害拒绝率 0.03%→87%** |
| 10 | `10-掩码语言模型-BERT.md` | BERT 与 GPT 的根本差异？双向编码器 | [MASK]上瘾 80%≫随机40%；未微调 BERT 句向量 AUC~0.65 < 静态~0.95(各向异性)；MLM 比 NTP 慢~7x |
| 11 | `11-信息检索与RAG.md` | 检索增强生成的工作原理（导引到《讲透RAG》） | 原始 TF 被关键词堆砌骗(垃圾页 7.69>正解 D0=3.07)；BM25 饱和项(tf→2.29 渐近 2.5)治此病，正解排回第 1 |
| 12 | `12-机器翻译.md` | 从 IBM Model 到 Transformer MT，再到 LLM 翻译 | Model1 EM 无监督学出 the→那个(t=0.696)；打乱词序后 t 表【完全相同】(差 6.66e-16)→证其对词序盲目 |
| 13 | `13-RNN与LSTM.md` | attention 之前如何处理变长序列？梯度消失怎么治 | 梯度消失(谱半径 0.83→‖∂h_T/∂h_0‖1e-2)/爆炸(5.33→1e-27)；字符级 RNN BPTT 学 hello(loss 4.9→0.2) |
| 14 | `14-语音学与特征提取.md` | 音素/MFCC/语谱图——语音的"token" | 人耳频率感知非线性(100→200Hz 明显 vs 7000→7100Hz 几乎听不出)→mel 对数刻度 |
| 15 | `15-自动语音识别-ASR.md` | HMM→CTC→Attention→Whisper 的演化 | beam search 加宽(5→20)CER 反降 9.7%；词典 LM rescoring CER 22.8%→0.5%(↓97.8%)——瓶颈在条件独立假设 |
| 16 | `16-语音合成-TTS.md` | 从拼接合成到 Neural TTS 到 zero-shot 声音克隆 | 3 共振峰频率 + 1 脉冲源 = 可辨别元音(不需精确模拟整个声道形状) |

### Volume II: Annotating Linguistic Structure（9 章）

| # | 文件 | 核心问题 | 实验关键数字 |
|---|---|---|---|
| 17 | `17-序列标注-POS与NER.md` | 给词打标签：HMM/CRF/BiLSTM-CRF/BERT 系 | 去掉转移概率，未知词准确率 84.6%→0.0%（OOV 全靠"标签序列语法骨架"兜底）|
| 18 | `18-上下文无关文法与成分句法分析.md` | CFG 与树库，PCFG 的概率推导 | "the cat sat..."=1棵树；"saw the man with the telescope"=2棵树，PCFG 选错(0.4/0.3=1.333纯频率比，不看词义) |
| 19 | `19-依存句法分析.md` | 为什么中文更适合依存？transition-based vs graph-based | arc-standard transition parser 对非投影句(交叉弧)有数学硬限——揭示其能力边界 |
| 20-21 | `20-信息抽取与语义角色.md` | 关系/事件/时间抽取 + 语义角色标注(论元结构) | 规则 F1=92.3% vs LLM F1=37.5%(小数据集上规则反超) |
| 22-23 | `22-情感与共指消解.md` | 情感极性/情绪/强度 + "她/他/它"指谁 + 指到 KB 哪个实体 | 词典零训练 88.9% 反超监督模型(低数据) |
| 24-25 | `24-篇章与对话.md` | 篇章连贯(RST/PDTB/entity grid)+对话行为/对话状态追踪(DST)/对话管理(MDP·POMDP) | 规则 100% ≈ softmax 95.5%(结构化)；开放 55% vs 25% → 必须预训练 |

### Appendix（11 篇）

| # | 文件 | 核心问题 |
|---|---|---|
| A | `appendix/A-隐马尔可夫模型.md` | HMM 三问题：评估/解码/学习；Viterbi/前向后向算法 |
| B | `appendix/B-朴素贝叶斯分类.md` | 文本分类的贝叶斯视角；为何"朴素"也能用 |
| C | `appendix/C-Kneser-Ney平滑.md` | N-gram 平滑的 SOTA 方法；绝对折扣与插值 |
| D | `appendix/D-拼写纠正与噪声信道.md` | 噪声信道模型；编辑距离的概率化 |
| E | `appendix/E-统计成分句法分析.md` | PCFG / lexicalized parsing / Berkeley parser |
| F | `appendix/F-上下文无关文法.md` | CFG 形式语言层级；Chomsky 层级 |
| G | `appendix/G-组合范畴语法CCG.md` | CCG 的组合算子；为何适合语义分析 |
| H | `appendix/H-句子意义的逻辑表示.md` | 一阶逻辑/λ-演算与语义组合 |
| I | `appendix/I-词义与WordNet.md` | 同义词集/上下位/部分整体；WordNet 工程实践 |
| J | `appendix/J-PPMI点互信息.md` | 共现统计与词关联；为何 PPMI 优于 PMI |
| K | `appendix/K-基于框架的对话系统.md` | 框架/槽位填充；任务型对话的早期范式 |

> 标 `—` 的实验数据列，在该章节落盘后会填上反直觉发现的"铁证数字"。

---

## 怎么跑

```bash
cd 讲透NLP
python3 -u experiments/02_edit_distance.py        # 编辑距离
python3 -u experiments/03_ngram_lm.py             # N-gram LM
python3 -u experiments/04_logistic_textclass.py   # 文本分类
python3 -u experiments/05_word2vec.py             # 词嵌入
python3 -u experiments/10_mlm_bert.py             # MLM/BERT
# ... 全 25 章 + 11 附录
```

每个脚本自包含、几秒内跑完、打印结论性数字。改参数做练习见各 `.md` 末尾「✍️ 练习」。

---

## 核心方法论（"讲透"标准）

1. **原理优先于 API**：先讲为什么，再讲怎么调库（HuggingFace/spaCy/NLTK）。
2. **每个结论都有可运行代码佐证**：不凭记忆下断言，数字都是跑出来的。
3. **批判性**：每篇结尾必有「局限与争议」——方法的失败模式、被 LLM 替代的程度、何时仍要用。
4. **离散 vs 连续分水岭始终强调**：从符号方法（规则/HMM/CFG）跨到神经方法（CE/softmax）必须翻的坎。
5. **历史脉络**：每个方法都讲"在它之前是什么、为什么被取代、现在还有没有用"——这是 SLP3 最有价值的部分。

---

## 前置要求

- **数学**：求和、对数、期望、矩阵乘、softmax、基本概率。附录的 HMM 推导是最高难度。
- **代码**：能读懂 PyTorch 的 `nn.Linear`/`cross_entropy`/`softmax`，能读 NumPy。
- **背景**：知道"神经网络要训练、有损失函数"即可。从公理推起，零基础也能跟。

姊妹项目：
- `../讲透基础模型/` —— 第 6/7/8 章的"深度学习部分"深度版
- `../讲透Transformer/` —— 第 8 章的深度版
- `../讲透RAG/` —— 第 11 章的深度版
- `../讲透Prompt/` `../讲透微调/` —— 第 9 章的深度版
- `../讲透分词器/`（笔记在 `../notes/`）—— 第 2 章的深化版
