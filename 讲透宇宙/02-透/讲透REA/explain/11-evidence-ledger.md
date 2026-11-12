<!-- source: knowledge-graph tour step | files: src/domain/evidence.ts, src/domain/evidenceBundle.ts, src/domain/digests.ts, src/domain/completionLedgerGeneration.ts -->

# 11 · Evidence 证据体系与完成账本

### 角色定位

REA 的每个分析结论——ELF 解析、JS bundle 重建、进程捕获——都收敛为可独立校验的 **Evidence 记录**。四个文件是收敛终点：`digests.ts` 定全仓 digest 形状，`evidence.ts` 定义证据身份与防篡改语义，`evidenceBundle.ts` 打包字节稳定的密封 bundle，`completionLedgerGeneration.ts` 生成"任务完成"的密码学承诺。它们零 I/O，`evidence.ts` 在 src+tools 内被 179 个文件直接 import（v6.1 为 150）。认识论框架从三分升为四分：**observations, derivations, inferences, unknowns**（AGENTS.md:3）；v6.2 起 Evidence 整体直接放进 `structuredContent`，旧 `{result, evidence_id, evidence}` 信封废除，`value = evidence.normalized_result`（docs/migration-6.2.md:7-15）。存在理由：**agent 逆向天然多疑——结论可能来自工具、重放或推断，唯一信任基础是"结论自带可重算的身份"**。

### 内部结构

#### digests.ts：一个正则的独裁

`SHA256_PATTERN`（digests.ts:16）、`digestSchema`、`prefixedDigestSchema(prefix)` 工厂（digests.ts:27-33）三导出。头注释（digests.ts:6-12）坦白：此前是约 30 个模块各自手抄。收敛后 `ev_`/`ecm_`/`ecl_`/`unk_` 家族不可能发明自己的拼法，前缀粘错直接校验失败。

#### evidence.ts：语义 ID 与不可变快照

`evidenceBaseSchema`（evidence.ts:123-142，strict）五组字段：主体（subject format 28 值枚举，:41-70）、来源（provider/operation/parameters/**analysis_profile**——必填，对象或 null，:128，v6.2 起参与身份，migration-6.2.md:50-55）、认识论分级（confidence 三级，:134 + **authority 五级** shipped-artifact/controlled-replay/historical-reference/external-service/analyst-inference，:108-114）、定位（locations 五 kind 判别联合，:89-106）、关联（evidence_links/relationship_coverage，:138-140）。profile 非空时必须与 provider 三字段全等（:145-164）。

防篡改核心 `computeEvidenceId`（evidence.ts:273-274）：对 `semanticProjection`（:247-270）做 canonical digest 加 `ev_` 前缀。projection 刻意排除 subject.name 与 local_path（显示字段，换机器就变但身份不应变），raw_result/normalized_result/analysis_profile 全参与哈希。`parseEvidence`（:277-284）据此双向认证：剥 ID 重算 digest，不匹配以 zod issue 拒绝（:174-179）——语义被改的记录进不了系统。

不可变走模块级 WeakMap（evidence.ts:189），parse 遇已注册引用直接命中（:278-282）。生产入口 `createEvidence`（:338-353）经 `normalizeEvidenceObservation`（:382-451）：无 target 时自动注入 limitation（:420-428）——连"不知主体是谁"也进语义哈希；result 已是认证快照时 safeExtend 免重走全量校验（:435-441）。协作式入口 `createImmutableEvidenceSteps`（:356-380）接受可变 result 直接抛 TypeError（:361-364）。

#### evidenceBundle.ts：确定性排序 + unknown 依赖图

bundle schema（evidenceBundle.ts:42-50）七组数组：records、投影去重的 artifacts/providers/environments、按 authority/predicate_type 筛出的 scenarios/captures、unknowns。`createEvidenceBundle`（:86-141）把 records 按 evidence_id、unknowns 按 (unknown_id, revision) 排序——"order has no semantics"。`parseEvidenceBundle`（:263）重建 canonical bundle 做 stringify 全等对比（:317-318），乱序夹带即抛 `NonCanonicalEvidenceBundleError`（TypeError 子类，:56-61）；密封入口先拒重复 ID（:69-73）。

`validateUnknownGraph`（evidenceBundle.ts:326）四条不变式：revision 从 1 连续且 digest 链咬合；引用 ID 必须存在；verified resolution 需至少一条**同时是 supporting、非 mutation、过资格门槛**的证据（:392-403）；`rejectDependencyCycles`（:510）栈 DFS 拒环。资格门槛按 confidence rank `{inferred:1, derived:2, observed:3}`（:490）与可空 environment 判定。

#### completionLedgerGeneration.ts：把"跑完了"变成承诺

把外部 verifier 的一次运行转成 `ecm_` manifest + `ecl_` ledger。`verifierRunSchema`（completionLedgerGeneration.ts:35-81）用 process_lineage 强制 `launcher_pid === verifier_pid`（:66-70）——verifier 必须自证"我就是被观测的进程"；pass 的 claim 必须 `artifact_sha256s.length > 0`（:99-103）。`createCompletionLedgerArtifacts`（:203）canonical 排序后，projection **剥掉 status 与 evidence_ids**（:111-113）进 manifest 算 `ecm_` ID，二者流向 ledger 侧（五态记录+`ecl_` ID）。manifest 有意排除瞬态 verifier_run（completionLedgerGeneration.test.ts:96 钉版）。

### 外部连接

**依赖**：evidence.ts 拉入 canonicalDigest/canonicalJsonDigestSteps、jsonValue、immutableJson、analysisProfile；evidenceBundle.ts 依赖 residualUnknown.ts（ResidualUnknown/UnknownStatus/RecordUnknownInput/UpdateUnknownInput :123,244,266,284）与 npm canonicalize。

**被消费**：digests 模块 71 个文件 import。会话账本 `EvidenceLedger` 移至 `src/application/investigation/EvidenceLedger.ts`（:43）：record() 同 ID 内容冲突即拒（:48），import() 先整包校验再原子合并。server 层 `ToolResultDelivery`（toolResult.ts:46）编码 MCP 响应；超预算不截断，改抛可恢复约束错误并附 retained-evidence 引用（:171-186）。

### 数据流

1. **铸造**：createEvidence 派生 subject、补默认 confidence=observed/authority=shipped-artifact（evidence.ts:417-418）、算 `ev_` ID；
2. **交付**：Evidence 整体即 `structuredContent`，`normalized_result` 就是业务值；超预算得约束错误，可同连接 `export_evidence_bundle` 取回；
3. **打包**：createImmutableEvidenceBundle 去重、校验 unknown 图、序列化落盘；
4. **验收**：verifier 报告 → createCompletionLedgerArtifacts 产出双承诺；任何事后手改都在 ID 重算中暴露。

快照与评估配套收紧：快照必须带 workflow_entries 且每个 cached query 有 profile-bound Evidence，import 拒绝不完整绑定；agent 评估 fixture 改为给"被引用的 Evidence"打分（migration-6.2.md:68-74,123-125）。

### 设计决策

**内容哈希做 ID**：天然去重、免分配器、防篡改免费；parse 重算 digest 的代价用 WeakMap 与 safeExtend 压到近零。

**路径排除、profile 进哈希**：身份跨机器稳定与显示信息分离；analysis_profile 参与身份保证"同结论不同 profile"不撞 ID——旧记录插 null 也救不回。

**顺序无语义**：构造时强制排序、parse 全等校验，bundle 可安全过任何不保序的存储。

**诚实优于完备**：函数比较状态收敛 unchanged/changed/unknown，不可达的 truncated 已删（migration-6.2.md:139-143）；未知就标 unknown，不伪造截断。

**契约先行**：completionLedgerGeneration 生产代码零调用、唯一消费者是 261 行测试，一旦有真实 verifier 消费即不可再改。

### 新人提示

**上手顺序**：digests.ts → evidence.ts（semanticProjection/parseEvidence）→ evidenceBundle.ts → completionLedgerGeneration.ts；先读 evidence.test.ts:381（semantic tampering 用例）建立直觉。

**易错点**：① `createImmutableEvidenceSteps` 传可变 result 直接抛 TypeError（evidence.ts:361-364）；② 手拼 bundle JSON 被 canonical 对比拒收，须走 export_evidence_bundle（evidenceBundle.ts:317-318）；③ verified resolution 的证据必须同时是 supporting、非 mutation 且过资格门槛；④ 旧 envelope 消费方要改成读 `structuredContent.normalized_result`。

**测试入口**：`npx vitest run src/domain/{evidence,evidenceBundle,completionLedgerGeneration,evidenceCompletionLedger}.test.ts` 与 `src/application/investigation/EvidenceLedger.test.ts`。
