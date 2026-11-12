# A-09 `NevaMind-AI/memU`（14.3K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\NevaMind-AI__memU
> Python / MIT ｜ 一句话定位："个人记忆存成 Wiki"——把 Claude Code/Codex/Cursor 等编码 Agent 的会话轨迹经"自进化"桥接管线蒸馏成 markdown 记忆/技能文件，跨会话/跨 Agent/跨设备共享同一记忆库。

## 1. 架构总览（目录地图，标出核心目录的职责）

```
src/memu/
├── app/                    # 核心服务：settings.py（全部配置）、service.py、agentic.py（检索/提交）
├── database/               # 三后端：inmemory / sqlite / postgres（含 pgvector），repo 模式统一
│   └── models.py           # Resource / RecallFile / RecallFileSegment + scope 混入
├── embedding/              # 独立嵌入包：openai/jina/voyage/doubao/openrouter 后端（ADR 0005）
├── hosts/                  # 8 个宿主适配器（claude_code/codex/cursor/openclaw/hermes/cola/workbuddy/generic）
│   ├── retrieval.py        # 注入缝：retrieve 命令（所有 host 共享一次实现）
│   ├── instruction.py      # 常驻系统指令模板（managed block 注入 host 配置）
│   ├── templates.py        # 自更新模板：server→cache→embedded 三级回退
│   └── bridging/           # 记录缝：prepare→(agent 自进化)→commit 管线
├── cloud.py                # 云后端客户端（api.memu.so/api/v4/memory）
├── vector.py               # 后端无关 cosine_topk（numpy argpartition）
└── events.py               # 客户端事件上报（ADR 0016）
docs/adr/                   # 16 篇 ADR，设计决策全公开
```

双缝设计（ADR 0008）：*Record*（各 host 自有会话日志格式）与 *Inject*（统一 retrieve 命令）分离（src/memu/hosts/retrieval.py:1-15）。

## 2. 记忆机制深读（本笔记核心，每个论断必须钉 `相对路径:行号`）

### 2.1 写入/抽取管线（谁触发、prompt 是什么、结构化 schema）

数据流总览：

```
宿主会话日志 ──prepare──> sessions/*.jsonl（切片）
                        ├─> jobs/NN-memory-job.txt ─┐
云端库镜像 ────────────> ~/.memu/memory|skill/     │ agent 自进化（三选一）
                        └─> jobs/NN-skill-job.txt ──┘（读转写→patch/create/no-op）
agent 写的 markdown ──commit──> diff_tracked → commit_results
                            ├─> RecallFile（file 级 name:desc 嵌入）
                            └─> RecallFileSegment（行级/skill 元数据级嵌入）
检索（每 turn hook）: query → progressive_retrieve → segments→files(roll-up)+resources
```

- **抽取者是宿主 Agent 自己，不是 SDK**：桥接管线三步 `prepare -> (the agent self-evolves) -> commit`，中间步"是真正的 agent 工作——读转写、做判断、写 markdown"（src/memu/hosts/bridging/pipeline.py:1-9）。`MemoryService` 不做任何 LLM 调用，只存储/嵌入/检索（README.md:96）。
- `prepare`：切片新会话转写（跳过桥接自身的会话防自我 mined，#606/ADR 0015，pipeline.py:43-64），镜像云端记忆库到 `~/.memu/memory|skill/`（pipeline.py:80-100），生成编号 job 指令文件（每会话一个 memory-job + 一个 skill-job，pipeline.py:114-135）。
- 抽取 prompt 全文内嵌（关键决策三选一）：**a) 什么都不做（no-op 是合法结果，"do not invent a memory to justify the run"）/ b) patch 既有文件（合并重写）/ c) 新建文件**；文件头 front-matter `name/description`（src/memu/hosts/bridging/instructions.py:17-69 memory 模板、:71-130 skill 模板）。skill 模板额外要求记录会话触碰过的文件（resource_log，instructions.py:128-130）。
- `commit`：diff 追踪目录→读取变更文件→`commit_results` 直写存储（无再加工，pipeline.py:139-156）；**状态只在成功后推进**（cursor/snapshot 于 commit 而非 prepare 提升，崩溃=有界重做而非静默丢失，pipeline.py:142-148）。
- 资源轨闭环：skill job 的第 4 步把会话触碰过的文件追加进 `.resource.tmp` 日志（instructions.py:128-130）；下次 prepare 生成 resource-job 让 agent 用 verify_command 验证存活后写描述进 `resources.md`（templates.py:64 占位符契约；layout.py:102-109），最终 commit 为 Resource 记录（caption 嵌入，agentic.py:286-296）。
- 任务编号约定：每会话两个 job（memory=2i-1，skill=2i），resource job 固定排在 2N+1（pipeline.py:130-135 的 `job_index=2*num_sessions+1`）——保证 agent 按依赖顺序执行。
- 结构化 schema：`RecallFile{name, track("memory"/"skill"), description, content}` + `RecallFileSegment{recall_file_id, track, text, embedding}`（src/memu/database/models.py:29-56）；skill 文件单一 segment（name+description），memory 文件按内容行切片（跳过空行与 `#` 标题，去重保序，src/memu/app/agentic.py:359-376）。

### 2.2 存储后端与数据模型（含"跨 Agent 归属/隔离"模型——本仓特别要求）
- **scope 是一等数据字段**（ADR 0003）：用 Pydantic 多继承把可配置 `UserConfig.model` 混入 Resource/RecallFile/RecallFileSegment 三个核心模型，字段冲突即报错（src/memu/database/models.py:62-95）；默认 scope 模型 `DefaultUserModel{user_id, agent_id}`（src/memu/app/settings.py:96-99）。
- **跨 Agent 个人记忆的实现**：`user_id` 是记忆主人、`agent_id` 是可选过滤维度——同一 user_id 下 agent_id 为 None 的行对所有 Agent可见，带 agent_id 的行按 Agent隔离；仓储写时带 `user_data`、读时带 `where` 过滤，API 的 where 先校验再执行（docs/adr/0003-user-scope-in-data-model.md:14-18）。云端版明确只支持 `user_id`/`agent_id` 精确过滤（src/memu/cloud.py:17-18,42-46）。
- 隔离的物理实现是**行级过滤而非分库分表**：in-memory 后端 `matches_where` 逐字段相等/`__in` 匹配（src/memu/database/inmemory/repositories/filter.py:7-29）；检索时 `where_filters` 传入每层查询（src/memu/app/agentic.py:109,147-151,206）。
- **文件夹式组织（确实存在，两层）**：(1) 本地镜像 `~/.memu/memory/`、`~/.memu/skill/` 目录树，track→子目录映射 `TRACK_DIRS={"memory","skill"}`（src/memu/hosts/bridging/layout.py:16）；文件名即 kebab-case 记忆名，agent 直接用 bash 读写。(2) 逻辑层 RecallFile 按 `(track, name)` 键唯一、keyset 分页按 `(track, name, id)` 排序遍历（ADR 0014，src/memu/app/agentic.py:67-83）。
- 后端矩阵：metadata_store ∈ {inmemory, sqlite, postgres}，vector_index ∈ {bruteforce, pgvector, none}，postgres 自动配 pgvector（src/memu/app/settings.py:146-168）；或整库换云后端（cloud.py）。

### 2.3 检索策略（向量/关键词/混合/重排/图，参数与阈值）
- 唯一检索路径 `progressive_retrieve`：**单发、无 LLM**——查询嵌入一次，segment 与 resource 两层各按余弦排序（src/memu/app/agentic.py:85-128 docstring 明言"no intention routing, sufficiency checks, or summarization"）。
- 三层结构：segments top_k 检索（默认 file.top_k=5，resource.top_k=5，settings.py:72-77）→ files 层不做独立检索，只按 segment 命中**回卷（roll-up）**，文件分=其 segment 最高分（agentic.py:159-188）→ resources 仅 `track="workspace"` 资源按 caption 嵌入检索（agentic.py:190-211）。
- 向量计算：numpy 矩阵化余弦 + argpartition O(n) top-k（src/memu/vector.py:42-61）——纯暴力扫描，无 ANN；pgvector 后端才走索引。
- 无关键词层、无重排、无图；检索按 track 过滤可用 `track__in`（agentic.py:148-150）。

### 2.4 遗忘·整合·演化（有无 decay/merge/re-rank/自更新）
- **演化=agent 决策的 patch/create/no-op 三选一**（instructions.py:40-56）：合并、分叉、丢弃全由 agent 判断，"A no-op is a perfectly good outcome"是反记忆膨胀的显式设计。
- segment 级增量调和：commit 时对新切片做 drop-and-add 差分——消失的文本删 segment、只对新文本嵌入，未变行保留原嵌入（agentic.py:378-409）；resource 更新=按 url 删旧建新（agentic.py:281-284）。
- 文件级更新触发条件克制：description 不变则不重嵌文件向量，只换 content（agentic.py:341-348）。
- 无 decay/时间衰减；无自动去重（依赖 agent patch 语义）。防自指回路：桥接自身会话不进入记忆（layout.py:86-92 self_sessions 按 host 隔离）。

### 2.5 注入上下文的方式（系统提示拼装、token 预算）
- 常驻指令（managed block 注入 host 系统配置，`<!-- memu:begin -->` 标记）：教 agent 在需要时**主动调用** `{binary} retrieve "<query>"`，且可改写查询词（src/memu/hosts/instruction.py:45-54）。
- retrieve 输出面向 agent 塑形：files 层**去 content 换 path**（返回可打开的镜像文件路径而非全文），segments 用 `source_file=<track>/<name>` 溯源，无法映射时才内联全文（src/memu/hosts/retrieval.py:59-117）——"位置+摘要"而非"整篇注入"，token 成本转嫁给按需 cat。
- 每轮 hook 只花一次检索 + 一次事件 POST（ADR 0016，retrieval.py:120-126）；**无显式 token 预算**，靠 top_k=5 与"位置+摘要"形态天然限流。
- 指令模板自更新：server（memu.pro/sdk/instructions）→last-good cache→embedded 三级回退，fail-open 永不抛错（src/memu/hosts/templates.py:1-36,174-181），模板需保持占位符契约否则拒用（templates.py:88-104）。

### 2.6 调度、事件与嵌入网关（补充）
- 调度窗口：桥接任务按 host 的调度窗口运行（src/memu/hosts/scheduling/windows.py + prompt.py），生成给 agent 的定时任务提示——记忆抽取是"后台批处理"而非每 turn 代价。
- 事件上报（ADR 0016）：所有操作记 `memory_list/memory_search_*/agent_error_reported` 等事件，spool 蓄积+单次 POST 交付，检索失败事件只 spool 不阻塞（src/memu/hosts/retrieval.py:130-151）；查询文本刻意不采集（retrieval.py:126 "counts only"）。
- 嵌入网关（ADR 0005）：独立 `memu.embedding` 包，gateway 统一分发到 openai/jina/voyage/doubao/openrouter 后端（src/memu/embedding/backends/），SDK 与 httpx 双客户端（client_backend 配置，settings.py:37-44），代理旁路挂载（embedding/http_client.py 的 proxy_bypass_mounts，cloud.py:10 引用）。
- 云后端：`CloudMemoryClient` 实现与本地 Mixin 相同的三个操作（list_all_recall_files/progressive_retrieve/commit_results，src/memu/cloud.py:94-140），重试覆盖 408/429/5xx（cloud.py:16），认证用项目 API key（MEMU_CLOUD_API_KEY，cloud.py:34-35）——"本地三后端 or 云"通过 `build_agentic_memory_backend_from_env`（src/memu/env.py）按环境变量切换，接口完全同构。
- 泛化 host：generic 适配器带 detect.py 自动探测宿主（src/memu/hosts/generic/detect.py），新 agent 无需专属适配器即可接入（ADR 0011）。
- 三条独立记忆线（ADR 0007）：wiki（memory 文件）/ graph（关系）/ 第三线在代码中体现为 track 字段扩展（"memory"/"skill"/"workspace" 三值分别由 RecallFile.track 与 Resource.track 承载，models.py:26,33,54）；skill 线"永远由描述合成、不从抽取的 skill 型记忆条目派生"（ADR 0004:30-33）。
- 常驻指令的安装形态：managed block 标记 `<!-- memu:begin -->` 包裹（instruction.py:45），宿主升级重装时幂等替换；另有 `memu-retrieve` SKILL.md 两句指针版（instruction.py:48-49,71-73）供技能目录型宿主使用。

## 3. 关键代码摘录（≤5 段，每段 ≤30 行，带行号）

**摘录 1：scope 混入——跨 Agent 隔离的数据模型基础（src/memu/database/models.py:62-75）**
```python
def merge_scope_model(user_model, core_model, *, name_suffix):
    overlap = set(user_model.model_fields) & set(core_model.model_fields)
    if overlap:
        raise TypeError(f"Scope fields conflict with core model fields: {sorted(overlap)}")
    return type(
        f"{user_model.__name__}{core_model.__name__}{name_suffix}",
        (user_model, core_model),
        {"model_config": ConfigDict(extra="allow")},
    )
```

**摘录 2：抽取三选一决策（src/memu/hosts/bridging/instructions.py:42-56 节选）**
```
a. **Do nothing.** ... A no-op is a perfectly good outcome — do not invent
   a memory to justify the run.
b. **Patch existing memory file(s).** ... Rewrite that file in place with
   the merged content.
c. **Create a new memory file.** ... Write a new file.
```

**摘录 3：files 层 roll-up 评分（src/memu/app/agentic.py:174-187）**
```python
file_scores: dict[str, float] = {}
for seg_id, score in segment_hits:
    seg = segment_pool.get(seg_id)
    if seg is None:
        continue
    fid = seg.recall_file_id
    ...
    if fid not in file_scores or score > file_scores[fid]:
        file_scores[fid] = score
file_hits = sorted(file_scores.items(), key=lambda kv: kv[1], reverse=True)
```

**摘录 4：segment 差分调和（src/memu/app/agentic.py:398-408）**
```python
for seg in existing:
    if seg.text not in new_set:
        store.recall_file_segment_repo.delete_segment(seg.id)

to_add = [text for text in new_texts if text not in existing_texts]
if not to_add:
    return
vecs, _ = await embed_client.embed(to_add)
```

**摘录 5：注入输出"位置而非全文"（src/memu/hosts/retrieval.py:93-106 节选）**
```python
subdir = TRACK_DIRS.get(track or "")
if subdir is not None and name:
    out_path = write_recall_file(base, subdir, {...})
    file["path"] = str(out_path)
else:
    file["content"] = content   # 无镜像位置才内联，绝不悬挂死路径
```

## 4. 基准/评测声明（反虚荣视角）
- README 无任何精度/延迟基准数字，仅功能矩阵（哪些 host 支持 Memorize/Retrieve，README.md:35-71）。[无声明]——反而在 ADR 0016 自建事件遥测（检索成败/时延/结果计数，retrieval.py:160-169）收集真实使用数据。
- 仓库测试较全（tests/ 30+ 文件，覆盖 bridging 提升、self_sessions、segment 去重、调度窗口等），工程可信度高。
- ADR 0016 §4 区分"检索异常"与"检索静默空结果"两种失效并分别上报（retrieval.py:130-135 注释）——把记忆系统的"沉默失效"当一等观测对象，是少见的自觉。
- "跨 Agent/跨设备"声明（README.md:7-9,23）由 scope 模型+云后端支撑，本地模式隔离仅到行级过滤，无 ACL/加密。
- 嵌入模型默认 OpenAI text-embedding-3-small（settings.py:29-31）：换 provider 需重嵌全库，无版本化向量/混合维度支持（embedding profile 机制仅选后端，settings.py:109-135）。

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量，区别于 mem0 已有结论）
1. **agent-as-extractor（SDK 零 LLM）**：记忆抽取交回宿主 agent 自己做（job 指令文件+no-op 合法化），SDK 只做存储/嵌入/检索（pipeline.py:1-9；README.md:96）——抽取成本转嫁给已付费的 agent 会话，且判断质量随宿主模型升级，是相对 mem0/Memori（SDK 内置或云端抽取）的结构性差异。
2. **scope 编译期混入**：`merge_scope_model` 用动态类型合成把租户字段焊进记录模型（models.py:62-75），隔离语义后端无关（ADR 0003:24-26）——比在查询层拼 where 字符串更不易漏。
3. **"位置+摘要"注入**：检索返回可打开的文件路径而非全文（retrieval.py:93-106），token 控制从"预算裁剪"变成"按需拉取"——对文件系统原生 agent（Claude Code 等）是零成本模式。
4. **两阶段游标提交**：pending/promoted 双 manifest，状态只在 commit 成功后推进（layout.py:50-65；pipeline.py:142-148）——记忆管线崩溃恢复的简洁范本。
5. **自更新指令模板三级回退**（server→cache→embedded，占位符契约校验，templates.py:88-104,174-181）：让"教 agent 怎么用记忆"的提示词本身可热修且离线安全。
6. **文件行级 segment 差分嵌入**（agentic.py:378-409）：markdown 记忆文件更新时只对增量行付费嵌入。
7. **记忆双轨 memory/skill + 资源第三轨**：稳定事实（memory）、可复用工作流（skill）、被触碰文件的描述索引（resource/workspace track）三类记忆各有专属抽取模板与切片策略（skill=单 segment 元数据、memory=按行、resource=caption 嵌入，agentic.py:359-376,286-295）——比单一"事实"抽象更贴编码 agent 场景。
8. **bridge 自会话免疫**：桥接管线运行产生的会话被显式排除在记忆挖掘之外（ADR 0015；layout.py:86-92），防止"记忆系统在记忆自己做记忆"的递归污染。

## 6. 局限与风险（失败模式、安全隐患、工程债）
- 检索纯暴力余弦（vector.py:42-61；默认 inmemory+bruteforce，settings.py:147,153）：记忆量大时每 turn hook 全量扫描，无 ANN 兜底（除非上 postgres/pgvector）。
- 行级 where 过滤是"软隔离"：后端配错或 where 漏传即跨用户泄漏（filter.py:7-29 无强制作用域注入）；无 ACL、无加密。
- 记忆质量完全押注宿主 agent 的三选一判断：弱模型会漏抽或滥建文件，无 SDK 侧质检/去重兜底；"last write wins when patching"（instructions.py:60-61）并发写同文件会互相覆盖。
- 抽取模板与检索指令从 memu.pro 远程拉取（templates.py:48,78）——供应链/提示注入面：恶意或被劫持的模板服务器可改写所有安装实例的 agent 行为（虽有占位符校验但无签名验证）；可用 `MEMU_TEMPLATE_BASE_URL=""` 关闭（templates.py:78-79）。
- 遥测默认上报（events.py，retrieval 每 turn 一次 POST；查询文本不记录 retrieval.py:126，但仍含 host/时延/计数）。
- 8 个 host 适配器的会话解析各自维护（hosts/*/sessions.py），宿主升级易碎（README.md:66 已见 Windows HERMES_HOME 兼容注记）。
- 资源描述质量无校验：resources.md 由 agent 按 RESOURCE_JOB 模板标注（模板要求占位符 `verify_command/resource_file`，templates.py:64），verify 命令只截取前 N 条 touched 路径（pipeline.py:105-108 注释），路径超量时静默丢弃。
- postgres 迁移链只有单一 initial_schema 版本（src/memu/database/postgres/migrations/versions/20260703_0001_initial_schema.py），schema 演进机制尚年轻；sqlite schema 手写（database/sqlite/schema.py）与 postgres 模型（postgres/models.py）双份维护，有漂移风险。
- 调度依赖宿主 agent 的 cron/task 机制（hosts/scheduling/），宿主不跑定时任务则记忆永不更新——静默失效模式。

## 7. 一句话对比 mem0
mem0 用自带 LLM 管线把对话提炼成事实并做 ADD/UPDATE/DELETE 决策；memU 反其道行之——SDK 完全不做 LLM 工作，把"读会话、判断值不值得记、怎么合并"交还给 agent 本人，自己只提供带 scope 隔离的"markdown 记忆文件系统 + 暴力向量检索"，成就了最轻的跨 Agent 个人记忆共享方案。
