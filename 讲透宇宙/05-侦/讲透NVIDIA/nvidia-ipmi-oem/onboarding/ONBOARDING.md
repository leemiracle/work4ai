# nvidia-ipmi-oem 仓库 Onboarding

> 仓库 `/usr-data/data2/repos/agent-repos/NVIDIA/nvidia-ipmi-oem`（commit dba74af0）；图谱 357 节点/605 边/8 层/10 步导览，fingerprints 43 文件基线。锚均经源码核实。

## 1. 这是什么仓库

NVIDIA IPMI OEM support library——OpenBMC `ipmid` 守护进程的**插件 .so**（构建产物 `libznvipmioemcmds.so` + 可选 `libznvipmi-metrics.so`，安装到 `lib/ipmid-providers`，`CMakeLists.txt:243,255`）。一个代码库同时服务 DGX 服务器、BlueField DPU（含 BF2/BF3/BF4-1/Spectre 变体）与 Grace（GH200/GB200）三类硬件平台，为它们提供 NVIDIA 私有 NetFn 上的带外管理命令：I2C 主读写、PSU/固件信息、DNS/NTP/SEL 策略、风扇 PWM、BIOS POST 码、BIOS 密码种子、Redfish bootstrap 账户、SBMR 启动进度码、IPMI 命令指标遥测。README 只有一行标题（`README.md:1`），全部知识都在源码与 CMake 开关里。

## 2. 五分钟心智模型

**寄主-插件模型**：OpenBMC 的 ipmid 在启动时扫描 provider 目录 dlopen 本插件；插件不提供入口函数，而是靠 GCC `__attribute__((constructor))` 在 .so 加载瞬间自注册命令处理器。注册入口按构造优先级排成一条链：DGX 核心 `constructor(101)`（`src/oemcommands.cpp:206`）→ BF 共用核心 `constructor(102)`（`src/BF/oemcommands.cpp:220`）→ 平台变体 `constructor(103)`（`src/BF/BF2/oemcommands.cpp:54`、`src/BF/BF4/oemcommands.cpp:99`）；无优先级的构造器（Grace `Grace/src/ghoemcommands.cpp:149`、机箱/传感器/存储/SBMR）最后跑。102/103 晚于 101 注册，使平台变体可用拒绝桩**覆盖**共用核心的同一命令——BF2 把 BF 核心注册的 Live Fish 重新注册为"unsupported in Bluefield 2"（`src/BF/BF2/oemcommands.cpp:68`）即此机制。

**命令坐标系**：OEM NetFn 常量钉在 `include/oemcommands.hpp:26-29`（0x32 netFnOemGlobal / 0x3C netFnOemNV / 0x30 netFnOemPost / 0x3E netFnOemEight），SBMR 用 0x2C（`include/sbmr-bootprogress.hpp:25`），Group Extension 命令用 0x52（`include/oemcommands.hpp:30`）。处理器签名统一 `ipmi::RspType<...>`，实现壳是薄薄的 D-Bus 桥——真正状态都在 phosphor 栈服务里（xyz.openbmc_project.*），本仓本质是 **IPMI 线协议 ↔ D-Bus ↔ 少量 /dev/i2c 与 sysfs/GPIO 直访** 的翻译层。

## 3. 目录地图

| 路径 | 职责 |
|---|---|
| `src/oemcommands.cpp`（4511 行） | DGX 核心：I2C 主读写 `i2cTransaction`（:349）起手，DNS/NTP（:437,:526/:621）、SEL 策略（:760）、Rshim（:1033）、BMC Boot Complete（:1177）、风扇 PWM（:1436）、PSU（:1576）、BIOS POST（:1682）、工厂复位（:281）、D-Bus 通用读写、bootstrap 账户（:3582）、GPIO（:2438）与注册表 `registerNvOemFunctions`（:4019） |
| `src/BF/` | BlueField 族：共用核心 `oemcommands.cpp`（3065 行，Live Fish :573/:586、TorSwitch :651、DPU 工厂复位 :1402、RAM 密码 bootstrap :1885）；`BF2/` BF2 变体、`BF4/` 工厂复位对齐、`chassiscommands.cpp` 电源控制（:86）、`spectre/` 全量拒绝桩（:57） |
| `Grace/` | 独立目录树：`ghoemcommands.cpp`（3301 行）风扇/SSD LED/SEL/Redfish 端点/BIOS 密码（:1336,:1405）/真 SMBPBI（:186）/PAM bootstrap（:1679）；`gh-config.hpp` 硬件常量 |
| `include/` | DGX/BF 共用头：`oemcommands.hpp`（NetFn/命令常量+getMaskdata :158）、`dgx-a100-config.hpp`（PSU I2C 拓扑 :29-31）、`sdrutils.hpp`/`sensorutils.hpp`/`sensorcommands.hpp` 传感器链、`storagecommands.hpp` FRU 结构、`types.hpp` DbusVariant（:48） |
| `src/sensorcommands.cpp`（1773 行）+ `src/storagecommands.cpp`（994 行） | IPMI 标准域：SDR/读数/阈值命令；FRU 读写/哈希设备号（:154 recalculateHashes） |
| `src/sbmr-bootprogress.cpp` + `Grace/src/sbmr-bootprogress.cpp` | SBMR 启动进度码收发（Redfish/D-Bus Raw 状态对象），两变体按构建选项二选一 |
| `src/nvidia-metrics-logging.cpp` + `src/nvidia-ipmi-metrics.cpp` | 遥测：filter 钩子记录每条 IPMI 命令（:147），UNIX 数据报 socket 外发（`/run/bmc-cmd-metrics.sock`，`src/nvidia-ipmi-metrics.cpp:24`） |

## 4. 分层走读（图谱 8 层归并四段）

1. **构建层（L01-02）**：`CMakeLists.txt`（280 行）以 30+ option 裁剪源集：GH 走 `Grace/src`（`CMakeLists.txt:131-134`），SPECTRE/BF2/BF3 选 BF 组合（`CMakeLists.txt:137-152`），缺省 DGX 只编 `src/oemcommands.cpp+sbmr`（`CMakeLists.txt:154-157`）；BF4-1 追加（`CMakeLists.txt:204-205`）。注意 `CMakeLists.txt:208-215`——**BF 族构建反而排除** `common_library_sources`（storage/sensor），而 DGX 核心编进所有 BF 构建。C++23（`CMakeLists.txt:6`），链接 pam/boost_process/OpenSSL/gpiodcxx（`CMakeLists.txt:232-241`）。白名单生成器 `generate-whitelist.py` 解析 `#<NetFn>:<Cmd>:<ChannelMask>` 行（`generate-whitelist.py:24-27`），缺省通道掩码 0xffff（:43）——但 conf 只有一行注释，产物头无仓内消费者（见 README 勘误）。
2. **公共设施（L03）**：`types.hpp` 的 `DbusVariant`/`SensorMap` 是全仓 D-Bus 数据形状（`include/types.hpp:48-56`）；`commandutils.hpp` 的 `ipmiPrintAndRegister` 实为死代码（:57，全仓零引用）；`biosversionutils.hpp` 供 BIOS 固件查询。
3. **平台命令层（L04-07）**：DGX/BF/Grace 三大 OEM 核心 + 标准 sensor/storage 链。传感器链自建缓存：D-Bus `InterfacesAdded/Removed` 信号触发 `sensorTree`/`sensorDataRecords` 清空重建（`src/sensorcommands.cpp:106-125`）。BF 族三层结构（共用核心→变体→拒绝桩）与 Grace 的 BIOS 密码/SMBPBI 特有命令见 explain 两篇。
4. **可观测层（L08）**：`nvidia-metrics-logging.cpp` 用 `ipmi::registerFilter(prioOemBase)` 挂旁路钩子（`src/nvidia-metrics-logging.cpp:154`），**只记录永不拦截**；`isSecretBearingCommand` 只 redact App NetFn 的 Set User Password（`src/nvidia-metrics-logging.cpp:218-222`），其余载荷全量 hex 落日志（`src/nvidia-ipmi-metrics.cpp:167-181`），4096 字节封顶加 `[truncated]`（`src/nvidia-ipmi-metrics.cpp:25`、:94-96）。

## 5. 数据流与控制流

一次 OEM 命令的生命周期：`ipmi 帧到达 → ipmid 解析 NetFn/Cmd/LUN → metrics filter 先行（记录+redact 判定，返回 ccSuccess 放行）→ 白名单/注册表查 handler（`ipmi::registerHandler` 注册于 `prioOemBase`）→ 处理器内做通道/状态检查 → 三类副作用之一：D-Bus 方法调用（大多数）、`/dev/i2c-N` ioctl 直访（`src/oemcommands.cpp:349` 起 i2cTransaction，open+ioctl I2C 读写）、文件/sysfs/GPIO（gpiodcxx）→ `ipmi::response(...)` 组包回程`。特权分级两档：绝大多数 Admin；**系统接口专属**命令注册为 `Privilege::sysIface`（BF TorSwitch Set/网络重供应 `src/BF/oemcommands.cpp:2921-2930`、BF2 PowerCap Set `src/BF/BF2/oemcommands.cpp:173`、三平台 bootstrap 账户 `registerGroupHandler` `src/oemcommands.cpp:4452-4455`/`Grace/src/ghoemcommands.cpp:3106-3113`）——这是"只有主机带内 BIOS 能调"的硬闸，比通道检查更根本。

## 6. 构建与运行

典型构建：`cmake -DBF3-OEM-COMMANDS=ON ..`（或 GH-oem-commands / 缺省 DGX）；产物随发行版装进 OpenBMC 镜像的 `/usr/lib/ipmid-providers/`，由 phosphor-host-ipmid 加载。外部依赖全是 OpenBMC 系：libipmid、sdbusplus、phosphor-logging、boost（process/asio 协程）、OpenSSL（BIOS 密码 PBKDF2、证书指纹）、libpam（bootstrap 改密）、gpiodcxx。运行期开关：指标功能由 D-Bus 属性 `xyz.openbmc_project.Settings /logging/bmc_cmd_metrics Enabled` 热启停（`src/nvidia-metrics-logging.cpp:38-41`），缺省开。

## 7. 设计决策与陷阱

- **构造优先级=平台覆盖序**：101/102/103 链是隐式契约，新增平台变体必须排在共用核心之后，否则拒绝桩会被共用实现反向覆盖。
- **拒绝桩是一种正常产品形态**：spectre 整仓（`src/BF/spectre/oemcommands.cpp:57` 起）与 BF 核心中 30 处 "unsupported in" 都是故意的——命令号占位保持线协议稳定，行为按平台熔断。
- **同名常量跨头重复定义**：`netFnOemNV=0x3C` 在 `include/oemcommands.hpp:27` 与 `include/sbmr-bootprogress.hpp:34` 各定义一次（namespace 相同），靠"不同 TU 不同 include"存活——合并 include 顺序敏感，重构易踩重定义。
- **README 一行+无独立 LICENSE 说明**：仓知识几乎全在 commit message（如 1266083 对 BIOS 密码通道限制的完整根因分析）与 CMake 注释里。
- **错误码私有区**：`ipmiCCBootStrappingDisabled=0x80`、`ipmiCCBIOSPostCodeError=0x89`（`src/oemcommands.cpp:221-225`）属 NVIDIA 自定义补码区，测试脚本需按平台区分。

## 8. 新人上手指引

1. 先读 `CMakeLists.txt:130-157` 弄清"你关心的是哪个平台构建"，再进对应核心文件；别假设 BF 构建里没有 DGX 代码。
2. 找命令号：`include/oemcommands.hpp` / `Grace/include/ghoemcommands.hpp`（BIOS 密码 0x36/0x37 在 `Grace/include/ghoemcommands.hpp:70-71`）常量区 → 注册表（DGX `src/oemcommands.cpp:4019` 起 / Grace `Grace/src/ghoemcommands.cpp:2946` 起 / BF `src/BF/oemcommands.cpp:2691` 起）→ 处理器实现。
3. 改动涉及密码/凭据时三线都要看：Grace BIOS 密码通道闸 `verifyBiosPasswordAccess`（`Grace/src/ghoemcommands.cpp:1302`）、metrics redact 名单（`src/nvidia-metrics-logging.cpp:218`）、sysIface 注册。
4. 验证优先用 ipmitool raw：`ipmitool raw 0x3C 0x36 …`（BIOS 密码需系统接口通道+CPU 未 boot 完）。
5. 图谱导览 T01→T10 与本节顺序一致，可作为代码浏览的 checklist。

---
字数 6240（非空白字符）/锚 43（唯一行号锚）
