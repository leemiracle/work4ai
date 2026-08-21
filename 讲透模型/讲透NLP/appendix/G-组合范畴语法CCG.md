# 附录 G — 组合范畴语法（CCG）：把语法塞进词典

> 对应 SLP3 附录 G。附录 E-F 使用 PCFG + CKY 进行语法分析，规则写在语法中，词语仅标注词性。CCG 则反其道而行：**几乎所有的语法信息都编码在词项的范畴（category）中**，而组合规则仅有寥寥数条。这种“极简规则 + 极丰词典”的设计使得 CCG 天然支持**透明的语义组合**——语法推导的每一步都对应于语义计算的一步，这也是它成为语义解析（semantic parsing）事实标准的原因。
>
> 配套实验：`experiments/G_ccg_parser.py`

---

## 1. 直觉：一句话就是一个函数调用

看英语句子 *United serves Miami*。如果我说：

- `United` = 一个名词短语值 `NP`
- `serves` = 一个函数，**右边吃一个 NP，吐出一个「左边吃 NP 吐出 S」的函数**，即 $(S\backslash NP)/NP$
- `Miami` = 一个名词短语值 `NP`

那么推导过程就是两次函数应用（function application）：

```
United     serves          Miami
NP         (S\NP)/NP       NP
              >  ← serves 吃掉右边的 NP，变成 S\NP
       <      ← 左边的 NP 吃掉 S\NP，变成 S
```

> `>` = 前向应用（函数在左，参数在右），`<` = 后向应用（函数在右，参数在左）。

**关键洞察**：动词的范畴 $(S\backslash NP)/NP$ 完全编码了其子类框架（subcategorization）——主语在左、宾语在右。语法规则只剩下两条函数应用，所有的句法复杂度都被压入了词典中。

---

## 2. 数学层

### 2.1 范畴的递归定义

范畴集合 $\mathcal{C}$ 由原子范畴递归生成：

- $A \in \mathcal{C}$（$A$ 是原子，如 $S, NP, N$）
- $(X/Y) \in \mathcal{C}$ 且 $(X\backslash Y) \in \mathcal{C}$，若 $X, Y \in \mathcal{C}$

斜杠方向编码了参数位置：$X/Y$ = 右边找 $Y$，返回 $X$；$X\backslash Y$ = 左边找 $Y$，返回 $X$。

### 2.2 三对组合算子

| 算子 | 规则 | 名称 | 语义 |
|------|------|------|------|
| $>$ | $X/Y \quad Y \Rightarrow X$ | 前向应用 | $f(a)$ |
| $<$ | $Y \quad X\backslash Y \Rightarrow X$ | 后向应用 | $f(a)$ |
| $>B$ | $X/Y \quad Y/Z \Rightarrow X/Z$ | 前向组合 | $f(g(\cdot))$ |
| $<B$ | $Y\backslash Z \quad X\backslash Y \Rightarrow X\backslash Z$ | 后向组合 | $f(g(\cdot))$ |
| $>T$ | $X \Rightarrow T/(T\backslash X)$ | 前向类型提升 | 将参数提升为高阶函数 |

**前向/后向应用**是所有范畴语法的基础。**组合**（composition）和**类型提升**（type raising）是 CCG 在基础范畴语法之上的扩展，使其能够处理非常规成分的并列（如 *We flew IcelandAir to Geneva and SwissAir to London*）和长距离依赖。

### 2.3 类型提升的力量

在普通推导中，主语 `United` 是 `NP`（参数）。类型提升将其变为 $S/(S\backslash NP)$——一个**吃 VP 吐 S 的函数**：

$$NP \Rightarrow S/(S\backslash NP)$$

提升后即可使用 $>B$（前向组合）直接与动词合成：`United serves` 变为 $S/NP$（还差一个宾语就成句）。这使得推导**严格从左到右**，更接近人类增量式的语言处理。

---

## 3. 应用：CCGbank 与语义解析

**CCGbank**（Hockenmaier & Steedman, 2007）从 Penn Treebank 自动翻译出 48,934 个带有 CCG 推导的树库，包含 44,000 个词、1,200+ 个范畴。它是 CCG 解析器训练的黄金标准。

**为什么 CCG 是语义解析的事实标准？** 因为句法推导与语义组合是一一对应的。给每个范畴附加 λ-表达式，推导树自动产生组合语义：

$$\text{serves} : \lambda y.\lambda x.\text{serve}(x,y) : (S\backslash NP)/NP$$

```
serves Miami  →  serve(x, Miami)   语义 = λx.serve(x, miami)
United serves Miami  →  serve(united, miami)
```

在 GeoQuery、SPIDER 等语义解析基准上，CCG 是长期主流的形式化工具。

### Supertagging 与 A* 解析

CCG 有 425+ 常用范畴（相比 Penn Treebank 的 45 个 POS），词汇歧义极大。解决方案是 **supertagging**（Bangalore & Joshi 1999）——使用序列标注模型（RNN/Transformer）先为每个词分配范畴分布，再用 **A\*** 启发式搜索寻找最优推导，大幅剪枝。

---

## 4. 代码层

```bash
cd 讲透NLP && python3 experiments/G_ccg_parser.py
```

实验实现了前向/后向应用算子 $(>, <)$ 和前向组合 $(>B)$，在 *United serves Miami* 上完整演示范畴归约 + 语义合成（λ-reduction 同步进行）。

---

## 5. 批判性视角

- **CCG ≠ 万能**：CCG 的表达能力处于 *mildly context-sensitive* 层级（与 TAG、LIG 并列），对自然语言的**绝大部分**够用，但某些跨从句的一致性现象仍需更强机制。
- **词典膨胀是代价**：CCG 将复杂度从规则转移到了词典，一个常见动词可能有 10+ 个范畴条目。对于低资源语言，标注 CCGbank 的成本很高。
- **LLM 时代 CCG 的角色**：现代 LLM 隐式完成句法+语义，不显式构建 CCG 推导。但 CCG 的**透明组合性**在可解释 NLP、形式化验证、低数据语义解析中仍有不可替代的价值——它提供了“每一步都可审计”的语义组合链。

---

## ✍️ 练习

1. ⭐ 给出 *She gave him a book* 的 CCG 推导。双宾语动词 `gave` 的范畴是什么？（提示：$((S\backslash NP)/NP)/NP$。）
2. 用类型提升重写 *United serves Miami* 的推导，使每一步都是前向（从左到右）。
3. ★ 为什么基本范畴语法（只有 $>, <$）表达能力不超过 CFG？组合算子 $(>B, <B)$ 增加了什么？（提示：非成分并列。）

→ [H-句子意义的逻辑表示.md](H-句子意义的逻辑表示.md)：CCG 的范畴推导如何映射到一阶逻辑语义。
