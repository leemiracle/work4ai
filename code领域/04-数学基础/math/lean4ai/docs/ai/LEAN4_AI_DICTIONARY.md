# Lean4 + AI 专项词典

> 最后更新：2025-03 | 面向形式化证明与AI结合的专项指南

---

## 📜 Lean与AI历史

```
Timeline: 定理证明 + AI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1970s  自动定理证明起步 (Boyer-Moore, LCF)
  ↓
1980s  Coq, Isabelle等证明助手诞生
  ↓
2013   Lean 1发布 (Leonardo de Moura)
  ↓
2017   DeepMath - 首次用神经网络辅助证明
  ↓
2019   Holist, TacticToe - ML选择策略
  ↓
2020   ProofNet, HOList基准
  ↓
2021   Lean 3成熟，mathlib壮大
  ↓
2021   GPT-f - 用Transformer生成证明
  ↓
2022   AlphaTensor - AI发现新算法
  ↓
2023   Lean 4发布，更强大的元编程
  ↓
2023   LeanDojo - Lean交互框架
  ↓
2023   LeanCopilot - LLM辅助定理证明
  ↓
2024   AlphaProof - DeepMind强化学习证明系统
  ↓
2024   IMO银牌 - AI首次在数学竞赛获佳绩
  ↓
2025   形式化证明成为AI推理能力测试场
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 1. Lean4基础概念

### 什么是Lean？

**费曼解释**：Lean是一个"编程语言 + 证明助手"。你可以写程序，也可以写数学证明，Lean会自动检查证明是否正确。

**特点**：
- **形式化**：每个证明都要机器验证
- **可编程**：可以写程序，也可以写证明
- **交互式**：一步步构建证明
- **库丰富**：mathlib4有海量数学库

**类比**：
- 传统数学：写在纸上，靠人检查
- Lean：写在电脑里，机器自动检查

---

### Lean vs 其他证明助手

| 系统 | 特点 | 适用场景 |
|------|------|----------|
| **Lean 4** | 现代化、可编程、活跃社区 | 数学形式化、程序验证 |
| **Coq** | 老牌、稳定、学术界主流 | 研究、教学 |
| **Isabelle** | 强大的自动化 | 大规模证明 |
| **Agda** | 纯函数式 | 类型论研究 |
| **Rocq** | Coq的升级版 | 研究 |

**为什么选Lean 4**：
1. 现代化的语言设计
2. 强大的元编程（写 tactic）
3. mathlib4 社区活跃
4. AI工具支持好

---

### Lean4核心概念

#### 1. 类型论基础

**费曼解释**：在Lean中，一切都是"类型"。类型就像是"标签"，告诉你这个东西是什么。

```lean
-- 自然数是类型
#check Nat       -- Nat : Type

-- 42是自然数
#check 42        -- 42 : Nat

-- 命题也是类型
#check 2 + 2 = 4 -- 2 + 2 = 4 : Prop
```

**核心思想**：
- 命题 = 类型（Prop）
- 证明 = 项（term）
- 类型检查 = 证明检查

---

#### 2. Tactics（策略）

**费曼解释**：Tactic是"证明指令"，告诉Lean怎么一步步证明。

**常用tactics**：

| Tactic | 作用 | 示例 |
|--------|------|------|
| `intro` | 引入假设 | `intro h` |
| `apply` | 应用定理 | `apply Nat.add_comm` |
| `exact` | 精确匹配 | `exact h` |
| `simp` | 简化 | `simp [Nat.add_comm]` |
| `rw` | 重写 | `rw [Nat.add_comm]` |
| `induction` | 归纳 | `induction n with` |
| `cases` | 分类讨论 | `cases h` |
| `have` | 引入中间结论 | `have h1 : ...` |
| `calc` | 计算证明 | `calc ...` |

**示例**：
```lean
example (a b : Nat) : a + b = b + a := by
  -- 使用交换律
  rw [Nat.add_comm]
```

---

#### 3. Inductive Types（归纳类型）

**费曼解释**：定义新的数据类型，通过"构造子"创建实例。

```lean
-- 自然数的定义
inductive Nat where
  | zero : Nat
  | succ : Nat → Nat

-- 列表的定义
inductive List (α : Type) where
  | nil : List α
  | cons : α → List α → List α
```

---

#### 4. Type Classes（类型类）

**费曼解释**：类似于接口，定义类型应该有什么能力。

```lean
-- 定义"可相加"的类型类
class Add (α : Type) where
  add : α → α → α

-- 为Nat实现
instance : Add Nat where
  add := Nat.add
```

---

## 2. mathlib4库

### 什么是mathlib4？

**费曼解释**：mathlib4是Lean的"数学标准库"，包含几乎所有大学数学内容的形式化定义和定理。

**规模**：
- 100万+行代码
- 15万+定理
- 覆盖：代数、分析、拓扑、数论、组合...

**为什么重要**：
1. 不用重复造轮子
2. 可靠的数学基础
3. 活跃的社区维护

---

### mathlib4使用

#### 安装

```bash
# 创建项目
lake new my_project

# 修改lakefile.toml
[[require]]
name = "mathlib"
scope = "leanprover-community"
rev = "v4.12.0"

# 更新
lake update
```

#### 使用

```lean
import Mathlib.Tactic
import Mathlib.Data.Nat.Basic

example (n : Nat) : n + 0 = n := by
  rw [Nat.add_zero]
```

---

### 常用模块

| 模块 | 内容 |
|------|------|
| `Mathlib.Tactic` | 常用tactic |
| `Mathlib.Data.Nat.Basic` | 自然数基础 |
| `Mathlib.Data.Real.Basic` | 实数基础 |
| `Mathlib.Topology.Basic` | 拓扑学 |
| `Mathlib.Algebra.Group.Basic` | 群论 |
| `Mathlib.Analysis.SpecialFunctions.Pow.Real` | 实分析 |

---

## 3. AI辅助定理证明

### 为什么需要AI？

**费曼解释**：证明定理很难，AI可以帮助：
1. **搜索证明路径** - 从海量定理中找合适的
2. **生成tactic** - 建议下一步用什么策略
3. **完成简单证明** - 自动化繁琐部分

---

### 主流AI工具

#### LeanCopilot ⭐⭐⭐⭐⭐

**费曼解释**：LLM驱动的"副驾驶"，为你的证明提供智能建议。

**GitHub**: lean-dojo/LeanCopilot

**安装**：
```lean
-- lakefile.toml
[[require]]
name = "LeanCopilot"
scope = "lean-dojo"
rev = "main"
```

**使用**：
```lean
import LeanCopilot

example (a b : Nat) : a + b = b + a := by
  -- 使用AI建议
  suggest_tactics
  
  -- 或自动完成
  autoprove
```

**能力**：
- 预测下一步tactic
- 生成完整证明
- 基于mathlib4训练

---

#### AlphaProof (DeepMind) ⭐⭐⭐⭐⭐

**费曼解释**：DeepMind的强化学习证明系统，在IMO竞赛中获得银牌。

**特点**：
- 强化学习
- 形式化证明
- 可验证

**成就**：
- 2024 IMO 4/6题
- 首次在数学竞赛与人类竞争

**技术**：
- Lean形式化
- AlphaZero风格搜索
- 自动定理生成

---

#### LLM-based Provers

**GPT-f (Meta)**
- 用Transformer生成证明
- 在Metamath上训练

**ProofNet**
- Lean 3的神经网络证明器
- 预测tactic

**Holist (Google)**
- HOL-Light上的神经网络
- 预测证明步骤

---

### AI证明的工作原理

**流程**：
```
1. 形式化目标（要证明的命题）
   ↓
2. 提取当前证明状态
   ↓
3. 编码为模型输入
   ↓
4. 模型预测下一步
   ├── 预测tactic
   ├── 预测下一步定理
   └── 预测完整证明
   ↓
5. 执行预测
   ↓
6. 检查是否完成
   └── 是 → 证明完成
   └── 否 → 回到步骤2
```

---

### AI证明的挑战

#### 1. 搜索空间爆炸

**费曼解释**：可能的证明路径太多，AI难以找到正确的。

**原因**：
- mathlib4有15万+定理
- 每步有无数选择
- 长证明需要多步

**解决方案**：
- 更强的模型
- 更好的搜索算法
- 形式化引导

---

#### 2. 长期推理

**费曼解释**：复杂证明需要"长远规划"，LLM不擅长。

**解决方案**：
- 强化学习（AlphaProof）
- 分层规划
- 人机协作

---

#### 3. 数据稀缺

**费曼解释**：训练AI需要大量证明数据，但形式化证明数据很少。

**解决方案**：
- 合成数据
- 迁移学习
- 主动学习

---

## 4. Lean4开发实战

### 项目结构

```
my_project/
├── lakefile.toml      # 项目配置
├── lean-toolchain     # Lean版本
├── MyProject/
│   ├── Basic.lean    # 基础定义
│   ├── Algebra.lean  # 代数相关
│   └── Analysis.lean # 分析相关
├── MyProject.lean    # 库入口
└── Main.lean         # 程序入口（如需）
```

---

### 开发流程

#### 1. 安装

```bash
# 安装elan（Lean版本管理器）
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh

# 创建项目
lake new my_project

# 进入项目
cd my_project
```

---

#### 2. 编写证明

**创建文件** `MyProject/Basic.lean`:
```lean
import Mathlib.Tactic
import Mathlib.Data.Nat.Basic

-- 定义偶数
def isEven (n : Nat) : Prop := ∃ k, n = 2 * k

-- 证明：偶数加偶数是偶数
theorem even_add_even {a b : Nat} 
    (ha : isEven a) (hb : isEven b) : isEven (a + b) := by
  -- 展开定义
  unfold isEven at *
  
  -- 从假设中提取k
  obtain ⟨ka, ha⟩ := ha
  obtain ⟨kb, hb⟩ := hb
  
  -- 重写
  rw [ha, hb]
  
  -- 简化
  ring
  
  -- 提供见证
  use ka + kb
  
  -- 证毕
  ring
```

---

#### 3. 运行检查

```bash
# 检查
lake build

# 如果成功，说明证明正确
```

---

### 常用工具

#### Loogle（引理搜索）

**费曼解释**：搜索引擎，帮你找需要的定理。

**使用**：
```bash
# 安装
lake install loogle

# 搜索
loogle "Nat → Nat → Prop"
loogle "_ + _ = _ + _"
```

---

#### VS Code插件

**功能**：
- 实时检查
- tactic建议
- 跳转定义
- 悬停信息

---

#### PaperProof（可视化）

**费曼解释**：把证明可视化，像纸上推导一样。

**GitHub**: Paper-Proof/paperproof

---

## 5. 形式化数学项目

### 大型项目

#### 1. Fermat's Last Theorem (FLT)

**费曼解释**：形式化费马大定理，数学史上的里程碑。

**状态**：进行中

**GitHub**: ImperialCollegeLondon/FLT

**意义**：
- 最复杂定理之一
- 需要大量数学库
- 推动mathlib发展

---

#### 2. Perfectoid Spaces

**费曼解释**：形式化Scholze的完美oid空间理论。

**成就**：完成

**意义**：
- 现代代数几何
- 顶尖数学验证了Lean

---

#### 3. Liquid Tensor Experiment

**费曼解释**：形式化Scholze的凝聚态数学。

**成就**：完成

**意义**：
- Peter Scholze亲自验证
- 证明AI辅助的可行性

---

### 教育项目

#### 1. Natural Number Game (NNG4)

**费曼解释**：游戏化学习Lean，从零开始证明自然数性质。

**地址**: https://adam.math.hhu.de/#/g/leanprover-community/NNG4

**特点**：
- 无需安装
- 游戏化
- 循序渐进

---

#### 2. Mathematics in Lean

**费曼解释**：用Lean学习数学，涵盖多个领域。

**地址**: https://leanprover-community.github.io/mathematics_in_lean/

---

#### 3. Theorem Proving in Lean 4

**费曼解释**：Lean 4官方教程，从基础到高级。

**地址**: https://lean-lang.org/theorem_proving_in_lean4/

---

## 6. AI + Lean 研究前沿

### 研究方向

#### 1. 自动证明生成

**目标**：AI自动生成完整证明

**方法**：
- LLM生成tactic序列
- 强化学习搜索
- 神经定理证明

**挑战**：
- 长期规划
- 搜索空间
- 正确性保证

---

#### 2. 证明补全

**目标**：AI辅助完成部分证明

**方法**：
- 下一步tactic预测
- 引理推荐
- 自动化simplification

**现状**：LeanCopilot已实现基础功能

---

#### 3. 反例生成

**目标**：当命题为假时，AI生成反例

**方法**：
- 搜索反例
- 生成矛盾

**应用**：帮助理解为什么命题不成立

---

#### 4. 自然语言到Lean

**目标**：从自然语言描述自动生成Lean代码

**方法**：
- LLM翻译
- 语义解析

**挑战**：
- 歧义消除
- 形式化准确

---

#### 5. Lean到自然语言

**目标**：把Lean证明翻译成可读的数学文本

**方法**：
- 模板生成
- LLM翻译

**应用**：证明文档化

---

### 重要论文

1. **"GPT-f"** (Polu & Sutskever, 2020)
   - 用Transformer生成Metamath证明

2. **"ProofNet"** (Azerbayev et al., 2023)
   - Lean 3的神经网络证明器

3. **"LeanDojo"** (Yang et al., 2023)
   - Lean与ML的交互框架

4. **"LeanCopilot"** (Song et al., 2023)
   - LLM辅助Lean证明

5. **"AlphaProof"** (DeepMind, 2024)
   - 强化学习数学推理

---

## 7. 实用资源

### 官方资源

| 资源 | 链接 |
|------|------|
| Lean官网 | https://lean-lang.org |
| mathlib4文档 | https://leanprover-community.github.io/mathlib4_docs |
| Lean Zulip | https://leanprover.zulipchat.com |

---

### 学习资源

| 资源 | 描述 |
|------|------|
| Natural Number Game | 游戏化入门 |
| Theorem Proving in Lean 4 | 官方教程 |
| Mathematics in Lean | 数学专题 |
| Functional Programming in Lean 4 | 函数式编程 |

---

### 工具

| 工具 | 用途 |
|------|------|
| VS Code + Lean4 | 开发环境 |
| Loogle | 引理搜索 |
| PaperProof | 可视化 |
| LeanCopilot | AI辅助 |

---

### 社区

- **Zulip**: 主要讨论平台
- **GitHub**: leanprover-community
- **Mathlib4**: 持续贡献

---

## 8. 最佳实践

### 1. 从小开始

```
先做简单证明 → 学习tactic → 再做复杂证明
```

---

### 2. 善用mathlib

```lean
-- 不要重复造轮子
-- 先搜索mathlib是否有现成定理
-- 使用Loogle搜索
```

---

### 3. 模块化

```lean
-- 分离定义和证明
-- 组织好模块结构
-- 写清楚文档
```

---

### 4. 使用AI辅助

```lean
import LeanCopilot

example : ... := by
  -- 卡住时让AI建议
  suggest_tactics
  
  -- 或尝试自动证明
  autoprove
```

---

### 5. 社区求助

```
卡住时：
1. 搜索Zulip
2. 搜索GitHub issues
3. 在Zulip提问
```

---

## 9. 未来展望

### 短期（1-2年）

- AI辅助证明更成熟
- mathlib4持续扩展
- 更多大型项目完成

---

### 中期（3-5年）

- 自动证明能力大幅提升
- 自然语言 ↔ Lean转换
- AI成为数学研究助手

---

### 长期（5年+）

- AI可能独立证明重要定理
- 形式化数学成为主流
- 数学教育与AI深度融合

---

## 🔗 总结

**Lean4 + AI = 形式化 + 智能化**

- **Lean4**：可靠的证明助手
- **mathlib4**：丰富的数学库
- **AI**：智能的辅助工具

**学习路径**：
```
1. 完成Natural Number Game
2. 阅读Theorem Proving in Lean 4
3. 探索mathlib4
4. 使用LeanCopilot
5. 参与社区贡献
```

---

*专项词典完成 | 持续更新 | 2025-03*
