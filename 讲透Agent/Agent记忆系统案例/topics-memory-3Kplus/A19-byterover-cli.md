# A-19 `campfirein/byterover-cli`（4.9K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\campfirein__byterover-cli
> TypeScript / v3.16.1，src 下 agent+server+tui+webui 四大块、目录 300+，测试目录与源码同构 / Elastic-2.0
> 一句话定位：把"项目知识"固化为 `.brv/context-tree/` Markdown 树、可通过 MCP/规则文件/skill 接线到 20+ 外部 Agent 的上下文记忆 CLI（命令名 `brv`）

## 1. 架构总览（目录地图，标出核心目录的职责）

- `src/agent/`：内嵌 LLM Agent（"cipher agent"）
  - `infra/memory/`：会话记忆 CRUD（memory-manager.ts）+ LLM 去重（memory-deduplicator.ts）
  - `infra/map/`：agentic map 管线——abstract-generator/queue、llm-map-service、有界缓冲 ContextTreeStore
  - `infra/session/`：SessionCompressor（会话→记忆抽取）、session-manager、chat-session
  - `infra/blob/`：文件型 blob 存储（FileBlobStorage，一 blob 一目录）
  - `infra/swarm/`：多 provider 记忆检索编排（byterover provider "context-tree (always on)"，swarm/status.ts:194）
- `src/server/`：常驻 daemon（TUI/WebUI 与 MCP 经 transport 与之通信）
  - `infra/context-tree/`：`.brv/context-tree/` 的写入/快照/归档/manifest/摘要传播/运行时信号
  - `infra/executor/`：curate-executor、query-executor（BM25 检索 5 级分层）、search-executor
  - `infra/dream/`：link/merge/prune/synthesize 四类记忆整理候选
  - `infra/mcp/`：对外 MCP server（brv-query/brv-curate 两个工具）
  - `infra/connectors/`：**跨 Agent 迁移核心**——rules/mcp/skill/hook 四类连接器 + 共享 patcher
  - `infra/cogit/` + `infra/vc/`：context-tree 的嵌套 git 语义版本控制（`brv vc`，push/pull 到 byterover.dev）
  - `infra/hub/`：知识包 registry（hub.byterover.dev/r/registry.json，environment.ts:48）
- `src/agent/resources/tools/`：Agent 工具的 prompt 文本（write_memory.txt、search_knowledge.txt、create_knowledge_topic.txt 等 30 个）
- `src/tui/`、`src/webui/`：Ink 终端前端与 React Web 前端
- 常量锚点：`BRV_DIR='.brv'`、`CONTEXT_TREE_DIR='context-tree'`（src/server/constants.ts:1,28）

## 2. 记忆机制深读

### 2.1 写入/抽取管线（谁触发、prompt、schema）

- 会话结束后由 `SessionCompressor.compress()` 抽取记忆，四步流程：
  1. 序列化会话消息为文本 digest（每条消息截 2000 字符，session-compressor.ts:281-293）
  2. LLM 抽取 5 类草稿记忆（temperature 0、maxTokens 1000）
  3. 取最近 60 条 agent 记忆做去重基准（`memoryManager.list({limit:60, source:'agent'})`，session-compressor.ts:116）
  4. 应用 CREATE/MERGE/SKIP 决策（session-compressor.ts:79-154）
- 抽取 prompt 固定 5 类，原文要点（session-compressor.ts:25-36）：
  - `PATTERNS`：可复用的代码/工作流模式
  - `PREFERENCES`：用户风格/命名/结构决策
  - `ENTITIES`：关键文件、模块、API、依赖
  - `DECISIONS`：架构选择（**永远抽取，即使已知——不可变日志**）
  - `SKILLS`：有效的工具调用配方
  - 约束：每类 0-3 条、单条 ≤200 字符
- DECISIONS 类豁免去重：deduplicator 与 fallback 路径都直接 CREATE（memory-deduplicator.ts:64-66；session-compressor.ts:216-218）——把架构决策当时间审计记录累积
- 去重由 LLM 单条判定，系统提示仅允许三种 JSON 输出（memory-deduplicator.ts:25-33）：
  - `{"action":"CREATE"}` / `{"action":"MERGE","targetId":...,"mergedContent":...}` / `{"action":"SKIP"}`
  - 温度 0、maxTokens 300、worker 并发 4（memory-deduplicator.ts:35, 97）
  - 解析失败 fail-open 为 CREATE（memory-deduplicator.ts:124-130）
- **curate 会话不走 LLM 抽取**：改用确定性 fallback 草稿——正则 `SOURCE_PATH_PATTERN` 提取 src/app/lib 路径、8 位指纹哈希、固定 6 条模板记忆（session-compressor.ts:156-199）；去重靠字符串归一化（PATTERNS/SKILLS 剥掉 "Session xxx:" 前缀后比对，session-compressor.ts:340-349）——省钱且可复现
- 主写入面 `brv curate`：外部 Agent 经 MCP 工具 `brv-curate` 或 CLI 触发，将知识写为 `.brv/context-tree/` 下的 Markdown topic 文件（检索面佐证：search_knowledge.txt:1；写入服务 file-context-tree-writer-service.ts:39）

### 2.2 存储后端与数据模型（文件布局，可移植格式的核心）

**双层存储**：

①会话记忆 = JSON blob：
- key 模式：`memory-{nanoid(12)}`，附件 `memory-{id}-{nanoid(8)}`（memory-manager.ts:123-129, 156）
- 落盘布局：`{storageDir}/blobs/{key}/content.bin + metadata.json`——一 blob 一目录、写临时文件+rename 原子写、单 blob 100MB / 总量 1GB 默认上限（file-blob-storage.ts:38-67）
- 记忆默认目录 `.byterover/cipher/memories`（core/domain/memory/types.ts:109）
- key 类型区分：附件 key 的后缀长度 ≠ 12，以此区分记忆与附件（`isMemoryKey` 用长度而非数中划线，因为 nanoid 本身可含 '-'，memory-manager.ts:570-580）

Memory schema（Zod 内嵌于实现，memory-manager.ts:29-69）：
```ts
content: string   // 1..10_000 字符（MAX_CONTENT_LENGTH=10k）
createdAt: number // Unix ms
id: string        // nanoid(12)
metadata?: {
  attachments?: [{blobKey, createdAt, name?, size, type}]  // blob 引用
  pinned?: boolean    // 是否自动加载
  source?: 'agent'|'system'|'user'
}  // passthrough 允许自定义字段（category 等即存在这里）
tags?: string[]   // ≤10 个、每个 ≤50 字符
updatedAt: number
```

②项目知识库 = context-tree：
- `.brv/context-tree/` 下的 Markdown 目录树（domain 子目录 + context.md 文件），**目录树本身即 schema**
- 摘要节点 YAML frontmatter（summary-frontmatter.ts:43-58）：
  - `type:'summary'`、`children_hash`（子节点一致性校验）、`covers[]`、`covers_token_total`
  - `condensation_order` / `summary_level`（d0/d1/... 分层摘要）、`compression_ratio`、`token_count`
- 归档而非删除：淘汰 topic 变为 `archive_stub`（`{evicted_at, evicted_importance, original_path, points_to}`），stub 仍进 BM25 索引（summary-frontmatter.ts:68-80；derived-artifact.ts:6）
- 渲染为 HTML topic（`.html` 后缀）+ index 生成器做确定性无 LLM 索引（index-generator.ts:4）

**跨机迁移**：
- context-tree 内嵌独立 `.git`（`brv vc` 语义版本控制，读取 `.brv/context-tree/.git/config` 判远端，read-context-tree-remote.ts:9-16）
- push/pull 走 `BRV_GIT_REMOTE_BASE_URL`（默认 byterover.dev，tui/lib/environment.ts:33）；旧 push/pull 命令已停用并指向 /vc（tui/utils/error-messages.ts:14）
- 共享知识源（knowledge source）只读挂载：检索结果带 `origin:'shared'|'local'` + `originContextTreeRoot`，本地结果轻微加权，共享树禁止 curate 写入（search_knowledge.txt:20-30；source-schema.ts:132-139 要求源项目同时有 `.brv/config.json` 和 `.brv/context-tree/`）

### 2.3 检索策略（BM25 分层，参数与阈值）

- 检索为 **MiniSearch BM25**（dream-session.ts:77-82 提到 MiniSearch 索引 TTL 5s 快路径），无向量嵌入
- 查询执行器 5 级降级（query-executor.ts:90-95）：
  - Tier 0：精确缓存命中（0ms）
  - Tier 1：Jaccard 相似度模糊缓存（~50ms）
  - Tier 2：纯 BM25 检索无 LLM（~100-200ms）
  - Tier 3：预取上下文的单次 LLM 调用（<5s）
  - Tier 4：完整 agentic 循环兜底（8-15s）
- 缓存参数：指纹缓存 TTL 30s（query-executor.ts:97）；tool-mode 默认 limit 10、上限 50，缓存按上限存、读取时切片（query-executor.ts:98-106）
- MCP `brv-query` 走 `query-tool-mode`：无 LLM、跳过 `canRespondDirectly` 置信门（"由调用方 Agent 决定结果是否有用"），瘦查询（totalFound<3）触发 `supplementEntitySearches` 补召回（query-executor.ts:133-138；brv-query-tool.ts:36-44）
- 复合排序分（memory-scoring.ts:73-79）：
  - `compoundScore = (0.6×BM25归一分 + 0.2×importance/100 + 0.2×recency) × tierBoost`
  - tierBoost：core 1.15 / validated 1.0 / draft 0.85（memory-scoring.ts:53-57）
- 查询结果渲染为 Markdown 段落（`## 标题 + rendered_md`），由调用方 Agent 自行综合（brv-query-tool.ts:155-169）

### 2.4 遗忘·整合·演化（FinMem 式信号 + dream 整理）

- RuntimeSignals 衰减（memory-scoring.ts:19-104）：
  - recency = exp(-days/30)（DECAY_RECENCY_FACTOR=30）
  - importance × 0.995^days（50 天不用约剩 78%）
  - 检索命中 +3、curate 更新 +5，封顶 100（ACCESS/UPDATE_IMPORTANCE_BONUS）
  - curate 更新同时 recency 重置为 1（memory-scoring.ts:170-177）
- 成熟度分层带**迟滞**（防抖动）（memory-scoring.ts:40-50, 119-142）：
  - draft→validated ≥65；validated→core ≥85
  - 降级：core→validated <60；validated→draft <35（升降阈值留 5-15 分缓冲带）
- MERGE 时信号合并：importance/recency 取 max、accessCount/updateCount 求和（memory-scoring.ts:189-202）
- `brv dream` 整理（dream-session.ts:33-119）：
  - 扫描全树并行生成 4 类候选：link（BM25 成对相似）、merge（更高阈值，merge-candidates.ts:4）、prune（低信号归档）、synthesize（跨主题综合）
  - 由调用 Agent 决策，败者路径移入 `.brv/archive/`（ARCHIVE_SUBDIR，dream-session.ts:37-38），支持 undo（dream-undo.ts）
  - 注释点名 FinMem 启发（memory-scoring.ts:1-2："FinMem-inspired memory scoring engine"）
- Agent 内 map 处理的有界缓冲（context-tree-store.ts:4-17）：
  - 热路径 store() 同步、零 LLM：超 τ_hard 驱逐最旧一半条目为确定性截断摘要，循环直至达标
  - 冷路径 compact() 一次性跑 LLM 3 级摘要（普通→激进→确定性截断，context-tree-store.ts:121-143）
  - 摘要预算默认 2000 token、压缩轮上限 10（context-tree-store.ts:39-44）

### 2.5 注入上下文的方式（跨 Agent 迁移机制，本仓最大特色）

**rules 连接器**（RULES_CONNECTOR_CONFIGS，rules-connector-config.ts:21-110，共 22 个 Agent）：

| Agent | filePath | writeMode |
|---|---|---|
| Claude Code / OpenClaude | CLAUDE.md | append |
| Codex / Amp / OpenCode | AGENTS.md | append |
| Cursor | .cursor/rules/agent-context.mdc | overwrite |
| Gemini CLI | GEMINI.md | append |
| Github Copilot | .github/copilot-instructions.md | append |
| Windsurf / Cline / Kiro / Roo / Qoder / Kilo | 各自 .xxx/rules/agent-context.md | overwrite |
| Warp / Qwen / Trae / Junie / Zed / Antigravity / Auggie / Augment | WARP.md / QWEN.md / project_rules.md / ... | append 或 overwrite |

- **幂等托管块**：注入内容包在 `<!-- BEGIN BYTEROVER RULES --> ... <!-- END BYTEROVER RULES -->` 内（constants.ts:10-13）；重复安装原位替换（保边界换行、不累积空行）、卸载干净移除并修复接缝（rule-segment-patcher.ts:198-236, 288-298）
- 共享文件归属消歧：AGENTS.md 被 Amp/Codex/OpenCode 共用，靠 footer `Generated by ByteRover CLI for X` 识别归属（constants.ts:4, 42-62）
- `hasByteroverBlock` 支持逐字节比对，陈旧内容视为缺失并触发修复（rule-segment-patcher.ts:238-258）
- **mcp 连接器**：向各 Agent 配置注入 MCP server 条目——JSON/TOML/YAML 三种写入器（json-mcp-config-writer.ts / toml-mcp-config-writer.ts / yaml-mcp-config-writer.ts）+ Claude Desktop 专用配置路径解析（claude-desktop-config-path.ts）
- **skill 连接器**：向 Claude Code 等安装 SKILL.md/WORKFLOWS.md 技能包（skill-connector.ts 16.5KB、skill-connector-config.ts），autonomous agent 的 always-loaded 启动文件（如 OpenClaw 的 AGENTS.md）写入 BYTEROVER 块（autonomous-agent-attachments.ts:70, 90）
- **hook 连接器**：注入生命周期 hook（hook-connector.ts + hook-connector-config.ts）
- 旧安装升级：sentinel 锚点补丁（如给已装文件插 `brv curate view` 用法行，每 patcher 自查 sentinel、失败静默跳过，rule-segment-patcher.ts:104-196, 305-332）
- token 预算：注入的是"如何用 brv-query/brv-curate 检索/写回"的说明（几十行），记忆本体按需检索——上下文常驻占用极小
- `.byterover`/`.brv` 均进文件系统服务的 blockedPaths 防止 agent 误写自身记忆（file-system-service.ts:164, 195）

## 3. 关键代码摘录

```ts
// src/server/infra/connectors/rules/rules-connector-config.ts:21-52（节选，共 22 个 Agent）
export const RULES_CONNECTOR_CONFIGS = {
  Amp:            { filePath: 'AGENTS.md', writeMode: 'append' },
  Antigravity:    { filePath: '.agent/rules/agent-context.md', writeMode: 'overwrite' },
  'Claude Code':  { filePath: 'CLAUDE.md', writeMode: 'append' },
  Codex:          { filePath: 'AGENTS.md', writeMode: 'append' },
  Cursor:         { filePath: '.cursor/rules/agent-context.mdc', writeMode: 'overwrite' },
  'Gemini CLI':   { filePath: 'GEMINI.md', writeMode: 'append' },
  'Github Copilot': { filePath: '.github/copilot-instructions.md', writeMode: 'append' },
  OpenCode:       { filePath: 'AGENTS.md', writeMode: 'append' },
  // ... Windsurf/Kiro/Roo/Warp/Qwen/Zed/Junie/Trae/Cline 等
} as const satisfies Partial<Record<Agent, RulesConnectorConfig>>
```

```ts
// src/server/core/domain/knowledge/memory-scoring.ts:73-79（复合评分）
export function compoundScore(bm25Normalized: number, signals: RuntimeSignals): number {
  const normalizedImportance = Math.min(signals.importance, 100) / 100
  const base = W_RELEVANCE * bm25Normalized + W_IMPORTANCE * normalizedImportance + W_RECENCY * signals.recency
  const boost = TIER_BOOST[signals.maturity] ?? TIER_BOOST.draft
  return base * boost   // 0.6 / 0.2 / 0.2 + core 1.15 / validated 1.0 / draft 0.85
}
```

```ts
// src/agent/infra/session/session-compressor.ts:25-36（抽取 prompt，5 类固定分类）
const SYSTEM_PROMPT = `You are a session memory extractor for ByteRover, a code intelligence tool.
Extract reusable memories from the conversation in exactly these 5 categories:
- PATTERNS: reusable code or workflow patterns discovered
- PREFERENCES: user style/naming/structure decisions
- ENTITIES: key files, modules, APIs, dependencies discovered
- DECISIONS: architectural choices (always extract, even if already known — immutable log)
- SKILLS: tool invocation recipes that worked
...
Extract 0-3 memories per category. Skip categories with nothing new. Be concise (max 200 chars per memory).`
```

```ts
// src/agent/infra/memory/memory-manager.ts:570-580（key 类型判定：长度而非分隔符）
private isMemoryKey(key: string): boolean {
  if (!key.startsWith(MemoryManager.MEMORY_KEY_PREFIX)) return false
  // Memory keys have format: memory-{id} where id is a fixed-length nanoid(12).
  // Attachment keys append an extra suffix: memory-{id}-{suffix}.
  // A valid memory id may itself contain '-', so counting dashes is incorrect.
  const suffix = key.slice(MemoryManager.MEMORY_KEY_PREFIX.length)
  return suffix.length === MemoryManager.MEMORY_ID_LENGTH
}
```

```ts
// src/server/infra/connectors/shared/rule-segment-patcher.ts:211-213（幂等替换托管块）
const nextContent = currentBlock
  ? existing.slice(0, currentBlock.start) + stripTrailingNewlines(blockContent) + existing.slice(currentBlock.end)
  : appendManagedBlock(existing, normalizeManagedBlock(blockContent))
```

## 4. 基准/评测声明（反虚荣视角）

- README:46-63：两个长程对话记忆基准
  - LoCoMo 96.1% overall（1,982 questions / 272 docs）
  - LongMemEval-S 92.8% overall（500 questions / 23,867 docs）
  - 口径：LLM-as-Judge accuracy（%），分 category 图表见 assets/images/benchmarks/
  - 论文：arXiv:2604.01599（README:63）
- 定性：[自封]——数字出自厂商自己的论文，无第三方复现；但 README:48 明确声明"all benchmarks run using the production byterover-cli codebase, no separate research prototype"，且 paper/ 目录在仓库内，可复现性中等
- deepwiki 首页称"memory architecture validated against industry-standard benchmarks"——与 README 同源 [deepwiki-未验证，实际即上述自封数字]
- deepwiki 关于"distributed system on local machine / UI 响应性"的叙述与本地结构相符（server daemon + transport client 分离，mcp-server.ts 依赖 brv-transport-client）[已核实：brv-query-tool.ts:74-85 的 waitForConnectedClient]

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量）

1. **记忆即纯 Markdown 文件树**：知识存为 Markdown + YAML frontmatter（children_hash 增量校验），任何编辑器/工具可读可 diff 可 git——比 mem0 的 SQLite/向量库底座更防供应商锁定；摘要与子节点的一致性靠 hash 而非外键
2. **标记块幂等注入全套**：唯一属主注释对（BEGIN/END）+ footer 归属消歧 + 逐字节陈旧检测 + 接缝修复——"多工具共写同一配置文件"问题的完整解法，mem0 无此机制
3. **DECISIONS 不可变追加**：分类别差异化去重策略（DECISIONS 永不 MERGE/SKIP），把架构决策当日志审计
4. **检索零 LLM 依赖降级链**（Tier0-4 + 薄查询补充召回）：MCP 工具返回原文让调用方 Agent 综合，避免"检索器里再套一个 LLM"的成本与延迟
5. FinMem 式 importance/recency 双衰减 + 迟滞分层 + tier boost 全部为纯函数（无副作用、易测试、易迁移到任何存储）
6. 长文处理的有界缓冲两路模式：热路径确定性截断（永不阻塞）、冷路径 LLM 摘要只跑一次

## 6. 局限与风险

- 会话记忆 `list()` 全量加载后内存过滤排序（memory-manager.ts:440-478），无索引；记忆上千条后每次去重都要读全部 blob
- 去重 LLM 只看既有记忆前 300 字符（memory-deduplicator.ts:83），长记忆的 MERGE 判定可能失真；fail-open=CREATE 有膨胀风险（DECISIONS 尤甚）
- 纯 BM25 无向量检索：同义改写查询召回弱（官方用 supplementEntitySearches 打补丁，query-executor.ts:138）
- rules append 模式依赖标记块纪律：用户手工删掉 END 标记会使注入内容泄漏为"用户内容"，hasMcpToolsInBrvSection 只在标记内检查（constants.ts:35-39）
- 概念面庞杂：curate/query/dream/vc/swarm/space/hub/cogit 多套子系统，`.brv`（项目级）与 `.byterover`（agent 级）双目录体系，学习曲线陡
- Elastic-2.0 许可（非 OSI）对商业化集成有约束

## 7. 一句话对比 mem0

mem0 是"抽取-去重-更新"的记忆 API 服务；byterover 把记忆做成**纯 Markdown 知识树 + 嵌套 git 同步 + 标记块注入**，重心不在记忆算法而在记忆的**可移植性与多 Agent 接线**——检索用 BM25 分层而非向量，演化用 FinMem 信号 + dream 整理而非 LLM 全量重写。
