# 当 Agent 的记忆长成一棵目录树：OpenViking 上下文数据库深度解析

> **一句话**：OpenViking 把 Agent 的记忆、资源、技能统一放进一个 `viking://` 虚拟文件系统，写入时自动压缩成 L0/L1/L2 三层渐进分辨率，检索走"目录递归 + 可观察轨迹"，会话提交后异步沉淀为九类长期记忆——它是"Context Engineering 的数据库范式"最具完成度的开源实现。

**信息基准**（2026-08-27）：
- 事实准绳：OpenViking 官方文档 `docs/zh/`（随仓库 HEAD `c66b9155`，2026-08-24 核实；评测数字对应 0.3.22）；
- 工程深度层：本案例库 25 篇源码精读笔记（`notes/`，行号已钉版），涉及"文档 vs 源码"的差异处均在文中显式标注；
- 论文：VikingMem（arXiv:2605.29640，VLDB 2026）。

---

## 0. TL;DR

- **范式转移**：从"黑盒向量库 top-k"转向"文件系统 + 数据库"——Agent 用 `ls`/`tree`/`find`/`grep` 确定性地浏览自己的上下文，向量检索只是目录递归的"路标"。
- **token 经济学**：每个目录挂两个隐藏 sidecar——L0 摘要（≤256 字符）进向量库、L1 概览（≤4000 字符）做 rerank，L2 全文按需加载。一棵千文件的资源树，导航成本从 10⁶ tokens 级降到每目录百 tokens 级。
- **检索可观察**：每次查询留下目录浏览轨迹与会话级台账，结果不对时能溯源到"它走了哪条路径"。
- **记忆闭环**：`session.commit()` 两阶段提交——同步归档、异步提取九类记忆，去重决策（skip/create/merge/delete）由 LLM 完成，`memory_diff.json` 留下完整审计日志。
- **实测效果**（官方自报）：LoCoMo 长对话记忆三种 Agent 集成全部拉到 80–83%（原生 24–57%），输入 token 反而减少 34.3%–91.0%；tau2-bench 任务成功率 +6.87～+11.87pp。

---

## 1. 问题：Agent 的上下文到底难在哪

官方文档（`getting-started/01-introduction.md`）把开发者的痛点总结为五条，我认为这是理解一切设计的钥匙：

| 痛点 | 本质 |
|---|---|
| **上下文碎片化** | 记忆写在代码里，资源在向量库，技能散落各处——没有统一的"存放处" |
| **所需上下文猛增** | 长程任务每次执行都产出上下文，简单截断/压缩必然丢信息 |
| **检索效果不佳** | 传统 RAG 平铺存储，chunk 之间没有结构，检索缺乏"全局视野" |
| **上下文不可观测** | 隐式检索链路是黑箱，召回错了不知道错在哪一步 |
| **记忆迭代有限** | 只有"用户记忆"，没有 Agent 自己的任务记忆（经验、轨迹） |

对这五条，OpenViking 的回答是一套完整的"数据库方案"：统一的寻址（URI）、分层的物化（L0/L1/L2）、结构化的检索（目录递归）、可观察的执行（轨迹留痕）、自动化的写入管线（会话→记忆）。这不是又一个 RAG 框架，而是给 Agent 造了一个"上下文的操作系统 + 数据库"。

**三种路线的分野**（对照 mem0 案例）：

| 维度 | 传统 RAG（向量库） | 记忆层（mem0） | 上下文数据库（OpenViking） |
|---|---|---|---|
| 核心抽象 | chunk + top-k | `Memory.add()/search()` | `viking://` 文件系统语义 |
| 信息组织 | 扁平 chunk | 扁平 memory 条目 + entity 链接 | L0/L1/L2 目录树渐进分辨率 |
| 确定性导航 | ❌ | 部分（graph 变体） | ✅ ls/tree/grep 零向量成本 |
| 覆盖上下文 | 知识文档 | 用户记忆 | 资源 + 记忆 + 技能三合一 |
| 形态 | 服务/库 | 库优先（可 embedded） | 服务优先（embedded 已删） |

---

## 2. `viking://`：把上下文装进一个文件系统

### 2.1 URI 与作用域

所有内容都有唯一 URI：`viking://{scope}/{path}`。作用域（scope）划分了生命周期与可见性：

| 作用域 | 说明 | 生命周期 | 可见性 |
|---|---|---|---|
| `resources` | 独立资源/客观知识（文档、代码、论文） | 长期 | account 全局 |
| `user` | 用户级数据（记忆、私有资源、技能、会话） | 长期/会话 | 当前用户 |
| `agent` | agent 能力与配置（技能、端点、工具、支付） | 长期 | account 全局 |
| `temp`/`queue`/`upload` | 内部实现作用域 | 临时 | 不可公开访问 |

一棵真实的树长这样（摘自 README）：

```
viking://
├── resources/              # 资源：项目文档、代码库、网页等
│   └── my_project/
│       ├── docs/
│       └── src/
└── user/
    └── {user_id}/
        ├── memories/
        │   └── preferences/
        │       ├── writing_style
        │       └── coding_habits
        ├── resources/
        ├── skills/
        └── peers/
            └── web-visitor-alice/   # 关于某个交互对象的记忆
```

两个值得玩味的设计：

- **家目录别名 `viking://~`**：`viking://~/memories/` 由服务端按认证身份展开为 `viking://user/{user_id}/memories/`——同一个字符串，不同调用方指向不同目录。响应永远回显 canonical 形式，杜绝别名泄漏进持久化数据。
- **路径变量**：`viking://resources/emails/{calendar:today}/inbox` 在服务端渲染为 `viking://resources/emails/2026/05/07/inbox`。按时间序列组织邮件、日志、日报的刚需被一等公民化了——这是"数据库"才有的查询表达力。

### 2.2 三种上下文类型

| 类型 | 用途 | 主动性 | 示例 |
|---|---|---|---|
| **Resource** | 知识和规则，相对静态 | 用户添加 | API 文档、代码仓库、FAQ |
| **Memory** | Agent 的认知，动态更新 | Agent 提取 | 用户偏好、实体、执行经验 |
| **Skill** | 可调用的能力，定义静态 | 用户/系统添加 | `SKILL.md` + scripts |

注意 Memory 的归属：**没有独立的 `viking://agent/memories`**——记忆存在用户或 Peer 命名空间下（`viking://~/memories/`、`viking://user/{uid}/peers/{peer_id}/memories/`）。"Agent 的记忆"挂在"Agent 服务的人"名下，这个设计选择暗含了产品假设：OpenViking 的记忆是"为用户而记"，不是"为 Agent 自己而记"。

### 2.3 类 Unix API

```python
client.find(query="用户认证")              # 语义搜索
client.ls(uri="viking://resources/")       # 列目录
client.tree(uri="viking://resources/my_project", level=2)
client.read(uri="viking://resources/docs/api.md")
client.abstract(uri="viking://resources/docs/")   # L0 摘要
client.overview(uri="viking://resources/docs/")   # L1 概览
client.grep("openviking", uri="viking://resources/my_project/docs")
```

命令行体验完全一致（Rust CLI `ov`）：

```bash
ov add-resource https://github.com/volcengine/OpenViking
ov ls viking://resources/
ov tree viking://resources/volcengine -L 2
ov find "what is openviking"
ov grep "openviking" --uri viking://resources/volcengine/OpenViking/docs/zh
```

**确定性导航（路径、grep）与语义检索（find/search）是并列的第一层分流**——前者零向量成本，后者才是语义管线。Agent 可以先 `tree` 看 L0 摘要定位，再语义搜索，最后 `read` 单个文件。这种"开发者式"的上下文操作，是与黑盒 top-k 的根本分野。

---

## 3. L0/L1/L2：为 token 预算设计的渐进分辨率

### 3.1 三层定义

| 层级 | 名称 | 存储形式 | 默认正文上限 | 用途 |
|---|---|---|---|---|
| **L0** | 摘要 | 目录内 `.abstract.md` | 256 字符 | 向量召回、快速过滤 |
| **L1** | 概览 | 目录内 `.overview.md` | 4000 字符 | Rerank、内容导航 |
| **L2** | 详情 | 原始文件和子目录 | 无统一上限 | 完整内容、按需加载 |

三个容易误解的精确点（官方文档反复强调）：

1. **L0/L1 是目录级 sidecar，不是 per-file 伴生文件**。向量检索的最小决策单元是"这个目录值不值得下钻"，不是"文件第 7 段说了什么"。文件摘要聚合进所在目录的 L1。
2. **两者不保证成对存在**。`mkdir(description=...)` 只产生 L0 也是合法状态；读侧代码必须处理"层不存在"。
3. **普通 `ls` 隐藏它们**；`ls output=agent` 才输出正文。

### 3.2 OKF sidecar：带受保护元数据的 Markdown

新生成的 L0/L1 是"最小 OKF Markdown"——YAML frontmatter + 可见正文：

```markdown
---
directory: viking://resources/docs/auth/
generated_by:
  component: SemanticProcessor
  trigger: resource_ingest
freshness:
  total_entries: 3
  sampled_entries: 3
  pending_child_changes: 0
---

API 认证指南，涵盖 OAuth 2.0、JWT 令牌和 API 密钥。
```

配套机制相当"数据库"：

- **写保护**：公共 `write` 不能创建新 sidecar、不能改受保护元数据；只提交正文则保留旧 metadata 重拼 canonical OKF。元数据只能由 SemanticProcessor 写。
- **Embedding 白名单**：只有"正文 + `directory` 一个字段"进入向量输入，`source`/`generated_by`/`freshness` 一律不进——保证重建索引不改变检索输入。
- **Freshness 统计**：`total/sampled/unsampled_entries` + `pending_child_changes` 只统计**直接子项**；子项超过 `overview_sample_limit`（默认 32）时用确定性保序采样——同一目录反复刷新选相同样本，避免正文与 git diff 抖动。

### 3.3 token 经济账

README 用 token 口径（L0 ≈ 100 tokens、L1 ≈ 2k tokens），配置用字符口径（256/4000）。源码精读笔记提醒：**中文字符的 token 密度约是英文的 3–4 倍**，做上下文预算要按语言实测。

经济账本身很清晰：一棵 1000 文件、5 层深的资源树，全量 L2 塞进上下文是 10⁶ tokens 级；而"L0 树导航"只需每目录百 tokens——Agent 先 `tree` 看 L0 定位（零向量成本）→ 读选中目录 L1（4k 字符）→ 最后 `read` 单文件 L2。**确定性路径导航 + 语义召回 + 深阅读**的三段式，就是"分层加载省 token"的落点。README 的评测里"token 减少 34.3%–91.0%"正是这套机制的直接收益。

多模态的处理也遵循目录级原则：图片/音视频不建 per-file sidecar，只生成文本摘要后作为普通文件摘要参与目录聚合（记忆提取时可用 VLM 把 ImagePart 描述为文本）。

---

## 4. 写入管线：解析与语义分离

### 4.1 三段流水线

```
输入文件 → Parser → TreeBuilder → SemanticQueue → 向量库
            ↓           ↓              ↓
         解析转换    文件移动     L0/L1 生成
         (无 LLM)   入队语义      (LLM 异步)
```

官方设计原则一句话：**Parser 不调 LLM，语义生成全部异步**。`add_resource` 的同步路径只到"入队"为止——用户不用等 LLM 跑完，LLM 成本全部移到后台队列。`--wait` 只是轮询任务状态，不改变异步本质。

- **Parser**：PDF/Markdown/HTML/代码仓库/图片/音视频各司其职。智能分割按 token 预算：≤1024 存单文件；否则按标题分割，小节 <512 合并、大节 >1024 升级为子目录。
- **TreeBuilder**：把 `viking://temp/` 的解析产物移入 AGFS 正式位置，5 阶段处理。
- **SemanticQueue**：自底向上生成——"文件摘要 → 叶子目录 L1 → 叶子目录 L0 → 父目录 → namespace 根边界"。单目录内并发 LLM 调用上限 10。

### 4.2 L0 从 L1 提取：一个省钱的小设计

L0 不是独立调用 LLM 生成的——它是 L1 正文的**结构化切片**（取 H1 之后、第一个 `##` 之前的 Brief Description 段落）。好处：省一半生成成本，且 L0/L1 天然一致。代价（源码精读发现）：L1 写得差（H1 后没有简介段）时 L0 会是空串，没有 fallback。

### 4.3 队列的防御工事（源码精读层）

精读笔记钉版的两个防御值得记录（`semantic_processor.py`）：

- **陈旧消息降级**：同目录有更新消息入队时，旧消息不整体跳过，而是降级为"仅文件工作"（不做目录聚合）——目录聚合让最新消息做，但旧消息改过的文件仍要单独摘要/向量化。
- **熔断重入队**：LLM API 已知故障时消息重新入队而非丢弃。

另一个官方文档自己承认的债：**语义冒泡写放大**。当前每次 resource/skill 语义任务成功后都会向父目录无条件冒泡刷新（直到 namespace 根），即使摘要没变——热点深层目录存在重复刷新与向上写放大。docs 的 concepts/03 与 06 两处都留着同一条 TODO：用 freshness 数据做合并/阈值/时间窗节流。有趣的是，`ov compile` 的写入路径（batch-write）已经实现了 `freshness_refresh_ratio=0.10` 的阈值调度（直接子项变更不足 10% 只累计 pending 不冒泡），通用摄取路径落地与否要看后续版本。

---

## 5. 检索：目录递归 + 可观察轨迹

### 5.1 两个入口：find 与 search

| 特性 | find() | search() |
|---|---|---|
| 会话上下文 | 不需要 | 需要 |
| 意图分析 | 不使用 | 使用 LLM 分析 |
| 查询数量 | 单一查询 | 0–5 个 TypedQuery |
| 延迟 | 低 | 较高 |
| 适用场景 | 简单查询 | 复杂任务 |

### 5.2 意图分析：把一句人话变成查询计划

IntentAnalyzer 的输入是"会话压缩摘要 + 最近 5 条消息 + 当前查询"，输出 0–5 个 `TypedQuery(query, context_type, intent, priority)`。查询风格有明确契约：

| 类型 | 风格 | 示例 |
|---|---|---|
| skill | 动词开头 | "创建 RFC 文档"、"提取 PDF 表格" |
| resource | 名词短语 | "RFC 文档模板"、"API 使用指南" |
| memory | "用户XX" | "用户的代码规范偏好" |

0 个查询 = 闲聊免检索；多个查询 = 一个任务同时要技能 + 资源 + 记忆。执行体是可单独配置的 `query_planner` 模型（未设置回退到 `vlm`）——官方在用微调小模型替换通用 VLM 做这一步以压成本（源码精读：两个 ollama 量化 SFT 模型各配了紧凑契约 prompt）。

### 5.3 层级检索：优先队列递归下钻

HierarchicalRetriever 的核心循环（官方文档伪代码）：

```python
while dir_queue:
    current_uri, parent_score = heapq.heappop(dir_queue)

    results = await search(parent_uri=current_uri)

    for r in results:
        # 分数传播：子节点分与父目录分的凸组合
        final_score = alpha * embedding_score + (1 - alpha) * parent_score

        if final_score > threshold:
            collected.append(r)
            if not r.is_leaf:          # 目录继续递归
                heapq.heappush(dir_queue, (r.uri, final_score))

    # 收敛检测
    if topk_unchanged_for_3_rounds:
        break
```

| 参数 | 默认值 | 说明 |
|---|---|---|
| `score_propagation_alpha` | 1.0 | 子节点自身分数的权重；1.0 = 不传播父目录分数 |
| `MAX_CONVERGENCE_ROUNDS` | 3 | top-k 连续不变即收网 |
| `GLOBAL_SEARCH_TOPK` | 10 | 全局搜索候选数 |

读懂这套算法的关键：**全局向量搜索只搜 level=[0,1]（目录级 sidecar 向量）**——L0 是递归的路标，L2 文件是终端命中（"目录层递归、文件层收网"）。Rerank（配置了 rerank AK/SK 时启用，失败自动回退向量分）用在两处：起始目录评估 + 每层子节点精排。

源码精读补充了文档没细说的默认值现实：**hotness 混合（`hotness_alpha` 默认 0）与分数传播（alpha 默认 1.0）两个排序旋钮默认全关**——生产默认形态其实是"裸向量分 + rerank"。机制的丰富性是预留的，不是开箱即用的。

### 5.4 可观察性：三层留痕

这是 OpenViking 最差异化的卖点之一。检索过程不是黑箱：

1. **请求级 telemetry span**：`search.intent_analysis`、`search.vector_retrieval` 等 span + counter 可随响应返回；
2. **会话级台账 `.recall_log.json`**：记录每个 served URI 的轮次与去向，可配冷却去重（近 N 轮已服务过的 URI 下一轮排除）；
3. **进程级 RetrievalStats**：zero_result_rate / avg_score / latency 经 observer API 暴露聚合健康度。

结果不对时，你能看到"它从哪个目录下钻、经过了哪些路径"——传统 RAG 里这叫"调不了"，这里叫"查日志"。

---

## 6. 会话 → 记忆：一个自动运转的闭环

### 6.1 两阶段 commit

```python
session = client.session(session_id="chat_001")
session.add_message(role="user", content="我喜欢深色模式")
result = session.commit()   # 启动后台记忆提取
task = client.get_task(task_id=result["task_id"])  # 轮询到 completed
```

- **Phase 1（同步，立即返回）**：消息写入归档目录 `history/archive_NNN/`，清空当前列表，返回 `task_id`；
- **Phase 2（异步后台）**：LLM 生成结构化摘要（写入归档的 `.abstract.md`/`.overview.md`）→ 提取长期记忆 → 写入 `memory_diff.json` 审计日志 → `.done` 完成标记。

### 6.2 九类内置记忆

| 用途 | 类型 |
|---|---|
| 用户与环境理解 | `profile`、`preferences`、`entities`、`events` |
| 助手身份与连续性 | `identity`、`soul` |
| 任务执行与学习 | `cases`、`trajectories`、`experiences` |

后三类是"Agent 越用越聪明"的关键：`cases` 沉淀可训练案例，`trajectories` 存可复用执行轨迹，`experiences` 是从执行结果提炼的经验。文档写明了依赖关系：`memory_policy.memory_types` 中启用 `experiences` 会激活完整 Agent Evolution 流程并自动带上 `cases`/`trajectories`；且**只有本次提取实际产生至少一个 case，才会继续训练 trajectory/experience**——没有案例的会话不产执行派生记忆。

### 6.3 记忆去重：LLM 做四值决策

提取不是无脑 append：

```
消息 → LLM 提取 → 候选记忆
        ↓
向量预过滤 → 找相似记忆
        ↓
LLM 去重决策 → candidate(skip/create/none) + item(merge/delete)
        ↓
写入 AGFS → 向量化
```

每次 commit 落盘 `memory_diff.json`，记录 adds/updates/deletes 的 URI、前后内容与计数——即使没有变更也写空结构。**记忆的每次演化都有审计日志**，这是"数据库"而非"缓存"的自我修养。

---

## 7. 进阶玩法：上下文编译（`ov compile`）

OpenViking 还内置了一个"知识编译器"：

```bash
ov compile \
  --from viking://resources/research \
  --to viking://resources/research-wiki \
  --skill viking://agent/skills/llm-wiki \
  --reason "把研究资料整理成便于团队检索的知识库" \
  --wait
```

三个输入：**从哪来**（`--from`）、**到哪去**（`--to`）、**编译成什么样**（`--skill`），外加可选的 `--reason`。执行体是 VikingBot：加载 Skill 后在一个独立 Agent Loop 里以你的身份 survey → 定向精读 → 写页面，经确定性 renderer 校验后 batch-write 回 `viking://` 树。

官方自带四个 Skill 示例：

| Skill | 产物形态 |
|---|---|
| **LLM Wiki** | 互链 Markdown 页面（实体/概念/方法页）+ 导航 `index.md` |
| **Knowledge Graph** | `entities/*.md` 节点 + `relations.jsonl` 关系边表 |
| **日报** | 每天一页 `<YYYY-MM-DD>.md`，从会话/IM 还原"做了什么" |
| **知识蒸馏** | 主题/结论两级树，跨来源提炼高层发现 |

与 L0/L1/L2 的关系是正交的："compile 把原始材料变成结构化知识产物（形态由 Skill 决定），semantic pipeline 把任意目录树压缩成 L0/L1 sidecar（形态固定）"。编译产物是普通 L2 文件，写入后由常规流水线自动补齐三层 sidecar——**编译自带语义闭环，但不自带重编译**（没有源→产物依赖图，源库更新后要手动重跑，这是当前的明确局限）。

---

## 8. 架构与部署：一切皆 HTTP

### 8.1 四层栈 + 双层存储

```
┌───────────────────────────────────────────────┐
│ Client 层    Python/Go/TS SDK · Rust CLI ov · MCP │
├───────────────────────────────────────────────┤
│ Service 层   FastAPI 单进程编排 8 个子服务          │
│              FS/Search/Session/Resource/Pack/     │
│              Debug/ResourceMemoryLink/AgentEvolution │  ← 文档列 6 个，源码 8 个
├───────────────────────────────────────────────┤
│ VikingFS     viking:// 虚拟文件系统抽象（URI 映射）   │
├───────────────────────────────────────────────┤
│ 存储层        AGFS/RAGFS（内容）+ 向量库（索引）      │
└───────────────────────────────────────────────┘
```

双层存储的设计原则是"**单一数据源**"：

| 存储层 | 职责 | 存储内容 |
|---|---|---|
| **AGFS**（已重写为 Rust 的 RAGFS） | 内容存储 | L0/L1/L2 完整内容、多媒体文件 |
| **向量库** | 索引存储 | URI、向量、元数据——**不存文件内容** |

所有内容从 AGFS 读取，向量库只存引用；`rm`/`mv` 自动同步向量（递归删除、URI 重写）。支持 localfs/s3fs 后端与多写模式（`storage.agfs.backups`：primary + backup 副本/迁移）。向量后端可选本地（C++ 引擎）、HTTP 远程、火山引擎 VikingDB。

### 8.2 Embedded 之死：一次自杀式重构（源码考古）

2026-08-10 的 PR #3712 彻底删除了 Python embedded mode——曾经 `ov.OpenViking(path="./data")` 进程内直调的用法不复存在，`openviking/client/` 只剩 28 行 HTTP 兼容 shim。**所有客户端（SDK/CLI/MCP/LangChain）统一走 HTTP**。

得到什么：单一协议砍掉双倍测试矩阵；客户端瘦到零原生依赖（Rust/C++ 扩展只在 server 进程内加载），`pip install openviking-sdk` 任何平台可用。

失去什么：Jupyter 探索式场景多了一跳"先起 server"；高频细粒度调用的 Agent 循环每步多付一次 RTT + JSON 序列化。mem0 至今保留进程内模式作为对位卖点——这是两条路线的真实分岔口。

### 8.3 单机锁：水平扩展的产品分界线

收敛的物理约束是 workspace 级 PID 锁（`.openviking.pid`）：同一数据目录只允许一个活进程。源码精读发现一个配置陷阱：`server.workers` 配置存在，但 workers>1 时第二个 worker 会在构造期撞锁直接崩——开多 worker 隐含要求 `skip_process_lock: true`（文档警告"仅在明确接受并发写风险时启用"）。Helm chart 默认 `replicaCount: 1` 自洽。

开源版的天花板就是单进程 + 异步；多写高可用属于商业版（私有化部署版"增加分布式部署能力"，激活码激活）或 roadmap（"分布式存储后端"在官方路线图未来计划里）。README 承诺开源版 AGPLv3 不锁功能——分界线画在"谁来运维、部署在哪"，不是"能不能用"。

### 8.4 五分钟跑起来

```bash
pip install openviking --upgrade
openviking-server init      # 交互式向导：火山引擎/OpenAI/Kimi/GLM/Ollama
openviking-server doctor    # 启动前体检
openviking-server           # 起在 127.0.0.1:1933
```

生产部署走 Docker/compose/Helm；公网 HTTPS 走 Caddy 反代（OAuth 对非 localhost 强制 TLS）。生态接入了 Claude Code、Codex、OpenClaw、Hermes、Cursor、Trae、OpenCode、pi、MCP 客户端、LangChain/LangGraph（独立包 `langchain-openviking`），另有桌面控制台 OpenViking Helper（Beta）和内置于服务器的 VikingBot（`ov chat`）。

---

## 9. 效果：评测数字说话

官方 0.3.22 评测（VLM=Doubao 2.0 Pro，Embedding=Doubao-embedding-vision-251215，复现脚本在 `./benchmark`）：

**用户记忆（LoCoMo 长对话记忆）**

| Agent 集成 | 原生记忆 | + OpenViking |
|---|---|---|
| OpenClaw | 24.20% | **82.08%** |
| Hermes | 33.38% | **82.86%** |
| Claude Code | 57.21% | **80.32%** |

同时输入 token **减少 34.3%–91.0%**，查询时延降低 58.45%–66.10%——准确率与成本同时改善，这是"分层加载 + 目录递归"结构红利的最直接证据。

**Agent 经验（tau2-bench 多轮任务）**：经验记忆让任务成功率 Retail +6.87pp、Airline +11.87pp（同一 LLM 无记忆对照）。

学术侧：OpenViking 开源了 VikingMem 论文（*VikingMem: A Memory Base Management System for Stateful LLM-based Applications*，arXiv:2605.29640）描述的部分核心能力，已被 VLDB 2026 接收。

*注意：以上为官方自报数字，评测配置（Doubao 全家桶）与你的栈可能有差；好在 benchmark 可复现。*

---

## 10. 批判性分析：七件值得冷静看待的事

赞美完毕。结合官方文档的自认与源码精读，这是我认为读者应该带着的问题：

1. **语义冒泡写放大**（官方 TODO）：每次成功的语义任务无条件向父目录冒泡刷新直到根，热点深层目录重复刷新。compile 路径已有 freshness 阈值节流（10%），通用摄取路径待落地。深目录大仓库摄取要有心理预期。
2. **打分信号薄**：rerank 的打分文本是 256 字符级的摘要——"目录值不值得下钻"由最短的文本决定。且 hotness 混合与分数传播默认全关，文档描述的丰富排序机制在默认配置下是"裸向量分 + rerank"。
3. **意图分析是单点**：search 链路的 IntentAnalyzer 无超时无兜底（源码精读发现，recall 链路反而有 5s 超时 + 回退）——query_planner 抖一次，整个请求 500。官方在用 SFT 小模型 + 紧凑 prompt 补这个洞。
4. **L0/L1 的质量上限 = 所配 VLM 的质量**：语义分层是 LLM 生成的，弱模型直接劣化检索第一跳。
5. **单机锁**：水平扩展默认关死，多实例共享 workspace 属于"危险开关"状态。分布式在 roadmap/商业版。
6. **compile 无依赖追踪**：没有源→产物脏标记、没有 make 式失效传播，重编译是任务级全量重付（60 分钟运行上限内的 LLM 调用全部重来）。增量收敛靠语义匹配旧页，漏配产同义重复页、错配污染结论——离"持续保鲜的编译型记忆"还差两块基础设施。
7. **迭代速度与合规**：30 天 262 commits 含 3 次破坏性变更（embedded 删除、URI 迁移、relations 删除）——上车要系安全带；主项目 AGPLv3 对闭源商用有传染性约束（CLI/examples 是 Apache 2.0），选型前让法务过目。

还有一处文档与源码的口径差值得记录：concepts/03 说"rerank scalar 是纯 L1 正文"，源码精读核实 rerank 打分文本实际是 `abstract` 字段（L0 级）；concepts/07 的 `MatchedContext` 字段表与实际 dataclass 也有出入。**读这个项目，"docs 为准、代码为真、DeepWiki 只当历史档案"是三方核对的心法**（DeepWiki 基线落后 262 commits，embedded mode 等整节已失效）。

---

## 11. 结语：Context Engineering 的数据库时刻

把 OpenViking 放回更大的图景里看：

- LLM 时代的前半场，大家把"记忆"当成**prompt 工程的附件**——塞一段系统提示词、维护一个 summary 文件；
- RAG 时代，记忆变成**检索问题**——向量库 + top-k，但结构、可观察性、token 预算全都缺席；
- OpenViking 代表的思路是：记忆是**数据管理问题**——需要寻址（URI）、模式（三种上下文类型）、物化视图（L0/L1/L2）、查询优化（目录递归）、事务与审计（commit + memory_diff）、甚至编译（ov compile）。

"数据库范式"不是修辞：上面每一个名词都对应数据库几十年的成熟积累。OpenViking 未必是最终形态（单机锁、写放大、compile 无增量都在提醒你它才几个月大），但它证明了一件事——**当你把 Agent 的上下文当作一等数据来管理，而不是当作 prompt 的补丁，准确率和成本可以同时改善**。LoCoMo 上 24%→82% 的跃迁，一半功劳属于记忆，另一半属于"记忆有了家"。

对想上手的读者：`pip install openviking` 五分钟后你就能 `ov tree` 看到自己的第一棵上下文树。对想做架构选型的读者：拿本文第十节的七个问题去问任何一家记忆系统厂商，都是合格的尽职调查清单。

---

## 参考资料

- 官方文档（本文事实准绳）：[docs.openviking.ai](https://docs.openviking.ai/) · 架构 [concepts/01](https://docs.openviking.ai/zh/concepts/01-architecture) · 分层 [concepts/03](https://docs.openviking.ai/zh/concepts/03-context-layers) · 检索 [concepts/07](https://docs.openviking.ai/zh/concepts/07-retrieval) · 会话 [concepts/08](https://docs.openviking.ai/zh/concepts/08-session) · 上下文编译 [context-compilation/01](https://docs.openviking.ai/zh/context-compilation/01-overview)
- 官方博客：[The Database Paradigm for Context Engineering](https://blog.openviking.ai/post/openviking-context-database/) · [评测报告](https://blog.openviking.ai/post/openviking-benchmark-results/)
- VikingMem 论文：arXiv:2605.29640（VLDB 2026）
- 源码精读笔记（工程细节与"文档 vs 源码"差异）：本案例库 `notes/`（00-overview/02-architecture、02-vikingfs-layers/02-l0l1l2、01-core-python/03-retrieve-pipeline、00-overview/04-two-modes、02-vikingfs-layers/03-context-compilation 等 25 篇）
- 对照案例：`../mem0开源记忆层/notes/`（记忆层 vs 上下文数据库两条路线）

*基准：docs @ HEAD `c66b9155`（2026-08-24）；源码精读行号同基准。写作日期 2026-08-27。*
