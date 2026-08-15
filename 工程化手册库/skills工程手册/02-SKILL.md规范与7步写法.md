# 02 · SKILL.md 规范与 7 步写法

> **本文是什么**：opencode SKILL.md 的标准结构 + 写新 skill 的 7 步法。
> **目的**：把"凭感觉写 skill"变成"按规范写可维护 skill"。

---

## 🎯 SKILL.md 7 要素（参照 prompt 的 ROIF-CSE）

```
1. 元数据（name + description）   ← opencode 用来匹配触发
2. Role（角色）
3. Triggers（触发条件）            ← 何种用户输入激活
4. Workflow（工作流）              ← 具体步骤
5. Resources（资源链接）
6. Cross-skill（跨 skill 协作）
7. Quality gates（质量门）
```

---

## 📐 标准 SKILL.md 模板

```markdown
---
name: my-skill-name
description: 简短描述（含中英文 triggers）。当用户说 X / 问 Y / 用 /cmd 时激活。
---

<!-- updated: 2026-08-13 -->
<!-- version: 1.0 -->

# Skill 标题

## Role

你是 [具体角色]，帮助用户 [核心目标]。

## Triggers

激活条件（任一）：
- 用户说 "X" / "Y" / "Z"
- 用户问 "[关键词]"
- 用户用 `/cmd`
- 用户当前任务涉及 [场景]

## Workflow

### Step 1: 理解需求
[具体动作]

### Step 2: 收集信息
[具体动作]

### Step 3: 执行
[具体动作]

### Step 4: 验证
[具体动作]

## Resources

| 资源 | URL | 用途 |
|------|-----|------|
| 官方文档 | https://... | 参考 |
| 教程 | https://... | 入门 |

## Cross-skill 协作

```
用户问 X → my-skill（核心讲解）
  ├─ 关联 A → skill-A（深挖）
  ├─ 关联 B → skill-B（实战）
  └─ 关联 C → skill-C（评估）
```

## Quality gates

发布前必须通过：
- [ ] description 含至少 5 个 triggers（中英混合）
- [ ] Workflow 至少 3 步
- [ ] 至少 3 个资源链接（已核实）
- [ ] 有跨 skill 协作段
- [ ] 跑过 1 次真实场景测试

## Anti-patterns（避免）

- ❌ [常见错误 1]
- ❌ [常见错误 2]
```

---

## 📋 写新 skill 的 7 步法

### Step 1 · 确定场景（**最重要**）
问自己：
- 用户**什么场景**会需要这个 skill？
- 这个场景**多久出现一次**？（每周 vs 每月 vs 一年一次）
- 已有 skill 能不能解决？（如果能 → 不要写新的）

**判断**：每周用 < 1 次 / 已有 skill 能 80% 解决 = **不要写新 skill**。

### Step 2 · 写 description（决定触发）
description 是 opencode 匹配的关键。必须含：
- **中文 + 英文 triggers**（用户可能用任一语言）
- **核心动词**（"读 / 写 / 优化 / 评估"）
- **场景关键词**

**❌ 坏例**（空泛）：
```
description: 帮助用户做 AI 任务
```

**✅ 好例**（具体）：
```
description: Use when user reads arXiv paper, asks to 精读/读论文/deep-read, 
or invokes /paper. 4-layer breakdown: motivation → method → experiments → limits.
```

### Step 3 · 写 Role（角色）
具体 + 经验 + 专长。

### Step 4 · 写 Workflow（工作流）
**3-7 步最佳**。每步：
- 动词开头（"读" / "提取" / "验证"）
- 可验证（"输出 X" 而不是"思考"）

### Step 5 · 收集 Resources
- 至少 3 个权威链接
- **链接必须核实**（用 webfetch）
- 标注用途

### Step 6 · 设计 Cross-skill 协作
问自己：用户问 X 时，**还会需要哪 2-3 个 skill**？
- 在 SKILL.md 里画协作图（如上模板）

### Step 7 · 质量门（自查）
对照 [`03-skill评价6维度`](03-skill评价6维度.md)：
- [ ] 准确性 ⭐⭐⭐+
- [ ] 触发精度 ⭐⭐⭐+
- [ ] 资源质量 ⭐⭐⭐+
- [ ] 协作性 ⭐⭐⭐+
- [ ] 维护性 ⭐⭐⭐+
- [ ] 安全性 ⭐⭐⭐⭐+

**任一低于 ⭐⭐⭐ → 不发布**。

---

## 🛠️ 实战：写一个 minimal skill（5 分钟）

最小可用 SKILL.md：

```markdown
---
name: hello-skill
description: 测试 skill。当用户说 "hello-skill" 或 "/hello" 时激活。
---

# Hello Skill

## Role
你是测试助手。

## Triggers
- 用户说 "hello-skill"
- 用户用 `/hello`

## Workflow
### Step 1: 打招呼
回应用户："Hello from skill!"

## Quality gates
- [x] 有 description
- [x] 有 trigger
- [x] 至少 1 步 workflow
```

放到 `~/.config/opencode/skills/hello-skill/SKILL.md`，重启 opencode，说"hello-skill"即可触发。

---

## 📊 SKILL.md 大小建议

| 用途 | 行数 | 例子 |
|---|---|---|
| **轻量触发器**（路由到其他 skill）| 30-50 | concept-3layer / impl-from-scratch |
| **标准 skill**（单任务工作流）| 80-150 | debug-helper / git-workflow |
| **重量级 skill**（多场景 + 多资源）| 150-250 | paper-mastery / ml-theory |
| **元 skill**（管理其他 skill）| 50-100 | customize-opencode |

**铁律**：
- **< 30 行**：太薄，可能不值得做成 skill（用 prompt 即可）
- **> 250 行**：太厚，考虑拆成多个 skill

---

## 🚨 常见反模式

### 1. description 太抽象
❌ "helps with coding"
✅ "Use when debugging Python errors, fixing stack traces, or optimizing performance"

### 2. Workflow 太抽象
❌ "Step 1: Think. Step 2: Do."
✅ "Step 1: Reproduce the bug. Step 2: Isolate minimal repro. Step 3: Hypothesize root cause."

### 3. 资源链接过时
❌ 链接到 2020 的文章
✅ 链接到最新官方文档（每 3 月复核）

### 4. 没跨 skill 协作
❌ 单干
✅ 明确"用户问 X 时，调用 skill-Y 做深挖"

### 5. 一次写太大
❌ 一个 skill 想覆盖所有 ML 任务
✅ 一个 skill 一个任务（paper 精读 ≠ 论文复现 ≠ 论文写作）

---

## 📌 本周必做

1. [ ] 用 7 步法写 1 个新 skill（参照 [`05-实战`](05-实战-写expert-track新skill.md)）
2. [ ] 给现有最常用的 skill 补 "跨 Skill 协作" 段
3. [ ] 给所有 skill 加 `<!-- updated: 2026-08-13 -->`

---

**版本**：v1.0（2026-08-13）
**核心隐喻**：**Skill 不是文档，是产品。7 要素 + 7 步法 = 可维护的 skill。**
