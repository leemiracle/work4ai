# 精讲 02 · spdmd 的发现引擎：spdmd/mctp_endpoint_discovery.cpp（1611 行）

## 角色定位

spdmd 是 libspdmcpp 在 openBMC 上的部署形态，这 1611 行是它的"感知器官"：监听 MCTP 总线与 inventory 的 D-Bus 变化，把"线缆上出现支持 SPDM 的端点"翻译成"创建 Responder D-Bus 对象"。入口 `spdmd/spdmd.cpp` 只有 555 行（CLI、连接、按发现结果动态建对象 `spdmd.cpp:337`），复杂度全在发现引擎的异步回调链里——它决定 spdmd 能否在端点热插拔、服务乱序启动的 BMC 现实里自愈。

## 内部结构

`MctpDiscovery` 构造（`mctp_endpoint_discovery.cpp:41`）后两条主线并行。**存量扫描线**：`setupMCTPServices`（`mctp_endpoint_discovery.cpp:246`）→ `issueGetManagedObjects`（`:284`）拉全量对象 → 失败由 `scheduleGetManagedObjectsRetry`（`:335`）定时重试（BMC 启动早期 mapper 可能未就绪）→ `scanExistingInventoryUUIDs`（`mctp_endpoint_discovery.cpp:764`）扫 inventory 存量。**增量信号线**：`mctpNewObjectSignal`（`:491`）接 InterfacesAdded、`inventoryNewObjectSignal`（`mctp_endpoint_discovery.cpp:897`）、`inventoryUUIDChangedSignal`（`:710`）接 UUID 属性变化。汇合后三级异步关联：`getUUID`（`:1158`）提 UUID → `getMCTPObjectAsync`（`:1240`）找对应 MCTP 对象 → `getInventoryPathAsync`（`:1314`）反查 inventory 路径；`getMediumType`（`:1450`）定传输介质。

## 外部连接

上游是 openBMC D-Bus：MCTP.Control 的 ObjectManager/PropertiesChanged 信号、mapper、inventory 树。下游交 `SpdmdApp::discoveryUpdateResponder`（`spdmd.cpp:295`）按 UUID 去重，`needRecreateResponder`（`:226`）判介质变化重建，`createResponder`（`:337`）实例化 D-Bus Responder，由 `spdmd/dbus_impl_responder.cpp` 把版本（`:111`）、测量哈希（`spdmd/dbus_impl_responder.cpp:245`）、签名（`:257`）落属性。度量策略：`--all` 发现即取测量、`cached_measurements_delay` 节流（`spdmd.cpp:62`）。进程形态：D-Bus 激活 + 60s 看门狗（`spdmd/service_files/spdmd.service:8`）。

## 数据流

以"ERoT 上电"为例：MCTP 守护注册新端点 → `mctpNewObjectSignal`（`:491`）收到对象路径、解出 EID，但 inventory 可能还没有 UUID → 挂起等 `inventoryNewObjectSignal`（`:897`）或属性变化（`:710`）→ 回调里核对 UUID ↔ MCTP 对象 → 组装 ResponderArgs 交 `discoveryUpdateResponder`（`spdmd.cpp:295`）→ `createResponder`（`:337`）→ 新 Responder 跑完整 SPDM 握手（版本→证书→度量）写 D-Bus → Redfish/pldm 消费方看到新部件。对象消失触发清理；介质变化（`getMediumType` 判 PCIe↔SMBus）强制重建连接。

## 设计决策

其一，**全异步回调而非轮询**：1611 行没有一个阻塞 sleep，重试全用定时器（`:335`），与 openBMC 事件循环共生，也解释了 60s 看门狗为何够用。其二，**UUID 是身份锚、EID 只是地址**：`resp_discovery` 以 UUID 为主键（`spdmd.cpp:298`），部件换 EID 不换 D-Bus 身份。其三，**两边都监听 + 异步互查**而非等某边齐再批量匹配——MCTP 与 inventory 对象到达顺序不确定，此设计对启动竞态天然免疫。其四，重试分级（服务级/mapper 级分开退避），一种故障不饿死另一种。

## 新人提示

先读 `spdmd/tests/mctp_endpoint_discovery_test.cpp`（1879 行）：`MockSpdmdApp`（`:293`）与 `MctpDiscoveryTest` 套件（`:306`）把每个信号入口做成可注入用例（`MctpNewObjectSignal` `:344`、`DifferentTransportMediums` `:424`）。真机调试：`busctl tree xyz.openbmc_project.MCTP.Control` 看对象，再查 spdmd 日志 "Creating SPDM object"（`spdmd.cpp:345`）。常见坑：端点在 MCTP 但 inventory 缺 UUID → 永不建 Responder——这是设计而非 bug（可见性由 `spdmd/conf_files/spdmd_conf.json` 的 visible 控制）。
