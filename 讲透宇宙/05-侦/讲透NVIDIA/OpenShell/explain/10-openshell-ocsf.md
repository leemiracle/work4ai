# 10 · openshell-ocsf：OCSF v1.8.0 审计事件与 Windows ETW FFI

## 一、角色定位

`openshell-ocsf` 把沙箱行为日志钉在**行业标准格式**上：OCSF（Open Cybersecurity Schema Framework）v1.8.0（crates/openshell-ocsf/src/lib.rs:25 `OCSF_VERSION`）。crate 文档（crates/openshell-ocsf/src/lib.rs:9-22）列六件套：8 个 OCSF 事件类、类型化枚举与对象、带共享 `EventContext` 的 builder、双格式化器（人类可读 shorthand 单行 + OCSF 合规 JSONL）、tracing 集成层、`ocsf_emit!` 宏。它自己不决定"何时发什么事件"——那是 sandbox/supervisor/server 各运行时的职责；它提供词汇表与出口。仓库顶层 `telemetry/` 目录（2026-07-08/07-26/08-10 三份双周报）是**匿名社区使用统计报告**，与 OCSF 审计日志是两条完全不同的线，别混为一谈。

## 二、内部结构

src 六个子目录：`events/`（9 个事件类型）、`enums/`（12 个枚举文件——status/severity/auth/launch/disposition/http_method/device_type/activity/security/action）、`objects/`（Actor/Process/Device/Container 等 20+ 对象）、`builders/`（api_activity/finding/http/lifecycle/network/process/ssh/config/base 九个 builder）、`format/`（jsonl/shorthand/downgrade）、`tracing_layers/`（jsonl_layer/shorthand_layer/event_bridge）。

三个关键构件：**`EventContext` 进程级单例**（ctx.rs:14 `OCSF_CTX: OnceLock<EventContext>`）——沙箱启动时 `set_ctx` 一次，之后所有 builder 经 `ctx()` 取共享元数据（sandbox_id/hostname/镜像/origin），未初始化时回退测试默认值（ctx.rs:13-23，hostname="test"、origin=Supervisor）。**builder 链式风格**（builders/base.rs:13-50）：`BaseEventBuilder::new(ctx).activity_name(...).unmapped(key, value).build()`，unmapped 字段是显式逃生舱——OCSF 没有的字段塞进 `unmapped` 而不是造私有 schema。**8 事件类与 OCSF UID 对照**（schemas/ocsf/README.md）：network_activity[4001]/http_activity[4002]/ssh_activity[4007]/process_activity[1007]/detection_finding[2004]/application_lifecycle[6002]/device_config_state_change[5019]/base_event[0]。

**vendored 双版本 schema**：`schemas/ocsf/v1.7.0/` 与 `v1.8.0/` 两目录（各含 classes/objects/，1.8.0 多 profiles/ai_operation），README 注明来源是 schema.ocsf.io 的 API 快照、用途是**离线测试校验**。`validation/schema.rs` 的 `load_class_schema`/`load_object_schema`（:10-32）直接按 `CARGO_MANIFEST_DIR` 拼路径读 JSON——所以 validation 模块只在 `test-support` feature 下编译（crates/openshell-ocsf/src/lib.rs:35-36），schema 文件不进运行时二进制。**降级过滤器**（format/downgrade.rs）：`downgrade_event`（:25）把 1.8.0 事件打回旧版本——降到 v1.3.0 及以下要剥 `ai_model/container/observation_point_id` 三个字段（:11）并从 metadata.profiles 里删 `ai_operation/container`（:14），最后重写 metadata.version。只支持"剥字段"这一个方向的降级。

## 三、外部连接

消费方三家：`openshell-sandbox`（AGENTS.md 专门有一节"Sandbox Logging (OCSF)"规定何时用 OCSF 结构化日志何时用 plain tracing）、`openshell-server`（ocsf_log.rs 712 行 + gateway_ocsf.rs——后者为网关侧事件维护进程级 `GatewayIdentity` 单例：operator 名 + 每副本 hostname（gateway_ocsf.rs:15-21），注释明说因为 TLS 重载 watcher、service router 这些地方拿不到 server config，身份只能在启动时解析一次全局共享）、`openshell-driver-mxc` 的 ETW 消费器。`event_bridge.rs` 是 tracing 系统的粘合：thread_local 暂存当前事件（:13），目标 target 固定 `"ocsf"`（:20），`emit_ocsf_event`（:37）设置后经 tracing 分发并在测试里验证分发后清空；`emit_ocsf_event_routed`（:84）带 sandbox_id 路由到对应沙箱的日志通道。

## 四、数据流

监督器/沙箱代码调 builder → `build()` 从 `ctx()` 单例取共享身份 → 产出 `OcsfEvent` → `emit_ocsf_event` 挂到 thread-local → 订阅者挂的 `OcsfShorthandLayer`（人读单行，格式 `<HH:MM:SS.mmm> <severity> <CLASS:ACTIVITY> <action> <key fields>`，shorthand.rs:4；时间戳越界输出 `??:??:??.???` 不 panic，:16-19）或 `OcsfJsonlLayer`（机器读 JSONL）落到 stdout/文件/网关 TracingLogBus → 网关侧再经 OCSF JSONL 落地。Windows 支线是独立一条：mxc 驱动的 `etw_consumer.rs`（2446 行）跑一个进程级实时 ETW 会话，消费 OS **Sandboxing** TraceLogging provider（`{f6ec123e-…}`）在 AppContainer/processcontainer 操作时产生的事件，经 TDH 解码成中性的 `DecodedEtwEvent`，再归因到 sandbox_id 映射成 OCSF 从 tracing sink 发出（文件头 :4-26）。该模块刻意分两半——capture+decode（unsafe FFI）与 attribute+map+emit（handler 闭包）——为将来抽 crate 留了"移文件即可"的缝。

## 五、设计决策

1. **事件格式选 OCSF 而非自造 schema**：安全审计日志的下游是 SIEM 生态，标准类的 UID（4001/4007…）让 OpenShell 事件能直接进现有管道，代价是字段受约束——所以 builder 留 `unmapped` 正规出口。
2. **vendored schema 只测不跑**：schema 快照锁进仓库保证离线 CI 可校验生产格式（tests/roundtrip.rs 等），运行时不读文件——零运行时依赖、零供应链面。
3. **单例身份而非参数传递**：`EventContext`/`GatewayIdentity` 两个 OnceLock 换来"任何深处代码一行就能发事件"，代价是进程只能有一个沙箱身份（监督器/沙箱进程模型恰好保证这一点）。
4. **降级只做减法**：旧版本消费者拿到的永远是合法子集，不需要双向转换器。
5. **shorthand 与 JSONL 同源**：人读格式从同一事件对象派生，永远不会出现"人看到的和机器收到的对不上"。

## 六、新人提示

- **勘误：ETW FFI 不在本 crate**——在 `openshell-driver-mxc/src/etw_consumer.rs`（且自述"Checkpoint 2: capture + decode only"，归因+OCSF 映射是后续 checkpoint，代码里 `#![allow(dead_code)]` 注明脚手架未接线）。
- **v1.7.0 目录与 OCSF_VERSION 不一致是常态**：实现版本 1.8.0，vendored 旧版本留给兼容性对照，不是没删干净。
- 加新事件字段时先查 vendored schema 里目标类有没有这个属性；没有就进 `unmapped`，别发明私有字段名。
- `validation` 模块要开 `test-support` feature 才存在，直接 `use openshell_ocsf::validation` 在纯生产构建会编译错误。
- MXC ETW 只消费 Sandboxing provider（Plane A）；Kernel-General provider 需要服务账号没有的特权，头注释明说不做——Windows 审计覆盖有已知边界。
- telemetry/ 目录的 md 是社区运营报告（双周聚合计数），改 OCSF 代码不用动它，看使用趋势倒是好材料。
