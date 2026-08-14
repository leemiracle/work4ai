# 讲透NLP × 数学：反向索引

> **本目录作用**：讲透NLP 是数学的**消费方**（用数学做 NLP），不是数学的**建立方**（证明新定理）。
> 这个 README 把 NLP 每章用到的数学**反向链接**到 [`../../top-math-courses/`](../../top-math-courses/) 的对应课程——
> 让你在学 NLP 时知道"哪个数学概念该回去补"，在学数学时知道"它能用在 NLP 哪里"。
>
> 这份索引是 [`../../top-math-courses/CROSS_INDEX_WITH_WORK4AI.md`](../../top-math-courses/CROSS_INDEX_WITH_WORK4AI.md) 的**反向版**（那份是 数学→NLP，本份是 NLP→数学）。

---

## 一、NLP 章节用到的数学（正向索引）

| NLP 章节 | 用到的数学概念 | 深度 | 去 top-math-courses 哪门课补 |
|---------|--------------|------|----------------------------|
| **Ch02** 词与 token、编辑距离 | 动态规划、字符串距离 | 浅 | MIT 6.042J 离散数学（#6）|
| **Ch03** N-gram 语言模型 | 条件概率、链式法则、对数概率、交叉熵 | 中 | Berkeley Stat 134（#7）+ MIT 18.424 信息论（#22）|
| **Ch04** 逻辑回归与文本分类 | sigmoid、极大似然、梯度下降、正则化 | 中 | Stanford CME 364A 凸优化（#20）+ Stat 200A（#21）|
| **Ch05** 词嵌入 word2vec/GloVe | 向量空间、内积、SGNS 损失、矩阵分解（Levy&Goldberg）| **中深** | MIT 18.06（#3）+ Berkeley Math 110 Axler（#5）+ 附录 J PPMI/SVD |
| **Ch06** 神经网络基础 | 链式法则、矩阵微分、激活函数连续性 | 中 | MIT 18.06（#3）+ MIT 18.100B 实分析（#11）|
| **Ch07** 大语言模型导引 | 自回归分解、softmax、温度采样 | 中 | Stat 134（#7）+ 信息论（#22）|
| **Ch08** Transformer | 线性投影、attention 矩阵、谱、低秩近似 | **深** | MIT 18.06 + Math 110 Axler（#5）+ MIT 18.102 泛函（#23，RKHS 视角）|
| **Ch09** 后训练 SFT/DPO | KL 散度、Bradley-Terry、refusal direction 几何 | **深** | 信息论（#22）+ Berkeley Stat 200A（#21）+ 线性代数（PC1 投影）|
| **Ch10** BERT | 各向异性、向量几何 | 中 | MIT 18.06（#3）|
| **Ch11** IR/RAG | TF-IDF、BM25、余弦相似度 | 中 | 信息论（#22）+ 18.06 |
| **Ch12** 机器翻译 | EM 算法、对齐概率 | 中深 | Stat 200A（#21，EM 的严格基础）+ 凸优化（#20，EM = KL 投影）|
| **Ch13** RNN/LSTM | 谱半径、梯度流、动力学稳定性 | **深** | Math 110（#5）+ MIT 18.03 ODE（#4）+ 18.100B（#11）|
| **Ch14** 语音学特征 | mel 刻度、傅里叶变换 | 中深 | **MIT 18.103 调和分析（#24）★ 强烈推荐** |
| **Ch15** ASR | HMM、CTC、beam search、Viterbi | **深** | Berkeley Math 218 随机过程（#25，Markov 链）+ 信息论 |
| **Ch16** TTS | 共振峰、源-滤波器模型 | 中 | 18.103 调和分析 |
| **Ch17** 序列标注 POS/NER | HMM、CRF、转移-发射 | 中深 | Math 218（#25，Markov）+ Stat 200A（#21，CRF 的指数族）|
| **Ch18** CFG / 成分句法 | PCFG、CKY 算法、Chomsky 范式 | 中 | MIT 6.042J 离散（#6）+ 概率（#7）|
| **Ch19** 依存句法 | 有向图、投影性、最大生成树 | 中 | 6.042J（#6，图论）+ CME 364A（#20，组合优化）|
| **Ch20** 信息抽取 / 语义角色 | 规则、模式匹配 | 浅 | 6.042J（#6）|
| **Ch22** 情感 / 共指 | 朴素贝叶斯、聚类 | 中 | Stat 134（#7）+ Stat 200A（#21）|
| **Ch24** 篇章 / 对话 | RST、DST、MDP/POMDP | **深** | **Berkeley Math 218 随机过程（#25）★ + UT Austin M 387D（#26 SDE/Bellman）** |
| **附录 A** HMM | 前向/后向算法、Viterbi、Baum-Welch | **深** | **Math 218（#25）★ + Stat 200A（#21，EM）** |
| **附录 B** 朴素贝叶斯 | 贝叶斯定理、条件独立 | 中 | Stat 134（#7）+ Stat 200A（#21）|
| **附录 C** Kneser-Key 平滑 | 绝对折扣、插值、回退 | 中 | Stat 200A（#21）|
| **附录 D** 拼写纠正 / 噪声信道 | Bayes 倒置、信源-通道模型 | 中 | 信息论（#22）|
| **附录 E** 统计成分句法 | PCFG、词法化、重排序 | 中 | 6.042J + Stat 134 |
| **附录 G** CCG | λ-演算、组合子、Curry-Howard | **深** | **MIT 18.100B 之外的：需读 Lambda 演算书（Hindley-Seldin）★** |
| **附录 H** 逻辑语义 | 一阶逻辑、模型论、λ-演算 | **深** | **数学系数理逻辑课（不在 30 课主线，建议读 Enderton《Mathematical Logic》）★** |
| **附录 J** PPMI/SVD | PMI、PPMI、奇异值分解 | 中深 | **MIT 18.06（#3，SVD）+ 信息论（#22，互信息）★** |

---

## 二、数学主题 → NLP 应用章节（反向索引）

> 这个表帮你学数学时知道"它能用在 NLP 哪里"。

| 数学主题 | top-math-courses 课 | 用在讲透NLP 哪 |
|---------|-------------------|---------------|
| **条件概率 / 贝叶斯** | Stat 134 (#7) | Ch03, 附录 B/D, Ch22 |
| **链式法则 / 极大似然** | Stat 200A (#21) | Ch03, Ch04, Ch05 |
| **交叉熵 / KL 散度** | 信息论 #22 | Ch03, Ch07, Ch09 (DPO), 附录 D |
| **softmax / 指数族** | Stat 200A (#21) | Ch04, Ch07, Ch17 (CRF) |
| **梯度下降 / 凸优化** | CME 364A (#20) | Ch04, Ch06, 讲透优化器 |
| **矩阵微分 / Jacobian** | MIT 18.06 (#3) | Ch06 (反向传播) |
| **特征值 / 谱 / SVD** | MIT 18.06 + Math 110 (#5) | Ch05 (词嵌入), Ch08 (attention), Ch10 (各向异性), 附录 J |
| **Markov 链** | Math 218 (#25) | Ch13 (RNN 动力学), 附录 A (HMM), Ch15 (ASR), Ch24 (对话) |
| **EM 算法** | Stat 200A (#21) | Ch12 (IBM Model), 附录 A (Baum-Welch) |
| **调和分析 / Fourier** | MIT 18.103 (#24) | Ch14 (语音特征 MFCC), Ch16 (TTS 共振峰) |
| **概率图模型** | Math 218 (#25) | 附录 A (HMM), Ch17 (CRF), Ch24 (POMDP) |
| **λ-演算 / 数理逻辑** | 自学（Enderton / Hindley-Seldin）| 附录 G (CCG), 附录 H (逻辑语义) |
| **信息几何** | 选学（Amari）| Ch09 (KL 几何), 进阶 LLM 对齐 |

---

## 三、按"想成为数学专家"的优先级排序

如果你目标是数学专家（不只是 NLP 工程师），按**数学深度**排序，NLP 里最值得深挖数学的方向是：

| 优先级 | NLP 主题 | 深挖哪个数学 |
|--------|---------|-------------|
| ⭐⭐⭐⭐⭐ | Transformer / Attention 几何 | 谱理论、泛函（RKHS）、信息几何 |
| ⭐⭐⭐⭐⭐ | HMM / CRF / 对话 (POMDP) | 随机过程、概率图模型 |
| ⭐⭐⭐⭐⭐ | 词嵌入 / 矩阵分解 | 线性代数（Axler）、SVD、低秩近似 |
| ⭐⭐⭐⭐ | 后训练 / DPO / refusal direction | 信息论（KL）、统计、线性几何 |
| ⭐⭐⭐⭐ | 语音 / 调和分析 | Fourier 分析、调和分析 |
| ⭐⭐⭐ | 逻辑语义 / CCG | 数理逻辑、λ-演算、Curry-Howard |
| ⭐⭐⭐ | 机器翻译 / EM | 凸优化（EM = KL 投影）、统计 |
| ⭐⭐ | 句法 / CFG | 离散数学、形式语言 |
| ⭐⭐ | 文本分类 / 逻辑回归 | 凸优化、统计 |

> 💡 **关键洞察**：NLP 里**深数学富集**的方向是 Transformer / HMM / 词嵌入 / 后训练 / 语音。这五个方向如果你想发数学论文，从这五个里挖——它们已经和顶会理论 track（如 ICLR theory / NeurIPS theory）挂钩。

---

## 四、学习建议

### 4.1 如果你正在学讲透NLP 某章

1. 看本表找到对应数学主题
2. 如果数学浅（如 Ch02 编辑距离）→ NLP 章节自带够，不补
3. 如果数学深（如 Ch08 Transformer）→ 学完 NLP 章**回去补对应数学课**
4. 补完数学 → 回来重读 NLP 章，看是否更深入

### 4.2 如果你正在学 top-math-courses 某课

1. 看反向索引找到数学主题用在哪个 NLP 章
2. 学完一个数学概念 → 去 NLP 章做实验验证
3. 例：学完 18.06 的 SVD → 去附录 J 跑 PPMI+SVD 实验

### 4.3 双向印证的最小循环

```
学 18.06 SVD (数学)
    ↓
做 附录 J PPMI 实验 (NLP)
    ↓
发现"king-man+woman≈queen"背后的 SVD 结构
    ↓
读 Levy & Goldberg 2014 (论文)
    ↓
在 Lean 里形式化"SVD 唯一性定理" (形式化)
    ↓
写一段讲透笔记 (产出)
```

---

## 五、本目录将来的扩展

未来可以在 `math/` 下加按数学主题分的子文件，例如：
- `math/probability.md` — NLP 里所有概率论概念详解
- `math/linear_algebra.md` — NLP 里的线代（attention 谱 / 词嵌入 SVD）
- `math/information_theory.md` — 交叉熵 / KL / 互信息在 NLP
- `math/optimization.md` — SGD / Adam / 优化在 NLP

目前先做索引（本 README）。子文件按需创建。

---

## 六、与其他文档的衔接

- **正向索引（数学→NLP）**：[`../../top-math-courses/CROSS_INDEX_WITH_WORK4AI.md`](../../top-math-courses/CROSS_INDEX_WITH_WORK4AI.md)
- **数学主路径**：[`../../top-math-courses/UNIFIED_ROADMAP.md`](../../top-math-courses/UNIFIED_ROADMAP.md)
- **数学研究方法论**：[`../../top-math-courses/RESEARCH_METHODOLOGY.md`](../../top-math-courses/RESEARCH_METHODOLOGY.md)
- **学数学同时练 Lean**：[`../../top-math-courses/LEAN_MATH_TRACK.md`](../../top-math-courses/LEAN_MATH_TRACK.md)
- **NLP 主 README**：[`../README.md`](../README.md)

---

📌 **下一步**：
- 在学讲透NLP 时，把本表当"数学导航"
- 如果某章的数学让你卡住 → 来本表找对应数学课 → 去补
- 学完一门数学课 → 来反向索引看它在 NLP 哪里用得上
