# 01 · cgo 核心与回调跳板（admin.go / api.go / native_calls.go / callback.c 族）

## 角色定位

这三组文件是 go-dcgm 绑定的"脊梁"：`admin.go` 负责**加载 libdcgm**（dlopen 三模式），`api.go` 是**对外门面与会话引用计数**，`native_calls.go` 是**原生调用的接口化底座**，三个 `.c` 跳板解决 **C 函数指针进不了 Go 闭包**的限制。没有它们，其余子系统都只是悬浮在接口上的纯逻辑。

## 内部结构

- **dlopen 加载**：`pkg/dcgm/admin.go:84-91` 的 `loadLibrary` 打开 `libdcgm.so.4`（admin.go:86），`C.dlopen` 带 `RTLD_LAZY|RTLD_GLOBAL`（admin.go:91）；LDFLAGS 在 admin.go:20-21 声明 `-ldl -Wl,--unresolved-symbols=ignore-in-object-files`——符号延迟到运行时 dlsym。三种宿主模式 `Embedded/Standalone/StartHostengine`（admin.go:43-47）。
- **V3 降级链**：Standalone 连接按符号可用性自动选协议——admin.go:155-160 构造 `useV3:true` 连接对象，admin.go:190-191 分流到 `connectStandaloneV3`，探测 `dcgmConnect_v3` 在 admin.go:226-227，缺失时 admin.go:229 报错需 DCGM 4.5.0+。旧库自动落 V2 连接串，**协议升级不破坏兼容**。
- **引用计数门面**：`api.go:23` `Init` 用包级 `dcgmInitCounter`（api.go:13）+mutex 管会话——计数为负说明 Shutdown 先于 Init（api.go:27-28），为零才真正初始化（api.go:31），递增后返回 cleanup 闭包（api.go:40-45）；`Shutdown`（api.go:49-61）只在计数归一时真正关停。
- **12 个 ops 接口**：`native_calls.go:5-6` `cgoAdapter struct{}` 聚合原生实现，切成 sessionCalls(native_calls.go:19)/watchGroupOps(:31)/pidWatchOps(:40)/deviceStatusOps(:50)/healthGroupOps(:59)/policyRegistrationCalls(:68)/fieldPolicyListCalls(:74)/fieldPolicyEventCalls(:80)/multiNodeDiagnosticCalls(:86)/deviceInfoOps(:92)/policyReadOps(:102)/topologyOps(:108) 共 12 个（实测口径，图谱称 15 系误）。
- **三个 C 跳板**：`callback.c:5-8` `violationNotify`→`ViolationRegistration`（policy.go:662-665 `//export`）；`field_policy_callback.c:18-21`→`FieldPolicyViolationRegistration`（field_policy.go:694-697）；`field_values_cb.c:25-26`（原型 field_values_cb.h:27）→`go_dcgmFieldValueEntityEnumeration`（field_values.go:124-125，extern 声明 field_values.go:23）。

## 外部连接

向上：api.go 的 26 个导出函数是 dcgm-exporter 等下游的唯一入口；向下：dlopen 句柄供 `requireFieldPolicySymbol`（field_policy.go:148）等符号探测复用。admin.go:65 `initDCGMWithCalls(api sessionCalls, ...)` 依赖注入使加载层可 mock（admin.go:60 生产注入 `cgoAdapter{}`）。

## 数据流

初始化：`Init(m)`→计数判断→`initDCGMWithCalls`→dlopen→按模式起 hostengine→返回 cleanup。回调（方向相反）：引擎线程→C 跳板 `field_values_cb.c`→`go_dcgmFieldValueEntityEnumeration`（field_values.go:124-125）→`callbackLimitExceeded`（field_values.go:63）背压检查（:72）→转换入 []FieldValue_v2；策略违规同构走 callback.c→policy.go:665→dispatcher。

## 设计决策

1. **dlopen 而非链接**：二进制在无 DCGM 机器上可分发、可测试；代价是符号探测代码散布各子系统。
2. **跳板只转发不做事**：C 侧零逻辑，复杂性留在可测的 Go 侧，DCGM 回调线程不被阻塞。
3. **ops 细粒度切分**：mock 时不需要实现全部方法（12 个小接口而非 1 个大接口）。
4. **引用计数而非全局单例锁**：谁 Init 谁清理，最后一次 Shutdown 才真正释放。

## 新人提示

改会话逻辑先读 admin.go:43-99（模式与加载）再看 api.go:23-61（计数）；新增原生调用要在 ops 接口加方法+cgoAdapter 实现，重跑 go:generate 刷新 mock。**排查"连接不上 hostengine"记住三层降级**：模式选错（Embedded vs Standalone）→ V3 符号缺失落 V2（admin.go:190-191）→ libdcgm.so.4 不在搜索路径（admin.go:86）。`//export` 函数里别做重活——背压熔断（field_values.go:63）就是为此准备的。
