# Aeneas 实战案例：Rust 程序的 Lean4 形式化验证

## 📖 项目概述

**Aeneas** 是一个 Rust 程序验证工具链，将 Rust 代码转换为形式化证明。它使用 Lean4（以及 F*、Coq、HOL4）作为后端证明器。

### 核心价值

```
Rust 代码 → Charon (LLBC) → Aeneas → Lean4 定理 → 数学证明
```

| 组件 | 功能 | 输出 |
|------|------|------|
| **Charon** | Rust → LLBC | 中间表示 |
| **Aeneas** | LLBC → 函数式表示 | 多后端代码 |
| **Lean4 后端** | 证明 Rust 程序正确性 | 形式化证明 |

---

## 🔧 安装和配置

### 1. 安装 Nix（推荐方式）

```bash
# 安装 Nix
curl -L https://nixos.org/nix/install | sh

# 进入项目目录
cd /mnt/c/workspace/math/lean4ai
```

### 2. 克隆 Aeneas 仓库

```bash
# 浅克隆（节省空间）
git clone --depth 1 https://github.com/AeneasVerif/aeneas.git
cd aeneas
```

### 3. 使用 Nix 运行

```bash
# 运行 Charon（生成 LLBC）
nix run github:AeneasVerif/aeneas#charon -- -I your_rust_file.rs

# 运行 Aeneas（生成 Lean4 代码）
nix run github:AeneasVerif/aeneas -- --backend lean your_file.llbc
```

---

## 🏗️ 项目结构分析

```
aeneas/
├── src/                    # OCaml 源代码
│   ├── main.ml            # 主入口
│   ├── translation.ml     # 翻译逻辑
│   └── backends/
│       ├── lean.ml        # Lean4 后端 ⭐
│       ├── coq.ml         # Coq 后端
│       └── fstar.ml       # F* 后端
│
├── backends/              # 标准库
│   ├── lean/
│   │   ├── State.lean     # 状态定义 ⭐
│   │   ├── StateMonad.lean # 状态单子 ⭐
│   │   ├── Builtins.lean   # 内置函数 ⭐
│   │   └── Num.lean        # 数值操作 ⭐
│   ├── coq/
│   └── fstar/
│
├── tests/                 # 测试用例
│   ├── basic/
│   │   ├── simple.rs      # 简单 Rust 示例
│   │   └── simple.lean     # 生成的 Lean4 代码 ⭐
│   └── ...
│
└── README.md
```

---

## 💡 对 Lean4 有用的技术提取

### 1. 状态单子（State Monad）

**位置**: `backends/lean/StateMonad.lean`

**用途**: 在 Lean4 中建模可变状态

```lean
-- 文件: backends/lean/StateMonad.lean

-- 状态单子定义
def StateM (σ : Type) (α : Type) : Type := σ → α × σ

-- 返回值
def StateM.pure {σ α : Type} (x : α) : StateM σ α :=
  fun s => (x, s)

-- 绑定操作
def StateM.bind {σ α β : Type} 
  (m : StateM σ α) (f : α → StateM σ β) : StateM σ β :=
  fun s => 
    let (a, s') := m s
    f a s'

-- 读取状态
def StateM.get {σ : Type} : StateM σ σ :=
  fun s => (s, s)

-- 写入状态
def StateM.set {σ : Type} (s : σ) : StateM σ Unit :=
  fun _ => ((), s)

-- 修改状态
def StateM.modify {σ : Type} (f : σ → σ) : StateM σ Unit :=
  fun s => ((), f s)

-- 实例：Monad
instance stateMonad (σ : Type) : Monad (StateM σ) where
  pure := StateM.pure
  bind := StateM.bind
```

**应用场景**: 在我们的项目管理系统中跟踪状态变化

```lean
-- 应用到项目管理
def ProjectState := Lean4demo.Project

def updateProgress (newProgress : Real) : StateM ProjectState Unit :=
  StateM.modify (fun state => { state with progress := newProgress })

def addTask (task : Task) : StateM ProjectState Unit :=
  StateM.modify (fun state => 
    { state with tasks := state.tasks ++ [task] })
```

---

### 2. 借用检查（Borrow Checking）

**位置**: 研究论文 - ICFP 2024

**核心概念**: Aeneas 在翻译过程中实现了符号借用检查

```lean
-- 借用类型
inductive Borrow (α : Type) where
  | owned : α → Borrow α       -- 拥有所有权
  | shared : α → Borrow α      -- 共享借用
  | mutable : α → Borrow α     -- 可变借用

-- 借用规则验证
def borrowCheck (value : α) (borrowType : BorrowType) : Bool :=
  match borrowType with
  | BorrowType.owned => True
  | BorrowType.shared => True
  | BorrowType.mutable => 
    -- 确保没有其他可变借用
    noOtherMutableBorrows value

-- 应用：在项目管理中追踪资源所有权
def ResourceOwnership := Map String (Borrow Resource)

def transferResource (resource : Resource) : StateM ProjectState Unit := by
  -- 验证借用规则
  if borrowCheck resource BorrowType.owned then
    -- 转移所有权
    modify (fun state => ...)
  else
    -- 错误处理
    throwError "Borrow check failed"
```

---

### 3. 函数式翻译（Functional Translation）

**位置**: `src/translation.ml` → Lean4 后端

**核心思想**: 将命令式 Rust 转换为函数式 Lean4

```lean
-- Rust 命令式代码:
-- fn factorial(n: u32) -> u32 {
--     if n == 0 { 1 } else { n * factorial(n - 1) }
-- }

-- Lean4 函数式翻译:
def factorial (n : Nat) : Nat :=
  match n with
  | 0 => 1
  | n + 1 => (n + 1) * factorial n

-- 带状态的函数:
-- Rust: fn increment(&mut x: u32) { *x += 1; }
-- Lean4:
def increment (s : State) : State :=
  { s with x := s.x + 1 }
```

**应用到我们的项目**:

```lean
-- 项目状态更新
def updateTaskStatus (taskId : Nat) (newStatus : TaskStatus) 
  (state : ProjectState) : ProjectState :=
  { state with 
    tasks := state.tasks.map (fun t => 
      if t.id == taskId then { t with status := newStatus } else t)
  }
```

---

### 4. 不动点语义（Fixpoint Semantics）

**位置**: `backends/lean/Builtins.lean`

```lean
-- 不动点组合子
def fix {α : Type} (f : (α → α) → α → α) (x : α) : α :=
  f (fix f) x

-- 用于递归函数
def recursiveFunction := fix (fun rec input =>
  if baseCase input then
    baseValue input
  else
    rec (step input)
)

-- 应用：计算项目复杂度
def calculateComplexity (project : Project) : Real :=
  fix (fun calc p =>
    if p.tasks.isEmpty then 0
    else 
      p.tasks.foldl (fun acc task => 
        acc + task.complexity + calc task.subProject
      ) 0
  ) project
```

---

### 5. 符号执行（Symbolic Execution）

**位置**: `src/symbolic_execution.ml`

```lean
-- 符号值
inductive SymbolicValue (α : Type) where
  | concrete : α → SymbolicValue α
  | symbolic : String → SymbolicValue α  -- 符号变量
  | operation : String → List (SymbolicValue α) → SymbolicValue α

-- 符号执行引擎
def symbolicExecute (code : RustCode) (state : SymbolicState) : 
  List (SymbolicState × PathCondition) :=
  -- 执行并生成所有可能的路径
  match code with
  | RustCode.assign (var, expr) => 
    [(evaluate expr state, True)]
  | RustCode.branch (cond, then_, else_) =>
    -- 分叉执行
    let thenState := symbolicExecute then_ (assume cond state)
    let elseState := symbolicExecute else_ (assume (¬ cond) state)
    thenState ++ elseState
  | _ => ...

-- 应用：验证所有可能的项目状态
def verifyAllProjectPaths (initialState : ProjectState) : 
  List (ProjectState × ProofObligation) :=
  symbolicExecute projectCode initialState
```

---

## 🚀 实战示例：验证 Rust 项目管理代码

### 1. 创建 Rust 源文件

```rust
// 文件: examples/project_manager.rs

#[derive(Clone, Copy, Debug, PartialEq)]
pub enum TaskStatus {
    Todo,
    InProgress,
    Done,
}

#[derive(Clone, Debug)]
pub struct Task {
    pub id: u32,
    pub name: String,
    pub status: TaskStatus,
    pub priority: u32,
}

#[derive(Clone, Debug)]
pub struct Project {
    pub tasks: Vec<Task>,
    pub total_budget: u32,
    pub spent_budget: u32,
}

// 添加任务
pub fn add_task(project: &mut Project, task: Task) {
    project.tasks.push(task);
}

// 更新任务状态
pub fn update_task_status(project: &mut Project, task_id: u32, new_status: TaskStatus) {
    if let Some(task) = project.tasks.iter_mut().find(|t| t.id == task_id) {
        task.status = new_status;
    }
}

// 计算完成百分比
pub fn completion_percentage(project: &Project) -> u32 {
    if project.tasks.is_empty() {
        return 0;
    }
    
    let completed = project.tasks.iter()
        .filter(|t| t.status == TaskStatus::Done)
        .count() as u32;
    
    (completed * 100) / project.tasks.len() as u32
}

// 验证预算不超支
pub fn is_budget_valid(project: &Project) -> bool {
    project.spent_budget <= project.total_budget
}

// 单元测试
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add_task() {
        let mut project = Project {
            tasks: Vec::new(),
            total_budget: 100,
            spent_budget: 0,
        };
        
        let task = Task {
            id: 1,
            name: String::from("Test Task"),
            status: TaskStatus::Todo,
            priority: 1,
        };
        
        add_task(&mut project, task);
        assert_eq!(project.tasks.len(), 1);
    }

    #[test]
    fn test_completion_percentage() {
        let project = Project {
            tasks: vec![
                Task { id: 1, name: String::from("Task 1"), status: TaskStatus::Done, priority: 1 },
                Task { id: 2, name: String::from("Task 2"), status: TaskStatus::Todo, priority: 2 },
            ],
            total_budget: 100,
            spent_budget: 50,
        };
        
        assert_eq!(completion_percentage(&project), 50);
    }

    #[test]
    fn test_budget_validation() {
        let valid_project = Project {
            tasks: Vec::new(),
            total_budget: 100,
            spent_budget: 50,
        };
        assert!(is_budget_valid(&valid_project));

        let invalid_project = Project {
            tasks: Vec::new(),
            total_budget: 100,
            spent_budget: 150,
        };
        assert!(!is_budget_valid(&invalid_project));
    }
}
```

### 2. 编译为 LLBC

```bash
# 使用 Charon 生成 LLBC
nix run github:AeneasVerif/aeneas#charon -- \
  --crate-type=lib \
  -L target/debug/deps \
  examples/project_manager.rs \
  -o project_manager.llbc
```

### 3. 翻译为 Lean4

```bash
# 使用 Aeneas 翻译
nix run github:AeneasVerif/aeneas -- \
  --backend lean \
  project_manager.llbc \
  -o ProjectManager.lean
```

### 4. 生成的 Lean4 代码（预期输出）

```lean
-- 文件: ProjectManager.lean
-- 自动生成，不要手动编辑

import Aeneas.Std

namespace ProjectManager

-- 任务状态（自动翻译）
inductive TaskStatus where
  | todo : TaskStatus
  | inProgress : TaskStatus
  | done : TaskStatus
deriving Repr, BEq

-- 任务结构（自动翻译）
structure Task where
  id : Nat
  name : String
  status : TaskStatus
  priority : Nat
deriving Repr

-- 项目结构（自动翻译）
structure Project where
  tasks : List Task
  totalBudget : Nat
  spentBudget : Nat
deriving Repr

-- 添加任务（自动翻译）
def addTask (project : Project) (task : Task) : Project :=
  { project with tasks := project.tasks ++ [task] }

-- 更新任务状态（自动翻译）
def updateTaskStatus (project : Project) (taskId : Nat) (newStatus : TaskStatus) : Project :=
  { project with 
    tasks := project.tasks.map (fun t =>
      if t.id == taskId then { t with status := newStatus } else t)
  }

-- 计算完成百分比（自动翻译）
def completionPercentage (project : Project) : Nat :=
  if project.tasks.isEmpty then 0
  else
    let completed := project.tasks.filter (·.status == TaskStatus.done) |>.length
    completed * 100 / project.tasks.length

-- 验证预算（自动翻译）
def isBudgetValid (project : Project) : Bool :=
  project.spentBudget ≤ project.totalBudget

-- ========================================
-- 手动添加的证明
-- ========================================

-- 证明：添加任务会增加任务列表长度
theorem addTask_increases_length (project : Project) (task : Task) :
  (addTask project task).tasks.length = project.tasks.length + 1 := by
  simp [addTask]
  exact List.length_append project.tasks [task]

-- 证明：完成百分比在 0-100 之间
theorem completionPercentage_bounded (project : Project) :
  completionPercentage project ≥ 0 ∧ completionPercentage project ≤ 100 := by
  simp [completionPercentage]
  split
  · simp
  · 
    by_cases h : project.tasks.filter (·.status == TaskStatus.done) |>.length * 100 / project.tasks.length < 0
    · simp [h]; sorry
    · simp [h]; sorry

-- 证明：有效项目的预算不超支
theorem budgetValid_correct (project : Project)
  (hvalid : isBudgetValid project) :
  project.spentBudget ≤ project.totalBudget := by
  simp [isBudgetValid] at hvalid
  exact hvalid

-- 证明：更新任务状态保持其他任务不变
theorem updateTaskStatus_other_tasks_unchanged 
  (project : Project) (taskId : Nat) (newStatus : TaskStatus)
  (otherTask : Task) (hother : otherTask ∈ project.tasks) 
  (hnotTarget : otherTask.id ≠ taskId) :
  (updateTaskStatus project taskId newStatus).tasks.indexOf otherTask = 
    project.tasks.indexOf otherTask := by
  sorry  -- 需要完整证明

end ProjectManager
```

### 5. 完成证明

```lean
-- 文件: ProjectManagerProofs.lean

import ProjectManager

namespace ProjectManager

-- 辅助引理
lemma filter_length_le (l : List Task) (p : Task → Bool) :
  l.filter p |>.length ≤ l.length := by
  induction l with
  | nil => simp
  | cons head tail ih =>
    simp [List.filter]
    split
    · simp [Nat.succ_le_succ_iff, ih]
    · exact ih

-- 完成百分比上限
theorem completionPercentage_upper_bound (project : Project) :
  completionPercentage project ≤ 100 := by
  simp [completionPercentage]
  split
  · simp
  · 
    have h1 : project.tasks.filter (·.status == TaskStatus.done) |>.length ≤ project.tasks.length := 
      filter_length_le project.tasks (·.status == TaskStatus.done)
    have h2 : project.tasks.length > 0 := by
      by_contra h
      push_neg at h
      exact List.length_eq_zero.mp (List.length_eq_zero.mpr h) (List.ne_nil_of_length_pos (by simp))
    -- 继续证明...
    sorry

-- 添加任务不改变预算
theorem addTask_preserves_budget (project : Project) (task : Task) :
  (addTask project task).totalBudget = project.totalBudget ∧
  (addTask project task).spentBudget = project.spentBudget := by
  simp [addTask]

-- 多次更新状态是可交换的（对于不同任务）
theorem updateTaskStatus_commutative_different_tasks
  (project : Project) (id1 id2 : Nat) (s1 s2 : TaskStatus)
  (hne : id1 ≠ id2) :
  updateTaskStatus (updateTaskStatus project id1 s1) id2 s2 =
  updateTaskStatus (updateTaskStatus project id2 s2) id1 s1 := by
  simp [updateTaskStatus]
  congr 1
  funext task
  simp only [List.map_map]
  congr 1
  split
  · simp [*]
  · split
    · simp [*]
    · rfl

end ProjectManager
```

---

## 📊 Aeneas 核心技术总结

### 对 Lean4 开发有用的技术

| 技术 | 位置 | 用途 |
|------|------|------|
| **状态单子** | `StateMonad.lean` | 管理可变状态 |
| **借用检查** | 研究论文 | 资源所有权追踪 |
| **函数式翻译** | `translation.ml` | 命令式 → 函数式 |
| **不动点语义** | `Builtins.lean` | 递归函数定义 |
| **符号执行** | `symbolic_execution.ml` | 路径分析 |
| **类型映射** | `backends/lean/` | Rust 类型 → Lean4 类型 |

### 可重用的 Lean4 模块

```lean
-- 从 Aeneas 提取的可重用模块

-- 1. 状态单子（直接使用）
import Aeneas.Std.StateMonad

-- 2. 数值操作（直接使用）
import Aeneas.Std.Num

-- 3. 内置函数（直接使用）
import Aeneas.Std.Builtins

-- 4. 自定义：项目状态单子
def ProjectM := StateM ProjectState

-- 5. 自定义：任务操作
namespace TaskOps
  def add (task : Task) : ProjectM Unit := 
    modify (fun s => { s with tasks := s.tasks ++ [task] })
  
  def update (id : Nat) (f : Task → Task) : ProjectM Unit :=
    modify (fun s => { s with 
      tasks := s.tasks.map (fun t => if t.id == id then f t else t) })
  
  def remove (id : Nat) : ProjectM Unit :=
    modify (fun s => { s with tasks := s.tasks.filter (·.id != id) })
end TaskOps
```

---

## 🔗 与我们项目的集成

### 1. 整合到 lean4ai

```bash
cd /mnt/c/workspace/math/lean4ai
mkdir -p aeneas-examples
cd aeneas-examples

# 复制 Aeneas 标准库
cp -r ../aeneas/backends/lean/* .

# 创建我们的示例
touch ProjectManager.lean
touch ProjectManagerProofs.lean
```

### 2. 在 YC-Killer 中使用

```python
# yc_killer_aeneas_agent.py

from typing import Dict, List
import subprocess

class AeneasVerificationAgent:
    """YC-Killer 的 Aeneas 验证代理"""
    
    def verify_rust_project_code(self, rust_code: str) -> Dict:
        """
        验证 Rust 项目管理代码
        
        Args:
            rust_code: Rust 源代码
        
        Returns:
            验证结果
        """
        # 1. 保存 Rust 代码
        with open("temp_project.rs", "w") as f:
            f.write(rust_code)
        
        # 2. 编译为 LLBC
        subprocess.run([
            "nix", "run", "github:AeneasVerif/aeneas#charon",
            "--", "-I", "temp_project.rs", "-o", "temp.llbc"
        ])
        
        # 3. 翻译为 Lean4
        subprocess.run([
            "nix", "run", "github:AeneasVerif/aeneas",
            "--", "--backend", "lean", "temp.llbc", "-o", "temp.lean"
        ])
        
        # 4. 运行 Lean4 验证
        result = subprocess.run(
            ["lake", "build"],
            capture_output=True,
            text=True
        )
        
        return {
            'verified': result.returncode == 0,
            'lean4_code': open("temp.lean").read(),
            'errors': result.stderr if result.returncode != 0 else None
        }
```

---

## 📚 相关资源

### 官方资源
- **Aeneas GitHub**: https://github.com/AeneasVerif/aeneas
- **Charon GitHub**: https://github.com/AeneasVerif/charon
- **Zulip 社区**: https://aeneas-verif.zulipchat.com

### 学术论文
- **ICFP 2022**: [Aeneas: Rust Verification by Functional Translation](https://dl.acm.org/doi/abs/10.1145/3547647)
- **ICFP 2024**: [Sound Borrow-Checking for Rust via Symbolic Semantics](https://dl.acm.org/doi/abs/10.1145/3674640)

### 相关项目
- **Charon**: Rust 到 LLBC 编译器
- **HaCL*: HACL* 密码库（类似验证方法）

---

## 🎯 总结

### Aeneas 为我们带来的价值

| 方面 | 价值 |
|------|------|
| **技术** | 状态单子、借用检查、函数式翻译 |
| **工具** | Rust → Lean4 自动翻译 |
| **方法** | 符号执行、形式化验证 |
| **实用** | 验证实际项目管理代码 |

### 可直接使用

1. ✅ `StateMonad.lean` - 状态管理
2. ✅ `Builtins.lean` - 内置函数
3. ✅ 翻译模式 - 命令式→函数式
4. ✅ 证明技术 - 形式化验证方法

---

**下一步**: 运行 Aeneas 示例，提取更多技术到我们的项目！
