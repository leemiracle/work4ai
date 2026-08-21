# 附录 H — 句子意义的逻辑表示：一阶逻辑与 λ-演算

> 对应 SLP3 附录 H。前面讲了词的语义（embedding）、句法结构（CFG/CCG），但“一个句子到底说了什么”需要一个**形式化的意义表示**（meaning representation）。本附录介绍计算语义学的基石：**一阶逻辑**（FOL）+ **λ-演算**，以及 **模型论语义学**如何将符号接地到世界。
>
> 本附录无独立实验，λ-reduction 逻辑融入 `experiments/G_ccg_parser.py` 的语义组合部分。

---

## 1. 直觉：句子 = 可验证的事实

用户问 *"Does Maharani serve vegetarian food?"*，系统需要：

1. 把句子表示为 `Serves(Maharani, VegetarianFood)`
2. 在知识库里查这条事实是否存在
3. 存在→答 yes，不存在→答 no/unknown

这就是 **可验证性**（verifiability）：表示能与世界（知识库）对照判定真假。一阶逻辑提供了这套符号系统——**常量**指代对象、**谓词**表示属性/关系、**量词**表达“存在/所有”。

### 意义表示的四条 desiderata

| 要求 | 含义 | 例子 |
|------|------|------|
| 可验证性 | 能与知识库对照判定真假 | `Serves(Maharani, VegFood)` 能查到 |
| 无歧义 | 一个表示只有一种解读 | "eat someplace" 不允许歧义残留 |
| 规范形式 | 同义不同形的输入映射到同一表示 | 主动/被动 → 相同谓词 |
| 支持推理 | 能推出知识库中未显式存储的结论 | 蕴含规则 + Modus Ponens |

---

## 2. 数学层

### 2.1 一阶逻辑（FOL）的要素

$$\text{Formula} \to \text{Atomic} \mid \text{Formula}\ \wedge\ \text{Formula} \mid \forall x.\ \text{Formula} \mid \exists x.\ \text{Formula} \mid \neg\text{Formula}$$

| 要素 | 符号 | 含义 | NLP 例子 |
|------|------|------|---------|
| 常量 | $A$, $Maharani$ | 特定对象 | 餐厅 Maharani |
| 变量 | $x$, $y$ | 匿名对象 | "某个餐厅" |
| 谓词 | $Serves(x,y)$ | 属性/关系 | $x$ 供应 $y$ |
| 函数 | $LocationOf(x)$ | 返回对象的属性 | Frasca 的位置 |
| 量词 | $\forall, \exists$ | 所有 / 存在 | 所有素食餐厅 |

### 2.2 量词与自然语言

不定名词短语 → 存在量词；全称名词短语 → 全称量词：

$$\text{Every student reads a book} \implies \forall x.\ \text{student}(x) \to \exists y.\ \text{book}(y) \wedge \text{read}(x, y)$$

$$\text{All restaurants serve food} \implies \forall x.\ \text{restaurant}(x) \to \text{serves}(x, \text{food})$$

> **注意量词辖域**：*Every student reads a book* 也可读作“有一本书，所有学生都读”（$\exists y.\ \text{book}(y) \wedge \forall x.\ldots$），但默认解读是“逐个学生各有书”（surface scope）。

### 2.3 λ-演算：语义组合的胶水

λ-抽象让我们从完整公式中“抽出”参数，逐步填充：

$$\lambda x.\ \lambda y.\ \text{Near}(x, y)$$

应用到常量时进行 **λ-reduction**（文本替换）：

$$\lambda x.\ \lambda y.\ \text{Near}(x,y)(\text{Bacaro}) \xrightarrow{\beta\text{-reduction}} \lambda y.\ \text{Near}(\text{Bacaro}, y)$$

$$\lambda y.\ \text{Near}(\text{Bacaro}, y)(\text{Centro}) \longrightarrow \text{Near}(\text{Bacaro}, \text{Centro})$$

**Currying**（Schönfinkel 1924）：将多元谓词拆成一元函数链。动词 `serves` 的语义 $\lambda y.\lambda x.\text{serve}(x,y)$ 与 CCG 范畴 $(S\backslash NP)/NP$ 完美对应——句法每步归约同步做一次 λ-reduction。

### 2.4 事件语义（Neo-Davidsonian）

谓词固定 arity 的困难（*I ate / I ate a sandwich / I ate at my desk* 参数数量不同），用**事件变量** $e$ 解决：

$$\exists e.\ \text{Eating}(e) \wedge \text{Eater}(e, \text{Speaker}) \wedge \text{Eaten}(e, \text{Sandwich}) \wedge \text{Location}(e, \text{Desk})$$

角色（Eater, Eaten, Location）按需附加，不影响核心谓词结构。

### 2.5 模型论语义学

表示如何接地到世界？通过 **模型** $M = \langle D, I \rangle$：

- **域** $D$ = 所有对象的集合
- **解释** $I$：常量→域元素，一元谓词→域子集，二元谓词→有序对的集合

> `Serves(Maharani, VegFood)` 为真 ⟺ $I(\text{Serves})$ 集合中有 $\langle I(\text{Maharani}), I(\text{VegFood}) \rangle$ 这对元素。一切都是集合运算。

### 2.6 推理：Modus Ponens

$$\frac{a \qquad a \Rightarrow b}{b}$$

已知 `VegetarianRestaurant(Leaf)` 和 $\forall x.\text{VegRestaurant}(x) \Rightarrow \text{Serves}(x, \text{VegFood})$，推出 `Serves(Leaf, VegFood)`。前向链 / 后向链（Prolog）是实践方式。

---

## 3. 代码层

λ-reduction 演示集成在 `experiments/G_ccg_parser.py` 中——CCG 推导的每步句法归约都同步执行 λ-reduction，最终输出句子的 FOL 表示。

---

## 4. 批判性视角

- **FOL 的表达力边界**：FOL 无法直接表达时态、模态、概率。需要扩展（时态逻辑、模态逻辑、概率逻辑），代价是推理复杂度上升。
- **规范形式理想 vs 现实**：*Is the food good? / How is the food? / What's the food like?* 理论上应映射到同一表示，但语义解析器极难做到——这是“语义等价”的深层难题。
- **LLM 跳过了显式逻辑**：现代系统不显式构建 FOL 表示，而靠 embedding 隐式编码语义。但 FOL 在**知识图谱推理、形式化验证、可审计 AI** 中仍然不可替代——它的透明性是神经网络无法提供的。

---

## ✍️ 练习

1. ⭐ 将 *"No student likes every course"* 翻译为 FOL。至少两种量词辖域解读。
2. 对 $\lambda x.\lambda y.\text{Loves}(x,y)$ 逐步做 β-reduction，应用到 `Romeo` 和 `Juliet`。
3. ★ 用事件语义表示 *"I ate a sandwich at noon quickly"*。有几个角色谓词？
4. 为什么 * VegetarianRestaurant(AyCaramba) → Serves(AyCaramba, VegFood)* 在 $\forall$ 量词语义下为真，即使 AyCaramba 不是素食餐厅？（提示：前件假 → 蕴含空真。）

→ [I-词义与WordNet.md](I-词义与WordNet.md)：逻辑表示中谓词的“意义”如何与词义网络连接。
