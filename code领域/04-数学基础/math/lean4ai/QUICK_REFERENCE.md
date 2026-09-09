# Lean4 快速参考

## 环境验证

```bash
# 检查版本
lean --version   # 应显示 4.28.0
lake --version   # 应显示 5.0.0

# 代理已配置到 ~/.bashrc
source ~/.bashrc
```

## 常用命令

### 项目管理
```bash
lake new <name>              # 创建新项目
lake new <name> math         # 创建数学项目（含 mathlib）
lake build                   # 构建项目
lake clean                   # 清理构建
lake update                  # 更新依赖
lake exe cache get           # 下载 mathlib 缓存
```

### 开发流程
```bash
# 在 VS Code 中打开
code /mnt/c/workspace/math/lean4demo

# 或在 Neovim 中（如果安装了 lean.nvim）
nvim MyProject/Basic.lean
```

## 基础语法

### 定义
```lean
-- 函数定义
def add (a b : Nat) : Nat := a + b

-- 递归定义
def factorial : Nat → Nat
  | 0 => 1
  | n + 1 => (n + 1) * factorial n

-- 类型类实例
instance : Add Nat where
  add := Nat.add
```

### 证明
```lean
-- 基本战术
example : True := by trivial

example (p q : Prop) (hp : p) (hq : q) : p ∧ q := by
  constructor    -- 分解合取
  · exact hp     -- 第一部分
  · exact hq     -- 第二部分

-- 使用 grind（自动化）
example (x : Nat) : 0 < x + 1 := by grind

-- 数学归纳法
example (n : Nat) : 0 ≤ n := by
  induction n with
  | zero => trivial
  | succ n ih => simp [Nat.le_add_left]
```

### 类型
```lean
-- 基础类型
#check Nat         -- Type
#check Int         -- Type
#check Bool        -- Type
#check String      -- Type

-- 多态
def id {α : Type} (a : α) : α := a

-- 依赖类型
def Vec (α : Type) (n : Nat) : Type := ...

-- 结构体
structure Point where
  x : Float
  y : Float
  deriving Repr
```

## 常用战术

| 战术 | 用途 |
|------|------|
| `intro` | 引入假设 |
| `exact` | 提供精确项 |
| `apply` | 应用定理 |
| `simp` | 简化 |
| `grind` | 强力自动化 |
| `decide` | 可判定命题 |
| `ring` | 环等式 |
| `omega` | 线性算术 |
| `induction` | 归纳法 |
| `cases` | 情况分析 |
| `constructor` | 构造 |
| `left` / `right` | 析取 |
| `contradiction` | 矛盾 |
| `trivial` | 平凡证明 |

## 搜索工具

### Loogle
```
URL: https://loogle.lean-lang.org

查询示例:
  Nat → Nat → Nat        # 类型签名
  ?a → ?a → ?a           # 模式匹配
  List α → List α        # 泛型
  _ + _ = _              # 加法等式
```

### Mathlib 文档
```
https://leanprover-community.github.io/mathlib4_docs

常用模块:
  - Mathlib.Algebra.Group
  - Mathlib.Analysis.Calculus
  - Mathlib.Topology.Basic
  - Mathlib.NumberTheory.Primes
```

## 项目示例

### 示例 1: 简单定理
```lean
-- 文件: MyProject/Basic.lean

def double (n : Nat) : Nat := n + n

theorem double_eq_two_mul (n : Nat) : double n = 2 * n := by
  simp [double, Nat.two_mul]
```

### 示例 2: 质数
```lean
-- 文件: MyProject/Primes.lean

def IsPrime (n : Nat) : Prop :=
  1 < n ∧ ∀ k, 1 < k → k < n → ¬ k ∣ n

theorem prime_two : IsPrime 2 := by
  simp [IsPrime]
  constructor
  · decide
  · intro k hk1 hk2
    interval_cases k
```

### 示例 3: 列表操作
```lean
-- 文件: MyProject/List.lean

def myLength {α : Type} : List α → Nat
  | [] => 0
  | _ :: xs => 1 + myLength xs

theorem length_append {α : Type} (xs ys : List α) :
    myLength (xs ++ ys) = myLength xs + myLength ys := by
  induction xs with
  | nil => simp [myLength]
  | cons x xs ih => simp [myLength, ih, Nat.add_assoc]
```

## 调试技巧

### 查看目标
```lean
example (n : Nat) : n + 0 = n := by
  show_term (simp [Nat.add_zero])  -- 显示使用的项
```

### 逐步调试
```lean
example (p q r : Prop) : (p ∧ q) ∧ r → p := by
  intro h
  have ⟨hpq, hr⟩ := h
  have ⟨hp, hq⟩ := hpq
  exact hp
```

### 使用 suggest
```lean
example (n : Nat) : n + 0 = n := by
  suggest  -- 列出可能的战术
```

## VS Code 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+Space` | 自动补全 |
| `Ctrl+Click` | 跳转定义 |
| `F12` | 转到定义 |
| `Shift+F12` | 查找引用 |
| `Ctrl+Shift+P` | 命令面板 |
| `Lean: Restart` | 重启服务器 |

## 常见错误

### 1. 类型不匹配
```lean
-- 错误
example : Nat := "hello"  -- 类型错误

-- 修正
example : String := "hello"
```

### 2. 未解决的问题
```lean
-- 错误
example (n : Nat) : n = 0 := by
  sorry  -- 不完整证明

-- 修正（使用可判定的具体值）
example : 0 = 0 := by rfl
```

### 3. 缺失导入
```lean
-- 错误
#check List.map  -- 未知标识符

-- 修正
import Std.Data.List
#check List.map
```

## 获取帮助

1. **Zulip**: leanprover.zulipchat.com（最活跃）
2. **Loogle**: 搜索引理
3. **Mathlib 文档**: 查看定义
4. **示例代码**: mathlib4 源码

## 下一步

1. [ ] 完成 Natural Number Game
2. [ ] 阅读 TPIL 第 1-3 章
3. [ ] 尝试上面的示例
4. [ ] 加入 Zulip 社区
