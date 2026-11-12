# 06 · modules 模块框架：DcgmModule 契约、dlopen 装配与 mndiag 适配器

## 角色定位

modules/ 是 hostengine 的插件化机体，12 个子目录（common/config/core/diag/health/introspect/mndiag/nvswitch/policy/profiling/sysmon/vgpu）对应 11 个模块 ID + 共享层。ID 枚举 dcgmModuleId_t（dcgm_structs.h:4059-4074）：Core=0（:4061，always loaded）到 MnDiag=10（:4071）。三个支点：DcgmModule 基类契约（modules/DcgmModule.h）、dlopen 装配线（DcgmHostEngineHandler.cpp:2669）、m_coreCallbacks 回调表注入的"穷人版 DI"。mndiag 在此之上叠加 adapters/ 适配器层，是全仓接缝设计最重的模块。

## 内部结构

**契约层**：DcgmModule 基类（DcgmModule.h:31）极小——虚析构（:35，注释"ancient compiler"）、静态 CheckVersion 比对消息 blob 前 4 字节版本（:47）、纯虚 ProcessMessage（:59）、可选 OnLoggingSeverityChange（:66）。模板中间层 DcgmModuleWithCoreProxy<moduleId>（DcgmModule.h:75-76）用**模板参数携带模块 ID**：构造期 InitLogToHostengine 接管日志严重度（:83）、LoggingSetHostEngineCallback 挂宿主回调（:84）、dcgmModuleIdToName 设日志组件名（:86-89），持有 m_coreCallbacks+m_coreProxy 双成员（:117-118）。C 边界三个函数指针类型 dcgmModuleAlloc_f/dcgmModuleFree_f/dcgmModuleProcessMessage_f（:123-125）是 .so 必须导出的全部符号；SafeWrapper 模板（:134-153）把构造异常吞成 nullptr 日志——C++ 异常绝不穿模块边界。

**装配层**：模块状态机七态 dcgmModuleStatus_t（dcgm_structs.h:4080-4091）。LoadModule（DcgmHostEngineHandler.cpp:2669）流程：moduleId<=Core 直接拒绝——core 永不 dlopen（:2671-2675）；Denylisted/Failed/Unloaded 拒绝重试（:2691-2696）；Lock 双检（:2700-2706）；GPU detach 期间中止（:2719-2723）；dlopen RTLD_NOW（:2729）→ dlsym 三符号（:2741-2744）→ **allocCB(&m_coreCallbacks) 完成依赖注入**（:2764）→ 置 Loaded（:2781）。消息路由：denylist 视为未装载（:1327-1331），未装载先懒加载（:1337-1346），pause/resume 广播全部模块（:1349-1352），其余 SendModuleMessage（:1358）。

**mndiag 适配器**：modules/mndiag/adapters/ 下 9 对 Base/Adapter 接口 + mock 目录，按职责分三族——通信族 DcgmApiBase（MultinodeRequest/Connect_v3/Disconnect，DcgmApiBase.h:37/:47/:57）与 Tcp/UdsSSHTunnelManager 双传输；资源族 DcgmCoreProxyBase（子进程五操作 + GPU 信息查询，DcgmCoreProxyBase.h:38-55）、DcgmResourceHandle 与 MnDiagMpiRunner 两套 Base/Factory；状态机族 MnDiagStateMachine。模块类 DcgmModuleMnDiag 继承 DcgmModuleWithCoreProxy<DcgmModuleIdMnDiag>（DcgmModuleMnDiag.h:25）实现 ProcessMessage（:38），业务编排在 DcgmMnDiagManager（DcgmMnDiagManager.h:97）：RunHeadNode 四步——解析 host 列表→预留资源→拉起诊断→填充响应；远程节点六个 Handle*（Reserve/Release/DetectProcess/BroadcastRunParameters/GetNodeInfo/BroadcastEnvVariables，DcgmMnDiagManager.h:136-141）与授权三联（:144-146）。

## 外部连接

模块对 core 只见 DcgmCoreProxy（modules/common/DcgmCoreProxy.h:37，构造吃 dcgmCoreCallbacks_t DcgmCoreProxy.h:43），回推数据用 AppendSamples（DcgmCoreProxy.h:264）。core 对模块只见三个 C 符号。客户端经 dcgm_module_command_header_t 进模块；dcgmi modules 的 pause/resume 落在状态机 Paused/Reloadable 态。mndiag 的 SSH 隧道与 MPI runner 对接远端 nv-hostengine 与 mnubergemm 二进制（cuda12/13 × x86_64/aarch64 四矩阵 Git LFS 挂载）。

## 数据流

请求流：客户端 API → HostEngineHandler 按 moduleId 懒加载 → SendModuleMessage → ProcessMessage → CheckVersion 验版本 → 业务执行。数据流（nvswitch 为例）：模块内 DcgmWatchTable 节拍（DcgmNvSwitchManagerBase.cpp:327）→ NSCQ 采集 → AppendSamples 回写 cache → core 的 pushedByModule 字段绕开自身采集循环（DcgmCacheManager.cpp:6058-6063）。mndiag：RunHeadNode → Connect_v3 连远端 → 广播参数 → MPI runner 起测试 → GetNodeInfo 汇聚 → 响应回填。

## 设计决策

1) **模板传 moduleId 而非虚函数**：模块静态绑定自己的 ID 与日志组件名，零运行时查表。2) **core 不走 dlopen**：它就是宿主本体，LoadModule 显式拒绝（DcgmHostEngineHandler.cpp:2671），避免自举悖论。3) **C 符号边界 + 异常吞没**（DcgmModule.h:134-153）保 .so ABI 稳定。4) **Paused 继承**：新模块装载即同步 core 暂停态，宁可卸载不留半活模块（DcgmHostEngineHandler.cpp:2792）。5) **mndiag 的 9 对适配器**为可测性把 Manager 依赖全部接口化（mock/ 目录证明意图），通信/资源/状态机三层各自可替换，代价是文件数翻倍。6) denylist 启动期即生效（hostengine/src/main.cpp:493-498），懒加载让健康节点零开销。

## 新人提示

新模块清单：modules/ 下建目录 → 继承 DcgmModuleWithCoreProxy<你的ID> → 导出三个 C 符号（参考 DcgmModuleApi）→ dcgm_structs.h 枚举**尾部**加 ID → CMake 注册。装载失败看 DcgmHostEngineHandler.cpp:2736 的 dlerror 日志；DCGM_ST_MODULE_NOT_LOADED 三种成因（denylist/Failed/Unloaded）在 :2694 区分。改模块消息结构务必 bump 版本号，CheckVersion 会拒旧客户端。读 mndiag 先看 adapters/ 各 Base.h 纯虚接口再看 Manager，mock/ 是捷径。模块内不要直接调 dcgmlib 符号——一切经 CoreProxy，否则破坏接缝与可测性。
