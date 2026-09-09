# Provenance Tag 设计（规则可信度的事实记录）

> **目标**：为每条蒸馏出的规则带 provenance tag，**不压缩成单一置信度数字**，让 L3 读者自己解读（Oracle Review S4）
> **依据**：[ADVERSARIAL_LAYER_DESIGN.md v2.0](./ADVERSARIAL_LAYER_DESIGN.md) + [ORACLE_REVIEW_RESPONSE.md](../02-research/deep/ORACLE_REVIEW_RESPONSE.md) S4/S5
> **服务**：对抗层 v2.0 的 ★★★ 重定义 + L3 英文输出的可信度标注

---

## 一、设计原则（Oracle Review 的两个核心洞察）

### S4：provenance 替代 correctness
**不声称规则「已验证正确」**。每条规则标 provenance（来自哪些 commit、匹配哪些文档、几源一致、是否人工审计）。让 L3 读者自己解读。**不引入 oracle 回归**（F1）。

### S5：Fixes: 链是金矿
fix commit 把**描述性 trace 转规范性信号**（fix 定义「正确」）。比 kernel 文档（与 buggy kernel 共享作者）**错误模式更去相关**。是 v0 主力 normative signal。

---

## 二、Provenance Tag JSON Schema

```json
{
  "rule_id": "spinlock_preempt_pair_discipline",
  "lean4_theorem": "NeoOs.SpinlockPreempt.Inv_preserved_over_trace",
  "statement_nl": "持有 spinlock 时 preempt_count 必须 ≥ 1（不可睡眠持锁）",
  
  "provenance": {
    "source_commits": [
      {"hash": "abc123...", "subject": "...", "category": "LOCK_SYNC"},
      {"hash": "def456...", "subject": "...", "category": "LOCK_SYNC"}
    ],
    "matched_docs": [
      {"path": "Documentation/locking/spinlocks.rst", "section": "..."},
      {"path": "kernel/sched/core.c", "line": 1234, "type": "comment"}
    ],
    "source_count": 2,                    // 独立来源数（commit + doc）
    "sources_decorrelated": true,         // 来源错误模式是否去相关
    
    "fixes_chain": {
      "has_fixes_tag": true,              // commit 含 Fixes: 标签
      "fixes_hash": "8510a043d334",       // 被修复的 bug commit
      "normative_signal": "strong"        // fix = 规范性信号强度
    },
    
    "multi_version_consensus": null,      // mainline/stable/longterm 一致性（v1+）
    
    "human_audited": {
      "audited": false,                   // 是否人工审计
      "auditor": null,                    // 审计者（kernel 工程师 id）
      "audit_date": null,
      "audit_verdict": null               // approve / reject / needs_revision
    },
    
    "lean4": {
      "proven": true,                     // Lean4 证明通过
      "axiom_record": ["propext", "Quot.sound"],  // 公理依赖
      "sorry_free": true,                 // 无 sorry
      "independent_check": false          // 是否经 nanoda/lean4lean 交叉核验
    },
    
    "adversarial_layer": {
      "tested": true,                     // 对抗层 v0 测试过
      "discriminating_power": 0.2,        // 判别率（v0: B1b 配对纪律）
      "blind_spots": ["B1a", "B2a", "B3"] // 盲点列表
    }
  },
  
  "confidence_level": 2,                  // ★★★(3) / ★★(2) / ★(1)
  "confidence_rationale": "Lean4 证明通过 + 2 源（commit + doc）+ Fixes 链，但未人工审计"
}
```

---

## 三、三级置信度重定义（基于 provenance，F6）

| 等级 | 条件 | L3 输出策略 |
|------|------|-----------|
| **★★★** | Lean4 证明（sorry 清零）+ provenance **≥3 源去相关** + **至少 1 源人工审计** + 对抗层判别率 ≥0.8 | 「可证明的解释」+ 标注 provenance |
| **★★** | Lean4 证明 + provenance ≥2 源（部分去相关）+ Fixes 链 | 「软规则」+ 标注 provenance |
| **★** | Lean4 证明（无 provenance 或单源）| 「形式证明级」+ 明确标注「未经独立验证」|

**关键（F6）**：★★★ **必须有人工审计**。不再有「自动 ★★★」——三方错误正相关时「自动一致」是最强假信号。

---

## 四、Fixes: 链作 normative signal（S5）

### 4.1 为什么 Fixes: 链是金矿

| 信号类型 | 描述性 vs 规范性 | 错误相关性 | 可信度 |
|---------|---------------|----------|--------|
| 普通 commit message | **描述性**（系统做了什么）| 与 buggy kernel 同源 | 低 |
| kernel 文档 | 规范性但可能过时 | 与 buggy kernel **共享作者** | 中 |
| **Fixes: 链** | **规范性**（系统**应该**做什么）| fix 修复 bug = **错误模式去相关** | **高** |

### 4.2 c1_pipeline 的 fix 字段作 normative signal

c1_pipeline.py 已抽取 `(symptom, root_cause, fix)` 三元组。**`fix` 字段是规范性信号的源头**。

集成方式：
```python
# c1_pipeline 输出的 fix 字段
{
  "fix": "remove volatile id from owner's idr while holding table lock",
  "fixes_chain": {                    # 新增：从 commit message 的 Fixes: 行提取
    "has_fixes": true,
    "fixes_hash": "8510a043d334",
    "normative_signal": "strong"      # 有 Fixes: = 强规范性
  }
}
```

### 4.3 provenance 打分公式（v0 占位，待 N≥10 校准）

```
provenance_score = 0.4 × fixes_signal      # Fixes 链（最强）
                 + 0.3 × source_count_norm  # 多源去相关
                 + 0.2 × doc_match          # 文档匹配
                 + 0.1 × multi_version      # 多版本一致（v1+）
```

⚠️ **阈值无根据（Oracle I7）**：0.7/0.2 是占位，待 N≥10 规则后用实际分布校准。

---

## 五、与 c1_pipeline 的集成

### 5.1 c1_pipeline 输出端加 provenance

在 `c1_pipeline.py` 的 `extract_l2` 函数输出中，新增字段：
- `fixes_chain`：从 commit body 的 `Fixes: <hash>` 行提取
- `source_type`：标记来源（kernel/etcd/raft）

### 5.2 规则库构建时聚合 provenance

当多条 commit 蒸馏出同一规则（rule_id 相同）时，聚合 provenance：
- `source_count` += 1
- `sources_decorrelated` = 检查来源是否跨子系统/跨版本
- `fixes_chain` 合并

---

## 六、与对抗层 v2.0 的一致性

| 对抗层 v2.0 组件 | provenance tag 的对应 |
|---------------|-------------------|
| ★★★ 重定义（F6）| `human_audited.audited == true` + `source_count >= 3` |
| Oracle 砍掉（F2）| provenance 替代 Oracle（S4）—— 不引入 LLM 形式化文档的幻觉 |
| Analyst 砍掉（S6）| provenance 是**事实记录**，不需 Analyst 压缩成置信度 |
| 手工 rule sensitivity（F3）| `adversarial_layer.discriminating_power` 记录判别率 |

---

## 七、实施路线

### Phase 1（立即，与 C1 扩量并行）
1. **c1_pipeline 加 Fixes: 提取**：parse commit body 的 `Fixes: <hash>` 行
2. **规则库 provenance 聚合**：同 rule_id 的 commit 聚合 source_count
3. **三级置信度 JSON 输出**：给 L3 英文层用

### Phase 1.5（C1 扩量到 1000 后）
4. **多版本一致性**：mainline/stable/longterm 对比（需多版本 commit 数据）
5. **人工审计 gate**：★★★ 规则经 kernel 工程师审计
6. **provenance 阈值校准**：N≥10 规则后用实际分布调 0.7/0.2

---

## 八、🟥 核心约束（不可违反）

1. **provenance 是事实记录，不是可信度判断**（S4）—— L3 读者自己解读
2. **★★★ 必须人工审计**（F6）—— 自动一致 ≠ 正确
3. **Fixes: 链是 normative signal，不是 ground truth**（S5）—— fix 可能 fix 了错误方向
4. **不引入 oracle 回归**（F1）—— provenance 来自多源，不依赖单一「独立 oracle」

---

*provenance tag 设计作为对抗层 v2.0 的可信度基础设施。与 c1_pipeline 集成，服务 L3 英文输出的诚实标注。*
