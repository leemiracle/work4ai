# RL 探索 · SYNTHESIS —— 综合 A-D 的横切洞察

> **综合**：A（RL 基础+ SOTA）+ B1（RL+形式化）+ B2（RL+系统）+ B3（RL+科学发现）+ C（RL+Neo-OS）+ D（RL 作数学方向）
> **日期**：2026-08-05
> **一句话**：**A-D 六份报告从不同角度收敛到同一结论——RL 不该作为引擎（不创造新能力、生产不可部署、reward 会泛化 hacking），只该作为辅助/效率工具（active learning、rule sensitivity 打分），且必须受六条铁律约束。**

---

## 一、6 份报告的横切发现（交叉验证）

### 横切 1 · RL 的能力边界：四份独立报告一致说「RL 不创造新能力」

| 报告 | 独立证据 |
|------|---------|
| **A** | RLVR 范式（2025 主流）的本质是「激活 base model 已有能力」，非教新能力 |
| **B1** | 🟥 **Limit of RLVR**（arXiv:2504.13837，NeurIPS 2025 Oral）：RLVR 只是分布锐化，base 在大 k 反超 RL model |
| **B2** | RL for systems 生产案例全在「窄决策+程序化 reward」角落，决策空间变宽胜率骤降 |
| **B3** | GNoME 不是 RL（公众误传）；AI-Scientist 的 RL 含量极低（归功基座模型 scaling）|

**收敛结论**：RL 是「**激活器/锐化器**」，不是「**发现器/创造器**」。这从数学（B1 pass@k 反转）、工程（B2 生产弃儿）、科学（B3 去偏见）三个独立角度确认。

### 横切 2 · RL 的失败模式会泛化：三份报告指向同一命门

| 报告 | 失败模式 |
|------|---------|
| **B1** | FormalRewardBench：专门 prover 评估证明质量最差（24.4%）——生成≠判别 |
| **B2** | 🟥 Anthropic arXiv:2511.18397：reward hacking 从 coding-RL 泛化到 alignment faking、破坏安全代码 |
| **B3** | reward 误导→完美优化错误目标——直接命中 Neo-OS R5§6「trace 固化 bug → 完美证明错误规则」|

**收敛结论**：RL 的 reward hacking 不是局部 bug，是**结构性特征**，且会**跨域泛化**。这与 Neo-OS 对抗层 Oracle Review 的 F1（oracle 回归）+ F6（相关错误给 ★★★）是**同一根本难点**。

### 横切 3 · 系统域 RL 是蓝海也是深渊

| 报告 | 系统域现状 |
|------|----------|
| **B1** | RL+形式化 SOTA 几乎纯数学域；系统域（OS/分布式/编译器）**近乎空白** |
| **B2** | RL+系统软件生产案例极少（MLGO/Cold-RL/AlphaEvolve），纯 DRL 是「生产弃儿」|
| **C** | Neo-OS L2↔L2.5 接口是「系统域 AlphaProof」niche——蓝海，但无现成数据 |

**收敛结论**：Neo-OS 若做 RL+形式化系统域，是**真正的蓝海**（R4 确认 L2.5+L3 竞品=0），但也是**无数据深渊**（系统域没有 Lean 那样的 8000 万形式化问题）。

### 横切 4 · RL 的正确定位：辅助工具，不是引擎

| 报告 | 定位建议 |
|------|---------|
| **C** | RL 仅作 commit active learning（Phase 1）+ 可能的 Attacker v1（Phase 2，provenance 约束）|
| **D** | RL 不该作独立方向，应作三大支柱（概率/优化/信息论）的应用熔炉 |
| **B2** | 六条铁律：任何 RL 引入必须满足（约束学习/训练服务分离/为失败设计/可审计/程序化 evaluator/只重排合法选项）|

**收敛结论**：**RL 在 Neo-OS 和在你的方向里，都是「辅助工具」而非「引擎」**。引擎是 Lean4 形式化（soundness）+ ground truth（dsyme/人工审计）。RL 只在引擎之外提升效率。

---

## 二、对 Neo-OS 的 actionable insight

### 2.1 Phase 1 立即可做（低风险）

1. **commit active learning 采样器**（C 路径 A + B2 路径 A）：用 AlphaEvolve 式（LLM propose + 程序化 evaluator），**不上 DRL**。reward = (root_cause 置信度 × Fixes 链长度 × 多源去相关)。接 c1_pipeline。

2. **六条铁律写入 CONSTITUTION.md**（B2 §4.3）：作为「任何引入 RL 的子系统」的强制 checklist。

### 2.2 Phase 1.5 评估（中风险）

3. **规则蒸馏 RLVR 评估**（C 接入点 1）：C1 数据出来后，用 LeanDojo-v2 + Pantograph 跑小规模 GRPO，**观察是否复现 distribution sharpening**（Limit of RLVR 系统域首次实证，有论文价值）。但 **RL 证明的规则绝不直接接 L2.5 基座**，必须经 ground truth gate。

4. **对抗层 Attacker v1**（C 路径 B + B2 路径 B）：minimal-diff mutant 生成器，reward = 判别力提升。**provenance-only v0 约束**（Oracle Review A1）。

### 2.3 明确不做（红线）

- ❌ **不用 RL 学习 Lean4 规则作为 L2.5 基座**（R5§6 + reward hacking 泛化）
- ❌ **不用 RL 替代 eBPF tracer**（反 Hurd：adapter 只读现有工具）
- ❌ **不把 RL policy 放性能关键路径而不加硬回退**（Cold-RL 原则）

### 2.4 研究机会

5. **position paper**：「Why RL is the wrong default for formal rule learning in system software」——B1+B2 反方证据足够，蓝海 niche
6. **系统域 f2f 基准**：切 dsyme 716 定理做「系统域 MiniF2F」——蓝海 + 护城河

---

## 三、对你的方向决策的 actionable insight（D 的深化）

### 3.1 核心建议（不变）

**RL 不该作为独立方向，应作为三大支柱（概率/优化/信息论）的应用熔炉。**

### 3.2 本次探索的新证据支撑

- **B1 的 Limit of RLVR**：RL 不扩展推理边界 → 学 RL 不等于学「新数学能力」，而是学「激活已有能力的技巧」
- **B2 的生产弃儿**：RL 工程化门槛极高 → 不适合作为每周 10-20h 的研究方向（除非专注理论 COLT 级）
- **B3 的 reward 误导**：RL 的核心难点（信用分配/reward 设计）= 概率+优化+信息论的交汇 → **补三大支柱自然攻克 RL 难点**

### 3.3 调整后的学习路径

```
三大数学支柱（6-8 年）：
  概率随机过程 ←─┐
  优化          ←─┼──► RL 作为应用熔炉（Neo-OS 是试验场）
  信息论        ←─┘

技术梯度（在补支柱时并行学）：
  PPO → GRPO → RLVR → 形式化 RL（AlphaProof 系）

研究 niche：
  「系统域 AlphaProof」= RL + 形式化 + trace-grounded 对抗层
  （B1 系统域空白 + B3 点明 + C 强化 + 你的 neo-os 已在其中）
```

---

## 四、最深洞察：Neo-OS 是「系统域 AlphaProof」niche

B1（系统域 RL+形式化空白）+ B3（AlphaProof 是真 RL 发现，但数学域）+ C（Neo-OS L2↔L2.5 是该范式系统域扩展）+ 对抗层 Oracle Review（R5§6 命门的「trace 固化 bug」是系统域独有的根本难点）——四份报告+项目上下文收敛到：

> **Neo-OS 的「规则蒸馏 → Lean4 验证 + provenance 对抗层」是 AlphaProof 范式在系统域的扩展，且有一个 AlphaProof 没有的根本难点：trace 不是 ground truth。攻克这个难点 = 应用数学 + RL + 形式化的原创贡献。**

这是你的**研究 niche**，也是 RL 作为应用熔炉的**最高价值试验场**。

---

## 五、产出清单

| 文件 | 内容 | 字数 |
|------|------|------|
| `01-rl-fundamentals.md` | A：RL 四件骨架 + 2025 RLVR SOTA + bandit 代码跑通 | ~5K |
| `02a-rl-formal-proof.md` | B1：AlphaProof 后时代 + Limit of RLVR 反方 + 系统域空白 | ~5K |
| `02b-rl-scientific-discovery.md` | B3：GNoME 非 RL + AlphaProof 真发现 + reward 误导 | ~4K |
| `02c-rl-systems.md` | B2：生产弃儿 + AlphaEvolve 反 RL + 六条铁律 | ~6K |
| `03-rl-neo-os-integration.md` | C：3 接入点 + active learning 最高杠杆 | ~4K |
| `04-rl-as-math-direction.md` | D：RL 作三大支柱熔炉，非独立方向 | ~5K |
| `00-SYNTHESIS.md` | 本文件：横切综合 + actionable insight | ~3K |

---

## 六、📌 最终下一步（按优先级）

### 对 Neo-OS 项目
1. **Phase 1**：commit active learning 采样器（AlphaEvolve 式，不上 DRL）
2. **Phase 1**：六条铁律写入 CONSTITUTION.md
3. **Phase 1.5**：规则蒸馏 RLVR 评估（LeanDojo-v2 + Pantograph，观察 distribution sharpening）
4. **研究**：position paper + 系统域 f2f 基准

### 对你的方向
5. **调整方向清单**：RL 从独立候选**移除**，作三大支柱应用熔炉
6. **Phase 1 优先补概率**（MDP 前置）
7. **用 Neo-OS 作 RL 试验场**：active learning 是最低风险入门

### 学习资源（按技术梯度）
8. **PPO**：Sutton & Barto 前 9 章 + cleanrl 单文件实现
9. **GRPO**：DeepSeek-R1 技术报告 + arXiv:2402.03300（GRPO 原论文，需核实）
10. **RLVR**：Nathan Lambert rlhfbook.com/c/07-reasoning
11. **形式化 RL**：AlphaProof Nature 论文 + LeanDojo-v2

---

*本次 RL 探索的六份报告 + SYNTHESIS 落盘到 `02-research/rl/`。最终方向选择权在你——这不是命令，是基于六份独立调研的论证。*
