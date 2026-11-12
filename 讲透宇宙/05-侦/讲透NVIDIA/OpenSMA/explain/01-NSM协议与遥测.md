# 01 · NSM 协议与遥测：nsm.cpp 的命令分发与缓存命中模型

## 角色定位

NSM（Node Scale Management）是 NVIDIA 在 MCTP 之上的私有管理消息层，位于 `src/nv/mctp/`——注意**不在** `src/nv/nsm/`（该目录不存在）。`src/nv/mctp/nsm.cpp`（3846 行，全仓最大单文件；类声明 `src/nv/mctp/nsm.h:1391`）承担 `mctp::Nsm` 类本体，向 MCTP driver 注册为消息处理器；Type2/3/4/5/FF 各一文件实现具体命令族。它与遥测缓存（`src/nv/telemetry/`）构成"命令分发 + 数据供给"二元结构。

## 内部结构

命令分发主干是 `Nsm::process`（`src/nv/mctp/nsm.cpp:1474`）：先验 NVIDIA PCI vendor id，再 switch `nrx.nv_msg_type`（`src/nv/mctp/nsm.cpp:1496`）。各 Type 规模差异大：Type2 链路管理 131 行（`src/nv/mctp/nsm_type_2.cpp:32` validatePcieLinkResetValue）；Type3 遥测查询 1572 行；Type4 事件/日志 1048 行（`src/nv/mctp/nsm_type_4.cpp:42` 起引 telemetry Cache 常量、`:45` 引 perf_mon CPU 利用率）加 debug token 通道（`src/nv/mctp/nsm_type4_debug_token.cpp`）；Type5 PCIe 电容/固件信息 1843 行——Type 族最大（`src/nv/mctp/nsm_type_5.cpp:47` ProtocolTypeMask）；TypeFF 扩展 438 行（`src/nv/mctp/nsm_type_ff.cpp:37` load_nv_internal_request、`:81` dispatch_nv_internal_get）。

nsm.cpp 内部按功能分区：DCD 命令族 `src/nv/mctp/nsm.cpp:939`（on_dcd_ping）、`:967`（on_dcd_get_sup_cmd_codes）、`:1224`（on_dcd_query_device_id）、`:1238`（on_dcd_get_device_capabilities_v2），汇聚到 `src/nv/mctp/nsm.cpp:1284`（process_device_capability_discovery）；固件管理 `src/nv/mctp/nsm.cpp:1397`（process_firmware）配 `:354`（get_active_slot）/`:366`（get_inactive_slot）/`:217`（get_redundancy_policy）/`:59`（is_any_background_copy_in_progress）/`:81`（can_revoke_otp）；事件订阅 `src/nv/mctp/nsm.cpp:1111`（on_dcd_set_event_subscription），事件上报在 `src/nv/mctp/nsm_event.cpp:34`（PrepareEventMessage）与 `src/nv/mctp/nsm_event.cpp:112`（ProcessType0Event）。公共位掩码在 `src/nv/mctp/nsm_common.h:26`（WriteProtectionGpioConfig）与 `src/nv/mctp/nsm_msg_bitmask.h:26-27`。

## 外部连接

上游对接 MCTP driver 消息回调（`src/nv/mctp/driver.cpp:269` on_receive 链路）；下游读遥测缓存（`src/nv/telemetry/cache.h:27`）、flash 服务与 bootloader 状态（`src/nv/mctp/nsm.cpp:400` 起引用 bootloader::Driver::State::InProgress/Complete）；旁挂功率平滑钩子（`src/nv/mctp/nsm_pwr_smoothing_handlers.h`）。版本串生成 `src/nv/mctp/nsm.cpp:340`（generate_fw_version）依赖构建注入的版本宏。

## 数据流

一次 Type3 遥测查询：主机 MCTP GET → driver 重组 → process() 验 vendor → 路由到 Type3 → `src/nv/mctp/nsm_type_3.cpp:54` 的 cachePowerSensorsMap 按 TelemId 查缓存（Gpu1Power/Gpu2Power/ModulePower）→ 命中即组装响应。**关键：查询路径不碰 I2C 总线**——缓存由传感器侧后台刷新（`src/nv/telemetry/cache.cpp:99` refresh），`Cache` 是以 TelemId 为索引的定长表（`src/nv/telemetry/cache.h:36` CacheSize=TelemId::MaxItem），单例 `src/nv/telemetry/cache.cpp:29`（inst）、读写 `src/nv/telemetry/cache.cpp:46`（set_cache）/`:63`（get_cache）。SMBus 侧组装在 `src/nv/telemetry/smb_telemetry.cpp:35`（weak get_end_address 起，124 行）。

## 设计决策

三个值得咀嚼的决策：①**缓存解耦**——查询延迟与总线轮询速率脱钩，代价是读数有陈旧度上限；告警项与阈值判断统一放缓存侧（`src/nv/telemetry/cache.cpp:83` set_error/`:91` clear_error）而非查询侧。②**弱符号特性开关**——`src/nv/mctp/nsm_pwr_smoothing_handlers_weak.cpp:43` 用 `__attribute__((weak))` 提供默认"不支持"应答（文件头 `src/nv/mctp/nsm_pwr_smoothing_handlers_weak.cpp:23` 注释明说链接期被覆盖），真实现（452 行，`src/nv/soc_pwr_smoothing/nsm_pwr_smoothing_handlers.cpp`）在别的产品线链接期覆盖，零代码改动。③**按 Type 分文件**——命令字对齐规范条目，审阅时可对照逐条打勾，代价是 nsm.cpp 仍要扛跨 Type 公共逻辑（槽位/版本/事件）。

## 新人提示

改 NSM 命令先看三处：分发 switch（`src/nv/mctp/nsm.cpp:1496`）、对应 type 文件、`src/nv/mctp/nsm_common.h:26` 位掩码。调试遥测先分清"缓存没数据"还是"查询没命中"——前者查传感器驱动与 `src/nv/telemetry/cache.cpp:99`，后者查 TelemId 映射（`src/nv/mctp/nsm_type_3.cpp:54`）。weak/strong 符号对分居 `src/nv/mctp/` 与 `src/nv/soc_pwr_smoothing/` 两目录，漏看一半会误判"未实现"。版本号问题从 `src/nv/mctp/nsm.cpp:340`（generate_fw_version）与 `:312`（append_number）入手。
