# 附录 C — Kneser-Ney 平滑：N-gram 语言模型的最佳平滑方法

> 对应 SLP3 附录 C。在神经网络 LM 出现之前，Kneser-Ney（KN）平滑是 N-gram 语言模型的工业标准（Google N-gram、SRILM、KenLM）。它解决的核心问题是：未见过的词组合概率不该是零，也不该均分。KN 的“延续概率”思想至今影响着神经 LM 的设计。
>
> 配套实验：`experiments/C_kneser_ney.py`

---

## 1. 直觉：为什么要平滑？

### 零概率灾难

N-gram 语言模型计算 $P(w_i \mid w_{i-1})$：

$$P(w_i \mid w_{i-1}) = \frac{c(w_{i-1}, w_i)}{c(w_{i-1})}$$

如果 bigram $(w_{i-1}, w_i)$ 在训练集中**从未出现**，$c = 0$，概率 = 0。但整句概率是所有词概率的乘积——一个零就毁掉全句。

> 这不是学术问题：2000 年代语音识别系统的崩溃，一大半是因为 N-gram 把合法句子打了零分。

### Add-1（Laplace）平滑——简单但粗暴

$$P_{\text{add-1}}(w_i \mid w_{i-1}) = \frac{c(w_{i-1}, w_i) + 1}{c(w_{i-1}) + V}$$

给所有 bigram 的计数加 1（包括未见的）。问题：**太粗暴**——把大量概率分给了未见的 bigram，导致见过的 bigram 被过度打折。

> **类比**：一个班 30 人，25 人考了 90 分以上，5 人没参加考试。Add-1 平滑相当于“给所有人加 1 分再归一化”——考过试的人被拖累，没考试的凭空得分。它把概率从**高频 bigram** 大量转移到**未见的 bigram**。

### KN 的核心洞察：换一种“频率”

Kneser-Ney 问了一个深刻的问题：

> 当一个 bigram $(w', w)$ 没见过时，应该用什么给 $w$ 分配概率？

直觉说：用 $w$ 的**一元频率** $P(w) = c(w) / N$。但这不对！

**反例**：考虑 "San Francisco" 和单独的 "Francisco"。"Francisco" 的一元频率很高（总在 "San Francisco" 中出现），但它**几乎从不跟在 "the" 后面**。如果用一元频率做回退，$P(\text{Francisco} \mid \text{the})$ 会被高估。

KN 的洞察：**不该用“这个词出现了多少次”，而该用“这个词能跟多少个不同的词搭配”**。

这就是 **延续概率（Continuation probability）**：

$$P_{\text{CONT}}(w) \propto |\{w' : c(w', w) > 0\}|$$

即：在训练集中有多少个**不同的前驱词** $w'$ 曾与 $w$ 组成过 bigram。

- "the" 能跟几乎所有词搭配 → $P_{\text{CONT}}(\text{the})$ 很高
- "Francisco" 几乎只跟 "San" 搭配 → $P_{\text{CONT}}(\text{Francisco})$ 很低

---

## 2. 数学：从绝对折扣到 KN

### 2.1 绝对折扣（Absolute Discounting）

KN 的第一步是**绝对折扣**：从每个非零计数中减去一个固定常数 $D$（通常 $D \approx 0.75$），把省下来的概率质量分给未见的 bigram：

$$P_{\text{abs}}(w_i \mid w_{i-1}) = \frac{\max(c(w_{i-1}, w_i) - D, \, 0)}{c(w_{i-1})} + \lambda(w_{i-1}) \cdot P_{\text{lower}}(w_i)$$

- 第一项：折扣后的 bigram 概率（$D$ 通常从数据中估计，经验值约 0.75）
- 第二项：回退到低阶模型 $P_{\text{lower}}$，权重 $\lambda(w_{i-1})$ 保证概率和为 1

$\lambda(w_{i-1})$ 的含义：前驱词 $w_{i-1}$ 有多少概率质量被“省下来”给未见 bigram：

$$\lambda(w_{i-1}) = \frac{D}{c(w_{i-1})} \cdot N_{1+}(w_{i-1}\bullet)$$

其中 $N_{1+}(w_{i-1}\bullet)$ = $w_{i-1}$ 后面跟过多少个**不同的**词（bigram 类型数）。

### 2.2 Kneser-Ney 完整公式（bigram 版）

把 $P_{\text{lower}}$ 换成延续概率，就是完整的 KN：

$$\boxed{P_{\text{KN}}(w_i \mid w_{i-1}) = \frac{\max(c(w_{i-1}, w_i) - D, \, 0)}{c(w_{i-1})} + \lambda(w_{i-1}) \cdot \frac{N_{1+}(\bullet w_i)}{N_{1+}(\bullet\bullet)}}$$

其中：
- $N_{1+}(\bullet w_i) = |\{w' : c(w', w_i) > 0\}|$：$w_i$ 的不同前驱数量
- $N_{1+}(\bullet\bullet)$：训练集中所有 bigram 的**类型**总数
- $\lambda(w_{i-1}) = \frac{D}{c(w_{i-1})} \cdot N_{1+}(w_{i-1}\bullet)$

### 2.3 Modified KN（实际使用的版本）

Kneser（1995）的原始论文用 **backoff**（只对未见的 bigram 回退），Ney et al.（1994）的改进版用 **interpolation**（所有 bigram 都混入低阶），效果更好且更简单：

$$P_{\text{mKN}}(w_i \mid w_{i-1}) = \frac{\max(c(w_{i-1}, w_i) - D, \, 0)}{c(w_{i-1})} + \gamma(w_{i-1}) \cdot P_{\text{CONT}}(w_i)$$

$\gamma(w_{i-1})$ 的设计保证：$\sum_{w_i} P_{\text{mKN}}(w_i \mid w_{i-1}) = 1$。

### 2.4 推广到 trigram（Modified Interpolated KN）

$$P_{\text{KN}}(w_i \mid w_{i-2}, w_{i-1}) = \frac{\max(c(w_{i-2}, w_{i-1}, w_i) - D, \, 0)}{c(w_{i-2}, w_{i-1})} + \gamma(w_{i-2}, w_{i-1}) \cdot P_{\text{KN}}(w_i \mid w_{i-1})$$

低阶 $P_{\text{KN}}(w_i \mid w_{i-1})$ 用同样的公式递归定义，最终回退到延续概率。这就是 **KenLM** 等工业级 LM 工具使用的标准算法。

---

## 3. 为什么 KN 比 Add-1 好得多？

| 问题 | Add-1 | KN |
|------|-------|-----|
| 对已见 bigram | 过度打折（分母加 $V$ 太大） | 只减固定 $D \approx 0.75$，温和 |
| 对未见 bigram | 一视同仁（每个 +1） | 按延续概率分配（合理） |
| “Francisco” 问题 | 用一元频率，高估 | 用延续概率，正确低估 |
| 工程验证 | PPL 高 30-50% | PPL 最低（N-gram 天花板） |

---

## 4. 代码跑通：Add-1 vs Kneser-Ney

```bash
python3 experiments/C_kneser_ney.py
```

实验在微型语料上训练 bigram LM，对比 add-1 和 KN 的困惑度（perplexity）：

**反直觉发现**：KN 的 PPL 比 add-1 **降低 38%**（6.4 vs 10.3）。更深层的是延续概率的效果——`the` 作为万能搭配词获得高延续概率，而只跟特定词搭配的词（如 `cat`：一元频率 0.047 但延续概率仅 0.020）被正确惩罚。

---

## 5. 在 LLM 时代的地位

KN 平滑作为**工业工具**已被神经 LM 取代（神经网络天然平滑——softmax 不产生零概率）。但它的思想影响了：

1. **Subword regularization / BPE-dropout**：通过在 token 级别引入随机性，模拟了 KN 的“给罕见组合分配概率”思想。
2. **Neural LM 的 smoothing**：Merity et al. (2017) 发现 AWD-LSTM 的 weight dropout 效果类似 KN 的折扣——都在防过拟合到高频模式。
3. **LLM 的 temperature**：本质上是在平滑输出分布，与 discounting 异曲同工。

---

## 6. 局限与批判

1. **只能用离散 N-gram**：KN 的 discounting 依赖离散计数，无法直接用于连续表示。神经网络通过连续 embedding 实现了“更好的平滑”，但机制完全不同。

2. **状态空间爆炸**：trigram 的状态数 $V^3$，对于 $V = 100{,}000$ 的词表就是 $10^{15}$。KenLM 用 trie 和量化压缩到可接受范围，但已经到了极限。

3. **没有语义泛化**：KN 完全靠统计共现。它知道 "the cat" 常见，但不知道 "the kitten" 语义相似。词嵌入解决了这个问题。

4. **仍是离线场景的最佳选择**：在**无法运行神经网络**的场景（嵌入式设备、超低延迟、海量数据离线打分），KenLM + KN 至今无可替代。

---

## 📌 下一步

- → `03-N元语法语言模型.md`：N-gram LM 的基础（本附录是其平滑方法的深度展开）
- → `05-词嵌入-word2vec与GloVe.md`：词嵌入如何解决 KN 的“无语义泛化”问题
- → 本附录的实验：`experiments/C_kneser_ney.py`

---

## ✍️ 练习

**练习 C.1**：在实验脚本中，把 $D$ 从 0.75 改成 0.1 和 0.99，观察 PPL 如何变化。为什么 $D$ 太大或太小都不好？

**练习 C.2**：手动计算 $P_{\text{CONT}}(\text{"the"})$ 和 $P_{\text{CONT}}(\text{"Francisco"})$ 在一个你构造的小语料上的值。验证 "Francisco" 虽然一元频率不低，但延续概率很低。

**练习 C.3**：实现 trigram 版 modified KN。提示：需要维护 trigram 统计 + bigram 类型数 + 延续。

**练习 C.4**：对比 interpolation（interpolated KN）和 backoff（original KN）在相同数据上的 PPL。SLP3 说 interpolation 更好——验证它。

---

> 配套实验：`experiments/C_kneser_ney.py`。姊妹章节：`03-N元语法语言模型.md`、`05-词嵌入-word2vec与GloVe.md`。
