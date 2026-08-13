# 讲透神经符号（Neuro-Symbolic）

> 神经符号（Neuro-Symbolic）是"**LLM 生成 + 符号验证**"的闭环——LLM 负责直觉生成（像人猜思路），符号系统（Lean4 / TLA+ / Z3）负责严格验证（像人写证明）。AlphaProof 用这个闭环拿 IMO 银牌，Delta-Prover 用它零微调达 95.9%，KVerus 用它验证真实 OS 内核。本系列讲清楚这个 2025-2026 最热的范式：**它的奇迹、它的陷阱（生成≠判别）、它为什么会重塑"AI 能否可信"的讨论**。
>
> 配套：[`讲透形式化验证`](../讲透形式化验证/)（Lean4 背景）+ [`讲透RL/04`](../讲透RL/04-RL与形式证明.md)（AlphaProof 谱系）+ [`讲透可解释性`](../讲透可解释性/)

---

## 篇目

| # | 标题 | 状态 | 核心 |
|---|------|------|------|
| **00** | [神经符号循环为什么是新范式](./00-神经符号循环为什么是新范式.md) | ✅ | LLM 生成 + Lean 验证闭环、AlphaProof/Delta-Prover/KVerus SOTA、基准自验证破灭、系统域根本难点 |
| 01 | VERISPECGEN：从需求到 spec | 🟡 | NL→Lean4 spec 合成，原子分解 + 可溯性 |
| 02 | 神经符号的对抗层 | 🟡 | 找反例 trace（prover/disprove 之外的第三条路）|

---

## 怎么用

- **想懂 AlphaProof 怎么工作**：[00](./00-神经符号循环为什么是新范式.md) §二
- **想在系统域用神经符号**：[00](./00-神经符号循环为什么是新范式.md) §五（系统域根本难点）
- **想理解为什么"90% 精度"是假象**：[00](./00-神经符号循环为什么是新范式.md) §四（基准破灭）

---

## 配套

- 形式化背景：[`讲透形式化验证`](../讲透形式化验证/)
- RL + 形式证明：[`讲透RL/04`](../讲透RL/04-RL与形式证明.md)
- RL 能力边界：[`讲透RL/05`](../讲透RL/05-RLVR的极限.md)

---

## 🔗 理论锚点（§12-15 横向打通）

> 本系列讲"LLM + Lean4 闭环 / AlphaProof"；名校理论课把"自指 + 类型论"**公理化**：
> 枢纽：[`§12-15 整合`](../§12-15%20理论·形式化·安全·可信AI%20整合.md) §21

| 课程 | 产物 | 公理化的内容 |
|---|---|---|
| §12.2 CMU 15-251 GITCS | [`gitcs.py`](../cmu-cs-projects/topic12-theory/gitcs.py) | Y combinator / Lawvere 不动点——自指的 constructive 版（AlphaProof 闭环的数学骨架：AI 用形式系统验证自己的输出）|
| §13.1 Oxford CPP | [`cpp.py`](../oxford-cs-projects/topic12-foundations/cpp.py) | STLC + Curry-Howard + CCC——Lean4 / Coq 的类型论地基（LLM 生成 Lean4 代码 = LLM 在做证明）|
