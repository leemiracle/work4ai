# 01 · extensions/automation-context：全仓访问控制的单一事实源

> 仓库：NVIDIA/AI-Factory-Operations-Agent（AFOA，Mosaic 栈的 OpenClaw 运维 agent）
> 主文件：`helm/mosaic-stack/files/openclaw-seed/extensions/automation-context.ts`（231 行）
> 协同文件：`extensions/mutation-ledger.ts`（158 行）、`extensions/bcm/index.ts`（935 行）

## 一、角色定位

如果把 AFOA 的安全模型比作一座大楼，`automation-context.ts` 就是门禁中控室：它不亲自开门，但每扇门"什么身份能开"的判定规则全部出自这里。文件只有 231 行，却导出 **17 个函数**、1 个会话扩展常量和 6 个类型（`automation-context.ts:86-111`），是全仓引用密度最高的策略模块——automation-guard、bcm、remote-ssh、kubernetes 四个插件全部从它导入判定函数（见"外部连接"节）。

它回答三个问题：

1. **这个会话是谁**——是不是自动化机器人（`isReadonlyAutomationSession`，`automation-context.ts:144`）？当前处于 View/Edit/Auto 哪种访问模式（`sessionAccessMode`，`automation-context.ts:148`）？
2. **这个工具是什么级别**——只读还是变更（`toolAccess`，`automation-context.ts:210`）？
3. **此刻允不允许动**——变更许可 = 全局 editEnabled 开 && 上下文允许编辑，双重闸门（`contextAllowsMutation`，`automation-context.ts:202`）。

配套的 `mutation-ledger.ts` 是"变更台账"：所有变更类操作先在磁盘上登记指纹再执行，同一 toolCallId 重放直接返回上次状态、不重复执行（`runMutationOnce`，`mutation-ledger.ts:103`）。`bcm/index.ts` 则是这套机制最重的消费者：935 行的 Broad Command Manager 桥接插件，把 OpenClaw 工具经 MCP streamable HTTP 转发到 bcm-mcp-tools 服务。

三者合起来构成 AFOA 的"判定—记账—执行"三层：判定在 automation-context，记账在 mutation-ledger，bcm 是用它们搭出来的典型变更工具实现。

## 二、内部结构

### 两张工具清单与一个正则

文件头三件套定义了分类基线：

- `ALWAYS_MUTATING_TOOLS`（`automation-context.ts:8-16`）：7 个恒变更工具——`apply_patch`、`edit`、`write`、`run_kubectl_admin`、`bcm_execute_cmsh_admin`、`bcm_add_note`、`bcm_remove_note`。
- `READ_ONLY_TOOLS`（`automation-context.ts:22-84`）：60 个只读工具，覆盖 BCM 查询族（`bcm_get_info`/`bcm_health` 等 8 个）、DCGM 族（5 个）、observability 族（5 个）、iraop 检索族（4 个），以及 `exec`、`read`、`grep`、`run_kubectl` 等通用件。两处注释值得细读：Grafana 建仪表盘的两个工具被**有意**归入只读（`automation-context.ts:18-21`——保存仪表盘只是"对观察数据的可视化"，属于 View 工作流）；硬件采集工具归只读但"应单独限速而非要求 Edit"（`automation-context.ts:50`）。
- `AUTOMATION_SESSION` 正则（`automation-context.ts:6`）：匹配 `mosaic-automation-(cluster-monitor|alert)-*` 形态的 sessionKey——定时巡检与告警触发的自动化会话由此识别，**无论请求什么模式一律按只读处理**。

### 模块级状态三件套

`automation-context.ts:118-120` 持有三份进程内状态：`runAccess`（Map，per-run 访问态，供 Slack 通道覆盖会话默认权限）、`mcpToolPolicies`（Map，每 MCP server 的工具策略表）、`identityApprovalBroker`（身份审批代理回调）。

`configureMcpToolPolicies`（`automation-context.ts:122-137`）把插件配置重建为 `server名__` 前缀的策略表：`defaultAccess` 与 `viewTools` 白名单，server 名与工具名统一小写归一。这给了外部 MCP server 一个声明式入口——不在两张清单里的 `mcp-server__tool` 形态工具，按前缀查这张表分级（`automation-context.ts:221-225`）。

### 分级核心 toolAccess

`toolAccess`（`automation-context.ts:210-227`）是四个插件共用的分级判据，判定顺序即优先级：

1. `run_remote_ssh` 特判：按 argv 是否过诊断白名单**动态**分级（`automation-context.ts:213-218`）——同一条 `nvidia-smi` 查询是只读，`systemctl restart` 就是变更，判据委托给 `diagnostic-policy.ts` 的 `isAllowedDiagnosticArgv`。
2. 恒变更集合命中 → `edit`；
3. 只读集合命中 → `read`；
4. MCP 前缀策略表 → 按表；
5. 其余 → `unknown`。

`toolRequiresEdit`（`automation-context.ts:229-231`）是便捷封装：**非 read 即视为需要 Edit——unknown 按 edit 处理，站在保守侧**。

### 审批链：fail closed 的身份审批

`requestIdentityApproval`（`automation-context.ts:177-182`）只有三行，却是 Slack 审批链的关键：非 Slack 提供方的 run 直接返回 `undefined`（走通用审批 UI）；**是 Slack 且 edit 模式但没有安装审批代理时直接返回 "deny"**（`automation-context.ts:180`）——这就是 fail closed：宁可拒绝，不静默放行。`configureIdentityApprovalBroker`（`automation-context.ts:171`）由 automation-guard 在启动时安装 Slack 按钮式代理。

### mutation-ledger：指纹台账与幂等执行

台账记录结构极简：`{id, fingerprint, state, startedAt, finishedAt}`（`mutation-ledger.ts:10-16`），state 三态 running/completed/failed（`mutation-ledger.ts:8`）。

**指纹**（`mutation-ledger.ts:80-84`）= `sha256(JSON.stringify([toolName, target, args]))`。注意它**包含**完整 args——这是幂等判定的需要（同一 toolCallId 配不同参数必须报错，`mutation-ledger.ts:116`："tool call id was already used for a different mutation"）。敏感面的控制发生在**入账之前**：kubernetes 插件对 stdin 原文只入账 `stdinSha256` 摘要而非本体（`kubernetes/index.ts:84` 配合 `kubernetes/policy.ts:114`），私钥路径等凭据则由各 runner 的脱敏层拦截（如 `remote-ssh/runner.ts:45-50`）。换言之：命令本身要进账（审计与幂等都依赖它），凭据材料不进账。

`runMutationOnce`（`mutation-ledger.ts:103-158`）的执行时序：

1. 领号：串行临界区内查台账，已有同 id 记录则不执行（重放返回上次状态，`mutation-ledger.ts:129`）；
2. **僵尸检测**：记录是 running 但 `active` 内存集合里没有对应 key——说明进程重启过，判 failed 收尾（`mutation-ledger.ts:117-121`），防止一次崩溃把整个 toolCallId 永久卡死；
3. 执行操作，成功/失败双路回写终态（`mutation-ledger.ts:134-153`），finally 释放 active（`mutation-ledger.ts:156`）。

写入本身三重防护：`serialized` promise 队列串行化所有台账读写（`mutation-ledger.ts:37-41`）；临时文件 + `rename` 原子替换（`mutation-ledger.ts:98-100`）；目录 0700、文件 0600、尾部只保留最近 1000 条（`mutation-ledger.ts:97-99`）。审批决定另记一本账（`recordApprovalDecision`，`mutation-ledger.ts:57-78`，独立文件 `mosaic-approval-ledger.json`），记录决策者 senderId——谁批的与改了什么分开存。

## 三、外部连接

`automation-context.ts` 被 6 个生产文件 + 2 个测试文件导入：

- **automation-guard**（守门插件）：`automation-guard/index.ts:5-17` 一次性导入 11 个符号，是最大消费者——它把 `toolAccess`/`contextAllowsMutation` 包成 `session-access` 可信策略挂到工具调用总线上（`automation-guard/index.ts:62-102`）；Slack 消息进来时用 `setRunAccess` 按 `slackEditUserIds` 名单定 mode（`automation-guard/index.ts:45-58`），run 结束 `clearRunAccess` 防跨 run 泄漏（`automation-guard/index.ts:59`）。
- **bcm**：`bcm/index.ts:5-10` 导入 4 个符号，`bcm-access` 策略拦截三个变更工具（`bcm/index.ts:560-606`）。
- **remote-ssh**：`remote-ssh/index.ts:5-14` 导入 4 个符号 + diagnostic-policy + mutation-ledger——一个文件串起本篇全部三个模块。
- **kubernetes**：`kubernetes/index.ts:5-19` 导入 3 个符号。
- **测试**：`helm/mosaic-stack/tests/automation-context.test.mjs:26`（自动化会话识别、默认 View 语义、fail-close 等 12 用例）；`tests/loki.test.mjs:8` 借用 `toolRequiresEdit` 判定日志工具级别。

下游依赖只有一条：`automation-context.ts:4` import `diagnostic-policy.ts`——这是它唯一的业务依赖（下一篇主角）。

`bcm/index.ts` 的外部连接是双向的：对上注册 13 个工具（`bcm/index.ts:608-933`：health/info/cmsh/cmsh_admin/notes 四件套/search_tools/search_docs/node_health_summary/slurm_job_evidence/execute_tool）与 `bcm-access` 策略；对下经 `fetch` 打 `http://bcm-mcp-tools:3001/mcp`（默认地址 `bcm/index.ts:13`），JSON-RPC 2.0 请求（`bcm/index.ts:397-402`）兼容 SSE 与纯 JSON 双响应形态（`parseRpcPayload`，`bcm/index.ts:325-343`）。

## 四、数据流

一次典型的 BCM 变更请求（Edit 模式、HITL 开）完整流过三层：

1. 模型调用 `bcm_execute_cmsh_admin`，参数 commands 经 `cmshCommands` 校验（非空、≤4096 字符、无 NUL，`bcm/index.ts:160-164`）；
2. **判定层**：`bcm-access` 策略先查自动化会话（是则直接 block，`bcm/index.ts:564-570`）；变更工具若 `hitl=false` 或 `contextSkipsApproval`（Auto 模式）放行（`bcm/index.ts:577`）；否则走 Slack 身份审批或通用 `requireApproval`，超时行为 deny（`bcm/index.ts:587-598`）；
3. **记账层**：审批通过后 `runMutationOnce` 领号（toolCallId + 指纹入账，`bcm/index.ts:800-805`）；重放请求在此被截住，返回 `{replayed: true, executed: false, previousStatus}`（`bcm/index.ts:806-813`）；
4. **执行层**：`callBcmTool` → `cachedBcmRpc` → `bcmRpc` 发 JSON-RPC（`bcm/index.ts:461-490`），结果经 `toOpenClawResult` 规范化（`bcm/index.ts:183-198`），同时把 start/delta/complete/error 事件 POST 到 Mosaic UI 的 subagent 端点（`postSubagentEvent`，`bcm/index.ts:277-301`——best-effort，失败静默不影响工具结果）。

读路径上有两个值得偷师的细节：**60 秒 TTL + in-flight 去重双 Map 缓存**（`bcmCache`/`bcmInFlight`，`bcm/index.ts:19-20` 与 `cachedBcmRpc` `bcm/index.ts:422-445`），同一请求并发只发一次；**缓存键归一化**（`normalizeRpcValue`，`bcm/index.ts:356-371`）把字符串压空白、对象键排序——参数顺序不同语义相同的调用命中同一缓存。

## 五、设计决策

1. **单一事实源而非分布式判定**。四套插件各自实现访问判定是灾难的开端——规则漂移后没人说得清哪条边界是真的。AFOA 把全部判定收进 231 行的一个文件，插件只消费不实现。代价是所有判定函数必须刻意保持纯函数化（工具清单 + 入参 → 结论），模块级状态只有 runAccess/mcpToolPolicies/broker 三份且都有明确的清理路径。
2. **unknown 按 edit 处理**（`automation-context.ts:229-231`）。新工具忘登记时落到保守侧；配合 automation-guard 里对 unknown 工具强制走审批（`automation-guard/index.ts:80-100`），"没分类"既不是放行也不是死路，而是升级到人。
3. **幂等键选 toolCallId 而非内容哈希**。内容相同的两次请求是两次合法操作（两次重启同一个服务），只有同一 toolCallId 的重试才是必须去重的重放——键的选择直接定义了"什么算重复"。
4. **僵尸检测放在领号时而非启动时**（`mutation-ledger.ts:117-121`）：只有当这条 running 记录被再次触碰且内存 active 集合无此 key 时才判死，避免启动扫描全表的代价，也避免误杀他人正在跑的合法操作。
5. **审批账与变更账分文件**（`mutation-ledger.ts:44` vs `:65-66`）：变更账会被截断到 1000 条，审批账不截断——两种数据的保留需求不同。

## 六、新人提示

- 改动两张工具清单（`automation-context.ts:8-84`）是全仓影响面最大的单点编辑之一：automation-guard、loki 测试、各插件策略全跟着变，先跑 `helm/mosaic-stack/tests/automation-context.test.mjs`。
- `sessionAccessExtension`（`automation-context.ts:184-188`）被四个插件各自注册一次——OpenClaw 的会话扩展注册是幂等的（namespace 相同），不是 bug。
- bcm 的 `slurm_job_evidence` 工具要 `slurmEnabled && cmshEnabled` 双开才注册（`bcm/index.ts:659`），`bcm_execute_cmsh` 系列要 `cmshEnabled`（`bcm/index.ts:758,780`）——工具"不存在"常常是配置未开，不是代码缺陷。
- 想追踪一次变更的完整痕迹：变更看 `mosaic-edit-ledger.json`，审批看 `mosaic-approval-ledger.json`（路径由 `MOSAIC_EDIT_LEDGER_PATH`/`MOSAIC_APPROVAL_LEDGER_PATH` 环境变量可覆盖，`mutation-ledger.ts:44,65`）。
- ⚠️ 甄别记录：任务简报称 mutation-ledger"指纹不含敏感参数"——源码核实指纹**包含完整 args**（`mutation-ledger.ts:80-84`）；准确的表述是"敏感原文不直接入账"（kubectl stdin 只存 sha256 摘要，`kubernetes/index.ts:84`）。本文按源码口径撰写，图谱 summary 与源码无其他冲突。

（行号锚基于当前工作树源码逐条核实。）
