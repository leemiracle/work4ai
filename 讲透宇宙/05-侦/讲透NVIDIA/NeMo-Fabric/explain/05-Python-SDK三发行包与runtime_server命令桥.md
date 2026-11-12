# 05 · Python SDK 三发行包与 runtime_server 命令桥

> 仓库：NVIDIA/NeMo-Fabric @ 86f86882 · sdk/python/{nemo-fabric-runtime, nemo-fabric-collector, nemo-fabric-adapter-catalog}

## 一、角色定位

Python SDK 面向**消费者一侧**——应用、评测框架（Harbor）、rollout 平台从这里接入 Fabric。三个 PyPI 包分工明确：

- **nemo-fabric-runtime**（主包，11471 行）：Fabric 类全生命周期客户端 + models/types 双模型层 + streaming 双流实现 + runtime_server 子系统 + harbor 集成。依赖刻意极窄：httpx/pydantic/typing-extensions（pyproject dependencies），Rust 扩展 `_native` 打包在内。
- **nemo-fabric-collector**（1460 行）：独立遥测采集服务，app.py 单文件 1266 行，starlette+uvicorn 起 HTTP 面，入口脚本 `nemo-fabric-collector`（pyproject [project.scripts]）。
- **nemo-fabric-adapter-catalog**：零依赖纯元数据包，__init__.py:9 钉版"Inspect bundled adapter metadata **without loading executable adapters**"——18 个 adapter + 2 个 target descriptor（catalog.json 2792 行，nvidia.fabric.claude/cline/codex/droid/hermes/kilo/kiro/langchain.deepagents/mini-swe-agent/nooa/nooa.bench-agent/openclaw/opencode/openhands/pi/qwen/remote-agent/strands + nvidia.nooa.arc-solver/coding-agent）。

runtime_server 是 SDK 内嵌的**沙箱内命令桥**：OpenShell 沙箱里的任务侧进程通过 Unix socket 与宿主通信的协议入口（runtime_server/__init__.py:7 "消费方中立的运行时服务器与本地命令桥 fabric-agent-ctl"）。

## 二、内部结构（带行号）

### Fabric 客户端（client.py 982 行）

client.py:56-59 的 try/except import 把 `_native` 缺失降级为 None；class Fabric（client.py:68）docstring（:69-86）就是 SDK 使用契约："每个生命周期方法接受完整 typed FabricConfig + 可选 base_dir；在 Python 侧组装变体再调 SDK；doctor/plan/run 返回 typed 只读模型；显式环境用户走 prepare/attach_environment → start_runtime_in → release_environment 分步"。__init__ 无状态（:88-89 一行 pass）。

方法地图：check(:91)/plan(:205)/doctor(:244)/run(:285)/start_runtime(:334)/prepare_environment(:402)/attach_environment(:483)/start_runtime_in(:526)/release_environment(:574)/_start_runtime(:600)/prepare_service(:804)/attach_service(:853)。run 的实现（:322-332）三步：plan → `expected_descriptor_sha256` 非空则 `_verify_adapter_descriptor` 拒绝 descriptor 漂移（:294-295 docstring："Reject descriptor drift before starting the runtime"）→ `_run_native_lifecycle`。client.py:64 的 `_CHECK_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="fabric-health")` 专门跑健康请求——调用进行中的探活不与主调用抢线程。

runtime.py 承接 Runtime(:70)/RuntimeStatus(:48) 活动句柄；`_PI_ADAPTER_ID = "nvidia.fabric.pi"`(:44) 是内置兜底适配器；_call_blocking(:1053) 把 Rust 阻塞调用搬进 executor 不堵 event loop；_run_native_lifecycle(:975) 是统一的 native 调用+错误归一层。

### 三模型层

models.py（1387 行 34 类）是 Pydantic **写作面**（FabricConfig 顶层 12 方法）；types.py（2642 行 43 类）是**读取面**——内部 _*Config 冻结快照层（_FabricConfigSnapshot 17 个方法）之上暴露 RunPlan/DoctorReport/RunResult/RunOutput/RunUsage 与 Environment/Runtime/Service 三类 handle。__init__.py barrel（:6-30+）re-export 全部公共名，是 `from nemo_fabric import ...` 唯一入口。

### runtime_server 子系统（五件套）

- **protocol.py**（288 行）是线格式宪法：INTERFACE_VERSION=2（:13）、REQUEST_LIMIT=512 KiB（:14）、RESPONSE_LIMIT=4 MiB（:15）、CALL_SECONDS=320（:16）、SOCKET_PATH=`/sandbox/fabric.sock`（:19）、OPERATIONS=(start,invoke,stop,serve,check)（:20）。MESSAGES 字典（:23-51）把每个响应码钉成固定文案——`runtime_exists` 条目的注释（:43-44）直说"保持 v2 响应码可识别，兼容仍然强制单 start 的旧 runtime-server 镜像"。ProtocolError（:61）docstring 钉版："固定诊断，**永不包含请求值或原始异常**"——错误信息零信息泄漏。
- **cli.py**（187 行）是 `fabric-agent-ctl` 命令（pyproject [project.scripts] fabric-agent-ctl）：模块文档（:7）"strict named commands and one JSON response per command"。read_input（:29-66）支持 `-`（stdin）与文件路径两态：stdin 走 fileno+select+10s deadline 的手读（:40-53），文件必须 O_NONBLOCK 打开且 stat 校验为常规文件（:57-61），超 512 KiB 直接 invalid_input。
- **transport.py**（374 行）模块文档（:7）"Bounded, single-request Unix socket connections and exclusive host ownership"——有界单请求连接+宿主独占。client(:87)/serve(:193) 是 socket 两端，fcntl 加锁（:44-47 仅 win32 之外）。
- **state.py**（288 行）：OwnedRuntime(:41)/RuntimeServer(:49) 会话状态机，_owned(:67) 校验请求归属。
- **health.py**（207 行）：runtime_report(:23)/check_response(:46)/server_report(:92) 三种探活报告与 validate_check_response(:61)/validate_server_response(:130) 双校验。

## 三、外部连接

- **上游**：Rust `_native` 扩展（fabric-python，20 函数，见第 1 篇）——client.py:915 `_require_native_module` 在扩展缺失时抛 FabricNativeUnavailableError。
- **下游消费者**：integrations/harbor/fabric_agent.py（1082 行）用 Fabric 类把 Harbor 评测任务翻译成 FabricConfig；examples/ 与 skills/nemo-fabric-integrate 也以本包为面。
- **runtime_server 的对端**：fabric-core 的 OpenShellRuntimeAdapter 经环境提供器把 TaskCommand 送进沙箱，沙箱内 fabric-agent-ctl 在 /sandbox/fabric.sock 上应答——这与第 2 篇 read_artifacts.py 的"一次性脚本"形成对照：工件读取无常驻，命令桥常驻。
- **collector**：被 client 的 ATOF collector 注册路径引用（_collector_client.py 238 行），遥测数据面独立成服务。

## 四、数据流

**常规调用**：应用构造 FabricConfig → `Fabric.run(config, input=...)` → client.py:322 plan（线程池里调 native plan_config）→ 可选 descriptor sha256 校验 → _run_native_lifecycle（native run_config，GIL 已由 py.detach 释放）→ RunResult.from_mapping 进 types.py 冻结模型 → 异步返回。

**沙箱命令桥**：沙箱内 CLI 收到 `fabric-agent-ctl invoke <payload.json>` → cli.py parse_command 校验操作名 ∈ OPERATIONS → read_input 读 payload（512 KiB 界）→ transport.client 连 /sandbox/fabric.sock → encode_request 带 interface_version=2 与 agent 归属 → 宿主侧应答单 JSON 响应（4 MiB 界）→ 超界报 response_too_large 且"**outcome is unknown**"（protocol.py:47 MESSAGES 原文）。

**目录查询**：`get_adapter_descriptor("nvidia.fabric.claude")` → catalog.json 重新加载（__init__.py:25-27 注释："每次重载给调用方独立对象，避免可变全局态"）→ 返回未修改 descriptor dict，KeyError 即未知 ID。

## 五、设计决策

1. **三包拆分按"谁需要什么"切**：catalog 零依赖让 UI/文档工具枚举适配器不必装 pydantic；collector 独立部署让遥测面可单独扩缩；主包收全部执行语义。
2. **catalog 是快照不是能力检查**：get_adapter_descriptor docstring（__init__.py:32-35）明确"release snapshot, not a capability check against an installed harness；lookup 既不 import 适配器代码也不注册 runner"——把"元数据查询"与"执行注册"彻底分离，目录查询不可能执行任意代码。
3. **两模型层防误用**：models.py 可变 Pydantic 供构造，types.py 冻结快照供消费——run 返回的 RunResult 不可被应用顺手改掉再当作新输入。
4. **协议错误零泄漏**：ProtocolError 固定文案设计（protocol.py:61）针对沙箱场景——错误对象若回显请求值/异常栈，可能把宿主侧信息漏给沙箱内不可信代码。
5. **超界即未知**：response_too_large 的文案承认"outcome unknown"（protocol.py:47）——不假装失败，把不确定性如实暴露给调用方决策（重试或换沙箱）。
6. **健康探活专用线程池**（client.py:64）：调用进行中的 check 不排队等大调用——评测系统的活性监控不能被长任务饿死。

## 六、新人提示

- 第一行代码写 `from nemo_fabric import Fabric, FabricConfig`，先跑 `Fabric().doctor(config)` 看配置诊断，再 `run`。
- input 与 request 互斥（client.py:288-290 docstring）；要自定义 request_id/context 就传 RunRequest。
- 装了 SDK 但报 FabricNativeUnavailableError，说明发行版没带平台 wheel 的 `_native`——检查 Python 版本与平台支持矩阵。
- 调 runtime_server 问题时先看 protocol.py 的 MESSAGES：所有错误码的文案都在那 30 行里，比猜日志快。
- catalog.json 与实际安装的适配器可能不同步——它是发布快照，真实验证要走 inspect/doctor，不要拿目录当安装清单。
