# Position Paper 大纲 · 系统域 AlphaProof 的先验修正

> **状态**：大纲就绪，待扩写（R4 建议 6 个月内出 arXiv 预印占位蓝海）
> **理论锚点**：Limit of RLVR（`../explorations/rl/05-paper-limit-of-rlvr.md`）（arXiv:2504.13837, NeurIPS 2025 Oral）
> **核心蓝海**：R4 确认 L2.5+L3 教学 同时 ≥3 的竞品 = 0；B1 确认系统域 RL+形式化 近乎空白

---

## 一、标题候选（3 个，按力度排序）

1. **「Trace is Not Ground Truth: Correcting the Prior Assumption of RLVR in System-Domain Neuro-Symbolic Rule Learning」**
   —— 最尖锐，直接点明核心论点

2. **「Why RL is the Wrong Default for Formal Rule Learning in System Software: A Position Paper」**
   —— B2 建议版，立场清晰，但偏否定

3. **「System-Domain AlphaProof: From Distribution Sharpening to Prior Correction」**
   —— 建设性，把贡献定位为「AlphaProof 范式的系统域扩展」

**推荐**：#1（最尖锐 + 最准确）。

---

## 二、核心论点（一句话）

> **Limit of RLVR 证明 RLVR 在数学域只是「分布锐化器」不扩展推理边界。本 position paper 论证：在系统域，RLVR 不只「不扩展」，还「固化 bug」——因为系统域的先验（trace）可能 buggy，RLVR 会完美证明错误规则。系统域 AlphaProof 必须修正 RLVR 的先验假设：引入独立 ground truth 打破「先验 = trace」的循环。**

---

## 三、目标会议/期刊

| 会议 | 截稿（2026-2027）| 适配度 | 理由 |
|------|---------------|--------|------|
| **NeurIPS 2027**（position track）| 2027-05 | ★★★★ | Limit of RLVR 是 NeurIPS 2025 Oral，接续对话 |
| **ICML 2027**（AI4Math workshop）| 2027-01 | ★★★★ | Limit of RLVR 是 ICML 2025 best paper |
| **CPP 2027**（C++ 形式化方法）| 2026-09 | ★★★ | 形式化方法社区，Lean4 受众 |
| **ITP 2027**（交互式定理证明）| 2027-03 | ★★★ | Lean4/Coq 社区 |
| **ICSE 2027**（软件工程）| 2027-02 | ★★★ | TAAF（ICSE 2026）是近亲，可接续 |

**推荐**：先投 **NeurIPS 2027 position track**（最大曝光 + 接续 Limit of RLVR 对话），同时 arXiv 预印占位。

---

## 四、大纲（position paper 结构，~8-10 页）

### §1 Introduction（1.5 页）
- **2025 RLVR 神话**：DeepSeek-R1/AlphaProof 让 RLVR 被认为「教推理」
- **Limit of RLVR 的反方**：Yue et al. 2025 证明 RLVR 只是分布锐化器
- **本 paper 的扩展**：系统域更危险——不只不扩展，还固化 bug
- **核心贡献**（3 条，见 §五）

### §2 Background（1 页）
- RLVR 基础（GRPO/二元 reward）
- Limit of RLVR 的精确结论（pass@k 反转 + 先验双刃剑）
- 系统域形式化（seL4/Lean4/对抗层）

### §3 🟥 核心论点：Trace is Not Ground Truth（2 页）

#### 3.1 数学域 vs 系统域的根本差异

| 维度 | 数学域（AlphaProof）| 系统域（Neo-OS）|
|------|------------------|---------------|
| 先验 | mathlib（**可信**）| trace（**可能 buggy**）|
| RLVR 锐化后果 | 无害（只是不扩展）| **有害**（固化 bug）|
| reward 可信度 | Lean 证明成立 = 对 | Lean 证明成立 **≠** 对 |

#### 3.2 先验双刃剑的系统域强化

Limit of RLVR §5 的「先验双刃剑」（动作空间大 + 预训练先验）在系统域**加倍致命**：
- 数学域：先验（mathlib）可信 → RLVR 锐化只是不发现新东西
- 系统域：先验（trace）**可能 buggy** → RLVR 锐化**固化 bug** = 完美证明错误规则

#### 3.3 R5§6 命门的形式化

定义「trace 固化 bug」问题：
- 给定 buggy trace T_bug（含错误行为）
- L2 蒸馏出规则 R_bug（编码了 bug）
- Lean4 证明 R_bug 在 T_bug 上成立（数学级 soundness）
- L3 输出「可证明的解释」——但 R_bug 语义错误
- **这是 AlphaProof 范式在系统域的根本不可迁移点**

### §4 解决方案：先验修正（2 页）

#### 4.1 provenance 替代 correctness（S4）
不声称规则「已验证正确」。每条规则标 provenance（多源去相关 + 人工审计）。

#### 4.2 Fixes: 链作 normative signal（S5）
fix commit 把描述性 trace 转规范性信号。比 kernel 文档错误模式更去相关。

#### 4.3 对抗层 v2.0（已实现）
- SpinlockPreempt v2（deadlocked 字段 + 零公理反例定理）
- provenance-only（砍 Oracle/Analyst/闭环）
- ★★★ 重定义（必须人工审计）

### §5 初步实证证据（1.5 页）

#### 5.1 C1 真实抽取（已有）
- 3 个真实 kernel fix commit，抽取率 66.7%（超现实线 40%）
- 证明 commit 蒸馏管线在 kernel(C) 有效

#### 5.2 SpinlockPreempt v2（已有）
- Lean4 证明 sorry 清零
- 但对抗层 v0 实证 Inv 只 1/5 判别力（部分是模型盲点冒充）

#### 5.3 pass@k 实验设计（待补，§六）
- H1：系统域复现 Limit of RLVR 反转
- H2：buggy trace 先验 → RLVR 固化 bug

### §6 Open Questions & Future Work（1 页）
- 系统域 RLVR 是否真能通过「先验修正」变得安全？
- 系统域 f2f 基准的构建（dsyme 716 定理子集）
- 多 agent RL 在系统域的角色（B2 六条铁律）

### §7 Conclusion（0.5 页）
重申核心论点 + 对社区的 actionable insight。

---

## 五、核心贡献（3 条，position paper 的「deliverable」）

1. **理论贡献**：扩展 Limit of RLVR 到系统域——论证「RLVR 在系统域不只不扩展边界，还固化 bug」，原因是先验（trace）不可信。这是 R5§6 命门的理论基础。

2. **方法贡献**：提出「先验修正」框架——provenance tag（S4）+ Fixes: 链 normative signal（S5）+ 对抗层 v2.0（手工 rule sensitivity + ★★★ 重定义）。这是 AlphaProof 范式在系统域的安全扩展。

3. **实证贡献**：SpinlockPreempt v2（Lean4 证明）+ C1 真实抽取（66.7%）+ 对抗层 v0（实证 Inv 不完备）+ pass@k 实验设计（可移植）。蓝海 niche 的首批工件。

---

## 六、待补实验（支撑论点）

| 实验 | 状态 | 支撑 |
|------|------|------|
| C1 扩量到 1000 | 🟡 脚本就绪待跑 | commit 蒸馏管线规模化 |
| **pass@k H1**（系统域复现反转）| 🟡 设计就绪待移植 GPU | RLVR 在系统域是锐化器 |
| **pass@k H2**（buggy 先验固化 bug）| 🟡 设计就绪 | R5§6 命门的实验验证 |
| 对抗层 v1（扩 Inv 到 ≥80% 判别力）| 🟡 v0 已跑 | rule sensitivity 有效性 |

**最小可投稿配置**：C1 扩量 + H1（H2 加分）。

---

## 七、相关工作定位（如何与已有文献区分）

| 相关工作 | 关系 | 区分 |
|---------|------|------|
| **Limit of RLVR**（Yue 2025）| 理论锚点 | 他们数学域；**我们系统域 + 先验修正** |
| **AlphaProof**（DeepMind 2025）| 范式来源 | 他们数学域 ground truth 可信；**我们系统域 trace 不可信** |
| **TAAF**（ICSE 2026）| 最近竞品 | 他们无形式化 + 无 RL 分析；**我们 L2.5 + RLVR 批判** |
| **Lean4Agent**（2026-06）| 最近竞品 | 他们验证 agent workflow；**我们验证系统因果规则 + 先验修正** |
| **Anthropic reward hacking**（arXiv:2511.18397）| 反方证据 | 他们 coding-RL；**我们系统域形式化规则** |

**蓝海确认**：R4 的 14 竞品矩阵里，**无人在 L2.5 形式化 + L3 教学 + RLVR 批判三者交集**。

---

## 八、风险与对策

| 风险 | 对策 |
|------|------|
| 「position paper 无新实验」质疑 | C1 + pass@k H1 作为实证（虽小但真实）|
| 「系统域太小众」质疑 | 强调可迁移性（OS/DB/分布式/编译器都适用）|
| Limit of RLVR 反方被推翻（Diversity Collapse）| 我们的核心论点（trace ≠ GT）独立成立，不依赖 RLVR 争论 |
| 「与 AlphaProof 太近」质疑 | 强调先验修正是 AlphaProof 没有的系统域独有点 |

---

## 九、写作策略

1. **arXiv 预印先行**：2026-09 前出 arXiv 占位（蓝海窗口 12-24 月）
2. **引用 Limit of RLVR 站肩膀**：不否定它，**扩展它**到系统域
3. **诚实标注验证等级**：position paper 的论证 > 实验，不夸大
4. **三份调研做背书**：R5（命门）+ B1（系统域空白）+ B2（生产弃儿）+ Limit of RLVR（理论锚点）

---

## 十、📌 下一步

1. **立即**：把本大纲扩写为 8-10 页草稿（基于已有全部调研，不需新实验）
2. **2026-09 前**：arXiv 预印占位
3. **并行**：C1 扩量 + pass@k H1 作为实证章节
4. **2027-05**：投 NeurIPS 2027 position track

---

*本大纲作为 position paper 的蓝图。已有调研（R2/R4/R5/B1/B2/B3 + Limit of RLVR + 对抗层 v2.0 + C1）足以支撑 8-10 页草稿。核心是站在 Limit of RLVR 肩膀上，论证系统域的先验修正。*
