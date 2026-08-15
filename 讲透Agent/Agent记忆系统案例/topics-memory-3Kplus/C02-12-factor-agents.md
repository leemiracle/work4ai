# C-02 `humanlayer/12-factor-agents`（25.3K★）—— 方法论精读：memory/state/context 相关因子与"记忆即因子"原则

> 层级：C 层外围。不克隆，信息源 = GitHub API（README、`content/` 全部 factor 原文、模板源码）+ deepwiki。
> 定位：Dex Horthy（HumanLayer）的"LLM 应用工程原则"指南，仿 12factor.net。**本体是文档仓库，不是记忆系统**——价值在于它把记忆/状态/上下文处理提炼成了可移植的因子。
> 仓库结构（目录树实测）：正文在 `content/factor-01..12 + appendix-13`；示例代码在 `packages/create-12-factor-agent/template/`（BAML + TS 脚手架）与 `workshops/2025-05*`（12 步渐进式 walkthrough，`09-state.ts` 为状态管理专章）。内容 CC BY-SA 4.0 / 代码 Apache-2.0。

## 0. 12 因子速查表（★ = 与 memory/state/context 直接相关）

| # | 因子 | 与记忆的关系 |
|---|---|---|
| 1 | Natural Language to Tool Calls | 间接：事件流的起点 |
| 2 | Own Your Prompts | 间接：prompt 版本化 = 可迭代的学习回路 |
| 3 | **Own Your Context Window** | ★★ 核心：记忆是上下文第四类输入源 |
| 4 | Tools are Structured Outputs | 间接：事件的结构化形态 |
| 5 | **Unify Execution State** | ★★ 核心：thread 即单一事实源 |
| 6 | **Launch/Pause/Resume** | ★ 持久化粒度须到事件级 |
| 7 | Contact Humans with Tools | ★ 人类响应当事件入 thread |
| 8 | Own Your Control Flow | ★ 压缩/清除窗口内容的决定权在应用 |
| 9 | **Compact Errors** | ★ 错误的记忆与遗忘策略 |
| 10 | Small, Focused Agents | 间接：防错误 spin-out 的第一手段 |
| 11 | Trigger From Anywhere | 间接：恢复触发源多元化 |
| 12 | **Stateless Reducer** | ★★ Agent = foldl(events)，记忆外置 |
| 13 | Pre-Fetch Context（附录） | ★ 确定性预取优于 agentic 检索 |

## 1. 与 memory/state/context 直接相关的因子（按原文精读）

### 1.1 Factor 3 — Own your context window（`content/factor-03-own-your-context-window.md`）
本仓被引用最多的"context engineering"源头（README:26 直接把该文等价于 Context Engineering 入口）。核心论断：
- LLM 是无状态函数，"Everything is context engineering"（f03:12）。上下文五要素清单（f03:14-20）：① prompt/指令 ② RAG 检索的外部数据 ③ **历史状态、工具调用与结果** ④ **来自相关但独立会话/历史的过去消息与事件（Memory）** ⑤ 结构化输出指令。→ **记忆在因子体系中被显式定义为上下文的第四类输入源**，与 RAG 并列。
- 反模式：标准 role-based 消息格式"能用但非最优"；主张自建上下文格式——示例把全部历史打包进单个 user message 的 XML 风格标签（`<slack_message>`、`<list_git_tags_result>`，f03:74-112），配套 Python `Thread/Event → thread_to_prompt()` 代码（f03:120-140）。
- 五项收益（f03:227-234）：信息密度、错误处理（**"已解决的错误可从上下文窗口隐藏/移除"**——这是显式的遗忘指令）、安全过滤、格式灵活性、token 效率。
- 关键句："I don't know what's the best approach, but I know you want the flexibility to be able to try EVERYTHING"（f03:257）——记忆注入方式必须应用侧可控，不可被框架锁死。

### 1.2 Factor 5 — Unify execution state and business state（`content/factor-05-unify-execution-state.md`）
对"记忆系统该存什么"最直接的一个因子：
- 执行状态（当前步/下一步/等待/重试计数）与业务状态（OpenAI 消息列表、工具调用与结果）**能合就合**："you can engineer your application so that you can infer all execution state from the context window"（f05:26）。
- 论据：执行状态本质上只是"发生过什么"的元数据。不可入窗信息（session id、密码上下文）应最小化（f05:28）。
- 统一后的七项收益（f05:30-38）值得整段抄录：单一事实源、**thread 可平凡序列化/反序列化**、全历史单点可调试、加新状态=加新事件类型、**任意点恢复（加载 thread 即可 resume）**、**任意点分叉（fork，拷贝 thread 子集到新 state ID）**、thread 可平凡渲染为人读 markdown 或 Web UI。
- → 这实际上给 A 层记忆系统划了底线：**事件溯源（event-sourced thread）本身就是最小可用的长期记忆**，mem0 式"抽取后的记忆条目"应视为 thread 的派生物而非替代品。

### 1.3 Factor 6 — Launch/Pause/Resume with simple APIs（`content/factor-06-launch-pause-resume.md`）
- Agent 就是程序：launch/query/resume/stop 应有简单 API；长操作可 pause；**外部触发（webhook）应能在不深度集成 orchestrator 的情况下从断点恢复**（f06:17-21）。
- 关键细节（f06:27）：很多 orchestrator 支持暂停恢复，但**不支持在"选定工具"与"执行工具"之间暂停**——记忆系统的持久化粒度必须到事件级（工具选择本身也是一个可持久化事件），才能支持人审批/换模型/迁移后续跑。
- 与 F5 显式互链：pause/resume 的可行性完全建立在"状态皆在 thread"之上。

### 1.4 Factor 9 — Compact Errors into Context Window（`content/factor-09-compact-errors.md`）
- 错误即记忆素材：`try/except → thread["events"].append({"type":"error","data":format_error(e)})`，LLM 读错误自愈（f09:11-29）。
- 配套连续错误计数器（≈3 次阈值）+ 升级人类（f09:33-62）。
- 但原文同时给出**反面警告**：过度自我重试会 spin out 重复同一错误（f09:79）；出路是 F8（自控控制流）+ F3——"你可以完全重构错误的表示方式、**从上下文窗口移除先前事件**，或任何确定性的手段拉回正轨"（f09:81）。→ 错误记忆需要 TTL/清除策略，不能只增不减。

### 1.5 Factor 12 — Make your agent a stateless reducer（`content/factor-12-stateless-reducer.md`）
- 全文最短（12 行，作者自嘲 "mostly just for fun"），但图示（`img/1c5-agent-foldl.png`）点题：**Agent = foldl(events)**——`新状态 = reduce(旧状态, 新事件)`。状态不在进程里、在事件序列里；进程无状态，记忆外置。这是"记忆即因子"的最纯表达。

### 1.6 Appendix Factor 13 — Pre-fetch all the context you might need（`content/appendix-13-pre-fetch.md`，"Honorable Mention"）
- 论断：若大概率会调用工具 X，**别浪费 token 往返让模型去 fetch，直接在构建上下文时确定性预取**（f13:147 金句："just call them DETERMINISTICALLY and let the model do the hard part"）。
- 给出三种实现层次：预取进模板变量 → 预取结果直接塞 thread events（`list_git_tags` + `list_git_tags_result` 成对追加，f13:114-143）→ 从 prompt 模板中删除该工具参数。
- → 对记忆检索的直接启示：**高置信度记忆召回应做在 context 构建期（确定性 pre-fetch），而非交给模型 agentic 检索**；RAG 式召回只该兜底长尾。

### 1.7 澄清：本仓没有 "data flywheel" 因子
12 因子 + 1 附录中无 "data flywheel / summarize-compact state" 专条（检索全文确认）。最接近的替代物：F2（Own your prompts——把 prompt 当代码版本化迭代）承担"从数据中学习"的成长回路，但未上升为记忆机制；F3/F9 中的"移除已解决错误、重构表示"是事实上的 compaction/summarize 操作，但以原则而非算法形态存在。任务假设中的 "compact/summarize state" 在本仓对应 F5+F12 的"thread 即状态"+F9 的选择性清除，而非专门因子。

## 2. 示例代码中的 memory 部分（实测源码）

- **`packages/create-12-factor-agent/template/src/state.ts`（全文 49 行）**——官方脚手架的持久层全部内容：
  - `ThreadStore` 接口仅三个方法：`create(thread) / get(id) / update(id, thread)`（state.ts:7-11）。
  - 唯一实现 `FileSystemThreadStore`：`.threads/{uuid}.json`（结构化 thread）+ `.threads/{uuid}.txt`（`thread.serializeForLLM()` 直出 LLM 视图）**双写**（state.ts:22-32）；get 时 `new Thread(JSON.parse(data).events)` 仅凭 events 重建（state.ts:34-39）。
  - 注释明示扩展点："you can replace this with any simple state management, e.g. redis, sqlite, postgres, etc"（state.ts:13-14）。
  - → **"记忆存储 = 事件数组 + 两个投影（JSON 持久化 / LLM 序列化）"**，这就是 12-factor 派记忆层的全部抽象；A 层系统（mem0 的三级记忆、MemOS 的 MemCube）可视为对该极简内核在不同方向的加厚。
- workshops 进阶路径中 `07-context-window`（07-agent.ts/07b-agent.ts 逐步演示上下文构造）、`09-state-management`（09-state.ts 引入持久化）、`10-human-approval`（state.ts + 暂停在工具调用边界的审批）构成 memory 相关的实操序列。

## 3. "记忆即因子"设计原则提炼（本仓对 Agent 记忆系统的最大增量）

1. **上下文窗口是唯一读写接口**：记忆系统的产出物不是"存储"而是"下一次 LLM 调用的上下文构造"；注入格式（XML/JSON/消息角色分布）属于应用资产，必须可实验、可版本化。
2. **thread = 事实源，其余皆投影**：执行状态、业务状态、LLM 视图、人类可读视图全部是同一事件序列的派生（F5/F12），序列化、恢复、分叉因此免费。
3. **持久化粒度到事件级**：工具选择、工具结果、错误、人类响应各自成事件，才能支持"工具选择后、执行前"的暂停恢复（F6）。
4. **遗忘是一等公民**：已解决的错误应可从窗口移除、失败调用可隐藏（F3/F9）——记忆生命周期管理（compaction/TTL）由应用拥有，而非默认全保留。
5. **确定性优先于 agentic**：可预测的上下文在构建期预取（F13），模型的"自主检索"只兜底不可预测部分。
6. **框架警戒**：README:39-41、153-161 反复主张生产级 Agent 多为"自研栈 + 从框架借小模块"——记忆层同理，应做成可整体替换的库（如 `ThreadStore` 三方法接口）而非深耦合框架特性。

落地形态示意（综合 F5/F12/state.ts，忠实于原文语义的事件循环）：

```python
thread = {"events": [initial_message]}          # thread 是唯一状态
while True:
    context = thread_to_prompt(thread)           # F3：自建格式渲染
    next_step = await determine_next_step(context)
    thread["events"].append({"type": next_step.intent, "data": next_step})
    if next_step.intent == "done_for_now":
        break
    result = await handle_next_step(next_step)   # 失败则 append error 事件（F9）
    thread["events"].append({"type": next_step.intent + "_result", "data": result})
    store.update(thread_id, thread)              # state.ts：每轮持久化
```

→ 对照：README:122-134 的原始 agent loop 只比这多一行 `context.append(...)`；12-factor 的全部记忆主张就是给这个循环的每个 append 点立规矩。

## 4. 与 A 层 29 仓的对照定位

- A 层几乎全部是"厚记忆层"（抽取管线/混合检索/遗忘曲线）；12-factor 提供的是**薄底座规范**：任何厚记忆层都应能退化表达为"事件进 thread + 上下文构造期注入"。
- 具体可当 A 层评测维度：① 记忆条目能否映射回原始事件（溯源 = F5 的单一事实源）；② 暂停/恢复是否到事件粒度（F6）；③ 注入格式是否应用可控（F3）；④ 有无确定性 pre-fetch 路径（F13）；⑤ 错误/低质记忆有无清除机制（F9）。
- 注意：作者观点基于其 2024-2025 生产经验（README:153 "talked to at least 100 SaaS builders"），属工程判断而非学术验证 [定性来源]。

## 5. 局限

- 文档定位，无可运行记忆系统；thread 全量进上下文的模式在超长历史上会撞 token 墙——F3 只给了"自定义格式"的灵活性，未给 compaction 算法（这一缺口恰是 A 层 mem0/Letta 等的生存空间）。
- F12 的 reducer 表述在 2025 年后已被作者自己弱化为幽默条目，不宜当作强规范引用。
