# 讲透形式化验证（Formal Verification）

> 形式化验证是"**用数学证明保证软件永远不会有某类 bug**"的工程学科。从 seL4（2009，第一个全验证的 OS 内核）到 Atmosphere（SOSP 2025，20 秒验证全微内核），2024-2026 这门学科正从"11 人年证明 8.7K 行"进入"工程实用性竞赛"阶段。本系列从"为什么形式化"讲到 Lean4 SOTA，重点是把**形式化方法**和**神经符号 RL**（AlphaProof 式）连起来——这是 2025-2026 的前沿交叉。
>
> 配套：[`讲透神经符号`](../讲透神经符号/)（AlphaProof 闭环）+ [`讲透RL/04`](../讲透RL/04-RL与形式证明.md)（RL 证定理）+ [`讲透可解释性`](../讲透可解释性/)

---

## 篇目

| # | 标题 | 状态 | 核心 |
|---|------|------|------|
| **00** | [为什么形式化 + Lean4 SOTA](./00-为什么形式化+Lean4SOTA.md) | ✅ | seL4→Verus→Atmosphere 演化、Lean4 为何成新宠、`omega` 解不掉的边界、验证剧场陷阱 |
| **01** | [Lean4 作为 RL 奖励验证器：速度可行性](./01-Lean4作为RL奖励验证器.md) | ✅ | 实测 sub-second（14.9× 余量）、三个陷阱（Mathlib/复杂度/稀疏）、与 Alive2 对比 |
| **02** | [从代码到规则：形式化的两层](./02-从代码到规则-形式化的两层.md) | ✅ | 形式化代码（seL4）vs 形式化因果规则（神经符号新范式）|

---

## 怎么用

- **想知道"形式化验证到底验证什么"**：直接读 [00 篇](./00-为什么形式化+Lean4SOTA.md)
- **想把 Lean4 塞进 RL 训练循环**：[00](./00-为什么形式化+Lean4SOTA.md) → [01 篇](./01-Lean4作为RL奖励验证器.md)（速度可行性 + 工程陷阱）
- **想搞 AlphaProof 式神经符号闭环**：[00](./00-为什么形式化+Lean4SOTA.md) → [`讲透神经符号`](../讲透神经符号/)
- **想理解 RL 为什么在形式化域有根本难点**：[00](./00-为什么形式化+Lean4SOTA.md) §五 → [`讲透RL/04`](../讲透RL/04-RL与形式证明.md) §五

---

## 配套

- 实战：[`讲透RL/04-RL与形式证明`](../讲透RL/04-RL与形式证明.md)（AlphaProof 后时代）
- 神经符号闭环：[`讲透神经符号`](../讲透神经符号/)
- RL 能力边界：[`讲透RL/05-RLVR的极限`](../讲透RL/05-RLVR的极限.md)

---

## 🔗 理论锚点（§12-15 横向打通）

> 本系列讲"为什么形式化 + Lean4 SOTA"；名校理论课把每一层**公理化**：
> 枢纽：[`§12-15 整合`](../§12-15%20理论·形式化·安全·可信AI%20整合.md) §21

| 课程 | 产物 | 公理化的内容 |
|---|---|---|
| §13.1 Oxford CPP | [`cpp.py`](../oxford-cs-projects/topic12-foundations/cpp.py) | Curry-Howard + STLC + CCC——Lean4 的类型论根基 |
| §13.2 Cambridge Hoare Logic | [`hoare_logic.py`](../cambridge-cs-projects/topic4-compiler/hoare_logic.py) | Hoare 三元组 + WP + 循环不变式方法（seL4 验证的方法论祖先）|
| §13.3 ETH FM（Basin）| [`formal_methods.py`](../eth-cs-projects/topic3-fm/formal_methods.py) | CTL Model Checking + DPLL + TLA+ 规约 |
| §13.4 CMU 15-414（Platzer）| [`diff_dyn_logic.py`](../cmu-cs-projects/topic12-theory/diff_dyn_logic.py) | differential dynamic logic + barrier certificate（cyber-physical 验证）|

---


---

## 🎭 欺骗动力学视角：数学/程序里藏漏洞

> 承接 [`欺骗动力学-社会进步的隐秘引擎.md`](欺骗动力学-社会进步的隐秘引擎.md) §5。

### 三问

1. **讲透形式化验证 防的是什么欺骗？** → 证明或代码里的错误被人忽略（hand-waving 掩盖漏洞）。
2. **被什么攻破？** → 形式化系统本身的元理论不一致 / 公理选择错误。
3. **沉淀进哪条主链？** → 密码学主链 + 验证主链——Lean4 把证明可信从「人审」变成「机器可检验」。

### 一句话

> 形式化验证是反欺骗的终极形态：把「我相信这个证明」变成「机器必须验证这个证明」。
