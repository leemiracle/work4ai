# 第 139 集｜苏煜：Agent 技术史与 OpenClaw Moment（精读笔记）

> **本文件性质**：**多源交叉精读笔记**（产业事实+工作年表+多源链接）。
> **互补文件**：👉 [`第139集-苏煜-Agent技术演化简史.详尽整理.md`](./第139集-苏煜-Agent技术演化简史.详尽整理.md) —— pub.atoma.one 的 14 章**详尽结构化整理**（概念框架+哲学论证+逐章原文引用），与本笔记**互补不重复**：本笔记偏"产业事实+年表"，详尽整理偏"概念框架+论证"。
>
> **嘉宾**：苏煜（俄亥俄州立大学 CS 副教授，OSU NLP group 共同负责人，**2025 斯隆研究奖**，NeoCognition 创始人 $40M seed）
> **时长**：138 分钟｜**发布**：2026-05-01
> **来源等级**：★★★ transcript + 多源精读（Scripod+TextMatrix+Wave 完整口述）

---

## 嘉宾定位

苏煜是**少数见证过 Agent 完整演化史的学者**，研究方向 Language Agent。最早从 Semantic Parsing 转型做 Language Agent 的学者之一。这集是**对接 `讲透Agent` 的天然骨架**——他把 Agent 60 年技术史梳理成一条清晰主线。

---

## 核心论点速览（对接 work4ai）

1. **Agent 四阶段演进史**：Logical Agent(1960-90s) → Neural Agent(2000+) → Semantic Parsing → Language Agent。→ `讲透Agent` 开篇骨架
2. **OpenClaw Moment ≈ ChatGPT Moment**——普通用户开始意识到 Agent 能进入数字环境替我操作真实软件。→ `讲透Agent`
3. **最终目标是 universal digital agent**——边界消弭与 coding 有关（会写代码的 Agent 才能给自己造新工具）。→ `讲透Agent`
4. **Language Agent 才三年**，过去三年速度远超过去几十年。→ `讲透Agent`
5. **Agent 框架已成独立变量**——重新定义任务完成率，不只是模型能力的竞争。→ `讲透Agent`
6. **Computer Use 把 GUI/浏览器/桌面纳入接口**——数字执行栈开始拼到一起。→ `讲透Agent`

---

## 主题精读：Agent 60 年技术史（本集最大价值）

> 这是 `讲透Agent` 开篇章节的现成骨架。来源：TextMatrix 精读 + Wave 完整口述 transcript。

### 阶段 1：Logical Agent（1960s-1990s）
把下一步写进规则——基于逻辑的早期 AI（SHRDLU、专家系统）。

### 阶段 2：Neural Agent（2000+）
从数据里学下一步——神经网络兴起，但 Agent 概念未成型。

### 阶段 3：Semantic Parsing（另一条线）
把语言翻成可执行表示（数据库查询、逻辑形式、程序）。**这条线替 Language Agent 探过路**：语言不只是表达工具，也可以成为行动的前端。

### 阶段 4：Language Agent（2022 后爆发）
语言直接参与计划、工具调用、记忆、协作。问题从"模型会不会回答"换成"系统能不能在开放环境里连续做事"。

### Language Agent 关键工作年表（来源：Wave transcript，苏煜亲述）

| 时间 | 代表工作 | 对 Agent 的意义 |
|------|---------|---------------|
| 2021 | WebGPT | 用浏览器环境训练引用问答 |
| 2022 | **ReAct** | 推理+行动交替组织成可检查轨迹 |
| 2023.02 | **Toolformer** | 第一个用 LM 做 Tool Use（Meta，Luke Zettlemoyer）|
| 2023.03 | **AutoGPT** | 开源 Agent 外壳，GitHub star 史上最快冲到 10 万+ |
| 2023 中 | **GPT-4V** | 第一个能打的多模态模型，Agent 全面转向多模态 |
| 2023.07 | WebArena（CMU）| Web Agent 的可复现 RL 环境 |
| 2023 下 | **SWE-bench** | 引领 Coding Agent 发展 |
| 2024 | **OSWorld**（宇涛组）| Desktop Agent 代表作 |
| 2024 下 | **UGround** | "Agent 应该像人一样用电脑"——visual perception + pixel-level action |
| 2024.10 | **Claude Computer Use** | 采用 UGround 式 embodiment |
| 2025 | **OpenAI Operator**、ChatGPT Agents | Agent 平台化 |
| 2025 下 | **Claude Code** 大爆发 | Opus 4.5 后硅谷研究员基本不自己写代码 |
| 2026 | **OpenClaw**、NeoCognition | 从"能否演示"转向"能否持续学习/专业化/可靠执行" |

> **对接 `讲透Agent`**：这张表就是讲透Agent 的"技术演进史"章节骨架，直接可用。

---

## 主题：OpenClaw Moment——界面边界开始松动

**ChatGPT Moment 的本质**：不是第一个聊天机器人出现，而是普通人意识到模型语言能力跨过可用门槛，可参与写作/总结/翻译/编程/检索。

**OpenClaw Moment 如果成立**：不是某个项目单独完成通用智能，而是**普通用户开始意识到 Agent 可以进入我的数字环境，替我操作真实软件，而不是只给建议**。

**OpenClaw 把分散的几层接口捏到一起**：
- 聊天入口（自然语言表达目标）
- 本地/云端执行环境（Agent 有自己的运行上下文）
- 工具与插件（邮件/日历/文件/浏览器/终端）
- 记忆与后台任务（不必每次从零开始）
- 编程能力（现成工具不够时写胶水代码补接口）

**"边界的消弭和 coding 有关"**：只会点按钮的 Agent，能力受限于现成界面；**会写代码的 Agent，才开始有机会给自己造新工具**。数字世界里很多工作不是缺智能，而是缺把不同系统粘起来的胶水。

---

## 主题：各大厂的 Agent bets（来源：TextMatrix）

| 公司 | 代表动作 | 押注点 |
|------|---------|--------|
| **OpenAI** | Operator、Responses API、Agents SDK、Computer Use | 搜索/文件/浏览器/追踪/多 Agent 编排平台化 |
| **Anthropic** | Claude Computer Use、Claude Code | coding+电脑操作+高信任工作流 |
| **Google** | ADK、Jules、Workspace/Cloud 连接器 | 云+Workspace+企业连接器承接复杂 Agent |
| **Microsoft** | Agent Framework、Copilot、M365 | AutoGen/Semantic Kernel 并入企业级状态/遥测 |
| **OpenClaw** | 聊天入口+邮箱/日历/航旅执行 | 个人数字环境变成 Agent 可持续操作的工作台 |
| **NeoCognition** | Specialized intelligence、world model of work | Agent 在使用中从通用执行者变领域专家 |

**关键判断**：OpenClaw 把入口和界面问题推到台前（用户看到 Agent 能进入数字世界）；NeoCognition 把问题推向长期学习和专业化（Agent 怎么越用越稳）。

---

## 金句

- "**At the end of the day，大家想要的就是 universal digital agent。**"
- "**边界的消弭和 coding 有关。**"
- "**OpenClaw Moment 和 ChatGPT Moment 有非常多相似的地方。**"
- "**我们这一代人经历了 Agent 的完整周期，我喜欢搭建 conceptual framework。**"

---

## work4ai 对接

| 本集主题 | 对接章节 | 用法 |
|---------|---------|------|
| Agent 四阶段演进史 | `讲透Agent` **开篇骨架** | 直接作技术史章节主线 |
| Language Agent 关键工作年表 | `讲透Agent` | 时间线表格直接可用 |
| OpenClaw Moment | `讲透Agent` | 范式判断 |
| 各大厂 Agent bets | `讲透Agent` 产业 | 章节结尾产业格局 |
| "边界消弭与 coding 有关" | `讲透Agent` | 解释为什么 coding 是 Agent 关键 |

> 这集是 **`讲透Agent` 系列最重要的单集参考**——它提供了从 1960s 到 2026 的完整骨架，配套有苏煜亲述的工作年表。

---

## 多源文字版

- 公众号"语言即世界"（待补/搜索苏煜）
- Scripod transcript：https://scripod.com/episode/ixgmg0kj879ts6fjsb450dzl/transcript
- TextMatrix 精读（深度）：https://txtmix.com/posts/video/agent-technology-history-su-yu/
- Wave podcast notes（含完整口述 transcript）：https://pod.wave.co/podcast/jun-14c5d25c-c21b-42a7-a307-be6b58bcd235/139-agentagentopenclaw-moment
- 小宇宙：https://www.xiaoyuzhoufm.com/episode/69f3857a5c60a99573fea0c2

---

**整理日期**：2026-08-03 ｜ **来源标注**：核心论点来自 TextMatrix 精读（2026-05-01）+ Wave 完整口述 transcript + Scripod
