# NVTX Onboarding（NVIDIA Tools Extension Library）

> 依据：仓内图谱 `.understand-anything/knowledge-graph.json`（467 节点/505 边/12 层/14 步导览，fingerprints 730 文件 @ b20b676e）+ 全部锚点源码复核。
> 图谱总入口 `onboard-input.json`（136KB）。行号锚均为本仓源码实证，抓取于 2026-11。

---

## 一、NVTX 是什么：一个仓库、四代实现

NVTX（`README.md:1`，443 行）是 NVIDIA 的**应用标注库**：开发者用 Mark/Range/资源命名 API 把"这段代码在干什么"写进程序，Nsight Systems/Compute 等分析工具注入后把这些标注渲染到时间线上——无工具附着时所有调用近似空操作，因此可以常年留在生产代码里。`README.md:21` 的循环可视化示例与 `README.md:49` 的标注分类（Markers/Ranges/Resource naming）是理解其功能面的最短路径。

仓库是**单仓四代实现**的总集：

| 实现 | 语言 | 入口 | 形态 |
|---|---|---|---|
| C API 头族 | C | `c/include/nvtx3/nvToolsExt.h`（1688 行） | 声明+Doxygen 一体 |
| C++ nvtx3 | C++ | `c/include/nvtx3/nvtx3.hpp`（4992 行） | header-only RAII 封装 |
| Rust crate | Rust | `rust/src/lib.rs`（474 行） | cargo workspace（含 nvtx-sys 子 crate） |
| Python 包 | Cython+Python | `python/src/nvtx/nvtx.py`（485 行） | pip 包，`_lib` Cython 扩展 |

根 `CMakeLists.txt` 仅 10 行：设最低版本后 `add_subdirectory` 进 `c/`，构建逻辑全在 `c/CMakeLists.txt`——Rust/Python 各自独立构建（`rust/Cargo.toml:5` workspace `members = ["crates/nvtx-sys"]`；Python 走 pyproject）。第四个"消费者"是 NVTXW 后端生态（见第七节）。

## 二、C 核心 API 头族（nvToolsExt 族）

`c/include/nvtx3/nvToolsExt.h` 是 C API 锚点（图谱 fanIn=72，全仓被引最多）：核心事件 API `nvtxMarkA:784`、`nvtxRangeStartEx:863`/`nvtxRangeEnd:942`（跨线程区间）、`nvtxRangePushEx:1023`/`nvtxRangePop:1114`（线程栈区间）；事件属性结构 `nvtxEventAttributes_v2:597-688`（消息/类别/颜色/负载的联合槽位描述）；域 API `nvtxDomainCreateA:1617`/`nvtxDomainDestroy:1642`/`nvtxDomainRegisterStringA:1551`/`nvtxDomainNameCategoryA:1404`；资源属性 `nvtxResourceAttributes_v0:1235-1292`；以及工具注入初始化入口 `nvtxInitialize:495`。A/W 后缀是 ASCII/宽字符双编码入口（Windows 友好）。文件末尾在版本保护下引入实现头：`NVTX_IMPL_GUARD` 定义后 include `nvtxDetail/nvtxTypes.h` 与 `nvtxDetail/nvtxImpl.h`（约 `nvToolsExt.h:1681-1686`）——声明与实现隔离的关键机关。

领域扩展头（均 `#include "nvToolsExt.h"` 后可用）：
- **Payload**：`nvToolsExtPayload.h`（1794 行）定义结构化负载体系——`nvtxPayloadData_t:859-990`、schema 描述 `nvtxPayloadSchemaEntry_t:991-1078`、注册 API `nvtxPayloadSchemaRegister:1343`/`nvtxPayloadEnumRegister:1356`、语义槽注册 `nvtxScopeRegister:1370`、Payload 版区间 `nvtxRangePushPayload:1399`、时间源 `nvtxTimestampGet:1482`。工具侧按 schema 解码任意 C 结构体的原始字节（sample-injection 有完整参考实现）。
- **Mem**：`nvToolsExtMem.h`（757 行）堆/区域/权限描述与批量注册（`nvtxMemHeapDesc_v1`、`nvtxMemRegionsRegisterBatch_v1`）；CUDA 适配在 `nvToolsExtMemCudaRt.h`（226 行）。
- **Counters**：`nvToolsExtCounters.h`（311 行）`nvtxCounterRegister/SampleInt64/SampleFloat64/SampleNoValue/BatchSubmit`，依托 Payload 语义槽传递计数语义。
- **Sync**：`nvToolsExtSync.h`（412 行）`nvtxDomainSyncUserCreate:308`/`Destroy:326`/`AcquireSuccess:379`，让自旋锁等非标准同步原语在时间线上可见。
- **资源命名**：`nvToolsExtCuda.h`（`nvtxNameCuDeviceA:84`、`nvtxNameCuStreamA:121`）、`nvToolsExtCudaRt.h`（139 行）、`nvToolsExtOpenCL.h`（213 行，覆盖 OpenCL 全部主要对象）。

语义系列头是纯类型定义：`nvToolsExtSemanticsTime.h`（49 行，timeDomainId+时间值）、`nvToolsExtSemanticsScope.h`（55 行，进程/设备/上下文/流层级）、`nvToolsExtSemanticsCorrelation.h`（68 行，外部系统请求 id 关联）、`nvToolsExtSemanticsCounters.h`（140 行，含限值 `nvtxCounterLimit_t`）。

## 三、C++ nvtx3 头文件库

`c/include/nvtx3/nvtx3.hpp`（4992 行）是对 C API 的 header-only RAII 封装，`namespace nvtx3:801` 起：`domain:1049`（域句柄，构造即 `nvtxDomainCreateA`）、`color:1339`（ARGB+CSS 名）、`category:1446`/`named_category_in:1529`、`registered_string_in:1755`（跨调用复用字符串句柄）、`message:1978`、`payload:2112`（强类型负载）、`schema:2225`/`payload_data:2295`（C++ 版结构化负载）、`event_attributes:2439`（链式 builder）、`scoped_range_in:2640`（析构自动 pop 的核心人体工学）以及 `semantic_base:911` 继承基座。README 示例 `README.md:26` 用的就是 `nvtx3.hpp`。这是 DeepWiki C API 文档之外第二个 Doxygen 站（`docs/doxygen-cpp/`，63 页）的主题。

## 四、nvtxDetail：扩展槽位机制（本仓最精巧的内核）

`c/include/nvtx3/nvtxDetail/`（磁盘 21 个头，图谱只收 4 个——见 README 勘误）是注入机制的实现层。骨架 `nvtxExtImpl.h`（123 行）定义**五态扩展槽位状态机**：`NVTX_EXTENSION_FRESH:94`→`DISABLED:95`/`STARTING:96`→`LOADED:97`/`INIT_FN_FAILED:98`；全局结构 `nvtxExtGlobals1_t:101-104` 用 `NVTX_LINKONCE_DEFINE_GLOBAL:106` 保证跨翻译单元唯一。

三个领域实现头 `nvtxExtImplCounters_v1.h`（166 行）/`nvtxExtImplMem_v1.h`（168 行）/`nvtxExtImplPayload_v1.h`（265 行）用 `NVTX_EXT_IMPL` 宏族以函数名参数展开生成实现体：**首次调用经初始化桩尝试加载工具，成功后跳转工具实现，未加载则降级为空操作**。这解释了两个现象：(a) 图谱对这三个头提取出 **0 个函数实体**——函数体由宏展开生成，无静态可寻址符号；(b) 真正的加载协议在未入图的 `nvtxInit.h`（499 行）/`nvtxInitDefs.h`（595 行）/`nvtxImplCore.h`（432 行）里。`tests/src/UseExportedApi.cpp:50` 的 X-macro（`nm -D` 导出清单配方注释在 `:55`）守护导出面不漏测。

## 五、Rust crate：workspace + nvtx-sys + domain 层

`rust/` 是 cargo workspace：安全封装 crate `nvtx`（`rust/src/lib.rs`，474 行）+ 原始 FFI crate `nvtx-sys`（`crates/nvtx-sys/src/lib.rs`，699 行，`rust/Cargo.toml:22` 以 path 依赖引入）。**注意 `sys` 不是内部 mod**——`rust/src/lib.rs:197` 是 `pub use nvtx_sys as sys`（外部 crate 别名）。

`lib.rs` 定义三级 feature 档（std/alloc/core-only，`rust/Cargo.toml:88-90` 的 std→alloc→nvtx-sys/std 特性链）与 `TypeValueEncodable` trait（值到载荷槽位的编码协议）。核心是 `rust/src/domain.rs`（1070 行）：域绑定 EventAttributesBuilder、注册字符串/类别缓存——**std 档 `HashMap`+`std::sync::Mutex`（`rust/src/domain.rs:25-27`），no_std+alloc 档 `BTreeMap`+`spin::Mutex`（`rust/src/domain.rs:14,23`），缓存字段在 `rust/src/domain.rs:268-269`**——同一文件条件编译双轨（图谱 NOTES 钉版条目）。

值类型族：`str.rs`（ASCII CString/UTF-16 WideCString 双编码统一载体）、`color.rs`（u32 位段 ARGB+CSS 颜色名 re-export）、`payload.rs`（泛型负载）、`category.rs`（原子计数器分配 id）、`ranges.rs`（`Range` 进程级 RAII/`LocalRange` 线程级 push/pop）、`error.rs`。CUDA 桥：`cuda.rs`（Device/Context/Stream/Event 四种 Driver 句柄）/`cuda_runtime.rs`（三种 Runtime 句柄）→ `nvtxNameCu*`/`nvtxNameCuda*`。线程标识：`domain/identifier/pthread.rs:10` 用 `#[cfg(not(target_os = "macos"))]` 排除 barrier/spinlock（`:21-24`）。生态集成：`rust/src/tracing.rs:54` `NvtxLayer` 实现 `tracing_subscriber` 的 `Layer`（`impl Layer:99`，`on_enter:143`/`on_exit:165` 对应 push/pop，字段经 `NvtxVisitor:188` 记为 payload）。

## 六、Python 绑定：Cython 主体 + 双态域 + 事后写出

`python/src/nvtx/nvtx.py`（485 行）是用户 API：`annotate` 上下文管理器/装饰器、`get_domain:141`（`@lru_cache:136` 缓存域对象）、`mark:256`/`push_range:309`/`pop_range:366`/`start_range:381`/`end_range:441`（自动从 Python 值推导 NVTX 载荷类型）、`numpy_dtype:55`（把 numpy dtype 注册为结构化负载 schema）、`enabled:454`。支撑模块 `_dtype_validation.py`（存储要求校验）与 `_metadata.py`（dtype 元数据映射+可哈希缓存键）。

**实现主体在 Cython**：`_lib/` 下 5 个 .pyx 共 4417 行（`lib.pyx` 1212、`counters.pyx` 804、`writer.pyx` 2185、`time.pyx` 127、`profiler.pyx` 89）。`_lib/__init__.py` 导出 `Domain` 与 `DummyDomain`/`dummy_domain`——工具未附着时降级 dummy（空操作），这是"双态域"设计。顶层还有三个图谱漏收的模块：`writer.py`（64 行，docstring `:19-29`）把**预先采集**的事件按显式时间戳经 NVTXW 后端写出（Nsight Systems 的 nsys_writer 集成即此路径）；`__main__.py`（54 行）提供 `python -m nvtx script.py` 的 cProfile 式 Profile 运行器；`colors.py`。

## 七、测试与注入体系：可替换后端是理解 NVTX 的钥匙

NVTX 的一切行为取决于**谁注入了函数表**。`tests/`（31 个源文件）就是围绕这一点构建的：

- **驱动与覆盖**：`RunTest.cpp` 装载各测试目标库并汇总；`TestCoverage.h`（558 行）12 个 `TestFuncRange*` 变体验证静态/动态/if/内联组合下的区间语义；`LinkerDupesFileA/B.cpp` 验证多翻译单元下全局对象只初始化一次。
- **注入三模式**：`PrintInjection.h` 按编译宏分 `SUPPORT_DYNAMIC_INJECTION:33`（环境变量注入）/`SUPPORT_PREINJECTION:44`（LD_PRELOAD）/`SUPPORT_STATIC_INJECTION:60`（静态函数指针）三模式导出；`SelfInjection.h`（717 行）用 `CallData` 继承多态+`Callbacks` 聚合 31 个函数指针记录回调流；`DllHelper.h` 把 dlopen/LoadLibrary 差异统一为宏。
- **NVTXW 线**：`MockNvtxwBackend.h`（602 行）实现完整 `nvtxwInterface_v2` 函数表并把后端收到的一切录进单例 Recorder；`CoverageNvtxwE2E.c`（314 行）走完整会话生命周期做端到端断言。
- **schema 宏守护**：`PayloadEntriesHelper.h:31-32` 用 `NVTX_DEFINE_STRUCT_WITH_SCHEMA`+`NVTX_PAYLOAD_ENTRIES` 生成 3..7 字段变体逐字段核对宏展开。
- **sample-injection 工具**（`tools/sample-injection/`，15 文件）是官方"如何自建 NVTX 消费后端"范本：`NvtxSampleInjection.cpp`（594 行）`InitializeInjectionNvtx2:523` 握手→`GetFunctionTable:105` 按模块取函数表→注册 Payload 扩展 `InitializePayloadExtension:458`→`TearDownDetector:91-93` 退出清理；`NvtxPayloadParser.cpp`（976 行，`BuildFieldDecodeInfo` 预计算+`Emit*Field` 族按类型从原始字节解码）+ `NvtxPayloadSchema.cpp`（528 行，`FinalizeSchema` 递归算嵌套布局）构成 schema 驱动解码完整管线，输出 JSON/文本两种格式。

Python 侧对应：`conftest.py`（992 行）`build_injection:83` 现场编译 mock 注入库，`NvtxEventsReader:361` 用 ctypes 结构体镜像读事件流，常量手工镜像（`COUNTER_FLAG_LIMIT_MIN:47`/`MAX:48`）构成生产/测试双源对照；四面测试 basic/counters/payloads/profiler 对应 API 四大语义面。

## 八、构建、CI 矩阵、文档与上手路径

**CI**（图谱 L02，19 文件）：`.gitlab-ci.yml`（619 行）= 3 模板（`.core-template:2`/`.python-template:18`/`.rust-template:38`）+ **56 个具名 job** 的编译器×平台矩阵——Core 线 Linux NVHPC 25.7-26.3/GCC 9-14/Clang 14-20/AOCC、MinGW、Windows VS 2015-2026 三架构、MSYS2/Cygwin；Python 线 3.9-3.14 含 free-threaded（3.13t/3.14t 验证 Cython 扩展无 GIL 可用）；Rust 线 Linux+Windows。GitHub Actions 14 个 workflow 补平台面：`core.yml`（479 行，Ubuntu 26/24/22+Windows 双工具链+Win11 ARM64+macOS）、`rust.yml`（run/msrv 1.77/deny/rustfmt/check 全 feature 组合含 no_std）、`python.yml`、`cibw.yml`、`validate.yml`（源文件版权头/行尾/编码校验）。

**文档三站**：`docs/doxygen/`（C API，106 页 HTML）+ `docs/doxygen-cpp/`（C++ nvtx3，63 页）+ `docs/python/`（14 页，图谱未收录），入口 `docs/index.html`。主题页如 `_p_a_g_e__m_e_m_o_r_y.html`（内存扩展）、NVTXW 用户指南、Payload 专题。

**上手路径**（对应图谱 14 步导览）：T01 仓库门面 → T03 `nvToolsExt.h` C API 锚点 → T04 nvtxDetail 扩展槽位 → T05 Counters/Mem 域扩展 → T06/T07 Rust 值类型与 CUDA 桥 → T08/T09 Python 主线与测试 → T10 RunTest/覆盖 → T11 注入与 NVTXW → T12 sample-injection 管线 → T13/T14 双 Doxygen 站。修改 C 头时务必同步检查 `tests/scripts/validate-source-files.sh` 的版权头/行尾约束（CI Source Validation job 强制）。
