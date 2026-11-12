# 03 — 路由与触发：description 即检索键

> 「讲透 Skills」第四篇。Agent 怎么决定用哪个 skill？答案：**拿 description 当检索键在任务意图上做匹配**。这一机制决定了 skill 写作的核心技巧全在一条 ≤1024（实现上 ≤250）字符的 description 里。

---

## 1. 触发机制解剖

用户输入到达时，agent（以 Claude Code 为例）看到的是：

```
<system>
...可用技能清单（L1：每个 skill 的 name + description）...
</system>
user: 我老板发来一个 Q4 sales final v2.xlsx，要我在 C 列收入 D 列成本基础上加一列利润率...
```

agent 在**生成过程中**决定：这个任务是否需要咨询某个 skill → 需要则读其 SKILL.md（L2 装载）→ 按正文指令执行。

关键事实（官方 skill-creator SKILL.md:396-400 一手原文）：

> "Claude only consults skills for tasks **it can't easily handle on its own** — simple, one-step queries like 'read this PDF' may not trigger a skill even if the description matches perfectly... **Complex, multi-step, or specialized queries reliably trigger skills** when the description matches."

三个推论：

1. **触发 = 任务复杂度 × description 匹配度**的联合函数，不是纯文本匹配。
2. eval 你的 skill 触发率时，query 必须是"真实用户会说的话"（带文件路径/背景/口语），不能用抽象短句（"处理 PDF"）——短句根本走不到触发那步。
3. 模型换代会改变触发基线：模型越强，"它能自己搞定"的集合越大，同一 skill 的触发率会漂移（这是 [06 模型适配](06-模型适配-同一个skill跨九种模型.md) 的一环）。

## 2. 欠触发（undertrigger）与官方 pushy 写法

skill-creator SKILL.md:67 一手原文：

> "currently Claude has a tendency to 'undertrigger' skills... To combat this, please make the skill descriptions **a little bit 'pushy'**. So for instance, instead of 'How to build a simple fast dashboard...', you might write 'How to build a simple fast dashboard... **Make sure to use this skill whenever the user mentions dashboards, data visualization, internal metrics, or wants to display any kind of company data, even if they don't explicitly ask for a dashboard.**'"

pushy 三要素：

```
① 动词式场景枚举：whenever the user mentions X, Y, Z
② 显式兜底：even if they don't explicitly ask for a 'X'
③ 同义词覆盖：把用户可能的每种说法都列进去（dashboards/data visualization/metrics/display company data）
```

本质：description 是写给**路由器（模型自己）看的检索键**，不是写给管理员看的功能说明。"功能介绍"视角（"Helps with PDFs"）在检索机制下就是烂键。

## 3. description 的双面写作契约

综合规范（01 章）与 Claude Code 深读（articles/14:124-128"description 写作契约：触发条件枚举＋正反例"）：

```markdown
description: <做什么：动词开头，一句话能力陈述>。
  <何时用：Use when 用户提到 X/Y/Z，包括没明说 X 但显然需要的场合>。
  <反例边界（可选但强烈推荐）：Not for A/B——A/B 该走别的路>。
```

正反例都要写，因为路由最大的错误源是 **near-miss**（看着像但不该触发）。

## 4. 官方 trigger eval 优化协议（skill-creator 详解，一手）

skill-creator 的 Description Optimization 是目前最完整的官方自动优化流程（SKILL.md:333-404），拆解如下：

### 第 1 步 · 造 20 条 trigger eval query

```
8-10 条 should_trigger（正例）：
  - 同一意图的多种说法（正式/口语/缩写/错别字混合）
  - 用户没点名 skill 但显然需要的场景
  - 与其他 skill 竞争但本 skill 应赢的场景
8-10 条 should_not_trigger（负例）——最有价值的是 near-miss：
  - 共享关键词但实际需要别的工具
  - 朴素关键词匹配会误触发但语义上不该触发的
```

官方对 query 质量的要求（原文意译）：真实到像用户打的字——文件路径、公司名、上下文 backstory、大小写混乱、缩写。反例：`"Format this data"` 是坏 query（太抽象，根本不构成触发测试）。

### 第 2 步 · 人工审 eval 集

HTML 模板（assets/eval_review.html）让用户增删改、翻转 should_trigger 标注。**坏 eval 集优化出坏 description**——这步不能省。

### 第 3 步 · 自动优化循环（scripts/run_loop.py）

```
输入: eval_set.json + skill 路径 + 当前会话同款 model
流程:
  1. 60/40 分 train/held-out test
  2. 评估当前 description（每条 query 跑 3 次取触发率——采样噪声控制）
  3. 把失败样本喂给模型 → 提议新 description
  4. 新 description 在 train + test 上重评
  5. 最多 5 轮迭代
输出: best_description ——按 test 分数（防过拟合）而非 train 分数选择
```

### 协议里的四个评估学精髓

| 设计 | 对应评估学原则 | 本仓对应 |
|---|---|---|
| 60/40 train/test 切分 | holdout 防过拟合 | prompt 手册 11 章六步闭环 ⑤验收 |
| 每条 query 跑 3 次 | 采样方差控制（temperature>0 时必需） | prompt 手册 04 章稳健性 A |
| near-miss 负例 | 对比例的区分力 > 正例 | 实践阶梯 dummy 下界探针 |
| 用会话同款 model 测 | 评估环境=部署环境 | 手册 11 章"首版仍值得手写好"同精神 |

> 与 DSPy GEPA 的关系：GEPA 优化的是整条 prompt（黄金集上进化候选），run_loop 优化的是 description（trigger eval 上进化）——同一"反思式进化"范式的两个实例。详见 [07 自动优化](07-自动优化-从skill-creator到MCE.md) 的三层工具栈对照。

## 5. 路由失败的四象限诊断

| | 触发了 | 没触发 |
|---|---|---|
| **该触发** | ✅ | **欠触发**：description 缺关键词/不够 pushy；或任务太简单模型自己扛了 |
| **不该触发** | **误触发**：near-miss 区分度不足，补反例 | ✅ |

诊断路径：先问"query 复杂度够吗"（简单 query 永不触发是正常的）→ 再看 description 是否覆盖该说法 → 最后查装载上限（02 章 1% 预算可能把你的 skill 挤出清单）。

## ✍️ 练习

1. 给下面这条 description 诊断触发问题并改写（pushy + 反例）："Helps with LaTeX math typesetting."
2. 为你自己的 skill 造 4 条 near-miss 负例（共享关键词但不该触发的 query）。
3. （实验）跑本站 [E1](experiments/01_trigger_eval.py)：用本地模型实测 10 条 query 的触发决策，观察"任务复杂度 × description 匹配"联合效应。

---

**下一篇**：[04 — 生态全景：七赛道与工具链](04-生态全景-七赛道与工具链.md)
