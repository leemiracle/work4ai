# A-03 `supermemoryai/supermemory`（28.9K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\supermemoryai__supermemory
> TypeScript（305 .ts + 305 .tsx）+ 42 .py ｜ Apache-2.0（LICENSE）｜ 一句话定位：**记忆引擎的商业封装仓库**——引擎本体（抽取/图/混合检索）不在本仓库，这里只有 MCP 服务、Web 控制台、SDK 适配层与 API 契约

## 0. 最重要的甄别结论（先说破）
**"local 运行路径"的引擎源码不在本仓库。** 逐项证据：
- 全仓 305 个 .ts 文件中无任何检索/嵌入/图引擎实现；无 .go/.rs 文件（全盘 Glob 验证）。
- MCP 服务的所有记忆操作都是 `https://api.supermemory.ai` 的远程调用：`SupermemoryClient` 构造器默认 `apiUrl = "https://api.supermemory.ai"`（apps/mcp/src/server/client/index.ts:175），search 直接转发 `this.client.search.memories(...)`（client/index.ts:279-285）。
- "Supermemory local"（`npx supermemory local` → `supermemory-server`，端口 6767，README.md:321-341）是**install 脚本分发的预编译二进制**；docs 自述 "it's [open source](https://git.new/memory)"（apps/docs/self-hosting/overview.mdx:21）——短链指向的源码仓库不在本 monorepo。
- 因此本篇对"检索/上下文引擎核心"的深读只能落在**API 契约（zod schema 即引擎行为规格）+ MCP 注入层 + 官方架构文档**三层，均钉行号；引擎内部实现 [不可审计-本仓库]。
- 复核路径（供后续验证）：① `Get-ChildItem -Recurse -Include *.go,*.rs` 为空；② `git grep -l "api.supermemory.ai" -- "*.ts"` 命中 client/index.ts:175 等远程调用点；③ `Select-String "git.new/memory" apps/docs/self-hosting/overview.mdx` 确认引擎源码短链外置。

## 1. 架构总览（目录地图）
```
supermemoryai__supermemory/          # Bun + Turborepo monorepo
├── apps/
│   ├── mcp/               # ⭐ MCP 服务器（Cloudflare Workers + Hono + Durable Objects）
│   │   ├── src/server/    # server.ts(装配) auth/(OAuth+RBAC) client/(API客户端) tools/(15工具) prompts/(context注入)
│   │   ├── e2e/           # 对生产环境的端到端测试（auth/graph/memory/space-scope/widget）
│   │   └── widget/        # MCP 内嵌 UI 组件（save 表单 studio 等）
│   ├── web/               # Next.js 消费者控制台（brain/onboarding/integrations/oauth/slack）
│   ├── browser-extension / raycast-extension / memory-graph-playground / docs(122 .mdx)
├── packages/
│   ├── validation/api.ts  # ⭐ 1523 行 zod + OpenAPI 注解 = 托管 API 的机器可读契约
│   ├── tools/src/         # mastra / openai / vercel(ai-sdk) / voltagent 框架适配器
│   ├── openai-sdk-python / pipecat-sdk-python / cartesia-sdk-python  # Python 侧 SDK
│   ├── memory-graph/      # 记忆关系图可视化组件（React，@supermemory/memory-graph 0.2.3）
│   └── lib/               # 共享 types / auth / similarity 工具
└── skills/supermemory/    # Agent skill（SKILL.md + references/architecture.md 引擎设计文档）
```
MCP 工具面共 15 个（apps/mcp/src/server/tools/index.ts:19-35 逐一注册）：search-memory / list-documents / get-document / list-memories / list-container-tags / who-am-i / select-space / set-active-tag / memory-graph / fetch-graph-data / add-memory / guided-save / save-memory / upload-file / prepare-file-upload——对照 README.md:157-161 宣传的三个面向 AI 的能力 `memory`（存/忘）/`recall`（检索+画像）/`context`（注入画像）。

## 2. 记忆机制深读（以契约与注入层还原引擎行为）

### 2.1 写入/抽取管线（契约还原）
- 写入异步：MCP `add_memory` → `client.add()` 立即返回 `{status: "queued"}`（client/index.ts:189-206），抽取在服务端队列完成。
- MCP 写工具分两级：`add_memory`（用户给出最终内容直接存）与 `guided-save`（打开人审表单，工具描述明确分流条件 "If the user provides the exact content... use add_memory instead"，tools/guided-save.ts:14）；另有 `save-memory`/`prepare-file-upload`/`upload-file` 文件通道（tools/index.ts:19-35）。
- 服务端六阶段管线见官方架构文档 skills/supermemory/references/architecture.md:37-155：Queued → Extracting（PDF/OCR/音频转写，:49-68）→ Chunking（按内容类型分策略：文档按语义节、代码按 AST 边界走独立开源库 code-chunk 见 apps/docs/concepts/super-rag.mdx:108、网页去导航后按文章结构，:89-130）→ Embedding → **Indexing 阶段建知识图**（Updates/Extends/Derives 三类关系，architecture.md:118-153）→ Done。
- 双摄取路径：`taskType: "memory"`（默认，抽事实+建图）vs `taskType: "superrag"`（纯 RAG，跳过事实抽取与图链接，apps/docs/concepts/super-rag.mdx:32-85）——一个 API 承载"记忆"与"文档检索"两种产品形态。
- 图式版本链（契约钉版）：memory entry 含 `version/isLatest/isForgotten/isStatic/isInference/history[].parentMemoryId/rootMemoryId`（apps/mcp/src/server/client/index.ts:37-64）；文档示例 "User prefers Vue(v1)→React(v2)→React+TS(v3, isLatest)"（architecture.md:186-201）。检索可按需取"最新版/全历史/指定版本"（architecture.md:197-201）。
- 框架适配层模式（packages/tools/）：以 voltagent 为例，`withSupermemory()` 包装函数把 agent config 注入存/取 hooks（packages/tools/src/voltagent/index.ts:30-60），apiKey/baseUrl 从 env 回退（:43-44）——所有适配器（mastra/openai/ai-sdk）同构，接入面统一为 `client.add/search/profile` 三原语。
- Python SDK 三件套（openai-sdk-python/pipecat-sdk-python/cartesia-sdk-python，各含 src/tests）：分别包装 OpenAI Agents SDK、Pipecat 语音框架、Cartesia 语音栈——语音 agent 是其重点渠道之一。
- **遗忘的两级降级**（MCP 客户端逻辑）：先精确匹配 `memories.forget({content})`，404 则以 `SIMILARITY_THRESHOLD = 0.85` 搜索相似记忆再按 id 删（client/index.ts:208-267）——把"模糊遗忘"做在客户端。

### 2.2 存储后端与数据模型
- 引擎存储 [不可审计-本仓库]。可观测面：local 模式数据全部落 `./.supermemory` 单目录（README.md:347），图引擎嵌入式、无外部数据库（overview.mdx:26）；local 默认嵌入 `Xenova/bge-base-en-v1.5`（768 维，本地推理免 key，configuration.mdx:72-74），摄取受 RAM 上限约束（默认 1GB，`SUPERMEMORY_EMBEDDING_RAM_LIMIT`，configuration.mdx:96-114）。
- local 二进制的可配置面（configuration.mdx 全表钉版）：`PORT/SUPERMEMORY_PORT`（默认 6767，:16）、`SUPERMEMORY_DATA_DIR`（默认 `./.supermemory`，:17）、嵌入 provider 切换 `SUPERMEMORY_EMBEDDING_PROVIDER`（local/openai/gemini/兼容端点，:72）、本地嵌入 worker 池 `SUPERMEMORY_LOCAL_EMBEDDING_POOL_SIZE`（默认 1，:83）、摄取并发 `SUPERMEMORY_INGEST_CONCURRENCY`（默认 2，:110）、跳过预热 `SUPERMEMORY_SKIP_EMBEDDING_PREWARM`（:87）；API key 写 `~/.supermemory/env`（:10）。**"产品面全在环境变量里"是二进制分发模式的典型工程形态**。
- 平台 vs self-host 差异表（overview.mdx:63-73）：记忆抽取 self-host 用"你自己的模型/你的 key"，平台用 "proprietary long-horizon models — higher quality, cheaper at scale"（:71）——官方承认**开源(二进制)路径抽取质量是降级档**；connectors 与 MCP 仅平台提供（:69-70）。
- 多租户键：`containerTag`（= space/project 标识）贯穿所有 API；MCP 侧默认 `sm_project_default`（client/index.ts:18）。

### 2.3 检索策略（从 API 契约反推）
`Searchv4RequestSchema`（packages/validation/api.ts:470-558）暴露引擎旋钮：
- `threshold` 默认 **0.6**（api.ts:476-493），语义为敏感度（越高越严格）；
- `rerank` 布尔开关（api.ts:548-552）；`rewriteQuery` 查询改写开关，**明码标价 +400ms 延迟**（api.ts:553-557）；
- `include: {documents/summaries/relatedMemories}`（api.ts:513-523）——检索可顺带返回图邻居（relatedMemories）；
- v3 文档检索有 `chunkThreshold`/`documentThreshold` 双层阈值（api.ts:351-399）与 `onlyMatchingChunks`：**默认 false = 返回命中 chunk 的前后邻接 chunk**（api.ts:448-452），与 mempalace 的源内邻居扩展（A02 §2.3-4）异曲同工，但前者在服务端默认开启；
- 复杂过滤 DSL：`{AND:[{key,value,negate},{filterType:"numeric",numericOperator:">",...}]}`（api.ts:400-418）。
- MCP `search_memory` 固定 `searchMode: "hybrid"`（client/index.ts:283）——记忆事实与文档 chunk 同查询混合。检索融合权重/算法 [不可审计]。
- searchMode 三态语义（apps/docs/concepts/super-rag.mdx:82-85 + README.md:280-281）：`"memories"`（只搜抽取事实）/"documents"（只搜文档 chunk）/"hybrid"（两者融合）；纯 superrag 摄入的内容只对 documents/hybrid 可见，**不会**被 memory 路径检索召回（super-rag.mdx:82-85）。
- v4 检索响应结构（api.ts:560-569）：chunks 带 content/similarity，文档与记忆可同响应返回；`include.relatedMemories` 打开图邻居扩展（api.ts:517）。
- 快速上手口径（README.md:309-315 API 表）：`client.add()` 存（text/conversations/URLs/HTML）、`client.search()` 混合检索、`client.documents.uploadFile()` 文件通道、`client.settings.update()` 调抽取/分块行为——**分块策略是服务端租户级设置而非每次调用参数**。

### 2.4 遗忘·整合·演化
- 演化即图：`Updates` 关系链接新旧版本，检索默认只回 `isLatest`（architecture.md:197-201）；矛盾解决由引擎 "tracks updates, resolves contradictions, auto-forgets expired info"（README.md:393-394）[自述，不可验证]。
- `isStatic`（长期事实）/`isInference`（推断事实）两类标记（client/index.ts:57-58）进入 profile 生成：static facts → 静态画像，dynamic → 近期上下文（architecture.md:291-315）。
- `isForgotten` 软删除标记（client/index.ts:46,56）+ 版本历史 `history[].parentMemoryId/rootMemoryId`（client/index.ts:43-44）——遗忘是图状态迁移而非物理删除，可审计轨迹在客户端类型层即可见。
- 图关系三类只出现在索引阶段（Updates/Extends/Derives，architecture.md:145-153）：Derives 示例为多条记忆归纳出推断结论（"User is an ML engineer/researcher"），说明**推断型记忆（isInference）是图遍历的产物**而非独立抽取。

### 2.5 注入上下文方式（本仓库真正的代码核心）
- **`context` MCP prompt**（apps/mcp/src/server/prompts/context.ts:15-115）：并发拉 profile + spaces（:29-32），拼装为一条 user 消息：Active space 头 + `Stable Context`/`Recent Context` 各限 **8 条事实**（`CONTEXT_FACT_LIMIT = 8`，:12）+ 最近 3 个其他 space（`RECENT_SPACE_LIMIT = 3`，:13）+ 隔离提示语（:86）。README.md:295 宣称 profile 调用 ~50ms。
- `search_memory` 输出拼装（apps/mcp/src/server/tools/search-memory.ts:35-74）：Profile（static+dynamic 事实列表）→ `## Matching memories`（每条带 `[NN%]` 相似度徽标，:70）——profile 与检索结果**同响应合并**，对应平台 `client.profile({q})` 的"画像+检索一次调用"设计（client/index.ts:297-332）。
- 画像双通道模型：`profile.static`（由 `isStatic` 长期事实聚合）/ `profile.dynamic`（近期上下文），README.md:289-293 给出对照示例；架构文档说明 profile 由记忆动态生成并短 TTL 缓存（architecture.md:291-315, :368）。
- MCP 服务端装配（apps/mcp/src/server/server.ts:63-102）：每 actor（bearer token）一个 `SupermemoryClient` 实例 + Durable Object 存 active space + 预生成 upload token 会话——**会话状态（当前 space）服务端化**，客户端无需每次传参。

### 2.6 API 层与鉴权设计（补充专列）
- 传输/发现：Cloudflare Workers + Hono（apps/mcp/src/server/index.ts:13-43），CORS 白名单含 claude.ai/chatgpt.com/gemini.google.com 等内置客户端域名（index.ts:25-41）；`/.well-known/oauth-protected-resource` 暴露 RFC 9728 元数据、授权服务器指向平台 `/api/auth`（index.ts:57-72），`/.well-known/oauth-authorization-server` 反向代理平台元数据（index.ts:88-104）。
- RBAC（apps/mcp/src/server/auth/rbac.ts:4-36）：会话 `accessType === "restricted"` 时非成员 space 降为 read；`scope.type === "scoped"` 时按 scope.tags 收敛——**权限计算在网关、每工具调用前过滤可写 tag 列表**（guided-save.ts:31-36 只暴露 write 权限 space）。
- 部署面：wrangler.jsonc 绑定自定义域 `supermemory.ai` zone + Durable Object `SupermemoryMCP`（apps/mcp/wrangler.jsonc name/main/compatibility 节）。
- e2e 行为钉版（apps/mcp/e2e/memory.test.ts:30-113）：save→recall 往返、includeProfile 双段输出、无命中优雅降级、**抽取未完成时 forget 仍可受理**（:68，对应异步队列的最终一致性）、containerTag 隔离（:85）、参数校验错误（:113）。

## 3. 关键代码摘录
摘录①（检索契约旋钮，packages/validation/api.ts:548-557）：
```typescript
rerank: z.boolean().optional().default(false)...
rewriteQuery: z.boolean().optional().default(false).openapi({
  description: "If true, rewrites the query ... This increases the latency by about 400ms",
```
摘录②（邻居 chunk 默认含上下文，api.ts:448-452）：
```typescript
onlyMatchingChunks: z.boolean().optional().default(true)...
// "Normally, we send the previous and next chunk to provide more context for LLMs."
```
摘录③（两级遗忘，apps/mcp/src/server/client/index.ts:227-232）：
```typescript
const SIMILARITY_THRESHOLD = 0.85
const searchResult = await this.search(content, 5, SIMILARITY_THRESHOLD, this.containerTag)
```摘录④（RBAC 收敛写权限，apps/mcp/src/server/auth/rbac.ts:22-36）：restricted 会话非成员降 read；scoped 会话只读（effectiveContainerTagAccess）。

摘录⑤（上下文注入限额，prompts/context.ts:12-13）：
```typescript
const CONTEXT_FACT_LIMIT = 8
const RECENT_SPACE_LIMIT = 3
```

### 补充：周边件深读要点
- **memory-graph**（packages/memory-graph/，@supermemory/memory-graph 0.2.3）：React 关系图组件"visualize and explore your memory connections"（package.json description），src/canvas、components、hooks、utils 分层 + mock-data——纯展示件，图数据来自 MCP 工具 `fetch-graph-data`/`memory-graph`（apps/mcp/src/server/tools/），印证"图在服务端、仓库只有视图"。
- **web 控制台**（apps/web/）：Next.js App Router，路由含 brain（记忆浏览）、onboarding、integrations、oauth/consent、org/invite、slack/link、upgrade-mcp——付费/组织/集成等 SaaS 骨架齐全；app/api 侧仅 3 个轻路由（emails/og/onboarding），主数据流全部直连平台 API。
- **skills/supermemory/references/architecture.md**（引擎设计的最详细公开文本，368+ 行）：六阶段管线（:37-155）、Updates/Extends/Derives 图关系（:118-153）、static/dynamic 记忆与版本链（:170-201）、chunk 相似度示例（:220）、profile 生成与短 TTL 缓存（:291-368）——**读引擎设计先读此文件**，但注意它是营销性技术文档，无代码对应。
- **packages/docs-test**：TS/Python 双侧 SDK 冒烟测试（tests/typescript、tests/python，含 ai-sdk/claude-memory/openai-sdk 集成用例），保证 SDK 与平台契约不漂移——"契约在 validation、漂移检测在 docs-test"的分层测试观。
- 中文 README（README.zh-CN.md）与插件矩阵（openclaw/claude/opencode 等独立仓库，README.md:132-135）显示其渠道策略：主仓聚合入口、各编辑器插件分仓维护。
- MCP widget（apps/mcp/src/widget/）：save 表单的 studio/views/components 分层（App.tsx 为入口），由 MCP `_meta` 携带 viewId 关联（guided-save.ts:38-49）——MCP UI 扩展（App-embedded tools）的先行实现样本。

## 4. 基准/评测声明（反虚荣视角）
- README.md:356-364："#1 on LongMemEval / LoCoMo / ConvoMo"，附 "95% Recall@15 while adding only ~720 tokens — 99.4% context reduction" —— **[自封][不可复现-本仓库]**：数字指向 supermemory.ai/research，仓库内无评测脚本、无结果文件（对照 mempalace 全套入库）。分类 recall：Knowledge Updates 99% / Assistant 100% / User 97% / Multi-session 93% / Temporal 91% / Preference 90%（README.md:364）。
- SMFS（Supermemory Filesystem）声明：xAFS 110 题上 Claude 省 3.0× token（24M vs 72M）、Codex 省 1.75×（README.md:366）——[自封]，write-up 在站外。
- MemoryBench 号称 "open-source framework"（README.md:368-372）但代码不在本仓 [自封]；其 CLI 形态 `-p supermemory -b longmemeval -j gpt-4o` 显示以自家为默认被测方。
- 交叉证据（竞品侧）：mempalace 的对比表将 "Supermemory ASMR" 标为 "~99% QA accuracy, not R@5, Experimental, Ensemble of Gemini 2.0 Flash/GPT-4o-mini"（MemPalace benchmarks/BENCHMARKS.md:73）——即第三方视角下其旗舰数字是 QA 口径+实验性+模型集成，与 R@5 类指标不可比。
- 本仓库的 e2e 测试（apps/mcp/e2e/memory.test.ts:30-113）只钉行为（save→recall 往返、containerTag 隔离、参数校验），不测检索质量。

## 5. 可借鉴模式（API 层设计增量）
- **zod+OpenAPI 注解即 API 规格**（packages/validation/api.ts）：1523 行单文件把每个旋钮的取值域、默认值、延迟代价写进 schema 描述——引擎黑盒时"契约即文档"的做法值得抄。
- **MCP 三层注入设计**：tool（search_memory 带画像）/ prompt（context 常驻注入）/ widget（guided-save 人审表单，tools/guided-save.ts:8-55）——把"存前确认"做成 MCP UI 组件而非纯文本往返。
- **状态化 MCP**：Durable Objects 存 active space（apps/mcp/src/server/space-state.ts）+ OAuth protected-resource 元数据自动发现（apps/mcp/src/server/index.ts:57-72）——多租户 MCP 部署范式。
- **客户端模糊遗忘**：exact→0.85 相似度回退两级协议（client/index.ts:208-267），简单但把语义删除的成本留在网关层。
- **写入分流的产品化描述**：`guided-save` 工具 description 本身就是一篇微 prompt，教会 agent 判断何时直接存、何时开表单人审（tools/guided-save.ts:14）——工具描述即行为契约，值得所有 MCP 工具作者借鉴。
- **画像/检索一跳合并**：`client.profile({q})` 单调用同时返回 static/dynamic 画像与检索结果（client/index.ts:297-332），MCP 层直接拼成单响应——对 agent 而言少一次往返且注入格式统一。
- 错误码产品化：402 → "Memory limit reached. Upgrade at supermemory.ai"（client/index.ts:489-490），付费墙内嵌客户端；`x-sm-source` 头全链路标注来源渠道（client/index.ts:183）便于归因。

## 6. 局限与风险
- **开源与营销的错位**：28.9K 星的仓库是"壳仓"——核心引擎（图构建、混合检索、profile 生成）不可审计，self-host 用户运行的是不透明二进制（curl | bash 安装，README.md:326）；"it's open source" 的链接是短链 git.new/memory（overview.mdx:21），源码不在本 monorepo，审计路径不透明。
- 双轨质量暗示：官方差异表承认 self-host 抽取用"你的模型"、平台用专有模型（overview.mdx:71）——self-host 用户的基准数字未必能复现 README 宣称（README 数字未注明跑在哪一轨）。
- 检索质量声明全部 [自封]；与 mem0/mempalace 的对比表由竞品（mempalace BENCHMARKS.md:70-78）标注为 "~99% QA accuracy, not R@5, Experimental"——口径混用且非自证。
- API v3/v4 并存（SearchRequestSchema api.ts:339 vs Searchv4RequestSchema api.ts:470），契约内留有 `// TODO: Improve filter schema`（api.ts:250）与 deprecated 字段（categoriesFilter api.ts:340-350）等技术债。
- MCP 客户端 30s 超时（FETCH_TIMEOUT_MS，client/index.ts:19）+ 单结果 200K 字符截断（MAX_CHARS，client/index.ts:17,111-113）——长文档场景静默截断风险。
- e2e 依赖生产环境与真实账号（apps/mcp/e2e/helpers.ts），CI 价值有限；e2e 目录与 src 平级的 vitest 单测（auth/index.test.ts、space.test.ts 等）覆盖面集中在协议层。
- 隐私面：MCP 服务器将 query 与内容转发至 api.supermemory.ai（client/index.ts:175,279），"local fully offline" 仅在自跑 supermemory-server 二进制时成立（overview.mdx:33-44）——使用者需明确区分"开源 MCP 客户端"与"本地引擎"两种部署形态的隐私边界。

## 7. 一句话对比 mem0
mem0 把引擎全部开源、检索端只是三信号线性加权；supermemory 反其道——引擎闭源商业化、把"图式版本链+画像+混合检索"包装成 50ms 的一跳 API，开源的只是接入层（MCP/SDK/契约）——两者恰好构成"记忆系统开源程度光谱"的两个极端，mempalace（引擎开源+检索极简）站在中间。

## 附：三仓横向速览（本系列结论）
| 维度 | mem0 | mempalace | supermemory |
|---|---|---|---|
| 引擎开源 | 全开源（Python 可读） | 全开源（Python 可读） | 二进制/托管，仓库只有接入层 |
| 抽取 | LLM ADD-only（写入端重） | 零 LLM，正则 closet（写入端轻） | 服务端专有模型（不可见） |
| 检索 | semantic+BM25+entity 线性融合 | 向量+closet秩次boost+源内grep | hybrid 模式+rerank/rewriteQuery 旋钮（黑盒） |
| 基准 | LoCoMo 92.5 [自封] | LME R@5 96.6 [自封-可复现] | "#1 三榜" [自封-不可复现] |
| 注入 | 调用方自理 | 4 层 wake-up（~900 tok 常驻） | context prompt 8+8 事实（~50ms） |

（附注：本篇 §2 各小节的"契约钉版"均以 packages/validation/api.ts 与 apps/mcp 源码为锚；引擎内部行为引用自 skills/supermemory/references/architecture.md 官方文档，属设计声明而非实现证据，引用时均已标注。）
