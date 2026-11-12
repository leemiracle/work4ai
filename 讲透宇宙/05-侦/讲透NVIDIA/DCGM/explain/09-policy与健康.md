# 09 · Policy 条件监察与健康看门狗：DCGM 的"超标即报警"双子模块

## 角色定位

policy 与 health 是 DCGM host engine 里语义相邻的兄弟模块：policy 回答"字段值是否越过用户阈值，越界要不要立刻回调通知客户端"；health 回答"GPU 各子系统（内存/PCIe/驱动/InfoROM/温度/功耗/NVLink/NVSwitch）当前处于 PASS/WARN/FAIL 哪一档"。两者都是标准 `DcgmModule`（模块 id 见 `dcgmlib/dcgm_structs.h:4064`：Introspect=3、Health=4、Policy=5），统一经 `PassMessageToModule`（`modules/DcgmModule.cpp:44`）派发并兜住异常。introspect 是家族里的自省员，量 host engine 自身的内存与 CPU 占用。`modules/health/DcgmHealthWatch.cpp` 实测 3808 行，是 modules/ 下最大单文件。

## 内部结构

policy 心脏是 `DcgmPolicyManager`（实测 1272 行）。每 GPU 一槽 `m_gpus[]` 存当前策略与 watcher 列表，初始化清零全部槽位以兼容后插入 GPU（48 行）。入口 `OnFieldValuesUpdate`（`modules/policy/DcgmPolicyManager.cpp:107`）遍历缓存管理器广播来的字段值，在 147 行按 fieldId switch 分派——恰好七类检查器：CheckEccErrors(319)、CheckPcieErrors(381)、CheckRetiredPages(442)、CheckThermalValues(548)、CheckPowerValues(589)、CheckNVLinkErrors(630)、CheckXIDErrors(693)，全部实现在 `modules/policy/DcgmPolicyManager.cpp:319` 起的连续区间。七类与 `dcgmPolicyCondition_t` 位掩码 0x1 DBE/0x2 PCI/0x4 页退休/0x8 温度/0x10 功耗/0x20 NVLink/0x40 XID（`dcgmlib/dcgm_structs.h:1900`）一一对应，`DCGM_POLICY_COND_IDX_MAX` 锁定序数/位掩码双轨一致（1892 行）。计数类检查靠 `GetCounterDelta`（`modules/policy/DcgmPolicyManager.cpp:272`）取最近两样本算增量，天然容忍计数器不清零。模块壳 `ProcessMessage`（`modules/policy/DcgmModulePolicy.cpp:185`）区分 core 事件与 GET/SET/REGISTER/UNREGISTER 四子命令，逐条先做版本握手。

health 心脏是 `DcgmHealthWatch`：`MonitorWatches`（`modules/health/DcgmHealthWatch.cpp:643`）按 groupId 取实体，先跑全局检查(792)，再逐实体查毁灭级 XID(703) 并按 systems 掩码分派 MonitorPcie/Mem 等。注册侧 `Set*` 家族按子系统挂字段监听：SetNvSwitchWatches(204)、SetPcie(897)、SetMem(919)、SetDriver(1082)、SetInforom(1123)、SetThermal(1190)、SetPower(1233)，底层 `ADD_WATCH` 宏（`modules/health/DcgmHealthWatch.cpp:123`）每 10 秒轮询、保留 1 小时。XID 判定核心是 `struct XidObservation`（`modules/health/DcgmHealthWatch.cpp:83`），以 Hit/ArchQueryFailed/ArchMismatch 三态支撑按 GPU 架构过滤。introspect 极简：`DcgmMetadataManager` 直接读 `/proc/self/status`（`modules/introspect/DcgmMetadataMgr.cpp:102`）算 RSS，CPU 利用率用两次采样差分（45 行）。

## 外部连接

上行：policy 由 core 的字段值更新事件驱动；health 与 introspect 是拉模式，客户端显式调用才检查。下行三条链：①SDK 的 dcgmPolicyRegister/Set/Get 在 `dcgmlib/src/DcgmApi.cpp:2292` 一带（Get 2205/Set 2258/Register 2292/Unregister 2318），统一经 `dcgmModuleSendBlockingFixedRequest`（`modules/DcgmModuleApi.cpp:33`）送入 host engine；②回调通道：`DcgmPolicyRequest::ProcessMessage`（`common/DcgmPolicyRequest.cpp:39`）识别 DCGM_MSG_POLICY_NOTIFY(67) 后解锁调用户回调(100)，异常全捕获不外泄；③CLI：`dcgmi policy` 的 SetCurrentViolationPolicy（`dcgmi/Policy.cpp:357`）、RegisterForPolicyUpdates(399) 与静态回调 ListenForViolations(446)。

## 数据流

policy 主链：SET_POLICY 设阈值 → `WatchFields`（`modules/policy/DcgmPolicyManager.cpp:746`）对硬编码 11 字段表(749)挂 watch → 周期广播 → 七类 Check 比对 → 命中即 `SetViolation`（`modules/policy/DcgmPolicyManager.cpp:204`）遍历该 GPU 的 watcher，条件掩码匹配且距上次通知超过 5 秒节流窗(215)才推送通知。health 主链：SET HEALTH WATCHES 挂字段 → 触发式与轮询式双路取证 → `ProcessXidFv`（`modules/health/DcgmHealthWatch.cpp:3264`）实时拦 XID：先查 m_devastatingXids（命中记入 m_gpuXidHistory，3274），再按 m_subsystemXids 归子系统。`BuildXidMappings`（`modules/health/DcgmHealthWatch.cpp:3355`）硬编码两张表：毁灭级 8 个（48/74/79/94/95/119/120/140），子系统级如 31 MMU、64 行重映射归 MEM，38/39/42 归 PCIE。

## 设计决策

①条件双轨制：序数枚举做数组下标、位掩码做开关，加第八类条件必须同时改两处。②节流窗 5 秒放在 watcher 级而非 GPU 级，多客户端互不饥饿；源码注释明言注入测试用 fv 时间戳可绕过。③分工哲学：policy 单条件命中即推事件（面向调度器摘卡），health 聚合分级结论（面向诊断报表）；毁灭级 XID 无视用户掩码强制监控是安全默认。④introspect 循环间隔 100 秒（`modules/introspect/DcgmModuleIntrospect.cpp:30`），数据完全按需拉取，不为自省付常驻 CPU。

## 新人提示

改七类检查逻辑先读 `OnFieldValuesUpdate` 的 switch：新增字段若不进 `WatchFields` 的 11 字段表(749)就永远没有样本到达检查器，这是"改了不生效"的最常见根因。policy 只处理 DCGM_FE_GPU（`modules/policy/DcgmPolicyManager.cpp:122`），非 GPU 实体直接跳过；health 的 Set* 家族则接受 VGpu/Switch 等多种 entity group。读 health 建议从 MonitorWatchesForGpu(538) 入手，它是最薄演示路径。一处口径勘误：本仓最大函数是字段表填充 `DcgmFieldsPopulateFieldTableWithFormatting`（`dcgmlib/src/dcgm_fields.cpp:213`，图谱 lineRange 213-6306 共 6094 行）——纯声明式表数据，勿当逻辑巨兽恐慌。
