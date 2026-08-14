# 讲透符号主义（Symbolicism / GOFAI / Neurosymbolic）

> **博士级地基**——AI 史上最被低估的范式。被连接主义"杀死"过两次，但**每次都复活**。2024-2026 的 Neurosymbolic + AlphaProof 证明符号主义没死。
>
> 一句话定位：[`讲透基础模型`](../讲透基础模型/) 讲神经派，本系列讲**符号派**——以及它们为什么必须融合。
>
> 配套：[`讲透AI历史`](../讲透AI历史/)（符号→连接大战）+ [`讲透AI应用全景/02-AI4Math`](../讲透AI应用全景/02-AI4Math.md)（AlphaProof = 神经+符号）

---

## 为什么单独开

- **AI 史最被低估**——符号主义不是"失败"，是"被吸收"
- **Neurosymbolic 是 2024+ 热点**——AlphaProof / AlphaGeometry / Lean
- **博士必修**：不懂符号主义，看不懂 Neurosymbolic 的另一半

---

## 篇目

### 基础层（00-06）

| # | 标题 | 核心 |
|---|------|------|
| **00** | [符号主义是什么](./00-符号主义是什么.md) | GOFAI 定义 + 物理符号系统假设 |
| **01** | [一阶逻辑与谓词演算](./01-一阶逻辑与谓词演算.md) | 谓词逻辑 / 演绎 / 归纳 / 溯因 + LLM 推理的模糊版 |
| **02** | [PROLOG 到 AnswerSet 到 ASP](./02-PROLOG到AnswerSet到ASP.md) | 符号推理语言演化 + 与 LLM 对比 |
| **03** | [知识图谱与本体](./03-知识图谱与本体.md) | RDF / OWL / Wikidata / 神经符号桥 |
| 04 | 知识图谱（旧版） | RDF / OWL / Wikidata / Google KG |
| 05 | 自动推理 | 定理证明 / SAT 求解 / SMT |
| 06 | Prolog 与逻辑编程 | Horn 子句 / unification |

### advanced 层（博士级，4 篇）

| # | 标题 | 核心 |
|---|------|------|
| A00 | 必读论文 + 书 | McCarthy / Minsky / Newell-Simon / CYC |
| A01 | Neurosymbolic AI | 神经+符号融合 / DeepProbLog / AlphaProof |
| A02 | 符号主义为什么"死而复生" | 历史与未来 |
| A03 | 开放问题 | LLM + 符号 + 因果 + world model 的融合 |

---

## 配套

- 历史：[`讲透AI历史`](../讲透AI历史/)（符号→连接大战）
- 应用：[`讲透AI应用全景/02-AI4Math`](../讲透AI应用全景/02-AI4Math.md)（AlphaProof）
- 因果：[`讲透因果推断`](../讲透因果推断/)（符号版的因果）
- 哲学：[`讲透科学的现代性/03`](../讲透科学的现代性/03-AI时代的科学哲学.md)

---

## 🔗 理论锚点（§12-15 横向打通）

> 本系列讲"符号主义 vs 连接主义"的思想史；名校理论课把符号系统的**边界公理化**：
> 枢纽：[`§12-15 整合`](../§12-15%20理论·形式化·安全·可信AI%20整合.md) §21

| 课程 | 产物 | 公理化的内容 |
|---|---|---|
| §12.2 CMU 15-251 GITCS | [`gitcs.py`](../cmu-cs-projects/topic12-theory/gitcs.py) | Gödel 不完备定理（自指/不动点/Y combinator）——符号主义形式系统的数学边界 |
| §13.1 Oxford CPP | [`cpp.py`](../oxford-cs-projects/topic12-foundations/cpp.py) | Curry-Howard 同构（命题=类型=定理）——符号推理的计算根基 |
