# 讲透实分析 · 从 ε-δ 到 Lebesgue（配 Lean 形式化）

> 用「直觉 → ε-δ 数学 → Python 数值实验 → Lean 机械证明 → 不足 → 应用」的方式，把实分析从零讲透。
>
> 主教材：**Tao《Analysis I》** + **Tao 的 Lean companion**（2025-05 发布，把整本教材 Lean 化）。
> 配套严格版：**Rudin《Principles of Mathematical Analysis》**（数学生圣经）。
>
> 这不是又一本实分析教程——市面上已有 Tao / Rudin / Pugh / Abbott 等优秀教材。本系列做的是**三件那些教材不做的事**：
> 1. **配 Python 实验**：每个定义 / 定理都跑数值实验验证直觉（work4ai 铁律）
> 2. **配 Lean 形式化**：每个定理在 Tao Lean companion 里有对应 sorry 让你填
> 3. **配 NLP/ML 应用**：每个抽象概念链接到讲透NLP/讲透基础模型里的应用

---

## 〇、为什么实分析是你数学专家路径的"主战场"

### 0.1 实分析在数学知识图谱的位置

```
微积分（高中/大一）
    ↓
实分析（严格化微积分）  ← 你现在的位置
    ↓
    ├── 测度论（Lebesgue 积分）
    │     ↓
    │   概率论（严格）→ 随机过程 → SDE → 扩散模型
    │
    ├── 泛函分析（无限维分析）
    │     ↓
    │   算子理论 / 谱理论 / RKHS → Kernel 方法 / Neural Tangent
    │
    ├── 调和分析（Fourier 分析）
    │     ↓
    │   信号处理 / 语音 / 压缩感知
    │
    └── 复分析（一阶延伸）
          ↓
        解析数论 / 黎曼面
```

**实分析是所有"分析"分支的根**。学透实分析 = 打通 5 条数学分支的入口。

### 0.2 实分析对你目标（应用数学研究型工程师）的价值

- **ML 理论**：泛化界、优化收敛、损失景观——全需要实分析
- **扩散模型**：测度论 + 随机过程 + 泛函，根还是实分析
- **数值分析**：浮点数误差界、数值稳定性——实分析是基础
- **优化**：凸函数、Lipschitz 连续、对偶——实分析语言

### 0.3 2025 年学实分析的最优路径

```
传统路径（pre-2025）：
  纸笔学 Tao/Rudin → 做习题 → 几年后学透

2025 路径（你正在走的）：
  纸笔学 Tao → 做习题
  ↓
  Python 跑数值实验（验证直觉）   ← 本系列
  ↓
  在 Lean companion 里填 sorry    ← 本系列 + 讲透Lean4数学
  ↓
  写"讲透"笔记（输出倒逼输入）   ← 本系列
  ↓
  数学 + 工程 + 形式化三修
```

---

## 一、章节列表

| # | 文件 | 主题 | 状态 | Tao 章 | Rudin 章 |
|---|------|------|------|--------|----------|
| 00 | [`00-实分析是什么.md`](00-实分析是什么.md) | 为什么需要"严格化"微积分 | ✅ | 前言 | Ch 1 引论 |
| 01 | [`01-实数构造.md`](01-实数构造.md) | Dedekind cut / Cauchy 序列构造 ℝ | ✅ | Ch 5-6 | Ch 1 |
| 02 | [`02-极限与εδ.md`](02-极限与εδ.md) | 极限的 ε-δ 定义，机械验证 | ✅ | Ch 9 | Ch 4 |
| 03 | `03-连续性.md` | 一致连续 / 函数极限 | 📝 | Ch 9-10 | Ch 4 |
| 04 | `04-微分.md` | 导数 / 中值定理 / Taylor | 📝 | Ch 10-11 | Ch 5 |
| 05 | `05-Riemann积分.md` | Riemann 积分 / 微积分基本定理 | 📝 | Ch 11 | Ch 6 |
| 06 | `06-无穷级数.md` | 收敛判别 / 幂级数 / 一致收敛 | 📝 | Ch 7, 15 | Ch 3, 7-8 |
| 07 | `07-函数序列.md` | 一致收敛 / Stone-Weierstrass | 📝 | Ch 14, 16 | Ch 7 |
| 08 | `08-Lebesgue导引.md` | 为什么 Riemann 不够 → Lebesgue | 📝 | — | Ch 2, 11 |
| 09 | `09-度量空间导引.md` | 度量空间 / 紧致性 / 完备性 | 📝 | Ch 12-13 | Ch 2 |
| 10 | `10-应用ML理论.md` | 实分析在 ML 理论的应用 | 📝 | — | — |

### 实验脚本（experiments/）

| 文件 | 用途 | 状态 |
|------|------|------|
| `experiments/00_irrational_density.py` | 无理数比有理数"多"的数值直觉 | ✅ |
| `experiments/02_epsilon_delta.py` | ε-δ 定义的数值可视化 | ✅ |
| `experiments/06_series_convergence.py` | 无穷级数收敛速度对比 | 📝 |

### 练习（exercises/）

每章 5-10 道习题，含：
- 纸笔证明（标 ✋）
- Python 数值实验（标 🐍）
- Lean 形式化（标 ⚡，对应 Tao companion 的 sorry）

---

## 二、前置要求

| 维度 | 要求 | 你的状态 |
|------|------|---------|
| 数学 | 高中微积分（会求导/积分的基本操作）| 自评 0 → 需先补 Spivak《Calculus》|
| ε-δ 文化 | 没接触过也行，本章从零讲 | — |
| Python | NumPy 基本操作 | ✅ 已会 |
| Lean | 讲透Lean4数学 01 章水平（induction）| 你 ai-os-dd 经验够 |
| **强烈推荐先修** | MIT 18.01 微积分（top-math-courses #1）| 📝 |

> ⚠️ **如果你数学自评 0**：不要直接上实分析。先学：
> 1. **Spivak《Calculus》**（微积分的严格化入门，是实分析的桥）
> 2. **MIT 18.01**（top-math-courses 阶段 0）
> 3. 然后回头学本系列

---

## 三、学习路径（与 top-math-courses + Lean 数学并行）

```
第 1 阶段：实分析入门（3-4 月）
  └─ 本系列 00, 01, 02, 03
     同步：Tao Analysis I Ch 5-10 纸笔
     同步：Tao Lean companion Ch 5-10 填 sorry
     同步：讲透Lean4数学 01-04

第 2 阶段：实分析核心（3-4 月）
  └─ 本系列 04, 05, 06, 07
     同步：Tao Ch 11-16 + Rudin Ch 3-7
     同步：Lean companion Ch 11-16

第 3 阶段：迈向测度 / 泛函（2-3 月）
  └─ 本系列 08, 09, 10
     同步：MIT 18.100B Rudin + 18.125 Folland 测度论
```

---

## 四、核心方法论（"讲透"标准）

每个概念按 6 层讲透：

1. **直觉层**：为什么需要这个概念？它解决什么问题？
2. **数学层**：ε-δ 严格定义 + 关键定理陈述 + 证明主线
3. **Python 层**：跑数值实验，验证直觉（experiments/）
4. **Lean 层**：在 Tao Lean companion 里填 sorry（机械验证）
5. **不足层**：方法的局限 / 失败模式 / 适用边界
6. **应用层**：在 ML / NLP / 数值分析哪里用到

> 📌 **铁律**：每个定理必须有至少一个"反直觉发现"——一个让你"啊，原来如此"的数字。

---

## 五、与其他系列的关系

| 系列 | 关系 |
|------|------|
| [`../讲透Lean4数学/`](../讲透Lean4数学/) | **强配套**：本系列教数学，它教怎么形式化 |
| [`../top-math-courses/UNIFIED_ROADMAP.md`](../top-math-courses/UNIFIED_ROADMAP.md) | 路径规划（本系列对应 #8 MAT 215 + #11 18.100B + #16 18.125）|
| [`../top-math-courses/LEAN_MATH_TRACK.md`](../top-math-courses/LEAN_MATH_TRACK.md) | 学数学同时练 Lean（本系列是 #8 的执行）|
| [`../讲透NLP/math/`](../讲透NLP/math/) | NLP 用到的实分析概念反查 |
| [`../讲透优化理论/`](../讲透优化理论/) | 优化需要实分析（Lipschitz/凸函数）|
| [`../讲透信息论/`](../讲透信息论/) | 信息论的极限定理需要实分析 |

---

## 六、怎么用这个系列

```bash
cd 讲透实分析

# 读章节
code 00-实分析是什么.md
code 01-实数构造.md
code 02-极限与εδ.md

# 跑 Python 配套实验
python3 -u experiments/00_irrational_density.py
python3 -u experiments/02_epsilon_delta.py

# Clone Tao Analysis I Lean companion（首次）
git clone https://github.com/terrytao/analysis1-lean ../analysis1-lean
cd ../analysis1-lean && lake build

# 在 Lean companion 里填对应章节的 sorry
code Chapter9/limits.lean
```

每个 `.md` 结尾有「✍️ 练习」，分三类（✋ 纸笔 / 🐍 Python / ⚡ Lean）。

---

## 七、铁律与教训

1. **不要跳过 ε-δ**：ε-δ 定义是实分析的核心。跳过它 = 没学过实分析。
2. **Python 不能替代证明**：Python 跑 1000 个数值不算证明，Lean 才算。
3. **Lean 不能替代思考**：Lean 是验证工具，思考还是要靠纸笔。
4. **做题是金标准**：每章至少做 10 道习题。不做题 = 没学。
5. **Tao 的书比 Rudin 友好**：先 Tao 后 Rudin。Tao 更适合自学。
6. **遇到抽象卡住**：回到具体例子（如 $f(x) = x^2$ 在 $x=2$ 的极限），用具体例子喂直觉。
7. **反例比正例更深刻**：每个定义背一个反例（如处处连续处处不可微的 Weierstrass 函数）。

---

📌 **下一步**：
- 数学自评 0 → 先读 [`00-实分析是什么.md`](00-实分析是什么.md) 建立直觉，再决定要不要先补 Spivak
- 有基础 → 直接读 [`01-实数构造.md`](01-实数构造.md)
- 配 [`../top-math-courses/LEAN_MATH_TRACK.md`](../top-math-courses/LEAN_MATH_TRACK.md) 看 Tao companion 怎么用
