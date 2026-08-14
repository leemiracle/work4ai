# 04 · 跨 Skill 协作设计

> **核心论点**：单个 skill 解决单点问题。**多个 skill 联动 = 解决复杂问题**。
> **本文是什么**：怎么设计 skill 间的协作关系。

---

## 🎯 为什么协作重要

opencode 的核心优势是 **N 个 skill 自动联动**——用户说一句话，多个 skill 协同工作。

**坏例子**（孤岛 skill）：
```
用户："读这篇 interp 论文"
→ 只激活 paper-mastery，输出解读
→ 但用户可能还想：复现 / 写 blog / 加入黄金集
```

**好例子**（协作 skill）：
```
用户："读这篇 interp 论文"
→ paper-mastery（核心解读）
  ├─ impl-from-scratch（如果用户想复现）
  ├─ prompt-eval-demo（如果想做黄金集）
  └─ paper-to-blog（如果想写 blog）
```

---

## 📐 3 种协作模式

### 模式 1 · 串行（Sequential）
A 的输出 → B 的输入

```
用户问"复现论文"
→ paper-mastery（解读论文，输出方法 + 关键公式）
  → impl-from-scratch（基于方法，从零实现）
    → ml-experiment（设计消融实验）
```

### 模式 2 · 并行（Parallel）
A 和 B 同时激活，分别处理不同维度

```
用户问"评估这个 prompt"
→ prompt-engineering（评价 prompt 结构）
  ├─ ml-experiment（设计 A/B 测试）
  └─ code-review-workflow（如果 prompt 含代码）
```

### 模式 3 · 路由（Router）
中央 skill 判断该走哪个分支

```
用户问"AI 学习"
→ progress-tracker（路由）
  ├─ 如果是新手 → learning-methodology
  ├─ 如果是读论文 → paper-mastery
  └─ 如果是学概念 → concept-3layer
```

---

## 🎨 怎么画协作图

在 SKILL.md 里加：

```markdown
## Cross-skill 协作

\`\`\`
用户问 X → 本 skill（核心）
  ├─ 关联 A → skill-A（深挖 / Y 场景）
  ├─ 关联 B → skill-B（实战）
  └─ 关联 C → skill-C（评估）
\`\`\`

**何时调用 A**：[具体条件]
**何时调用 B**：[具体条件]
```

---

## 📊 推荐的协作组（基于用户顶级专家目标）

### 协作组 1 · 论文学习流水线
```
用户："读论文 arXiv:2406.11717"
→ paper-mastery（精读：动机 → 方法 → 实验 → 局限）
  ├─ 想复现 → impl-from-scratch + ml-experiment
  ├─ 想写笔记 → 故事化学习法/05-prompt 模板（论文变侦探小说）
  └─ 想评估 → prompt-eval-demo（建黄金集）
```

### 协作组 2 · 概念学习
```
用户："什么是 attention"
→ concept-3layer（直觉 → 公式 → 代码）
  ├─ 想深挖 → ml-theory（数学推导）
  ├─ 想看实现 → 讲透Transformer（work4ai 内）
  └─ 想跑实验 → impl-from-scratch
```

### 协作组 3 · 数学补强
```
用户："学线性代数"
→ math-learning（路径规划）
  ├─ 遇到概念 → concept-3layer
  ├─ 遇到证明 → top-math-courses（资源）
  └─ 想做闪卡 → learning-methodology
```

### 协作组 4 · interp 实战
```
用户："跑 interp 实验"
→ expert-track（新 skill，见 05）
  ├─ 装 TransformerLens → prototype
  ├─ 跑 demo → repo-scan（参考 ARENA）
  └─ 写 blog → paper-to-blog（新 skill）
```

### 协作组 5 · 前沿追踪
```
用户："今天有什么新论文"
→ frontier-briefing（扫 arXiv）
  ├─ 感兴趣 → paper-mastery（精读）
  ├─ 想分享 → trending-projects
  └─ 想存档 → deep-research
```

---

## 🛠️ 怎么给现有 skill 加协作段

### Step 1 · 找到该 skill 的"上下游"
- 上游：什么 skill 会触发它？
- 下游：它处理后该走什么 skill？

### Step 2 · 在 SKILL.md 末尾加段
```markdown
## Cross-skill 协作

\`\`\`
用户问 X → 本 skill
  ├─ 上游 ← skill-上游
  ├─ 下游 → skill-下游-A
  └─ 下游 → skill-下游-B
\`\`\`
```

### Step 3 · 测试联动
跑一次真实场景，看是否按预期协作。

---

## 🚨 协作反模式

### 1. 过度协作（指向 10+ skill）
用户晕。**3-5 个下游最佳**。

### 2. 循环协作
A → B → A → 无限。**避免**。

### 3. 协作但不调
写了协作段但实际不调。**测试**。

### 4. 单一中心
所有 skill 都依赖一个中心 skill。**中心挂了全挂**。

---

## 📌 本周必做

1. [ ] 给 8 个 P0/P1 skill（见 [`01-审计报告`](01-现有skills审计报告.md)）加协作段
2. [ ] 设计你最常用的 1 个协作组（如"论文学习流水线"）
3. [ ] 测试联动是否按预期工作

---

**版本**：v1.0（2026-08-13）
**核心隐喻**：**单 skill 像单兵。协作 skill 像特种部队。设计协作 = 设计战斗力。**
