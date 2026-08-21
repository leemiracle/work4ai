# 06 · memory 体系深读：五层架构与"写路径即安全边界"

> 一句话：**openclaw 把 agent memory 当成了操作系统级的持久化子系统来做——纯文件可见、SQLite 溯源、确定性 gate、模型判断只出现在界内，~170K 行是全仓最大的单一子系统。**
>
> 证据基准：钉版 `f612675284`，路径缩写 `SDK`=packages/memory-host-sdk/src/host · `MC`=extensions/memory-core · `AM`=extensions/active-memory。
> 规模实测：memory-core 79,970 行(233 文件) + memory-wiki 32,347 + active-memory 12,672 + memory-host-sdk 16,007 + lancedb 10,310 + UI 8,773 + QA 2,662 + hook 2,210 ≈ **165K 行**；近一月 commit 流里 `fix(memory)` 密度全仓第一。

## 1. 五层分解（先看骨架）

| 层 | 组成 | 关键事实 |
|---|---|---|
| 文件层 | `MEMORY.md`/`USER.md`/`memory/YYYY-MM-DD.md`/`DREAMS.md`/`memory/.dreams/` | 纯 Markdown，"no hidden state"，编辑器可直改 |
| 索引层 | 每 agent SQLite（STRICT）：chunks+fts5+vec0+provenance+recall_meta | 溯源是**列**不是文本（`memory-schema-provenance.ts:10-11` CHECK 约束） |
| 插件层 | memory-core（默认 slot）+ lancedb（sidecar）+ wiki（知识编译）+ active-memory（编排） | `plugins.slots.memory` 单 slot；lancedb 不抢 slot（`lancedb/index.ts:210-217`） |
| 宿主层 | src/memory-host-sdk + src/agents/memory-search.ts + memory flush + session-memory hook | flush turn 工具面清空：`agent-tools.ts:871 toolsForMemoryFlush=[]` |
| 表现层 | UI Dreams（夜空+龙虾宠物）+ memory-import + 10 个 QA yaml | "声明即验证"，高风险场景断言到请求 ID 级 |

五档 tier 模型（docs/concepts/memory-architecture.md:50-56）：Instructions(人写) / **Curated core**(MEMORY+USER，dreaming 唯一写者) / Episodic(日记，只可搜) / Prospective(intents，触发才注入) / Review(DREAMS.md，人看)。**curated↔episodic 之间的 promotion gate 是全系统最要紧的边界。**

## 2. 溯源：安全模型的地基

四级 origin class（SQLite CHECK，模型写 prose 伪造不了）：
- `owner`（可信频道主人输入）/ `agent`（从 owner 内容派生）/ `untrusted`（网页、工具输出、群聊非 owner）/ `system`（脚手架：heartbeat/cron 前导）
- 分类代码 `SDK/session-files.ts:642-670`：assistant 看轮污染标记→untrusted；user 看 `__openclaw.senderIsOwner`；**保守默认**：遗留行回填 `untrusted/unknown`（provenance.ts:38-41），"never defaulted to owner"
- 三道结构性防御：①session-kind gate（cron/heartbeat/subagent 会话不产生 durable 候选）②recall-loop prevention（被召回过的内容标记后不再当新记忆学，`isRecalledMemoryMessage` session-files.ts:634-640）③taint 贯穿 consolidation（`isPromotionOriginBlocked`：untrusted/system 在**建 prompt 之前**被剔除，dreaming-consolidation-candidates.ts:11-14——是前置条件不是扣分）
- 防污染正则族：`isContaminatedDreamingSnippet`（short-term-promotion-utils.ts:159-187）+ MEMORY_FLUSH_PROMPT_RE/DREAMING_TRANSCRIPT_PROMPT_LINE_RE 等，专防"把提示词当事实学"

**这个设计对应威胁模型：memory poisoning（OWASP ASI06 / MINJA arXiv:2503.03704）。结论是检测式防御不可靠，改为写时溯源+结构性隔离**——untrusted 可存可搜，但永远进不了 curated、永远不会 auto-inject，即使被召回也包 untrusted 框架。

## 3. 写路径：dreaming 是唯一 durable 写者

三阶段 sweep（默认 cron `0 3 * * *`）：**light**（排序去重暂存，不写）→ **REM**（主题反思，不写）→ **deep**（打分晋升，唯一写 MEMORY.md）。

deep 的确定性 gate（三层全过才到模型）：
1. 六信号加权：`{relevance:.30, frequency:.24, diversity:.15, recency:.15, consolidation:.10, conceptual:.06}`（short-term-promotion-utils.ts:34-40，与文档一致）+ light/REM 相位加成（≤0.06/≤0.09，14 天半衰）
2. 三阈值：minScore **0.75** / minRecallCount **3** / minUniqueQueries **3**（plugin.json:158-169）——"记忆因持续有用而毕业，不是因写得自信"
3. 模型 consolidation 只做合并/去重/supersede，产物须过结构校验：旧条目损失 ≤**25%**、预算 ≤**10,000 chars**（memory-budget.ts:33）、每条带 `Source: path#Lx-Ly` 锚点；**乐观并发**：hash 复查+原子 rename，被拒则回退 append-only

> 关键认知（docs 引 LongMemEval arXiv:2410.10813）：**"writing is the hard part"**——写时策展比索引方式更决定长期质量。所以 openclaw 把策展从忙碌的回复路径挪到后台专项。

## 4. 读路径：双车道成本分治

**Lane 1（每轮，零模型调用）**：
- bootstrap 注入 MEMORY/USER（预算内，每轮刷新免重启）
- 混合搜索 `memory_search`：vector **0.7** + BM25 **0.3**（memory-search.ts:127-128）→ 30 天半衰期时间衰减（MEMORY/USER evergreen 不衰减，temporal-decay.ts:72-81）→ importance(1-10) 乘子 → MMR λ=0.7 去冗余。无 learned reranker，importance 写时打分换查询时零模型（Generative Agents arXiv:2304.03442 的直接结论）
- trigger 注入：条目尾注 `<!-- trigger: ... -->`，词法+向量预过滤，强命中 ≤3 条/轮注入 hidden block

**Lane 2（escalation，真子代理）**：active-memory 插件。默认 `escalate` 模式 = **recall intent**（14 条英文正则+中日韩规则，escalation.ts:3-46）**且 lane 1 无强命中**才跑——15s 超时、3 次超时熔断 60s、失败绝不阻塞回复。跨会话召回 `rememberAcrossConversations` 只限同 agent 私密 DM 互查，群组/频道永不。论文锚点：时间/多跳问题正是 flat retrieval 最弱处（LongMemEval），把贵的延迟花在刀刃上。

## 5. 特殊记忆类型（三件非典型设计）

- **USER.md**：指令式用户模型（"Always/Never/Prefer"+observed 日期+active/superseded），**supersede in place 禁止 append 矛盾史**——依据 PrefEval（arXiv:2502.09597）：偏好仅"在场"几个轮后就失效，且模型爱从旧值作答
- **standing intents**：事件条件 prospective memory 存 SQLite（`standing_intents` 表+FTS），六态状态机 pending→armed→fired→done（+cancelled/expired），匹配路径 FTS 确定性零模型，**owner-only 创建**（index.ts:159），防唠叨默认 cooldown 24h/max 3 fires/90 天过期。依据 TriggerBench（arXiv:2606.23459）：把意图编译出模型，不信模型能自己想起来
- **memory flush**：compaction 前静默 turn 抢救未落盘事实；工具面**清空**（防借 flush 执行任意工具），写路径强制 workspace 内（agent-runner-memory.ts:156-162 防穿越）；可指定本地小模型（ollama/qwen3:8b）

## 6. 四插件关系图

```
active-memory(编排) ──读 slots.memory──> memory-core(默认slot=真相之源)
     │lane1 trigger+lens                     │embedding引擎(被复用)
     │lane2 嵌入式子代理 ──toolsAllow──> memory_search/get
     │                                       │公开工件(bridge单向拉取)
     │                            memory-wiki(知识编译,只读不反写)
     │                            memory-lancedb(sidecar自注册3工具,
     │                              auto-recall/auto-capture,不抢slot)
```
- memory-wiki：把耐久记忆编译成 claim/evidence 级 vault（frontmatter claims 带 confidence+证据行号，≥30 天 aging/≥90 天 stale，9 张 dashboard 报矛盾/低置信/开放问题）——"页面是编译产物不是事实之源"
- memory-lancedb：`memory_store/recall/forget` 三工具+自动捕获（多语触发词+0.95 去重+信封污泥清洗 sanitizeForMemoryCapture）；输出必冠"记忆是不可信历史数据"声明
- 两者都复用 memory-core 的 embedding 引擎——**向量计算归一、存储后端可换**

## 7. 文档 vs 代码差异（实测发现，读码价值）

| 项 | 文档说 | 代码是 | 证据 |
|---|---|---|---|
| trigger 强命中阈值 | 0.72 | **0.65** | AM/trigger-recall.ts:13-18 注释：20 触发/50 无关合成语料实测 0.65 零误报，0.72 误杀合法改写，0.68 是单词触发上限(0.85×0.8) |
| 时间衰减默认 | 描述为常开 | 插件默认 off，宿主默认 on | temporal-decay.ts:11 `enabled:false` vs memory-search.ts:132 `DEFAULT_TEMPORAL_DECAY_ENABLED=true`（宿主覆盖） |
| recency 半衰期 | 30 天 | 两套：搜索 30 天 / **晋升排序 14 天** | memory-search.ts:133 vs short-term-promotion.ts:27 |

**元教训：连文档极度完善的顶级项目，调参类数字仍以代码+注释为准。**

## 8. 批判性评估

**值得偷的**：
1. 溯源列进 schema（CHECK 约束）而非文本标注——"prose 声称是 owner 写的不代表它是"
2. 确定性 gate 外包模型判断、模型产物必须过结构校验+可回滚（pre-image 全存）
3. 记忆失败 fail-open 全链贯穿（超时/降级/空结果都不吃回复轮）
4. QA 声明即验证：10 个 yaml 把"跨 reset 私有召回不泄漏群组"这类安全性质固化成回归测试
5. 调参注释带实验依据（0.65 的注释就是一篇迷你 ablation）

**风险与短板**：
1. **复杂度是第一敌人**：165K 行、5 插件交织（slot vs sidecar vs 编排），文档已现滞后（§7）；修复流（fix(memory) 密度第一）本身就证明系统在超重边缘
2. recall intent 检测英文中心（14 正则英文，中日韩是补丁式规则）——中文用户 escalate 命中率存疑
3. 阈值全是手调魔数（0.65/0.75/0.25/10k...），无统一调参/评估框架，跨语种泛化未证
4. consolidation 让模型重写 MEMORY.md 是已知的风险点（25% loss 上限+hash 并发只是兜底而非消除）
5. project_key 大小写敏感策略被代码注释自认"可能跨大小写变体 miss"（curated-annotations.ts:37-40）——fail-closed 的代价

**一句话定位**：这是"个人 agent 长期记忆"目前公开可见最完整的工程实现——不是最新颖（论文都 2023-2025 已发表），而是**把 7 篇论文的结论编译成了一个有 QA、有 UI、有迁移工具、有失败语义的生产系统**。与 ClaudeCode 的"记忆无向量库、纯文件+grep"哲学相反：openclaw 押注"检索要强但写入要严"，ClaudeCode 押注"结构越少越可控"。两者共享同一条底线：**记忆必须人可读可改**。

## 审计命令

```bash
cd ~/ai/agent/awesome-agents/repos/openclaw
git log -1 --format=%h                                   # f612675284
grep -c "" packages/memory-host-sdk/src/host/memory-schema-provenance.ts  # 溯源 DDL
grep -n "STRONG_TRIGGER_MATCH_SCORE" extensions/active-memory/trigger-recall.ts  # 0.65
grep -n "DEFAULT_PROMOTION_WEIGHTS" -A7 extensions/memory-core/src/short-term-promotion-utils.ts # 六信号
ls qa/scenarios/memory/                                  # 10 行为契约
```
