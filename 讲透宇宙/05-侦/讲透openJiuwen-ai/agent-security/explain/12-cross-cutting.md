# 12 · 横切视图：fail-open/fail-closed 三层分区、四子系统边界与测试资产盘点

## 一、角色定位

本篇不做单模块精讲，而是回答三个读完全仓才会浮现的问题：**同一仓里为什么 ssas 处处 fail-open、shield 的 Shell 路径 fail-closed、box 里两种都有——判据是什么？四个子系统（agent_shield / agent_ssas / jiuwenbox / foundation）到底怎么协作？878 个测试在守护什么、又有哪些"文档态领先代码态"的差集？**

先钉一个结构事实：四子系统**零交叉 import**（全仓 grep 实证：agent_shield、agent_ssas、jiuwenbox、foundation 互不引用对方包）。它们不是微内核上的插件，而是**同一安全理念在四个执行位的独立落地**，真正的耦合点只有运行时数据约定（ctx.extra 标志、AgentSSASBackendProtocol）。分仓的意义是部署形态自由组合：宿主可以只装 shield 不装沙箱，或只跑 ssas 的 HTTP 服务。

## 二、内部结构：fail 语义的三层分区

把全仓的失败处理摆在一起，判据清晰得像一条公理——**"故障时阻断主业务吗"**：

### 观测增强层 → fail-open（挂了也放行）

- **agent_ssas 全线三层兜底**：EventReporter 异常返回 `SecurityAllow()`（agent_ssas/src/agent_ssas/backend_client/openjiuwen/event_reporter.py:44-51）；引擎 report_event 大 try 返回无风险 `RiskAssessment()`（agent_ssas/src/agent_ssas/core/framework/access_adapter/agent_backend.py:207-212）；HTTP 客户端网络异常合成 Safe（agent_ssas/src/agent_ssas/core/framework/access_adapter/agent_remote_backend.py:83-87）。auth 检测超时也不抛异常，按 module.yaml 策略合成默认报告（allow 合成无风险，pipeline.py:342-358）。
- **shield 的例外区**：deletion_guard 解析失败/目标不可访问时 fail-open 返回 None 只告警，"由既有规则兜底"（agent_shield/tool_permission/delguard/deletion_guard.py:9, :138）。
- **box 的软删除**：回收站/归档/broker 不可用回落原始删除，"命令必须跑成"（jiuwenbox/src/jiuwenbox/native/softdelete/softdelete.c:8-10）。

共同点：这些组件的价值是**增量防御或旁路观测**——它们失效时，主业务的正确性不依赖它们（ssas 挂了事件不分析而已；softdelete 挂了删除照常发生）。阻断它们等于让可选增强变成单点故障。

### 决策拦截层 → fail-closed（拿不准就拦）

- **shield Shell 命令权限**：规则/approval/baseline/defaults 全部 miss 时，Shell 落 ASK 而非放行——tiered.py 注释一句话钉死立场："Shell stays fail-closed; non-shell abstains so Net/File can speak alone"（agent_shield/tool_permission/toolguard/tiered.py:393-395）。非 Shell 工具返回 None 弃权，让 NetGuard/FileGuard 继续发言——弃权本身是精确的（某守卫不认识≠无害）。
- **shell AST 解析**：tree-sitter 后端不可用时保守扫描器把复合/重定向/替换语法降级为 `parse_unavailable`，"callers must fail closed for parse_unavailable + risky structure"（agent_shield/tool_permission/toolguard/shell_ast.py:9-12）。
- **box 的资源限额**：cgroup 不可写但策略要求限额时抛 `CgroupSetupError` 拒绝建沙箱，"rather than silently dropping the limits"（jiuwenbox/src/jiuwenbox/supervisor/cgroup.py:12-14）。

共同点：这些组件的输出**就是主业务的安全边界**——限额定不住的沙箱、判不准的命令，放行的代价由用户资产承担。

### 加固层 → 策略化降级（按配置选边）

- **Landlock** 的 `compatibility: disabled/best_effort/hard_requirement`（default-policy.yaml 默认 best_effort，jiuwenbox/src/jiuwenbox/configs/default-policy.yaml:156）：硬性要求下失败直接退出码 126（landlock_launcher.py:123-127, :239-240）。同一机制、两种立场，交给部署者选。
- **iptables 自保护**：装不上规则时 warning 后继续（process.py:110-114）——无特权 code-agent 部署的既定取舍。
- **seccomp/Landlock/bwrap 本身不可用时**：bwrap 缺失则 bubblewrap runtime 在 /capabilities 里报 unavailable（routes/sandbox.py:81-82），诚实降级而非假装可用。

一句话总结判据：**观测与增强可牺牲，决策与资源边界不可让，加固层看配置**。同一仓里三种子系统各自落在正确的一侧，这个一致性是读代码时最容易被忽视的设计纪律。

## 三、外部连接：四子系统的协作边界

四个子系统的运行时协作面只有三处，全部是**数据约定而非代码依赖**：

1. **AgentSSASBackendProtocol**（agent_ssas/src/agent_ssas/core/framework/access_adapter/protocol.py:16-32）：ssas 引擎与宿主 Rail 之间的唯一跨仓契约，32 行 Protocol，report_event 一个方法。进程内/HTTP 两实现（07 篇）。
2. **ctx.extra["_skip_tool"] / ["_interrupt_decision"]**：shield 的 PermissionInterruptRail（priority 90）先跑并写入 deny 标志，ssas 的 Rail（priority 80）后跑读到该标志，把普通生命周期事件改写为 `permission_interrupt_tool` 安全检测事件（agent_ssas/src/agent_ssas/backend_client/openjiuwen/event_filter.py:37-45；priority 排序见 agent_ssas_security_rail.py:54-61）。这是 shield→ssas 的单向事件衍生：拦截者不知道观测者，观测者靠优先级约定观察拦截者。
3. **策略 YAML 六档**（jiuwenbox/src/jiuwenbox/configs/）：default（isolated 网络，注释范本）/ java（无出网）/ windows（wfp_loopback_proxy:48-51）/ inference（8322 代理档，listen_port 0 默认关）/ code-agent（`mode: host` 全家族最宽面，:99-100）/ enterprise（**孤儿**——src 与 tests 全仓零引用，grep 实证；名字最像生产档却无任何代码路径加载它）。

jiuwenswarm 宿主（patch 文件在 agent_ssas/patches/）把 ssas 接入 swarm 进程；shield 与 box 由宿主按需装配。foundation/security_mask 仓内零消费（11 篇），是给仓外调用方预备的 stdlib 件。

## 四、数据流：默认暴露面与信任边界

全仓两张默认全网监听的口子，构成部署时的第一信任边界：

- **8321**（jiuwenbox 管理 API）：`DEFAULT_LISTEN = "http://0.0.0.0:8321"`（jiuwenbox/src/jiuwenbox/server/launcher.py:30），Bearer 认证 opt-in——不配 token 中间件直接放行（server/auth.py:45-55）。
- **8443**（agent_ssas HTTP 服务）：`http_host: "0.0.0.0"`（agent_ssas/src/agent_ssas/core/framework/config/settings.py:53-54），`http_token` 默认 None 时 TokenAuthMiddleware 压根不挂载（access_adapter/http_server.py:114-116）。

对照面：8322 隐私代理默认关（listen_port 0）、60080-60089 仅回环且 WFP 强制、daemon 控制 socket 走 pass_fds 的 Unix socket 在沙箱外（sandbox_daemon.py:32-40）。**带密钥的面默认关、不带密钥的面默认开**——这个不对称是刻意的（密钥泄露不可逆、管理面暴露假设有防火墙），但部署清单必须把"8321/8443 加 token 或改回环/UDS"列为第一项。

第二信任边界在沙箱内→外：code-agent 的 host 网络档下，iptables 按 sandbox-uid 阻断到 8321 的回环访问是唯一防线，且无 root 时该防线静默缺席（process.py:110-114）。

## 五、设计决策与权衡

1. **分区判据外显为注释纪律**。三个子系统的关键失败路径都有"为什么选这边"的注释（tiered.py:393、cgroup.py:12-14、softdelete.c:8-10）——失败语义在这个仓里是被当作 API 设计的，不是实现的副产品。
2. **弃权（None）作为第三态**。shield 非 Shell 工具在无配置时返回 None 而非 ASK（tiered.py:393-395）：ASK 会打断用户，None 让专业守卫先说。三态决策（allow/deny/abstain）比二态多出"组合判断"的表达力，代价是调用方必须处理 None 语义。
3. **配置孤儿是文档债的另一种形态**。enterprise-policy.yaml 与 agent_moss（08 篇）同类：宣称的体系比发行的体系大。CI 不校验"配置文件有消费者"，也不校验"README 模块在目录里"——文档态领先代码态的差集只能靠 grep 盘点。
4. **测试按金字塔分层且平台隔离干净**（见下节盘点）：unit 不碰真内核，system 需真环境标 `system` marker 由 CI 跳过（agent_ssas/pyproject.toml markers 定义）。

## 六、新人提示与坑：测试资产盘点

全仓测试规模（test_*.py 文件数 / 用例数，grep def test_ 计）：**agent_shield 29 文件 393 例、jiuwenbox 27 文件 352 例、agent_ssas 31 文件 123 例、foundation 1 文件 9 例——合计 88 文件约 877 例**。结构盘点与替身手法：

- **状态机转换表活在测试侧**：沙箱状态机（provisioning→ready/error、ready→stopped/error/deleting、stopped/error→ready/deleting、deleting 终态）的权威定义不是 models 里的枚举，而是 `StateMachineValidator.VALID_TRANSITIONS`（jiuwenbox/tests/system_tests/test_utils.py:214-223）。改状态机先改这张表，否则系统测试用旧表判新实现。类似地 ssas 的 pyproject 定义了 level0/level1/slow 等 marker 分层（agent_ssas/pyproject.toml），PR 门禁只压 level0。
- **Linux CI 上测 Windows 线的三套替身**：① `sys.modules` 注入假 win32security——`_fake_dacl` 用 SimpleNamespace 伪造 GetAceCount/GetAce（tests/unit/test_win_softdelete_env.py:33-47），无 pywin32 也能跑 DACL 断言；② 反向平台替身——monkeypatch `sys.platform="linux"` 专测"非 win32 必须拒绝"的守卫（tests/unit/test_windows_runtime.py:33-36）；③ 函数级替换——`win_proxy.resolve_upstream = fake_resolve`（tests/unit/test_win_upstream.py:250-253）。真 Windows 专属用例才 skipif（test_win_softdelete_env.py:13）。
- **系统测试需要真实 root 与内核特性**（bwrap/cgroup/stress-ng OOM 触发器见 test_utils.py:202-210），CI 里整体跳过——**本仓的 CI 绿不代表沙箱真能建**，改动 supervisor 线必须在有 root 的 Linux 上跑 system 套件。
- **双系统默认暴露**（8321/8443）与 **agent_ssas 的 HTTP 模式在 jiuwenswarm online patch 下**是三个容易在渗透测试里最先被打的点；排查时先看 `get_configured_token()` 是否为 None。
- **跨仓排障入口**：shield 的行为查 tests 的 fixture 与 builtin_rules；ssas 查 docs/zh/explanation/（其中 agent_ssas/docs/zh/explanation/detection-pipeline.md:106 明言当前全 notify 模式，别按 auth 排障）；box 查 tests/integration/ 的三套 default 测试（cli/mcp/server）；foundation 只有 9 例，是唯一"测试即全规格"的包。
- 最后一条工程纪律：这个仓的代码注释密度极高且大量记载"为什么"（挂载顺序、BPF 跳转、全角星号、fail 语义）。**改行为前先读注释里的历史决策，很多"看起来能简化"的地方是事故现场**——bwrap 排序、seccomp 跳转偏移、markdown 星号三处都有测试守护，动了先跑对应守护测试。
