# 讲透 NVMeDeviceMain.cpp（装配中枢，1429 行）

## 角色定位
进程入口 + 全局状态持有者 + 五路 D-Bus 事件路由。全部"发现/销毁/电源联动"策略集中于此；NVMeDevice 只是它管理的一个个盘对象。

## 内部结构
全局单例态：driveMap（:47-51，eid→NVMeDevice）、discoveredDriveEids（:61）、coldRemovalCheckComplete（:67）、sensorManager（:54，NVME_MI_SENSORS 时）。发现链：createDrives（:420）→ GetObjects 拉配置（kernel-MCTP 与 mctpd 接口集分流 :429-438）→ handleMCTPEndpoints（:341）筛 SupportedMessageTypes 含 NVMe-MI（:377-378）→ collectInventory/handleEmEndpoints（:316/:115）合并 EM 侧 FormFactor/LocationCode/Associations（"containing" 关联 :196-199）建 NVMeDevice。状态文件读改写在 updateSingleDriveState（:446）/markDriveAsRemoved（:553）。

## 外部连接
向 object_server 注册三个 manager 路径（:1137-1141）；订阅 EM/mctpd/systemd1/chassis 信号；host0 状态经 isHostRunning/isHostOff（:769/:685）；TAL TelemetryAggregator 注册 "nvmesensor" 生产者（:1143-1147）。

## 数据流
启动：post(createDrives+request_name :1156-1159)→五 match 挂钩→io.run（:1421）。运行期三类事件：①端点增删（InterfacesAdded 1s 防抖 :1230-1257 / Removed 即时 :1261-1269）→重建盘；②MCTP Connectivity 变化（:1273-1282）→connectivityChanged（:803）更新降级态；③host0 电源（:1337-1417）：Off → 先对**所有**盘 cancelPendingOperations 再逐个 closeEndpoint + deferredDestroyDrive（:1362-1387，顺序是为了让共享 worker 队列先排干），并清 discoveredEIDs、复位 cold-removal 标志；Running → 直接重扫（暖重启时 mctpd 不发端点信号，:1397-1407）。开机后等 300s（bootProgressTimeout）才做冷拔盘盘点 checkForColdRemovedDrives（:1286-1315/:873），给 MCTP 发现留时间。

## 设计决策
①全部信号处理 1 秒防抖（filterTimer/debounceTimer/emSensorConfigTimer :1161/:1230/:1206）——EM 启动风暴下避免反复拆建设备；②销毁走 deferredDestroyDrive（:986）把 D-Bus 注销挪出信号回调上下文；③盘状态 JSON 逐盘增量更新而非全量重写（:446-546），掉电也只丢一条；④connectivity 三态中仅 Degraded 需 in-kernel MCTP（README:248-249），userspace mctpd 路径只在重扫时重置。

## 新人提示
main 只认 --debug（:1119-1125），别找 --help。排障三板斧：`busctl tree xyz.openbmc_project.NVMeDevice` 看对象、journal 里 "Chassis power state"/"Host state changed" 看电源联动、/var/lib/nvidia-nvme-manager/nvme_drive_state.json 看 EID→槽位映射。注意 driveMap 键是 uint8_t EID 而 PendingMCTPEndpoint.bus 初始化为 -1（:105）是"未知"哨兵而非真实总线号。
