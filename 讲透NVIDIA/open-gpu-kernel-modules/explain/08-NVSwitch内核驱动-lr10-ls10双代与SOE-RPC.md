# 08 · NVSwitch 内核驱动：lr10/ls10 双代 HAL、SOE RPC 与 fabric 管理面

> 仓库 @ 615.71.09。本篇覆盖 `src/common/nvswitch/`（注意：实际路径在 `common/` 下，不是根级 `src/nvswitch/`）与 Linux 粘合层 `kernel-open/nvidia/linux_nvswitch.c`。

## 一、角色定位：交换芯片的内核代理，fabric manager 的对端

NVSwitch 是 DGX/HGX 服务器里 NVLink 拓扑的交换芯片——GPU 全互联（如 DGX H8 的 18 芯片 fat-tree）靠它们转发。本目录是 NVSwitch 芯片的内核驱动库，但它服务的"用户"几乎只有一个：用户态的 **nvidia-fabricmanager**（FM）。FM 负责整台机器的 fabric 拓扑发现、路由表下发、链路训练与降级隔离；内核驱动则提供设备枚举、寄存器访问、微控制器（SOE）通信、中断与错误上报这条"内核侧通道"。

一个必须先说清的构建事实（也是本篇最重要的甄别结论）：**NVSwitch 驱动不独立成 `.ko`，它被编进 `nvidia.ko`，且主体实现位于闭源二进制核里**。开源构建侧 `kernel-open/nvidia/nvidia-sources.Kbuild:59-61` 只编三个粘合文件（linux_nvswitch.c / procfs_nvswitch.c / i2c_nvswitch.c）；这些文件调用的 `nvswitch_lib_*` 符号由 `nv-kernel.o_binary` 提供（`kernel-open/nvidia/nvidia.Kbuild:19-21` 注释直言这是"shared across all UNIX platforms"的二进制核）。`src/common/nvswitch/` 全库 83k 行源码（4.6MB）在开源构建中**不参与编译**——它是随仓发布的参考源码，对应闭源 blob 内的实现。理解这一点后，读这 83k 行的意义是"看懂 blob 在做什么"，而非"改了就能生效"。

代际上双代并存：**LR10**（Ampere/Hopper 世代 NVSwitch，NVLink-SW 3.0）与 **LS10**（Blackwell 世代，NVLink-SW 5.0）。`nvswitch_lib_validate_device_id`（kernel/nvswitch.c:2096）用两个谓词分流：`nvswitch_is_lr10_device_id` / `nvswitch_is_ls10_device_id`（声明于 kernel/inc/common_nvswitch.h:605-606）。

## 二、内部结构：三目录 + kernel 下的"共享子系统 × 双代"矩阵

```
src/common/nvswitch/
├── common/inc/         # 与库实现共享的头（soe/soeif*.h 接口头在这里）
├── interface/          # 对外契约：export_nvswitch.h / ctrl_dev_nvswitch.h / ioctl_common_nvswitch.h
└── kernel/             # 主体
    ├── nvswitch.c      # 6710 行：nvswitch_lib_* 公共 API（probe 初始化/ctrl 分发）
    ├── lr10/           # LR10 代：lr10.c 8359 / intr_lr10.c 6104 / link 2712 / soe 2610 / minion 1390 ...
    ├── ls10/           # LS10 代：intr_ls10.c 9170(全库最大) / ls10.c 6895 / link 2222 / soe 1887 / sugen 1523 / multicast 1412 / tnvl 1322 ...
    ├── soe/            # SOE 微控制器通信骨架（268 行 + soe_call_hal 分派）
    ├── flcn/           # Falcon 队列框架（flcnqueue 1654 行 + v03/v04/v05/v06 四代）
    ├── cci/            # 线缆管理抽象（cci_nvswitch 3067 行 + cables/{copper,direct,optical})
    ├── inforom/        # InfoROM 读写（ECC/OMS/BBX/NVL 对象五文件）
    └── ipmi/           # 服务器带外管理接口
```

体量前十的文件里双代各占一半，能看出两代的侧重差异：LR10 的复杂度在 `lr10.c`（初始化与控制流），LS10 的复杂度转移到 `intr_ls10.c`（9170 行中断处理——Blackwell 世代错误源与路由表规模暴涨）且多出三个 LR10 没有的文件：`sugen_ls10.c`（软复位序列生成器）、`multicast_ls10.c`（NVLS 多播路由）与 `tnvl_ls10.c`（可信 NVLink）。TNVL 是链路级安全特性：`tnvl_ls10.c:45-54` 定义证书链与测量上限常量（`TNVL_MAX_CERT_CHAIN_SIZE 0x1000`、PEM 边界串），把 X.509 式认证引入交换芯片链路配置。

HAL 组织与 GPU 侧 RM 不同：没有函数指针大结构体式的 HAL 表，而是 `haldef_nvswitch.h` 定义的宏族 + `*_call_hal_nvswitch.c` 小分派文件（soe/flcn/flcnable 各一个），每个 HAL 函数按 device 代际展开到 lr10/ls10 具体实现。

## 三、外部连接：一个 pci_driver、105 条控制命令、一个心跳协议

**PCI 与字符设备**：`kernel-open/nvidia/linux_nvswitch.c:120` 定义 `nvswitch_pci_driver`（probe 于 :104 声明、:1340 实现）。probe 里先 `nvswitch_lib_validate_device_id` 过滤（:1347-1350），再按 `NVSWITCH_DEVICE_INSTANCE_MAX` 分配 minor、BAR0 iomap、注册为 `/dev/nvidia-nvswitch*` 字符设备（设备名 `nvidia-nvswitch%d`，:1391-1394 的 snprintf）。`nvswitch_register_chrdev` 在 :1839 经 `pci_register_driver` 挂总线。粘合层与 NVKMS 的字符设备一样走主设备号 195。

**控制面 ioctl** 分两层。全局（control 字符设备）只有 5 条：`GET_DEVICES / GET_DEVICES_V2 / GET_DEVICE_NODES / CHECK_VERSION / CHECK_VERSION_V2`（`kernel-open/nvidia/ioctl_nvswitch.h:253-265`）。设备级控制命令在 `src/common/nvswitch/interface/ctrl_dev_nvswitch.h`（4701 行）里定义了 **105 条**（0x01 起手，:4598-4632 可见连续枚举段），按功能分五族：路由下发（INGRESS_REQUEST_TABLE / ROUTING_ID / ROUTING_LAN 及其 *_VALID 位）、链路运维（RESET_AND_DRAIN_LINKS 0x14 / GET_NVLINK_STATUS 0x17 / UNREGISTER_LINK 0x13）、监控（GET_TEMPERATURE 0x1B / GET_INTERNAL_LATENCY 0x07 / THROUGHPUT/NVLIPT 计数器）、fabric 治理（BLACKLIST_DEVICE 0x20 / SET_FM_DRIVER_STATE 0x21 / SET_DEVICE_FABRIC_STATE 0x22 / SET_FM_HEARTBEAT_TIMEOUT 0x23）与 SOE 通道（GET_SOE_HEARTBEAT 0x55）。ioctl 码用 `NVSWITCH_IOCTL_CODE` 宏（ioctl_common_nvswitch.h:61-75）按数据方向自动挑 `_IOR/_IOW/_IOWR/_IO`——按值语义声明，免手写方向位。

**fabric 状态机**是驱动与 FM 的契约核心，两组枚举（ioctl_common_nvswitch.h:90-108）：驱动级 `OFFLINE → STANDBY（驱动起、FM 未连）→ CONFIGURED（FM 在管）`，异常态 `MANAGER_TIMEOUT / MANAGER_ERROR`；设备级多一个 `BLACKLISTED`。心跳超时默认 10 秒（ctrl_dev_nvswitch.h:2295 的 `NVSWITCH_DEFAULT_FM_HEARTBEAT_TIMEOUT_MSEC (10*1000)`）。黑名单理由细分十种（:117-128 枚举）：手动带外/带内、因 peer 被拉黑、trunk 链路失效（本端/对端）、access 链路失效（本端/对端）、未指明设备故障（本端/对端）——"对端"枚举的存在说明 FM 在做跨交换机的关联隔离判定，内核侧只需如实记录理由并拒绝对黑名单设备的 open、关中断（头注释 :84-88 明文）。

## 四、数据流：下行三通道与上行事件

**下行通道一：ioctl→HAL→寄存器**。FM 的 `SET_SWITCH_PORT_CONFIG` 等命令经 nvswitch.c 的 ctrl 分发函数直达 HAL，读写 NVSwitch 寄存器（BAR0 映射）。路由表类命令逐条下发（SET_INGRESS_REQUEST_TABLE 一次一表项），大拓扑初始化时这个通道吞吐量可观。

**下行通道二：SOE RPC**。部分管理任务（温度、SPI、热管理、心跳）归属芯片上的 SOE 微控制器。RPC 机制 = Falcon 队列框架（flcn/，队列读写 API `flcnQueueReadData` 于 inc/flcn/flcn_nvswitch.h:293）+ EMEM 搬运：`soe_nvswitch.c:58/:85` 的 `soeEmemTransfer_HAL` 负责主内存与 SOE 私有内存之间双向搬运命令/响应块。soeif*.h 十四个接口头（common/inc/soe/）按服务域分文件：soeifcci（线缆）、soeifchnmgmt（链路管理）、soeiftherm（热）、soeifheartbeat（心跳）、soeifsmbpbi（带外 SMBus 桥）、soeififr（InfoROM）、soeiftnvl（可信链路）、soeifspi（SPI ROM）。双代各自的 SOE 适配层 soe_lr10.c（2610 行）/soe_ls10.c（1887 行）填这些接口的实现。

**下行通道三：inband 带内消息**。NVLink 协议自身携带的管理消息（不占额外管理网络）。消息格式定义在 `src/common/nvswitch/../nvlink/inband/interface/`（属 nvlink 库），nvswitch 侧在 nvswitch.c 消费：无法处理的消息按类型 NACK 或丢弃（:1541-1562，经 HAL `nvswitch_send_inband_nack`），链路数据以 `inbandData.nonpersistent_list`（:1605）挂链，`_nvswitch_ctrl_inband_flush_data`（:38 声明）供 FM 排空。

**上行事件**：中断处理（intr_ls10.c 9170 行）汇总错误计数与链路事件，FM 经 `GET_ERRORS` 拉取或等待 `wait_q_errors` 等待队列（linux_nvswitch.c probe 里 init_waitqueue_head）。`nvswitch_task_dispatch`（:1287）是粘合层的工作项泵，把延迟任务（如黑名单后的清场）串行化执行。

## 五、设计决策

1. **单库双代 + 宏 HAL**：不用大函数指针结构，而以 `haldef_nvswitch.h` 宏 + `*_call_hal_*` 文件分派。代价是新增函数要碰宏表，收益是分派代码极薄且编译期可查漏。
2. **管理面全交 FM，内核只做通道**：内核驱动刻意不做任何拓扑决策——路由表、隔离判定都是 FM 下发的数据。这让内核侧代码可以长期稳定（nvswitch.c 的 API 面多年不变），策略演进全在用户态。
3. **黑名单粒度到"理由"级**：十种 BLACKLIST_REASON 把跨交换机故障归因（本端/对端对称展开）编码进 ABI，FM 的判定结果对内核是自解释的，运维侧 `procfs`（procfs_nvswitch.c）可直接读出。
4. **SOE/Falcon 框架复用 GPU 侧血统**：flcn/ 的队列框架与 GSP/RM 的 Falcon 通信同构（v03-v06 四代队列版本并存），NVSwitch 只是又一个 Falcon 宿主——跨产品线复用一套微控制器通信栈。
5. **CCI 线缆多态**：cables/ 下 copper/direct/optical 三实现挂同一抽象，LS10 世代 NVSwitch 出现光电混合背板（光模块直连）后，线缆探测/读写差异被隔离在这层。
6. **参考源码 vs 二进制核的透明化**：83k 行"不可编译但可读"的源码随仓发布，配合开源粘合层，使行为可审计——这是 NVIDIA 开源策略在交换芯片线的投影。

## 六、新人提示

- **读码顺序**：ioctl_common_nvswitch.h（144 行，状态机契约）→ linux_nvswitch.c 的 probe（:1340-1450）→ ctrl_dev_nvswitch.h 的命令枚举段（:4598-4700）→ 按需进 lr10/ls10。
- **改代码前先想清楚**：这 83k 行在开源构建里不编译（见第一节），想验证改动需闭源构建链路或向 NVIDIA 报 issue。
- **代际黑话**：LR10 = NVLink-SW 3.0（Ampere/Hopper 交换），LS10 = 5.0（Blackwell）；MINION = 链路训练微引擎（每物理管一组，minion_lr10/ls10.c）；SUGEN = LS10 软复位序列生成；NVLS = NVLink SHARP（交换机内多播归约，multicast_ls10.c）；TNVL = 可信 NVLink（证书链认证的链路配置）。
- **调黑名单问题**先看 procfs 输出的 reason 枚举值再对照 :117-128，"PEER"后缀意味着故障在对面那颗交换机。
- intr_ls10.c 一文件 9170 行不要通读，按中断位查（Blackwell 的错误寄存器布局在 inc/ls10/ 的头里）。
- 与 GPU 侧 NVLink 的边界：链路的"GPU 半段"由 nvidia.ko 的 nvlink 库（src/common/nvlink/）管，"交换机半段"才是本库；inband 消息格式两边共享。

---

**本篇甄别备注**：任务描述所称 `src/nvswitch/` 实际路径为 `src/common/nvswitch/`；"inband" 目录实为 `src/common/nvlink/inband/interface/`（nvlink 库名下），nvswitch.c 是消费方。NVSwitch 驱动不产出独立内核模块，主体编入 nvidia.ko 的闭源二进制核（nv-kernel.o_binary），本文第三节所述粘合层文件为开源构建中唯三的 nvswitch 编译单元。
