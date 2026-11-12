# DCGM (Data Center GPU Manager) 新人上手指南

> 基于知识图谱（4261 节点 / 5644 边 / 16 层 / 16 步导览，指纹 1178 文件 @ commit `64df9f89`）与源码逐条核实编写。
> 所有 `文件:行号` 锚点均从仓库源码验证；行数以 `wc -l` 实测为准。
> 版本基线：DCGM 4.6.1（`project(datacenter-gpu-manager-4 VERSION 4.6.1)`，CMakeLists.txt:17）。

---

## 1. 项目定位：DCGM 是什么

DCGM（Data Center GPU Manager，包名 `datacenter-gpu-manager-4`）是 NVIDIA 开源的数据中心 GPU 管理套件，覆盖四大能力面：**监控（monitoring）、诊断（diagnostics）、健康（health）、策略/治理（policy & governance）**。它不是单一工具，而是一套以 `nv-hostengine` 守护进程为核心、CLI（`dcgmi`）、诊断套件（NVVS）、诊断验证库（`dcgmlib`）协同的完整栈：

- **监控**：以字段（field）为统一词汇的遥测采集——`dcgmlib/dcgm_fields.h`（3993 行）用 `#define DCGM_FI_DEV_*` 枚举了全部可监控字段（如 `DCGM_FI_DEV_SM_CLOCK 100`，dcgm_fields.h:554；`DCGM_FI_DEV_XID_ERROR 230`，dcgm_fields.h:806），从时钟/温度/功耗/ECC 到 NVLink/XID/SXID 全覆盖。
- **诊断**：主动式 GPU 验证套件 NVVS（NVIDIA Validation Suite）+ 22 核显存压测 memtest + 多节点 mndiag，由 `dcgmi diag` 触发。
- **健康**：被动式子系统健康判定（内存/PCIe/散热/功耗/InfoROM/NVLink/NVSwitch），见 `modules/health/DcgmHealthWatch.cpp`（3808 行，实测 wc -l）。
- **策略**：七类条件检查器（ECC/PCIe/RetiredPages/Thermal/Power/NVLink/XID）超阈告警，见 `modules/policy/DcgmPolicyManager.cpp`。

**技术栈是 Go+C++ 双栈的形态**——注意：本仓（NVIDIA/DCGM）主体是 **C++23**（根 CMakeLists.txt 设置 `cmake_minimum_required(VERSION 4.0.0)` 于 15 行），Go 生态的对接点在仓外的 `dcgm-exporter`（Kubernetes Prometheus 导出器）与 GPU Operator：运行时镜像 `docker/Dockerfile.ubi9:48-49` 显式 `EXPOSE 5555` 并以 `/usr/bin/nv-hostengine` 为入口"供 dcgm-exporter 等其他容器使用"。即：**C++ 侧是引擎本体，Go 侧是云原生消费端，5555 端口（HostEngineCommandLine.cpp:382 默认值）是两者的契约点**。

**支持平台**：x86_64 与 aarch64（Arm）双架构交叉编译（toolchain 镜像 `ARCHITECTURE=x86_64/aarch64` 双目标）；README 还提及 POWER。发布节奏见 `docs/support_EOL.md`：按 semver 半年一个 X/Y 版本、季度补丁版、每个 Y 版本支持一年。

**仓库规模感**：根 CMakeLists.txt:527-542 以 16 个 `add_subdirectory` 拉起全部子系统（common/config-files/cublas_proxy/dcgm_stub/dcgmi/dcgmlib/dcgmproftester/docs/hostengine/modules/nvml-injection/nvvs/scripts/sdk/sdk_samples/testing）。知识图谱收录 1178 个源文件（指纹基线），核心大文件包括 16530 行的 `DcgmCacheManager.cpp` 与含 6094 行单函数的 `dcgm_fields.cpp`（见第 3 节）。

**一句话心智模型**：`nv-hostengine` 是常驻代理，缓存并调度一切 GPU 遥测；`dcgmi` 是用户入口；模块（health/policy/diag/...）按需懒加载进引擎；NVVS 是被 diag 模块拉起的独立诊断二进制；一切数据最终源自 NVML/NSCQ/NVSDM 三个硬件 SDK。

---
## 2. 架构总览：16 层依赖地图

知识图谱把 1178 个文件组织为 16 层，自底向上可以归并为六大带（文件数为图谱分层统计）：

**带一：common 双层地基（L02+L03，91+98 文件）**
被所有子系统共享的基座。L02 是核心基础设施：plog 日志门面 `DcgmLogging.h`（fanIn=94 全仓第二高，`DcgmLoggingInit` 在 367 行，`log_verbose`/`log_info` 内联模板在 254/267 行）、超时互斥锁 `DcgmMutex.h`（`dcgmMutexSt` 枚举 26 行、`class DcgmMutex` 56 行）、字段 watch 订阅调度表 `DcgmWatchTable.h`（`dcgm_watch_info_t` 80 行、`class DcgmWatchTable` 128 行、`GetFieldsToUpdate` 234 行——它决定下一轮采样谁，是采集节拍的心脏）、传输协议头 `common/transport/DcgmProtocol.h:32`（消息 magic `0xadbcbcad`，pragma pack(1) 紧凑对齐）。L03 是成建制子系统：ChildProcess 子进程管理（asio）、RemoteConn SSH 隧道（`SSHTunnelManager.hpp` 940+ 行，detail 层 `TcpSSHTunnelManager` 571 行 / `UdsSSHTunnelManager` 650 行，公开包装 909/923 行）、CudaLib/CudaWorker CUDA 桥（`FieldWorkers.hpp` 1178 行含八种负载生成器，`FieldWorkerBase` 64 行 + `DoOneDutyCycle` 纯虚 104 行）。

**带二：引擎核心（L05，113 文件）**
`dcgmlib`（C API 库）+ `hostengine`（守护进程）。数据模型总集 `dcgmlib/dcgm_structs.h`（4374 行，fanIn=155 全仓最高——155 个文件 include 它）、agent 契约 `dcgm_agent.h`、内部结构 `dcgm_structs_internal.h`（与公共头分离以稳定对外 ABI）、API 入口点宏体系 `entry_point.h`（1035 行）。详见第 3 节。

**带三：modules 模块四层（L07-L10，32+43+49+61 文件）**
L07 模块框架与 core/config；L08 nvswitch（NSCQ）与 diag（对接 NVVS）；L09 被动治理六模块（sysmon/health/policy/introspect/profiling/vgpu）；L10 mndiag 多节点诊断与 LFS 二进制。详见第 5 节。

**带四：nvvs 三层（L11-L13，116+151+46 文件）**
L11 诊断框架核心（主控/插件基类/dlopen 装载器/记录器）；L12 诊断插件群（memtest/memory/pcie/nvbandwidth/nccl_tests/targetedpower 等）；L13 配置样例（37 套 configfile_examples）与 Python 集成示例。详见第 6 节。

**带五：外围工具与 SDK（L04+L14，71+83 文件）**
独立于主链：nvml-injection（YAML 驱动的 NVML 注入测试体系，8334 行生成头 `InjectionArgument.h`）、cublas_proxy（转发代理库，version-script 限制符号导出）、dcgmproftester（PTX 自旋核压测工具）、sdk/ 三绑定（NVML 12790 行主头、NSCQ 425 行、NVSDM 1243 行）。详见第 4/7 节。

**带六：构建与发布（L01+L15+L16，24+67+64 文件）**
根构建配置与工程约定、包验证黄金清单（verify_package_contents）、dcgmbuild 三级容器镜像链。详见第 8 节。

**关键耦合点**（跨层边）：
- `dcgm_structs.h` ← 155 文件：一切结构体的家，改一处动全身；
- `DcgmLogging.h` ← 94 文件：日志门面；
- `DcgmWatchTable.h` 的 watch 机制连接 CacheManager（生产者）与 health/policy 模块（消费者）；
- `modules/dcgm_module_structs.h` 的 `dcgm_module_command_header_t` 是所有模块消息的公共头（fanIn=16）；
- diag 模块（L08）经 `DcgmDiagManager.cpp:289` 的 `/usr/libexec/datacenter-gpu-manager-4/nvvs` 命令行跨进程拉起 NVVS（L11），是 modules→nvvs 唯一通道；
- NVVS 插件（L12）经 `PluginInterface.h` 的 C ABI 与框架（L11）解耦，`dcgmDiagPlugin*` 回调是边界。

**图谱勘误（源码核实）**：图谱层摘要写的 `dcgmStartDiag_v8` 在源码中不存在——实际 API 是 `dcgmRunDiagnostic`（dcgm_agent.h:1817），请求结构体为 `dcgmRunDiag_v10`（dcgm_structs.h:3593 定义、3598 版本宏；v7/v8 已 @deprecated，见 3444/3480 行注释）。

---
## 3. hostengine 核心：守护进程与采集心脏

### 3.1 入口与守护化（hostengine/src/main.cpp，580 行）

`main` 在 main.cpp:423。启动序列：`ParseCommandLine`（TCLAP，失败即 syslog 报错退出，433-440 行）→ 非 root 仅告警不退出（444-448 行）→ `ShouldTerminate()` 时调 `terminateHostEngineDaemon` 终止既有守护进程（453-456 行）→ `ShouldDaemonize()` 时先 `isDaemonRunning` 查活、`delete_pidfile_if_not_running_or_exit` 清陈旧 pidfile，再 `heDaemonize()`（461-468 行；heDaemonize 定义在 281 行）。

pidfile 生命周期是一组独立函数：`write_to_pidfile`:46、`read_from_pidfile`:71、`isDaemonRunning`:131、`termDaemonIfRunning`:154、`delete_pidfile_if_not_running_or_exit`:188、`create_daemon_pid_file`:205——新人排查"hostengine 起不来"十有八九要先看这几个函数的日志路径。

命令行面（`hostengine/src/HostEngineCommandLine.cpp`）：配置藏在 pimpl `Impl` 结构（35 行），`m_shouldDaemonize`（53 行）、`GetPort`:88、`GetDenylistedModules`:128、`GetServiceAccount`:133（降权账户）。**默认 TCP 端口 5555 在 382 行**——这就是 Dockerfile.ubi9 EXPOSE 与 dcgm-exporter 的对接点。也支持 UDS socket / vsock / 指定 bind 接口（`GetUnixSocketPath`:62、`GetVsockCid`:103）。

### 3.2 DcgmHostEngineHandler：进程内总线（5482 行实现）

`class DcgmHostEngineHandler`（DcgmHostEngineHandler.h:125）是引擎进程内聚合根：持有 CacheManager/GroupManager/连接管理与**模块表** `m_modules[DcgmModuleIdCount]`（h:790）。模块是**懒加载共享库**：构造时只登记文件名（cpp:2407-2417 的 `libdcgmmodulenvswitch.so.4` / `libdcgmmodulehealth.so.4` 等 10 个 .so），首次用到才 `LoadModule`（h:605 声明，cpp:2669 实现）：`dlopen(filename, RTLD_NOW)`（cpp:2729）→ `dlsym` 解析三个 C ABI 符号 `dcgm_alloc_module_instance` / `dcgm_free_module_instance` / `dcgm_module_process_message`（cpp:2741-2743），缺一即判加载失败。模块 ID 枚举在 dcgm_structs.h:4058-4072：`DcgmModuleIdCore=0`（常驻，不走 dlopen）到 `DcgmModuleIdMnDiag=10`，共 11 个 ID、10 个可懒加载 .so。模块间消息统一走 `SendModuleMessage`（h:639）+ `dcgm_module_command_header_t` 公共头。

### 3.3 DcgmCacheManager：16530 行的调度心脏

`dcgmlib/src/DcgmCacheManager.cpp` 实测 16530 行（全仓最大文件），类声明在 `DcgmCacheManager.h:534`（头文件本身 2752 行、196 个方法），事件线程 `DcgmCacheManagerEventThread` 在 h:513。它集中了：字段值缓存与更新调度、watch 管理（消费 `DcgmWatchTable`）、MIG GPU/计算实例追踪（`DcgmGpuInstance`）、NVSwitch watch、事件线程驱动的周期采样。**读它的正确姿势**：从 `DcgmCacheManagerEventThread::OnRun` 的循环入手，追 `GetFieldsToUpdate`（DcgmWatchTable.h:234）返回的字段集如何被派发给 NVML 采集。

NVML 采集的唯一通道是 `NvmlTaskRunner`（NvmlTaskRunner.hpp:95，497 行 28 方法）+ 安全句柄族（`SafeNvmlHandle` hpp:30）——全库 NVML 调用都经此收口，测试注入（nvml-injection）也挂在这一层（`DcgmInjectionNvmlManager.h`）。

### 3.4 dcgm_fields.cpp：6094 行单函数的字段总表

`DcgmFieldsPopulateFieldTableWithFormatting` 从 dcgm_fields.cpp:213 开始、6306 行结束（`}`）——**函数体 6094 行**（6306-213+1），全仓最大单函数，调用点在 6410 行（`DcgmFieldsInit` 静态初始化）。它逐字段登记元数据（类型/单位/tag/NVML 映射/字段宽宽），配合 dcgm_fields.h 的 `#define DCGM_FI_DEV_*` ID 表构成 DCGM 遥测体系的单一事实源。**改字段的流程 = dcgm_fields.h 加 ID + 这个巨函数加登记项**，没有别的入口。

### 3.5 API 层：entry_point.h 宏管道

`dcgmlib/entry_point.h`（1035 行）以 `DCGM_ENTRY_POINT(name, tsapi, args, fmt...)` 宏统一声明每个公共 API（首个条目 `dcgmInjectFieldValue` 在 19 行；末尾 `dcgmAttachDriver`/`dcgmDetachDriver` 1021/1023 行）——既是 API 权威清单，也是把本地调用转投递到 hostengine 连接的模板化管道。对外 C 契约两份：`dcgm_agent.h`（agent 消费者，如 `dcgmRunDiagnostic`:1817）与 dcgm_core_communication.h（libdcgm.so 请求回调全集，972 行）。

---
## 4. dcgmi CLI：Command 命令模式与 dcgmproftester

### 4.1 Command 基类与分派

`dcgmi` 的每个子命令都是 Command 命令模式的实例。基类在 `dcgmi/Command.h`（72 行小而关键）：`class Command`:27、公共入口 `Connect()`:37、`SetPersistAfterDisconnect()`:44、`Execute()`:49，派生类实现纯虚 `DoExecuteConnected() = 0`:57。`persistAfterDisconnect` 语义（成员 m_persistAfterDisconnect 在 64 行）决定客户端断连后 hostengine 是否保留其创建的 watch——**这是长时监控与一次性查询的行为分水岭**。

`main_dcgmi.cpp:54` 的 main 只做环境准备，74 行委托 `CommandLineParser::ProcessCommandLine`。`CommandLineParser.cpp`（3168 行）以成员函数指针 map 分派子系统：`StaticConstructor` 在 100-116 行注册 **17 个子系统**（discovery/policy/group/fieldgroup/config/health/diag/stats/topo/introspect/nvlink/dmon/modules/profile/set/test/mndiag——`dmon` 即 `dcgmi dmon` 实时监控面板，115 行）。子命令头文件一一对应：Query.h/Policy.h/Health.h/Diag.h/MnDiag.h/Config.h/Group.h/Topo.h/Nvlink.h 等（每个文件含 2-6 个 Command 子类）。

输出侧配套两件：`DcgmiOutput.h` 的 Boxer/Tree/Columns/Json 四套格式化抽象（fanIn=18），与 `CommandOutputController.h` 的 display 模板（fanIn=16）。TCLAP 的 DCGM 定制扩展在 `NvcmTCLAP.h`（处理子系统名不参与解析但要出现在 usage 的场景）。

### 4.2 dcgmproftester：验证 profiling 字段的压测工具

`dcgmproftester/` 是独立发布工具，用于制造**可控的 SM/SMSP/周期级负载**来验证 DCGM profiling 字段读数。核心执行体 `DcgmProfTesterKernels.cu`：`waitPerSm`:65、`waitPerSmsp`:79 等 `__global__` 自旋核。关键工程决策：预编译为 `DcgmProfTesterKernels.ptx`（compute_70，由 `buildptx.sh:24-28` 在 CUDA 10.2 容器里 nvcc -ptx 生成），运行时经 **CUDA Driver API** 加载——从而摆脱对特定 CUDA 运行时版本的绑定（与 memtest 的 tests.ptx 同一手法，见第 6 节）。`.ptx` 作为安装资产由 dcgmproftester/CMakeLists.txt:72/77 落盘。外围：`Arguments.h` 652 行参数体系、`DistributedCudaContext.h`（816 行，每 MIG 实例一个 CUDA worker 进程）、`PhysicalGpu.h`（54 方法）。

另有一个小而精的伴生库 `cublas_proxy/`：`cublas_proxy.cpp` 把 cublasDgemm 等 API 转发到真实 cuBLAS，`cublas_proxy.linux_def` 版本脚本只导出 `Dcgm::CublasProxy::*` 符号——让 NVVS 插件与宿主进程的 cuBLAS 版本解耦（按 CUDA 11/12/13 生成三个代理库）。

---
## 5. 模块框架：DcgmModule 契约、policy 七检查器与 health 业务规则

### 5.1 模块契约

一切模块继承 `class DcgmModule`（modules/DcgmModule.h:31）。基类提供两件公共能力：`CheckVersion`（DcgmModule.cpp:25 实现；h:47 声明——比对消息头前 4 字节版本）与自由函数 `PassMessageToModule`（cpp:44）。消息统一以 `dcgm_module_command_header_t`（modules/dcgm_module_structs.h，fanIn=16）打头，先过版本检查再进各模块 `ProcessMessage` 分发。`DcgmModuleApi.h:39` 的 `dcgmModuleSendBlockingFixedRequest` 是客户端向模块发阻塞请求的辅助通道。**装载机制见 3.2 节**：10 个懒加载 .so（nvswitch/vgpu/introspect/health/policy/config/diag/profiling/sysmon/mndiag）+ 常驻 Core。图谱摘要称"八模块"，源码实测为 11 个模块 ID（dcgm_structs.h:4058-4072）、10 个 dlopen 库（DcgmHostEngineHandler.cpp:2408-2417）——以源码为准。

模块访问 core 能力（CacheManager/分组/watch）的唯一通道是 `DcgmCoreProxy`（modules/common/DcgmCoreProxy.h:37，544 行 53 方法；实现 DcgmCoreProxy.cpp 1433 行）——它把 Get*/Set*/watch 请求打包为 core 模块消息（Blob 增长缓冲）。core 模块本体 `DcgmModuleCore`（66 方法）聚合 CacheManager/GroupManager/InjectionNvmlManager。config 模块（`DcgmConfigManager.cpp` 1631 行）治理时钟/功耗上限/ECC/compute mode/sync boost/workload power profile 的 Set/Get/Enforce。

### 5.2 policy：七类条件检查器（告警语义权威）

`modules/policy/DcgmPolicyManager.cpp`（1272 行）以字段值回调驱动判定：`OnFieldValuesUpdate`:107 是统一入口，`SetViolation`:204 是统一出口。**七类条件的 SetViolation 调用点**：ECC 双比特错 `DCGM_VIOLATION_POLICY_FAIL_ECC_DBE`:366、PCIe `FAIL_PCIE`:427、退役页超限 `FAIL_MAX_RETIRED_PAGES`:541、过热 `FAIL_THERMAL`:582、功耗 `FAIL_POWER`:623、NVLink `FAIL_NVLINK`:678、XID `FAIL_XID`:722。用户经 `dcgmi policy` 注册条件+动作（isolate/rollback 等），条件结构在 `dcgm_policy_structs.h` 的 `dcgmPolicy_t`。配套测试 `tests/DcgmPolicyManagerTests.cpp`（约 690 行）注入字段值逐类验证——**改任何告警阈值/语义必须同步它**。

### 5.3 health：3808 行被动健康监视

`modules/health/DcgmHealthWatch.cpp` 实测 3808 行（62 个函数），是 DCGM 健康监控**全部业务规则**所在地：按子系统（内存/PCIe/散热/功耗/InfoROM/驱动/NVLink/NVSwitch）设置字段 watch，`MonitorWatches` 周期判定阈值并生成健康结果。响应组装在 `DcgmHealthResponse.cpp`（AddIncident 记录事件、PopulateHealthResponse 填充 v5 结构）。`DcgmModuleHealth.cpp` 的 ProcessMessage 分发 Set/Get/CheckV5/CheckGpus/字段更新通知。

**全仓最大测试文件**是它的配套：`tests/DcgmHealthWatchTests.cpp` 4909 行，13 个辅助类注入各子系统字段值，逐系统验证阈值判定、结果掩码与多版本响应兼容——这份测试事实上是健康子系统行为的可执行规格书，读懂它等于读懂判定矩阵。

### 5.4 diag 与 nvswitch：两个硬件面模块

diag 模块（`DcgmDiagManager.cpp` 2273 行）承接 `dcgmRunDiagnostic` 请求：构造 NVVS 命令行（`CreateNvvsCommand`:628）、以子进程执行 nvvs 二进制（默认路径 `/usr/libexec/datacenter-gpu-manager-4/nvvs`，:289；可被环境变量覆盖，:295-300；nvvs 进程 pid 跟踪 `m_nvvsPID`，:121/136）、解析结果并强制 GPU 配置。多版本响应适配在 `DcgmDiagResponseWrapper.cpp`（1128 行，v7-v12 八代）。`DcgmModuleDiag.cpp`（601 行）处理 ProcessRun_v5..v12 的版本演进消息。`DcgmDiagCallers` 按连接 id 记录心跳判定调用方存亡。

nvswitch 模块的精髓在 `FieldDefinitions.h`（2527 行）：`FieldIdControlType<fieldId>` 模板宏体系（宏体 44-46 行）让每个 NvSwitch 字段成为编译期单例，携带 NSCQ 路径与更新函数的静态映射（首个特化 `DCGM_FI_DEV_NVSWITCH_TEMP_CELSIUS` 在 64 行）。两个数据源管理器：`DcgmNscqManager`（DcgmNscqManager.h:36，基于 NSCQ 库）与 `DcgmNvsdmManager`（DcgmNvsdmManager.h:82，基于 NVSDM 数据模型；绑定层 `NvsdmLib.h:86` 生产实现+Mock 双轨）。

---
## 6. nvvs 诊断套件：Plugin 插件框架与 memtest 22 核

### 6.1 主控与插件 ABI

NVVS 是独立二进制（被 diag 模块拉起，见 5.4）。入口 `nvvs/src/NvvsMain.cpp:99`，主控逻辑 `NvidiaValidationSuite::Go`（NvidiaValidationSuite.cpp:443，文件 1787 行）：GPU 枚举、测试分发、nvvs 子进程构造。测试级别枚举在 `nvvs/include/NvvsCommon.h:44-52`：`NVVS_SUITE_CUSTOM/QUICK/MEDIUM/LONG/PRODUCTION_TESTING/XLONG`（逐级超集；图谱摘要写 SHORT/MEDIUM/LONG/XLONG，源码实际是 QUICK 非 SHORT）；全局停止标志 `main_should_stop`:41。

**插件框架三层**：
- `nvvs/include/PluginInterface.h`（403 行）：C ABI 边界——`dcgmDiagPluginInfo_t`/`dcgmDiagPluginEntityList_v1`/`dcgmDiagPluginTestParameter_t` 等结构与 `dcgm_api_export` 导出约定；
- `nvvs/include/Plugin.h`（522 行，44 方法）：插件基类，聚合 `DcgmRecorder`（515 行，为测试录制 DCGM 字段值与错误码）、`CustomStatHolder`（自定义统计累积）；
- `nvvs/src/PluginLib.cpp`（906 行）：装载器——`dlopen(path, RTLD_LAZY)`:180、`dlsym` 解析 `InitializePlugin` 等入口（`LoadFunction` 封装 :271；`m_initializeCB` 绑定 :142；`InitializePlugin` 调用 :376）。注意 `extern "C"` 块内函数 tree-sitter 静态分析识别不了（批阶段笔记亦证实），人工读代码时直接看导出块最稳。

`Test.h` 的 Test 基类对插件做隔离包装——**兜住插件抛出的异常**，保证单个插件崩溃不拖垮整个套件。配套设施：`TestParameters.h` 参数容器（字符串/双精度双类型）、`PluginStrings.h`（490 行，全部插件测试名/参数名常量，框架与插件的命名契约）、`ConfigFileParser_v2`（配置文件解析）、`IgnoreErrorCodesHelper.h`（解析 `"gpu0:28;gpu1:140,92"` 格式的按 GPU 忽略错误码）。

### 6.2 memtest：22 个 CUDA 核、免 CUDA 运行时

`nvvs/plugin_src/memtest/` 是显存测试重镇，血统特殊——**UIUC Illinois 开源许可**（misc.h:2-7，"University of Illinois/NCSA"，非 NVIDIA Apache2），改文件时注意保留原始版权头。

- `tests.cu`（644 行）：**22 个 `__global__` 测试核**（58 行起到 616 行，walking bits / block stride / moving inversions 等经典显存算法）；
- `tests.ptx`：预编译 PTX，运行时经 **CUDA Driver API** 加载——`Memtest.cpp`（2141 行）做 CUDA module 加载与 test0-test10 编排，完全不链接 cudart，**免 CUDA 运行时版本绑定**（与 dcgmproftester 的 buildptx.sh 同一手法）；
- `Memtest.h:122` 的 `class Memtest` 继承 DcgmThread（可协作停止）；`MemoryChunkManager.h` 管分块显存（RAII CudaMemoryDeleter）；
- `MemtestWrapper.cpp` 导出 C ABI：`extern "C"` 块 27 行起，`GetPluginInfo`:34、`InitializePlugin`:86、`RunTest`:103，130 行收块。

### 6.3 插件群像与配置

其余插件：`memory/`（新一代显存测试，L1 tag 压测 L1TagCuda/L1CudaUtils）、`pcie/`（BusGrind+SmPerfDevice，cublas 句柄走 cublas_proxy）、`diagnostic/`（GpuBurn，`compare.cu` 的 compareFP32/FP64/FP16 对比核反复读写矩阵统计 faulty/nan 元素）、`contextcreate/`、`targetedpower`/`targetedstress`（老式布局：插件类+worker 线程+实现同文件，TargetedPower_wrapper.cpp 的 CudaInit 占 359 行；多流 cperf_stream_t+事件机制控制每批 op 下发节奏）、`nccl_tests/`（**C++23 `std::expected`** 返回可执行路径 + boost::process 管子进程，NcclTestsPlugin.cpp）、`nvbandwidth/`（`NVBandwidthPlugin.h:34`，包装 LFS 二进制 nvbandwidth，见第 8 节）。

诊断参数的**权威源**是 `nvvs/diag-skus.yaml.in`（4711 行，dcgm-diag-v1 规范的全 SKU 默认参数表）——15 行起头注释大写 `DO NOT MODIFY`，19 行指明覆盖途径 `dcgmi diag -c <config_file>`。37 套 `configfile_examples/*.conf`（由 `fill_configs.py` 读 allowlist.txt 套模板批量生成）是活样例。

---
## 7. SDK 绑定：NVML / NSCQ / NVSDM 与注入测试体系

### 7.1 三大硬件 SDK 的 vendored 绑定（sdk/nvidia/）

- **NVML**：`sdk/nvidia/nvml/dcgm_nvml.h` 实测 12790 行——NVIDIA 管理库全部 API/结构/枚举的 vendored 副本（fanIn=30）；`nvml_entry_points.h` 2193 行是全部 `nvml*` 函数指针入口表（加载与符号解析的枢纽，配套 `nvml_loader_hook.h` 供注入测试替换库路径）；common/ 下还有 timelib/hashtable/MurmurHash3/keyedvector 等随包工具（开放寻址哈希缓存）。弃用 API 单独放 `nvml_deprecated.h` 保持兼容。
- **NSCQ**：`sdk/nvidia/nscq/nscq.h` 425 行（NVSwitch 配置查询 C 接口）；`path.h`（146 行）定位 `libnscq.so` 的搜索策略**含注入覆盖路径**；`dlwrap/` 是 dlopen 包装层。
- **NVSDM**：`sdk/nvidia/nvsdm/nvsdm.h` 1243 行（v1.2，NVSwitch 数据模型——交换机发现/遥测/配置读取），经 `dcgm_nvsdm.h` 引入 DCGM 命名空间，消费方即 5.4 节的 `DcgmNvsdmManager`。

三绑定的共同纪律：**SDK 头是 vendored 契约，不随 DCGM 代码风格重构**（`.clang-format-ignore` 排除 sdk/ 目录）。

### 7.2 nvml-injection：无 GPU 也能测全链路

`nvml-injection/` 是 YAML 驱动的 NVML 注入库：`include/nvml_injection.h` 以 `nvmlRet + values + valueCount` 模式暴露注入 C 接口（`NVML_INJECTION_MAX_VALUES` 等容量常量在 29-31 行）；`InjectionArgument.h` 8334 行是**生成代码**（InjectionArgument 模板对全部 NVML 结构类型 622 个实例化）；`AttributeHolder.h`（615 行）以设备/UUID 为键存时间戳化注入数据，`TimestampedData` 支持 AfterTimestamp 序列回放；`PassThruNvml` 单例管理真实 NVML 透传。消费端：dcgmlib 的 `DcgmInjectionNvmlManager` 桥接到字段注入，`dcgm_test_apis.h`（480 行）是仅测试构建可见的伪造数据接口。**跑 CI 单测不需要真 GPU**，秘密全在这里。

### 7.3 dependency_flags.sh：构建黄金清单

`dcgmbuild/dependency_flags.sh`（110 行）是全部第三方依赖的**SHA256 锁定清单**：`dependencies()` 函数（21 行起 heredoc 输出）逐行列 `名称 URL sha256`——Boost 1.85.0 / Catch2 v3.10.0 / CMake 4.3.2 / crosstool-ng 1.28.0（gcc 14.3.0、glibc 2.27、binutils 2.42、linux 4.20.17 头）/ clang / ccache / corrosion 等。三级容器镜像都从这里取参（dcgmbuild/build.sh 调它生成下载参数再 `docker buildx bake`）——**升级任何依赖 = 改这一个文件 + 重算校验和**，别去 Dockerfile 里找版本号（镜像里的 URL/哈希全部由此注入）。

---
## 8. 新人上手：三个禁区、构建链与调试入口

### 8.1 三条红线（动手前必读）

1. **diag-skus.yaml.in 禁改**：4711 行全 SKU 默认诊断参数表由流水线生成，头注释（15 行 `DO NOT MODIFY`）明确覆盖途径是 `dcgmi diag -c <config_file>`。同理 `nvml-injection/include/InjectionArgument.h`（8334 行）与 `nvml_injection_structs.h`（881 行）是 libclang 生成代码（`scripts/codegen/libclang/generate.py` 读 `files.yml` 清单批量产出），改源模板而非生成物。
2. **mndiag 二进制是 Git LFS 指针**：`modules/mndiag/cuda12|cuda13 × x86_64|aarch64` 的 `libcurand.so.10.x` / `mnubergemm` 与 `nvvs/plugin_src/nvbandwidth/Cuda12|Cuda13/bin/*/nvbandwidth` 在工作区只是 3 行指针文本（version/oid sha256/size——mnubergemm 真身 718,471,384 字节），追踪规则在 `.gitattributes`（17 行规则：mndiag 8 条+nvbandwidth 4 条+testing 5 条）。clone 后不 `git lfs pull` 就构建/打包必失败；`build.sh:209-213` 会自动 `git-lfs install --local && git lfs pull`，跳过开关是 `DCGM_SKIP_LFS_INSTALL=1`（build.sh:72 有文档）。
3. **SDK 目录与生成物不参与格式化/覆盖率**：`.clang-format-ignore` 排除 sdk/；gcovr.cfg 排除 sdk、sdk_samples、testing。`validate_format.sh` 提交钩子（`install_git_hooks.sh` 安装到 pre-commit）按 `GetChangedFiles`:32 取暂存区文件，`ValidateFiles`:74 分别套 clang-format（108 行）与 autopep8（117 行）校验，失败阻断提交。

### 8.2 构建链：三级镜像 + 交叉工具链

本机构建入口 `build.sh`（约 340 行）：检查 git-lfs → Python lint → CMake 配置构建测试打包。规范路径是容器化：`intodocker.sh` 按目标架构（`-x86_64`/`-aarch64` 后缀）把工作区挂进 `dcgmbuild` 镜像执行。三级镜像链：

1. **common-host-software**：宿主工具层（ccache/clang/cmake/git/git-lfs/lcov/ripgrep/sccache，全部 SHA256 校验下载；BuildKit 语法 `ADD --checksum`）；`0050_clang.sh` 以 update-alternatives 主/从链接组管理 LLVM 多版本。
2. **toolchain**：crosstool-ng 配置驱动构建 gcc 14.3 交叉工具链，`ARCHITECTURE=x86_64|aarch64` 双目标 + Rust（corrosion 集成）。
3. **dcgmbuild**：三阶段主构建镜像（downloads/toolchain 基/builder），ENV 设置 `$TARGET-gcc` 等交叉前缀，逐脚本编译十个第三方库进 sysroot。

运行时镜像另有一条线：`docker/Dockerfile.ubi9` 基于 CUDA 13.0.1-base-ubi9，dnf 装 cuda13/cuda12 两个变体 RPM（33-34 行），`EXPOSE 5555`:48、`ENTRYPOINT /usr/bin/nv-hostengine`:49。CMake 预设见 `CMakePresets.json`（Debug/RelWithDebInfo/Release/Package + DEB/RPM/TGZ 打包矩阵）。

### 8.3 发布件：systemd 降权与包内容黄金清单

打包侧两个值得知道的细节：deb/rpm 安装后脚本（scripts/deb/postst 的 postinst:20-27 与 scripts/rpm/postinstall:20-27）创建 `nvidia-dcgm` 系统服务用户（`useradd -Urs /usr/sbin/nologin`）与 `/var/log/nvidia-dcgm` 日志目录，配合 `config-files/systemd/nvidia-dcgm.service.in` 以 `--service-account nvidia-dcgm` 降权运行。`scripts/verify_package_contents/` 用模板化 golden manifest 做打包回归：`_common.sh` 的 `template_deb`:37/`template_rpm`:47 把具体包名归一化为版本无关模板名，`generate_package_contents.sh:26` 的 `generalize()` 把版本/架构替换为占位符后写清单（write_template_deb:47 / write_template_rpm:57），verify 方向逐一比对——**动 install() 规则忘了刷新清单，打包 CI 会红**。

### 8.4 建议路线图（按图谱 tour 16 步精简为 7 站）

1. README.md + 根 CMakeLists.txt（527-542 子目录表）建立地图；
2. hostengine/src/main.cpp 全文 580 行精读（守护化+pidfile）；
3. DcgmHostEngineHandler.cpp 的 2407-2417（模块表）+ 2669-2760（LoadModule/dlopen/dlsym）；
4. dcgmi/Command.h（72 行）+ CommandLineParser.cpp:100-116（17 子系统表）后挑一个子命令（建议 `dcgmi dmon`）从 Execute 追到 hostengine；
5. DcgmWatchTable.h + DcgmCacheManager.h 的类声明区（h:508-534 起）理解采集节拍；
6. 挑一个 policy 检查器（如 XID:722）对照 DcgmPolicyManagerTests.cpp 读懂"注入字段值→判定→SetViolation"闭环；
7. 跑一次 `dcgmi diag -r 1`，对照 diag-skus.yaml.in 与 nvvs 插件目录走完触发链（diag 模块 → nvvs 二进制 → 插件 .so → DcgmRecorder 回填）。

调试小抄：nv-hostengine 日志默认 `/var/log/nvidia-dcgm`（postinst 创建）；日志收集脚本 `scripts/gather-dcgm-logs.sh`；多节点诊断的 openmpi 路径探测见 `config-files/systemd/nvidia-dcgm-multinode-diagnostics-generator.sh`；测试注入入口在 `dcgmi test`（DcgmiTest.h 的 IntrospectCache/InjectCache/ModulesPauseResume）与 `dcgm_test_apis.h`。

---

## 附：本文锚点清单（源码核实）

行号类锚点 60+（均经 grep/sed/wc 逐条核实于 commit `64df9f89`）：CMakeLists.txt:15/17/527-542；HostEngineCommandLine.cpp:35/53/62/88/128/133/382；main.cpp:46/71/131/154/188/205/281/423/467；DcgmHostEngineHandler.h:125/605/639/790；DcgmHostEngineHandler.cpp:2407-2417/2669/2729/2741-2743；DcgmCacheManager.h:513/534；dcgm_fields.cpp:213/6306/6410；dcgm_fields.h:554/619/806；dcgm_structs.h:3444/3471/3509/3593/3598/4058-4072；dcgm_agent.h:1817；entry_point.h:19/1021-1027；Command.h:27/37/44/49/57/64；main_dcgmi.cpp:54/74；CommandLineParser.cpp:100-116；DcgmProfTesterKernels.cu:65/79；buildptx.sh:24-28；DcgmModule.h:31/47；DcgmModule.cpp:25/44；DcgmModuleApi.h:39；DcgmCoreProxy.h:37；DcgmPolicyManager.cpp:107/204/366/427/541/582/623/678/722；DcgmDiagManager.cpp:119/289/628；FieldDefinitions.h:44/64；DcgmNscqManager.h:36；DcgmNvsdmManager.h:82；NvsdmLib.h:86；NvvsMain.cpp:99；NvidiaValidationSuite.cpp:443；PluginLib.cpp:142/180/271/376；NvvsCommon.h:41/44-52；MemtestWrapper.cpp:27/34/86/103/130；Memtest.h:122；misc.h:2-7；diag-skus.yaml.in:15-19；NVBandwidthPlugin.h:34；nvml_injection.h:29-31；dependency_flags.sh:21+；.gitattributes（17 条规则）；build.sh:72/209-213；Dockerfile.ubi9:33-34/48/49；postinst:20-27；postinstall:20-27；_common.sh:24/37/47；generate_package_contents.sh:26/47/57；validate_format.sh:32/74/108/117；DcgmLogging.h:254/267/367；DcgmMutex.h:26/56；DcgmWatchTable.h:80/128/234；DcgmProtocol.h:32；DcgmSettings.h:31；DcgmIpc.h:136/202；NvmlTaskRunner.hpp:30/95；DcgmFvBuffer.h:78；SSHTunnelManager.hpp:571/650/909/923；FieldWorkers.hpp:64/104。

实测行数锚（wc -l）：DcgmCacheManager.cpp=16530；DcgmCacheManager.h=2752；dcgm_fields.cpp=6872（单函数 213-6306=6094 行）；dcgm_fields.h=3993；dcgm_structs.h=4374；entry_point.h=1035；CommandLineParser.cpp=3168；DcgmHealthWatch.cpp=3808；DcgmHealthWatchTests.cpp=4909；DcgmDiagManager.cpp=2273；DcgmDiagResponseWrapper.cpp=1128；FieldDefinitions.h=2527；DcgmConfigManager.cpp=1631；DcgmMnDiagManager.cpp=2031；MnDiagManagerTests.cpp=3981；memtest/Memtest.cpp=2141；tests.cu=644（22 个 __global__）；diag-skus.yaml.in=4711；Plugin.h=522；PluginInterface.h=403；PluginLib.cpp=906；NvidiaValidationSuite.cpp=1787；dcgm_nvml.h=12790；nvml_entry_points.h=2193；nscq.h=425；nvsdm.h=1243；InjectionArgument.h=8334；dependency_flags.sh=110；DcgmCoreProxy.h=544；DcgmCoreProxy.cpp=1433；DcgmHostEngineHandler.cpp=5482；main.cpp=580。

**与图谱摘要的差异（以源码为准）**：诊断 API 实为 `dcgmRunDiagnostic`（非 dcgmStartDiag_v8）；NVVS 套件级别为 CUSTOM/QUICK/MEDIUM/LONG/PRODUCTION_TESTING/XLONG（无 SHORT）；模块为 11 ID/10 懒加载 .so（非八模块）；DcgmCoreProxy.h 实测 544 行。
