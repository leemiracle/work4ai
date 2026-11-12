# 11 · SDK 三绑定：NVML 加载器、NSCQ dlwrap 与 NVSDM 加载器

## 角色定位

`sdk/` 回答一个问题：DCGM 怎么用三个无法静态链接的厂商运行时库？`libnvidia-ml.so.1`（GPU 管理）、`libnvidia-nscq.so.N`（NVSwitch 查询）、`libnvsdm.so.1`（NVSwitch 设备管理）都随驱动发布且无静态归档。三绑定把编译期符号依赖降级为运行时 dlsym，深度递进：NVML 是"加载器+可注入口"（421 行）；NSCQ 绑定 vendor 了上游 dlwrap 包装层（独立 MIT 源码库），只补一个拍平 include 路径的 `patches/dlwrap.patch`；NVSDM 绑定最年轻，加载器仅 198 行，重量在 1243 行的数据模型头 `nvsdm.h`。三者共享 X-macro 范式：`entry_points.h:37-39`、`dcgm_nscq.h:18-19`、`dcgm_nvsdm.h:18` 都是伞形 include，被不同宏反复包含生成代码。

## 内部结构

NVML 加载器全局状态四件套在 `nvml_loader.cpp:30-33`：句柄、递归共享锁、原子 open 计数、hook 世代计数。核心宏 `NVML_DYNAMIC_WRAP`（`nvml_loader.cpp:68`）生成 Default/Hooked 双槽、set/reset hook（声明侧 `nvml_loader_hook.h:26-29`）、pre/post 任务上下文钩子与懒 dlsym 双检锁（`nvml_loader.cpp:117`）。nvmlInit 家族特例：取写锁后以 `takeLock=false` 生成局部包装（`nvml_loader.cpp:228`）；加载按六条 fallback 路径（`nvml_loader.cpp:177-188`），`NVML_INJECTION_MODE` 可切注入库（`nvml_loader.cpp:201`）；dlclose 后缓存作废，靠 `resetAllNvmlHooks` 递增世代计数（`nvml_loader.cpp:396`）。

`common/NvmlRecursiveSharedMutex` 支持读、写各自递归，但禁止读→写升级并抛 `logic_error`（`NvmlRecursiveSharedMutex.cpp:25-29`，测试 `NvmlRecursiveSharedMutexTests.cpp:83` 用 `REQUIRE_THROWS` 钉死）；写线程可再取读锁（`NvmlRecursiveSharedMutex.cpp:87-92`）。`common/` 的 C 容器是注入库数据面：`timeseries_t` = 类型标签 + keyedvector（`timeseries.h:62-67`），`mcollect_t` 内嵌 hashtable（`measurementcollection.h:61-65`、`hashtable.h:40-51`）；`nvml_entry_points.h` 共 307 条 X-macro，第二字段 `tsapiXxx` 即这套 API 的命名（`nvml_entry_points.h:37`）。

NSCQ 侧 `dlwrap.c:78` 的 `NSCQ_DLWRAP_FUNC_IMPL` 为每个函数生成静态符号缓存，`sym_cycle` 对比 `dl_cycle` 决定重查——并发不加锁是故意的（`dlwrap.c:94-102` 注释：多线程写入同一值）。OS 层 `posix.c:37-51` 注释是"dlclose 后符号悬挂"的教科书陈述：读锁持有整段调用（`posix.c:107-118`），库名按 API 主版本拼成 `libnvidia-nscq.so.%u`（`posix.c:63-64`，宏在 `nscq.h:49`）。

NVSDM 加载器：`LibHandle` 用 unique_ptr 定制 deleter 管 dlclose（`nvsdm_loader.cpp:46`），句柄常驻 `s_handle("libnvsdm.so.1")`（`nvsdm_loader.cpp:90`）；`NVSDM_FUNCTION` 宏（`nvsdm_loader.cpp:146-161`）生成的包装调用期间不持锁——三者唯一。错误串编译内置（`nvsdm_loader.cpp:166-172`：没装库也要能报错），DCGM 入口 `dcgmLoadNvsdm`（`nvsdm_loader.cpp:184`）。

## 外部连接

下游：`modules/nvswitch/DcgmNscqManager.cpp:593` 用 `NSCQ_FN` 包回调做路径观察；`modules/nvswitch/NvsdmLib.cpp:323` 起逐函数转发 `::nvsdmXxx`（`NvsdmBase` 是测试桩）；NVML 绑定直供全仓 dcgmlib/dcgm_stub。三方 pre/post 汇聚到 `common/TaskContextManager.hpp`（登记"线程在等厂商库"给挂起检测）。许可证实测：dlwrap 为 **MIT**（`README.adoc:47-49` + `dlwrap.c:2-21` 头声明），与主仓 Apache-2.0 并存；`dcgm_nvml.h`/`nscq.h`/`path.h` 是 NVIDIA source license；`nvsdm_loader.cpp:3-9` 与 `nvsdm_entry_points.h:3-9` 带 NVIDIA 专有头——一个 sdk 树四种许可。

## 数据流

NVML 调用链：`nvmlXxx` → 共享读锁 → hook 检查 → 双检 dlsym → pre → 真函数 → post → 解锁；同线程持读锁再进时计数递增不死锁。NSCQ 调用链：`nscq_dl_get()` 取读锁返 cycle → 不匹配则重查符号 → 调用 → `nscq_dl_put()`。NSCQ 查询模型是路径树：`path.h` 把 NVSwitch 建模成带 `{port}/{lane}/{vc}/{osfp}` 通配符的文件系统，如 NVLink 口状态（`path.h:94`）、CCI 线缆类型（`path.h:127`）、驱动版本（`path.h:51`）。NVSDM 最直白：`m_func` 空才 `load()`，否则裸调。遥测用 `nvsdmTelemParam_v1_t` 批量结构（`nvsdm.h:428-440`）：telemType 分 PORT/PLATFORM（QM3 传感器）/CUSTOM/CONNECTX（`nvsdm.h:175`），设备分 CA/SWITCH/ROUTER/RNIC/GPU（`nvsdm.h:126-135`）；`nvsdmSwitchInfo_v1_t` 的 linearFDBCap/SLtoVL 字段是 InfiniBand SwitchInfo MAD 镜像；`utils.h:88` 起 UMAD/MAD/netlink 错误码暴露内核 MAD 通道底细。

## 设计决策

同是"dlclose 重载后符号悬挂"，三绑定三种答案：NVML 用世代计数作废缓存（支持卸载重开与 hook 全重置）；NSCQ 用"读锁持有整段调用 + cycle 比对"，最优雅但强制全走包装；NVSDM 无卸载路径，于是无锁。dlopen flags 分道：NVML/NSCQ 用 RTLD_NOW，NVSDM 用 RTLD_LAZY（`nvsdm_loader.cpp:57`）。NSCQ 版本钉死编译期（`nscq.h:53-55` 的 `NSCQ_API_VERSION_CODE` + devel hash g7aa2171），库名带主版本；NVSDM 用 `NVSDM_STRUCT_VERSION` 把版本号与 sizeof 打包进 uint64（`nvsdm.h:77`）做轻量 ABI 协商。

## 新人提示

加 NVML 入口点只改 `nvml_entry_points.h`，生成、hook、注入面全自动；注入侧 `entry_point_nvml_injection.h` 需同步。绝不要在读锁下升级写锁——那是异常不是阻塞。查 NVSwitch 字段先翻 `path.h` 路径表。注入库永不 dlclose 不是泄漏（`nvml_loader.cpp:312-316` 注释：注入实现依赖全局变量）。想懂 dlsym 生命周期：精读 `posix.c:37-51` 注释再看 `dlwrap.c` 的 cycle 逻辑。sdk 四证并存，搬代码前必读文件头。
