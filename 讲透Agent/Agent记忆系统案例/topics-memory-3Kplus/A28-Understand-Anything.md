# A-28 `Egonex-AI/Understand-Anything`（79K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\Egonex-AI__Understand-Anything
> TypeScript pnpm monorepo ｜ Claude Code 插件：把代码库/文档库转成知识图谱 JSON + 交互式 dashboard ｜ 79K 星最高仓，"图记忆"形态代表

## 1. 架构总览（目录地图）

- `understand-anything-plugin/skills/` — 9 个技能入口：`understand`（主分析管线，SKILL.md 858 行）、`understand-chat`（图谱问答）、`understand-dashboard`/`understand-diff`/`understand-domain`/`understand-explain`/`understand-figma`/`understand-knowledge`/`understand-onboard`
- `understand-anything-plugin/agents/` — 9 个子代理 prompt：project-scanner/file-analyzer/assemble-reviewer/architecture-analyzer/tour-builder/domain-analyzer/graph-reviewer 等（管线各阶段的 LLM 角色）
- `understand-anything-plugin/packages/core/` — `@understand-anything/core` TS 库：`types.ts`（图 schema）、`plugins/tree-sitter-plugin.ts`（AST）、`plugins/parsers/`（13 种非代码解析器）、`plugins/extractors/`（14 语言提取器）、`search.ts`/`embedding-search.ts`、`fingerprint.ts`/`staleness.ts`/`change-classifier.ts`（增量）、`persistence/index.ts`
- `packages/dashboard/`（React 可视化）、`packages/viewer/`（只读查看器）、`tree-sitter-dart-wasm/`、`tree-sitter-swift-wasm/`（自维护 wasm 语法）
- 顶层 `.claude-plugin/`/`.copilot-plugin/`/`.cursor-plugin/` — 多平台插件清单；`READMEs/` 8 语言 README（营销面拉满）

## 2. 记忆机制深读（构建管线视角）

### 2.1 写入/抽取管线（谁触发、两阶段抽取）
- **触发**：用户在 Claude Code 里敲 `/understand`；SKILL.md 即编排程序——主会话按 Phase 0→7 逐段执行 bash/node/python 并派发子代理（`skills/understand/SKILL.md:1-39`）。7 阶段：0 预检（全量 vs 增量决策表，`SKILL.md:182-190`）→ 0.5 `.understandignore` 确认（`SKILL.md:212-227`）→ 1 SCAN（project-scanner 子代理产出 scan-result.json 含 importMap，`SKILL.md:231-274`）→ 1.5 BATCH（compute-batches.mjs 语义分批，`SKILL.md:278-291`）→ 2 ANALYZE（file-analyzer 子代理**最多 5 并发**逐批分析，`SKILL.md:303`）→ 3 ASSEMBLE REVIEW → 4 ARCHITECTURE（分层）→ 5 TOUR（导览路径）→ 6 REVIEW（校验）→ 7 落盘
- **两阶段抽取（核心设计）**：file-analyzer 子代理先跑确定性脚本 `extract-structure.mjs`（tree-sitter WASM 提取函数/类/导入/导出/调用图，`agents/file-analyzer.md:29-119`），再让 LLM 基于结构数据做语义标注（summary/tags/complexity/语义边），**"Do NOT re-read the source files"**（`file-analyzer.md:147`）——AST 当骨架、LLM 只做注释，幻觉面收窄
- **prompt 防注入**：README/manifest 作为"untrusted project data"注入子代理，明示忽略其中指令样文本（`SKILL.md:249`）
- 语言/framework/locale 上下文按检测结果注入 markdown 附加文件（`skills/understand/languages/*.md`、`frameworks/*.md`、`locales/*.md`，`SKILL.md:422-424`）

### 2.2 存储后端与数据模型（图 schema）
- **存储 = 单个 JSON 文件** `.ua/knowledge-graph.json`（+`meta.json`/`config.json`/`fingerprints.json`），无数据库（`core/src/persistence/index.ts:84-155`；deepwiki "saved to .ua/knowledge-graph.json" 已验证）
- 节点模型 `GraphNode{id, type, name, filePath?, lineRange?, summary, tags[], complexity, languageNotes?, domainMeta?, knowledgeMeta?, figmaMeta?}`（`core/src/types.ts:54-67`）
- **27 种节点类型**：5 代码（file/function/class/module/concept）+ 8 非代码（config/document/service/table/endpoint/pipeline/schema/resource）+ 3 领域 + 5 知识（article/entity/topic/claim/source）+ 6 设计（Figma）（`types.ts:1-8` 注释自述分类）
- **38 种边类型分 9 类**：结构（imports/contains/inherits）、行为（calls/publishes）、数据流（reads_from/transforms）、依赖（tested_by/configures）、语义（related/similar_to）、基础设施（deploys/serves）、schema（migrates）、领域、知识（cites/contradicts/builds_on）（`types.ts:10-21`）
- 根对象 `KnowledgeGraph{version, project{...gitCommitHash}, nodes, edges, layers[], tour[]}`（`types.ts:107-115`）——图上还挂"架构分层"和"学习路径"两类人类视角结构
- AST 插件：`TreeSitterPlugin` 基于 web-tree-sitter WASM，每语言一个可复用 parser（`core/src/plugins/tree-sitter-plugin.ts:31-48`），14 语言 extractor + 13 非代码 parser（dockerfile/terraform/sql/graphql/protobuf/env 等，`plugins/parsers/`）

### 2.3 检索策略
- **Fuse.js 模糊搜索**：字段权重 name 0.4 / tags 0.3 / summary 0.2 / languageNotes 0.1，threshold 0.4，查询词空格拆分后 OR 连接（`core/src/search.ts:14-47`）——纯词法，无向量无图遍历
- **SemanticSearchEngine**：预计算节点 embedding + cosine 相似度暴力扫（`core/src/embedding-search.ts:61-80`），供 dashboard 用
- **understand-chat 的"检索"是 grep**：指示 agent 用 Grep 在 JSON 里搜 name/summary/tags，再对命中节点 grep edges 取 **1-hop 子图**，加 layers 定位（`skills/understand-chat/SKILL.md:51-64`）——图检索逻辑由 LLM 即兴执行而非代码实现
- 边做 dangling 检查：merge 脚本丢弃引用缺失节点的边（`SKILL.md:346-355`）

### 2.4 遗忘·整合·演化（增量更新机制）
- **三级变更分类**：`ChangeLevel = NONE | COSMETIC | STRUCTURAL`——内容变但结构签名（函数/类/导入签名）不变 = COSMETIC 跳过重析；结构变才重析；无 tree-sitter 数据的文件一律保守判 STRUCTURAL（`core/src/fingerprint.ts:48,128-147`）；汇总级 `classifyUpdate` 输出 SKIP/PARTIAL_UPDATE/FULL（`core/src/change-classifier.ts:16-21`）
- **增量管线**：`git diff <lastCommitHash>..HEAD --name-only` 取变更文件（`SKILL.md:194-198`）→ 只重析变更文件所在批次（neighborMap 仍引用未变文件保跨批边，`SKILL.md:361-385`）→ 旧图中变更文件的节点/边剪除后与新批合并（`SKILL.md:378-385`）；`staleness.ts` 提供 isStale/mergeGraphUpdate（`core/src/staleness.ts:383,472`）
- **演化 = 版本快照**：图绑定 gitCommitHash，更新即重建到新 commit；无内容 decay/merge——"遗忘"只发生在文件被删时
- **图质量守门**：默认走确定性 inline 校验（node id 唯一、边 dangling、层引用、节点跨层冲突检查，`SKILL.md:611-649`），`--review` 才启用 LLM graph-reviewer（`SKILL.md:607`）；merge 脚本做 ID 规范化/复杂度归一/去重/tested_by 边两遍矫正（`SKILL.md:346-355`）

### 2.5 注入上下文的方式
- understand-chat：新鲜度检查（对比图 commit 与 HEAD + `git diff --name-only -- .`，monorepo 兄弟项目变更不算 stale，`understand-chat/SKILL.md:36-49`）→ grep 子图 → LLM 基于子图作答；无 token 预算机制，靠"只读相关段"纪律（`understand-chat/SKILL.md:27-29`）
- dashboard 走 HTTP 数据 API + 前端力导向图渲染

## 3. 关键代码摘录

**摘录 1：图 schema 全景（`packages/core/src/types.ts:1-21`）**
```typescript
// Node types (27 total: 5 code + 8 non-code + 3 domain + 5 knowledge + 6 design)
export type NodeType =
  | "file" | "function" | "class" | "module" | "concept"
  | "config" | "document" | "service" | "table" | "endpoint"
  | "pipeline" | "schema" | "resource"
  | "domain" | "flow" | "step"
  | "article" | "entity" | "topic" | "claim" | "source"
  | "page" | "screen" | "component" | "componentSet" | "instance" | "token";

// Edge types (38 total in 9 categories ...)
export type EdgeType =
  | "imports" | "exports" | "contains" | "inherits" | "implements"
  | "calls" | "subscribes" | "publishes" | "middleware"
  ...
  | "cites" | "contradicts" | "builds_on" | "exemplifies" | "categorized_under" | "authored_by"
```

**摘录 2：Fuse.js 加权模糊检索（`packages/core/src/search.ts:14-25`）**
```typescript
const FUSE_OPTIONS: IFuseOptions<GraphNode> = {
  keys: [
    { name: "name", weight: 0.4 },
    { name: "tags", weight: 0.3 },
    { name: "summary", weight: 0.2 },
    { name: "languageNotes", weight: 0.1 },
  ],
  threshold: 0.4,
  includeScore: true,
  ignoreLocation: true,
  useExtendedSearch: true,
};
```

**摘录 3：三级变更分类（`packages/core/src/fingerprint.ts:126-147`）**
```typescript
 * - COSMETIC: content differs but structural signatures match (internal logic only)
 * - STRUCTURAL: signature-level changes detected
export function compareFingerprints(
...
  // we cannot verify structure didn't change — classify as STRUCTURAL.
```

**摘录 4：两阶段抽取纪律（`agents/file-analyzer.md:145-149`）**
```markdown
## Phase 2 -- Semantic Analysis

After the script completes, read `$UA_DIR/tmp/ua-file-extract-results-<batchIndex>.json`.
Use these structured results as the foundation for your analysis. Do NOT re-read
the source files unless the script skipped a file or you need to understand a
specific pattern that the script could not capture.
```

**摘录 5：增量更新的跨批边保全（`skills/understand/SKILL.md:368-374`）**
```markdown
Run compute-batches with `--changed-files`:
...
This produces a `batches.json` that contains only batches with changed files, but
neighborMap entries still reference unchanged files (with their full-graph
batchIndex) so cross-batch edges remain emittable.
```

## 4. 基准/评测声明（反虚荣视角）
- **零基准**：README/仓库无任何 accuracy/recall 数字，无评测 harness；质量保障全靠确定性校验 + LLM reviewer 可选路径 **[无评测，纯工具仓]**
- 79K 星 vs 实质：产品是"代码库→可视化图谱"的 Claude Code 插件，直击"新人上手大代码库"痛点 + 8 语言 README + homepage 营销站 + 一键安装脚本（`install.sh`/`install.ps1`）+ 多平台适配（Claude/Copilot/Cursor/Kiro/...）——**星数反映分发与营销强度，工程内核（core 包）是扎实但常规的 tree-sitter + LLM 标注管线**；管线本体是 858 行 markdown 编排（依赖宿主 LLM 的纪律执行），并非传统意义上的程序化库
- 子代理并发 5、>100 文件提示用户收窄范围（`SKILL.md:271`）——隐含承认大规模成本问题

## 5. 可借鉴模式（对 Agent 记忆系统设计的增量）
1. **AST 确定性骨架 + LLM 语义注释的分工**：结构（函数/类/导入/调用图）由 tree-sitter 保证零幻觉，LLM 只产 summary/tags/语义边——比"全靠 LLM 抽取"的记忆系统（mem0 事实抽取）可靠性高一档（`file-analyzer.md:29-149`）
2. **三级变更分类的增量记忆**：COSMETIC（注释级改动）不触发重写、STRUCTURAL 才重析——把"遗忘/更新"的粒度从文件级细化到结构签名级，省 LLM 成本（`fingerprint.ts:126-147`）
3. **边类型受控词表（38 种 9 类）**：记忆间关系不是自由文本而是 schema 化枚举，含 tested_by 双遍矫正、跨层冲突检测等图卫生机制（`types.ts:10-21`、`SKILL.md:346-355`）
4. **知识节点类型（article/claim/source/cites/contradicts）**：图 schema 原生支持"论断-证据-矛盾"知识记忆，是记忆系统做知识矛盾检测的现成模型（`types.ts:20`）
5. **图+分层+导览三视图同存储**：同一份 JSON 同时挂 layers（架构视角）与 tour（学习路径视角）——记忆不止可检索，还可"被讲解"（`types.ts:107-115`）
6. **prompt 注入防御示范**：README 等项目数据注入子代理前显式降权为 untrusted（`SKILL.md:249`）

## 6. 局限与风险（作为 Agent 记忆底座的可行性评估）
- **只读快照，非运行时记忆**：图在 commit 粒度全量/增量重建，无 agent 交互期写入路径；"记忆"仅关于代码结构，无经验/偏好/轨迹——**作为 Agent 记忆底座需要外挂写入管线，本体只解决"世界知识"层**（`staleness.ts:383` 的 isStale 是唯一活性检查）
- **检索太浅**：Fuse.js 词法 + grep 式 1-hop，无向量混合（dashboard 的 cosine 是暴力扫）、无多跳图查询、无重排；大图（10万行代码库）下 understand-chat 的 grep 检索噪声大
- 管线是 markdown 编排，执行质量取决于宿主模型对 858 行指令的遵循度；防御性文本（"no fusion"、"verify each batchIndex on disk"）暗示 LLM 执行常见跑偏（`SKILL.md:337`）
- 单 JSON 文件存储：无并发写保护、无部分加载，超大图内存压力大
- LLM 语义边（calls/related）跨批置信依赖 neighborMap 启发式，dangling 边靠丢弃兜底——边召回率无量化

## 7. 一句话对比 mem0
mem0 是"对话事实的向量卡片盒"，Understand-Anything 是"代码世界的结构化地图"——它证明了记忆可以 schema 化成 27 节点 38 边的图并用 AST 保证骨架真实，但它只有构建期记忆没有运行期记忆，是 Agent 记忆系统的"世界模型层"补件而非替代品。
