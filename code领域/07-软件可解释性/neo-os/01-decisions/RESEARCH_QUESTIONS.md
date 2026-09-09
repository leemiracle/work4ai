# Neo-OS · 研究问题（RESEARCH_QUESTIONS）

> 版本 v2.0。三个 paper-grade 研究点 + 开放问题清单。

---

## Paper #1 · Linux Commit History as Training Corpus for System World Models

**目标会议**：SOSP / OSDI / ACL

**核心问题**：能否从 30 年 Linux commit 历史（~1.3M commits）蒸馏出一个能解释系统行为的 world model？

**子问题**：
- R1.1：从 (commit message, diff) 抽取 (symptom, root_cause, fix) 三元组的准确率上限？（E05 命门）
- R1.2：commit 蒸馏 vs 合成数据 vs 在线 LLM，哪种数据策略最有效？
- R1.3：蒸馏出的 world model 能否泛化到 non-Linux 系统（macOS/Windows/自研 OS）？
- R1.4：survival bias（commit 只含已修复 bug）如何量化与缓解？

**评估基准**：
- Held-out bug 集合（来自 syzkaller + CVE）
- 三元组抽取 precision/recall
- 解释的人工满意度（专家组评分）

**贡献**：
1. 第一个 commit-distilled system world model
2. 公开数据集（commit, trace, explanation）三元组
3. 抽取 pipeline 的 agent 化创新（LLM 主动推理因果链）

---

## Paper #2 · Neuro-Symbolic Trace Explanation with Formal Soundness

**目标会议**：NeurIPS / NeSy / POPL

**核心问题**：如何用 Lean4 形式化规则为 LLM 的 trace 解释提供 soundness 保证？

**子问题**：
- R2.1：系统行为的"因果规则"形式化粒度如何选择？（E03 最大风险）
- R2.2：LLM 归纳规则 + Lean4 验证的闭环（AlphaProof 范式）能否工程化？
- R2.3：不完备性（Gödel）下，如何分级置信度（可证明 / 软规则 / LLM 直觉）？
- R2.4：形式化规则集的完备性 epistemic gap 如何度量与标注？

**评估基准**：
- 形式化规则覆盖率（在 held-out bug 上）
- sound 解释的准确率（应为 100%，否则 Lean4 错）
- 软规则/LLM 层的准确率与误报率

**贡献**：
1. 第一个神经符号 trace-native 解释架构
2. "形式化运行时行为规则"的粒度方法论（属性级 Cedar 范式）
3. 三级置信度体系

---

## Paper #3 · Cognitive Token Cost: A Metric for Democratizing Complex Software

**目标会议**：CHI / CSCW / ASPLOS

**核心问题**：如何度量"人理解复杂软件的认知成本"，并用 Neo-OS 降低它？

**子问题**：
- R3.1：CTC 的操作化定义（公式 + 度量方法）？
- R3.2：基准任务集（覆盖 OS/浏览器/编译器/数据库/分布式 top-K 问题）？
- R3.3：Neo-OS 在 CTC 上相对传统调试（读源码 + Stack Overflow + gdb）的改进倍数？
- R3.4：教学场景能否逼近 Bloom 2-sigma（d≈2.0）？

**评估基准**：
- 标准系统任务集（合成 + 真实混合）
- CTC 量化（定位时间 × 难度 × 尝试次数）
- 对照实验：传统组 / LLM-baseline 组 / Neo-OS 组

**贡献**：
1. CTC 度量体系（把 democratizing systems 从口号变科学指标）
2. 通用复杂软件可解释性的基准
3. 教学场景的 2-sigma 实证

---

## 开放问题清单（按不确定性排序）

### 致命级（Phase 0 必攻）
- **OQ1**：commit 三元组抽取成功率（V25）——决定项目存亡
- **OQ2**：形式化粒度是否存在（V11）——认识论问题，可能伪命题
- **OQ3**：Lean4 还是 Isabelle——已倾向 Lean4，但需 PoC 验证

### 高优先级（Phase 1-2）
- **OQ4**：五原子是否真的领域无关（Phase 2 第二靶子验证）
- **OQ5**：world model 蒸馏 vs 在线 LLM 的成本/质量权衡
- **OQ6**：3% 性能预算下的事件采样策略

### 中优先级（Phase 3）
- **OQ7**：跨域知识迁移（编译器 IR 思想帮浏览器？）
- **OQ8**：GPU/闭源 driver 的可解释性补偿策略
- **OQ9**：分布式因果重放（不需精确复现）

### 长期（Phase 4+）
- **OQ10**：自研 microkernel 是否必要
- **OQ11**：Neo-OS 自身是否是 autopoietic 系统
- **OQ12**：CTC 能否成为行业标准 metric

---

## 与现有工作的差异化（增量矩阵）

| 现有工作 | 它们做 | Neo-OS 增量 |
|---------|--------|------------|
| AIOS / MemGPT | LLM 当 OS 调度器/内存 | LLM 当翻译器（正交）|
| Datadog Bits / Dynatrace | 云端事后统计根因 | 本机常驻/实时/形式化可证明 |
| seL4 | 形式化 kernel 代码正确性 | 形式化解释规则 soundness |
| DTrace / eBPF | 输出结构化 trace | 输出英文因果解释 |
| AlphaProof | 神经符号证明数学定理 | 神经符号解释系统行为 |
| Prophet / APR | 从 commit 学修复补丁 | 从 commit 蒸馏 world model |
| LeanDojo / ReProver | LLM 辅助数学证明 | LLM 辅助 OS 规则形式化 |
| Khanmigo / LLM tutor | 通用 AI 教学 | trace-grounded 系统教学（无幻觉）|

**结论**：Neo-OS 在每个单独维度都有先驱，但**这个特定组合没有祖先**——这是新颖性来源。

---

*研究问题版本 v2.0。详见 [EXPANDED_KNOWLEDGE.md](../02-research/EXPANDED_KNOWLEDGE.md) 第五编架构与红队。*
