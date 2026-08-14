# 02 · PROLOG 到 Answer Set 到 ASP：符号推理语言的演化

> 承接 [01-一阶逻辑与谓词演算](./01-一阶逻辑与谓词演算.md)。01 讲了 FOL 的数学内核和归结。本章讲**符号推理语言的工程演化**——从 PROLOG（1972）到 Answer Set Programming（ASP，1999）——并指出：每一次演化都是在补 FOL 的某个洞（否定、默认推理、并行模型），而 LLM 在 2023+ 用自然语言"软性"补了同样的洞，但代价是失去可判定性。

---

## 直觉层

### 一个具体时刻

> 1972 年，Alain Colmerauer 在马赛大学做出 PROLOG（PROgramming in LOGic）。**角色**：Colmerauer。**冲突**：他要做自然语言理解，FOL 太通用，不能直接当编程语言跑。**时刻**：他限定 FOL 到 **Horn 子句**（至多一个正文字），让"声明式编程"第一次可执行——你写"什么是真的"，引擎算"结论"。这是符号主义的**工程巅峰**：把推理本身做成语言。

但 PROLOG 有个致命缺陷：它用 **NEGATION AS FAILURE (NAF)**——"查不到就当不存在"——这违反经典逻辑的开放世界假设。

> 1999 年，Vladimir Lifschitz 与 Michael Gelfond 提出 **Answer Set Programming (ASP)**，基于**稳定模型语义**。它**正面接受**默认推理：你说"鸟会飞"，加上"除非有例外"，ASP 会生成多个"answer set"（可能的世界）。这是 PROLOG 的进化版——专门为**组合优化 + 常识推理**而生。

### 为什么 LLM 时代要读

LLM 用"概率化默认推理"绕过了 PROLOG 的 NAF 问题——它会说"企鹅不会飞，因为训练数据这么说"。但 LLM **不能给出模型集**——它给一个最可能答案，而不是所有可能世界。**ASP 给的是可枚举的世界集；LLM 给的是边际最高的那个**。这是"推理"与"猜测"的根本差异。

---

## 数学层

### PROLOG = Horn 子句 + SLD 归结

Horn 子句：至多一个正文字的析取。

$$\text{Head} \leftarrow \text{Body}_1 \land \text{Body}_2 \land \cdots \land \text{Body}_n$$

PROLOG 程序就是一组 Horn 子句，引擎用 SLD（Selective Linear Definite）归结做反向链推理。**优势**：可实现、可判定（Datalog 子集）、声明式。**劣势**：NAF 在经典 FOL 下无严格语义。

### ASP = 稳定模型语义

ASP 把一个逻辑程序 $P$ 的"answer set"定义为 $P$ 的一个**极小模型** $M$，使得 $M$ 是 $P$ 在 $M$ 自身重写（把 `not b` 替换为真/假）后的唯一最小模型。

$$M \models P \;\iff\; M = \text{LM}(P^M)$$

其中 $\text{LM}$ 是最小 Herbrand 模型，$P^M$ 是化简程序。一个程序可以有 **0、1 或多个** answer set——**多模型 = 多个可能世界**。

### ASP 的"约束"算子

```asp
% 规则
1 { color(X,C) : C = 1..3 } 1 :- node(X).   % 每个节点恰好一种颜色
:- edge(X,Y), color(X,C), color(Y,C).        % 相邻节点不同色
```

`:-` 是约束——若违反，整个 answer set 被剔除。**这是 NP 完全问题（图着色）的几行表达**——ASP 求解器（clingo）直接枚举所有解。

### 适用边界

- PROLOG 擅长：演绎查询（祖先、家族树、语法解析）。
- ASP 擅长：组合优化（排班、配置、规划），因为它原生支持多模型 + 约束。
- 两者都**不擅长**：感知、学习——这是 LLM 的领域。
- **复杂度边界**：ASP 的判定问题是 $\Sigma_2^P$-完全——比 NP 还高一档。可解但昂贵。

---

## 代码层

PROLOG 经典例子（用 `swipl` 或 Python 的 `pyswip`）：

```python
from pyswip import Prolog
prolog = Prolog()
prolog.assertz("parent(tom, bob)")
prolog.assertz("parent(bob, ann)")
prolog.assertz("ancestor(X,Y) :- parent(X,Y)")
prolog.assertz("ancestor(X,Y) :- parent(X,Z), ancestor(Z,Y)")
print(list(prolog.query("ancestor(tom, Who)")))
# [{'Who': 'bob'}, {'Who': 'ann'}]
```

ASP 等价程序（用 `clingo` Python API）：

```python
import clingo
prog = """
parent(tom, bob). parent(bob, ann).
ancestor(X,Y) :- parent(X,Y).
ancestor(X,Y) :- parent(X,Z), ancestor(Z,Y).
#show ancestor/2.
"""
ctl = clingo.Control()
ctl.add("base", [], prog)
ctl.ground([("base", [])])
models = []
with ctl.solve(yield_=True) as h:
    for m in h:
        models.append([str(s) for s in m.symbols(atoms=True)])
print(models)  # 单一稳定模型：ancestor(tom,bob), ancestor(tom,ann), ancestor(bob,ann)
```

加上默认推理的差异就出来了：

```asp
bird(tweety). bird(penguin).
penguin(penguin).
flies(X) :- bird(X), not penguin(X), not abnormal(X).   % 默认会飞，除非例外
```

PROLOG 用 `not` 也有类似效果，但 ASP 给出严格的**稳定模型语义**，PROLOG 的 NAF 只有程序级语用。

**LLM 对比**：问 LLM "tweety 会飞吗"，它答"会"——但它没区分"默认会飞"和"必然会飞"。ASP 区分。这是 LLM 推理的**类型错误**——它把概率默认当逻辑必然。

---

## 不足层

- **已证明**：Horn 子句的可判定性（Datalog）；ASP 的稳定模型语义在命题层面是 NP/co-NP 完备的。
- **经验但未证**：在工业配置/排班上（如 2010s 西门子、CMU 的机器人路径规划），ASP 求解器在 100K 变量规模下仍可用——但这是经验，没有"为何 scalable"的理论。
- **未解**：
  1. **学习规则本身**：ASP 规则要人写，这是 CYC 瓶颈的延续。ILP（归纳逻辑编程）试图学规则，但规模远不及神经网络。
  2. **LLM + ASP 的端到端训练**：LLM 生成 ASP 程序，ASP 求解返回答案——但梯度无法穿过求解器。这是神经符号的核心开放问题（[`讲透神经符号`](../讲透神经符号/)）。
  3. **可解释 vs 可信赖的鸿沟**：ASP 给的"answer set"对工程师可解释，对终端用户仍然抽象。

---

## 📌 下一步 + ✍️ 练习

- **下一章**：[03-知识图谱与本体](./03-知识图谱与本体.md)——从推理语言转向**知识表示**的语言（RDF/OWL）。
- **练习**：
  1. 用 clingo 写一个 N-皇后问题的 ASP 程序（5 行内），运行验证。
  2. 让 LLM 解 N=8 皇后，记录它给出的解数量 vs clingo 给出的全部解数量。思考"完整枚举" vs "采样"的工程含义。

---

## 费曼回炉记录（L2 自检）

- **F2 卡壳点**：我最初把 ASP 和 PROLOG 的差异简化成"ASP 是 PROLOG 的升级版"。重读 Gelfond-Lifschitz 1988 后发现，关键是**语义**而非语法——ASP 的稳定模型语义把 NAF 升级成严格的极小模型，而 PROLOG 的 NAF 是程序执行策略。两者语法相似，语义根基不同。
- **F3 术语翻译**：
  - "Horn 子句" → 至多一个"正面说法"的句子，比如"A 成立如果 B 和 C 都成立"。
  - "稳定模型" → 一个能"自我支撑"的世界：把世界里的所有"非"按这个世界解释后，规则恰好生成这个世界本身。
  - "NAF（negation as failure）" → 查不到就算假——日常常识推理就是这样。
- **F4 回炉**：v1 只讲 PROLOG，没讲 ASP；v2 加入 ASP，因为只讲 PROLOG 会让读者以为符号推理语言 1972 年就停滞了——其实 ASP 在 2000s 工业部署很广，且它是"多模型推理"的代表，对照 LLM 的"单答案"模式特别清楚。

---

## 🔗 跨系列引用

- 元理论：[`故事即世界迭代器-元理论.md`](../故事即世界迭代器-元理论.md) §断言 4（ASP 多模型 = 多个候选"故事"，LLM 单模型 = 边际最高故事）。
- 上游：[`01-一阶逻辑与谓词演算`](./01-一阶逻辑与谓词演算.md)
- 下游：[`03-知识图谱与本体`](./03-知识图谱与本体.md)
- 神经符号桥：[`讲透神经符号/01-VERISPECGEN`](../讲透神经符号/01-VERISPECGEN-从需求到spec.md)（LLM 生成 spec + 符号求解 = 隐式 ASP）。
- 形式化背景：[`讲透形式化验证`](../讲透形式化验证/)
