# Quote4 集成指南

## 项目概述

**Quote4** 是一个为 Lean 4 提供直观、类型安全的表达式引用 (quotation) 库，是元编程的核心工具。

| 属性 | 值 |
|------|-----|
| **仓库** | https://github.com/leanprover-community/quote4 |
| **Stars** | 102 |
| **Forks** | 20 |
| **语言** | Lean 4 |
| **许可证** | Apache 2.0 |
| **描述** | Intuitive, type-safe expression quotations for Lean 4 |
| **主题** | lean4 |

---

## 核心概念

### 什么是引用 (Quotation)？

```
┌─────────────────────────────────────────────────────────────┐
│                    引用 (Quotation)                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   引用是将 Lean 代码转换为 Expr (表达式) 的机制              │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Lean 代码                 Expr                     │   │
│   │  ──────────               ─────                    │   │
│   │  1 + 2        ──`──>      app (app + 1) 2         │   │
│   │  fun x => x   ──`──>      lam x (bvar 0)          │   │
│   │  Nat.add      ──`──>      const `Nat.add []       │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   引用类型:                                                 │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  `(...)`      - 精确引用      : Term                │   │
│   │  `(...)`      - 模式引用      : Term                │   │
│   │  `(...)`      - 策略引用      : Tactic              │   │
│   │  $(...)       - 拼接          : Expr → Term        │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   用途:                                                     │
│   • 元编程 - 生成代码                                      │
│   • 宏定义 - 语法扩展                                      │
│   • 策略编写 - 自动化证明                                  │
│   • 代码分析 - 静态检查                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Quote4 vs 内置 Quote

```
┌─────────────────────────────────────────────────────────────┐
│              Quote4 vs 内置 Quote                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Lean4 内置 Quote:                                         │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  • 基础功能                                          │   │
│   │  • 手动类型注解                                      │   │
│   │  • 较少类型安全                                      │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   Quote4 增强:                                              │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  ✅ 类型安全的引用                                   │   │
│   │  ✅ 自动类型推断                                     │   │
│   │  ✅ 更直观的语法                                     │   │
│   │  ✅ 模式匹配支持                                     │   │
│   │  ✅ 拼接操作更简单                                   │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   示例对比:                                                 │
│                                                             │
│   内置:                                                     │
│   ```lean                                                   │
│   def myExpr : Expr := `(Nat.add 1 2)                      │
│   ```                                                       │
│                                                             │
│   Quote4:                                                   │
│   ```lean                                                   │
│   def myExpr : Q (Nat → Nat → Nat) := q(Nat.add)           │
│   def myApp : Q Nat := q(Nat.add 1 2)                      │
│   ```                                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 基本用法

### 1. 安装配置

```lean
-- lakefile.lean
import Lake
open Lake DSL

package myproject

require quote4 from git
  "https://github.com/leanprover-community/quote4" @ "master"
```

### 2. 基本引用

```lean
import Qq

open Qq

-- 类型安全的引用
def natExpr : Q Nat := q(42)

def addExpr : Q (Nat → Nat → Nat) := q(Nat.add)

-- 自动类型推断
def appExpr : Q Nat := q(Nat.add 1 2)

-- 函数引用
def idExpr : Q (α → α) := q(fun x => x)

-- 多态引用
def composeExpr : Q ((β → γ) → (α → β) → α → γ) := 
  q(fun f g x => f (g x))
```

### 3. 拼接 (Splicing)

```lean
import Qq

open Qq

-- 基本拼接
def makeAdd (n : Nat) : Q Nat := q($n + 1)

-- 表达式拼接
def makeApp (f : Q (Nat → Nat)) (x : Q Nat) : Q Nat := 
  q($f $x)

-- 列表拼接
def makeList (xs : List (Q Nat)) : Q (List Nat) := 
  q([$xs,*])

-- 示例
def myList : Q (List Nat) := makeList [q(1), q(2), q(3)]
-- 结果: `[1, 2, 3]`

-- 条件拼接
def makeIf (cond : Q Bool) (thenBranch : Q α) (elseBranch : Q α) : Q α :=
  q(if $cond then $thenBranch else $elseBranch)
```

### 4. 模式匹配引用

```lean
import Qq

open Qq

-- 匹配表达式结构
def isAddition : Q Nat → Bool
  | q($a + $b) => true
  | _ => false

-- 提取加法操作数
def getAddArgs? : Q Nat → Option (Q Nat × Q Nat)
  | q($a + $b) => some (a, b)
  | _ => none

-- 递归匹配
def countAdditions : Q Nat → Nat
  | q($a + $b) => 1 + countAdditions a + countAdditions b
  | _ => 0

-- 匹配函数应用
def getAppFn? : Q α → Option (Name × List (Q Expr))
  | q($f $args*) => 
    some (f.getAppFnName, args)
  | _ => none
```

---

## 高级功能

### 1. 类型类实例引用

```lean
import Qq

open Qq

-- 获取类型类实例
def getHAddInstance (α β γ : Q Type) : Q (HAdd $α $β $γ) := 
  q(instHAdd)

-- 构造类型类约束的表达式
def makeAddWithInstance (α : Q Type) [inst : Q (Add $α)] 
    (a b : Q $α) : Q $α :=
  q($a + $b)

-- 示例
def natAddInstance : Q Add Nat := q(instAddNat)
def natSum : Q Nat := makeAddWithInstance q(Nat) q(1) q(2)
```

### 2. 策略生成

```lean
import Qq
import Lean.Meta

open Qq Lean Meta

-- 生成策略表达式
def mkIntroTactic : Q Tactic := 
  q(intro)

def mkApplyTactic (h : Q Expr) : Q Tactic :=
  q(apply $h)

def mkExactTactic (h : Q Expr) : Q Tactic :=
  q(exact $h)

-- 组合策略
def mkSeqTactic (t1 t2 : Q Tactic) : Q Tactic :=
  q($t1; $t2)

-- 生成完整证明
def generateSimpleProof (goal : Q Prop) : MetaM (Q Tactic) := do
  pure q(trivial)
```

### 3. 定义生成

```lean
import Qq
import Lean.Meta

open Qq Lean Meta

-- 生成函数定义
def mkFunDef (name : Name) (type : Q Type) (body : Q $type) : Q Command :=
  q(def $name : $type := $body)

-- 生成定理
def mkTheorem (name : Name) (prop : Q Prop) (proof : Q $prop) : Q Command :=
  q(theorem $name : $prop := $proof)

-- 生成实例
def mkInstance (className : Name) (type : Q Type) 
    (inst : Q ($className $type)) : Q Command :=
  q(instance : $className $type := $inst)

-- 示例
def myDef : Q Command := mkFunDef `myAdd q(Nat → Nat → Nat) q(fun a b => a + b)
```

---

## 与 Lean4AI 集成

### 1. 项目验证代码生成

```lean
-- Lean4AI/Quote4/CodeGen.lean

import Qq
import Lean.Meta

open Qq Lean Meta

namespace Lean4AI.Quote4

/-- 生成项目结构定义 -/
def generateProjectStruct : Q Command :=
  q(structure Project where
    name : String
    budget : Nat
    spent : Nat
    tasks : List Task
    deriving Repr)

/-- 生成验证定理 -/
def generateBudgetTheorem : Q Command :=
  q(theorem Project.budget_valid (p : Project) (h : p.isValid) :
      p.spent ≤ p.budget := by
    exact h.spending_ok)

/-- 动态生成验证器 -/
def mkProjectVerifier (fields : List (Name × Q Type)) : MetaM (Q Command) := do
  -- 生成结构字段
  let fieldCmds : List (Q StructField) := fields.map fun (name, ty) =>
    q({ $name : $ty })
  
  pure q(structure Project where
    $fieldCmds:*
    deriving Repr)

/-- 生成策略 -/
def mkVerificationTactic (constraints : List (Q Prop)) : Q Tactic := do
  let tactics := constraints.map fun c => q(intro; exact $c)
  pure q(intros; constructor; all_goals trivial)

end Lean4AI.Quote4
```

### 2. 证明脚本生成

```lean
-- Lean4AI/Quote4/ProofGen.lean

import Qq
import Lean.Meta
import Lean.Elab.Tactic

open Qq Lean Meta Elab Tactic

namespace Lean4AI.Quote4.ProofGen

/-- 证明策略 -/
inductive ProofStrategy where
  | trivial : ProofStrategy
  | simp : ProofStrategy
  | nativeDecide : ProofStrategy
  | aesop : ProofStrategy
  | induction : Name → ProofStrategy
  | cases : Name → ProofStrategy

/-- 策略到引用 -/
def strategyToQ : ProofStrategy → Q Tactic
  | .trivial => q(trivial)
  | .simp => q(simp)
  | .nativeDecide => q(native_decide)
  | .aesop => q(aesop)
  | .induction n => q(induction $n)
  | .cases n => q(cases $n)

/-- 生成证明脚本 -/
def generateProofScript (strategies : List ProofStrategy) : Q Tactic := do
  match strategies with
  | [] => q(trivial)
  | [s] => strategyToQ s
  | s :: rest => 
    let first := strategyToQ s
    let restScript ← generateProofScript rest
    q($first; $restScript)

/-- 分析目标并建议策略 -/
def suggestTactics (goal : Q Prop) : MetaM (List ProofStrategy) := do
  let goalType ← inferType goal
  
  if goalType.isProp then
    if goalType.isAppOf ``True then
      pure [.trivial]
    else if goalType.isDecidable then
      pure [.nativeDecide]
    else
      pure [.simp, .aesop]
  else
    pure [.trivial]

/-- 自动生成证明 -/
def autoGenerateProof (goal : Q Prop) : MetaM (Q Tactic) := do
  let strategies ← suggestTactics goal
  generateProofScript strategies

end Lean4AI.Quote4.ProofGen
```

### 3. Python 桥接

```python
# quote4_bridge.py

import subprocess
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class QuotedExpr:
    """引用表达式"""
    type: str
    code: str
    is_valid: bool

class Quote4Bridge:
    """
    Quote4 与 Python 的桥接
    """
    
    def __init__(self, lean_path: str = "lean"):
        self.lean_path = lean_path
    
    def quote_term(self, term: str) -> QuotedExpr:
        """
        引用一个项
        """
        lean_code = f"""
import Qq

open Qq

def quoted : Q _ := q({term})

#check quoted
"""
        result = subprocess.run(
            [self.lean_path, "--run", "-"],
            input=lean_code,
            capture_output=True,
            text=True
        )
        
        return QuotedExpr(
            type="term",
            code=term,
            is_valid=result.returncode == 0
        )
    
    def splice(self, template: str, bindings: Dict[str, str]) -> QuotedExpr:
        """
        执行拼接
        """
        # 构建 Lean 代码
        defs = "\n".join(
            f"def {k} : Q _ := q({v})"
            for k, v in bindings.items()
        )
        
        lean_code = f"""
import Qq

open Qq

{defs}

def result : Q _ := q({template})

#check result
"""
        result = subprocess.run(
            [self.lean_path, "--run", "-"],
            input=lean_code,
            capture_output=True,
            text=True
        )
        
        return QuotedExpr(
            type="spliced",
            code=template,
            is_valid=result.returncode == 0
        )
    
    def pattern_match(self, pattern: str, expr: str) -> Optional[Dict[str, str]]:
        """
        模式匹配
        """
        lean_code = f"""
import Qq

open Qq

def pattern : Q _ := q({pattern})
def expr : Q _ := q({expr})

def matchResult : Option _ := 
  match expr with
  | q({pattern}) => some ()
  | _ => none

#eval matchResult
"""
        result = subprocess.run(
            [self.lean_path, "--run", "-"],
            input=lean_code,
            capture_output=True,
            text=True
        )
        
        if "some" in result.stdout:
            return {"matched": True}
        return None
    
    def generate_definition(self, 
                            name: str, 
                            type_str: str, 
                            body: str) -> str:
        """
        生成定义代码
        """
        return f"""
def {name} : {type_str} := {body}
"""
    
    def generate_theorem(self,
                         name: str,
                         statement: str,
                         proof: str) -> str:
        """
        生成定理代码
        """
        return f"""
theorem {name} : {statement} := by
  {proof}
"""

class CodeGenerator:
    """
    使用 Quote4 的代码生成器
    """
    
    def __init__(self):
        self.bridge = Quote4Bridge()
    
    def generate_project_code(self, spec: Dict) -> str:
        """
        从规格生成项目代码
        """
        parts = []
        
        # 生成结构定义
        if "structure" in spec:
            struct = spec["structure"]
            fields = "\n".join(
                f"  {f['name']} : {f['type']}"
                for f in struct["fields"]
            )
            parts.append(f"""
structure {struct['name']} where
{fields}
  deriving Repr
""")
        
        # 生成定理
        if "theorems" in spec:
            for thm in spec["theorems"]:
                parts.append(f"""
theorem {thm['name']} : {thm['statement']} := by
  {thm.get('proof', 'sorry')}
""")
        
        return "\n".join(parts)
    
    def generate_verification_module(self, 
                                     module_name: str,
                                     definitions: List[Dict]) -> str:
        """
        生成验证模块
        """
        header = f"/- {module_name} -/\n\nimport Qq\n\nopen Qq\n\n"
        
        content = []
        for defn in definitions:
            if defn["kind"] == "structure":
                content.append(self._gen_struct(defn))
            elif defn["kind"] == "theorem":
                content.append(self._gen_theorem(defn))
            elif defn["kind"] == "instance":
                content.append(self._gen_instance(defn))
        
        return header + "\n".join(content)
    
    def _gen_struct(self, d: Dict) -> str:
        fields = "\n".join(f"  {f['name']} : {f['type']}" for f in d["fields"])
        return f"""
structure {d['name']} where
{fields}
  deriving Repr
"""
    
    def _gen_theorem(self, d: Dict) -> str:
        return f"""
theorem {d['name']} : {d['statement']} := by
  {d.get('proof', 'sorry')}
"""
    
    def _gen_instance(self, d: Dict) -> str:
        return f"""
instance : {d['class']} {d['type']} where
  {d.get('body', 'sorry')}
"""
```

### 4. 宏定义辅助

```lean
-- Lean4AI/Quote4/Macros.lean

import Qq
import Lean.Meta
import Lean.Elab.Command

open Qq Lean Meta Elab Command

namespace Lean4AI.Quote4.Macros

/-- 自动生成访问器 -/
def mkAccessors (structName : Name) (fields : List (Name × Q Type)) 
    : MetaM (List (Q Command)) := do
  fields.mapM fun (fieldName, fieldType) => do
    let accessorName := structName ++ fieldName
    pure q(def $accessorName (s : $structName) : $fieldType := s.$fieldName)

/-- 自动生成修改器 -/
def mkModifiers (structName : Name) (fields : List (Name × Q Type))
    : MetaM (List (Q Command)) := do
  fields.mapM fun (fieldName, fieldType) => do
    let modifierName := structName ++ s!"set{fieldName.capitalize}"
    pure q(def $modifierName (s : $structName) (v : $fieldType) : $structName :=
      { s with $fieldName := v })

/-- 生成 Builder 模式 -/
def mkBuilder (structName : Name) (fields : List (Name × Q Type))
    : MetaM (Q Command) := do
  let builderFields := fields.map fun (name, ty) => q({ $name : Option $ty })
  
  pure q(structure $structName.Builder where
    $builderFields:*
    
    def build (b : Builder) : Option $structName := do
      -- 从 builder 构建结构
      some { -- 字段初始化 }
  )

/-- 生成 lenses -/
def mkLenses (structName : Name) (fields : List (Name × Q Type))
    : MetaM (List (Q Command)) := do
  fields.mapM fun (fieldName, fieldType) => do
    let lensName := structName ++ s!"{fieldName.capitalize}Lens"
    pure q(def $lensName : Lens $structName $fieldType where
      get := (·.$fieldName)
      set := fun s v => { s with $fieldName := v })

end Lean4AI.Quote4.Macros
```

---

## 实际应用示例

### 1. 动态定理生成

```lean
import Qq
import Lean.Meta

open Qq Lean Meta

/-- 根据约束动态生成定理 -/
def mkConstraintTheorem (name : String) (lhs rhs : Q Nat) : Q Command :=
  q(theorem $(mkIdent name) : $lhs ≤ $rhs := by native_decide)

-- 批量生成
def mkBudgetTheorems (projects : List (String × Q Nat × Q Nat)) : Q Command :=
  let theorems := projects.map fun (name, budget, spent) =>
    q(theorem $(mkIdent s!"{name}_budget") : $spent ≤ $budget := by native_decide)
  
  q(section
    $theorems:*
    end)
```

### 2. 策略组合子

```lean
import Qq
import Lean.Elab.Tactic

open Qq Lean Elab Tactic

/-- 组合策略 -/
def composeTactics (t1 t2 : Q Tactic) : Q Tactic :=
  q(seq $t1 $t2)

/-- 条件策略 -/
def condTactic (cond : Q Bool) (thenTactic elseTactic : Q Tactic) : Q Tactic :=
  q(if $cond then $thenTactic else $elseTactic)

/-- 重复策略 -/
def repeatTactic (t : Q Tactic) : Q Tactic :=
  q(repeat $t)

/-- 尝试策略 -/
def tryTactic (t : Q Tactic) : Q Tactic :=
  q(try $t)
```

### 3. 类型安全 DSL

```lean
import Qq

open Qq

/-- 项目 DSL -/
def ProjectDSL := Q Type

def project : ProjectDSL := q(Project)
def task : ProjectDSL := q(Task)
def sprint : ProjectDSL := q(Sprint)

/-- DSL 操作 -/
def mkProject (n : Q String) (b : Q Nat) : Q Project :=
  q({ name := $n, budget := $b, spent := 0, tasks := [] })

def addTask (p : Q Project) (t : Q Task) : Q Project :=
  q({ $p with tasks := $t :: p.tasks })

def completeTask (p : Q Project) (idx : Q Nat) : Q Project :=
  q({ $p with tasks := p.tasks.set $idx { p.tasks.get! $idx with status := Status.done } })
```

---

## 性能考虑

### 引用开销

```lean
-- 编译时生成 (推荐)
def myExpr : Q Nat := q(1 + 2 + 3)

-- 运行时生成 (谨慎使用)
def mkExpr (n : Nat) : Q Nat := q($n + 1)
```

### 优化技巧

```lean
-- 缓存引用
def cachedAdd : Q (Nat → Nat → Nat) := q(Nat.add)

-- 避免重复拼接
def efficientConcat (xs : List (Q Nat)) : Q (List Nat) := Id.run do
  if xs.isEmpty then q([])
  else q([$xs,*])
```

---

## 项目统计更新

| 指标 | 更新前 | 更新后 |
|------|--------|--------|
| 集成项目数 | 26 | 27 |
| 元编程工具 | 2 | 3 |
| Stars 总和 | ~19,142 | ~19,244 |

---

## 快速开始

```bash
# 安装
cd /mnt/c/workspace/math/lean4ai
git clone https://github.com/leanprover-community/quote4.git

# 在 lakefile 中添加
# require quote4 from git "https://github.com/leanprover-community/quote4"

# 使用
# import Qq
-- open Qq
-- def myExpr : Q Nat := q(42)
```

---

**版本**: 18.0.0 (Twenty-Seven-in-One)
**更新日期**: 2025-03-25
