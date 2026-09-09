# C · RL 接入 Neo-OS 的方案

> **探索维度 C**：把 RL 视角接入刚做的 Neo-OS 工作（对抗层/规则蒸馏/commit 抽取）
> **依赖**：A（RL 基础）+ B3（RL+形式化的 AlphaProof 启示）+ 项目上下文（R5§6 命门 + 对抗层 v2.0）
> **结论先行**：RL 接入 Neo-OS 有三个点，但**只有一个在 Phase 1 可行**（commit active learning），另两个需等 Phase 1.5+ 且都受 R5§6 命门约束

---

## 一、三个 RL 接入点

### 接入点 1：L2 规则蒸馏的 RLVR（AlphaProof 范式）🟡 Phase 1.5+

**机制**：把规则蒸馏建模为 MDP
- 状态：commit message + 已生成的 Lean4 规则片段
- 动作：生成下一个 Lean4 token / tactic
- reward：Lean4 验证通过 = 1，否则 0（RLVR，可验证 reward）
- 策略：LLM（通用编码模型，非数学 prover——R5 §4 建议）

**对标**：AlphaProof（Nature 2025）/ DeepSeek-Prover-V2 / Seed-Prover heavy（R5 报告已分析）

**可行性**：🟡 **Phase 1.5+**，不是 Phase 1
- 需要先有 C1 真实抽取的规则数据（Phase 1 产出）
- 需 Lean4 验证后端（kimina-lean-server 或 lake）
- 算力：7B 推理 + 批量验证，可行（R5 §4.4）

**🟥 根本约束（R5§6 命门）**：
- RLVR 的 reward = "Lean4 证明成立"
- 但 Neo-OS 的 trace 可能固化 bug → 规则可能编码错误行为
- Lean4 会完美证明错误规则 → reward=1 → RL 强化错误路径
- **这是 AlphaProof 范式在系统域的根本不可迁移点**（R5 §6 + 对抗层 v2.0 已分析）
- 缓解：对抗层 v2.0 的 provenance + Fixes: 链作 normative signal（但不能消除）

### 接入点 2：对抗层 Attacker 的突变策略学习 🔴 Phase 2+（v2.0 已砍）

**机制**：用 RL 学习最有破坏力的 mutant 策略
- 状态：当前 Inv/safe 定义
- 动作：选择突变算子 + 突变点
- reward：mutant 让规则失效 = 1（找到了盲点）
- 策略：curiosity-driven RL（鼓励探索新失败模式）

**对标**：LeVer Attacker Agent（ACL 2026）/ curiosity-driven exploration（KARL 2026）

**可行性**：🔴 **Phase 2+，v2.0 已砍自动化对抗层**
- Oracle Review 判 v2.0 砍掉 Attacker 自动化（A1 方案）
- v0 仅作方法论原型，生产对抗层推迟到 Phase 1.5
- 即使重建，RL Attacker 是 Phase 2 研究问题

**结论**：这个接入点在 v2.0 设计下**不推荐近期做**。

### 接入点 3：commit 蒸馏的 active learning 🟢 Phase 1 立即可行

**机制**：用 RL（bandit）选最有信息量的 commit 抽取
- 状态：已抽取的 commit 类别分布 + 当前候选 commit
- 动作：抽取 / 跳过 / 标注
- reward：抽取的 commit 提供新规则模式 = 1，重复 = 0
- 策略：k-armed bandit（A 文档的 rl_bandit.py 已示范）或 contextual bandit

**可行性**：🟢 **Phase 1 立即可行**
- 不需 Lean4 验证后端
- 不需大量算力（bandit 是最轻量 RL）
- 直接接 c1_pipeline.py（已跑通）
- 用 A 文档的 bandit 代码作起点

**价值**：
- 解决 C1 扩量的「选哪些 commit」问题（1000 个里选最有信息量的）
- 按 category 分层抽样（council D1）的 RL 化版本
- 低风险（bandit 不引入 RL 的不稳定性）

---

## 二、推荐路径（按 Phase + 风险排序）

| Phase | 接入点 | RL 方法 | 风险 | 价值 |
|-------|--------|---------|------|------|
| **Phase 1**（立即）| **接入点 3：commit active learning** | k-armed/contextual bandit | 🟢 低 | C1 扩量优化 |
| Phase 1.5 | 接入点 1：规则蒸馏 RLVR（评估）| GRPO + Lean4 reward | 🟡 中（R5§6 命门）| AlphaProof 范式系统域扩展 |
| Phase 2+ | 接入点 2：Attacker RL（如果重建对抗层）| curiosity-driven | 🔴 高（v2.0 已砍）| 自动红队 |

**核心建议**：**Phase 1 只做接入点 3（bandit）**。接入点 1 需等 C1 数据 + 评估 R5§6 命门的缓解效果。接入点 2 推迟。

---

## 三、接入点 3 的最小实现（可立即做）

基于 A 文档的 `rl_bandit.py`，扩展为 contextual bandit 选 commit：

```python
# commit_active_learning.py（伪代码骨架）
# 用 contextual bandit 选最有信息量的 commit 抽取
import numpy as np

class CommitBandit:
    """按 category 维护臂，优先选当前信息量最高的 category"""
    def __init__(self, categories):
        self.categories = categories  # [LOCK_SYNC, MEM_REF, CONCURRENCY, ...]
        self.Q = {c: 0.0 for c in categories}  # 估计的信息量
        self.N = {c: 0 for c in categories}    # 抽取次数
    
    def select(self, eps=0.1):
        # ε-greedy：以 ε 探索新 category，否则选当前最优
        if np.random.random() < eps:
            return np.random.choice(self.categories)
        return max(self.Q, key=self.Q.get)
    
    def update(self, category, reward):
        # reward = 该 commit 是否提供新规则模式（0/1）
        self.N[category] += 1
        self.Q[category] += (reward - self.Q[category]) / self.N[category]
```

**接 c1_pipeline**：在 `c1_pipeline.py run` 时，用 bandit 选 commit 而非顺序遍历。reward = L2 抽取的三元组是否含新 root_cause 模式（去重后）。

---

## 四、RL 接入与对抗层 v2.0 的关系

**关键澄清**：v2.0 砍了对抗层的自动化，**不等于砍掉所有 RL**。

- ❌ 砍的：Oracle Agent 的 LLM 形式化（F2）/ Attacker 自动化（A1）/ Analyst 闭环（I4）
- ✅ 留的：commit active learning（bandit，低风险）/ 规则蒸馏 RLVR（Phase 1.5 评估）

**RL 在 Neo-OS 的正确姿态**：
1. **不作为可信度来源**（v2.0 已否定 RL 自动判 ★★★）
2. **作为效率工具**（active learning 选 commit，降低 C1 扩量成本）
3. **作为研究 niche**（Phase 1.5+ 的规则蒸馏 RLVR，对标 AlphaProof 系统域扩展）

---

## 五、🟥 最深洞察：Neo-OS 是 RL + 形式化的「系统域 AlphaProof」

B3 调研的核心启示：AlphaProof 证明了「RL + 形式化 = 用数学发现数学」。Neo-OS 的 L2↔L2.5 接口（规则蒸馏 → Lean4 验证）**正是这个范式在系统域的扩展**——但有一个 AlphaProof 没有的根本难点：

| 维度 | AlphaProof（数学域）| Neo-OS（系统域）|
|------|------------------|---------------|
| ground truth | Lean4 证明成立 = 对 | Lean4 证明成立 ≠ 对（trace 可能 buggy）|
| reward 可信度 | ✅ 绝对可信 | 🟥 受 R5§6 命门污染 |
| RL 收敛 | 收敛到正确规则 | 可能收敛到固化 bug 的规则 |

**这就是你的研究 niche**：在系统域修正 AlphaProof 范式——对抗层 v2.0 的 provenance + Fixes: 链就是第一步修正。如果做出来，这是**应用数学 + RL + 形式化的原创贡献**（B3 §三.2 已点明）。

---

## 六、📌 下一步

1. **Phase 1 立即**：实现 `commit_active_learning.py`（bandit），接 c1_pipeline，优化 C1 扩量的 commit 选择
2. **Phase 1.5 评估**：C1 数据出来后，评估规则蒸馏 RLVR 的可行性（需先评估 R5§6 命门的缓解）
3. **研究定位**：把「系统域 AlphaProof」（RL + 形式化 + trace-grounded 对抗层）作为论文 niche——这是 RL + 应用数学 + 形式化的交汇，蓝海

---

*C 文档作为 RL 接入 Neo-OS 的工程方案。与 D（RL 作为数学方向）呼应：Neo-OS 是 RL 作为应用熔炉的天然试验场。*
