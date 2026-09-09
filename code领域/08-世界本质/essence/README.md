# Essence · 世界运行的本质

> "The first principle is that you must not fool yourself — and you are the easiest person to fool."  
> — Richard Feynman

> "如果你不能简单地解释一件事，说明你还没有真正理解它。"  
> — 爱因斯坦（据传）

---

## 这个项目是什么

一个**跨学科的、终其一生、持续的"追寻世界运行本质"项目**。

目标不是成为某个细分领域的专家（那是 PhD 干的事），而是不断追问：

- 世界的"原子"是什么？哪些概念是**真正基本的**，哪些是衍生品？
- 不同学科之间，是否有**共同的底层结构**？（答案是：有，而且惊人地多）
- 那些"硬通货"——**金钱、权力、地位**——的本质是什么？它们如何流动？
- **智能**（人类的、AI 的）的本质是什么？学习、注意、记忆、推理的最小单元？
- **复杂系统**（生命、社会、市场、互联网）为什么会涌现出秩序？

---

## 核心方法论（尽一切手段）

详见 [`MANIFESTO.md`](./MANIFESTO.md)。简表：

| 方法 | 一句话 | 何时用 |
|------|--------|--------|
| **第一性原理** | 拆到不能再拆，从公理重建 | 概念模糊、被类比带偏时 |
| **费曼学习法** | 用最朴素的话讲给外行听，讲不通就是没懂 | 检验自己是否真懂 |
| **苏格拉底之问** | 连续追问"为什么"，直到触底或暴露假设 | 质疑权威、暴露盲点 |
| **三层讲解** | 直觉 → 数学 → 代码 | 学任何新概念 |
| **跨学科映射** | 同一个概念（如熵）在不同学科是什么形态 | 发现底层统一性 |
| **思维模型清单** | 维护一张"心智工具箱"，刻意练习 | 决策时 |
| **输出倒逼输入** | 写笔记、讲给人听、做练习 | 把"看过"变"掌握" |
| **5 Whys** | 连问 5 个为什么 | 找根因 |
| **反演思维** (Inversion) | 不问"如何成功"，问"如何必然失败" | 避开致命错误 |

---

## 目录结构（五维设计）

> ⚠️ **2026-07 重要修订**：原结构把哲学放在 04-humanities 下作为平级学科。
> 经过检验（"所有学科最终回归哲学"这一说法），认识到哲学是**所有学科不可消除的边界面**，
> 而非平级学科。**哲学已提升为根层 `00-philosophy/`**。详见 [`00-philosophy/README.md`](./00-philosophy/README.md)。

### 🌳 哲学之根（不可见但无所不在）

**哲学不是平级学科，是所有学科的地基**。每个学科目录里都有 `_philosophy-of-X.md` 作为锚点，
回答"这门学科的基础假设是什么？边界在哪？"。学任何学科，先读它的哲学锚点。

```
00-philosophy/            哲学之根
  ├── README.md            （哲学之根的论证与使用指南）
  ├── ontology.md          本体论：什么存在？
  ├── epistemology.md      认识论：我们如何知道？
  ├── logic/               逻辑学：什么是有效推理？
  ├── metaphysics/         形而上学：最深的"为什么"
  ├── ethics/              伦理学：什么是好/对？
  ├── aesthetics/          美学：什么是美？
  ├── philosophy-of-mind/  心智哲学（特殊：跨哲学+AI+心理学）
  ├── meta-philosophy/     元哲学（哲学本身是什么）
  ├── history-of-philosophy/ 哲学演化史
  └── _philosophy-of-X-template.md  学科哲学模板
```

### 🛠 方法论元层（如何思考）

```
00-meta/                   元层：学习方法本身
  ├── MANIFESTO.md          方法论宪章（见根目录）
  ├── concept-3layer-template.md  三层讲解模板
  ├── mental-models.md      思维模型清单（45+ 个）
  ├── reading-log.md        周/月/季反思模板
  └── first-principles.md / feynman-technique.md / socratic.md（待扩充）
```

### 📚 学科纵切（深挖单一领域）

每个学科目录下都有 `_philosophy-of-X.md` 锚点 + 主笔记。
追问"这门学科的**第一性原理**是什么？哪些是它的**核心抽象**？"

```
01-natural-sciences/      自然学科
  ├── mathematics/         数学（最纯粹的抽象）
  ├── physics/             物理（最接近"世界语法"的学科）
  ├── chemistry/           化学
  ├── biology/             生物（生命的本质）
  └── earth-science/       地球科学

02-formal-sciences/       形式科学
  ├── computer-science/    计算的本质（图灵/邱奇）
  ├── logic/               逻辑的本质
  ├── information-theory/  信息论（香农）
  ├── probability/         概率的本质
  └── statistics/          统计的本质

03-social-sciences/       社会学科
  ├── economics/           经济（价值的本质）
  ├── politics/            政治（权力的本质）
  ├── sociology/           社会
  ├── psychology/          心理（心智的本质）
  └── anthropology/        人类学

04-humanities/            人文学科
  ├── history-of-philosophy/ 哲学史（作为研究对象；哲学本身在 00-philosophy/）
  ├── history/               历史（时间的规律）
  ├── linguistics/           语言（符号与思维）
  ├── arts/                  艺术（美的本质）
  └── literature/            文学（人性的镜像）
```

### 🧠 主题横切（跨学科本质）

项目的**灵魂**。同一个概念在不同学科里反复出现——这些就是"世界的公分母"。

```
05-intelligence/          智能的本质（横跨生物与 AI）
  ├── learning/           学习（RL/监督/自监督的共同骨架）
  ├── attention/          注意力（人脑与 Transformer 共享？）
  ├── emergence/          涌现（多即不同）
  ├── consciousness/      意识（最难的问题）
  ├── memory/             记忆
  └── reasoning/          推理

06-systems/               系统的本质
  ├── systems-thinking/   系统思维
  ├── complexity/         复杂性科学
  ├── networks/           网络科学
  ├── feedback/           反馈回路
  ├── chaos/              混沌
  ├── game-theory/        博弈论
  └── cybernetics/        控制论

07-worldly-power/         现实世界的"硬通货"
  ├── money/              金钱（交换媒介/信息载体/权力凭证）
  ├── power/              权力
  ├── status/             地位
  ├── capital/            资本
  └── influence/          影响力

08-cross-cutting/         跨学科本质主题（最高价值）
  ├── entropy.md          熵：物理↔信息↔经济↔认知
  ├── evolution.md        演化：生物↔经济↔算法↔文化
  ├── networks.md         网络结构
  ├── feedback.md         反馈（控制论↔RL↔经济↔生物）
  ├── symmetry.md         对称性（物理↔数学↔美学）
  ├── information.md      信息
  ├── scale.md            规模
  ├── equilibrium.md      均衡
  └── game-theory.md      博弈
```

### 🛠 方法论元层

```
00-meta/                   元层：学习方法本身
  ├── MANIFESTO.md          方法论宪章（见根目录）
  ├── first-principles.md   第一性原理思维
  ├── feynman-technique.md  费曼学习法
  ├── socratic.md           苏格拉底之问
  ├── mental-models.md      思维模型清单（持续维护）
  ├── concept-3layer.md     三层讲解模板
  └── reading-log.md        阅读与反思日志
```

### 📝 沉淀层（把"看过"变"拥有"）

```
insights/                  洞察笔记（碎片化、高价值、按月归档）
  └── 2026-07/

questions/                 开放问题（驱动探索的引擎）
  ├── big-questions.md      大问题清单（23 个）
  └── philosophical-roots.md 大问题的哲学根源索引

knowledge-graph/           知识图谱（概念之间的连接）
  └── connections.md       跨学科连接表

reading-list/              经典书单（按学科 + 按主题）

briefings/                 每周/每月必读（前沿追踪）

projects/                  深度探索项目（每个 dive 持续数周）
```

---

## 如何使用这个项目

### 日常循环（建议每周至少一次）

```
   ┌──────────────────────────────────┐
   │  1. 提问   ← 从 questions/ 选一个  │
   └──────────┬───────────────────────┘
              ↓
   ┌──────────────────────────────────┐
   │  2. 探索   ← 第一性原理 + 跨学科映射 │
   └──────────┬───────────────────────┘
              ↓
   ┌──────────────────────────────────┐
   │  3. 沉淀   ← 写三层笔记 + 洞察     │
   └──────────┬───────────────────────┘
              ↓
   ┌──────────────────────────────────┐
   │  4. 连接   ← 更新知识图谱          │
   └──────────┬───────────────────────┘
              ↓
   ┌──────────────────────────────────┐
   │  5. 反思   ← 费曼复述 + 苏格拉底之问│
   └──────────────────────────────────┘
```

### 单个主题的探索模板

在任意学科目录下新建 `.md` 文件，套用 [`00-meta/concept-3layer.md`](./00-meta/concept-3layer.md) 模板：

1. **直觉层**：1 句话比喻 + 为什么需要它（先于公式）
2. **数学层**：关键公式与推导主线，标注假设与边界
3. **代码层**：可运行的最小示例（Python/伪代码）
4. **跨学科映射**：这个概念在哪些其他学科里出现？
5. **局限与反例**：它在哪里失效？
6. **开放问题**：还有什么没想通？

### 与其他项目的关系

- **`/mnt/c/workspace/ai-atlas/`**：AI 学习知识库。`05-intelligence/` 下的笔记遇到 AI 技术细节时，链接过去。
- **`/mnt/c/workspace/math/`**：数学项目（含 Lean4/Mathlib4）。`01-natural-sciences/mathematics/` 遇到形式化证明时，链接过去。
- **`/mnt/c/workspace/Foundations-of-LLMs/`**：LLM 教材。`05-intelligence/learning/` 和 `attention/` 链接过去。
- **`/mnt/c/workspace/fastisslow/`**：段永平投资哲学。`07-worldly-power/money/` 和 `03-social-sciences/economics/` 链接过去。

---

## 给自己的一段话

这个项目不会让你"学完"任何东西——它没有终点。

它的真正价值在于：**你会越来越快地看清新事物的本质**，因为世界上绝大多数"新概念"只是少数几个"老本质"的重新组合。

当你能下意识地把一个新现象拆解成「熵增 / 反馈回路 / 网络效应 / 博弈均衡 / 涌现」时，你就拥有了一个**可迁移的世界模型**。

这是复利最高的事。

---

## 立即开始

1. 读 [`MANIFESTO.md`](./MANIFESTO.md) 内化方法论
2. 读 [`00-philosophy/README.md`](./00-philosophy/README.md) 理解为什么哲学是根
3. 浏览 [`questions/big-questions.md`](./questions/big-questions.md) 选一个最让你兴奋的问题
4. 用 [`questions/philosophical-roots.md`](./questions/philosophical-roots.md) 找到这个问题的哲学根源
5. 看 [`08-cross-cutting/entropy.md`](./08-cross-cutting/entropy.md) 体会"跨学科本质"是什么感觉
6. 在对应学科目录下新建你的第一篇笔记——**记得先读该学科的 `_philosophy-of-X.md`**

**记住：不要追求完美，追求真实理解。写错了就改，想不通就记下来。**
