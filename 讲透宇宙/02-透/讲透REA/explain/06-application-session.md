<!-- source: knowledge-graph tour step | files: src/application/AnalysisProvider.ts, src/application/binary/BinarySession.ts, src/application/DirectAnalysis.ts -->

# 06 · 应用编排与会话

### 角色定位

三者同属**应用编排层**：`AnalysisProvider.ts`（297 行）是纯类型契约中枢，零 I/O；`BinarySession.ts`（999 行）是有状态会话门面，持有 CLI/MCP 共享的唯一 active target（`BinarySession.ts:81` 的 `#active`）；`DirectAnalysis.ts` 是 one-shot 执行引擎，CLI 每次调用刻意隔离——同一抽象支撑两种生命周期。深度 provider 注册表现扩为四家 `[hopper, ghidra, ida, kuna]`（`src/composition/binary.ts:32`）。

### 内部结构

#### 2.1 AnalysisProvider.ts：封闭联合与原子观察

核心是五套工具名加健康探针的**封闭联合** `AnalysisOperation`（`AnalysisProvider.ts:36-42`），TS 层面杜绝传错工具名。三个关键形状：

- `AnalysisExecution`（`:45-62`）：原子观察单元——result/rawResult 双份、provider 出身、profile 承诺、limitations/locations、subject；新增 `relationshipCoverage`（`:52`，caller/callee 完备性自评）与 `referencesTruncated`（`:59`，xrefs 截断声明，不进 Evidence）。工厂 `createAnalysisExecution`（`:81-120`）强制 `jsonValueSchema.parse`+`structuredClone`。
- `AnalysisClient`（`:150-169`）：execute/close 之外全是可选钩子——`executeIfReady` 快路径、进程 lineage/请求活动/操作健康三类观测；`close` 失败的清理被保留供重试。
- `CapabilityDescriptor`（`:214-226`）：7 布尔副作用（`:192-200`）+`cachePolicy`（`:221`）决定能否快照重放。`AnalysisProviderCandidate`（`:285-297`）新增 `hasPendingOwnedResources()`/`closeOwnedResources()`（`:294-296`）——候选级资源也要有主人。

#### 2.2 BinarySession.ts：单目标会话与代际并发

`BinarySession extends BinarySessionRecords implements BinarySessionPort`（`:77-79`）。`#serialize`（`:865-890`）promise 链串行生命周期并递增**代际号**（`:872`）；`#drainCalls`（`:892-898`）只等 `generation <= admittedThrough` 的调用——后到的 open 不把更晚的调用算进排水。

`#openWithinTransition`（`:284-375`）：解析路由→排水→重试上次保留的失败清理（`:537-557`）→同 target+同 profile 走 **liveness 门控快路径**（`:117-131`，`#retainedClientLive` 读子进程 operationHealthSnapshot 判死活，`:916-928`）→否则关旧 client→新 runId→createClient→health 探活（`:342`），失败经 `#restoreAfterFailedOpen` 重建旧目标（`:574-582`）；成功提交 `#active` 并选/清/导入快照。`#execute`（`:690-790`）：预检能力/缓存（`BinarySessionExecution.ts:55-94`）→缓存命中直接返回（`:719`）→mutatesArtifact 在**派发前**失效快照（`:720-722`）→`client.execute`→profile/subject 双重绑定校验→`procedure_callers/callees` 未报 coverage 回填 unknown（`:730-742`）→可缓存则 createEvidence 记账（`:761-787`）。

#### 2.3 DirectAnalysis.ts：按工具名路由的一次性引擎

顶部 20 值 `DirectAnalysisTool` 联合（`:63-83`，较 v6.1 新增 `search_bytes`）。三入口：`runDirectAnalysis`（`:94`）、`runProviderAnalysis`（`:130`）、`runManagedProviderExecution`（`:161`，managed 隔离会话）。

`runAnalysis`（`:212-391`）：parseConfig→快照读盘校验（不符即拒，`:547`）→`previewTarget` 预解析路由（`:262`），Ghidra 须活跃 client 承认源码不走 CLI 直放（`:283-284`），其余缓存命中**直接重放，provider 根本不启动**（`:293-302`）→`openResolvedTarget`（`:325`）→`executeAnalysisTool`（`:393`）→快照落盘→finally 关会话。v6.2 起快照必含 `workflow_entries`（缺失即拒，`AnalysisSnapshotFiles.ts:113`），每个缓存查询须有 profile 绑定的 Evidence，import 拒绝不完整绑定；artifact inventory 同步拆为 nodes（内容身份 artifact_id/sha256/format）×occurrences（per-path 角色/可执行位）。

### 外部连接

依赖全指向 domain/contracts；编排零件拆在 binary/ 子目录。MCP 侧 open_binary 调 `session.open`（`registerSessionTools.ts:182`），`provider_id`（`:192-194`）可指定深度 provider；v6.2 删 binary_session 顶层 provider/providers 别名，改读 `analysis_provider_binding`/`analysis_provider_candidates`（`BinarySessionStatus.ts:91-92`）。registerNativeTools 经 registerEvidenceTools+retainedSummaryDelivery 注册（`registerNativeTools.ts:14-24`）。CLI 7 个命令模块消费 composition/directAnalysis；`composeBinarySession`（`BinarySessionComposition.ts:11-18`）用 `SessionProviderRouter.selectable` 构造，`assertDisjoint`/`assertUniqueProviderIds`（`SessionProviderRouter.ts:191-215`）保证 provider id 唯一、auxiliary 操作集不相交，违反抛 TypeError。

### 数据流：一次 CLI 调用的完整路径

以 `read_bytes` 为例：①SIGINT 转 abort；②造一次性会话；③快照读盘校验；④previewTarget 缓存命中直接返回 Evidence；⑤open 见 2.2 流程；⑥execute：无 active target 抛 NoBinaryOpenError（`BinarySessionExecution.ts:66`）→校验返回 provider 与所选 profile **id/name/version 全等**（`:104-108`）→校验 subject sha256；⑦createEvidence 记账、写快照落盘；⑧finally 关会话——清理失败不再静默：`#pendingCleanup` 供下次 open 重试（`BinarySession.ts:524-557`），一次性分析可报 `cleanup_incomplete`。

### 设计决策

**封闭联合代替裸 string**：health 也走 execute，能力查找、缓存键、探活共用一个类型。

**代际排水而非全局锁**："生命周期串行+分析并发+切换前排水"（`:865-898`），支持 MCP 并发工具调用又保证切换时旧资源安全释放。

**失败恢复优先**：切换失败重启旧目标，但 open 仍返回切换失败（`:574-582`）；恢复失败以 `analysisErrorWithCleanupFailure` 合并上报，不吞清理错误。

**身份三重校验**：provider 声称身份、profile.provider、subject.sha256 任一不符即 ProviderAdapterError。

**缓存双向收口**：非 stateful+具体 profile+非 mutatesArtifact+cachePolicy!=="live" 才可缓存；mutatesArtifact **派发前**失效快照——失败回复不能证明元数据写已回滚（`:720-722`）；失效后导出/导入拒绝并附恢复指引（`BinarySessionRecords.ts:154-162`），导出还须具体 profile（`:165-170`）。

**错误走 Result 通道**：CLI 出口 `cliError` 才投影为秘密安全 JSON；`#emitAvailabilityChanged` 吞观察者异常。

### 新人提示

**上手顺序**：`AnalysisProvider.ts`→SessionProviderRouter→BinarySession 的 #open/#execute→runAnalysis。

**易错点**：①enhanced/workflow 不走 provider 快照缓存，`providerIdentity` 对 enhanced 回退"唯一 available 的 official provider"推断，多 provider 时返回 composite 身份（`:134-155`）；②快照须具体 profile，"有 target 无 profile"导出直接报错（`BinarySessionRecords.ts:165-170`）；③`#active` 只能经 protected 钩子 `activeAnalysisBinding()`（`:611-613`）访问；④外部命令（rizin/gdb）变更目标走 `withAdmittedExternalMutation`（`:378-435`），Ghidra 活跃时直接拒绝。

**测试入口**：`tests/fixtures/binarySession.ts`、tests/boundary/mcp/、managedDirectAnalysis.test.ts。
