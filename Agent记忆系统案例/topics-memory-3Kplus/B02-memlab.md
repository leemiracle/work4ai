# B-02 `facebook/memlab`（5K★）
> 克隆：C:\Users\mirac\AppData\Local\Temp\opencode\memory-clones\facebook__memlab（HEAD）
> TypeScript monorepo（core/cli/api/e2e/heap-analysis/lens/mcp-server/memlab）｜ MIT ｜ Meta memory_lab oncall
> 一句话定位：**JS 堆快照三点 diff + 保持路径(retainer path)分析**的内存泄漏检测框架——用 (target−baseline)∩final 圈出泄漏对象，再用支配树/保留大小解释"为什么还活着"
> 仓库根有 AI.md（为 AI 辅助维护准备的仓库级说明，tree 实证）

## 1. 架构总览（目录地图）

```
facebook__memlab/packages/
├── core/                       # 核心算法（本次深读）
│   ├── src/lib/HeapAnalyzer.ts # 快照 diff + 泄漏分析主流程（783 行）
│   ├── src/lib/Config.ts       # 28.7KB 配置中枢
│   ├── src/lib/heap-data/      # Chrome .heapsnapshot 解析（HeapSnapshot 20KB/HeapNode/HeapEdge/NumericSet）
│   ├── src/lib/leak-filters/   # 9 条泄漏判定规则链
│   ├── src/paths/TraceFinder.ts# 最短保持路径 + 支配树/保留大小（637 行）
│   ├── src/trace-cluster/      # 泄漏轨迹聚类去重（SequentialClustering/MultiIterationSeqClustering/ML 策略）
│   ├── src/modes/              # RunningModes：InteractionTestMode / MeasureMode
│   └── src/lib/Serializer.ts / charts/   # 报告序列化 / 内存条形图
├── memlab/    # CLI：跑浏览器场景→强制 GC→抓三段快照
├── e2e/       # puppeteer 驱动
├── heap-analysis/  # 交互式 API：14 个分析插件
├── api/ lens/ cli/ mcp-server/  # 库 / IDE lens / 独立 CLI / MCP 服务器（AI 辅助入口）
```

工作流协议（`memlab run`）：
1. 驱动页面执行 **baseline 交互 → target 交互 → final 交互**三段脚本；
2. 每段结束后强制 GC 并抓堆快照（`InteractionTestMode` 编排）；
3. `diffSnapshots` 圈泄漏集 → 规则链过滤；
4. 每个泄漏节点 BFS 回溯 GC 根得保持路径；
5. 归一化聚类去重 → JSON/文本报告。

## 2. 核心算法深读

### 2.1 三点快照 diff（`core/src/lib/HeapAnalyzer.ts:246-349`）
- 按 tabsOrder 顺序流式加载快照序列：
  - target 之前的所有快照节点 id 并入 `baselineIds`（:253-255, 306-311）；
  - target 快照：`targetAllocated = target − baseline`（:313-324）——"本次交互新分配的"；
  - final 快照：`leaked = targetAllocated ∩ final`（:326-337）——"新分配且任务结束后仍存活的"。
- 退化路径：无 final 快照时 `leaked = Set{target} − baseline`（:321-323）。
- 每次加载快照前 `global.gc()` 强制回收（:264-267），保证"存活"语义干净。
- 性能选项：非 target/final 快照只扫节点 id 不建完整索引（`getSnapshotNodeIdsFromFile`，:297-304）。
- **集合代数就是泄漏的定义**：任务前已有的不算（可能是合法缓存）、任务后消失的不算（已释放），只有"因本次任务而生、且滞留"的对象进入分析。

### 2.2 支配树与保留大小（`core/src/paths/TraceFinder.ts:515-532`）
- `calculateAllNodesRetainedSizes` 三步：
  1. 先标记 window 可达节点（`flagReachableNodesFromWindow`，:520-521）——隔离调试器注入的边，防支配关系被工具自身污染；
  2. `computeDominatorsAndRetainedSizes`（:523-524）算支配序与保留大小；
  3. 回填 `node.retainedSize / node.dominatorNode`（:527-531）。
- 保留大小的语义：**成本归因的不是对象自身大小，而是它独占持有的子树**。

### 2.3 最短保持路径（`TraceFinder.ts:534-634`）
- `annotateShortestPaths`：从 GC 根集合（优先级分层 root list）多源 BFS：
  - 跳过已有 `pathEdge` 的节点（:561-563）；
  - 跳过弱引用边（WeakMap 键可按 excludeKeySet 排除，:571-576）；
  - **优先级延迟**：灰名单边/低偏好节点（C++ 根、调试器边）先进 postponeQueue，主队列枯竭才消费（:577-609）。
- 产出的是"人类最想看的解释路径"而非任意最短路。
- `getPathToGCRoots` 沿 pathEdge 逐级回溯成链表 + 访问环检测（:614-634）。
- 路径 >100 边直接丢弃（`HeapAnalyzer.ts:602-605`）——**解释性优先于完备性**。
- `heap-analysis` 包提供 14 个交互式插件复核单点：`ObjectShallowSizeAnalysis / ObjectRetainedSizeAnalysis / ObjectFanoutAnalysis / ObjectUnboundGrowthAnalysis / ShapeUnboundGrowthAnalysis / DetachedDOMElementAnalysis / UnmountedReactFiberNodesAnalysis / StringAnalysis` 等（plugins/ 目录实证）。

### 2.4 泄漏判定规则链（三值决策）
- 规则列表 9 条（`core/src/lib/leak-filters/LeakFilterRuleList.ts:24-34`）：
  1. `FilterUserTaggedLeaksRule`（用户 `memlab标记` API 打的标签）→ 2. `FilterByExternalFilterRule`（外部自定义过滤器）→ 3. `FilterTrivialNodeRule`（平凡节点）→ 4. `FilterHermesNodeRule`（RN/Hermes）→ 5. `FilterOverSizedNodeAsLeakRule`（超大即泄漏）→ 6. `FilterUnmountedFiberNodeRule` → 7. `FilterDetachedDOMElementRule` → 8. `FilterStackTraceFrameRule` → 9. `FilterXMLHTTPRequestRule`。
- 执行器 `LeakObjectFilter.filter`：每规则返回 `LEAK / NOT_LEAK / 无意见` 三值，命中即短路（`leak-filters/LeakObjectFilter.ts:30-46`）。
  - **可组合、可覆盖、默认保守**：全无意见 = 不是泄漏。
- React 专用知识内建：`markAllDetachedFiberNode / markAlternateFiberNode`（`HeapAnalyzer.ts:360-363`）。

### 2.5 聚类去重与 A/B 归因
- 聚类去重：`NormalizedTrace.clusterPaths` 按归一化保持路径聚类（`HeapAnalyzer.ts:634-643`），策略可换 `MLTraceSimilarityStrategy`（trace-cluster/strategies/，`HeapAnalyzer.ts:42` import）。
- 聚类持久化：cluster 与历史库 diff 出新增/陈旧聚类（`serializeClusterUpdate → diffClusters`，:707-729）。
- **control/treatment 对照**（`diffMemoryLeakTraces`，:95-175）：
  - 两组工作目录各自出泄漏轨迹后 `clusterControlTreatmentPaths`（:146-157）；
  - 只报 **treatment-only clusters**（:158-161 "Memlab found N new leak(s) in the treatment group"）——回归检测语义："新版本引入的泄漏模式"。
- 采样 `TraceSampler` 控制报告规模（:611-618）；泄漏摘要按 `name (type)` 聚合并按 retainedSize 排序 Top20（:390-419）。
- 整体报告四层输出：内存柱状图（MemoryBarChart）→ 泄漏对象摘要表 → 聚类轨迹（retainer path 文本）→ 逐节点 JSON 明细（traceDetailsLogger.logTraces，:185-191）。

### 2.6 值得注意的周边
- `mcp-server/` 包：把堆分析能力包装成 MCP 工具——**泄漏分析对 AI Agent 开放**的先行案例。
- `MeasureMode`：不判泄漏只测内存水位变化（与 InteractionTestMode 并列，modes/ 实证）。
- 快照元数据 `tabsOrder` 序列化为"页面交互摘要"写入报告头（`dumpPageInteractionSummary`，:369-377）——**复现步骤与数据同存档**。

## 3. 源码导航（core 包文件实证，供后续深读）

| 文件 | 职责 |
|---|---|
| `lib/Types.ts`（82KB） | 全部接口/类型契约（快照、节点、边、轨迹、聚类） |
| `lib/Utils.ts`（65KB） | 工具集：节点遍历、Fiber 判定、retainedSize 聚合（`aggregateDominatorMetrics`） |
| `lib/Config.ts`（28.7KB） | 配置中枢（灰名单/白名单、开关、cluster 目录） |
| `lib/heap-data/HeapSnapshot.ts`（20KB） | Chrome .heapsnapshot 解析与节点索引构建 |
| `lib/heap-data/HeapNode.ts / HeapEdge.ts / HeapLocation.ts` | 节点/边/位置对象模型 |
| `lib/heap-data/utils/NumericSet.ts` | 针对堆节点 id 优化的数值集合（diff 三件套的底座） |
| `lib/MemlabTagStore.ts` | 用户打标 API 的标签存取（`memlab.markAsLeaked` 类入口） |
| `lib/HeapParser.ts / StringLoader.ts` | 流式解析与字符串表加载（快照字符串先建表再引用） |
| `lib/Serializer.ts`（28.9KB） | 报告序列化（路径/交互摘要/聚类的文本与 JSON 渲染） |
| `lib/TraceSampler.ts` | 报告采样率控制 |
| `modes/RunningModes.ts` | 模式分派（InteractionTest / Measure） |
| `lib/charts/MemoryBarChart.ts` | 三快照内存柱状图（CLI 报告头图） |

monorepo 其余包：`api`（编程接口）、`cli`、`e2e`（puppeteer）、`heap-analysis`（14 个交互分析插件）、`lens`（IDE 集成）、`mcp-server`（MCP 工具服务器）、`memlab`（CLI 主包）。

## 4. 与 Agent 记忆的可迁移机制

1. **三点 diff 是 episodic 记忆变化检测的原型**：
   - `(任务中新增) ∩ (任务后仍存活) = 应升级为长期记忆的候选`；
   - 对称地 `(任务中新增) − (任务后存活)` 是可丢弃的工作记忆；
   - A 层系统大多只有"写入+检索"，缺**任务边界处的批量凝缩时机**——memlab 把它做成了协议。
2. **保留大小 ≠ 条目大小**：记忆的真实成本是它独占牵连的子树（附属 chunk、专属向量、关联索引）；用支配树思维评估"删除这条能省多少"，比按字节配额精准。
3. **retainer path = 记忆滞留的解释与删除路径**：每条"该忘没忘"的记忆都应能回答"谁在持有我"（任务引用？实体索引？去重锁？），沿路径剪断引用即可释放——记忆 GC 的可执行语义。
4. **规则链三值决策**：记忆保留策略应是可组合规则（用户标记 > 显式策略 > 启发式），默认"无意见=不动作"。
5. **聚类去重 + A/B 对照**：按归一化来源路径聚类膨胀条目，对照中只报新增模式——记忆膨胀的回归检测形态。
6. **解释性预算**：>100 边路径丢弃；给 Agent 的记忆解释链同样要有长度预算。
7. **MCP 化自家工具**：memlab 把分析器开成 MCP server——记忆治理工具链对 Agent 自身可用是趋势。

## 5. 局限
- 依赖 Chrome DevTools Protocol 抓快照 + 强制 GC；GC 时机与快照完整性决定结论可靠性。
- JS 堆专用（Hermes/RN 有特判但非一等公民）；不覆盖 native 内存。
- 三点法对"跨任务慢性泄漏"（每任务漏一点、单次不显著）不敏感，需多轮迭代对照。
- 快照大（数百 MB 常见），diff 是离线批处理而非在线监测。
- （补充）AI.md 在仓库根部（tree 实证）——Meta 已为 AI 辅助维护准备了仓库级说明文件，与 mcp-server 包同向。
