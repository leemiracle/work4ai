# 让经验留在队伍里：TencentDB Agent Memory 团队记忆架构全解析

> **姊妹篇**：[A05b-场景迁移-安卓个人助手Agent架构.md](A05b-场景迁移-安卓个人助手Agent架构.md)——以本文为骨架之一，设计**安卓个人助手 Agent 的完整七层架构**（循环/工具/记忆/技能/上下文/模型/治理——App Graph、Routine、谱系化上下文、隐私分级）。
>
> 从 Semantic Pyramid 到 KV-cache 友好注入，一个开源团队记忆系统的工程取舍
>
> 信源声明：本文以官方仓库文档为准（`docs/`，基于 v2.0.0，2026-08-11 更新；GitHub [TencentCloud/TencentDB-Agent-Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory)，MIT 协议），并参考一份逐行源码深读笔记（A05）补充实现细节与批判视角。文中所有机制描述以 docs 为准；来自源码笔记的细节会单独标注。

## TL;DR

- **定位**：不只是"记住对话"——把 Chat Memory、Skill、Wiki、CodeGraph 统一成可治理的 **Memory Asset（记忆资产）**，让下一个 Agent 在第一个 turn 就拿到"前一个 Agent 留下的存档"。
- **核心抽象**：**Semantic Pyramid（语义金字塔）**——L0 原始对话 → L1 原子记忆 → L2 场景块 → L3 用户画像，逐层提炼，分层召回。
- **最值得学的三件事**：① 单次 LLM 调用同时完成"场景切分 + 记忆抽取"，四动作判重（store/update/merge/skip）显式建模新旧记忆关系；② **KV-cache 友好的注入经济学**——稳定内容进 system prompt、易变内容 prepend user prompt、L0/L1 下沉为按需调用的只读工具；③ 用户手工编辑的 Wiki 页 `locked: true`，机器永不覆盖——人机共治记忆的最小安全阀。
- **成绩单**：PersonaMem 基准从无记忆 48% → 启用后 76%（相对提升 +59%）。
- **代价**：组件多（四件套）、全链路强 LLM 依赖、CodeGraph 核心是第三方原生依赖——它换来的"团队级治理"是不是你要的，读完本文你自己判断。

---

## 一、问题：Agent 的"失忆症"到底贵在哪

每个重度使用 Coding Agent 的人都被同一件事折磨过：

项目背景讲过了，换个 Session 还得再讲一遍；文档读过了，每个新 Agent 都要从第一页重读；一套排障流程上周刚跑通，这次又从 Stack Overflow 重新搜起。

传统解法有两档，都不够：

| | 聊天历史 | 普通 RAG | TencentDB Agent Memory |
| :--- | :---: | :---: | :---: |
| 跨会话理解用户 | △ | △ | ✅ Chat Memory（L0–L3）|
| 沉淀可执行经验 | — | — | ✅ Skill（版本化）|
| 文档结构与关系 | — | △ 切片检索 | ✅ Wiki + Link Graph |
| 代码调用与影响范围 | — | △ 文本命中 | ✅ CodeGraph |
| Owner / 版本 / 状态 | — | — | ✅ |
| 团队分享与 Agent 配装 | — | — | ✅ |
| 私有 / 团队 / ACL | — | △ | ✅ |

一句话：**RAG 解决"能查到什么"，Team Memory 还要解决"谁可以用、哪个版本有效、应该配给哪个 Agent"。**

这个项目的设计哲学就是三个问号：**什么值得记？谁能用？怎么取？** 后文的所有机制，都是这三个问题的工程答案。

## 二、总体架构：四件套 + 一个 SDK

```text
┌────────────────────────────────────────────────────────────────┐
│              Claude Code / CodeBuddy / OpenClaw / Hermes        │
└───────────────┬────────────────────────────┬───────────────────┘
                │ OpenAI/Anthropic 协议       │ HTTP API / SDK
                ▼                            ▼
      ┌──────────────────┐        ┌──────────────────────────┐
      │ MemoryProxy      │        │ MemoryCore Gateway :8420 │
      │ :8096 透明转发    │ ─────► │  记忆 L0/L1/L2/L3        │
      │ session 初始化    │  HTTP  │  Skill 抽取/版本          │
      │ context 注入      │        │  Team/Agent/User 元数据   │
      │ 对话回写          │        │  SQLite + 本地文件        │
      └──────────────────┘        └────────▲─────────────────┘
                                         │ 注册/回调
      ┌──────────────────────────────────┴──────────────────────┐
      │              Memory Hub = Panel + Knowledge              │
      │  MemoryPanel :8125    MemoryKnowledge :8424              │
      │  资产治理/权限 UI      Wiki ingest + CodeGraph 索引        │
      └──────────────────────────────────────────────────────────┘
```

四个组件各管一段，边界非常克制：

| 组件 | 端口 | 一句话 | 关键约束 |
|------|------|--------|---------|
| **MemoryCore** | 8420 | 大脑：存储 + L0→L3 提炼 + Skill + 元数据 | 最复杂，~230 文件 |
| **MemoryProxy** | 8096 | 嘴巴：接 Coding Agent，注入 + 回写 | **自己不落任何记忆数据** |
| **MemoryPanel** | 8125 | 控制台：人看/治理资产 | 无状态 BFF，不存会话不存用户库 |
| **MemoryKnowledge** | 8424 | 书架：Wiki + CodeGraph 内容检索 | **只存知识内容，元数据归 Core** |

三个部署形态：三件套一键起（推荐）、Panel+Knowledge 合并镜像、独立部署。本地跑通只要：

```bash
git clone https://github.com/Tencent/TencentDB-Agent-Memory.git
cd TencentDB-Agent-Memory/deploy/global-images
cp .env.example .env && $EDITOR .env   # 填两组 LLM 参数
./start-all.sh                          # 结束会打印 Claude Code 可直接复制的接入命令
```

### 一次对话如何变成记忆（端到端数据流）

这是整个系统最核心的循环，官方叫 **Every Loop Gains Experience**：

1. **Step A 对话产生**：Proxy 拦截首轮请求 → 弹表单让用户选 Team → Agent → Task；把该 Agent 绑定的 Skill / Wiki / CodeGraph 摘要 + L2/L3 按预算注入 system prompt；**L0/L1 作为 read-only 工具暴露给模型按需调用**。
2. **Step B 对话回写**：一轮真人提问结束（注意是 round-level，不是每次 HTTP），Proxy 把对话切片推给 Core：一路进 Skill 归档候选队列，一路写 L0。
3. **Step C 后台提炼**（异步 pipeline）：L0 →L1 抽取→ L1 →L2 聚合→ L2 →L3 画像生成；对话中还可提炼出 Skill 草稿。所有提炼都走 LLM。
4. **Step D 下次复用**：下一个 session 选了同一个 Agent，Proxy 自动注入 L2/L3 + 已审 Skill——Agent 不用重新介绍项目背景，直接干活。

## 三、Semantic Pyramid：记忆不是平铺记录，而是逐层生长

这是整个系统对外宣示的核心概念。对话先作为 L0 全量保存，再由异步 Pipeline 提炼成不同粒度：

| 层级 | 保存什么 | 主要用途 |
|------|---------|---------|
| **L0 Conversation** | 原始对话与完整上下文 | 核对原话、时间和来源 |
| **L1 Atom** | 事实 / 偏好 / 约束 / 事件 | 精确召回可执行信息 |
| **L2 Scenario** | 围绕项目或场景组织的知识块 | 快速恢复一个工作场景 |
| **L3 Core / Persona** | 长期画像、稳定模式、高层认知 | 让 Agent 迅速进入用户和团队语境 |

### 3.1 L0：全量捕获，但防"记忆反馈环"

L0 按**日分片 JSONL**存储（`conversations/YYYY-MM-DD.jsonl`）。两个容易忽视的工程细节：

- **双层去重**：正常流程用"位置切片"（缓存消息计数，`agent_end` 时只取新增）；进程重启后位置信息丢失，靠"时间戳游标"兜底（只接受严格大于最后记录时间戳的消息）。
- **Sanitize 清洗**：写盘前剥离 `<relevant-memories>`、`<user-persona>` 等系统注入标签、框架噪声和内联 base64 图片。**为什么重要？如果不剥，Agent 会把"系统注入的记忆"当成对话内容再记一遍——记忆吃掉自己的尾巴，形成反馈环。**

### 3.2 L1：一次 LLM 调用干两件事，四动作判重

L1 抽取是整个管线的灵魂，有两个反直觉的设计：

**设计一：场景切分和记忆抽取合并成单次 LLM 调用。** 模型一次输出 `SceneSegment{scene_name, message_ids, memories[]}`——既完成了话题切分，又完成了记忆抽取，而且每条记忆天然带上场景聚类标签。比逐条抽取省调用，也省协调成本。（源码笔记补充：取最近 10 条新消息 + 5 条背景消息，每会话上限 10 条记忆；抽取前有质量门 `shouldExtractL1` 过滤短消息/纯工具输出/prompt-injection。）

记忆类型三种：**`persona`**（用户偏好）、**`episodic`**（事件经历）、**`instruction`**（指令约束）。

**设计二：LLM 判重不是"相似或不相似"，而是显式四动作。** 新记忆与库中已有记录比对后，LLM 决策：

| Action | 含义 |
|--------|------|
| `store` | 无冲突，新建 |
| `update` | 新信息更准，替换旧记录 |
| `merge` | 合并新旧为一条更完整的记录（保留 timestamps 轨迹，可看合并史）|
| `skip` | 现有记录更优，丢弃新的 |

对比 mem0 式 ADD/UPDATE/DELETE 三分类，`merge` 显式建模了"新事实与旧记忆的关系"，比"覆盖"或"并存"都更接近人对记忆更新的直觉。候选召回本身有三级降级：向量余弦优先 → 无 embedding 时退 FTS5 BM25 → 都没有就全作新记录（**零配置也能跑，只是记忆会膨胀**）。

存储是**双写**：JSONL 追加式（备份/恢复的真源）+ SQLite 向量库（主检索引擎），update/merge 时实时删旧行。

### 3.3 L2：让 LLM 在沙箱里当"文件管理员"

L1 完成后推进 L2 定时器（delayAfterL1 90s，间隔 900–3600s，且 **downward-only**——触发时间只能提前不能延后，公式 `max(now+delay, lastL2+min)` 同时保证响应性和限流）。L2 Runner 把 L1 记忆合并进 `scene_blocks/*.md`，用的是一套很"Agent 原生"的机制：

- **沙箱工作区**：LLM 只能看到 `scene_blocks/` 目录，用 `read/write/edit` 工具操作 markdown 文件，碰不到 `checkpoint.json` 等系统文件；所有路径经沙箱校验不可逃逸。
- **软删除**：LLM 无权直接删文件，只能写入 `[DELETED]` 标记，由 runner 随后清理——防误删的最后防线。
- **容量三级警告**：基于 `maxScenes=20`，场景数到红区强制 MERGE、橙区只许 UPDATE、黄区建议合并——**用 prompt 级指令给 LLM 的"文件系统手"装了护栏**。
- **Fail-Soft**：每次 LLM 修改前先快照 `scene_blocks/`，产出损坏或进程崩溃可回滚。
- **带外信号**：L2 是系统首次检测"用户根本画像是否改变"的位置——LLM 可在文本输出中发 `[PERSONA_UPDATE_REQUEST]` 信号触发下一周期 L3。

### 3.4 L3：Persona Architect 的四层深度扫描

L3 生成 `persona.md`（≤2000 字符），有五个优先级触发条件（显式请求 / 冷启动 / 恢复损坏 / 第一个场景块 / 每 50 条新记忆）。生成 prompt 指示 LLM 按四层模型分析用户：

| Layer | 扫描什么 |
|-------|---------|
| Base Anchors | 事实、人口统计、当前状态 |
| Interest Graph | 爱好、消费习惯、主动 vs 被动兴趣 |
| Interaction Protocol | 沟通风格、"landmines"（应避开的话题）、工作流偏好 |
| Cognitive Kernel | 决策逻辑、核心矛盾、终极驱动 |

执行分 `first`（全量初始化）和 `incremental`（只喂自上次以来的变更场景）两种模式——增量模式既省 token 又聚焦演化。

### 3.5 别踩坑：系统里有**两套平行的 L1/L2/L3**

docs 反复强调的命名陷阱：Memory 管线之外还有一条 **Offload 管线**，是编码助手场景的**工具调用压缩**链路，输入是 tool_use/tool_result 对，产出是 **Mermaid flowchart 任务拓扑图（Symbolic Memory）**——把冗长的 tool 执行日志变成高密度拓扑图留在上下文里，原始 token 密集的 tool output 卸到磁盘 `refs/*.md`，Agent 需要时按 `node_id` 下钻。压缩分三个递增严重度的 Tier（mild 摘要替换 ratio 0.4 → aggressive 前缀删除 0.2 → emergency 截断 0.95），配套一个不走 BPE 的 `fastEstimateTokens`（~5ms/100K 字符、误差 2–7%，带 CJK 查找表和连续汉字 0.94x 合并折扣）——**先快估再精确，只在关键节点用 tiktoken**。两条管线概念同名但完全独立，读源码时务必分清。

## 四、Skill：把 SOP 做成版本化资产，而不是一段自由文本

Skill 是"程序性记忆"：Agent 做完复杂工作后，从对话和工具调用中提炼可复用的工作流。它不是一段 prompt，而是带**版本、资源文件、触发边界、执行步骤和验证规则**的配置对象。

治理动作 6 写 4 读（create/update/patch/delete/writeFiles/removeFiles + …），写前三重校验 `assertTeamMatch / assertOwner / assertVersionFresh`。数据模型是**单表多行多版本**（源码笔记：`UNIQUE(skill_id, version)` 不可变快照 + `(team_id, owner_agent_id, name) WHERE is_head=1` 的部分唯一索引）：

```sql
CREATE TABLE skills (
  row_id TEXT PRIMARY KEY, skill_id TEXT NOT NULL, version INTEGER NOT NULL,
  is_head INTEGER NOT NULL DEFAULT 1,
  user_id TEXT NOT NULL, owner_agent_id TEXT NOT NULL, team_id TEXT NOT NULL,
  name TEXT NOT NULL, content TEXT NOT NULL, content_hash TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  UNIQUE(skill_id, version)
);
```

抽取管线本身也值得抄作业：

- **Transcript 头尾截断**：head 8000 / tail 32000 字符——**保开头（意图）和结尾（成功结果），剥中间**。这是对"长对话里最有信息量的部分在哪"的务实回答。
- **归档阈值**：对话累积到 `tool_call ≥ 10` 或 `bytes ≥ 40KB` 才触发抽取，避免碎片段污染。
- **Review Agent 模式**：LLM 不是直接输出 skill，而是拿着 `skill_create/skill_update/skill_patch/skill_delete/skill_files_write` 五个工具（最多 16 轮迭代）去评审现有 skill 库并产出候选——**增量维护，而非每次重建**。
- **资产联动幂等**：`onSkillCreated` 前置 await（失败即创建失败，不留孤儿资产）、读时自愈、归档级联，三条路径全覆盖。

个人 Skill 默认私有；审核后可分享团队，再配装给其他 Agent——"练会一次，全队可用"。

## 五、Knowledge：一张同时看懂文档和代码的地图

### 5.1 Wiki：增量摄取 + locked 硬约束

Wiki 的思路直接受 Karpathy 的 "LLM Wiki" gist 启发：把文档视为**由 LLM 增量维护、可持续复利**的知识产物。摄取流水线（ingest-v2）的关键决策：

- **增量省 token**：按 sha256 对比磁盘源与 source 表，只为新增/失败/变更的源调 LLM；source 表作为一等实体追踪生命周期。
- **两阶段 LLM**：先 analysis 出抽取计划，再 generate 出 FILE 块（质量更稳，空结果自动降级单阶段）；chunker 按 markdown 标题边界切（28000 字符预算，overlap 400）。
- **canonicalizePagePath**：不信任 LLM 选的目录/文件名，用 frontmatter 的 type+title 强制规范化——保证"同一实体二次摄取 → 同一路径"的 dedup 不变量。
- **locked 硬约束**（我最喜欢的一条）：用户手工编辑过的页自动标 `locked: true`，摄取**永不覆盖**。这是人机共同治理记忆的最小安全阀——机器可以整理，但人定稿的地方机器闭嘴。
- **merge 分档**：小页整页重写（质量优先），大页追加增量片段（省 output token + 防丢旧事实）。
- **per-wiki 独立 index.db**：每个 wiki 一个 SQLite（FTS5 + page_meta + graph_edge 三表）+ LRU 读连接池，内存上限与 wiki 总数解耦——根治了早期全量常驻内存的 OOM。

检索是 **BM25 全文（title×5 加权，jieba 中文分词）+ wikilink 图多跳 BFS**（hop≤5、逐层衰减、硬上限 200 节点）。每个搜索结果带邻居，响应带结果间连线——Agent 不只查到"这页讲了什么"，还看到"它和谁有关"。

### 5.2 CodeGraph：代码的 caller/callee/impact 查询

代码库 `git clone` 后经静态索引变成可查询的图谱：符号、文件、调用关系、影响路径。Agent 改代码前可以先做 impact analysis——"不只告诉它代码在哪，还告诉它改了会影响哪"。

两点工程上的清醒认知：① 核心引擎是**复用开源项目 `@colbymchenry/codegraph`**（官方 README 明确致谢），本仓库只做桥接封装和元数据管理；② 第一版只支持公开 HTTPS 仓库（带 SSRF 私网黑名单），私有仓库和 SSH 凭证仍在完善。auto-sync 默认关闭，开启后每 10 分钟扫 ready 状态仓库做增量同步。

Wiki 和 CodeGraph 都通过 `/v3/tools/list` + `/v3/tools/call` 两步自发现暴露给 Agent，也有 MCP stdio（12 个只读工具）。**知识不整库注入，而是按需调用**——它们平时只是可用的工具，真正需要时才进上下文。

## 六、注入的经济学：KV-cache 是第一公民

这一节是我认为全项目最有"生产味"的部分。所有记忆最终要进 prompt，而**怎么进**直接决定推理成本：

| 内容 | 稳定性 | 注入策略 |
|------|--------|---------|
| L3 Persona + L2 场景导航 + 工具指南 | 会话内稳定 | append 进 system prompt（**命中 KV-cache**）|
| L1 相关记忆 | 每轮变化 | prepend 到 user prompt |
| L0/L1 全量 | — | **不注入，下沉为只读工具**（`/memory-bridge` 反代）|

为什么 L0/L1 不每轮注入？**会打爆上游 KV-cache**——每轮变动的注入内容会让 Anthropic/OpenAI 的 prompt cache 反复 miss。所以 Proxy 的注入 pipeline 用 9 个 injection point + hook cache（`session_init` 时 prewarm、命中即跳过）保证 system prompt **字节级稳定**，甚至提供出站 body MD5 观测来长稳验证 cache 命中。

配套还有几个"防 Agent 作妖"的细节：

- **搜索限流写进注入 prompt**：`tdai_memory_search` 和 `tdai_conversation_search` 每轮合计最多调 3 次；3 次无果就直说"该信息不在记忆中"。这是对"Agent 搜索成瘾"失效模式的直接工程对策。
- **三重预算卡**：单条记忆字符上限截断（保留最小 40 字符）+ 总量字符预算 + 5s 超时——**记忆是来帮忙的，不许反过来占满上下文**。
- **round-level 回流**：一次真人提问会引发 N 次 HTTP（工具循环），Proxy 只在"无 tool_use 的最终回复"出现时才回流一次——RPC 数降 N 倍。且 L0 写入是 fire-and-forget（不阻塞 SSE 流式关流），靠 in-flight 追踪 + SIGTERM 兜底 flush。
- **`mem:` 命令零 token 拦截**：用户输入 `mem:sync` 等命令时直接在代理层拦截并伪造响应，不转发上游，但记忆时间线照常记录。
- **CC 请求分流**：Claude Code 后台会发 FORK（SUGGESTION/RECAP）和 SIDEQUERY（TITLE/probe）请求，Proxy 精准识别后分别 readOnly 注入/跳过注入——最大化 cache 命中。

安全设计同样在线：skill/memory bridge 反代时，session 里的身份字段**强制覆盖** LLM 提供的同名字段（LLM 不能伪造身份）；serviceToken 只存在于 proxy→core 一段，**绝不进 LLM 可见的 prompt**；团队级搜索二次过 ACL 白名单且 fail-closed。

## 七、治理：记忆资产的权限模型

团队场景下，"谁能用"和"记什么"同样重要。系统给了完整的答案：

- **三维隔离**：每个数据面请求必须带 `Team × Agent × User`（`x-tdai-*` header），session/task 可选收窄。用户身份从 Panel 的 `sk-mem-` key → Claude Code 的 `ANTHROPIC_AUTH_TOKEN` → Proxy 的 `auth/verify` → 后端过滤，端到端贯穿同一个 key。
- **五级可见性**：`private`（连团队 admin 都看不到）/ `team` / `restricted`（User/Role/Agent ACL 精确授权）/ `agent`（定向装配）/ `task`。
- **六段式权限纯函数**：asset 存在性 → owner → team 成员 → visibility 分支 → 角色默认（admin=[read,write,assign,share]，member=[read]）→ ACL 显式匹配，allow-only。
- **双部署模式**：standalone（SQLite + 进程内调度，零配置）↔ service（MongoDB database-per-instance + Redis XREADGROUP 分布式队列 + 死信队列），**runner/handler 共用，只换调度层**。
- **可追溯**：Wiki/CodeGraph 各有 append-only audit 表；每次记忆生成记录层级/模型/prompt 版本/延迟/输入输出引用（源码笔记称 MemoryGenerationLog）——记忆可以回答"谁在何时用什么 prompt 生成了我"。

## 八、批判性评估：它付出什么，缺什么

任何架构都是取舍。综合 docs 自述的注意事项与源码笔记，把丑话说在前面：

1. **全链路强 LLM 依赖**。L1 抽取、判重、场景聚合、persona 生成、skill 提炼全是 LLM。弱模型下 JSON 输出质量不可控（源码笔记：靠 sanitize+repair 抢救过 `"priority": sheet` 这类输出）；判重失败会降级为全量 store，长期有记忆膨胀风险。**换模型 = 换记忆质量**，选型时要把它当 LLM 应用对待。
2. **每轮两次 LLM 后台调用的成本**。抽取 + 判重各一次（超时 180s 量级），高频回写下这是持续成本；好在是异步旁路，不阻塞对话。
3. **CodeGraph 是第三方原生依赖**。平台二进制包，跨平台/CI 需要保证 optional dependency 安装；上游 API 漂移会直接断桥。官方对此很坦诚（README 致谢 + Roadmap 标注私有仓库支持仍在完善）。
4. **三维隔离是"半路加装"**。字段可选 + 旧数据 `__legacy__` 回填（`legacyCompatMode` 填占位符），且 `/v3` 严格隔离开关**默认 OFF**，生产部署必须显式开 `V3_STRICT_ISOLATION`——这是一个容易踩的默认值。
5. **组件多、上手成本真实存在**。四个服务 + 两类存储后端 + 三路可观测（Opik/Langfuse/ClickHouse 互相独立、任一失败不影响业务）。个人玩家建议从三件套脚本起步，别一上来就 service 模式。
6. **评测口径刚起步**。目前公开基准只有 PersonaMem（48%→76%）；没有 LongMemEval/LoCoMo 类横评。好消息是内部的评测指标管道（抽取率、判重决策分布、分层延迟）已经在建设。
7. **生态绑定适中**。默认全本地 SQLite 可跑，但 TCVDB（腾讯云向量库）/COS/MongoDB 等云上能力构成迁移引力。

### 和 mem0 比呢？

源码笔记里有一句话总结得很准：**mem0 是"个人 Agent 的记忆层"，TencentDB Agent Memory 是"团队 Agent 的记忆资产治理平台"。** 前者轻、开箱即用；后者用 L0–L3 分层 + 四动作判重保持对话记忆新鲜度，再把 mem0 没有的 Skill（版本化）、Wiki（locked 硬约束 + 审计）、CodeGraph（影响分析）纳入同一套租户隔离、审计溯源和代理注入体系。代价是组件多、强 LLM 依赖。选型建议很清晰：**个人助手选 mem0 式轻方案；一支 Agent 团队要共享、审计、配装记忆资产时，才值得上这套。**

## 九、可以带走的设计模式

即使不用这个项目，下面几条也值得抄进你自己的 Agent 记忆设计：

1. **单次 LLM 调用做"场景切分 + 记忆抽取"**，以 previousSceneName 传递连续性——省调用，且记忆天然带场景标签。
2. **四动作判重（store/update/merge/skip）** 显式建模新旧记忆关系，merge 保留 timestamps 轨迹。
3. **locked 页硬约束**：人手工编辑的知识机器永不覆盖——人机共治的最小安全阀。
4. **分层注入缓存感知**：稳定进 system prompt（吃 KV-cache），易变 prepend user prompt，原始层下沉为工具——直接优化推理成本。
5. **把工具调用限额写进注入 prompt**（≤3 次/轮）——给"搜索成瘾"上物理刹车。
6. **技能即版本化资产**：FTS/向量双索引 + owner + 团队命名空间 + 不可变版本快照，把程序性记忆做成可治理配置项。
7. **round-level 回流 + fire-and-forget 写入**：对齐"一次真人提问"的语义边界，而不是 HTTP 边界。
8. **L0 sanitize 剥离注入标签**：切断"系统注入 → 被记住 → 再注入"的记忆反馈环。

## 十、结语：没有 Memory，Loop 只是更快地重复

官方 README 里有一句很好的话，值得作为这篇长文的结尾：

> **没有 Memory，Loop 可能只是更快地重复。能继承记忆，每一轮才有机会比上一轮更好。**

Agent Memory 这个领域远没有标准答案——分层怎么分、判重怎么判、注入怎么省、权限怎么管，每个团队都在摸石头。TencentDB Agent Memory 的价值在于它把这些问题的答案**做成了一个可部署、可治理、可审计的整体**，并且以 MIT 协议开源、默认本地零配置可跑。Roadmap 上的零配置冷启动、Skill 导出、更多框架接入（Codex 等）也值得持续关注。

如果你的团队里每个 Agent 都还在"每次从零学习你的项目"，给它一个读档的机会：

```bash
export ANTHROPIC_BASE_URL=http://127.0.0.1:8096/claude-code/default
export ANTHROPIC_AUTH_TOKEN='sk-mem-<your-key>'
claude --model <model>
```

---

**参考**：
- 官方仓库与文档：[TencentCloud/TencentDB-Agent-Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory)（`docs/00-项目总览.md` 至 `13-术语表.md`，v2.0.0，2026-08-11）
- 致谢项目：[codegraph](https://github.com/colbymchenry/codegraph)、[Hermes Agent](https://github.com/nousresearch/hermes-agent)、[Karpathy 的 LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- 源码深读笔记：A05-TencentDB-Agent-Memory.md（本文实现细节与批判视角的补充信源）
