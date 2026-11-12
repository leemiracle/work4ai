# 02 · rebuild 子系统与断点续跑

对象：`src/lib/actions/sandbox/rebuild-pipeline.ts`（1176 行）、`rebuild-recreate-journal.ts`（818 行）、`forward-recovery.ts`（1090 行）。三者在图谱中同属"rebuild 子系统与断点续跑"层。

## 角色定位

rebuild 的产品语义是"活着重建"：在保留 agent 注册状态与策略的前提下删掉旧沙箱、用新镜像重建同名沙箱。`rebuild-pipeline.ts` 是总编排（`rebuildSandbox` 公共入口 :122），`rebuild-recreate-journal.ts` 是断点续跑的持久层——用 checkpoint 事务与恢复标记把"删了旧的、新的还没好"这个危险窗口变成可恢复状态机；`forward-recovery.ts` 则负责重建后宿主侧端口转发（dashboard/messaging/agent 声明端口）的健康检查与重建。

## 内部结构

pipeline 外层三重护栏：`delegateRebuildToOwningRegistry`（:130）把请求让渡给拥有该沙箱的注册表；`withPortableOnboardRetirementBoundary` + `withMcpLifecycleLock`（:139/:147）串行化生命周期；scoped 环境变量按白名单保存恢复（:156-182）防凭据泄漏。核心 `rebuildSandboxUnlocked`（:188）按阶段推进：preflight（:213）→ stoppedSource 捕获（:255）→ registry 回滚快照（:267）→ pre-delete 恢复复核（:286）→ backup 阶段（:517 `runRebuildBackupPhase`，含 policy/MCP/Hermes operator config 三类 handoff :552-610）→ 最后安全点复核（:648-685：镜像上下文、DCode 路由、受管工作负载三重 revalidate）→ 打开 journal（:687）→ destroy（:841，`validateAfterMcpPreparation`/`validateAtDeleteEdge` 两回调 :856/:922）→ recreate（:1017）→ restore+post-restore（:1053-1108，Hermes cron 走 dispatch-gate 事务 :1065）。journal 侧：恢复标记 `.nemoclaw-rebuild-recovery.json`（journal:56）分 V1/V2/V3 三代 schema（:59-88，V3 加 `phase: restore|cleanup`）；`readRecoveryRecord`（:203）用 `O_NOFOLLOW`+UID 属主+nlink=1+mode 0600+大小界 1-4096 做文件权威校验（:221-232），前后双 fstat 防读中被替换（:234-243）；写入走临时文件+rename+目录 fsync 原子路径（:267-287）。事务状态机七态 `planned→deleting→deleted→creating→created→registry_committing→completed`（`onboard-checkpoint-types.ts:94-102`）。

## 外部连接

pipeline 是全仓 import 密度最高的节点之一（38 连接）：上接 `rebuild.ts` CLI 与 `rebuild/owning-registry-worker.ts`；阶段模块 backup/destroy/recreate/restore/post-restore/preflight/messaging/mcp 八族全部由它调度；状态层依赖 `state/onboard-session`、`state/registry`、`state/mcp-lifecycle-lock`、`state/migrations/removed-immutability`。journal 依赖 `sandbox-recreate-transaction`（事务推进/CAS）、`sandbox-recreate-probe`（网关观察）、`gateway-teardown-authority`（权威解析）。forward-recovery 的消费方横跨 `global.ts`、`stop.ts`、`destroy-preflight.ts`、`process-recovery.ts`、`launch-readiness/health.ts`（39 连接），是 launch/stop/destroy 三命令共享的转发真相源。

## 数据流

journal 是中枢：destroy 前经 `openRebuildRecreateJournal`（journal:671）打开——先重验网关权威（权威漂移即抛 `GatewayAuthorityError` 并经 `onAuthorityRefusal` 上报，#8103，:682-706），再 `ownSandboxRecreateTransaction` 认领或替换 void journal（:711/:732），`targetIntentFingerprint`（:581，把 agent/镜像/GPU/挂载/网关等 17 项意图压成指纹）保证续跑时"新沙箱还是我想要的那个"；随后 `recordRebuildRecoveryBackup`（pipeline:699）把备份绑定到事务。断点续跑三条恢复路径在 pipeline 里显式分叉：①cleanup-only 收尾——handoff 已退役但标记残留，只补清理（:488-515）；②acceptedTarget 收敛——前一轮已建成并证明替换者，本轮跳过 destroy 直接 restore+post-restore+cron 恢复+`completeAcceptedTarget`（:711-836）；③正常全管线。删除边界上，`beginDelete`（journal:777）推进 phase，`confirmDeleted`（:795）必须观察到源沙箱 "missing" 才进 deleted。人工退役通道 `retireRebuildRecoveryBackup`（:456）要求 `--yes` 确认数据已恢复（:465）且网关证明旧沙箱缺席（:512-520）才清 handoff 与标记。

## 设计决策

①**destroy 前最后安全点复核**：镜像上下文、DCode 路由、受管工作负载在删除前重验（pipeline:648-685），注释明言"mutation of the retained copy cannot cross the destructive boundary"。②**policy handoff 不被 teardown 污染**：MCP 拆除会临时剥掉凭据绑定规则，delete 边沿用拆除前捕获的完整文档而非重抓临时态（:952-957）。③**恢复标记是凭证级资产**：mode/属主/符号链接/尺寸全查（journal:221-232），损坏即拒绝并指示"ask a NemoClaw maintainer"（:117-125），绝不静默重建。④**意图指纹防挂羊头**：续跑时指纹不匹配即拒绝，mount-free journal 保留 v1 指纹版本注释（:625-628）体现兼容性谨慎。⑤**转发不夺占**：非本沙箱所有的 listener（foreign/indeterminate）只上报不顶替——顶替会把 dashboard token 发给陌生进程（forward-recovery.ts:768-774，#11149）。⑥**观察期计划一致性**：健康检查中途 plan 变化（端口集/bind/网关）即抛错返回 indeterminate（:979-1040）。

## 新人提示

读 pipeline 建议先走 `rebuildSandboxUnlocked` 正常路径，再回看三条恢复分叉——`bail` 回调是唯一退出通道，返回 `undefined` 即失败终态。journal 测试大量覆盖 schema 拒绝分支，是理解文件权威校验的最快入口。forward-recovery 有 31 个导出，先抓四个动词：ensure（建立）、recover（重建）、retire（退役 legacy）、observe（健康观察）；端口集合语义见 `resolveSandboxForwardPortsFromAuthority`（:187）。注意 `retainPolicyHandoffForRecovery` 标志（pipeline:1003-1008 在 onDeleted/onDeleteStateAmbiguous 置位）决定 finally 块是否保留 handoff 供续跑（:1133-1150）。
