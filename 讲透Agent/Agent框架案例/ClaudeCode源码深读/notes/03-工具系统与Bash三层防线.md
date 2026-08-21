# 03 · 工具系统与 Bash 三层防线

> card_id: ccsrc-03
> universe: Agent框架案例/ClaudeCode源码深读
> burke: 场景=模型要安全地操作真实世界；主体=43 工具 + BashTool 1.2 万行；能动=注册过滤分区调度 + AST 策略沙箱纵深；行动=每步 fail-closed；目的=能力最大与爆炸半径最小的平衡；张力=放行速度 vs 检查彻底；弧线=从权限弹窗到纵深防御流水线
> status: 已完成（2026-08-20，钉版 `091cde4`）
> refs: articles/03/04/05/06/13/14/16 要点 + tools.ts 抽查验证
> updated: 2026-08-20

## 1. Tool 接口：一个超宽契约（Tool.ts:362）

五组字段：①身份检索（name/aliases/searchHint/mcpInfo）②执行（call/inputSchema(zod v4)/validateInput/checkPermissions）③调度决策（**isConcurrencySafe/isReadOnly/isDestructive/interruptBehavior**）④提示词面（description/prompt/inputJSONSchema）⑤渲染面（近十个 React 钩子）。

`call` 签名还收 `canUseTool` 回调 + 父消息——**工具执行中可再次发起权限询问**（BashTool 对子命令逐个确认）。两个上下文类型：`ToolPermissionContext` 不可变快照（DeepImmutable 包裹）+ `ToolUseContext` 运行时大杂烩。工具不 import 全局状态，一切经 context 注入——**同一套工具在主线程/子代理/SDK 三宿主复用**。

`TOOL_DEFAULTS` 的 fail-closed 默认：不并发安全/不是只读/checkPermissions 放行交还通用权限系统（Tool.ts:757-769）——**默认不信任**。`ToolResult` 三载荷：`newMessages`（AgentTool 注入子代理转写）、`contextModifier`（改后续上下文）、`mcpMeta`；`maxResultSizeChars` 自报上限，**Read 必须设 Infinity，否则"结果落盘→模型再 Read 落盘文件"死循环**（Tool.ts:458-466）。

## 2. 注册与过滤（tools.ts）

`getAllBaseTools()` 是 feature 门求值现场（已抽查验证 ：25-35）：`USER_TYPE==='ant'` 才 require REPLTool；`feature('PROACTIVE')||feature('KAIROS')` 才挂 SleepTool；TeamCreate/SendMessage 用 lazy require 破循环依赖。三道过滤到"本轮可用"：SIMPLE 模式只留 Bash/Read/Edit → deny 规则（`mcp__server` 前缀整批剥）→ isEnabled() 自查。

**`assembleToolPool()` 排序为缓存服务**（tools.ts:345-367）：内置按名排序构成连续前缀 + MCP 各自排序后追加——服务端 cache breakpoint 打在最后一个前缀匹配内置工具后，交叉排序使后续所有 cache key 失效。`getMergedTools()`（不排序不去重）只服务 ToolSearch 阈值计算——**"给模型的池"与"全量列表"是两个函数**。

## 3. 调度：按 isConcurrencySafe 分区（toolOrchestration.ts:86-116）

模型一次响应多个 tool_use → 连续并发安全调用合并为并发批、其余各自串行批；**分区保序**：[Read,Read,Edit,Read] → [并发×2, 串行, 串行]，批次边界即同步点。三个防御细节：判定前先 safeParse（解析失败保守串行）；isConcurrencySafe 可能抛异常（shell-quote 解析失败）catch 降级；**安全性按输入判定——BashTool 对 `ls` 和 `rm` 给不同答案**。

并发上限 `CLAUDE_CODE_MAX_TOOL_USE_CONCURRENCY`=10；`all()` 生成器组合子手写 race 循环（generators.ts:32-68）——**限流对象是生成器的 next() 而非 promise**，进度与结果消息流经同一条流。`contextModifier` 串行立即应用、并发按 toolUseID 排队批后按序应用——并发期间 context 对批内保持一致。

**StreamingToolExecutor**（530 行）：`canExecuteTool` 两级分类——执行中存在非并发安全工具则整体等待（StreamingToolExecutor.ts:129-135）；**产出顺序严格按接收顺序**：getCompletedResults 遇"执行中且非并发安全"直接 break，后面已完成的并发工具也等着（:428-438）。**Bash 失败 abort 兄弟**：三级 AbortController（父→siblingAbortController→每工具子节点），Bash 出错 abort 中间层杀光兄弟（mkdir 失败后续无意义），父节点不动 query 不结束（:354-364）。被级联取消的工具收到合成 tool_result（sibling_error/user_interrupted/streaming_fallback 三种原因）。

## 4. 单次调用生命周期：runToolUse 七步（toolExecution.ts:337）

1. **别名解析**：当前池找不到退全量表且只认别名命中（旧 transcript 的 KillShell→TaskStop）；未知工具产 `<tool_use_error>` + 遥测；MCP 归因（`mcp__server__tool` 反查传输类型）
2. **输入验证**：zod safeParse 失败返回 InputValidationError；deferred 工具 schema 未发送则提示先 ToolSearch
3. **PreToolUse hooks**：产出翻译为 progress/权限裁定/updatedInput/preventContinuation/stop
4. **权限裁定**：`resolveHookPermissionDecision` 封装不变式——**hook 的 allow 不绕过 settings 的 deny/ask 规则**（hook 放行仍要过 checkRuleBasedPermissions）；`requiresUserInteraction()` 工具即使 hook 放行也必须走 canUseTool（toolHooks.ts:347-405）
5. **执行**：进度回调与结果通过手搓 Stream 汇合同一条 async iterable；**OTel 双 span**：startToolSpan/startToolBlockedOnUserSpan 分开"等用户"与"真执行"耗时（:909-914）——权限弹窗等待不污染执行统计。**backfillObservableInput 权衡**：hooks/权限看到打过补丁的输入（路径展开），但传给 call() 的必须原始路径——工具结果字符串嵌着这个路径，改动会破坏 VCR fixture 哈希
6. **PostToolUse hooks**：**MCP 工具与非 MCP 顺序相反**——非 MCP 先落结果再 hooks；MCP 反过来因 hook 可返回 updatedMCPToolOutput 改写输出
7. **错误分类**：不用 `error.constructor.name`（minify 后三字符）而用 classifyToolError（TelemetrySafeError/errno/显式 .name）；权限拒绝后的 `executePermissionDeniedHooks` 若返回 retry:true 追加 meta 消息"该命令现已批准可重试"——**拒绝成为 hook 可参与的协商过程**

## 5. Bash 三层防线（BashTool 1.2 万行）

决策总线 `bashToolHasPermission`（bashPermissions.ts:1663）：

**第一层：AST 解析**。tree-sitter 解析出 simple/too-complex/parse-unavailable 三态；too-complex 直接 ask（但先跑 checkEarlyExitDeny 保证显式 deny 不被降级）。legacy 路径 `bashSecurity.ts`（2592 行）是**"解析器差异攻击"编目：23 项编号检测**（bashSecurity.ts:77-101）——IFS 注入、`/proc/*/environ`、Unicode 空白、zsh `=cmd` 等号展开（`=curl evil.com` 被 zsh 展开成 `/usr/bin/curl evil.com` 绕过前缀规则）。CR/LF 差异：shell-quote 把 CR 当词分隔符、bash IFS 不含 CR（:2339-2346）。非 misparsing 的 ask 被"延迟"，跑完全部 misparsing 验证器再定（攻击样本：`cat safe.txt \; echo /etc/passwd > ./out`）。

**第二层：策略**。规则匹配三态（exact/prefix/wildcard）；归一化先剥离输出重定向（`Bash(python:*)` 能匹配 `python script.py > out.txt`）；deny/ask 剥离更激进——迭代剥安全包装到不动点（`nohup FOO=bar timeout 5 claude`）；**allow 规则有意不这么剥**（HackerOne #3543050：否则 `LD_PRELOAD=evil allowed_cmd` 被放行）。防绕过：prefix 强制词边界（`ls:*` 不匹配 `lsof`）。分类器：deny/ask 自然语言规则用 Haiku 并行分类；**推测性分类器**把一次网络调用延迟藏进用户看弹窗的时间（startSpeculativeClassifierCheck 提前发起，弹窗期间消费，高置信且用户未交互则自动批准）。只读推断 `COMMAND_ALLOWLIST` 白名单+flag 解析：**拒绝任何含 `$` 的 token**（`git diff "$Z--output=/tmp/pwned"`：校验器看是位置参数、bash 展开成任意文件写）；白名单注释就是攻击史——`fd -x/--exec` 排除（对每个结果执行命令）、`xargs -i/-e` 移除（GNU getopt 可选附着参数语义差异可致代码执行）。git 三守卫：复合命令同含 cd 和 git 不放行（防恶意仓库 core.fsmonitor/hooks）；bare 仓库结构不放行；写 git 内部路径再跑 git 不放行。

**贯穿原则：deny 不可被降级为 ask**——三层防线单调性，任何层升级严格判断不被后续放松。

**第三层：运行时**。路径约束 `checkPathConstraints`：进程替换 `>(cmd)` 直接 ask（写入目标不出现在重定向里）；管道各段 allow 后仍须对**原始命令**跑路径检查（分段处理剥掉重定向，`echo 'x' | xargs printf '%s' >> /tmp/file` 的 `>>` 会漏检）。沙箱决策 shouldUseSandbox：排除清单"是便利特性而非安全边界"（文件头声明）；`autoAllowBashIfSandboxed` 开启时无显式 deny/ask 的命令**在沙箱内直接放行——弹窗这一步被沙箱隔离替代**（信任从"逐条审批"转移到"限制爆炸半径"）。模型可传 `dangerouslyDisableSandbox:true`（写在公开 schema）但是否生效取决于策略位，且每次绕过体现在输出标志上并触发审批；沙箱违规不静默——annotateStderrWithSandboxFailures 写进输出，模型后续轮次能读到失败原因。

**sed 特例**：`sed -i 's/a/b/' file` 语义是文件编辑——`parseSedEditCommand` 严格解析（恰好一个表达式一个文件、flags 白名单），解析成功走"**预览即执行**"：用户批准的是预览的新文件内容，批准后写 `_simulatedSedEdit` 字段，call 检测到就 `applySedEdit` **根本不执行 sed**（JS 侧替换，BRE→ERE 转义方向反转 + 随机盐防 `&` 注入）；该字段被刻意从模型可见 schema 剔除。PowerShellTool 是同构镜像（威胁模型按 PS 语义重写：IEX/download cradle/参数缩写/Unicode 破折号/New-Item SymbolicLink 的 TOCTOU）。

**模型可见 prompt 是最后防线**：把模型从 find/grep/cat/sed 引导向专用工具（"better user experience and easier to review"）；沙箱配置 dedup + per-UID 临时目录归一成 `$TMPDIR` **保持跨用户 prompt 缓存命中**；PowerShell prompt 检测 5.1/7 版本切换语法段（模型训练数据覆盖两版却无法分辨目标）。

## 6. 搜索与扩展面（06/13/14/16 篇要点）

- **06 篇：无向量索引**——搜索靠 ripgrep 进程、定位 glob、语义 LSP、文件选择手写模糊匹配器。**在 2026 年的最强 coding agent 里 RAG 不是必需品**
- **13 篇 MCP 客户端**：连接/OAuth/`mcp__server__tool` 命名空间；MCP 工具在 client 层动态创建，assembleToolPool 合并
- **14 篇 Skills**：渐进式披露——能力做成可分页资源（与 Skills生态全景卡互锚）
- **16 篇 Hooks 引擎**：`utils/hooks.ts` 单文件 **5,022 行**、**27 个生命周期事件、五种形态**（shell 命令/LLM 判断/HTTP 回调/SDK 回调/函数钩子）——五档接入成本对应五档破坏面，安全机制（trust 闸门/allowlist/SSRF 段表）按梯度叠加；协议分层：stdin JSON 输入 + 退出码与 stdout JSON 双通道输出；**决策归一：blockingError 与 preventContinuation 收敛为 AggregatedHookResult 统一字段，主循环单点消费**

## 7. 可借鉴清单

1. **fail-closed 默认值 + 抛异常即降级**——一切不确定走串行/ask
2. **按输入判定安全性**——isConcurrencySafe(input) 而非静态属性
3. **推测性分类器**——把审批延迟藏进用户看弹窗的时间
4. **deny 单调性**——多层防线中 deny 永不升级为 ask
5. **预览即执行**（sed 通道）——批准语义对象从命令变为效果
6. **`_=Infinity` 防落盘循环**——工具结果上限的特例思维
7. **双 span 计时**——"等用户"与"真执行"分开统计
8. **无向量索引**——grep+glob+LSP+fuzzy 对代码库足够；RAG 是选项不是前提

📌 下一步：04 篇——上下文工程三件套（装配/缓存/五层压缩）。
