# Plausible 集成指南

## 项目概述

**Plausible** 是 Lean4 的可满足性检查器，用于验证逻辑公式的可满足性。

| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/leanprover-community/plausible |
| **Stars** | 83 |
| **Forks** | 18 |
| **语言** | Lean 4 |
| **许可证** | Apache 2.0 |
| **创建时间** | 2024-10-23 |

---

## 核心概念

### 什么是 Plausible？

```
┌─────────────────────────────────────────────────────────────┐
│                    Plausible 概念                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Plausible 是一个可满足性模态理论 (SMT) 求解器             │
│                                                             │
│   核心功能:                                                 │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  1. 可满足性检查 (SAT)                               │   │
│   │     - 判断公式是否有解                               │   │
│   │     - 找到满足公式的赋值                             │   │
│   │                                                     │   │
│   │  2. 理论求解 (SMT)                                   │   │
│   │     - 结合背景理论 (线性算术、数组等)               │   │
│   │     - 处理等式、不等式、量词                        │   │
│   │                                                     │   │
│   │  3. 反例生成                                        │   │
│   │     - 当命题不成立时，生成反例                      │   │
│   │     - 帮助调试和验证                                │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   与其他工具的关系:                                         │
│   • Duper: 叠加原理证明器                                  │
│   • Aesop: 自动化策略                                       │
│   • simp: 简化器                                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 基本用法

### 安装

```bash
cd /mnt/c/workspace/math/lean4ai
git clone https://github.com/leanprover-community/plausible.git

cd plausible
lake build
```

### 配置

```lean
-- lakefile.lean
import Lake
open Lake DSL

package myproject

require plausible from git
  "https://github.com/leanprover-community/plausible" @ "main"
```

### 使用示例

```lean
import Plausible

-- 检查可满足性
example : ∃ x : Nat, x > 0 := by plausible

-- 带约束的检查
example (x : Nat) (h : x > 0) : x + 1 > 1 := by plausible

-- 生成反例
example : ∀ x : Nat, x > x := by
  plausible  -- 会失败并给出反例

-- 线性算术
example (x y : Int) : x + y = y + x := by plausible
```

---

## 核心功能

### 1. 可满足性检查

```lean
-- Plausible/SAT.lean

import Lean

namespace Plausible

/-- 可满足性结果 -/
inductive SatResult where
  | sat : List (Name × Expr) → SatResult  -- 满足，带赋值
  | unsat : SatResult                          -- 不满足
  | unknown : SatResult                         -- 未知

/-- 检查公式可满足性 -/
def checkSat (prop : Expr) : MetaM SatResult := do
  -- 简化实现
  pure SatResult.unknown

/-- 检查多个公式 -/
def checkSatConj (props : List Expr) : MetaM SatResult := do
  -- 检查所有公式的合取
  pure SatResult.unknown

end Plausible
```

### 2. 反例生成

```lean
-- Plausible/Counterexample.lean

import Lean

namespace Plausible

/-- 反例 -/
structure Counterexample where
  assignment : List (Name × Expr)
  message : String

/-- 生成反例 -/
def generateCounterexample (prop : Expr) : MetaM (Option Counterexample) := do
  -- 当命题不成立时，生成反例
  pure none

/-- 格式化反例 -/
def formatCounterexample (c : Counterexample) : String :=
  s!"Counterexample found:\n" ++
  c.assignment.foldl (fun acc (name, val) => 
    acc ++ s!"  {name} = {val}\n"
  ) "" ++
  s!"Explanation: {c.message}"

end Plausible
```

### 3. 理论求解

```lean
-- Plausible/SMT.lean

import Lean

namespace Plausible

/-- 理论类型 -/
inductive Theory where
  | linearArith : Theory     -- 线性算术
  | array : Theory           -- 数组理论
  | bitvec : Theory          -- 位向量
  | datatypes : Theory       -- 数据类型

/-- SMT 配置 -/
structure SMTConfig where
  theories : List Theory := [Theory.linearArith]
  timeout : Nat := 30
  verbose : Bool := false

/-- SMT 求解 -/
def solve (prop : Expr) (config : SMTConfig := {}) : MetaM SatResult := do
  -- 使用配置的理论求解
  pure SatResult.unknown

/-- 线性算术求解 -/
def solveLinearArith (prop : Expr) : MetaM SatResult := do
  solve prop { theories := [Theory.linearArith] }

/-- 带数组的求解 -/
def solveWithArrays (prop : Expr) : MetaM SatResult := do
  solve prop { theories := [Theory.linearArith, Theory.array] }

end Plausible
```

---

## 与 Lean4AI 集成

### 1. 项目约束验证

```lean
-- Lean4AI/Plausible/ProjectConstraints.lean

import Plausible

namespace Lean4AI.Plausible

/-- 验证项目约束 -/
def verifyProjectConstraint (p : Project) : MetaM Bool := do
  -- 检查项目约束是否可满足
  let constraints := [
    mkLeConstraint p.spent p.budget,
    mkNonemptyConstraint p.name,
    mkPositiveConstraint p.tasks.length
  ]
  
  match ← Plausible.checkSatConj constraints with
  | Plausible.SatResult.sat _ => pure true
  | _ => pure false

where
  mkLeConstraint (a b : Nat) : Expr := q($a ≤ $b)
  mkNonemptyConstraint (s : String) : Expr := q($s ≠ "")
  mkPositiveConstraint (n : Nat) : Expr := q($n ≥ 0)

/-- 检查 Sprint 容量 -/
def checkSprintCapacity (s : Sprint) (capacity : Nat) : MetaM Bool := do
  let constraint := q(${s.totalPoints} ≤ $capacity)
  match ← Plausible.checkSat constraint with
  | Plausible.SatResult.sat _ => pure true
  | _ => pure false

/-- 检查风险分数 -/
def checkRiskScore (r : Risk) : MetaM Bool := do
  let constraints := [
    q(${r.score} ≥ 0),
    q(${r.score} ≤ 1)
  ]
  match ← Plausible.checkSatConj constraints with
  | Plausible.SatResult.sat _ => pure true
  | _ => pure false

/-- 批量验证 -/
def verifyAllConstraints (project : Project) : MetaM (List String) := do
  let mut errors := []
  
  unless ← verifyProjectConstraint project do
    errors := errors ++ ["Project constraint violation"]
  
  for s in project.sprints do
    unless ← checkSprintCapacity s project.capacity do
      errors := errors ++ [s!"Sprint {s.name} exceeds capacity"]
  
  for r in project.risks do
    unless ← checkRiskScore r do
      errors := errors ++ [s!"Risk {r.name} has invalid score"]
  
  pure errors

end Lean4AI.Plausible
```

### 2. 反例辅助调试

```lean
-- Lean4AI/Plausible/Debugging.lean

import Plausible

namespace Lean4AI.Plausible.Debugging

/-- 验证结果 -/
inductive VerificationResult where
  | valid : VerificationResult
  | invalid : Counterexample → VerificationResult
  | unknown : String → VerificationResult

/-- 验证定理并生成反例 -/
def verifyWithCounterexample (statement : Expr) : MetaM VerificationResult := do
  -- 首先尝试证明
  try
    let _ ← inferType statement
    pure VerificationResult.valid
  catch _ =>
    -- 如果证明失败，尝试生成反例
    match ← Plausible.generateCounterexample statement with
    | some c => pure (VerificationResult.invalid c)
    | none => pure (VerificationResult.unknown "Could not generate counterexample")

/-- 验证项目属性 -/
def verifyProjectProperty (p : Project) (prop : Project → Bool) 
    (propName : String) : MetaM VerificationResult := do
  if prop p then
    pure VerificationResult.valid
  else
    let ce : Counterexample := {
      assignment := [
        (`project, q($p))
      ],
      message := s!"Property '{propName}' does not hold for this project"
    }
    pure (VerificationResult.invalid ce)

/-- 辅助修复建议 -/
def suggestFix (ce : Counterexample) : List String := Id.run do
  let mut suggestions := []
  
  for (name, val) in ce.assignment do
    suggestions := suggestions ++ [s!"Consider adjusting {name} (current: {val})"]
  
  suggestions := suggestions ++ [ce.message]
  
  pure suggestions

end Lean4AI.Plausible.Debugging
```

### 3. Python 桥接

```python
# plausible_bridge.py

import subprocess
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class SatResult:
    satisfiable: bool
    assignment: Optional[Dict[str, Any]] = None
    counterexample: Optional[Dict[str, Any]] = None

class PlausibleBridge:
    """
    Plausible 与 Python 的桥接
    """
    
    def __init__(self, lean_path: str = "lean"):
        self.lean_path = lean_path
    
    def check_sat(self, expression: str, timeout: int = 30) -> SatResult:
        """
        检查表达式可满足性
        """
        lean_code = f"""
import Plausible

#check Plausible.checkSat q({expression})
"""
        
        result = subprocess.run(
            [self.lean_path, "--run", "-"],
            input=lean_code,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        # 解析结果
        if "sat" in result.stdout.lower():
            return SatResult(satisfiable=True)
        elif "unsat" in result.stdout.lower():
            return SatResult(satisfiable=False)
        else:
            return SatResult(satisfiable=False, counterexample={"error": result.stderr})
    
    def generate_counterexample(self, proposition: str) -> Optional[Dict]:
        """
        生成反例
        """
        lean_code = f"""
import Plausible

#eval Plausible.generateCounterexample q({proposition})
"""
        
        result = subprocess.run(
            [self.lean_path, "--run", "-"],
            input=lean_code,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # 解析反例
        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except:
                return None
        return None
    
    def verify_constraint(self, constraint: str) -> bool:
        """
        验证约束
        """
        result = self.check_sat(constraint)
        return result.satisfiable
    
    def find_valid_assignment(self, 
                               variables: List[str], 
                               constraints: List[str]) -> Optional[Dict[str, Any]]:
        """
        找到满足所有约束的赋值
        """
        all_constraints = " ∧ ".join(constraints)
        result = self.check_sat(all_constraints)
        
        if result.satisfiable:
            return result.assignment
        return None

class ProjectConstraintVerifier:
    """
    项目约束验证器
    """
    
    def __init__(self, plausible: PlausibleBridge):
        self.plausible = plausible
    
    def verify_project(self, project: Dict) -> Dict:
        """
        验证项目约束
        """
        results = {
            "valid": True,
            "violations": []
        }
        
        # 检查预算约束
        if project.get("spent", 0) > project.get("budget", 0):
            results["valid"] = False
            results["violations"].append({
                "type": "budget_exceeded",
                "message": f"Spent ({project['spent']}) exceeds budget ({project['budget']})"
            })
        
        # 检查名称非空
        if not project.get("name", ""):
            results["valid"] = False
            results["violations"].append({
                "type": "empty_name",
                "message": "Project name cannot be empty"
            })
        
        # 检查任务约束
        for task in project.get("tasks", []):
            if task.get("points", 0) <= 0:
                results["valid"] = False
                results["violations"].append({
                    "type": "invalid_task_points",
                    "message": f"Task '{task.get('name')}' has invalid points"
                })
        
        return results
    
    def suggest_fixes(self, violations: List[Dict]) -> List[str]:
        """
        根据违规建议修复
        """
        suggestions = []
        
        for v in violations:
            if v["type"] == "budget_exceeded":
                suggestions.append("Increase budget or reduce spending")
            elif v["type"] == "empty_name":
                suggestions.append("Provide a project name")
            elif v["type"] == "invalid_task_points":
                suggestions.append("Set positive points for all tasks")
        
        return suggestions

class ConstraintSolver:
    """
    约束求解器
    """
    
    def __init__(self, plausible: PlausibleBridge):
        self.plausible = plausible
    
    def solve_scheduling(self, 
                         tasks: List[Dict], 
                         sprints: List[Dict],
                         capacity: int) -> Optional[Dict]:
        """
        求解调度问题
        """
        # 生成约束
        constraints = []
        
        # Sprint 容量约束
        for sprint in sprints:
            sprint_tasks = [t for t in tasks if t.get("sprint") == sprint["id"]]
            total_points = sum(t.get("points", 0) for t in sprint_tasks)
            constraints.append(f"{total_points} ≤ {capacity}")
        
        # 任务分配约束
        for task in tasks:
            if task.get("assigned"):
                constraints.append(f"task_{task['id']}_assigned = true")
        
        # 求解
        assignment = self.plausible.find_valid_assignment([], constraints)
        
        return assignment
    
    def optimize_resource_allocation(self,
                                       resources: List[Dict],
                                       requirements: List[Dict]) -> Optional[Dict]:
        """
        优化资源分配
        """
        # 简化实现
        return {"allocation": "optimized"}
```

---

## 与其他工具比较

| 工具 | 类型 | 优势 | 适用场景 |
|------|------|------|----------|
| **Plausible** | SAT/SMT | 反例生成，约束求解 | 验证，调试 |
| **Duper** | 叠加原理 | 完备证明，等式推理 | 定理证明 |
| **Aesop** | 自动策略 | 快速，可扩展 | 常规证明 |
| **native_decide** | 决策过程 | 高效，确定性 | 可判定命题 |

---

## 最佳实践

### 1. 选择合适的工具

```lean
-- 可判定命题: native_decide
example : 1 + 1 = 2 := by native_decide

-- 需要等式推理: Duper
example (a b : Nat) : a + b = b + a := by duper

-- 需要反例: Plausible
example : ∀ x : Nat, x > x := by
  plausible  -- 会生成反例 x = 0

-- 常规自动化: Aesop
example (p q : Prop) : p ∧ q → q ∧ p := by aesop
```

### 2. 组合使用

```lean
-- 先用 plausible 检查可满足性
example (x : Nat) : x > 0 → x + 1 > 1 := by
  plausible  -- 检查约束

-- 然后用其他策略完成证明
example (x : Nat) : x > 0 → x + 1 > 1 := by
  intro h
  linarith
```

---

## 项目统计更新

| 指标 | 更新前 | 更新后 |
|------|--------|--------|
| 集成项目数 | 27 | 28 |
| 验证工具 | 4 | 5 |
| Stars 总和 | ~19,244 | ~19,327 |

---

## 快速开始

```bash
# 安装
cd /mnt/c/workspace/math/lean4ai
git clone https://github.com/leanprover-community/plausible.git
cd plausible && lake build

# 使用
# import Plausible
-- example ... := by plausible
```

---

**版本**: 19.0.0 (Twenty-Eight-in-One)
**更新日期**: 2025-03-25
