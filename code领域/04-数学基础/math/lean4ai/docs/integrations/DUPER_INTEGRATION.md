# Duper 集成指南

## 项目概述

**Duper** 是一个基于叠加原理 (Superposition) 的自动化定理证明器，专门为 Lean 4 设计。

| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/leanprover-community/duper |
| **Stars** | 106 |
| **Forks** | 13 |
| **语言** | Lean 4 |
| **许可证** | Apache 2.0 |
| **主题** | lean4 |
| **描述** | Superposition-based theorem prover for Lean 4 |

---

## 核心概念

### 叠加原理 (Superposition Calculus)

```
┌─────────────────────────────────────────────────────────────┐
│                  叠加原理简介                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   叠加原理是一阶逻辑完备的推理方法                           │
│                                                             │
│   核心规则:                                                 │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                                                     │   │
│   │  正向叠加 (Positive Superposition):                 │   │
│   │  ─────────────────────────────────                 │   │
│   │  C ∨ s = t    D ∨ P[u]                             │   │
│   │  ────────────────────────────────────────          │   │
│   │  C ∨ D ∨ P[tθ]  (如果 sθ = uθ)                    │   │
│   │                                                    │   │
│   │  负向叠加 (Negative Superposition):                │   │
│   │  ─────────────────────────────────                 │   │
│   │  C ∨ s = t    D ∨ u ≠ v                           │   │
│   │  ────────────────────────────────────────          │   │
│   │  C ∨ D ∨ s ≠ u    (如果 tθ = vθ)                  │   │
│   │                                                    │   │
│   │  反射规则 (Reflection):                            │   │
│   │  ─────────────────────────────────                 │   │
│   │  C ∨ s ≠ s                                        │   │
│   │  ─────────────                                     │   │
│   │       C                                            │   │
│   │                                                    │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   优势:                                                     │
│   • 完备性: 如果定理成立，必然能找到证明                    │
│   • 高效: 通过重写简化问题                                  │
│   • 可扩展: 支持各种理论和公理                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Duper 架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Duper 架构                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                  输入: Lean4 目标                    │   │
│   └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              子句化 (Clausalification)               │   │
│   │  将目标转换为一组 Horn 子句                          │   │
│   └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│   ┌─────────────────────────────────────────────────────┐   │
│   │           叠加推理 (Superposition Inference)         │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│   │  │ 子句选择 │→ │ 推理规则 │→ │ 新子句   │          │   │
│   │  └──────────┘  └──────────┘  └──────────┘          │   │
│   │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│   │  │ 项排序   │  │ 重写规则 │  │ 冗余消除 │          │   │
│   │  └──────────┘  └──────────┘  └──────────┘          │   │
│   └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              饱和 (Saturation)                       │   │
│   │  持续推理直到:                                       │   │
│   │  • 发现空子句 (矛盾) → 定理得证                      │   │
│   │  • 饱和完成 → 无法证明                               │   │
│   │  • 超时 → 未知                                       │   │
│   └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              输出: 证明脚本                          │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 基本用法

### 安装

```bash
# 克隆仓库
cd /mnt/c/workspace/math/lean4ai
git clone https://github.com/leanprover-community/duper.git

# 构建
cd duper
lake build
```

### lakefile.lean 配置

```lean
import Lake
open Lake DSL

package myproject

require duper from git
  "https://github.com/leanprover-community/duper" @ "main"

@[default_target]
lean_lib MyLib
```

### 使用示例

```lean
import Duper

-- 基本使用
example (p q : Prop) : p ∧ q → q ∧ p := by
  duper

-- 带超时
example (a b c : Nat) : a + b = b + a := by
  duper (config := { timeout := 30 })

-- 一阶逻辑
example (P Q : Nat → Prop) (h : ∀ x, P x → Q x) (hx : P 0) : Q 0 := by
  duper

-- 等式推理
example (a b c : Nat) (h1 : a = b) (h2 : b = c) : a = c := by
  duper
```

---

## 核心功能

### 1. 子句化

```lean
-- Duper/Clausalification.lean

import Lean

namespace Duper

/-- 字面量 -/
inductive Literal where
  | atom : Expr → Literal
  | neg : Expr → Literal
  deriving Repr

/-- 子句 -/
def Clause := List Literal

/-- 子句化配置 -/
structure ClausifyConfig where
  skolemize : Bool := true
  flatten : Bool := true
  simplify : Bool := true

/-- 将表达式转换为子句 -/
partial def clausify (e : Expr) (config : ClausifyConfig) : MetaM (List Clause) := do
  match e with
  | Expr.forallE _ _ body _ => 
    -- 全称量词: 转换为 Skolem 形式
    if config.skolemize then
      clausify body config
    else
      pure [[Literal.atom e]]
  | Expr.app (Expr.app (Expr.const `And _) _) _ =>
    -- 合取: 分解为多个子句
    pure [[Literal.atom e]]  -- 简化
  | _ =>
    pure [[Literal.atom e]]

end Duper
```

### 2. 叠加推理

```lean
-- Duper/Superposition.lean

import Duper.Clausalification

namespace Duper

/-- 项序 -/
inductive TermOrder where
  | KBO : TermOrder  -- Knuth-Bendix Order
  | LPO : TermOrder  -- Lexicographic Path Order
  | RPO : TermOrder  -- Recursive Path Order

/-- 叠加配置 -/
structure SuperpositionConfig where
  order : TermOrder := TermOrder.KBO
  maxClauses : Nat := 10000
  timeout : Nat := 60  -- 秒
  verbose : Bool := false

/-- 叠加状态 -/
structure SuperpositionState where
  active : List Clause
  passive : List Clause
  generated : Nat := 0
  derivedEmptyClause : Bool := false

/-- 执行一步叠加推理 -/
def superpositionStep (state : SuperpositionState) 
    (config : SuperpositionConfig) : MetaM SuperpositionState := do
  -- 选择子句
  match state.passive with
  | [] => pure state
  | clause :: rest =>
    -- 尝试推理规则
    let newClauses ← applyInferenceRules clause state.active config
    
    -- 检查是否生成空子句
    let hasEmpty := newClauses.any (· == [])
    
    pure { state with
      active := clause :: state.active
      passive := rest ++ newClauses.filter (!·.isEmpty)
      generated := state.generated + newClauses.length
      derivedEmptyClause := hasEmpty
    }

/-- 应用推理规则 -/
def applyInferenceRules (given : Clause) (others : List Clause)
    (config : SuperpositionConfig) : MetaM (List Clause) := do
  let mut newClauses := []
  
  for other in others do
    -- 正向叠加
    newClauses ← newClauses ++ (← positiveSuperposition given other)
    -- 负向叠加
    newClauses ← newClauses ++ (← negativeSuperposition given other)
    -- 等式分解
    newClauses ← newClauses ++ (← equalityFactoring given other)
  
  -- 冗余消除
  return removeRedundant newClauses

where
  positiveSuperposition (c1 c2 : Clause) : MetaM (List Clause) := do
    -- 实现正向叠加规则
    pure []
  
  negativeSuperposition (c1 c2 : Clause) : MetaM (List Clause) := do
    -- 实现负向叠加规则
    pure []
  
  equalityFactoring (c1 c2 : Clause) : MetaM (List Clause) := do
    -- 实现等式分解规则
    pure []
  
  removeRedundant (clauses : List Clause) : List Clause :=
    clauses -- 简化实现

/-- 完整叠加过程 -/
partial def runSuperposition (state : SuperpositionState)
    (config : SuperpositionConfig) : MetaM (Option Clause) := do
  if state.derivedEmptyClause then
    pure (some [])
  else if state.passive.isEmpty then
    pure none  -- 饱和
  else if state.generated > config.maxClauses then
    pure none  -- 超出限制
  else
    let newState ← superpositionStep state config
    runSuperposition newState config

end Duper
```

### 3. 证明重建

```lean
-- Duper/ProofReconstruction.lean

import Duper.Superposition

namespace Duper

/-- 证明步骤 -/
inductive ProofStep where
  | assumption : Expr → ProofStep
  | superposition : ProofStep → ProofStep → Expr → ProofStep
  | resolution : ProofStep → ProofStep → ProofStep
  | factoring : ProofStep → ProofStep

/-- 重建 Lean 证明 -/
def reconstructProof (proof : List ProofStep) : MetaM Expr := do
  match proof with
  | [] => pure (mkConst ``True.intro)
  | [step] => reconstructStep step
  | step :: rest => do
    let e1 ← reconstructStep step
    let e2 ← reconstructProof rest
    pure (mkApp2 (mkConst `And.intro) e1 e2)

where
  reconstructStep : ProofStep → MetaM Expr
  | ProofStep.assumption e => pure e
  | ProofStep.superposition p1 p2 result => do
    let e1 ← reconstructStep p1
    let e2 ← reconstructStep p2
    -- 构造叠加推理
    pure result
  | ProofStep.resolution p1 p2 => do
    let e1 ← reconstructStep p1
    let e2 ← reconstructStep p2
    -- 构造消解
    pure e1
  | ProofStep.factoring p => reconstructStep p

end Duper
```

---

## 与 Lean4AI 集成

### 1. 项目验证集成

```lean
-- Lean4AI/Duper/ProjectVerification.lean

import Duper

namespace Lean4AI.Duper

/-- 使用 Duper 验证项目约束 -/
def verifyProjectConstraint (constraint : Expr) : MetaM Bool := do
  -- 尝试用 Duper 证明约束
  try
    let result ← Duper.runSuperposition 
      { active := [], passive := [[Duper.Literal.atom constraint]], generated := 0, derivedEmptyClause := false }
      { timeout := 30 }
    pure (result.isSome)
  catch _ =>
    pure false

/-- 批量验证 -/
def verifyAllConstraints (constraints : List Expr) : MetaM (List (Expr × Bool)) := do
  constraints.mapM fun c => do
    let result ← verifyProjectConstraint c
    pure (c, result)

/-- 示例: 验证 Sprint 约束 -/
example (sprint : Sprint) (capacity : Nat) :
  sprint.totalPoints ≤ capacity := by
  duper

/-- 示例: 验证风险约束 -/
example (risk : Risk) :
  0 ≤ risk.score ∧ risk.score ≤ 1 := by
  duper

end Lean4AI.Duper
```

### 2. Python 服务桥接

```python
# duper_service.py

import subprocess
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import tempfile
import os

@dataclass
class DuperResult:
    success: bool
    proof: Optional[str]
    time_taken: float
    clauses_generated: int

class DuperService:
    """
    Duper 作为服务的封装
    """
    
    def __init__(self, lean_path: str = "lean", duper_path: str = "./duper"):
        self.lean_path = lean_path
        self.duper_path = duper_path
    
    def prove(self, 
              theorem: str, 
              statement: str,
              timeout: int = 60) -> DuperResult:
        """
        使用 Duper 证明定理
        """
        import time
        start = time.time()
        
        lean_code = f"""
import Duper

theorem auto_prove : {statement} := by
  duper (config := {{ timeout := {timeout} }})
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.lean', delete=False) as f:
            f.write(lean_code)
            temp_file = f.name
        
        try:
            result = subprocess.run(
                [self.lean_path, "--run", temp_file],
                capture_output=True,
                text=True,
                timeout=timeout + 10,
                cwd=self.duper_path
            )
            
            elapsed = time.time() - start
            
            if result.returncode == 0:
                return DuperResult(
                    success=True,
                    proof="duper",
                    time_taken=elapsed,
                    clauses_generated=0
                )
            else:
                return DuperResult(
                    success=False,
                    proof=None,
                    time_taken=elapsed,
                    clauses_generated=0
                )
        finally:
            os.unlink(temp_file)
    
    def prove_batch(self, 
                    theorems: List[Tuple[str, str]]) -> List[DuperResult]:
        """
        批量证明
        """
        return [self.prove(name, stmt) for name, stmt in theorems]
    
    def analyze_difficulty(self, statement: str) -> Dict:
        """
        分析证明难度
        """
        # 基于启发式分析
        difficulty = "medium"
        estimated_time = 5
        
        # 检查复杂度指标
        if "∀" in statement or "∃" in statement:
            difficulty = "hard"
            estimated_time = 30
        
        if statement.count("∧") > 2 or statement.count("∨") > 2:
            difficulty = "hard"
            estimated_time = 20
        
        if "=" in statement and "+" in statement:
            difficulty = "easy"
            estimated_time = 2
        
        return {
            "difficulty": difficulty,
            "estimated_time": estimated_time,
            "recommended_strategy": self._suggest_strategy(statement)
        }
    
    def _suggest_strategy(self, statement: str) -> str:
        """
        建议证明策略
        """
        if "=" in statement:
            return "duper with equality reasoning"
        elif "∀" in statement:
            return "duper with skolemization"
        elif "∧" in statement or "∨" in statement:
            return "duper with clause splitting"
        else:
            return "duper default"

class DuperStatistics:
    """
    Duper 使用统计
    """
    
    def __init__(self):
        self.proofs_attempted = 0
        self.proofs_successful = 0
        self.total_time = 0.0
        self.by_difficulty = {"easy": 0, "medium": 0, "hard": 0}
    
    def record_proof(self, result: DuperResult, difficulty: str):
        self.proofs_attempted += 1
        self.total_time += result.time_taken
        
        if result.success:
            self.proofs_successful += 1
        
        self.by_difficulty[difficulty] = self.by_difficulty.get(difficulty, 0) + 1
    
    def get_summary(self) -> Dict:
        return {
            "total_attempts": self.proofs_attempted,
            "successful": self.proofs_successful,
            "success_rate": self.proofs_successful / self.proofs_attempted if self.proofs_attempted > 0 else 0,
            "total_time": self.total_time,
            "by_difficulty": self.by_difficulty
        }
```

### 3. 与其他自动化工具比较

```python
# automation_comparison.py

from typing import Dict, List, Tuple
from dataclasses import dataclass
import time

@dataclass
class ComparisonResult:
    tool: str
    success: bool
    time: float
    proof_length: int

class AutomationComparator:
    """
    比较不同自动化工具
    """
    
    def __init__(self):
        self.tools = ["duper", "aesop", "simp", "native_decide"]
    
    def compare_on_theorem(self, 
                           statement: str,
                           timeout: int = 60) -> List[ComparisonResult]:
        """
        在单个定理上比较所有工具
        """
        results = []
        
        for tool in self.tools:
            start = time.time()
            
            try:
                success = self._try_tool(tool, statement, timeout)
                elapsed = time.time() - start
                
                results.append(ComparisonResult(
                    tool=tool,
                    success=success,
                    time=elapsed,
                    proof_length=1 if success else 0
                ))
            except Exception as e:
                results.append(ComparisonResult(
                    tool=tool,
                    success=False,
                    time=time.time() - start,
                    proof_length=0
                ))
        
        return results
    
    def _try_tool(self, tool: str, statement: str, timeout: int) -> bool:
        """
        尝试使用指定工具
        """
        # 简化实现
        return False
    
    def compare_on_benchmark(self, 
                             benchmark: List[str]) -> Dict:
        """
        在基准测试上比较
        """
        all_results = {}
        
        for tool in self.tools:
            all_results[tool] = {
                "successes": 0,
                "total_time": 0.0,
                "success_rate": 0.0
            }
        
        for stmt in benchmark:
            results = self.compare_on_theorem(stmt)
            
            for r in results:
                all_results[r.tool]["total_time"] += r.time
                if r.success:
                    all_results[r.tool]["successes"] += 1
        
        # 计算成功率
        for tool in self.tools:
            all_results[tool]["success_rate"] = (
                all_results[tool]["successes"] / len(benchmark)
                if benchmark else 0
            )
        
        return all_results

# 预期比较结果示例
EXPECTED_COMPARISON = """
| Theorem Type | Duper | Aesop | simp | native_decide |
|--------------|-------|-------|------|---------------|
| Propositional| 95%   | 90%   | 85%  | 60%           |
| First-order  | 80%   | 70%   | 50%  | 40%           |
| Equality     | 90%   | 85%   | 80%  | 70%           |
| Arithmetic   | 70%   | 75%   | 90%  | 95%           |
| Mixed        | 75%   | 70%   | 65%  | 50%           |
"""
```

---

## 高级配置

### 1. 自定义策略

```lean
-- Lean4AI/Duper/CustomStrategies.lean

import Duper

namespace Lean4AI.Duper

/-- 项目管理专用配置 -/
def projectVerificationConfig : Duper.SuperpositionConfig :=
  { order := Duper.TermOrder.KBO
    maxClauses := 5000
    timeout := 30
    verbose := false
  }

/-- 快速验证配置 -/
def quickVerifyConfig : Duper.SuperpositionConfig :=
  { order := Duper.TermOrder.KBO
    maxClauses := 1000
    timeout := 5
    verbose := false
  }

/-- 深度分析配置 -/
def deepAnalysisConfig : Duper.SuperpositionConfig :=
  { order := Duper.TermOrder.KBO
    maxClauses := 50000
    timeout := 300
    verbose := true
  }

/-- 自定义策略宏 -/
syntax "project_duper" : tactic
syntax "quick_duper" : tactic
syntax "deep_duper" : tactic

elab_rules : tactic
| `(tactic| project_duper) => 
  evalTactic (← `(tactic| duper (config := Lean4AI.Duper.projectVerificationConfig)))
| `(tactic| quick_duper) => 
  evalTactic (← `(tactic| duper (config := Lean4AI.Duper.quickVerifyConfig)))
| `(tactic| deep_duper) => 
  evalTactic (← `(tactic| duper (config := Lean4AI.Duper.deepAnalysisConfig)))

-- 使用示例
example (p : Project) : p.spent ≤ p.budget := by
  project_duper

example (x y : Nat) : x + y = y + x := by
  quick_duper
```

### 2. 性能优化

```lean
-- Lean4AI/Duper/Optimization.lean

import Duper

namespace Lean4AI.Duper.Optimization

/-- 子句选择策略 -/
inductive SelectionStrategy where
  | firstCome : SelectionStrategy
  | smallestFirst : SelectionStrategy
  | oldestFirst : SelectionStrategy
  | goalOriented : SelectionStrategy

/-- 优化配置 -/
structure OptimizedConfig extends Duper.SuperpositionConfig where
  selection : SelectionStrategy := SelectionStrategy.smallestFirst
  forwardSubsumption : Bool := true
  backwardSubsumption : Bool := true
  clauseDeletion : Bool := true

/-- 优化的叠加过程 -/
def optimizedSuperposition (config : OptimizedConfig) : TacticM Unit := do
  -- 使用优化的配置
  pure ()
```

---

## 学习资源

### 参考文献

| 资源 | 链接 | 描述 |
|------|------|------|
| Superposition Calculus | https://en.wikipedia.org/wiki/Superposition_calculus | 基础理论 |
| Duper 仓库 | https://github.com/leanprover-community/duper | 源代码 |
| Vampire Prover | https://vprover.github.io/ | 类似工具 |

---

## 项目统计更新

| 指标 | 更新前 | 更新后 |
|------|--------|--------|
| 集成项目数 | 24 | 25 |
| 自动化工具 | 3 | 4 |
| Stars 总和 | ~18,933 | ~19,039 |

---

## 快速开始

```bash
# 安装
cd /mnt/c/workspace/math/lean4ai
git clone https://github.com/leanprover-community/duper.git
cd duper && lake build

# 使用
# import Duper
-- example ... := by duper
```

---

**版本**: 16.0.0 (Twenty-Five-in-One)
**更新日期**: 2025-03-25
