# 03 · 策略健康诊断与 REST 依赖注入（policy.go / field_policy.go / health / diag / samples/restApi）

## 角色定位

这条线是 go-dcgm 的**主动监控面**：policy 在超阈时推事件（ECC/PCIe/温度/功耗/NVLink/XID），health 给子系统级判定，diag/mndiag 跑主动诊断；samples/restApi 示范"**如何把绑定包装成 HTTP 服务且保持可测**"。
## 内部结构

- **policy.go（1166 行，全仓最大）**：七类条件强类型化——`DbePolicyCondition`（policy.go:146）/`Pci`（:154）/`RetiredPages`（:160）/`Thermal`（:168）/`Power`（:174）/`Nvlink`（:180）/`Xid`（:188），统一入口 `PolicyCondition`（policy.go:26），默认阈值如 DefaultMaxRetiredPages=10 对齐 dcgmi（policy.go:58）。`translateConditions`（policy.go:486）把 Go 条件翻译成 C 位掩码。事件分发器 `policyDispatcher`（policy.go:219）：`addSubscription`（:250）注册、`removeSubscription`（:293）退订、`deliver`（:426）分发、`dropped`（:454）丢弃计数；注册失败回滚 `rollbackSubscription`（:361-362，调用点 :1095）。
- **field_policy.go**：字段策略独立成套——并发注册表 `fieldPolicySubscriptionRegistry`（field_policy.go:546）+运行时符号探测 `requireFieldPolicySymbol`（field_policy.go:148，使用点 :218/:255/:276）。
- **health/diag/mndiag**：health.go `HealthSet`（:54）/`HealthGet`（:95）/`HealthCheck`（:138），模型 `DeviceHealth`（:43）/`Incident`（:114）；diag.go 四层结果 `DiagResult`（:36）/`DiagEntityResult`（:54）/`DiagResults`（:88）legacy/新版双解析；mndiag.go `requireMultiNodeDiagnosticSymbol`（mndiag.go:127）+异步 stop+wait 防句柄泄漏；error.go:84 `getErrorMeta`。
- **restApi 样本**：handlers/dcgm.go:14 `deviceDeps` 聚合依赖（dcgm.go:23 `realDeviceDeps` 绑真实函数），处理器全部 `getXxxWithDeps`（dcgm.go:38/:51/:78/:107）；server.go:24 gorilla-mux 装配（server.go:10）。

## 外部连接

入口全在 api.go：`ListenForPolicyViolations`（api.go:156）/`WatchPolicyViolationsForGroup`（:231）订阅事件流，`PolicyViolationDropCount`（:237）暴露丢弃计数，`HealthCheckByGpuId`（api.go:128）健康查询，`GetErrorMeta`（api.go:192）错误查询。事件物理通路：引擎→callback.c:5-8→`ViolationRegistration`（policy.go:662-665）→按 condition 类型解码 C 结构（:674 dbe/:697 thermal/:719 xid）→dispatcher.deliver；字段策略同构走 field_policy_callback.c:18-21→field_policy.go:694-697。

## 数据流

订阅：`ListenForPolicyViolations`→translateConditions（policy.go:486）→DCGM 注册（失败即 rollbackSubscription :361）→channel 返回。事件：引擎检测超阈→跳板→解码→deliver→channel 满**则丢弃并计数**（dropped :454）——消费慢不反压引擎。健康：HealthSet 配宽度→引擎判定→HealthCheck 聚合 Incident（health.go:114/138）。REST：请求→handler→deps（真实 dcgm.go:23/测试 fake）→dcgm 包→JSON。

## 设计决策

1. **手写 dispatcher 而非每订阅者一个原生回调**：DCGM 回调线程宝贵，Go 侧 channel 解耦；丢弃计数把"丢事件"变成可观测指标。
2. **rollbackSubscription（policy.go:361）**：本地注册表与引擎状态同进退，半注册状态是脏数据之源。
3. **符号探测降级（field_policy.go:148/mndiag.go:127）**：新 API 旧库时优雅报错——绑定库比 DCGM 本体发布更频繁，这是生存必需。
4. **restApi 的 deps 注入**：HTTP 层零硬依赖即可测（dcgm.go:14），是绑定库消费者的标准姿势——比 mock cgo 简单一个量级。

## 新人提示

读 policy.go 别按行号顺序——先 policy.go:219-460（dispatcher）再 :486+（条件翻译）最后 :662-719（回调解码）。**消费 violation channel 必须快或带缓冲**，否则事件从 dropped（policy.go:454）漏掉——告警场景把 DropCount 纳入监控。写自己的服务直接抄 restApi 的 deps 模式（dcgm.go:14/:23）。健康宽度用位掩码（health.go:54），XID/InfoROM 信号量最大。
