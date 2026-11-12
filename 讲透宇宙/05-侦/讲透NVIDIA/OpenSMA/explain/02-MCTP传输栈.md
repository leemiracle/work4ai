# 02 · MCTP 传输栈：driver.cpp 的端点管理与三协议共用信封

## 角色定位

MCTP（DMTF Management Component Transport Protocol）是 NSM/SPDM/PLDM 三条协议共用的总线传输层——所有带外消息的"信封"。实现在两处：固件侧 `src/nv/mctp/`（driver/control/composer）与 PDK 侧 `corepdk/modules/mctp-cpp/`（报文组装/路由/平台特化）。它向下对接 I2C/USB 物理通道，向上给协议处理器投递重组完整的 Packet。

## 内部结构

`src/nv/mctp/driver.cpp`（1096 行）是引擎本体：`Driver` 构造函数（`src/nv/mctp/driver.cpp:64`）初始化路由队列（`src/nv/mctp/driver.cpp:73` ipc::Queue::make(QueueId::RoutingTable)）与 validator（`src/nv/mctp/driver.cpp:67` 挂 control.router()）；`Driver::init`（`src/nv/mctp/driver.cpp:105`）注入 UUID（`:107`）；主循环 `[[noreturn]] Driver::main`（`src/nv/mctp/driver.cpp:141`）事件驱动。EID 端点管理：`on_get_eid_probe_response`（`src/nv/mctp/driver.cpp:256`，校验 `:260` 的 dst_eid==0 广播探测）应答端点探测，`update_eid`（`src/nv/mctp/driver.cpp:456`）在转发时学习端点。接收链 `on_receive(Client)`（`src/nv/mctp/driver.cpp:269`）做分片重组（SOM/EOM 拼包）与消息类型分发（`:328` 处理探测响应）；转发链 `forward`（`src/nv/mctp/driver.cpp:381`）与 `on_forward_message`（`src/nv/mctp/driver.cpp:443`）处理跨端点路由；事件上报 `on_receive_event`（`src/nv/mctp/driver.cpp:238`）带 nsmType/eventId。

配套文件：`src/nv/mctp/interface.h:23` 起定义 Packet POD 与层间消息类型标签；`src/nv/mctp/enums.h:27`（using MsgType）起 741 行别名表把 pdk::mctp 的 MsgType/Ccode/Rcode/PhyId 枚举逐项 using 进 nv::mctp 命名空间；协议任务循环 `src/nv/mctp/task.cpp:32`（Task::make）/`:75`（Task::entrypoint）；发送侧组装 `src/nv/mctp/composer.h:21` 命名空间；控制命令 `src/nv/mctp/control.h:22`。PDK 侧 `corepdk/modules/mctp-cpp/src/app/`：`pdk-mctp-app-composer.h`/`pdk-mctp-app-composer.cpp` 组装 tx 报文头与缓冲布局、`pdk-mctp-app-router.cpp` 路由表、`pdk-mctp-app-packet.cpp` 报文封装、`pdk-mctp-app-vendor.h` 厂商消息——模块在 modules 与 platforms/mcxn236 各有一份平台特化。

## 外部连接

下接物理层：I2C 端口抽象（`src/nv/i2c/port.h`，39 行）与 USB 备份通道——`src/nv/usb/mctp_router.cpp:98`（update_routing_table）+ `src/nv/usb/usb_mctp_header.h`，经 `src/nv/usb/hid_smb.cpp:44`（i2c_manual_nack）HID-SMBus 桥，任务循环 `src/nv/usb/task.cpp:48`（Task::make）/`:59`（entrypoint）。上接协议：NSM（`src/nv/mctp/nsm.cpp:1474` process）、SPDM（`src/nv/spdm/task.cpp:257` spdm_tx 走 MCTP、`:285`/`:289` UsbRxBit/I2cRxBit 双通道收）、PLDM（corepdk/modules/pldm-fd）。横向依赖 IPC 基础设施（`src/nv/ipc/queue.h:35` class Queue、`src/nv/ipc/task.h` 任务基类）。

## 数据流

收：物理通道字节流 → driver 分片重组（`src/nv/mctp/driver.cpp:269`）→ 按 MCTP 消息类型标签分流：控制消息走 control（Set/Get Endpoint ID 等标准命令），NVIDIA vendor 消息按子类型进 NSM/SPDM/PLDM 处理器。发：处理器产出 Packet → composer 组装 MCTP 头 → `src/nv/mctp/driver.cpp:381`（forward）按路由表发端点。跨核场景：消息经 IPC 队列投递到对核（`src/nv/mctp/driver.cpp:443`），MCXN 双核的 NSM 响应可能在另一核组装。

## 设计决策

①**传输与协议彻底分层**——driver 只认 MCTP 头与端点，不解析 NSM/SPDM 载荷，三协议独立演进（这也是 SPDM 四种 transport 绑定 MCTP/PCIeDOE/TCP/Storage 中本仓只启用 MCTP 的原因）；②**双物理通道冗余**——I2C 主路 + USB/HID 备份路（`src/nv/usb/mctp_router.cpp`），现场总线故障可切通道；③**EID 学习式端点管理**——probe（`src/nv/mctp/driver.cpp:256`）/update（`:456`）而非静态配置，适应机箱内端点热插拔；④**741 行别名表是编译防火墙**——业务代码只 using nv::mctp 前缀（`src/nv/mctp/enums.h:27`），PDK 枚举变动不扩散。

## 新人提示

读消息流从 `src/nv/mctp/driver.cpp:141`（Driver::main）事件循环进入，跟 `:269`（on_receive）一条线到协议分发。改报文格式必须同步 `src/nv/mctp/interface.h:23`、`src/nv/mctp/composer.h:21`、`corepdk/modules/mctp-cpp/src/app/pdk-mctp-app-packet.cpp` 三处并跑同目录 composer-test/control-test/driver-test。EID 问题先看 `src/nv/mctp/driver.cpp:256` 与 `:456`。"为什么消息没到 NSM"——九成是消息类型标签或 vendor id 校验（`src/nv/mctp/nsm.cpp:1474` 入口）没过。USB 通道调试记得 `src/nv/usb/task.cpp:59` 任务也在收发路径上。
