# agent-security 新人上手指南（ONBOARDING）

> 图谱口径：1209 节点 / 2725 边 / 16 层 / 16 步 tour @3cf4c82a，fingerprints 400 文件。行号锚均经源码核实（2026-11-02）。

## ① 项目定位：四子系统安全合集

**openJiuwen-ai/agent-security 是面向 Agent 场景的安全能力集合仓**，按纵深防御切为四个独立子系统——各自持 pyproject，仓库根无统一安装入口：

- **agent_shield**（agent-shield）：进程内动作决策 SDK。纯规则、无 LLM、无网络 IO，对工具调用给确定性 allow/ask/deny（tool_permission）；detection 子包只给风险信号不拦截。
- **agent_ssas**（agent-ssas，态势感知）：事件采集+插件化威胁检测+OCSF 威胁报告，框架无关，JiuwenSwarm 集成只是其中一条 rail。
- **jiuwenbox**：沙箱服务。FastAPI 管理沙箱创建/exec/文件传输，policy 驱动隔离——Linux 走 bubblewrap+netns/Landlock/seccomp/cgroup，Windows 走 WFP/Job Object/DACL/受限令牌。
- **foundation**（security-mask）：纯 stdlib 流式脱敏基件——README 未列的第四子系统。

三者互不启动、不组单进程：agent_shield 在调用方进程内裁决；agent_ssas 经 patch 以 Rail 插桩 jiuwenswarm（priority=80，观察前序 Rail 的 deny）；jiuwenbox 是独立服务。上游主站在 AtomGit/gitcode（online patch 从 gitcode.com/openJiuwen/agent-security.git 拉取，patches/jiuwenswarm_ssas_online.patch:156），本仓是同源镜像。

## ② 技术栈与代码形态

全部 Python ≥3.11。agent_shield 零运行时依赖、flat layout（`package-dir={"agent_shield"="."}`，pyproject.toml:28），可选 tree-sitter-bash 解析 shell；agent_ssas 运行时仅 pyyaml、src layout（pyproject.toml:37），HTTP 模式装 fastapi/uvicorn/httpx extras；jiuwenbox 依赖 pydantic/fastapi/uvicorn/httpx/mcp，双 console scripts；foundation 零依赖。Windows 原生层一块 C：softdelete.c 3856 行 Detours DLL 预编译随 wheel。

形态四特征：**四包四布局**（flat/src 混存）；**测试即架构**（facade 契约、状态机转换表都活在测试侧）；**零网络裁定纪律**（netguard 校验宿主 DNS 快照而非自己解析，address_policy.py:3）；**镜像痕迹**（sandbox_daemon.py:126 帧函数是 daemon_ipc 的刻意镜像拷贝）。

## ③ 目录结构导览（对应图谱 16 层）

- **L01** 根+docs/+foundation/：双语 README 与开发指南、security_mask（25 文件）
- **L02-L06 agent_shield**：L02 引擎总装 engine/manager/routing/component（11）；L03 fileguard——file_guard.py 1021 行主判定+路径策略/不可变控制面（16）；L04 命令三守卫 toolguard/hostguard/delguard（17）；L05 netguard 八件套+detection 四路后端（13）；L06 测试线含 netguard 审计回归（34）
- **L07-L12 agent_ssas**：L07 内核 core_types/settings/存储/module_manager（16）；L08 流水线 pipeline/preprocessor/aggregator/detection_modules（29）；L09 access_adapter+backend_client（23）；L10 测试金字塔+事件工厂（43）；L11 design/patches/examples（28）；L12 en/zh 双语文档树（33）
- **L13-L16 jiuwenbox**：L13 policy.py 982 行+六份策略 YAML+1309 行 CLI（21）；L14 server 总装+sandbox_manager 1412 行+隐私代理（27）；L15 supervisor 隔离链+win_*+softdelete.c（24）；L16 docker 三镜像+4990 行 API 集成旗舰+system_tests（48）

## ④ 核心数据流

### 4.1 agent_shield 权限裁决链
PermissionManager（manager.py:21，进程级 key→配置表）→ `check_permission`（engine.py:121）→ `build_candidates`（:216）按 Table A 命令入口表（routing.py:52）剥壳展开候选 → 九组件逐一 evaluate（Injection/CommandAllowlist/DestructiveWarning/TieredPolicy/HostGuard/FileGuard/DeletionGuard/ImmutableControlPlane/NetGuard）→ approval 短路（:280）→ `_merge_results` 取最严（:436）；更新走 `_install` 原子换装（:97）失败保旧，warning-only 结果绝不单独放行。双管线：命令侧 tiered.py 裁决链 approval_overrides→规则→基线→defaults→shell 兜底 ASK+四守卫结构地板（tiered.py:34）；文件侧 file_guard.py 编译 EffectiveFileGuardConfig（:248）逐访问取最严。

### 4.2 agent_ssas 事件流水线
AgentSSASSecurityRail（priority=80，agent_ssas_security_rail.py:61）组装 IDManager→EventBuilder→EventFilter→EventReporter → EventFilter 识别 deny 场景改写 event_type=permission_interrupt_tool（event_filter.py:43，policy_deny=medium :91）→ 上报，异常 fail-open 返回 SecurityAllow（event_reporter.py:46-51）→ AgentSSASBackend.report_event（agent_backend.py:139）：raw_event 先落库→preprocessor 展开派生/基础/聚合三类事件（三级 LRU）→ pipeline 分流：notify 后台 create_task，auth 同步等待、超 auth_timeout（默认 2s）降级（pipeline.py:111-116）→ 单模块链 建模→分析→存储→OCSF 呈现 → 有风险统一写 alerts 表，threat_log 落盘 threat 报告 JSON（threat_log.py:25）。

### 4.3 jiuwenbox 沙箱请求生命周期
launcher 启动（默认 0.0.0.0:8321，launcher.py:30）→ app.py lifespan：按平台装后端、PolicyReader 三级解析策略（构造参数→JIUWENBOX_POLICY_PATH→bundled default，policy_reader.py:23；is_proxy_only 时跳过沙箱 :92）→ SandboxManager 协调 runtime adapter，registry 按平台选后端（registry.py:39）→ process.py（3180 行）每沙箱一次性 spawn bwrap → supervisor 把 SecurityPolicy 翻译为隔离：bwrap from_policy（bwrap.py:134）、seccomp BPF 写匿名 memfd（seccomp.py:4-5）、landlock_launcher 在沙箱内 apply Landlock 后 compile+exec 载入 daemon——零 execve 约束完整继承（landlock_launcher.py:5-8）→ 后续 exec/文件操作走沙箱内 daemon 帧协议 IPC（sandbox_daemon.py:126）。

## ⑤ 关键模块深潜

### 5.1 netguard——零网络出站判定
快照校验架构：不发起任何网络调用，只校验宿主提供的 DNS 快照（1-64 个 IP 字面量，address_policy.py:299）与连接地址一致性，混合地址类永不放行，防 rebinding 复用旧 allow；地址分类用 64K 项 IPv4 /16 查表（bytearray(65536)，:130）。URL 规则编译为 exact/prefix/suffix 三索引（component.py:36-38），上限 10000 条，容量满 fail-closed。iptext.py 让地址常量以参数书写，防扫描器误报。

### 5.2 test_import_rules.py——惰性 facade 的 fitness function
114 行六测：包根零导出（:49，子进程干净解释器验证 `import agent_shield` 后 dir() 无公开名）、facade 名可解析（:65）、guard 目录不公开（:70）、子模块必须相对导入（:77）、不 import 兄弟项目（:92）、其他项目只从子模块根导入（:104）。重构包结构前先跑它。

### 5.3 softdelete.c——3856 行 Detours 软删除
Detours 挂钩 NtCreateFile/NtDeleteFile/NtSetInformationFile/DeleteFileW/RemoveDirectoryW/CreateProcessInternalW 等 NT 级 API（:346-355），删除转回收站移动或同卷归档改名，必要时 TCP 询问 box-server recycle broker；CreateProcessInternalW 钩子以挂起子进程+导入表补丁实现进程树级联注入，补丁失败仍 resume——"命令必须能跑，软删尽力而为"的 fail-open 边界（:31-42）。

### 5.4 IDManager——session 级序号 LRU 池
OrderedDict LRU 池（上限 100 session，id_manager.py:47/:55）维护三类自增序号，解决 DeepAgent 外层与 ReActAgent 内层 ctx.extra 不跨层共享；分析侧 preprocessor 复刻同款三级 LRU。

## ⑥ 设计决策与权衡

1. **fail-open 哲学贯穿但边界刻意画清**：ssas 全链 fail-open——任一环节故障返回无风险结果（agent_backend.py:155）；反向两处 fail-closed——shell AST 解析不可用且检出风险结构必须抬升（shell_ast.py:10-11）、box 安全能力协商缺失抛 CapabilityUnsupportedError 绝不静默降级（runtime/capabilities.py:56）。**观测层 fail-open，裁决与隔离层 fail-closed**。agent_shield 守护的是工具层边界，原生代码仍需 box 的 OS 级隔离兜底。
2. **0.0.0.0 默认 + 零认证的现实**：ssas 的 decision_policy 默认 observe_only 全放行（settings.py:81），但 http_host 默认 "0.0.0.0"（:53）而 http_token 默认 None（:52）——HTTP 模式开箱即全网卡无认证；modes/http/server.py:12 docstring 写"未设 SSAS_HTTP_HOST 时只绑定回环"，与 settings 实际默认矛盾（HTTP 暴露勘误：文档读着安全、跑着暴露）。box 同款：默认 0.0.0.0:8321（launcher.py:30），Bearer 认证 opt-in，未设 JIUWENBOX_API_TOKEN 完全放行（auth.py:13）——部署必须显式配 token 或防火墙。
3. **agent_moss 未分发与 enterprise-policy 孤儿**：README.zh.md:52、开发指南与 CHANGELOG:22 三处声称"3 个内置检测模块（agent_moss/security_rail_detection/test_detection）"，design/README.md:12 还引 AgentSSAS_04 设计文档——实际 detection_modules/ 只有后两者+common，04 文档不存在。box 侧 configs/enterprise-policy.yaml 全仓零引用，仅是备用模板。
4. **Windows/Linux 双线对称而非移植**：Linux=bwrap+netns+Landlock+seccomp+cgroup；Windows=两跳启动绕权限墙（win_exec.py:2-6）+Job Object 等价 cgroup+WFP 回环代理+合成 SID DACL+Detours。win_* 模块顶层零 win32 import，Linux 可直接跑单测。
5. **上游 AtomGit 镜像**：online patch 从 gitcode.com/openJiuwen/agent-security.git subdirectory=agent_ssas 拉取（:156/:164）——上游主站在 AtomGit/gitcode，本仓是镜像，改动同步两侧。
6. **状态机转换表活在测试侧**：SandboxPhase 五态的合法转换表 VALID_TRANSITIONS 只定义在 tests/system_tests/test_utils.py:217-218，生产代码不强制——加状态先改这张表。

## ⑦ 常见任务上手

- **加检测模块（ssas）**：detection_modules/<name>/ 建 module.yaml（name/enabled/subscribed_events/plugins 双插件，参考 security_rail_detection/module.yaml）+ 建模与分析插件各一（model_type 配对）。无需改框架；模块仅初始化时扫描一次，重启生效。启用二选一：宿主 config.yaml 的 `ssas.modules.<name>.enabled` 覆盖（推荐）或改包内 yaml。验证：启动日志 + `<storage>/modules/<name>/` 目录。
- **改沙箱策略（box）**：六份内置 YAML 在 src/jiuwenbox/configs/，自定义用 JIUWENBOX_POLICY_PATH。校验全 fail-closed：路径必须绝对、deny-by-default 网络必须配白名单、安全能力缺失抛错（policy/capabilities.py:78）。改 models/policy.py 须过 loader 的 schema_version 兼容测试（tests/unit/test_policy_unified.py）。
- **跑测试**：四子系统独立跑。agent_shield：`cd agent_shield && uv run pytest`；agent_ssas：`make check` 或 `uv run pytest`（207 用例基线）；jiuwenbox：`uv run pytest tests/unit` 跨平台，integration/system_tests 需起 server 与 Linux 工具链，不足自动 skip。零网络体验：examples/inprocess_quickstart/main.py。

## ⑧ 新人提示与坑

1. **四包名映射与布局分裂**：pip 名 agent-shield/agent-ssas/security-mask，import 名下划线化，jiuwenbox 同名；仓库根无统一安装入口须分目录装。agent_shield 是 flat layout（pyproject.toml:28）而 ssas/box 是 src layout——在错误层找源码是第一大时间坑。
2. **agent_shield 导入铁律**：包根零导出（agent_shield/__init__.py:7），必须 `from agent_shield.tool_permission import PermissionEngine`；toolguard/fileguard/netguard/hostguard 非稳定路径。
3. **test_verify_phase3 文件头笔误**：自述 `python -m tests.verify_phase3`（test_verify_phase3.py:3/:11）并残留 Windows 开发机路径——实际模块路径是 tests.agent_ssas.core.integration，照注释跑必 ModuleNotFoundError。
4. **同源镜像与刻意镜像双坑**：仓级——本仓是 AtomGit/gitcode 上游镜像，改动同步两侧；文件级——sandbox_daemon.py 与 landlock_launcher.py 是"刻意零仓内 import"的独立执行体，改 daemon_ipc.py 帧协议必须手动同步 sandbox_daemon.py:126 的镜像拷贝。
5. **文档差集清单（读文档后回源码对默认值）**：README 未列 foundation；agent_moss 三处提及但未分发；modes/http/server.py:12 回环声明与 settings.py:53 矛盾；enterprise-policy.yaml 无消费者。
6. **测试环境前提**：ssas 测试靠根 conftest 分配独立 SSAS_HOME 临时目录（隔离 SQLite WAL 锁）；netguard 测试线复用同一对工厂（tests/netguard/test_net_guard.py），test_audit_regressions.py 每用例对应一条已修复绕过路径——改 netguard 匹配逻辑先读它。
