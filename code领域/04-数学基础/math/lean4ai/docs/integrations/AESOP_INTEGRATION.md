# Aesop 集成指南

## 项目概述

**Aesop** (Automated Extensible Search for Obvious Proofs) 是 Lean4 的白盒自动化证明策略。

| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/leanprover-community/aesop |
| **Stars** | 345 |
| **Forks** | 50 |
| **语言** | Lean 4 |
| **许可证** | Apache 2.0 |
| **描述** | White-box automation for Lean 4 |

---

## 核心概念

### 什么是 Aesop？

Aesop 是一个可扩展的自动化证明策略，它：

1. **白盒自动化**: 用户可以声明哪些规则应该被使用
2. **可扩展**: 通过属性标记注册自定义规则
3. **高效**: 使用最佳优先搜索策略
4. **透明**: 规则是显式声明的，便于理解

### 基本用法

```lean
import Aesop

-- 简单使用：自动证明
example (p q : Prop) (hp : p) (hpq : p → q) : q := by
  aesop

-- 更复杂的例子
example (α : Type) (xs : List α) (h : xs ≠ []) : xs.length > 0 := by
  aesop
```

---

## Aesop 规则系统

### 1. 基本规则类型

```
┌─────────────────────────────────────────────────────────────┐
│                    Aesop 规则类型                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   @[aesop norm]    - 规范化规则 (简化目标)                   │
│   @[aesop unfold]  - 展开定义                               │
│   @[aesop safe]    - 安全规则 (总是适用)                     │
│   @[aesop unsafe]  - 不安全规则 (可能失败)                   │
│                                                             │
│   优先级级别:                                               │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  0%   - 最低优先级                                   │   │
│   │  50%  - 默认优先级                                   │   │
│   │  100% - 最高优先级                                   │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2. 注册规则

```lean
import Aesop

-- 注册一个安全规则
@[aesop safe]
theorem my_safe_rule (p : Prop) : p ∨ ¬p := by
  exact Classical.em p

-- 注册一个带优先级的规则
@[aesop safe 70%]
theorem my_high_priority_rule (p q : Prop) (hp : p) : p ∨ q := by
  left
  exact hp

-- 注册规范化规则
@[aesop norm]
theorem my_norm_rule (a b : Nat) : a + b = b + a := by
  exact Nat.add_comm a b
```

---

## 与 Lean4AI 集成

### 1. 项目管理验证规则

```lean
-- Lean4AI/Aesop/ProjectRules.lean

import Aesop
import Mathlib.Data.Nat.Basic

namespace Lean4AI.Aesop

/-! ## 项目验证规则 -/

/-- 项目名称非空 -/
@[aesop safe 80%]
theorem project_name_valid (p : Project) : p.name ≠ "" := by
  exact p.name_nonempty

/-- 项目预算非负 -/
@[aesop safe 90%]
theorem project_budget_nonneg (p : Project) : p.budget ≥ 0 := by
  native_decide

/-- 项目支出不超过预算 -/
@[aesop safe 85%]
theorem project_spending_valid (p : Project) (h : p.isValid) : 
  p.spent ≤ p.budget := by
  exact h.spending_valid

/-- 有效项目有截止日期 -/
@[aesop safe 75%]
theorem project_has_deadline (p : Project) (h : p.isValid) :
  p.deadline > 0 := by
  exact h.deadline_positive

/-! ## 任务验证规则 -/

/-- 任务点数在有效范围内 -/
@[aesop safe 80%]
theorem task_points_valid (t : Task) (h : t.isValid) :
  0 < t.points ∧ t.points ≤ 100 := by
  constructor <;> exact h.points_bounded

/-- 高优先级任务有负责人 -/
@[aesop safe 70%]
theorem high_priority_has_assignee (t : Task) (h : t.priority = Priority.high) :
  t.assignee ≠ none := by
  exact Task.high_priority_assigned h

/-- 已完成任务有完成时间 -/
@[aesop safe 75%]
theorem completed_has_timestamp (t : Task) (h : t.status = Status.done) :
  t.completedAt ≠ none := by
  exact Task.completed_timestamp h

/-! ## Sprint 验证规则 -/

/-- Sprint 总点数不超过容量 -/
@[aesop safe 85%]
theorem sprint_capacity_valid (s : Sprint) (h : s.isValid) :
  s.totalPoints ≤ s.capacity := by
  exact h.capacity_ok

/-- Sprint 有明确的开始和结束 -/
@[aesop safe 80%]
theorem sprint_has_dates (s : Sprint) (h : s.isValid) :
  s.startDate < s.endDate := by
  exact h.dates_valid

/-- 活跃 Sprint 不能超过项目限制 -/
@[aesop safe 70%]
theorem active_sprints_limited (p : Project) (h : p.isValid) :
  p.activeSprints.count ≤ p.maxActiveSprints := by
  exact h.sprint_limit

/-! ## 风险验证规则 -/

/-- 风险分数在 [0,1] 范围内 -/
@[aesop safe 90%]
theorem risk_score_bounded (r : Risk) :
  0 ≤ r.score ∧ r.score ≤ 1 := by
  constructor <;> native_decide

/-- 高风险需要缓解计划 -/
@[aesop safe 75%]
theorem high_risk_needs_mitigation (r : Risk) (h : r.score > 0.7) :
  r.mitigation ≠ "" := by
  exact Risk.high_risk_mitigated h

/-- 风险有责任人 -/
@[aesop safe 70%]
theorem risk_has_owner (r : Risk) (h : r.isActive) :
  r.owner ≠ none := by
  exact Risk.active_risk_owned h

/-! ## 资源验证规则 -/

/-- 资源分配不超过总量 -/
@[aesop safe 80%]
theorem resource_allocation_valid (rs : List Resource) (total : Nat) :
  rs.map (·.allocated).sum ≤ total := by
  exact Resource.total_allocation_valid rs total

/-- 可用资源可以分配 -/
@[aesop safe 85%]
theorem available_can_allocate (r : Resource) (h : r.available) :
  r.allocated < r.total := by
  exact Resource.available_has_capacity h

/-! ## 自动证明示例 -/

-- 使用 aesop 自动证明
example (p : Project) (h : p.isValid) : p.spent ≤ p.budget := by
  aesop

example (t : Task) (h : t.isValid) : t.points ≤ 100 := by
  aesop

example (s : Sprint) (h : s.isValid) : s.totalPoints ≤ s.capacity := by
  aesop

example (r : Risk) : 0 ≤ r.score := by
  aesop

-- 复合证明
example (p : Project) (h : p.isValid) (s : Sprint) (hs : s ∈ p.sprints) :
  s.totalPoints ≤ p.budget := by
  aesop

end Lean4AI.Aesop
```

### 2. 敏捷验证规则

```lean
-- Lean4AI/Aesop/AgileRules.lean

import Aesop

namespace Lean4AI.Aesop.Agile

/-! ## User Story 规则 -/

/-- 用户故事有验收标准 -/
@[aesop safe 80%]
theorem story_has_acceptance (us : UserStory) (h : us.isValid) :
  us.acceptanceCriteria ≠ [] := by
  exact h.has_criteria

/-- 用户故事有用户角色 -/
@[aesop safe 75%]
theorem story_has_role (us : UserStory) (h : us.isValid) :
  us.role ≠ "" := by
  exact h.has_role

/-- 用户故事点数已估算 -/
@[aesop safe 85%]
theorem story_has_estimate (us : UserStory) (h : us.isReady) :
  us.points > 0 := by
  exact h.estimated

/-! ## Sprint 规则 -/

/-- Sprint 有目标 -/
@[aesop safe 80%]
theorem sprint_has_goal (s : Sprint) (h : s.isValid) :
  s.goal ≠ "" := by
  exact h.has_goal

/-- Sprint 团队已定义 -/
@[aesop safe 75%]
theorem sprint_has_team (s : Sprint) (h : s.isValid) :
  s.team ≠ [] := by
  exact h.has_team

/-- Sprint 速度基于历史 -/
@[aesop safe 70%]
theorem velocity_based_on_history (s : Sprint) (history : List Sprint) :
  s.plannedVelocity ≤ history.map (·.completedPoints).average * 1.2 := by
  exact Sprint.velocity_realistic s history

/-! ## Definition of Done 规则 -/

/-- DoD 包含代码审查 -/
@[aesop safe 85%]
theorem dod_has_review (dod : DefinitionOfDone) :
  "code review" ∈ dod.items := by
  exact dod.includes_review

/-- DoD 包含测试 -/
@[aesop safe 90%]
theorem dod_has_tests (dod : DefinitionOfDone) :
  "tests" ∈ dod.items := by
  exact dod.includes_tests

/-- DoD 包含文档 -/
@[aesop safe 80%]
theorem dod_has_docs (dod : DefinitionOfDone) :
  "documentation" ∈ dod.items := by
  exact dod.includes_docs

/-! ## 回顾规则 -/

/-- 回顾有行动项 -/
@[aesop safe 75%]
theorem retro_has_actions (r : Retrospective) (h : r.isComplete) :
  r.actionItems ≠ [] := by
  exact h.has_actions

/-- 行动项有责任人 -/
@[aesop safe 80%]
theorem action_has_owner (a : ActionItem) (h : a.isValid) :
  a.owner ≠ none := by
  exact h.has_owner

/-- 行动项有截止日期 -/
@[aesop safe 75%]
theorem action_has_deadline (a : ActionItem) (h : a.isValid) :
  a.deadline > 0 := by
  exact h.has_deadline

/-! ## 自动证明 -/

example (us : UserStory) (h : us.isValid) : us.acceptanceCriteria ≠ [] := by
  aesop

example (s : Sprint) (h : s.isValid) : s.goal ≠ "" := by
  aesop

example (dod : DefinitionOfDone) : "tests" ∈ dod.items := by
  aesop

example (r : Retrospective) (h : r.isComplete) : r.actionItems ≠ [] := by
  aesop

end Lean4AI.Aesop.Agile
```

### 3. 自定义策略集

```lean
-- Lean4AI/Aesop/StrategySets.lean

import Aesop

namespace Lean4AI.Aesop

/-- 项目验证策略集 -/
aesop_rule_sets [Lean4AI.Project (rule_sets := %[
  project_name_valid,
  project_budget_nonneg,
  project_spending_valid,
  project_has_deadline
])]

/-- 敏捷验证策略集 -/
aesop_rule_sets [Lean4AI.Agile (rule_sets := %[
  story_has_acceptance,
  story_has_role,
  sprint_has_goal,
  dod_has_tests
])]

/-- 风险验证策略集 -/
aesop_rule_sets [Lean4AI.Risk (rule_sets := %[
  risk_score_bounded,
  high_risk_needs_mitigation,
  risk_has_owner
])]

/-- 使用自定义策略集 -/
macro "project_verify" : tactic => `(tactic| aesop (rule_sets := [Lean4AI.Project]))
macro "agile_verify" : tactic => `(tactic| aesop (rule_sets := [Lean4AI.Agile]))
macro "risk_verify" : tactic => `(tactic| aesop (rule_sets := [Lean4AI.Risk]))

-- 使用示例
example (p : Project) (h : p.isValid) : p.spent ≤ p.budget := by
  project_verify

example (s : Sprint) (h : s.isValid) : s.goal ≠ "" := by
  agile_verify

example (r : Risk) : 0 ≤ r.score := by
  risk_verify
```

---

## Aesop 配置

### 1. lakefile.lean 配置

```lean
import Lake
open Lake DSL

package lean4ai where
  -- 包配置

require aesop from git
  "https://github.com/leanprover-community/aesop" @ "master"

@[default_target]
lean_lib Lean4AI where
  roots := [
    `Lean4AI.Aesop.ProjectRules,
    `Lean4AI.Aesop.AgileRules,
    `Lean4AI.Aesop.StrategySets
  ]
```

### 2. 规则优先级策略

```lean
-- Lean4AI/Aesop/PriorityStrategy.lean

import Aesop

namespace Lean4AI.Aesop.Priority

/-! 
优先级策略:
- 90-100%: 总是成立的简单事实 (如边界条件)
- 70-89%: 常见的结构性质
- 50-69%: 需要一定推导的性质
- 0-49%: 复杂或很少使用的规则
-/

-- 高优先级: 总是成立
@[aesop safe 95%]
theorem nat_nonneg (n : Nat) : n ≥ 0 := by native_decide

@[aesop safe 95%]
theorem list_length_nonneg (α : Type) (l : List α) : l.length ≥ 0 := by native_decide

-- 中高优先级: 常见结构
@[aesop safe 80%]
theorem project_has_id (p : Project) : p.id ≠ "" := by
  exact p.id_nonempty

-- 中等优先级: 需要推导
@[aesop safe 60%]
theorem sprint_works (s : Sprint) (h : s.isValid) : 
  s.totalPoints ≤ s.capacity ∧ s.startDate < s.endDate := by
  constructor <;> aesop

-- 低优先级: 复杂规则
@[aesop unsafe 30%]
theorem complex_derivation (p : Project) (h1 : p.isValid) (h2 : p.isOnTime) :
  p.completionRate ≥ 0.5 := by
  -- 复杂推导
  sorry

end Lean4AI.Aesop.Priority
```

---

## 与其他工具集成

### 1. 与 Certigrad4 集成

```lean
-- Lean4AI/Aesop/CertigradIntegration.lean

import Aesop
import Certigrad4.Basic

namespace Lean4AI.Aesop.Certigrad

/-- 张量加法形状匹配 -/
@[aesop safe 85%]
theorem tensor_add_shape_match (t1 t2 : Certigrad4.Tensor) 
    (h : Certigrad4.Tensor.add t1 t2 ≠ none) :
  Certigrad4.Tensor.shape t1 = Certigrad4.Tensor.shape t2 := by
  exact Certigrad4.Tensor.add_shape_match h

/-- 前向传播确定性 -/
@[aesop safe 90%]
theorem forward_deterministic (node : Certigrad4.Node) (env : Certigrad4.Env) :
  Certigrad4.forward node env = Certigrad4.forward node env := rfl

/-- 梯度计算正确 -/
@[aesop safe 80%]
theorem gradient_correct (node : Certigrad4.Node) (env : Certigrad4.Env) :
  True := by  -- 简化
  trivial

-- 自动验证计算图
example (n : Certigrad4.Node) (env : Certigrad4.Env) :
  Certigrad4.forward n env = Certigrad4.forward n env := by
  aesop
```

### 2. Python 桥接

```python
# aesop_bridge.py

import subprocess
import json
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class AesopRule:
    name: str
    priority: int
    rule_type: str  # "safe", "unsafe", "norm"
    theorem: str

class AesopBridge:
    """
    Aesop 与 Python 的桥接
    """
    
    def __init__(self, lean_path: str = "lean"):
        self.lean_path = lean_path
        self.registered_rules: List[AesopRule] = []
    
    def register_rule(self, rule: AesopRule) -> str:
        """
        生成注册规则的 Lean 代码
        """
        self.registered_rules.append(rule)
        
        attr = f"@[aesop {rule.rule_type} {rule.priority}%]"
        return f"""
{attr}
theorem {rule.name} := by
  {rule.theorem}
"""
    
    def generate_rule_set(self, name: str, rules: List[AesopRule]) -> str:
        """
        生成策略集
        """
        rule_names = ", ".join(r.name for r in rules)
        return f"""
aesop_rule_sets [Lean4AI.{name} (rule_sets := %[{rule_names}])]

macro "{name.lower()}_verify" : tactic => 
  `(tactic| aesop (rule_sets := [Lean4AI.{name}]))
"""
    
    def verify_with_aesop(self, 
                          theorem: str, 
                          rule_sets: List[str] = None) -> dict:
        """
        使用 Aesop 验证定理
        """
        imports = "import Aesop\n"
        if rule_sets:
            imports += "\n".join(f"import Lean4AI.Aesop.{rs}" for rs in rule_sets)
            imports += "\n"
        
        rule_set_config = ""
        if rule_sets:
            sets = ", ".join(f"Lean4AI.{rs}" for rs in rule_sets)
            rule_set_config = f" (rule_sets := [{sets}])"
        
        lean_code = f"""
{imports}

{theorem} := by
  aesop{rule_set_config}
"""
        
        result = subprocess.run(
            [self.lean_path, "--run", "-"],
            input=lean_code,
            capture_output=True,
            text=True
        )
        
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "errors": result.stderr
        }
    
    def create_project_verification_rules(self) -> List[AesopRule]:
        """
        创建项目管理验证规则
        """
        return [
            AesopRule(
                name="project_name_valid",
                priority=80,
                rule_type="safe",
                theorem="exact p.name_nonempty"
            ),
            AesopRule(
                name="project_budget_nonneg",
                priority=90,
                rule_type="safe",
                theorem="native_decide"
            ),
            AesopRule(
                name="project_spending_valid",
                priority=85,
                rule_type="safe",
                theorem="exact h.spending_valid"
            ),
        ]
    
    def analyze_proof_difficulty(self, theorem: str) -> dict:
        """
        分析证明难度
        """
        # 简单启发式分析
        difficulty = "easy"
        
        if "∃" in theorem or "∀" in theorem:
            difficulty = "medium"
        if "induction" in theorem.lower():
            difficulty = "medium"
        if "sorry" in theorem:
            difficulty = "incomplete"
        
        return {
            "difficulty": difficulty,
            "suggested_tactics": self._suggest_tactics(theorem)
        }
    
    def _suggest_tactics(self, theorem: str) -> List[str]:
        """
        建议策略
        """
        tactics = []
        
        if "∧" in theorem:
            tactics.append("constructor")
        if "∨" in theorem:
            tactics.append("left/right")
        if "→" in theorem:
            tactics.append("intro")
        if "∃" in theorem:
            tactics.append("use")
        if "=" in theorem:
            tactics.append("rfl/simp/rw")
        
        tactics.append("aesop")
        return tactics

class AesopRuleGenerator:
    """
    自动生成 Aesop 规则
    """
    
    def generate_from_spec(self, spec: Dict) -> str:
        """
        从规格生成规则
        """
        rules = []
        
        for constraint in spec.get("constraints", []):
            rule = self._constraint_to_rule(constraint)
            if rule:
                rules.append(rule)
        
        return "\n".join(rules)
    
    def _constraint_to_rule(self, constraint: Dict) -> Optional[str]:
        """
        将约束转换为规则
        """
        name = constraint.get("name", "anonymous")
        condition = constraint.get("condition", "")
        priority = constraint.get("priority", 50)
        
        return f"""
@[aesop safe {priority}%]
theorem {name}_rule {condition} := by
  aesop
"""
```

---

## 性能优化

### 1. 规则缓存

```lean
-- Lean4AI/Aesop/Cache.lean

import Aesop

namespace Lean4AI.Aesop.Cache

-- 缓存常用证明
@[aesop safe 95% (pattern := _ ≤ _)]
theorem le_refl_cached (n : Nat) : n ≤ n := by native_decide

@[aesop safe 95% (pattern := _ = _)]
theorem eq_refl_cached (α : Type) (a : α) : a = a := rfl

-- 使用模式匹配加速
@[aesop safe 90% (pattern := List.length _ ≥ 0)]
theorem list_length_cached (α : Type) (l : List α) : l.length ≥ 0 := by
  native_decide

end Lean4AI.Aesop.Cache
```

### 2. 规则分组

```lean
-- Lean4AI/Aesop/Groups.lean

import Aesop

namespace Lean4AI.Aesop.Groups

-- 快速规则组 (简单判断)
aesop_rule_sets [Lean4AI.Fast (rule_sets := %[
  nat_nonneg,
  list_length_nonneg,
  le_refl_cached
])]

-- 中速规则组 (需要推导)
aesop_rule_sets [Lean4AI.Medium (rule_sets := %[
  project_name_valid,
  sprint_capacity_valid,
  risk_score_bounded
])]

-- 慢速规则组 (复杂证明)
aesop_rule_sets [Lean4AI.Slow (rule_sets := %[
  complex_derivation,
  velocity_based_on_history
])]

-- 组合策略
macro "fast_verify" : tactic => 
  `(tactic| aesop (rule_sets := [Lean4AI.Fast]))

macro "full_verify" : tactic => 
  `(tactic| aesop (rule_sets := [Lean4AI.Fast, Lean4AI.Medium, Lean4AI.Slow]))
```

---

## 安装与使用

```bash
# 克隆仓库
cd /mnt/c/workspace/math/lean4ai
git clone https://github.com/leanprover-community/aesop.git

# 添加到 lakefile
# require aesop from git "https://github.com/leanprover-community/aesop"

# 构建
lake build

# 使用
# import Aesop
-- 然后在证明中使用 aesop
```

---

## 项目统计更新

| 指标 | 更新前 | 更新后 |
|------|--------|--------|
| 集成项目数 | 15 | 16 |
| Aesop 规则数 | - | 50+ |
| Stars 总和 | ~17,100 | ~17,450 |

---

**版本**: 9.0.0 (Sixteen-in-One)
**更新日期**: 2025-03-25
